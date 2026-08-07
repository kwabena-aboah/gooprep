<template>
  <!-- Full-screen room — no sidebar/navbar injected by App.vue for this route -->
  <div id="room-wrap" style="height:100vh;display:flex;flex-direction:column;background:#0a0a0a">
    <!-- Top bar -->
    <div style="height:52px;background:#111;display:flex;align-items:center;padding:0 1rem;gap:.75rem;flex-shrink:0;border-bottom:1px solid #222">
      <img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:28px" />
      <div v-if="lesson" class="text-white small flex-grow-1">
        <strong style="color:var(--gp-amber)">{{ lesson.subject_name || 'Tutoring Session' }}</strong>
        <span class="text-white-50 mx-2">·</span>
        <span>with {{ auth.isStudent ? lesson.tutor_name : lesson.student_name }}</span>
        <span class="text-white-50 mx-2">·</span>
        <span>{{ lesson.duration_minutes }} min</span>
      </div>
      <div class="d-flex align-items-center gap-2">
        <span v-if="isLive" class="badge bg-danger d-flex align-items-center gap-1">
          <span class="rounded-circle bg-white d-inline-block" style="width:7px;height:7px;animation:pulse 1s infinite"></span>LIVE
        </span>
        <span v-if="elapsed" class="text-white-50 small">{{ elapsed }}</span>
        <button class="btn btn-sm btn-outline-danger ms-2" @click="endOrExit">
          <i class="bi me-1" :class="auth.isTutor?'bi-stop-circle':'bi-x-circle'"></i>
          {{ auth.isTutor ? 'End Lesson' : 'Leave' }}
        </button>
      </div>
    </div>

    <!-- Pre-join screen -->
    <div v-if="!joined" class="flex-grow-1 d-flex flex-column align-items-center justify-content-center gap-4"
         style="background:radial-gradient(ellipse at center,#1a0800 0%,#0a0a0a 70%)">
      <div class="rounded-circle d-flex align-items-center justify-content-center"
           style="width:120px;height:120px;border:3px solid var(--gp-red);animation:pulseRing 2s ease-out infinite">
        <i class="bi bi-camera-video-fill text-white" style="font-size:2.5rem"></i>
      </div>

      <div class="text-center" v-if="lesson">
        <h4 class="text-white fw-700 mb-1">{{ lesson.subject_name || 'Tutoring Session' }}</h4>
        <p class="text-white-50 small">with {{ auth.isStudent ? lesson.tutor_name : lesson.student_name }}</p>
      </div>

      <div class="text-center text-white" v-if="!canJoin">
        <div class="fw-800" style="font-size:2.5rem;font-family:'Plus Jakarta Sans',sans-serif">{{ countdown }}</div>
        <div class="text-white-50 small">until lesson starts</div>
      </div>
      <div v-else class="text-success fw-600"><i class="bi bi-check-circle me-2"></i>Ready to join!</div>

      <div class="d-flex gap-4 flex-wrap justify-content-center">
        <div class="form-check form-switch" style="color:#94a3b8">
          <input class="form-check-input" type="checkbox" v-model="withCam" />
          <label class="form-check-label small"><i class="bi bi-camera-video me-1"></i>Camera</label>
        </div>
        <div class="form-check form-switch" style="color:#94a3b8">
          <input class="form-check-input" type="checkbox" v-model="withMic" />
          <label class="form-check-label small"><i class="bi bi-mic me-1"></i>Microphone</label>
        </div>
      </div>

      <div v-if="error" class="alert alert-danger text-center" style="max-width:400px">
        <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
      </div>

      <div class="d-flex gap-3">
        <button class="btn btn-gp btn-lg px-5" @click="joinRoom"
                :disabled="joinLoading || (!canJoin && !auth.isTutor)">
          <span v-if="joinLoading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-camera-video-fill me-2"></i>Join Classroom
        </button>
        <RouterLink to="/lessons" class="btn btn-outline-light btn-lg">
          <i class="bi bi-x me-1"></i>Cancel
        </RouterLink>
      </div>

      <p class="text-white-50 small d-flex align-items-center gap-2">
        <i class="bi bi-shield-check text-success"></i>Secured by Gooprep · End-to-end encrypted
      </p>
    </div>

    <!-- BBB iframe -->
    <iframe v-if="joined && joinUrl" :src="joinUrl" style="flex:1;border:none;width:100%"
            allow="camera; microphone; display-capture; fullscreen; autoplay; clipboard-read; clipboard-write"
            allowfullscreen></iframe>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost, createWS } from '@/utils/api'

const route      = useRoute()
const router     = useRouter()
const auth       = useAuthStore()
const notifStore = useNotifStore()
const lessonId   = route.params.id
const lesson     = ref(null)
const joinUrl    = ref('')
const joined     = ref(false)
const joinLoading = ref(false)
const error      = ref('')
const isLive     = ref(false)
const elapsed    = ref('')
const canJoin    = ref(false)
const countdown  = ref('')
const withCam    = ref(true)
const withMic    = ref(true)
let elapsedTimer, countdownTimer, ws

function fmt(s) {
  const h = Math.floor(s/3600), m = Math.floor((s%3600)/60), sec = s%60
  return h > 0 ? `${h}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}` : `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`
}

function updateCountdown() {
  if (!lesson.value) return
  const now   = new Date()
  const start = new Date(lesson.value.start_time)
  const win   = new Date(start.getTime() - 10*60000)
  canJoin.value = now >= win
  const diff  = start - now
  if (diff <= 0) { countdown.value = 'Now'; canJoin.value = true; return }
  const h = Math.floor(diff/3600000), m = Math.floor((diff%3600000)/60000), s = Math.floor((diff%60000)/1000)
  countdown.value = h > 0 ? `${h}h ${m}m` : m > 0 ? `${m}m ${s}s` : `${s}s`
}

function connectWS() {
  ws = createWS(`lessons/${lessonId}/status/`)
  ws.onmessage = e => {
    const d = JSON.parse(e.data)
    if (d.lesson_status === 'completed') router.push('/lessons?ended=1')
  }
}

async function joinRoom() {
  joinLoading.value = true; error.value = ''
  try {
    const { data } = await apiPost(`/scheduling/lessons/${lessonId}/join/`)
    if (data?.join_url) {
      joinUrl.value = data.join_url; joined.value = true; isLive.value = true
      const start = Date.now()
      elapsedTimer = setInterval(() => { elapsed.value = fmt(Math.floor((Date.now()-start)/1000)) }, 1000)
      connectWS()
    } else { error.value = data?.error || 'Could not get classroom link.' }
  } catch(e) { error.value = e.response?.data?.error || 'Failed to connect. Please try again.' }
  finally { joinLoading.value = false }
}

async function endOrExit() {
  if (auth.isTutor) {
    if (!confirm('End this lesson for all participants?')) return
    try { await apiPost(`/scheduling/lessons/${lessonId}/end/`) } catch {}
  }
  router.push('/lessons')
}

onMounted(async () => {
  if (!lessonId) { router.push('/lessons'); return }
  try {
    const { data } = await apiGet(`/scheduling/lessons/${lessonId}/`)
    lesson.value = data
    if (data.status === 'in_progress') canJoin.value = true
    updateCountdown()
    countdownTimer = setInterval(updateCountdown, 1000)
  } catch { error.value = 'Could not load lesson details.' }
})

onUnmounted(() => {
  clearInterval(elapsedTimer); clearInterval(countdownTimer); ws?.close()
})
</script>

<style>
@keyframes pulseRing {
  0%   { box-shadow: 0 0 0 0 rgba(230,57,0,.5); }
  70%  { box-shadow: 0 0 0 24px rgba(230,57,0,0); }
  100% { box-shadow: 0 0 0 0 rgba(230,57,0,0); }
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
</style>
