<template>
  <div style="max-width:640px;margin:0 auto">
    <div class="mb-4">
      <RouterLink to="/lessons" class="btn btn-link btn-sm text-muted p-0 mb-2">
        <i class="bi bi-chevron-left me-1"></i>Back to Lessons
      </RouterLink>
      <h2 class="fw-800 mb-0">Reschedule Lesson</h2>
      <p class="text-muted small">Propose a new time with your {{ auth.isStudent ? 'tutor' : 'student' }}.</p>
    </div>

    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!lesson" icon="bi bi-calendar-x" message="Lesson not found." action-label="Back" action-to="/lessons" />
    <div v-else>
      <!-- Current lesson -->
      <div class="gp-card p-4 mb-4 border-start border-4" style="border-color:var(--gp-red)!important">
        <div class="small fw-600 text-muted mb-2 text-uppercase" style="letter-spacing:.06em">Current Schedule</div>
        <div class="d-flex align-items-center gap-3 flex-wrap">
          <div class="text-center rounded-3 p-2 flex-shrink-0" style="min-width:56px;background:rgba(230,57,0,.08)">
            <div class="fw-800 text-gp-primary" style="font-size:1.3rem">{{ fmtDay(lesson.start_time) }}</div>
            <div class="text-muted" style="font-size:.7rem">{{ fmtMonth(lesson.start_time) }}</div>
          </div>
          <div>
            <div class="fw-700">{{ lesson.subject_name || 'Tutoring Session' }}</div>
            <div class="text-muted small">with {{ auth.isStudent ? lesson.tutor_name : lesson.student_name }}</div>
            <div class="text-muted small"><i class="bi bi-clock me-1"></i>{{ fmtTime(lesson.start_time) }} – {{ fmtTime(lesson.end_time) }} · {{ lesson.duration_minutes }} min</div>
          </div>
          <span class="badge ms-auto" :class="statusBadge(lesson.status)">{{ lesson.status }}</span>
        </div>
      </div>

      <!-- New schedule form -->
      <div class="gp-card p-4 mb-4">
        <h5 class="fw-700 mb-4"><i class="bi bi-calendar-plus me-2 text-gp-primary"></i>Propose New Time</h5>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label small fw-600">New Date *</label>
            <input type="date" class="form-control" v-model="form.date" :min="minDate" :max="maxDate" />
          </div>
          <div class="col-md-6">
            <label class="form-label small fw-600">New Start Time *</label>
            <input type="time" class="form-control" v-model="form.time" />
          </div>
          <div class="col-12">
            <label class="form-label small fw-600">Duration</label>
            <select class="form-select" v-model="form.duration">
              <option value="30">30 minutes</option>
              <option value="60">1 hour</option>
              <option value="90">1.5 hours</option>
              <option value="120">2 hours</option>
            </select>
          </div>
          <div class="col-12">
            <label class="form-label small fw-600">Reason for Rescheduling</label>
            <textarea class="form-control" rows="3" v-model="form.reason" maxlength="500"
                      placeholder="e.g. I have a scheduling conflict at the original time…"></textarea>
            <div class="text-end text-muted small">{{ form.reason.length }}/500</div>
          </div>
        </div>

        <!-- Preview -->
        <div class="gp-card-flat p-3 mb-4" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)" v-if="form.date && form.time">
          <div class="small fw-600 text-muted mb-2">New Schedule Preview</div>
          <div class="d-flex align-items-center gap-3">
            <div class="text-center rounded-3 p-2" style="min-width:52px;background:#fff;border:1px solid rgba(230,57,0,.2)">
              <div class="fw-800 text-gp-primary" style="font-size:1.2rem">{{ fmtDay(newStart) }}</div>
              <div class="text-muted" style="font-size:.65rem">{{ fmtMonth(newStart) }}</div>
            </div>
            <div>
              <div class="fw-700 small">{{ lesson.subject_name || 'Session' }}</div>
              <div class="text-muted small"><i class="bi bi-clock me-1"></i>{{ fmtTime(newStart) }} – {{ fmtTime(newEnd) }}</div>
              <div class="text-muted small"><i class="bi bi-hourglass me-1"></i>{{ form.duration }} minutes</div>
            </div>
            <span class="ms-auto badge bg-success-subtle text-success">Proposed</span>
          </div>
        </div>

        <div class="alert alert-info small mb-4">
          <i class="bi bi-info-circle me-2"></i>
          <strong>Policy:</strong> The other party has 48 hours to accept or decline. If declined, the original time stays active.
        </div>

        <div class="d-flex gap-3">
          <button class="btn btn-gp flex-grow-1" @click="submit" :disabled="submitting || !form.date || !form.time">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-send me-2"></i>Send Request
          </button>
          <RouterLink to="/lessons" class="btn btn-outline-secondary">Cancel</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDay, fmtMonth, fmtTime, statusBadge } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'

const route      = useRoute()
const router     = useRouter()
const auth       = useAuthStore()
const notifStore = useNotifStore()
const loading    = ref(true)
const submitting = ref(false)
const lesson     = ref(null)
const form       = ref({ date: '', time: '', duration: '60', reason: '' })

const minDate = new Date(Date.now() + 3600000).toISOString().split('T')[0]
const maxDate = new Date(Date.now() + 60*86400000).toISOString().split('T')[0]
const newStart = computed(() => form.value.date && form.value.time ? new Date(`${form.value.date}T${form.value.time}:00`) : null)
const newEnd   = computed(() => newStart.value ? new Date(newStart.value.getTime() + parseInt(form.value.duration)*60000) : null)

async function submit() {
  if (!form.value.date || !form.value.time) { notifStore.toast('Select date and time.', 'error'); return }
  submitting.value = true
  try {
    await apiPost(`/scheduling/lessons/${route.params.id}/reschedule/`, {
      new_start_time: newStart.value.toISOString(),
      new_end_time:   newEnd.value.toISOString(),
      reason: form.value.reason,
    })
    notifStore.toast('Reschedule request sent! 48 hours to respond.', 'success')
    setTimeout(() => router.push('/lessons'), 1500)
  } catch(e) {
    notifStore.toast(Object.values(e.response?.data||{}).flat().join(' ')||'Failed.', 'error')
  } finally { submitting.value = false }
}

onMounted(async () => {
  try {
    const { data } = await apiGet(`/scheduling/lessons/${route.params.id}/`)
    lesson.value = data
    form.value.duration = String(data.duration_minutes || 60)
  } catch {} finally { loading.value = false }
})
</script>
