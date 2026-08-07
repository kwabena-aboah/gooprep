<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5" style="background:linear-gradient(135deg,#111 0%,#1a0800 50%,#111 100%)">
    <div style="width:100%;max-width:520px;padding:1rem">
      <div class="text-center mb-4">
        <RouterLink to="/"><img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:56px"/></RouterLink>
        <p class="text-white-50 mt-2">Join thousands of learners and expert tutors.</p>
      </div>
      <div class="gp-card p-4 p-md-5">
        <div v-if="auth.error" class="alert alert-danger small py-2">{{ auth.error }}</div>
        <div class="mb-4">
          <label class="form-label small fw-600 text-muted text-uppercase" style="letter-spacing:.06em">I want to</label>
          <div class="row g-2">
            <div class="col-4" v-for="r in roles" :key="r.value">
              <div class="text-center p-3 rounded-3 border" :class="form.role===r.value?'border-primary bg-primary bg-opacity-10':''" style="cursor:pointer;transition:all .2s" @click="form.role=r.value">
                <i :class="['fs-3 d-block mb-1', r.icon, form.role === r.value ? 'text-primary' : 'text-muted']"></i>
                <div class="small fw-600" :class="form.role===r.value?'text-primary':''">{{ r.label }}</div>
                <div class="text-muted" style="font-size:.65rem">{{ r.sub }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-6"><label class="form-label small fw-600">First Name *</label><input class="form-control" v-model="form.first_name" placeholder="Alice"/></div>
          <div class="col-6"><label class="form-label small fw-600">Last Name *</label><input class="form-control" v-model="form.last_name" placeholder="Mensah"/></div>
        </div>
        <div class="mb-3"><label class="form-label small fw-600">Email *</label><input type="email" class="form-control" v-model="form.email" placeholder="you@example.com"/></div>
        <div class="mb-3"><label class="form-label small fw-600">Phone <span class="text-muted fw-400">(optional)</span></label>
          <div class="input-group"><span class="input-group-text text-muted small">+233</span><input class="form-control" v-model="form.phone" placeholder="24 000 0000"/></div>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-6"><label class="form-label small fw-600">Password *</label>
            <div class="input-group"><input :type="showPw?'text':'password'" class="form-control" v-model="form.password" placeholder="Min 8 chars"/><button class="btn btn-outline-secondary" @click="showPw=!showPw"><i class="bi" :class="showPw?'bi-eye-slash':'bi-eye'"></i></button></div>
          </div>
          <div class="col-6"><label class="form-label small fw-600">Confirm *</label>
            <input :type="showPw?'text':'password'" class="form-control" v-model="form.password2" :class="{'is-invalid':form.password2&&form.password!==form.password2}" placeholder="Repeat password"/>
            <div class="invalid-feedback">Passwords do not match.</div>
          </div>
        </div>
        <div v-if="form.password" class="mb-3">
          <div class="d-flex gap-1 mb-1"><div v-for="n in 4" :key="n" class="flex-grow-1 rounded" style="height:4px;transition:background .3s" :style="{background:n<=strength?strengthColor:'#e2e8f0'}"></div></div>
          <div class="small" :style="{color:strengthColor}">{{ strengthLabel }}</div>
        </div>
        <div class="form-check mb-4">
          <input class="form-check-input" type="checkbox" v-model="agreed" id="chkTerms"/>
          <label class="form-check-label small" for="chkTerms">I agree to Gooprep's <RouterLink to="/terms" target="_blank" class="text-gp-primary">Terms</RouterLink> & <RouterLink to="/privacy" target="_blank" class="text-gp-primary">Privacy Policy</RouterLink></label>
        </div>
        <button class="btn btn-gp w-100 py-2 mb-3" @click="submit" :disabled="auth.loading||!agreed||form.password!==form.password2">
          <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-person-plus me-2"></i>Create Account
        </button>
        <p class="text-center small text-muted mb-0">Already have an account? <RouterLink to="/login" class="text-gp-primary fw-600">Sign in</RouterLink></p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const auth=useAuthStore(); const router=useRouter()
const showPw=ref(false); const agreed=ref(false)
const form=ref({first_name:'',last_name:'',email:'',phone:'',password:'',password2:'',role:'student'})
const roles=[{value:'student',label:'Learn',sub:'Find tutors',icon:'bi bi-mortarboard'},{value:'tutor',label:'Teach',sub:'Earn income',icon:'bi bi-person-video3'},{value:'institution',label:'Manage',sub:'Bulk enrol',icon:'bi bi-building'}]
const strength=computed(()=>{const p=form.value.password;if(!p)return 0;let s=0;if(p.length>=8)s++;if(/[A-Z]/.test(p))s++;if(/[0-9]/.test(p))s++;if(/[^A-Za-z0-9]/.test(p))s++;return Math.max(1,s)})
const colors=['#ef4444','#f59e0b','#3b82f6','#10b981']
const labels=['Very weak','Weak','Good','Strong']
const strengthColor=computed(()=>colors[strength.value-1])
const strengthLabel=computed(()=>labels[strength.value-1])
async function submit(){const{ok,role}=await auth.register(form.value);if(ok)router.push(role==='tutor'?'/tutor-onboarding':'/dashboard')}
</script>
