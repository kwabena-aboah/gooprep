<template>
  <div>
    <h2 class="fw-800 mb-4">Earnings</h2>
    <GpSpinner v-if="loading" />
    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3"><StatCard label="Available Balance" :value="`GHS ${profile.pending_payout||'0.00'}`" icon="bi bi-wallet2" color="green" sub="Ready to withdraw" /></div>
        <div class="col-6 col-lg-3"><StatCard label="This Month" :value="`GHS ${monthEarnings}`" icon="bi bi-calendar-month" color="red" sub="This month" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Total Earned" :value="`GHS ${profile.total_earnings||'0.00'}`" icon="bi bi-graph-up" color="amber" sub="All time" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Total Paid Out" :value="`GHS ${profile.total_paid_out||'0.00'}`" icon="bi bi-send" color="blue" sub="Total withdrawn earnings" /></div>
      </div>

      <!-- Chart row -->
      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <div class="gp-card p-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-700 mb-0"><i class="bi bi-bar-chart me-2 text-gp-primary"></i>Monthly Earnings</h5>
              <select class="form-select form-select-sm" v-model="chartYear" style="width:auto" @change="buildChart">
                <option v-for="y in [2024,2025,2026]" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <div class="d-flex align-items-end gap-1" style="height:120px">
              <div v-for="(m,i) in monthlyData" :key="i" class="flex-grow-1 d-flex flex-column align-items-center">
                <div class="rev-bar w-100" :style="`height:${m.pct}%`" :title="`GHS ${m.amount}`"></div>
                <div class="text-muted mt-1" style="font-size:.6rem">{{ m.label }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="gp-card p-4">
            <h5 class="fw-700 mb-3"><i class="bi bi-pie-chart me-2 text-gp-primary"></i>Revenue Split</h5>
            <div v-for="item in revSplit" :key="item.label" class="mb-3">
              <div class="d-flex justify-content-between small mb-1">
                <span>{{ item.label }}</span><span class="fw-600">{{ item.pct }}%</span>
              </div>
              <div class="gp-progress"><div class="gp-progress-bar" :style="`width:${item.pct}%;background:${item.color}`"></div></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Transactions -->
      <div class="gp-card p-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-700 mb-0"><i class="bi bi-receipt me-2 text-gp-primary"></i>Transaction History</h5>
          <button class="btn btn-gp btn-sm" @click="showPayout=true"
                  :disabled="parseFloat(profile.pending_payout||0)<50">
            <i class="bi bi-send me-1"></i>Request Payout
          </button>
        </div>
        <GpEmpty v-if="!txns.length" icon="bi bi-receipt" message="No earnings yet. Book your first lesson!" />
        <div v-else class="table-responsive">
          <table class="gp-table">
            <thead><tr><th>Date</th><th>Student</th><th>Subject</th><th>Duration</th><th>Gross</th><th>Net ({{ Math.round(TUTOR_SHARE * 100) }}%)</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-for="t in txns" :key="t.id">
                <td class="small text-muted">{{ fmtDate(t.created_at) }}</td>
                <td class="small fw-600">{{ t.payer_name }}</td>
                <td class="small">{{ t.lesson_subject || '—' }}</td>
                <td class="small text-muted">{{ t.lesson_duration || '—' }} min</td>
                <td class="small fw-600">GHS {{ t.amount }}</td>
                <td class="fw-700 text-success">GHS {{ (parseFloat(t.amount)*TUTOR_SHARE).toFixed(2) }}</td>
                <td><span class="badge small" :class="t.status==='success'?'bg-success-subtle text-success':'bg-warning-subtle text-warning'">{{ t.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Payout modal -->
    <div class="modal fade" :class="{show:showPayout}" :style="showPayout?'display:block':''" v-if="showPayout">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title fw-700">Request Payout</h5><button class="btn-close" @click="showPayout=false"></button></div>
          <div class="modal-body">
            <div class="alert alert-success small"><i class="bi bi-wallet2 me-1"></i>Available: <strong>GHS {{ profile.pending_payout }}</strong></div>
            <div class="mb-3"><label class="form-label small fw-600">Amount (GHS) *</label><input type="number" class="form-control" v-model="pf.amount" :max="profile.pending_payout" min="50" /></div>
            <div class="mb-3"><label class="form-label small fw-600">Method *</label>
              <select class="form-select" v-model="pf.method">
                <option value="mtn_momo">MTN MoMo</option>
                <option value="at_momo">AirtelTigo Money</option>
                <option value="tel_cash">Telecel Cash</option>
                <option value="bank">Bank Transfer</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label small fw-600">{{ pf.method==='bank'?'Account':'Mobile' }} Number *</label><input class="form-control" v-model="pf.number" placeholder="0240000000" /></div>
            <button class="btn btn-gp w-100" @click="submitPayout" :disabled="pf.submitting||parseFloat(pf.amount)<50">
              <span v-if="pf.submitting" class="spinner-border spinner-border-sm me-1"></span>Confirm Payout
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showPayout" @click="showPayout=false"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDate } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'
import StatCard  from '@/components/common/StatCard.vue'
import { PLATFORM_COMMISSION, TUTOR_SHARE } from '@/utils/platform'

const notifStore = useNotifStore()
const loading    = ref(true)
const profile    = ref({})
const txns       = ref([])
const showPayout = ref(false)
const chartYear  = ref(new Date().getFullYear())
const monthlyData= ref([])
const pf         = ref({ amount:'', method:'mtn_momo', number:'', submitting:false })

const MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

const monthEarnings = computed(() => {
  const m = new Date().getMonth(), y = new Date().getFullYear()
  return txns.value
    .filter(t => { const d = new Date(t.created_at); return d.getMonth()===m && d.getFullYear()===y && t.status==='success' })
    .reduce((a,t) => a+parseFloat(t.amount)*TUTOR_SHARE, 0).toFixed(2)
})

const revSplit = computed(() => {
  const total = parseFloat(profile.value.total_earnings||0)
  return [
    { label:`Your earnings (${Math.round(TUTOR_SHARE*100)}%)`, pct:TUTOR_SHARE*100, color:'var(--gp-red)' },
    { label:`Platform fee (${Math.round(PLATFORM_COMMISSION*100)}%)`, pct:PLATFORM_COMMISSION*100, color:'var(--gp-amber)' },
  ]
})

function buildChart() {
  const byMonth = Array(12).fill(0)
  txns.value.filter(t => t.status==='success' && new Date(t.created_at).getFullYear()===chartYear.value)
    .forEach(t => { byMonth[new Date(t.created_at).getMonth()] += parseFloat(t.amount)*TUTOR_SHARE })
  const max = Math.max(...byMonth, 1)
  monthlyData.value = byMonth.map((v,i) => ({ amount: v.toFixed(2), pct: Math.round(v/max*100), label: MONTH_LABELS[i] }))
}

async function submitPayout() {
  pf.value.submitting = true
  try {
    await apiPost('/payments/payouts/', { amount:pf.value.amount, method:pf.value.method, details:{number:pf.value.number} })
    showPayout.value = false
    notifStore.toast('Payout requested! 24–48h processing.', 'success')
    const p = await apiGet('/tutors/my-profile/'); profile.value = p.data || {}
  } catch(e) { notifStore.toast(Object.values(e.response?.data||{}).flat().join(' ')||'Failed.','error') }
  finally { pf.value.submitting = false }
}

onMounted(async () => {
  try {
    const [p, t] = await Promise.all([ apiGet('/tutors/my-profile/'), apiGet('/payments/transactions/') ])
    profile.value = p.data || {}; txns.value = t.data?.results || []
    buildChart()
  } catch {} finally { loading.value = false }
})
</script>
