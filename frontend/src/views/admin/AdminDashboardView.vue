<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Admin Overview</h2><p class="text-muted small mb-0">Platform health at a glance</p></div>
      <div class="d-flex gap-2">
        <select class="form-select form-select-sm" v-model="period" @change="fetchStats" style="width:auto">
          <option value="today">Today</option><option value="week">This Week</option>
          <option value="month">This Month</option><option value="all">All Time</option>
        </select>
        <button class="btn btn-gp btn-sm" @click="fetchStats"><i class="bi bi-arrow-clockwise me-1"></i>Refresh</button>
      </div>
    </div>

    <GpSpinner v-if="loading" />
    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-2"><StatCard label="Total Users" :value="s.users" icon="bi bi-people" color="red" /></div>
        <div class="col-6 col-lg-2"><StatCard label="Active Tutors" :value="s.tutors" icon="bi bi-person-badge" color="green" /></div>
        <div class="col-6 col-lg-2"><StatCard label="Students" :value="s.students" icon="bi bi-mortarboard" color="amber" /></div>
        <div class="col-6 col-lg-2"><StatCard label="Lessons" :value="s.lessons" icon="bi bi-calendar-check" color="blue" /></div>
        <div class="col-6 col-lg-2"><StatCard label="Revenue" :value="`GHS ${s.revenue}`" icon="bi bi-currency-dollar" color="purple" /></div>
        <div class="col-6 col-lg-2"><StatCard label="Pending" :value="s.pending_approvals" icon="bi bi-hourglass-split" color="amber" /></div>
      </div>

      <div class="row g-4 mb-4">
        <!-- Revenue chart -->
        <div class="col-lg-8">
          <div class="gp-card p-4">
            <h5 class="fw-700 mb-3"><i class="bi bi-bar-chart me-2 text-gp-primary"></i>Daily Revenue (Last 30 Days)</h5>
            <div class="d-flex align-items-end gap-px" style="height:100px;gap:2px">
              <div v-for="(d,i) in revenueChart" :key="i"
                   class="rev-bar flex-grow-1" :style="`height:${d.pct}%`"
                   :title="`${d.label}: GHS ${d.amount}`"></div>
            </div>
          </div>
        </div>
        <!-- Quick actions -->
        <div class="col-lg-4">
          <div class="gp-card p-4">
            <h5 class="fw-700 mb-3"><i class="bi bi-lightning me-2 text-gp-primary"></i>Quick Actions</h5>
            <div class="d-grid gap-2">
              <RouterLink to="/admin/tutors" class="btn btn-outline-secondary btn-sm text-start d-flex align-items-center gap-2">
                <i class="bi bi-person-badge text-gp-primary"></i>Tutor Approvals
                <span v-if="s.pending_approvals" class="badge bg-danger ms-auto">{{ s.pending_approvals }}</span>
              </RouterLink>
              <RouterLink to="/admin/disputes" class="btn btn-outline-secondary btn-sm text-start d-flex align-items-center gap-2">
                <i class="bi bi-exclamation-triangle text-warning"></i>Open Disputes
                <span v-if="s.open_disputes" class="badge bg-warning text-dark ms-auto">{{ s.open_disputes }}</span>
              </RouterLink>
              <RouterLink to="/admin/moderation" class="btn btn-outline-secondary btn-sm text-start d-flex align-items-center gap-2">
                <i class="bi bi-shield-check text-primary"></i>Pending Reviews
                <span v-if="s.pending_reviews" class="badge bg-primary ms-auto">{{ s.pending_reviews }}</span>
              </RouterLink>
              <RouterLink to="/admin/bbb" class="btn btn-outline-secondary btn-sm text-start d-flex align-items-center gap-2">
                <i class="bi bi-camera-video text-success"></i>BBB Status
                <span class="badge ms-auto" :class="bbbOnline?'bg-success':'bg-danger'">{{ bbbOnline?'Online':'Offline' }}</span>
              </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Recent users -->
        <div class="col-lg-6">
          <div class="gp-card p-4">
            <div class="d-flex justify-content-between mb-3">
              <h5 class="fw-700 mb-0"><i class="bi bi-person-plus me-2 text-gp-primary"></i>Recent Sign-ups</h5>
              <RouterLink to="/admin/users" class="btn btn-sm btn-link p-0">View all</RouterLink>
            </div>
            <div v-for="u in recentUsers.slice(0,6)" :key="u.id" class="d-flex align-items-center gap-2 mb-2 p-2 border-bottom">
              <img :src="u.avatar_url||fallback(u.full_name)" class="rounded-circle" width="32" height="32" style="object-fit:cover" />
              <div class="flex-grow-1 overflow-hidden">
                <div class="small fw-600 text-truncate">{{ u.full_name }}</div>
                <div class="text-muted" style="font-size:.7rem;text-transform:capitalize">{{ u.role }} · {{ timeAgo(u.date_joined) }}</div>
              </div>
              <span class="badge small" :class="u.is_active?'bg-success-subtle text-success':'bg-secondary-subtle text-secondary'">{{ u.is_active?'Active':'Inactive' }}</span>
            </div>
          </div>
        </div>
        <!-- Recent lessons -->
        <div class="col-lg-6">
          <div class="gp-card p-4">
            <div class="d-flex justify-content-between mb-3">
              <h5 class="fw-700 mb-0"><i class="bi bi-calendar3 me-2 text-gp-primary"></i>Recent Lessons</h5>
              <span class="text-muted small">Last 24h</span>
            </div>
            <div v-for="l in recentLessons.slice(0,6)" :key="l.id" class="d-flex align-items-center gap-2 mb-2 p-2 border-bottom">
              <div class="text-center rounded-3 p-1 flex-shrink-0" style="min-width:40px;background:rgba(230,57,0,.08)">
                <div class="fw-800 text-gp-primary" style="font-size:.9rem">{{ fmtDay(l.start_time) }}</div>
                <div class="text-muted" style="font-size:.6rem">{{ fmtMonth(l.start_time) }}</div>
              </div>
              <div class="flex-grow-1 overflow-hidden">
                <div class="small fw-600 text-truncate">{{ l.tutor_name }} → {{ l.student_name }}</div>
                <div class="text-muted" style="font-size:.7rem">{{ l.subject_name }} · GHS {{ l.price }}</div>
              </div>
              <span class="badge small" :class="statusBadge(l.status)">{{ l.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiGet } from '@/utils/api'
import { timeAgo, fmtDay, fmtMonth, statusBadge } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import StatCard  from '@/components/common/StatCard.vue'

const loading     = ref(true)
const period      = ref('month')
const bbbOnline   = ref(false)
const recentUsers = ref([])
const recentLessons = ref([])
const revenueChart= ref([])
const s           = ref({ users:0, tutors:0, students:0, lessons:0, revenue:'0.00', pending_approvals:0, open_disputes:0, pending_reviews:0 })
const fallback    = n => `https://ui-avatars.com/api/?name=${encodeURIComponent(n||'U')}&background=e2e8f0&color=64748b`

async function fetchStats() {
  loading.value = true
  try {
    const [stats, users, lessons, bbb] = await Promise.all([
      apiGet('/admin-panel/stats/', { period: period.value }),
      apiGet('/admin-panel/users/', { ordering:'-date_joined', page_size:6 }),
      apiGet('/scheduling/lessons/', { ordering:'-start_time', page_size:6 }),
      apiGet('/admin-panel/bbb/status/').catch(() => ({ data:{online:false} })),
    ])
    s.value           = { ...s.value, ...stats.data }
    recentUsers.value = users.data?.results || []
    recentLessons.value = lessons.data?.results || []
    bbbOnline.value   = bbb.data?.online ?? false
    // Build 30-day chart
    const daily = stats.data?.daily_revenue || []
    const max   = Math.max(...daily.map(d=>d.amount||0), 1)
    revenueChart.value = daily.map(d => ({ label:d.date, amount:(d.amount||0).toFixed(2), pct:Math.round((d.amount||0)/max*100) }))
  } catch(e) { console.error(e) }
  finally { loading.value = false }
}

onMounted(fetchStats)
</script>
