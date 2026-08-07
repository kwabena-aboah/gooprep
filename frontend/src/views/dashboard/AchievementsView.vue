<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div><h2 class="fw-800 mb-0">Achievements</h2><p class="text-muted small mb-0">Your learning milestones and rewards</p></div>
      <RouterLink to="/leaderboard" class="btn btn-gp btn-sm"><i class="bi bi-trophy me-1"></i>Leaderboard</RouterLink>
    </div>
    <GpSpinner v-if="loading" />
    <div v-else>
      <!-- XP bar -->
      <div class="gp-card p-4 mb-4" style="background:linear-gradient(135deg,#111,#1a0800)">
        <div class="row align-items-center g-3">
          <div class="col-auto">
            <div class="rounded-circle d-flex align-items-center justify-content-center fw-800 text-white"
                 style="width:80px;height:80px;background:linear-gradient(135deg,var(--gp-red),var(--gp-amber));font-size:2rem;font-family:'Plus Jakarta Sans',sans-serif">
              {{ auth.user?.level || 1 }}
            </div>
          </div>
          <div class="col text-white">
            <div class="fw-700 fs-5 mb-1">Level {{ auth.user?.level || 1 }} — {{ levelTitle }}</div>
            <div class="d-flex align-items-center gap-2 mb-1">
              <div class="gp-progress flex-grow-1" style="height:12px;background:rgba(255,255,255,.15)">
                <div class="gp-progress-bar" :style="`width:${xpPct}%`"></div>
              </div>
              <span class="text-white-50 small">{{ xpIn }}/500 XP</span>
            </div>
            <div class="text-white-50 small">{{ 500 - xpIn }} XP to Level {{ (auth.user?.level||1)+1 }}</div>
          </div>
          <div class="col-auto text-center text-white">
            <div class="fw-800 fs-2" style="color:var(--gp-amber)">{{ (auth.user?.total_points||0).toLocaleString() }}</div>
            <div class="text-white-50 small">Total Points</div>
          </div>
          <div class="col-auto text-center text-white">
            <div class="fw-800 fs-2 text-danger">{{ auth.user?.streak_days || 0 }}</div>
            <div class="text-white-50 small">🔥 Day Streak</div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-8">
          <!-- Badges -->
          <div class="gp-card p-4 mb-4">
            <h5 class="fw-700 mb-4"><i class="bi bi-award-fill me-2 text-warning"></i>Badges ({{ badges.length }})</h5>
            <GpEmpty v-if="!badges.length" icon="bi bi-award" message="Complete lessons to earn badges!" />
            <div v-else class="row g-3">
              <div v-for="ub in badges" :key="ub.id" class="col-6 col-md-4 col-lg-3">
                <div class="text-center p-3 rounded-3 border"
                     :style="`background:${ub.badge?.color||'#e63900'}08;border-color:${ub.badge?.color||'#e63900'}40!important`">
                  <div class="rounded-circle d-flex align-items-center justify-content-center mx-auto mb-2"
                       :style="`width:56px;height:56px;background:${ub.badge?.color||'#e63900'}20;border:2px solid ${ub.badge?.color||'#e63900'}`">
                    <i :class="ub.badge?.icon" class="fs-3" :style="`color:${ub.badge?.color||'#e63900'}`"></i>
                  </div>
                  <div class="fw-600 small">{{ ub.badge?.name }}</div>
                  <div class="text-muted" style="font-size:.7rem">{{ timeAgo(ub.earned_at) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Points history -->
          <div class="gp-card p-4">
            <h5 class="fw-700 mb-4"><i class="bi bi-clock-history me-2 text-gp-primary"></i>Points History</h5>
            <GpEmpty v-if="!history.length" icon="bi bi-trophy" message="No points earned yet." />
            <div v-else>
              <div v-for="h in history.slice(0,15)" :key="h.created_at"
                   class="d-flex align-items-center gap-3 p-2 border-bottom">
                <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                     :style="`width:36px;height:36px;background:${h.points>0?'#dcfce7':'#fee2e2'}`">
                  <i class="bi" :class="h.points > 0 ? 'bi-plus-circle-fill text-success' : 'bi-dash-circle-fill text-danger'"></i>
                </div>
                <div class="flex-grow-1 overflow-hidden">
                  <div class="small fw-600 text-truncate">{{ h.description || h.action }}</div>
                  <div class="text-muted" style="font-size:.7rem">{{ timeAgo(h.created_at) }}</div>
                </div>
                <span class="fw-800 small" :class="h.points>0?'text-success':'text-danger'">
                  {{ h.points > 0 ? '+' : '' }}{{ h.points }} XP
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Leaderboard + Streak -->
        <div class="col-lg-4">
          <div class="gp-card p-4 mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-700 mb-0"><i class="bi bi-bar-chart-steps me-2 text-gp-primary"></i>Leaderboard</h5>
              <select class="form-select form-select-sm" v-model="lbRole" @change="fetchLB" style="width:auto">
                <option value="student">Students</option>
                <option value="tutor">Tutors</option>
              </select>
            </div>
            <div v-if="lbLoading" class="text-center py-3"><div class="spinner-border spinner-border-sm text-gp-primary"></div></div>
            <div v-else>
              <div v-if="myRank" class="mb-3 p-2 rounded-3 text-center" style="background:rgba(230,57,0,.08)">
                <div class="text-muted small">Your rank</div>
                <div class="fw-800 fs-3 text-gp-primary">#{{ myRank }}</div>
              </div>
              <div v-for="e in leaderboard.slice(0,10)" :key="e.rank"
                   class="lb-row" :class="{ me: e.is_me }">
                <div class="fw-700 text-center" style="width:28px;font-size:.9rem">
                  {{ e.rank===1?'🥇':e.rank===2?'🥈':e.rank===3?'🥉':'#'+e.rank }}
                </div>
                <img :src="e.avatar || fallback(e.name)" class="rounded-circle" width="32" height="32" style="object-fit:cover" />
                <div class="flex-grow-1 overflow-hidden">
                  <div class="small fw-600 text-truncate">{{ e.name }}
                    <span v-if="e.is_me" class="badge bg-primary-subtle text-primary ms-1 small">You</span>
                  </div>
                  <div class="text-muted" style="font-size:.65rem">Level {{ e.level }} · 🔥{{ e.streak }}</div>
                </div>
                <span class="fw-700 text-gp-primary small">{{ (e.points||0).toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <!-- Streak -->
          <div class="gp-card p-4" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)">
            <h5 class="fw-700 mb-3"><i class="bi bi-fire me-2 text-danger"></i>Daily Streak</h5>
            <div class="text-center mb-3">
              <div class="fw-800 text-danger" style="font-size:3rem">{{ auth.user?.streak_days || 0 }}</div>
              <div class="text-muted small">consecutive days</div>
            </div>
            <div class="d-flex justify-content-between mb-3">
              <div v-for="(day,i) in ['M','T','W','T','F','S','S']" :key="i" class="text-center">
                <div class="small text-muted mb-1">{{ day }}</div>
                <div class="rounded-circle mx-auto"
                     :style="`width:24px;height:24px;background:${i<(auth.user?.streak_days||0)%7?'var(--gp-red)':'#e2e8f0'}`"></div>
              </div>
            </div>
            <RouterLink to="/tutors" class="btn btn-gp btn-sm w-100">
              <i class="bi bi-lightning-fill me-1"></i>Book Now to Keep Streak
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
import { apiGet } from '@/utils/api'
import { timeAgo } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'

const auth      = useAuthStore()
const loading   = ref(true)
const lbLoading = ref(false)
const badges    = ref([])
const history   = ref([])
const leaderboard = ref([])
const myRank    = ref(null)
const lbRole    = ref('student')

const xpIn     = computed(() => (auth.user?.total_points || 0) % 500)
const xpPct    = computed(() => Math.round(xpIn.value / 5))
const titles   = ['Beginner','Explorer','Learner','Achiever','Scholar','Expert','Master','Champion','Legend','Grand Master']
const levelTitle = computed(() => titles[Math.min((auth.user?.level||1)-1, titles.length-1)])
const fallback = name => `https://ui-avatars.com/api/?name=${encodeURIComponent(name||'U')}&background=e2e8f0&color=64748b`

async function fetchLB() {
  lbLoading.value = true
  try {
    const { data } = await apiGet('/gamification/leaderboard/', { role: lbRole.value })
    leaderboard.value = data.entries || []
    myRank.value = data.my_rank || null
  } catch {} finally { lbLoading.value = false }
}

onMounted(async () => {
  try {
    const [b, pts] = await Promise.all([
      apiGet('/gamification/badges/'),
      apiGet('/gamification/points/'),
    ])
    badges.value  = b.data || []
    history.value = pts.data?.history || []
    await fetchLB()
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>
