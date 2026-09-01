<template>
  <div class="container py-4" style="max-width:1000px">
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-1">{{ institution.name || 'Institution workspace' }}</h2><p class="text-muted mb-0">Manage learners and tutors from one place.</p></div>
      <span class="badge" :class="institution.approval_status === 'approved' ? 'bg-success' : institution.approval_status === 'rejected' ? 'bg-danger' : 'bg-warning text-dark'">{{ institution.approval_status || 'pending' }}</span>
    </div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div class="row g-3 mb-4">
      <div class="col-md-4"><div class="gp-card p-4"><div class="text-muted small">Members</div><div class="display-6 fw-800">{{ institution.member_count || 0 }}</div></div></div>
      <div class="col-md-4"><div class="gp-card p-4"><div class="text-muted small">Location</div><div class="fw-700">{{ institution.city || 'Add your city' }}</div><div class="small text-muted">{{ institution.country }}</div></div></div>
      <div class="col-md-4"><div class="gp-card p-4"><div class="text-muted small">Access</div><div class="fw-700 text-success">All features included</div><div class="small text-muted">Pay only for tutor bookings</div></div></div>
    </div>
    <div class="row g-4">
      <div class="col-lg-7"><div class="gp-card p-4"><h5 class="fw-700 mb-3">Members</h5><div v-if="!institution.members?.length" class="text-muted small">No members yet. Add a student or tutor by email.</div><div v-for="member in institution.members" :key="member.id" class="d-flex align-items-center gap-3 py-2 border-bottom"><div class="flex-grow-1"><div class="fw-600">{{ member.name || member.email }}</div><div class="text-muted small">{{ member.email }}</div></div><span class="badge bg-light text-dark text-capitalize">{{ member.role }}</span><button class="btn btn-sm btn-outline-danger" @click="removeMember(member.id)">Remove</button></div></div></div>
      <div class="col-lg-5"><div class="gp-card p-4"><h5 class="fw-700 mb-3">Add member</h5><input class="form-control mb-2" type="email" v-model="newEmail" placeholder="member@example.com"/><select class="form-select mb-3" v-model="newRole"><option value="student">Student</option><option value="tutor">Tutor</option><option value="staff">Staff</option></select><button class="btn btn-gp w-100" @click="addMember" :disabled="saving || !newEmail.trim()">Add member</button></div><div class="gp-card p-4 mt-4"><h5 class="fw-700 mb-2">Profile details</h5><p class="small text-muted mb-0">{{ institution.address || 'Add an address in your institution profile.' }}</p><p class="small text-muted mb-0">{{ institution.contact_email || 'No contact email added.' }}</p></div></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { apiDelete, apiGet, apiPost } from '@/utils/api'
import { useNotifStore } from '@/stores/notifs'

const institution = ref({ members: [] })
const newEmail = ref('')
const newRole = ref('student')
const saving = ref(false)
const error = ref('')
const notifStore = useNotifStore()

async function load() {
  try { const { data } = await apiGet('/institutions/'); institution.value = data }
  catch (e) { error.value = e.response?.data?.detail || 'Could not load institution workspace.' }
}
async function addMember() {
  saving.value = true
  try { await apiPost('/institutions/members/', { email: newEmail.value, role: newRole.value }); newEmail.value = ''; await load(); notifStore.toast('Member added.', 'success') }
  catch (e) { notifStore.toast(e.response?.data?.error || 'Could not add member.', 'error') }
  finally { saving.value = false }
}
async function removeMember(id) {
  if (!confirm('Remove this member from the institution?')) return
  try { await apiDelete(`/institutions/members/${id}/`); await load(); notifStore.toast('Member removed.', 'success') }
  catch { notifStore.toast('Could not remove member.', 'error') }
}
onMounted(load)
</script>
