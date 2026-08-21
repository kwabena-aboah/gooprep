<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Tutor Approvals</h2><p class="text-muted small mb-0">{{ pending.length }} pending applications</p></div>
      <select class="form-select form-select-sm" v-model="statusFilter" @change="fetch" style="width:auto">
        <option value="pending">Pending</option><option value="approved">Approved</option>
        <option value="rejected">Rejected</option><option value="">All</option>
      </select>
    </div>
    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!tutors.length" icon="bi bi-person-badge" message="No tutor applications." />
    <div v-else class="row g-3">
      <div v-for="t in tutors" :key="t.id" class="col-md-6">
        <div class="gp-card p-4">
          <div class="d-flex gap-3 mb-3">
            <img :src="t.avatar_url||fallback(t.full_name)" class="rounded-circle flex-shrink-0" width="56" height="56" style="object-fit:cover;border:2px solid var(--gp-red)" />
            <div class="flex-grow-1 overflow-hidden">
              <div class="fw-700">{{ t.full_name }}</div>
              <div class="text-muted small text-truncate">{{ t.headline }}</div>
              <div class="text-muted small">{{ t.email }} · {{ t.city }}</div>
            </div>
            <span class="badge align-self-start" :class="statusBadge(t.approval_status)">{{ t.approval_status }}</span>
          </div>
          <div class="d-flex flex-wrap gap-1 mb-3">
            <span v-for="s in (t.subjects_list||[]).slice(0,4)" :key="s.id" class="gp-badge">{{ s.name }}</span>
          </div>
          <div class="row g-2 text-center mb-3">
            <div class="col-3"><div class="fw-700">{{ t.years_experience }}yr</div><div class="text-muted" style="font-size:.7rem">Exp</div></div>
            <div class="col-3"><div class="fw-700">GHS {{ t.hourly_rate }}</div><div class="text-muted" style="font-size:.7rem">/hr</div></div>
            <div class="col-3"><div class="fw-700">{{ t.education?.length||0 }}</div><div class="text-muted" style="font-size:.7rem">Degrees</div></div>
            <div class="col-3"><div class="fw-700">{{ t.certifications?.length||0 }}</div><div class="text-muted" style="font-size:.7rem">Certs</div></div>
          </div>
          <div v-if="t.bio" class="text-muted small mb-3 p-2 rounded-3" style="background:#f8fafc;max-height:80px;overflow:hidden">{{ t.bio }}</div>
          <div class="border rounded-3 p-2 mb-3">
            <div class="small fw-700 mb-1"><i class="bi bi-file-earmark-check me-1"></i>Verification documents</div>
            <div v-if="!(t.verification_documents||[]).length" class="small text-muted">No documents uploaded.</div>
            <div v-for="doc in (t.verification_documents||[])" :key="doc.id" class="d-flex justify-content-between align-items-center small mb-1">
              <span class="text-truncate me-2">{{ doc.doc_label }} · {{ doc.file_name }}</span>
              <a class="btn btn-sm btn-outline-primary py-0" :href="doc.file_url" target="_blank" rel="noopener"><i class="bi bi-eye me-1"></i>Preview</a>
            </div>
          </div>
          <div v-if="t.approval_status==='pending'" class="d-flex gap-2">
            <button class="btn btn-success btn-sm flex-grow-1" @click="decide(t,'approved')">
              <span v-if="deciding===t.id+'a'" class="spinner-border spinner-border-sm"></span>
              <i v-else class="bi bi-check-circle me-1"></i>Approve
            </button>
            <button class="btn btn-outline-danger btn-sm flex-grow-1" @click="decide(t,'rejected')">
              <i class="bi bi-x-circle me-1"></i>Reject
            </button>
            <RouterLink :to="`/tutors/${t.id}`" target="_blank" class="btn btn-sm btn-outline-secondary">
              <i class="bi bi-eye"></i>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { statusBadge } from '@/utils/helpers'
import { useNotifStore } from '@/stores/notifs'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'
const notifStore = useNotifStore()
const tutors = ref([]); 
const pending = ref([]); 
const loading = ref(true)
const statusFilter = ref('pending'); 
const deciding = ref('')
const fallback = n => `https://ui-avatars.com/api/?name=${encodeURIComponent(n||'T')}&background=e63900&color=fff`
async function fetch() {
  loading.value = true
  try {
    const { data } = await apiGet('/admin-panel/tutors/', { approval_status: statusFilter.value })
    tutors.value = data.results || []
    pending.value = tutors.value.filter(t=>t.approval_status==='pending')
  } catch {} finally { loading.value = false }
}
async function decide(t, status) {
  deciding.value = t.id+(status==='approved'?'a':'r')
  try {
    await apiPost(`/admin-panel/tutors/${t.id}/approve/`, { status })
    t.approval_status = status
    notifStore.toast(`Tutor ${status}!`, status==='approved'?'success':'error')
  } catch {} finally { deciding.value = '' }
}
onMounted(fetch)
</script>
