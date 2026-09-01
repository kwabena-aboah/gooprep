<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">My Lessons</h2><p class="text-muted small mb-0">{{ total }} lessons total</p></div>
      <RouterLink v-if="auth.isStudent" to="/tutors" class="btn btn-gp btn-sm">
        <i class="bi bi-plus me-1"></i>Book New Lesson
      </RouterLink>
    </div>

    <!-- Status tabs -->
    <div class="d-flex gap-1 mb-4 flex-wrap align-items-center">
      <button v-for="t in statusTabs" :key="t.value"
              class="btn btn-sm" :class="activeStatus===t.value?'btn-gp':'btn-outline-secondary'"
              @click="setStatus(t.value)">
        {{ t.label }}
        <span v-if="t.count" class="badge ms-1 rounded-pill"
              :class="activeStatus===t.value?'bg-white text-primary':'bg-secondary text-white'">{{ t.count }}</span>
      </button>
      <div class="ms-auto">
        <input type="month" class="form-control form-control-sm" v-model="monthFilter" @change="fetchLessons" style="width:auto" />
      </div>
    </div>

    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!lessons.length" icon="bi bi-calendar-x"
             message="No lessons found."
             action-label="Find a Tutor" action-to="/tutors" />

    <div v-else>
      <div v-for="l in lessons" :key="l.id" class="gp-card p-3 mb-3">
        <div class="row align-items-center g-3">
          <!-- Date -->
          <div class="col-auto">
            <div class="text-center rounded-3 p-2" style="min-width:56px;background:rgba(230,57,0,.08)">
              <div class="fw-800 text-gp-primary" style="font-size:1.3rem">{{ fmtDay(l.start_time) }}</div>
              <div class="text-muted" style="font-size:.7rem">{{ fmtMonth(l.start_time) }}</div>
            </div>
          </div>
          <!-- Info -->
          <div class="col">
            <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
              <span class="fw-700">{{ l.subject_name || 'Tutoring Session' }}</span>
              <span class="badge small" :class="statusBadge(l.status)">{{ l.status.replace('_',' ') }}</span>
              <span v-if="l.record_session && l.recording_available" class="badge bg-danger-subtle text-danger small">
                <i class="bi bi-record-circle me-1"></i>Recorded
              </span>
            </div>
            <div class="text-muted small mb-1">
              <i class="bi bi-person me-1"></i>with <strong>{{ auth.isStudent ? l.tutor_name : l.student_name }}</strong>
              &nbsp;·&nbsp;<i class="bi bi-clock me-1"></i>{{ fmtTime(l.start_time) }} – {{ fmtTime(l.end_time) }}
              &nbsp;·&nbsp;{{ l.duration_minutes }} min
            </div>
            <div v-if="l.topic" class="text-muted small"><i class="bi bi-chat-quote me-1"></i>{{ l.topic }}</div>
          </div>
          <!-- Price -->
          <div class="col-auto text-center d-none d-md-block">
            <div class="fw-700 text-gp-primary">GHS {{ l.price }}</div>
            <div class="small text-muted">{{ l.payment_status }}</div>
          </div>
          <!-- Actions -->
          <div class="col-auto">
            <div class="d-flex flex-wrap gap-1 justify-content-end">
              <RouterLink v-if="l.can_join" :to="`/lessons/${l.id}/join`" class="btn btn-gp btn-sm">
                <i class="bi bi-camera-video-fill me-1"></i>Join Now
              </RouterLink>
              <button v-if="l.status==='confirmed' && !l.can_join" class="btn btn-sm btn-outline-secondary"
                      @click="reschedule(l)">
                <i class="bi bi-calendar-event me-1"></i>Reschedule
              </button>
              <button v-if="l.status==='completed' && l.recording_available" class="btn btn-sm btn-outline-danger"
                      @click="viewRecording(l)">
                <i class="bi bi-play-circle me-1"></i>Recording
              </button>
              <button v-if="l.status==='completed' && l.ai_summary" class="btn btn-sm btn-outline-primary"
                      @click="viewDetail(l)">
                <i class="bi bi-robot me-1"></i>AI Notes
              </button>
              <button v-if="l.status==='completed' && !l.has_review && auth.isStudent"
                      class="btn btn-sm btn-outline-warning" @click="writeReview(l)">
                <i class="bi bi-star me-1"></i>Review
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <GpPagination :page="page" :total-pages="totalPages" @change="changePage" />

    <!-- AI Notes modal -->
    <div class="modal fade" id="lessonModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content" v-if="detail">
          <div class="modal-header">
            <h5 class="modal-title fw-700">{{ detail.subject_name || 'Lesson' }} — {{ fmtDateTime(detail.start_time) }}</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <ul class="nav nav-tabs mb-3" v-if="detail.ai_summary || detail.ai_flashcards?.length || detail.ai_quiz?.length">
              <li class="nav-item"><button class="nav-link" :class="{active:aiTab==='summary'}" @click="aiTab='summary'">Summary</button></li>
              <li class="nav-item" v-if="detail.ai_flashcards?.length"><button class="nav-link" :class="{active:aiTab==='cards'}" @click="aiTab='cards'">Flashcards ({{ detail.ai_flashcards.length }})</button></li>
              <li class="nav-item" v-if="detail.ai_quiz?.length"><button class="nav-link" :class="{active:aiTab==='quiz'}" @click="aiTab='quiz'">Quiz ({{ detail.ai_quiz.length }})</button></li>
            </ul>
            <div v-if="aiTab==='summary' && detail.ai_summary" class="gp-card p-3" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)">
              <i class="bi bi-robot text-gp-primary me-2"></i>{{ detail.ai_summary }}
            </div>
            <FlashcardDeck v-if="aiTab==='cards'" :cards="detail.ai_flashcards || []" />
            <QuizWidget v-if="aiTab==='quiz'" :questions="detail.ai_quiz || []" />
          </div>
        </div>
      </div>
    </div>

    <!-- Review modal -->
    <div class="modal fade" id="reviewModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content" v-if="reviewLesson">
          <div class="modal-header"><h5 class="modal-title fw-700">Write a Review</h5><button class="btn-close" data-bs-dismiss="modal"></button></div>
          <div class="modal-body">
            <div class="mb-3 text-center">
              <label class="form-label small fw-600 d-block">Rating *</label>
              <div class="d-inline-flex gap-1">
                <i v-for="n in 5" :key="n" class="bi fs-2"
                   :class="n<=reviewForm.rating?'bi-star-fill text-warning':'bi-star text-muted'"
                   style="cursor:pointer" @click="reviewForm.rating=n"></i>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-600">Review *</label>
              <textarea class="form-control" rows="4" v-model="reviewForm.content" placeholder="Share your experience…"></textarea>
            </div>
            <div class="form-check mb-3">
              <input class="form-check-input" type="checkbox" v-model="reviewForm.would_recommend" />
              <label class="form-check-label small">I would recommend this tutor</label>
            </div>
            <button class="btn btn-gp w-100" @click="submitReview" :disabled="reviewLoading||!reviewForm.rating">
              <span v-if="reviewLoading" class="spinner-border spinner-border-sm me-1"></span>Submit Review
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDay, fmtMonth, fmtTime, fmtDateTime, statusBadge } from '@/utils/helpers'
import GpSpinner    from '@/components/common/GpSpinner.vue'
import GpEmpty      from '@/components/common/GpEmpty.vue'
import GpPagination from '@/components/common/GpPagination.vue'
import FlashcardDeck from '@/components/student/FlashcardDeck.vue'
import QuizWidget    from '@/components/student/QuizWidget.vue'

const auth       = useAuthStore()
const notifStore = useNotifStore()
const router     = useRouter()
const lessons    = ref([])
const loading    = ref(true)
const total      = ref(0)
const page       = ref(1)
const pageSize   = 15
const monthFilter   = ref('')
const activeStatus  = ref('all')
const detail     = ref(null)
const aiTab      = ref('summary')
const reviewLesson  = ref(null)
const reviewForm    = ref({ rating: 0, content: '', would_recommend: true })
const reviewLoading = ref(false)

const totalPages = computed(() => Math.ceil(total.value / pageSize))
const statusTabs = computed(() => [
  { value:'all',         label:'All',         count: total.value },
  { value:'confirmed',   label:'Upcoming',    count: lessons.value.filter(l=>l.status==='confirmed').length },
  { value:'in_progress', label:'In Progress', count: lessons.value.filter(l=>l.status==='in_progress').length },
  { value:'completed',   label:'Completed',   count: lessons.value.filter(l=>l.status==='completed').length },
  { value:'cancelled',   label:'Cancelled',   count: lessons.value.filter(l=>l.status==='cancelled').length },
])

async function fetchLessons() {
  loading.value = true
  try {
    const params = { ordering:'-start_time', page: page.value, page_size: pageSize }
    if (activeStatus.value !== 'all') params.status = activeStatus.value
    if (monthFilter.value) params.month = monthFilter.value
    const { data } = await apiGet('/scheduling/lessons/', params)
    lessons.value = data.results || []; total.value = data.count || 0
  } catch { lessons.value = [] }
  finally { loading.value = false }
}

function setStatus(s) { activeStatus.value = s; page.value = 1; fetchLessons() }
function changePage(p) { page.value = p; fetchLessons(); window.scrollTo(0,0) }
function reschedule(l) { router.push(`/lessons/${l.id}/reschedule`) }

async function viewDetail(l) {
  try {
    const { data } = await apiGet(`/scheduling/lessons/${l.id}/`)
    detail.value = data
  } catch { detail.value = l }
  aiTab.value = 'summary'
  new Modal(document.getElementById('lessonModal')).show()
}

async function viewRecording(l) {
  try {
    const { data } = await apiGet(`/scheduling/lessons/${l.id}/bbb/recordings/`)
    if (data.recordings?.length) window.open(data.recordings[0].playback_url, '_blank')
    else notifStore.toast('Recording not yet available.', 'warning')
  } catch { notifStore.toast('Could not load recording.', 'error') }
}

function writeReview(l) {
  reviewLesson.value = l
  reviewForm.value = { rating: 0, content: '', would_recommend: true }
  new Modal(document.getElementById('reviewModal')).show()
}

async function submitReview() {
  if (!reviewForm.value.rating) { notifStore.toast('Please select a rating.', 'error'); return }
  reviewLoading.value = true
  try {
    await apiPost('/reviews/', {
      lesson: reviewLesson.value.id, tutor: reviewLesson.value.tutor,
      rating: reviewForm.value.rating, content: reviewForm.value.content,
      would_recommend: reviewForm.value.would_recommend,
    })
    Modal.getInstance(document.getElementById('reviewModal'))?.hide()
    notifStore.toast('Review submitted! Thank you.', 'success')
    fetchLessons()
  } catch(e) { notifStore.toast(Object.values(e.response?.data||{}).flat().join(' ')||'Failed.', 'error') }
  finally { reviewLoading.value = false }
}

onMounted(fetchLessons)
</script>
