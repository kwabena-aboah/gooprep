<template>
  <div class="chat-area d-flex flex-column h-100">
    <div class="chat-header px-3 py-2 border-bottom bg-white d-flex align-items-center gap-2">
      <button class="btn btn-sm btn-outline-secondary d-lg-none me-1" @click="$emit('back')"><i class="bi bi-chevron-left"></i></button>
      <div class="position-relative">
        <img :src="other?.avatar||fb(other?.name)" class="rounded-circle" width="36" height="36" style="object-fit:cover"/>
        <span v-if="other?.is_online" class="position-absolute bottom-0 end-0 online-dot" style="width:9px;height:9px"></span>
      </div>
      <div class="flex-grow-1">
        <div class="fw-700 small">{{ other?.name }}</div>
        <div class="small" :class="other?.is_online?'text-success':'text-muted'">{{ other?.is_online?'Online':'Offline' }}</div>
      </div>
    </div>
    <div class="flex-grow-1 overflow-y-auto p-3" style="background:#f8fafc" ref="chatBox">
      <GpSpinner v-if="loading" height="120px"/>
      <div v-else>
        <div v-for="m in messages" :key="m.id" :class="m.sender===myId?'text-end':'text-start'" class="mb-2">
          <div class="chat-bubble d-inline-block" :class="m.sender===myId?'me':'other'">{{ m.content }}</div>
          <div class="text-muted mt-1" :class="m.sender===myId?'text-end pe-1':'text-start ps-1'" style="font-size:.65rem">
            {{ fmtTime(m.created_at) }}<i v-if="m.sender===myId" class="bi ms-1" :class="m.is_read?'bi-check2-all text-primary':'bi-check2'"></i>
          </div>
        </div>
        <div v-if="typing" class="text-start"><div class="chat-bubble other d-inline-flex align-items-center gap-1" style="padding:.5rem .9rem"><span v-for="n in 3" :key="n" class="typing-dot" :style="`animation-delay:${(n-1)*0.2}s`"></span></div></div>
      </div>
    </div>
    <div class="p-2 border-top bg-white">
      <div class="input-group">
        <input type="text" class="form-control" v-model="newMsg" placeholder="Type a message…" @keyup.enter="send" @input="sendTyping"/>
        <button class="btn btn-gp" @click="send" :disabled="!newMsg.trim()"><i class="bi bi-send-fill"></i></button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue'
import GpSpinner from '@/components/common/GpSpinner.vue'
import { apiGet, createWS } from '@/utils/api'
import { fmtTime } from '@/utils/helpers'
import { useAuthStore } from '@/stores/auth'
const props=defineProps({conv:Object})
defineEmits(['back'])
const auth=useAuthStore();const myId=auth.user?.id;const other=ref(props.conv?.other_user)
const messages=ref([]);const newMsg=ref('');const loading=ref(true);const typing=ref(false);const chatBox=ref(null)
let ws,typingTO
const fb=name=>`https://ui-avatars.com/api/?name=${encodeURIComponent(name||'U')}&background=e2e8f0&color=64748b`
async function loadMessages(){loading.value=true;try{const{data}=await apiGet(`/messaging/conversations/${props.conv.id}/messages/`);messages.value=Array.isArray(data)?data:(data.results||[]);await nextTick();scrollBottom()}catch{}finally{loading.value=false}}
function connectWS(){if(ws)ws.close();ws=createWS(`chat/${props.conv.id}/`);ws.onmessage=async e=>{const{type,data}=JSON.parse(e.data);if(type==='message'){messages.value.push(data);await nextTick();scrollBottom()}else if(type==='typing'&&data.user_id!==myId){typing.value=data.is_typing;if(typing.value)setTimeout(()=>typing.value=false,3000)}}}
function send(){if(!newMsg.value.trim()||!ws||ws.readyState!==1)return;ws.send(JSON.stringify({type:'message',content:newMsg.value}));newMsg.value=''}
function sendTyping(){if(!ws||ws.readyState!==1)return;ws.send(JSON.stringify({type:'typing',is_typing:true}));clearTimeout(typingTO);typingTO=setTimeout(()=>ws?.send(JSON.stringify({type:'typing',is_typing:false})),1500)}
function scrollBottom(){if(chatBox.value)chatBox.value.scrollTop=chatBox.value.scrollHeight}
watch(()=>props.conv,()=>{loadMessages();connectWS()},{immediate:true})
onUnmounted(()=>ws?.close())
</script>
<style scoped>
.typing-dot{width:8px;height:8px;background:var(--gp-muted);border-radius:50%;display:inline-block;animation:typingBounce 1.2s infinite}
@keyframes typingBounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
</style>
