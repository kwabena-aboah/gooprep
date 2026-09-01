<template>
  <div class="container py-5" style="max-width:720px">
    <div class="gp-card p-4 p-md-5">
      <h2 class="fw-800 mb-1">Complete your student profile</h2>
      <p class="text-muted small mb-4">Tell us about your learning goals and upload an identity document for approval.</p>
      <div class="row g-3">
        <div class="col-md-6"><label class="form-label small fw-600">Education level</label><input class="form-control" v-model="form.education_level" /></div>
        <div class="col-md-6"><label class="form-label small fw-600">Educational institution</label><select class="form-select" v-model="form.school"><option value="" disabled>Select institution</option><option v-for="institution in institutions" :key="institution" :value="institution">{{ institution }}</option></select></div>
        <div class="col-12"><label class="form-label small fw-600">Subjects of interest</label><input class="form-control" v-model="subjectsText" placeholder="Mathematics, English, Biology" /></div>
        <div class="col-12"><label class="form-label small fw-600">Learning goals</label><textarea class="form-control" rows="4" v-model="form.learning_goals"></textarea></div>
        <div class="col-md-6"><label class="form-label small fw-600">Identity document type *</label><select class="form-select" v-model="form.identity_document_type"><option value="" disabled>Select document type</option><option v-for="option in identityOptions" :key="option.value" :value="option.value">{{ option.label }}</option></select></div>
        <div class="col-md-6"><label class="form-label small fw-600">Identity document *</label><input class="form-control" type="file" accept="image/*,.pdf" @change="setIdentityDocument" /><div class="form-text">JPG, PNG or PDF. Maximum 10MB.</div></div>
        <div class="col-12"><label class="form-label small fw-600">Other supporting documents <span class="text-muted fw-400">(optional)</span></label><input class="form-control" type="file" accept="image/*,.pdf" multiple @change="setSupportingDocuments" /></div>
      </div>
      <button class="btn btn-gp mt-4" @click="save" :disabled="saving || !form.identity_document_type || !identityFile"><span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>Save and continue</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet, apiUpload } from '@/utils/api'
import { useNotifStore } from '@/stores/notifs'
import { GHANA_INSTITUTIONS } from '@/utils/ghanaInstitutions'

const router = useRouter()
const notifStore = useNotifStore()
const saving = ref(false)
const institutions = GHANA_INSTITUTIONS
const identityOptions = [
  { value: 'ghana_passport_card', label: 'Ghana passport card' },
  { value: 'voters_id_card', label: "Voter's ID card" },
  { value: 'drivers_license', label: "Driver's license" },
  { value: 'other_id', label: 'Other identity document' },
]
const form = ref({ education_level: '', school: '', subjects_interest: [], learning_goals: '', identity_document_type: '' })
const subjectsText = ref('')
const identityFile = ref(null)
const supportingFiles = ref([])
const userId = JSON.parse(localStorage.getItem('gp_user') || '{}').id || 'guest'
const draftKey = `gooprep:student-onboarding:${userId}`

function saveDraft() {
  localStorage.setItem(draftKey, JSON.stringify({ form: form.value, subjectsText: subjectsText.value }))
}

function restoreDraft(profile) {
  try {
    const draft = JSON.parse(localStorage.getItem(draftKey) || '{}')
    if (draft.form) Object.assign(form.value, draft.form)
    if (draft.subjectsText) subjectsText.value = draft.subjectsText
  } catch { /* Ignore invalid drafts. */ }
  if (profile) {
    form.value.education_level ||= profile.education_level || ''
    form.value.school ||= profile.school || ''
    form.value.learning_goals ||= profile.learning_goals || ''
    form.value.identity_document_type ||= profile.identity_document_type || ''
    form.value.date_of_birth ||= profile.date_of_birth || ''
    form.value.gender ||= profile.gender || ''
    form.value.city ||= profile.city || ''
    form.value.address ||= profile.address || ''
    if (!subjectsText.value && Array.isArray(profile.subjects_interest)) subjectsText.value = profile.subjects_interest.join(', ')
  }
}

watch([form, subjectsText], saveDraft, { deep: true })
function setIdentityDocument(e) { identityFile.value = e.target.files[0] || null }
function setSupportingDocuments(e) { supportingFiles.value = Array.from(e.target.files || []) }

async function save() {
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('date_of_birth', form.value.date_of_birth)
    fd.append('gender', form.value.gender)
    fd.append('city', form.value.city)
    fd.append('address', form.value.address)
    fd.append('education_level', form.value.education_level)
    fd.append('school', form.value.school)
    fd.append('learning_goals', form.value.learning_goals)
    fd.append('identity_document_type', form.value.identity_document_type)
    fd.append('subjects_interest', JSON.stringify(subjectsText.value.split(',').map(s => s.trim()).filter(Boolean)))
    fd.append('identity_document', identityFile.value)
    supportingFiles.value.forEach(file => fd.append('documents', file))
    fd.append('document_type', 'other')
    await apiUpload('/students/profile/', fd)
    localStorage.removeItem(draftKey)
    router.push('/dashboard')
  } catch (e) {
    notifStore.toast(Object.values(e.response?.data || {}).flat().join(' ') || 'Could not save profile.', 'error')
  } finally { saving.value = false }
}

onMounted(async () => {
  const { data } = await apiGet('/students/profile/')
  restoreDraft(data)
})
</script>
