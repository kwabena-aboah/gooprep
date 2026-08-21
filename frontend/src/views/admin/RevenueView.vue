<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Revenue</h2><p class="text-muted small mb-0">Platform financial overview</p></div>
      <div class="d-flex gap-2">
        <select class="form-select form-select-sm" v-model="period" @change="fetch" style="width:auto">
          <option value="week">This Week</option><option value="month">This Month</option>
          <option value="quarter">This Quarter</option><option value="year">This Year</option>
        </select>
      </div>
    </div>
    <GpSpinner v-if="loading" />
    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3"><StatCard label="Gross Revenue" :value="`GHS ${stats.gross}`" icon="bi bi-cash-stack" color="red" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Platform Fees" :value="`GHS ${stats.fees}`" icon="bi bi-percent" color="green" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Tutor Payouts" :value="`GHS ${stats.payouts}`" icon="bi bi-send" color="amber" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Pending Escrow" :value="`GHS ${stats.escrow}`" icon="bi bi-safe" color="blue" /></div>
      </div>
      <div class="gp-card p-4 mb-4">
        <h5 class="fw-700 mb-3">Revenue Chart</h5>
        <div class="d-flex align-items-end gap-px" style="height:120px;gap:2px">
          <div v-for="(d,i) in chart" :key="i" class="flex-grow-1 d-flex flex-column align-items-center">
            <div class="rev-bar w-100" :style="`height:${d.pct}%`" :title="`GHS ${d.amount}`"></div>
            <div class="text-muted mt-1" style="font-size:.55rem">{{ d.label }}</div>
          </div>
        </div>
      </div>
      <div class="gp-card p-4">
        <h5 class="fw-700 mb-3">Recent Transactions</h5>
        <div class="table-responsive">
          <table class="gp-table">
            <thead><tr><th>Date</th><th>Payer</th><th>Amount</th><th>Fee</th><th>Method</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-for="t in txns" :key="t.id">
                <td class="small text-muted">{{ fmtDate(t.created_at) }}</td>
                <td class="small">{{ t.payer_name }}</td>
                <td class="fw-700">GHS {{ t.amount }}</td>
                <td class="text-success small">GHS {{ (parseFloat(t.amount)*PLATFORM_COMMISSION).toFixed(2) }}</td>
                <td class="small">{{ methodLabel(t.payment_method) }}</td>
                <td><span class="badge small" :class="t.status==='success'?'bg-success-subtle text-success':'bg-warning-subtle text-warning'">{{ t.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { PLATFORM_COMMISSION } from '@/utils/platform'
import { apiGet } from '@/utils/api'
import { fmtDate, methodLabel } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import StatCard  from '@/components/common/StatCard.vue'
const loading = ref(true); const period = ref('month')
const stats = ref({ gross:'0.00', fees:'0.00', payouts:'0.00', escrow:'0.00' })
const txns  = ref([]); const chart = ref([])
async function fetch() {
  loading.value = true
  try {
    const [s, t] = await Promise.all([apiGet('/admin-panel/revenue/', {period:period.value}), apiGet('/admin-panel/transactions/',{page_size:30})])
    stats.value = s.data || {}; txns.value = t.data?.results||[]
    const daily = s.data?.daily||[]; const max = Math.max(...daily.map(d=>d.amount||0),1)
    chart.value = daily.map(d=>({label:d.date?.slice(5),amount:(d.amount||0).toFixed(2),pct:Math.round((d.amount||0)/max*100)}))
  } catch {} finally { loading.value = false }
}
onMounted(fetch)
</script>
