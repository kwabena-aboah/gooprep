<template>
  <div>
    <h2 class="fw-800 mb-4">Payments & Billing</h2>
    <GpSpinner v-if="loading" />
    <div v-else>
      <!-- Stat cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3"><StatCard label="Total Spent" :value="`GHS ${summary.total_spent}`" icon="bi bi-wallet2" color="red" sub="Lifetime" /></div>
        <div v-if="auth.isTutor" class="col-6 col-lg-3"><StatCard label="Available" :value="`GHS ${tutorProfile.pending_payout||'0.00'}`" icon="bi bi-cash-coin" color="green" sub="Ready to withdraw" /></div>
        <div v-if="auth.isTutor" class="col-6 col-lg-3"><StatCard label="Total Earned" :value="`GHS ${tutorProfile.total_earnings||'0.00'}`" icon="bi bi-graph-up" color="amber" sub="All time" /></div>
        <div class="col-6 col-lg-3"><StatCard :label="auth.isTutor?'Paid Out':'Current Plan'" :value="auth.isTutor?`GHS ${tutorProfile.total_paid_out||'0.00'}`:(auth.user?.subscription_plan||'Free')" icon="bi bi-star" color="blue" /></div>
      </div>

      <!-- Tabs -->
      <div class="gp-card">
        <ul class="nav nav-tabs px-4 pt-3">
          <li v-for="t in tabs" :key="t.key" class="nav-item">
            <button class="nav-link small fw-600" :class="{active:tab===t.key}" @click="tab=t.key">
              <i :class="t.icon" class="me-1"></i>{{ t.label }}
            </button>
          </li>
        </ul>
        <div class="p-4">
          <!-- Transactions -->
          <div v-if="tab==='txns'">
            <GpEmpty v-if="!txns.length" icon="bi bi-receipt" message="No transactions yet." />
            <div v-else class="table-responsive">
              <table class="gp-table">
                <thead><tr><th>Date</th><th>Description</th><th>Method</th><th>Amount</th><th>Status</th></tr></thead>
                <tbody>
                  <tr v-for="t in txns" :key="t.id">
                    <td class="small text-muted">{{ fmtDate(t.created_at) }}</td>
                    <td class="small">{{ t.description || 'Lesson payment' }}</td>
                    <td><span class="badge bg-light text-dark border small">{{ methodLabel(t.payment_method) }}</span></td>
                    <td class="fw-600">GHS {{ t.amount }}</td>
                    <td><span class="badge small" :class="t.status==='success'?'bg-success-subtle text-success':t.status==='pending'?'bg-warning-subtle text-warning':'bg-danger-subtle text-danger'">{{ t.status }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Payouts (tutor only) -->
          <div v-if="tab==='payouts' && auth.isTutor">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="fw-700 mb-0">Payout History</h6>
              <button class="btn btn-gp btn-sm" @click="showPayoutModal=true" :disabled="parseFloat(tutorProfile.pending_payout||0)<50">
                <i class="bi bi-send me-1"></i>Request Payout
              </button>
            </div>
            <GpEmpty v-if="!payouts.length" icon="bi bi-wallet2" message="No payouts yet." />
            <div v-else class="table-responsive">
              <table class="gp-table">
                <thead><tr><th>Date</th><th>Method</th><th>Amount</th><th>Status</th></tr></thead>
                <tbody>
                  <tr v-for="p in payouts" :key="p.id">
                    <td class="small text-muted">{{ fmtDate(p.requested_at) }}</td>
                    <td class="small">{{ p.payout_method }}</td>
                    <td class="fw-600">GHS {{ p.amount }}</td>
                    <td><span class="badge small" :class="p.status==='completed'?'bg-success-subtle text-success':p.status==='processing'?'bg-info-subtle text-info':'bg-warning-subtle text-warning'">{{ p.status }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Disputes -->
          <div v-if="tab==='disputes'">
            <GpEmpty v-if="!disputes.length" icon="bi bi-shield-check" message="No disputes. All clear! ✓" />
            <div v-for="d in disputes" :key="d.id" class="gp-card p-3 mb-2">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <div class="fw-600 small">Lesson dispute</div>
                  <div class="text-muted small mt-1">{{ d.reason }}</div>
                  <div class="text-muted" style="font-size:.7rem">{{ fmtDate(d.created_at) }}</div>
                </div>
                <span class="badge" :class="d.status==='resolved'?'bg-success-subtle text-success':'bg-warning-subtle text-warning'">{{ d.status }}</span>
              </div>
              <div v-if="d.resolution" class="alert alert-info small mt-2 mb-0 py-2">
                <i class="bi bi-check-circle me-1"></i>{{ d.resolution }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payout modal -->
    <div class="modal fade" id="payoutModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title fw-700">Request Payout</h5><button class="btn-close" data-bs-dismiss="modal"></button></div>
          <div class="modal-body">
            <div class="alert alert-info small"><i class="bi bi-info-circle me-1"></i>Available: <strong>GHS {{ tutorProfile.pending_payout || 0 }}</strong>. Min GHS 50.</div>
            <div class="mb-3"><label class="form-label small fw-600">Amount (GHS)</label><input type="number" class="form-control" v-model="payoutForm.amount" :max="tutorProfile.pending_payout" min="50" /></div>
            <div class="mb-3"><label class="form-label small fw-600">Method</label>
              <select class="form-select" v-model="payoutForm.method">
                <option value="mtn_momo">MTN MoMo</option>
                <option value="at_momo">AirtelTigo Money</option>
                <option value="tel_cash">Telecel Cash</option>
                <option value="bank">Bank Transfer</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label small fw-600">{{ payoutForm.method==='bank'?'Account':'Mobile' }} Number</label><input class="form-control" v-model="payoutForm.number" placeholder="0240000000" /></div>
            <button class="btn btn-gp w-100" @click="submitPayout" :disabled="payoutForm.loading||parseFloat(payoutForm.amount)<50">
              <span v-if="payoutForm.loading" class="spinner-border spinner-border-sm me-1"></span>Confirm Payout
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Modal } from 'bootstrap'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDate, methodLabel } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'
import StatCard  from '@/components/common/StatCard.vue'

const auth        = useAuthStore()
const notifStore  = useNotifStore()
const loading     = ref(true)
const tab         = ref('txns')
const txns        = ref([])
const payouts     = ref([])
const disputes    = ref([])
const tutorProfile= ref({})
const payoutForm  = ref({ amount:'', method:'mtn_momo', number:'', loading:false })
const showPayoutModal = ref(false)

const summary = computed(() => ({
  total_spent: txns.value.filter(t=>t.status==='success').reduce((a,t)=>a+parseFloat(t.amount),0).toFixed(2)
}))

const tabs = computed(() => {
  const t = [{ key:'txns',     label:'Transactions', icon:'bi bi-receipt' }]
  if (auth.isTutor) t.push({ key:'payouts', label:'Payouts', icon:'bi bi-send' })
  t.push({ key:'disputes', label:'Disputes', icon:'bi bi-exclamation-triangle' })
  return t
})

watch(showPayoutModal, val => {
  if (val) new Modal(document.getElementById('payoutModal')).show()
})

async function submitPayout() {
  if (parseFloat(payoutForm.value.amount) < 50) { notifStore.toast('Min GHS 50.', 'error'); return }
  payoutForm.value.loading = true
  try {
    await apiPost('/payments/payouts/', { amount: payoutForm.value.amount, method: payoutForm.value.method, details: { number: payoutForm.value.number } })
    Modal.getInstance(document.getElementById('payoutModal'))?.hide()
    notifStore.toast('Payout requested! Processing in 24-48h.', 'success')
    const po = await apiGet('/payments/payouts/'); payouts.value = po.data?.results || []
  } catch(e) { notifStore.toast(Object.values(e.response?.data||{}).flat().join(' ')||'Failed.', 'error') }
  finally { payoutForm.value.loading = false; showPayoutModal.value = false }
}

onMounted(async () => {
  try {
    const [t, d] = await Promise.all([ apiGet('/payments/transactions/'), apiGet('/payments/disputes/') ])
    txns.value = t.data?.results || []
    disputes.value = d.data?.results || []
    if (auth.isTutor) {
      const [po, tp] = await Promise.all([ apiGet('/payments/payouts/'), apiGet('/tutors/my-profile/') ])
      payouts.value = po.data?.results || []; tutorProfile.value = tp.data || {}
    }
  } catch(e) { console.error(e) }
  finally { loading.value = false }
})
</script>
