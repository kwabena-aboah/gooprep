<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Gooprep Rooms</h2><p class="text-muted small mb-0">GooPrep Virtual Server & Active Sessions</p></div>
      <button class="btn btn-gp btn-sm" @click="fetch"><i class="bi bi-arrow-clockwise me-1"></i>Refresh</button>
    </div>
    <GpSpinner v-if="loading" />
    <div v-else>
      <!-- Server status -->
      <div class="bbb-server-card mb-4">
        <div class="d-flex align-items-center gap-3 mb-3">
          <div class="bbb-dot" :class="status.online?'online':'offline'"></div>
          <h5 class="fw-700 text-white mb-0">Gooprep Server</h5>
          <span class="badge ms-auto" :class="status.online?'bg-success':'bg-danger'">{{ status.online?'Online':'Offline' }}</span>
        </div>
        <div class="row g-3">
          <div class="col-6 col-md-3 text-center">
            <div class="fw-800 text-white fs-3">{{ status.active_meetings||0 }}</div>
            <div class="text-white-50 small">Active Meetings</div>
          </div>
          <div class="col-6 col-md-3 text-center">
            <div class="fw-800 text-white fs-3">{{ status.participant_count||0 }}</div>
            <div class="text-white-50 small">Participants</div>
          </div>
          <div class="col-6 col-md-3 text-center">
            <div class="fw-800 text-white fs-3">{{ status.meeting_count||0 }}</div>
            <div class="text-white-50 small">Total Today</div>
          </div>
          <div class="col-6 col-md-3 text-center">
            <div class="fw-800 text-white fs-3">{{ status.version||'—' }}</div>
            <div class="text-white-50 small">Version</div>
          </div>
        </div>
        <div class="mt-3 small text-white-50">Server URL: {{ status.url || status.server_url || 'Not configured' }}</div>
      </div>

      <!-- Active meetings -->
      <div class="gp-card p-4 mb-4">
        <h5 class="fw-700 mb-3"><i class="bi bi-camera-video-fill me-2 text-success"></i>Active Meetings ({{ rooms.length }})</h5>
        <GpEmpty v-if="!rooms.length" icon="bi bi-camera-video-off" message="No active meetings right now." />
        <div v-else class="table-responsive">
          <table class="gp-table">
            <thead><tr><th>Meeting ID</th><th>Attendees</th><th>Duration</th><th>Created</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="r in rooms" :key="r.meetingID">
                <td class="small fw-600">{{ r.meetingName || r.meetingID }}</td>
                <td><span class="badge bg-primary-subtle text-primary">{{ r.participantCount || 0 }} online</span></td>
                <td class="small text-muted">{{ r.duration || '—' }}</td>
                <td class="small text-muted">{{ fmtTime(r.createTime) }}</td>
                <td>
                  <button class="btn btn-xs btn-outline-danger" @click="endMeeting(r.meetingID, r.moderatorPW)" title="End meeting">
                    <i class="bi bi-stop-circle"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recent recordings -->
      <div class="gp-card p-4">
        <h5 class="fw-700 mb-3"><i class="bi bi-record-circle me-2 text-gp-primary"></i>Recent Recordings</h5>
        <GpEmpty v-if="!recordings.length" icon="bi bi-film" message="No recordings found." />
        <div v-else class="table-responsive">
          <table class="gp-table">
            <thead><tr><th>Title</th><th>Duration</th><th>Size</th><th>Created</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="rec in recordings" :key="rec.recordID">
                <td class="small fw-600">{{ rec.name || rec.recordID }}</td>
                <td class="small text-muted">{{ rec.duration || '—' }}</td>
                <td class="small text-muted">{{ rec.size || '—' }}</td>
                <td class="small text-muted">{{ fmtDate(rec.startTime) }}</td>
                <td class="d-flex gap-1">
                  <a v-if="rec.playbackUrl" :href="rec.playbackUrl" target="_blank" class="btn btn-xs btn-outline-primary">
                    <i class="bi bi-play-circle"></i>
                  </a>
                  <button class="btn btn-xs btn-outline-danger" @click="deleteRec(rec.recordID)">
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDate, fmtTime } from '@/utils/helpers'
import { useNotifStore } from '@/stores/notifs'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'

const notifStore = useNotifStore()
const loading    = ref(true)
const status     = ref({ online: false, active_meetings: 0, participant_count: 0 })
const rooms      = ref([])
const recordings = ref([])
let refreshTimer

async function fetch() {
  loading.value = true
  try {
    const [s, r, rec] = await Promise.all([
      apiGet('/admin-panel/bbb/status/'),
      apiGet('/admin-panel/bbb/rooms/'),
      apiGet('/admin-panel/bbb/recordings/'),
    ])
    status.value = s.data || {}
    rooms.value = r.data?.meetings || []
    recordings.value = rec.data?.recordings || []
  } catch (error) {
    status.value = {
      online: false,
      configured: false,
      url: '',
      error: error.response?.data?.error || 'Unable to load BBB data.',
    }
    rooms.value = []
    recordings.value = []
    notifStore.toast(status.value.error, 'error')
  } finally {
    loading.value = false
  }
}

async function endMeeting(meetingID, pw) {
  if (!confirm(`End meeting ${meetingID}? All participants will be removed.`)) return
  try {
    await apiPost('/admin-panel/bbb/end-meeting/', { meeting_id: meetingID, moderator_pw: pw })
    notifStore.toast('Meeting ended.', 'success')
    fetch()
  } catch { notifStore.toast('Failed to end meeting.', 'error') }
}

async function deleteRec(recordID) {
  if (!confirm('Delete this recording? This cannot be undone.')) return
  try {
    await apiPost('/admin-panel/bbb/delete-recording/', { record_id: recordID })
    recordings.value = recordings.value.filter(r => r.recordID !== recordID)
    notifStore.toast('Recording deleted.', 'success')
  } catch { notifStore.toast('Failed to delete.', 'error') }
}

onMounted(() => {
  fetch()
  refreshTimer = setInterval(fetch, 30000) // auto-refresh every 30s
})
onUnmounted(() => clearInterval(refreshTimer))
</script>
