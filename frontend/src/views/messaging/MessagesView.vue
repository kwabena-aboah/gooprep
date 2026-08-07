<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2 class="fw-800 mb-0">Messages</h2>
      <button class="btn btn-gp btn-sm" @click="showNewConv = true">
        <i class="bi bi-plus me-1"></i>New Message
      </button>
    </div>

    <div class="gp-card overflow-hidden" style="height:calc(100vh - 180px);display:flex">
      <!-- Conversation list -->
      <div class="border-end" :class="activeConv ? 'd-none d-lg-flex' : 'd-flex'"
           style="width:300px;flex-shrink:0;flex-direction:column">
        <div class="p-2 border-bottom">
          <div class="input-group input-group-sm">
            <span class="input-group-text"><i class="bi bi-search text-muted"></i></span>
            <input class="form-control" v-model="search" placeholder="Search conversations…" />
          </div>
        </div>
        <div class="overflow-y-auto flex-grow-1">
          <GpSpinner v-if="loading" height="120px" />
          <div v-else-if="!filtered.length" class="text-center p-4 text-muted small">
            <i class="bi bi-chat-dots d-block fs-2 mb-1 opacity-25"></i>No conversations yet
          </div>
          <div v-else>
            <div v-for="c in filtered" :key="c.id"
                 class="d-flex align-items-center gap-2 p-3 border-bottom"
                 :class="activeConv?.id===c.id?'bg-light':''"
                 style="cursor:pointer" @click="openConv(c)">
              <div class="position-relative flex-shrink-0">
                <img :src="c.other_user?.avatar || fallback(c.other_user?.name)" class="rounded-circle"
                     width="42" height="42" style="object-fit:cover" />
                <span v-if="c.other_user?.is_online" class="position-absolute bottom-0 end-0 online-dot" style="width:9px;height:9px"></span>
              </div>
              <div class="flex-grow-1 overflow-hidden">
                <div class="d-flex justify-content-between">
                  <span class="fw-600 small text-truncate">{{ c.other_user?.name }}</span>
                  <span class="text-muted flex-shrink-0" style="font-size:.65rem">{{ timeAgo(c.last_message_at) }}</span>
                </div>
                <div class="text-muted small text-truncate" style="font-size:.8rem">{{ c.last_message || 'Start a conversation' }}</div>
              </div>
              <span v-if="c.unread_count>0" class="badge bg-primary rounded-pill ms-1 flex-shrink-0">{{ c.unread_count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat area -->
      <div class="flex-grow-1 overflow-hidden" :class="!activeConv ? 'd-none d-lg-flex' : 'd-flex'" style="flex-direction:column">
        <div v-if="!activeConv" class="flex-grow-1 d-flex flex-column align-items-center justify-content-center text-muted">
          <i class="bi bi-chat-dots-fill mb-3" style="font-size:3rem;color:var(--gp-red);opacity:.3"></i>
          <p class="small">Select a conversation or start a new one</p>
          <button class="btn btn-gp btn-sm" @click="showNewConv=true">
            <i class="bi bi-plus me-1"></i>New Message
          </button>
        </div>
        <ChatWindow v-else :conv="activeConv" @back="activeConv=null" />
      </div>
    </div>

    <!-- New conversation modal -->
    <div class="modal fade" :class="{show:showNewConv}" :style="showNewConv?'display:block':''" v-if="showNewConv">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-700">New Message</h5>
            <button class="btn-close" @click="showNewConv=false"></button>
          </div>
          <div class="modal-body">
            <label class="form-label small fw-600">Search for a tutor or student</label>
            <input class="form-control mb-3" v-model="userSearch" placeholder="Type a name or email…" @input="searchUsers" />
            <div v-for="u in userResults" :key="u.id"
                 class="d-flex align-items-center gap-2 p-2 rounded border-bottom"
                 style="cursor:pointer" @click="startConv(u)">
              <img :src="u.avatar_url || fallback(u.full_name)" class="rounded-circle" width="36" height="36" style="object-fit:cover" />
              <div class="flex-grow-1">
                <div class="fw-600 small">{{ u.full_name }}</div>
                <div class="text-muted" style="font-size:.75rem;text-transform:capitalize">{{ u.role }}</div>
              </div>
              <span class="btn btn-sm btn-gp">Message</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showNewConv" @click="showNewConv=false"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiGet, apiPost } from '@/utils/api'
import { timeAgo, debounce } from '@/utils/helpers'
import GpSpinner  from '@/components/common/GpSpinner.vue'
import ChatWindow from '@/components/messaging/ChatWindow.vue'

const route       = useRoute()
const auth        = useAuthStore()
const convs       = ref([])
const activeConv  = ref(null)
const loading     = ref(true)
const search      = ref('')
const showNewConv = ref(false)
const userSearch  = ref('')
const userResults = ref([])

const filtered = computed(() => {
  if (!search.value) return convs.value
  const q = search.value.toLowerCase()
  return convs.value.filter(c => (c.other_user?.name||'').toLowerCase().includes(q))
})

const fallback = name => `https://ui-avatars.com/api/?name=${encodeURIComponent(name||'U')}&background=e2e8f0&color=64748b`

async function loadConvs() {
  loading.value = true
  try {
    const { data } = await apiGet('/messaging/conversations/')
    convs.value = data.results || []
  } catch {} finally { loading.value = false }
}

function openConv(c) {
  activeConv.value = c
  c.unread_count = 0
}

const searchUsers = debounce(async () => {
  if (!userSearch.value.trim()) { userResults.value = []; return }
  try {
    const { data } = await apiGet('/auth/users/', { search: userSearch.value, page_size: 8 })
    userResults.value = (data.results || []).filter(u => u.id !== auth.user?.id)
  } catch { userResults.value = [] }
}, 350)

async function startConv(u) {
  try {
    const { data } = await apiPost('/messaging/conversations/', { user_id: u.id })
    showNewConv.value = false; userSearch.value = ''; userResults.value = []
    await loadConvs()
    const conv = convs.value.find(c => c.id === data.id) || data
    openConv(conv)
  } catch {}
}

onMounted(async () => {
  await loadConvs()
  const tutorId = route.query.tutor
  if (tutorId) {
    try {
      const { data } = await apiPost('/messaging/conversations/', { user_id: tutorId })
      await loadConvs()
      const c = convs.value.find(x => x.id === data.id) || data
      openConv(c)
    } catch {}
  }
})
</script>
