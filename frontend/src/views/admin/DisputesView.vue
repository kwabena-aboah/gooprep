<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Disputes</h2><p class="text-muted small mb-0">{{ total }} total · {{ open }} open</p></div>
      <select class="form-select form-select-sm" v-model="statusFilter" @change="fetch" style="width:auto">
        <option value="">All</option><option value="open">Open</option>
        <option value="under_review">Under Review</option><option value="resolved">Resolved</option>
      </select>
    </div>
    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!disputes.length" icon="bi bi-shield-check" message="No disputes found." />
    <div v-else>
      <div v-for="d in disputes" :key="d.id" class="gp-card p-4 mb-3">
        <div class="d-flex justify-content-between align-items-start mb-3 flex-wrap gap-2">
          <div>
            <div class="fw-700">Dispute #{{ d.id }}</div>
            <div class="text-muted small">Filed {{ timeAgo(d.created_at) }} by {{ d.filed_by_name }}</div>
          </div>
          <span class="badge" :class="d.status==='resolved'?'bg-success-subtle text-success':d.status==='under_review'?'bg-info-subtle text-info':'bg-warning-subtle text-warning'">{{ d.status.replace('_',' ') }}</span>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <div class="gp-card-flat p-3" style="background:#f8fafc">
              <div class="small fw-600 mb-1 text-muted">Lesson</div>
              <div class="small">{{ d.lesson_subject }} · {{ fmtDateTime(d.lesson_date) }}</div>
              <div class="small text-muted">{{ d.tutor_name }} → {{ d.student_name }}</div>
              <div class="small fw-600 text-gp-primary">GHS {{ d.amount }}</div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="gp-card-flat p-3" style="background:#fff8f5">
              <div class="small fw-600 mb-1 text-muted">Reason</div>
              <div class="small">{{ d.reason }}</div>
            </div>
          </div>
        </div>
        <div v-if="d.status !== 'resolved'" class="row g-2">
          <div class="col-md-8">
            <textarea class="form-control form-control-sm" v-model="d._resolution" rows="2" placeholder="Resolution notes…"></textarea>
          </div>
          <div class="col-md-4 d-flex flex-column gap-1">
            <button class="btn btn-success btn-sm" @click="resolve(d,'refund')"><i class="bi bi-cash me-1"></i>Resolve & Refund</button>
            <button class="btn btn-outline-secondary btn-sm" @click="resolve(d,'no_refund')"><i class="bi bi-x-circle me-1"></i>Resolve – No Refund</button>
            <button class="btn btn-outline-info btn-sm" @click="resolve(d,'review')"><i class="bi bi-eye me-1"></i>Mark Under Review</button>
          </div>
        </div>
        <div v-else class="alert alert-success small py-2 mb-0">
          <i class="bi bi-check-circle me-1"></i><strong>Resolution:</strong> {{ d.resolution }}
        </div>
      </div>
    </div>
    <GpPagination :page="page" :total-pages="totalPages" @change="p=>{page=p;fetch()}" />
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { timeAgo, fmtDateTime } from '@/utils/helpers'
import { useNotifStore } from '@/stores/notifs'
import GpSpinner    from '@/components/common/GpSpinner.vue'
import GpEmpty      from '@/components/common/GpEmpty.vue'
import GpPagination from '@/components/common/GpPagination.vue'
const notifStore = useNotifStore()
const disputes = ref([]); const loading = ref(true)
const total = ref(0); const open = ref(0); const page = ref(1)
const statusFilter = ref('open')
const totalPages = computed(() => Math.ceil(total.value / 15))
async function fetch() {
  loading.value = true
  const params = { page: page.value, page_size: 15 }
  if (statusFilter.value) params.status = statusFilter.value
  try {
    const { data } = await apiGet('/admin-panel/disputes/', params)
    disputes.value = (data.results||[]).map(d=>({...d,_resolution:''}))
    total.value = data.count||0; open.value = data.open_count||0
  } catch {} finally { loading.value = false }
}
async function resolve(d, action) {
  try {
    await apiPost(`/admin-panel/disputes/${d.id}/resolve/`, { action, resolution: d._resolution })
    d.status = action==='review'?'under_review':'resolved'
    d.resolution = d._resolution
    notifStore.toast('Dispute updated!', 'success')
  } catch { notifStore.toast('Action failed.', 'error') }
}
onMounted(fetch)
</script>
