import axios from 'axios'
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const api = axios.create({ 
  baseURL: `${API_BASE}/api`, 
  timeout: 30000, 
  headers: { 'Content-Type': 'application/json' }, 
  withCredentials: true 
})
api.interceptors.request.use(cfg => { const t = localStorage.getItem('access_token'); 
if(t) cfg.headers.Authorization=`Bearer ${t}`; return cfg })
let refreshing=false,queue=[]
const flush=(e,t)=>{queue.forEach(p=>e?p.reject(e):p.resolve(t));queue=[]}
api.interceptors.response.use(r=>r,async err=>{
  const orig=err.config
  if(err.response?.status===401&&!orig._retry){
    if(refreshing) return new Promise((res,rej)=>queue.push({resolve:res,reject:rej})).then(t=>{orig.headers.Authorization=`Bearer ${t}`;
    return api(orig)})
    orig._retry=true;refreshing=true
    const refresh=localStorage.getItem('refresh_token')
    if(refresh){
      try{
        const{data}=await axios.post(`${API_BASE}/api/auth/token/refresh/`,{refresh});
        localStorage.setItem('access_token',data.access);
        flush(null,data.access);
        orig.headers.Authorization=`Bearer ${data.access}`;
        return api(orig)
      }catch(e){
         flush(e, null)

        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')

        return Promise.reject(e)
      }finally{
        refreshing=false}
      }else{
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')

        return Promise.reject(err)
      }
  }
  return Promise.reject(err)
})
export const apiGet=(url,params={})=>api.get(url,{params})
export const apiPost=(url,data={})=>api.post(url,data)
export const apiPatch=(url,data={})=>api.patch(url,data)
export const apiPut=(url,data={})=>api.put(url,data)
export const apiDelete=(url)=>api.delete(url)
export const apiUpload=(url,form)=>api.patch(url,form,{headers:{'Content-Type':'multipart/form-data'}})
export function createWS(path){
  const base=import.meta.env.VITE_WS_URL||'ws://localhost:8000';
  const token=localStorage.getItem('access_token');
  return new WebSocket(`${base}/ws/${path}${token?`?token=${token}`:''}`)
}
export default api
