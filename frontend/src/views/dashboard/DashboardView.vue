<template>
  <div>
    <!-- Greeting -->
    <div class="d-flex justify-content-between align-items-start mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-800 mb-0">{{ greeting }}, {{ auth.user?.first_name }}! 👋</h2>
        <p class="text-muted small mb-0">Here's what's happening with your learning today.</p>
      </div>
      <div class="d-flex gap-2 flex-wrap">
        <RouterLink v-if="auth.isStudent" to="/tutors" class="btn btn-sm btn-gp-outline">
          <i class="bi bi-search me-1"></i>Find Tutor
        </RouterLink>
        <RouterLink v-if="auth.isTutor" to="/availability" class="btn btn-sm btn-gp">
          <i class="bi bi-clock me-1"></i>Set Availability
        </RouterLink>
      </div>
    </div>

    <GpSpinner v-if="loading" />
    <div v-else>
      <!-- Stats row -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3"><StatCard :label="'Total Lessons'" :value="stats.total_lessons" icon="bi bi-calendar-check" color="red" :sub="`+${stats.lessons_month} this month`" /></div>
        <div class="col-6 col-lg-3"><StatCard :label="auth.isTutor ? 'Hours Taught' : 'Hours Learned'" :value="stats.total_hours" icon="bi bi-clock-history" color="green" :sub="`${stats.avg_session || 0} avg/session`" /></div>
        <div class="col-6 col-lg-3"><StatCard :label="auth.isTutor ? 'Avg Rating' : 'Tutors Tried'" :value="auth.isTutor ? stats.avg_rating || '—' : stats.tutors_count || 0" icon="bi bi-star-fill" color="amber" :sub="`${stats.reviews_count || 0} reviews`" /></div>
        <div class="col-6 col-lg-3"><StatCard :label="'Day Streak'" :value="auth.user?.streak_days || 0" icon="bi bi-fire" color="blue" sub="🔥 Keep it up!" /></div>
      </div>

      <div class="row g-4">
        <!-- Upcoming lessons -->
        <div class="col-lg-7">
          <div class="gp-card p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-700 mb-0"><i class="bi bi-calendar3 me-2 text-gp-primary"></i>Upcoming Lessons</h5>
              <RouterLink to="/lessons" class="btn btn-sm btn-outline-secondary">View all</RouterLink>
            </div>
            <GpEmpty v-if="!upcoming.length && auth.isStudent" 
                 icon="bi bi-calendar-x"
                 message="No upcoming lessons."
                 action-label="Find a Tutor" 
                 action-to="/tutors" />
            <div v-for="l in upcoming.slice(0, 5)" :key="l.id"
                 class="d-flex align-items-center gap-3 p-3 rounded-3 border mb-2"
                 :class="l.can_join ? 'border-success bg-success-subtle' : ''">
              <div class="text-center rounded-3 p-2 flex-shrink-0" style="min-width:52px;background:rgba(230,57,0,.08)">
                <div class="fw-800 text-gp-primary" style="font-size:1.2rem">{{ fmtDay(l.start_time) }}</div>
                <div class="text-muted" style="font-size:.7rem">{{ fmtMonth(l.start_time) }}</div>
              </div>
              <div class="flex-grow-1 overflow-hidden">
                <div class="fw-600 text-truncate">{{ l.subject_name || 'Tutoring Session' }}</div>
                <div class="text-muted small">with {{ auth.isStudent ? l.tutor_name : l.student_name }} · {{ fmtTime(l.start_time) }}</div>
                <span class="badge small" :class="statusBadge(l.status)">{{ l.status.replace('_',' ') }}</span>
              </div>
              <div class="d-flex flex-column gap-1">
                <RouterLink v-if="l.can_join" :to="`/lessons/${l.id}/join`" class="btn btn-gp btn-sm">
                  <i class="bi bi-camera-video-fill me-1"></i>Join
                </RouterLink>
                <RouterLink :to="`/lessons`" class="btn btn-sm btn-outline-secondary">Details</RouterLink>
              </div>
            </div>
          </div>
        </div>

        <!-- Right column -->
        <div class="col-lg-5">
          <!-- AI Assistant -->
          <div class="gp-card p-4 mb-4" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)">
            <div class="d-flex align-items-center gap-3 mb-3">
              <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                   style="width:48px;height:48px;background:linear-gradient(135deg,var(--gp-red),var(--gp-amber))">
                <i class="bi bi-robot text-white fs-5"></i>
              </div>
              <div>
                <div class="fw-700">AI Study Assistant</div>
                <div class="text-muted small">Instant homework help</div>
              </div>
            </div>
            <div class="input-group mb-2">
              <input class="form-control form-control-sm" v-model="aiQ"
                     placeholder="Ask a question…" @keyup.enter="askAI" />
              <button class="btn btn-gp btn-sm" @click="askAI" :disabled="aiLoading">
                <span v-if="aiLoading" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-stars"></i>
              </button>
            </div>
            <div v-if="aiReply" class="bg-white rounded-3 p-3 small border" style="max-height:140px;overflow-y:auto">
              <i class="bi bi-robot text-gp-primary me-1"></i>{{ aiReply }}
            </div>
          </div>

          <!-- Achievements -->
          <div class="gp-card p-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-700 mb-0"><i class="bi bi-trophy me-2 text-warning"></i>Achievements</h5>
              <RouterLink to="/achievements" class="btn btn-sm btn-link p-0 small">View all</RouterLink>
            </div>
            <div class="row g-2 mb-3 text-center">
              <div class="col-4"><div class="fw-800 fs-4 text-gp-primary">{{ auth.user?.total_points || 0 }}</div><div class="text-muted small">Points</div></div>
              <div class="col-4"><div class="fw-800 fs-4 text-warning">{{ auth.user?.level || 1 }}</div><div class="text-muted small">Level</div></div>
              <div class="col-4"><div class="fw-800 fs-4 text-danger">{{ auth.user?.streak_days || 0 }}</div><div class="text-muted small">Streak</div></div>
            </div>
            <div class="d-flex flex-wrap gap-2">
              <div v-for="ub in badges.slice(0, 6)" :key="ub.id" class="text-center" :title="ub.badge?.name">
                <div class="rounded-circle d-flex align-items-center justify-content-center mx-auto"
                     :style="`width:44px;height:44px;background:${ub.badge?.color || '#e63900'}20;border:2px solid ${ub.badge?.color || '#e63900'}`">
                  <i :class="ub.badge?.icon" :style="`color:${ub.badge?.color || '#e63900'};font-size:1.1rem`"></i>
                </div>
                <div style="font-size:.6rem;margin-top:2px" class="text-muted">{{ ub.badge?.name }}</div>
              </div>
              <div v-if="!badges.length" class="text-muted small py-2">Complete lessons to earn badges!</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="gp-card p-4 mt-4">
        <h5 class="fw-700 mb-3"><i class="bi bi-lightning-fill me-2 text-warning"></i>Quick Actions</h5>
        <div class="row g-2">
          <div v-for="q in quickLinks" :key="q.to" class="col-6 col-md-3">
            <RouterLink :to="q.to" class="btn btn-outline-secondary w-100 d-flex align-items-center gap-2 small py-2">
              <i :class="q.icon" class="text-gp-primary"></i>{{ q.label }}
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDay, fmtMonth, fmtTime, statusBadge } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'
import StatCard  from '@/components/common/StatCard.vue'

const auth        = useAuthStore()
const notifStore  = useNotifStore()
const loading     = ref(true)
const upcoming    = ref([])
const badges      = ref([])
const stats       = ref({ total_lessons:0, lessons_month:0, total_hours:'0', avg_session:0 })
const aiQ         = ref('')
const aiReply     = ref('')
const aiLoading   = ref(false)

const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening'
})

const quickLinks = computed(() => auth.isTutor
  ? [
      { to:'/lessons',     label:'My Lessons',   icon:'bi bi-calendar-check' },
      { to:'/earnings',    label:'Earnings',      icon:'bi bi-wallet2' },
      { to:'/availability',label:'Availability',  icon:'bi bi-clock' },
      { to:'/my-students', label:'My Students',   icon:'bi bi-people' },
    ]
  : [
      { to:'/tutors',       label:'Find Tutors',  icon:'bi bi-search' },
      { to:'/lessons',      label:'My Lessons',   icon:'bi bi-calendar-check' },
      { to:'/knowledge-base',label:'My Notes',    icon:'bi bi-journal-richtext' },
      { to:'/achievements', label:'Achievements', icon:'bi bi-trophy' },
    ]
)

async function askAI() {
  if (!aiQ.value.trim()) return
  aiLoading.value = true; aiReply.value = ''
  try {
    const { data } = await apiPost('/ai/chat/', { message: aiQ.value })
    aiReply.value = data.response || 'No response.'
    aiQ.value = ''
  } catch { aiReply.value = 'AI unavailable right now.' }
  finally { aiLoading.value = false }
}

onMounted(async () => {
  try {
    await auth.fetchMe()
    const [lessons, badgeData] = await Promise.all([
      apiGet('/scheduling/lessons/', { ordering: '-start_time', page_size: 20 }),
      apiGet('/gamification/badges/'),
    ])
    const all = lessons.data.results || []
    upcoming.value = all.filter(l => ['confirmed', 'in_progress'].includes(l.status))
    badges.value = badgeData.data || []
    const done = all.filter(l => l.status === 'completed')
    stats.value = {
      total_lessons: all.length,
      lessons_month: all.filter(l => new Date(l.start_time) > new Date(new Date().setDate(1))).length,
      total_hours: (done.reduce((a,l) => a + (l.duration_minutes||0), 0) / 60).toFixed(1),
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>
