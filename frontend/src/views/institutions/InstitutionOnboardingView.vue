<template>
  <div class="container py-5" style="max-width:720px">
    <div class="gp-card p-4 p-md-5">
      <h2 class="fw-800 mb-1">Set up your institution</h2>
      <p class="text-muted small mb-4">Complete these details so our team can review your institution account.</p>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div class="row g-3">
        <div class="col-12"><label class="form-label small fw-600">Institution name *</label><input class="form-control" v-model="form.name" required /></div>
        <div class="col-md-6"><label class="form-label small fw-600">Institution type *</label><select class="form-select" v-model="form.type"><option value="school">School</option><option value="university">University</option><option value="organisation">Organisation</option><option value="ngo">NGO</option></select></div>
        <div class="col-md-6"><label class="form-label small fw-600">City *</label><input class="form-control" v-model="form.city" required placeholder="Accra, Kumasi…" /></div>
        <div class="col-12"><label class="form-label small fw-600">Address *</label><textarea class="form-control" v-model="form.address" rows="2" required /></div>
        <div class="col-md-6"><label class="form-label small fw-600">Contact email *</label><input class="form-control" type="email" v-model="form.contact_email" required /></div>
        <div class="col-md-6"><label class="form-label small fw-600">Contact phone *</label><input class="form-control" type="tel" v-model="form.contact_phone" required /></div>
        <div class="col-12"><label class="form-label small fw-600">Website <span class="text-muted fw-400">(optional)</span></label><input class="form-control" type="url" v-model="form.website" placeholder="https://example.org" /></div>
        <div class="col-12"><label class="form-label small fw-600">Description</label><textarea class="form-control" v-model="form.description" rows="3" placeholder="Tell us about your institution…" /></div>
      </div>
      <button class="btn btn-gp mt-4" @click="save" :disabled="saving || !valid"><span v-if="saving" class="spinner-border spinner-border-sm me-1" />Submit for approval</button>
    </div>
  </div>
</template>
<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet, apiPatch } from '@/utils/api'
import { useNotifStore } from '@/stores/notifs'
const router = useRouter(); const notifStore = useNotifStore()
const saving = ref(false); const error = ref('')
const form = ref({ name:'', type:'school', city:'', address:'', contact_email:'', contact_phone:'', website:'', description:'' })
const valid = computed(() => form.value.name.trim() && form.value.city.trim() && form.value.address.trim() && form.value.contact_email.trim() && form.value.contact_phone.trim())
async function save() {
  saving.value = true; error.value = ''
  try { await apiPatch('/institutions/', form.value); notifStore.toast('Institution submitted for approval.', 'success'); router.push('/institution') }
  catch (e) { error.value = Object.values(e.response?.data || {}).flat().join(' ') || 'Could not save institution details.' }
  finally { saving.value = false }
}
onMounted(async () => { try { const { data } = await apiGet('/institutions/'); Object.assign(form.value, data) } catch {} })
</script>
