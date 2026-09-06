import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiPost, apiGet, apiPatch } from '@/utils/api'
export const useAuthStore = defineStore('auth',()=>{
  const user=ref(JSON.parse(localStorage.getItem('gp_user')||'null'))
  const accessToken=ref(localStorage.getItem('access_token')||'')
  const refreshToken=ref(localStorage.getItem('refresh_token')||'')
  const loading=ref(false);const error=ref('')
  const isAuthenticated=computed(()=>!!accessToken.value&&!!user.value)
  const isStudent=computed(()=>user.value?.role==='student')
  const isTutor=computed(()=>user.value?.role==='tutor')
  const isAdmin=computed(()=>user.value?.role==='admin')
  const isInstitution=computed(()=>user.value?.role==='institution')
  function persist(data){accessToken.value=data.access;refreshToken.value=data.refresh;user.value=data.user;localStorage.setItem('access_token',data.access);localStorage.setItem('refresh_token',data.refresh);localStorage.setItem('gp_user',JSON.stringify(data.user))}
  async function getOnboardingPath(profile){
    if (profile.role === 'tutor') {
      const { data } = await apiGet('/tutors/onboarding/')
      return data.onboarding_complete ? '' : '/tutor-onboarding'
    }
    if (profile.role === 'student') {
      const { data } = await apiGet('/students/profile/')
      return data.has_identity_document ? '' : '/student-onboarding'
    }
    if (profile.role === 'institution') {
      const { data } = await apiGet('/institutions/')
      const complete = Boolean(
        data.name && data.type && data.city && data.address &&
        data.contact_email && data.contact_phone
      )
      return complete ? '' : '/institution-onboarding'
    }
    return ''
  }
  async function login(email,password){
    loading.value=true
    error.value=''
    try {
      const {data}=await apiPost('/auth/token/',{email,password})
      persist(data)
      let onboardingPath = ''
      try {
        onboardingPath = await getOnboardingPath(data.user)
      } catch {
        // Login should still succeed if a profile lookup is temporarily unavailable.
      }
      return {ok:true,role:data.user.role,onboardingPath}
    } catch(e) {
      // Do not let an old session make a failed login appear authenticated.
      accessToken.value=''
      refreshToken.value=''
      user.value=null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('gp_user')
      error.value=e.response?.data?.detail||'Invalid email or password.'
      return {ok:false}
    } finally { loading.value=false }
  }
  async function register(payload){
    loading.value=true
    error.value=''
    try {
      const {data}=await apiPost('/auth/register/',{
        ...payload,
        username:payload.email.split('@')[0]+Date.now(),
      })
      // Registration must not create a session before email verification.
      accessToken.value=''
      refreshToken.value=''
      user.value=null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('gp_user')
      return {ok:true,email:data.email,verificationSent:data.verification_sent,detail:data.detail}
    } catch(e) {
      const errs=e.response?.data||{}
      error.value=Object.values(errs).flat().join(' ')||'Registration failed.'
      return {ok:false}
    } finally { loading.value=false }
  }
  async function logout(){try{await apiPost('/auth/logout/',{refresh:refreshToken.value})}catch{}accessToken.value='';refreshToken.value='';user.value=null;localStorage.clear()}
  async function fetchMe(){
    try {
      const {data}=await apiGet('/auth/users/me/')
      user.value=data
      localStorage.setItem('gp_user',JSON.stringify(data))
      return data
    } catch (error) {
      if ([401, 403].includes(error.response?.status)) {
        accessToken.value=''
        refreshToken.value=''
        user.value=null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('gp_user')
      }
      return null
    }
  }
  async function updateProfile(payload){const{data}=await apiPatch('/auth/users/me/',payload);user.value=data;localStorage.setItem('gp_user',JSON.stringify(data));return data}
  return{user,accessToken,loading,error,isAuthenticated,isStudent,isTutor,isAdmin,isInstitution,login,register,logout,fetchMe,updateProfile}
})
