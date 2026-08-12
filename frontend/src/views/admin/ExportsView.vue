<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-800 mb-0">Export Reports</h2>
        <p class="text-muted small mb-0">Download platform data for analysis and record keeping.</p>
      </div>
      <div class="d-flex gap-2">
        <RouterLink to="/admin/referrals" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-share me-1"></i>View Referrals
        </RouterLink>
        <RouterLink to="/admin" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i>Admin Overview
        </RouterLink>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-8">
        <div class="gp-card p-4">
          <h5 class="fw-700 mb-4"><i class="bi bi-download me-2 text-gp-primary"></i>Choose export options</h5>

          <div class="mb-4">
            <label for="report-type" class="form-label small fw-600">Report</label>
            <select id="report-type" v-model="form.type" class="form-select">
              <option v-for="report in reports" :key="report.value" :value="report.value">
                {{ report.label }} — {{ report.description }}
              </option>
            </select>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <label for="report-format" class="form-label small fw-600">File format</label>
              <select id="report-format" v-model="form.format" class="form-select">
                <option value="excel">Excel (.xlsx)</option>
                <option value="pdf">PDF (.pdf)</option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="report-period" class="form-label small fw-600">Date range</label>
              <select id="report-period" v-model="form.period" class="form-select">
                <option value="all">All time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 days</option>
                <option value="month">Last 30 days</option>
                <option value="quarter">Last 90 days</option>
                <option value="year">Last 365 days</option>
              </select>
            </div>
          </div>

          <div v-if="form.type === 'referrals'" class="alert alert-info small">
            <i class="bi bi-info-circle me-1"></i>Referral reports are available as Excel files only.
          </div>

          <div v-if="errorMessage" class="alert alert-danger small" role="alert">
            <i class="bi bi-exclamation-triangle me-1"></i>{{ errorMessage }}
          </div>

          <button class="btn btn-gp" :disabled="loading" @click="downloadReport">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-file-earmark-arrow-down me-2"></i>
            {{ loading ? 'Preparing download…' : 'Download report' }}
          </button>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="gp-card p-4">
          <h5 class="fw-700 mb-3">Available reports</h5>
          <div v-for="report in reports" :key="report.value" class="d-flex gap-2 mb-3">
            <i :class="report.icon" class="text-gp-primary fs-5"></i>
            <div>
              <div class="fw-600 small">{{ report.label }}</div>
              <div class="text-muted small">{{ report.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { apiDownload } from '@/utils/api'
import { useNotifStore } from '@/stores/notifs'

const notifStore = useNotifStore()
const loading = ref(false)
const errorMessage = ref('')

const reports = [
  { value: 'users', label: 'Users', description: 'Accounts, roles, plans, and activity', icon: 'bi bi-people' },
  { value: 'lessons', label: 'Lessons', description: 'Bookings, schedules, payments, and status', icon: 'bi bi-calendar-check' },
  { value: 'revenue', label: 'Revenue', description: 'Successful transactions and platform fees', icon: 'bi bi-cash-stack' },
  { value: 'tutors', label: 'Tutors', description: 'Tutor profiles, ratings, and approvals', icon: 'bi bi-person-badge' },
  { value: 'referrals', label: 'Referrals', description: 'Users who joined through referrals', icon: 'bi bi-share' },
]

const form = reactive({
  type: 'users',
  format: 'excel',
  period: 'month',
})

function filenameFromHeaders(headers) {
  const disposition = headers['content-disposition'] || ''
  const match = disposition.match(/filename="?([^";]+)"?/i)
  return match?.[1] || `gooprep_${form.type}_${form.period}.${form.format === 'excel' ? 'xlsx' : 'pdf'}`
}

async function downloadReport() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await apiDownload('/admin-panel/export/', {
      type: form.type,
      format: form.type === 'referrals' ? 'excel' : form.format,
      period: form.period,
    })
    const blobUrl = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = filenameFromHeaders(response.headers)
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(blobUrl)
    notifStore.toast('Report downloaded successfully.', 'success')
  } catch (error) {
    errorMessage.value = await getDownloadError(error)
    notifStore.toast(errorMessage.value, 'error')
  } finally {
    loading.value = false
  }
}

async function getDownloadError(error) {
  if (error.response?.data instanceof Blob) {
    try {
      const data = JSON.parse(await error.response.data.text())
      return data.error || data.detail || 'The report could not be generated.'
    } catch {
      return 'The report could not be generated.'
    }
  }
  return error.response?.data?.error || error.response?.data?.detail || 'The report could not be generated.'
}
</script>
