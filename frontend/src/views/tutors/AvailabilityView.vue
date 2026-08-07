<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">My Availability</h2><p class="text-muted small mb-0">Set your weekly teaching schedule</p></div>
      <button class="btn btn-gp btn-sm" @click="saveAll" :disabled="saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-save me-1"></i>Save Schedule
      </button>
    </div>

    <GpSpinner v-if="loading" />
    <div v-else class="row g-4">
      <!-- Weekly schedule -->
      <div class="col-lg-8">
        <div class="gp-card p-4 mb-4">
          <h5 class="fw-700 mb-3"><i class="bi bi-calendar-week me-2 text-gp-primary"></i>Weekly Schedule</h5>
          <div v-for="(day, idx) in days" :key="idx" class="mb-3 pb-3 border-bottom">
            <div class="d-flex align-items-center gap-3 mb-2 flex-wrap">
              <div class="fw-600" style="min-width:100px">{{ day }}</div>
              <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" :id="`day${idx}`"
                       v-model="schedule[idx].enabled" />
                <label class="form-check-label small" :for="`day${idx}`">
                  {{ schedule[idx].enabled ? 'Available' : 'Not available' }}
                </label>
              </div>
            </div>
            <div v-if="schedule[idx].enabled">
              <div v-for="(slot, si) in schedule[idx].slots" :key="si"
                   class="d-flex align-items-center gap-2 mb-2 flex-wrap">
                <input type="time" class="form-control form-control-sm" v-model="slot.start" style="width:130px" />
                <span class="text-muted small">to</span>
                <input type="time" class="form-control form-control-sm" v-model="slot.end" style="width:130px" />
                <button class="btn btn-sm btn-outline-danger" @click="schedule[idx].slots.splice(si,1)">
                  <i class="bi bi-x"></i>
                </button>
              </div>
              <button class="btn btn-sm btn-gp-outline mt-1"
                      @click="schedule[idx].slots.push({start:'09:00',end:'17:00'})">
                <i class="bi bi-plus me-1"></i>Add Slot
              </button>
            </div>
          </div>
        </div>

        <!-- Blocked dates -->
        <div class="gp-card p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-700 mb-0"><i class="bi bi-calendar-x me-2 text-gp-primary"></i>Blocked Dates</h5>
            <button class="btn btn-sm btn-gp-outline" @click="addBlock">
              <i class="bi bi-plus me-1"></i>Add Date
            </button>
          </div>
          <GpEmpty v-if="!blockedDates.length" icon="bi bi-calendar-check"
                   message="No blocked dates — you're fully available!" />
          <div v-else>
            <div v-for="(b,i) in blockedDates" :key="i"
                 class="d-flex align-items-center gap-2 mb-2 p-2 border rounded-3">
              <input type="date" class="form-control form-control-sm" v-model="b.date" style="width:160px" />
              <input class="form-control form-control-sm" v-model="b.reason" placeholder="Reason (optional)" />
              <button class="btn btn-sm btn-outline-danger" @click="blockedDates.splice(i,1)">
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right sidebar: settings -->
      <div class="col-lg-4">
        <div class="gp-card p-4 mb-4">
          <h5 class="fw-700 mb-3"><i class="bi bi-sliders me-2 text-gp-primary"></i>Booking Settings</h5>
          <div class="mb-3">
            <label class="form-label small fw-600">Minimum notice (hours)</label>
            <select class="form-select form-select-sm" v-model="settings.min_notice">
              <option value="1">1 hour</option><option value="2">2 hours</option>
              <option value="4">4 hours</option><option value="12">12 hours</option>
              <option value="24">24 hours</option><option value="48">48 hours</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-600">Max bookings per day</label>
            <input type="number" class="form-control form-control-sm" v-model="settings.max_daily" min="1" max="12" />
          </div>
          <div class="mb-3">
            <label class="form-label small fw-600">Buffer between lessons (min)</label>
            <select class="form-select form-select-sm" v-model="settings.buffer">
              <option value="0">None</option><option value="10">10 min</option>
              <option value="15">15 min</option><option value="30">30 min</option>
            </select>
          </div>
          <div class="form-check form-switch mb-2">
            <input class="form-check-input" type="checkbox" v-model="settings.instant_book" />
            <label class="form-check-label small"><i class="bi bi-lightning-fill text-warning me-1"></i>Instant Book enabled</label>
          </div>
        </div>

        <!-- Upcoming preview -->
        <div class="gp-card p-4">
          <h5 class="fw-700 mb-3"><i class="bi bi-calendar3 me-2 text-gp-primary"></i>This Week</h5>
          <GpEmpty v-if="!upcoming.length" icon="bi bi-calendar" message="No lessons this week." />
          <div v-for="l in upcoming.slice(0,4)" :key="l.id"
               class="d-flex align-items-center gap-2 mb-2 p-2 rounded-3 border">
            <div class="text-center rounded-3 p-1 flex-shrink-0" style="min-width:40px;background:rgba(230,57,0,.08)">
              <div class="fw-800 text-gp-primary" style="font-size:.9rem">{{ fmtDay(l.start_time) }}</div>
              <div class="text-muted" style="font-size:.6rem">{{ fmtMonth(l.start_time) }}</div>
            </div>
            <div class="overflow-hidden">
              <div class="small fw-600 text-truncate">{{ l.student_name }}</div>
              <div class="text-muted" style="font-size:.72rem">{{ fmtTime(l.start_time) }} · {{ l.duration_minutes }}m</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDay, fmtMonth, fmtTime } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'

const notifStore = useNotifStore()
const loading    = ref(true)
const saving     = ref(false)
const upcoming   = ref([])
const blockedDates = ref([])
const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

const schedule = ref(days.map(() => ({ enabled: false, slots: [{ start:'09:00', end:'17:00' }] })))
const settings = ref({ min_notice: 24, max_daily: 6, buffer: 15, instant_book: true })

function addBlock() { blockedDates.value.push({ date: '', reason: '' }) }

async function saveAll() {
  saving.value = true
  try {
    const slots = []
    schedule.value.forEach((day, idx) => {
      if (day.enabled) {
        day.slots.forEach(s => {
          if (s.start && s.end) slots.push({ day_of_week: idx, start_time: s.start, end_time: s.end })
        })
      }
    })
    await apiPost('/tutors/my-availability/', { slots, blocked_dates: blockedDates.value, ...settings.value })
    notifStore.toast('Schedule saved!', 'success')
  } catch(e) { notifStore.toast('Failed to save.', 'error') }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [avail, lessons] = await Promise.all([
      apiGet('/tutors/my-profile/'),
      apiGet('/scheduling/lessons/', { ordering: 'start_time', page_size: 10 }),
    ])
    const av = avail.data?.availability || []
    av.forEach(slot => {
      schedule.value[slot.day_of_week].enabled = true
      if (!schedule.value[slot.day_of_week].slots.some(s => s.start === slot.start_time))
        schedule.value[slot.day_of_week].slots.push({ start: slot.start_time, end: slot.end_time })
    })
    upcoming.value = (lessons.data?.results || []).filter(l => l.status === 'confirmed')
    settings.value.instant_book = avail.data?.instant_book ?? true
  } catch {} finally { loading.value = false }
})
</script>
