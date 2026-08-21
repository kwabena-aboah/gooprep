<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4"><div><h2 class="fw-800 mb-0">Student Approvals</h2><p class="text-muted small mb-0">Review and manage student access.</p></div><select class="form-select form-select-sm" v-model="status" @change="load" style="width:auto"><option value="pending">Pending</option><option value="approved">Approved</option><option value="all">All</option></select></div>
    <GpSpinner v-if="loading" />
    <div v-else class="gp-card table-responsive"><table class="gp-table"><thead><tr><th>Student</th><th>School</th><th>Education</th><th>Documents</th><th>Status</th><th>Action</th></tr></thead><tbody><tr v-for="student in students" :key="student.id"><td><div class="fw-600 small">{{ student.full_name }}</div><div class="text-muted small">{{ student.email }}</div></td><td>{{ student.school || '—' }}</td><td>{{ student.education_level || '—' }}</td><td><div v-for="doc in (student.verification_documents||[])" :key="doc.id"><a :href="doc.file_url" target="_blank" rel="noopener" class="small">{{ doc.doc_label }} <i class="bi bi-eye"></i></a></div><span v-if="!(student.verification_documents||[]).length" class="text-muted small">None</span></td><td><span class="badge" :class="student.is_approved?'bg-success-subtle text-success':'bg-warning-subtle text-warning'">{{ student.is_approved ? 'Approved' : 'Pending' }}</span></td><td><button class="btn btn-sm" :class="student.is_approved?'btn-outline-danger':'btn-gp'" @click="update(student)">{{ student.is_approved ? 'Suspend' : 'Approve' }}</button></td></tr></tbody></table><GpEmpty v-if="!students.length" icon="bi bi-people" message="No students found." /></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { useNotifStore } from '@/stores/notifs'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty from '@/components/common/GpEmpty.vue'
const students = ref([]); const loading = ref(true); const status = ref('pending'); const notifStore = useNotifStore()
async function load() { loading.value = true; try { const {data} = await apiGet('/admin-panel/students/', {approval_status:status.value}); students.value = data.results || [] } finally { loading.value = false } }
async function update(student) { try { await apiPost(`/admin-panel/students/${student.id}/approve/`, {action:student.is_approved?'suspend':'approve'}); notifStore.toast('Student status updated.', 'success'); await load() } catch { notifStore.toast('Could not update student.', 'error') } }
onMounted(load)
</script>
