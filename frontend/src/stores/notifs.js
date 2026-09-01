import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiGet, apiPost, createWS } from '@/utils/api'
export const useNotifStore = defineStore('notifs',()=>{
  const notifications=ref([]);const toasts=ref([]);const unreadCount=computed(()=>notifications.value.filter(n=>!n.is_read).length);let ws=null
  async function fetchNotifs(){try{const{data}=await apiGet('/auth/notifications/');notifications.value=data.results||[]}catch{}}
  async function markAllRead(){try{await apiPost('/auth/notifications/mark-read/');notifications.value.forEach(n=>{n.is_read=true})}catch{}}
  async function markRead(ids){try{await apiPost('/auth/notifications/mark-read/',{ids});ids.forEach(id=>{const n=notifications.value.find(x=>x.id===id);if(n)n.is_read=true})}catch{}}
  function connectWS(){
    if(ws)ws.close()
    try{
      ws=createWS('notifications/')
      ws.onmessage=e=>{
        try{
          const msg=JSON.parse(e.data)
          if(msg.type==='notification'){
            notifications.value.unshift(msg.data)
            toast(msg.data.title,'info')
          }
        }catch{}
      }
      ws.onerror=()=>{ ws=null }
    }catch{}
  }
  function disconnectWS(){if(ws){ws.close();ws=null}}
  function toast(message,type='',duration=3500){const id=Date.now();toasts.value.push({id,message,type});setTimeout(()=>{toasts.value=toasts.value.filter(t=>t.id!==id)},duration)}
  return{notifications,toasts,unreadCount,fetchNotifs,markAllRead,markRead,connectWS,disconnectWS,toast}
})
