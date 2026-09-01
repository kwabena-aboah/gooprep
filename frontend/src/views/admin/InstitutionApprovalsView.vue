<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2"><div><h2 class="fw-800 mb-0">Institution Approvals</h2><p class="text-muted small mb-0">Review and approve institution accounts.</p></div><button class="btn btn-gp btn-sm" @click="load"><i class="bi bi-arrow-clockwise me-1" />Refresh</button></div>
    <div class="d-flex gap-2 mb-3"><button v-for="tab in tabs" :key="tab.value" class="btn btn-sm" :class="filter===tab.value?'btn-gp':'btn-outline-secondary'" @click="filter=tab.value;load()">{{ tab.label }}</button></div>
    <GpSpinner v-if="loading" /><div v-else-if="!items.length" class="gp-card p-5 text-center text-muted">No {{ filter || '' }} institution applications.</div>
    <div v-else class="row g-3"><div v-for="item in items" :key="item.id" class="col-lg-6"><div class="gp-card p-4"><div class="d-flex justify-content-between gap-2"><div><h5 class="fw-700 mb-1">{{ item.name }}</h5><div class="text-muted small">{{ item.owner_email || 'Institution owner' }} · {{ item.type }}</div></div><span class="badge" :class="badgeClass(item.approval_status)">{{ item.approval_status }}</span></div><p class="small text-muted mt-3 mb-2">{{ item.city }} · {{ item.address || 'No address' }}</p><div class="d-flex gap-2" v-if="item.approval_status==='pending'"><button class="btn btn-sm btn-success" @click="decide(item,'approved')">Approve</button><button class="btn btn-sm btn-outline-danger" @click="decide(item,'rejected')">Reject</button></div><div v-else class="small text-muted">Reviewed {{ item.reviewed_at ? new Date(item.reviewed_at).toLocaleDateString() : '—' }}</div></div></div></div>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import GpSpinner from '@/components/common/GpSpinner.vue'
const items = ref([]); const loading = ref(true); const filter = ref('pending')
const tabs = [{ value:'pending', label:'Pending' }, { value:'approved', label:'Approved' }, { value:'rejected', label:'Rejected' }, { value:'', label:'All' }]
async function load() { loading.value = true; try { const { data } = await apiGet('/admin-panel/institutions/', { approval_status: filter.value, page_size: 100 }); items.value = data.results || [] } finally { loading.value = false } }
function badgeClass(status) { return status === 'approved' ? 'bg-success' : status === 'rejected' ? 'bg-danger' : 'bg-warning text-dark' }
async function decide(item, status) { const reason = status === 'rejected' ? prompt('Reason for rejection (optional):') : ''; if (status === 'rejected' && reason === null) return; await apiPost(`/admin-panel/institutions/${item.id}/approve/`, { status, reason: reason || '' }); await load() }
onMounted(load)
</script>
