<template>
  <div class="container py-5" style="max-width:720px">
    <div class="gp-card p-4 p-md-5">
      <h2 class="fw-800 mb-1">Complete your student profile</h2>
      <p class="text-muted small mb-4">Tell us about your learning goals so we can personalize Gooprep.</p>
      <div class="row g-3">
        <div class="col-md-6"><label class="form-label small fw-600">Education level</label><input class="form-control" v-model="form.education_level" /></div>
        <div class="col-md-6"><label class="form-label small fw-600">School</label><input class="form-control" v-model="form.school" /></div>
        <div class="col-12"><label class="form-label small fw-600">Subjects of interest</label><input class="form-control" v-model="subjectsText" placeholder="Mathematics, English, Biology" /></div>
        <div class="col-12"><label class="form-label small fw-600">Learning goals</label><textarea class="form-control" rows="4" v-model="form.learning_goals"></textarea></div>
      </div>
      <button class="btn btn-gp mt-4" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>Save and continue</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiPatch } from '@/utils/api'
import { useNotifStore } from '@/stores/notifs'
const router = useRouter(); const notifStore = useNotifStore(); const saving = ref(false)
const form = ref({ education_level:'', school:'', subjects_interest:[], learning_goals:'' })
const subjectsText = ref('')
async function save() {
  saving.value = true
  try { await apiPatch('/students/profile/', {...form.value, subjects_interest: subjectsText.value.split(',').map(s => s.trim()).filter(Boolean)}); router.push('/dashboard') }
  catch (e) { notifStore.toast(Object.values(e.response?.data || {}).flat().join(' ') || 'Could not save profile.', 'error') }
  finally { saving.value = false }
}
</script>
