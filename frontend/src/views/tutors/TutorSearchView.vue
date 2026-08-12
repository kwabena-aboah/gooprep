<template>
  <div>
    <!-- Public navbar for non-auth users -->
    <nav v-if="!auth.isAuthenticated" class="gp-navbar mb-0">
      <RouterLink to="/" class="me-auto logo"><img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:36px" /></RouterLink>
      <RouterLink to="/login" class="btn btn-sm btn-outline-light me-2">Log in</RouterLink>
      <RouterLink to="/register" class="btn btn-sm btn-gp">Sign up</RouterLink>
    </nav>

    <div class="row g-4" :class="auth.isAuthenticated ? '' : 'mt-0'">
      <!-- Filters -->
      <div class="col-lg-3">
        <div class="gp-card p-4 sticky-top" style="top:80px">
          <h6 class="fw-700 mb-3"><i class="bi bi-funnel me-1 text-gp-primary"></i>Filters</h6>
          <div class="mb-3">
            <label class="form-label small fw-600">Search</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-search text-muted"></i></span>
              <input class="form-control form-control-sm" v-model="filters.search"
                     placeholder="Name or keyword…" @input="debouncedFetch" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-600">Subject</label>
            <select class="form-select form-select-sm" v-model="filters.subject" @change="fetchTutors">
              <option value="">All Subjects</option>
              <option v-for="s in subjects" :key="s.id" :value="s.slug">{{ s.name }}</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-600">Price (GHS/hr)</label>
            <div class="d-flex gap-2">
              <input type="number" class="form-control form-control-sm" v-model="filters.min_price" placeholder="Min" @change="fetchTutors" />
              <input type="number" class="form-control form-control-sm" v-model="filters.max_price" placeholder="Max" @change="fetchTutors" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-600">Min Rating</label>
            <select class="form-select form-select-sm" v-model="filters.min_rating" @change="fetchTutors">
              <option value="">Any</option>
              <option value="3">3+</option><option value="4">4+</option>
              <option value="4.5">4.5+</option><option value="4.8">4.8+</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-600">Teaching Style</label>
            <select class="form-select form-select-sm" v-model="filters.teaching_style" @change="fetchTutors">
              <option value="">Any</option>
              <option value="interactive">Interactive</option>
              <option value="structured">Structured</option>
              <option value="flexible">Flexible</option>
              <option value="practical">Practical</option>
              <option value="visual">Visual</option>
            </select>
          </div>
          <div class="form-check form-switch mb-2">
            <input class="form-check-input" type="checkbox" v-model="filters.instant_book" @change="fetchTutors" />
            <label class="form-check-label small">Instant Book only</label>
          </div>
          <div class="form-check form-switch mb-3">
            <input class="form-check-input" type="checkbox" v-model="filters.featured" @change="fetchTutors" />
            <label class="form-check-label small">Featured tutors</label>
          </div>
          <button class="btn btn-gp btn-sm w-100 mb-2" @click="fetchTutors">
            <i class="bi bi-search me-1"></i>Apply
          </button>
          <button class="btn btn-link btn-sm w-100 text-muted" @click="clearFilters">Clear all</button>
        </div>
      </div>

      <!-- Results -->
      <div class="col-lg-9">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
          <div>
            <h4 class="fw-800 mb-0">Find Your Tutor</h4>
            <p class="text-muted small mb-0">{{ total }} tutors available</p>
          </div>
          <div class="d-flex gap-2 align-items-center">
            <select class="form-select form-select-sm" v-model="ordering" @change="fetchTutors" style="width:auto">
              <option value="-average_rating">Top Rated</option>
              <option value="hourly_rate">Price: Low → High</option>
              <option value="-hourly_rate">Price: High → Low</option>
              <option value="-total_lessons">Most Lessons</option>
            </select>
            <div class="btn-group btn-group-sm">
              <button class="btn" :class="view==='grid'?'btn-primary':'btn-outline-secondary'" @click="view='grid'">
                <i class="bi bi-grid"></i>
              </button>
              <button class="btn" :class="view==='list'?'btn-primary':'btn-outline-secondary'" @click="view='list'">
                <i class="bi bi-list"></i>
              </button>
            </div>
          </div>
        </div>

        <GpSpinner v-if="loading" />
        <GpEmpty v-else-if="!tutors.length" icon="bi bi-search"
                 message="No tutors match your criteria."
                 action-label="Clear filters" @action="clearFilters" />

        <!-- Grid -->
        <div v-else-if="view === 'grid'" class="row g-3">
          <div class="col-md-6 col-xl-4" v-for="t in tutors" :key="t.id">
            <TutorCard :tutor="t" :is-fav="favs.has(t.id)"
                       @select="openTutor" @fav="toggleFav" />
          </div>
        </div>

        <!-- List -->
        <div v-else>
          <div v-for="t in tutors" :key="t.id"
               class="gp-card p-3 mb-3 d-flex gap-3 align-items-start"
               style="cursor:pointer" @click="openTutor(t)">
            <div class="position-relative flex-shrink-0">
              <img :src="t.avatar_url || fallback(t.full_name)" class="rounded-circle"
                   width="72" height="72" style="object-fit:cover;border:3px solid var(--gp-red)" />
              <span v-if="t.is_online" class="position-absolute bottom-0 end-0 online-dot"></span>
            </div>
            <div class="flex-grow-1 overflow-hidden">
              <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
                <h5 class="fw-700 mb-0">{{ t.full_name }}</h5>
                <span v-if="t.is_top_rated" class="badge bg-warning-subtle text-warning small">Top Rated</span>
                <span v-if="t.is_featured" class="badge bg-primary-subtle text-primary small">Featured</span>
              </div>
              <p class="text-muted small mb-1">{{ t.headline }}</p>
              <div class="gp-stars small mb-2">
                <i class="bi bi-star-fill" v-for="n in 5" :key="n" :class="{ 'opacity-25': n > Math.round(t.average_rating) }"></i>
                <span class="text-muted ms-1">{{ t.average_rating }} ({{ t.total_reviews }}) · {{ t.total_lessons }} lessons</span>
              </div>
              <div class="d-flex flex-wrap gap-1">
                <span v-for="s in (t.subjects_list||[]).slice(0,5)" :key="s.id" class="gp-badge">{{ s.name }}</span>
              </div>
            </div>
            <div class="text-end flex-shrink-0">
              <div class="fw-700 text-gp-primary fs-5">GHS {{ t.hourly_rate }}<span class="text-muted fw-400 small">/hr</span></div>
              <div class="d-grid gap-1 mt-2">
                <button class="btn btn-gp btn-sm" @click.stop="openTutor(t)">View Profile</button>
                <button class="btn btn-outline-secondary btn-sm" @click.stop="msgTutor(t)">
                  <i class="bi bi-chat me-1"></i>Message
                </button>
              </div>
            </div>
          </div>
        </div>

        <GpPagination :page="page" :total-pages="totalPages" @change="changePage" />
      </div>
    </div>

    <!-- Tutor modal -->
    <div class="modal fade" id="tutorModal" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-scrollable">
        <div class="modal-content" v-if="selected">
          <div class="modal-header border-0">
            <div class="d-flex align-items-center gap-3 w-100 flex-wrap">
              <img :src="selected.avatar_url || fallback(selected.full_name)" class="rounded-circle"
                   width="72" height="72" style="object-fit:cover;border:3px solid var(--gp-red)" />
              <div class="flex-grow-1">
                <h4 class="fw-700 mb-0">{{ selected.full_name }}</h4>
                <div class="text-muted small">{{ selected.headline }}</div>
                <div class="gp-stars small">
                  <i class="bi bi-star-fill"></i> {{ selected.average_rating }} ({{ selected.total_reviews }})
                  <span v-if="selected.is_top_rated" class="badge bg-warning-subtle text-warning ms-1">Top Rated</span>
                </div>
              </div>
            </div>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-4">
              <div class="col-md-8">
                <ul class="nav nav-tabs mb-3">
                  <li class="nav-item"><button class="nav-link" :class="{active:mTab==='about'}" @click="mTab='about'">About</button></li>
                  <li class="nav-item"><button class="nav-link" :class="{active:mTab==='reviews'}" @click="mTab='reviews'">Reviews</button></li>
                  <li class="nav-item"><button class="nav-link" :class="{active:mTab==='book'}" @click="mTab='book'">Book</button></li>
                </ul>
                <div v-if="mTab==='about'">
                  <div class="row g-3 mb-3">
                    <div class="col-3 text-center"><div class="fw-700 text-gp-primary fs-5">{{ selected.total_lessons }}</div><div class="text-muted small">Lessons</div></div>
                    <div class="col-3 text-center"><div class="fw-700 text-gp-primary fs-5">{{ selected.total_students }}</div><div class="text-muted small">Students</div></div>
                    <div class="col-3 text-center"><div class="fw-700 text-gp-primary fs-5">{{ selected.years_experience }}yr</div><div class="text-muted small">Experience</div></div>
                    <div class="col-3 text-center"><div class="fw-700 text-gp-primary fs-5">{{ selected.response_time }}m</div><div class="text-muted small">Response</div></div>
                  </div>
                  <p class="text-muted small" v-if="selected.bio">{{ selected.bio }}</p>
                  <div class="d-flex flex-wrap gap-1 mb-3">
                    <span v-for="s in (selected.subjects_list||[])" :key="s.id" class="gp-badge">{{ s.name }}</span>
                  </div>
                </div>
                <ReviewList v-if="mTab==='reviews'" :reviews="modalReviews" :loading="reviewsLoading" />
                <BookingWidget v-if="mTab==='book'" :tutor="selected" :loading="booking"
                               @book="confirmBook" />
              </div>
              <div class="col-md-4">
                <div class="gp-card p-4 mb-3">
                  <div class="fw-800 fs-3 text-gp-primary mb-3">GHS {{ selected.hourly_rate }}<span class="text-muted fw-400 small">/hr</span></div>
                  <div class="d-grid gap-2">
                    <button class="btn btn-gp py-2" @click="mTab='book'"><i class="bi bi-calendar-plus me-2"></i>Book a Lesson</button>
                    <button class="btn btn-gp-outline" @click="msgTutor(selected)"><i class="bi bi-chat me-2"></i>Message</button>
                    <button class="btn btn-outline-secondary" @click="toggleFav(selected)">
                      <i class="bi me-2" :class="favs.has(selected.id)?'bi-heart-fill text-danger':'bi-heart'"></i>
                      {{ favs.has(selected.id) ? 'Saved' : 'Save Tutor' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <PaymentPrompt
      v-if="paymentLesson"
      :lesson="paymentLesson"
      :tutor-name="selected?.full_name || 'your tutor'"
      @cancel="paymentLesson = null"
    />

    <AppFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { debounce } from '@/utils/helpers'
import GpSpinner    from '@/components/common/GpSpinner.vue'
import GpEmpty      from '@/components/common/GpEmpty.vue'
import GpPagination from '@/components/common/GpPagination.vue'
import TutorCard    from '@/components/tutor/TutorCard.vue'
import ReviewList   from '@/components/tutor/ReviewList.vue'
import BookingWidget from '@/components/scheduling/BookingWidget.vue'
import PaymentPrompt from '@/components/payments/PaymentPrompt.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const auth       = useAuthStore()
const notifStore = useNotifStore()
const router     = useRouter()
const tutors     = ref([])
const subjects   = ref([])
const loading    = ref(true)
const total      = ref(0)
const page       = ref(1)
const view       = ref('grid')
const ordering   = ref('-average_rating')
const favs       = ref(new Set())
const selected   = ref(null)
const modalReviews = ref([])
const reviewsLoading = ref(false)
const mTab       = ref('about')
const booking    = ref(false)
const paymentLesson = ref(null)

const filters = ref({
  search:'', subject:'', min_price:'', max_price:'',
  min_rating:'', teaching_style:'', instant_book:false, featured:false
})

const totalPages = computed(() => Math.ceil(total.value / 12))
const fallback = name => `https://ui-avatars.com/api/?name=${encodeURIComponent(name||'T')}&background=e63900&color=fff`

const debouncedFetch = debounce(() => fetchTutors(), 400)

async function fetchTutors() {
  loading.value = true
  try {
    const params = { ordering: ordering.value, page: page.value, page_size: 12 }
    if (filters.value.search)         params.search         = filters.value.search
    if (filters.value.subject)        params.subject        = filters.value.subject
    if (filters.value.min_price)      params.min_price      = filters.value.min_price
    if (filters.value.max_price)      params.max_price      = filters.value.max_price
    if (filters.value.min_rating)     params.min_rating     = filters.value.min_rating
    if (filters.value.teaching_style) params.teaching_style = filters.value.teaching_style
    if (filters.value.instant_book)   params.instant_book   = true
    if (filters.value.featured)       params.is_featured    = true
    const { data } = await apiGet('/tutors/', params)
    tutors.value = data.results || []; total.value = data.count || 0
  } catch { tutors.value = [] }
  finally { loading.value = false }
}

function clearFilters() {
  filters.value = { search:'', subject:'', min_price:'', max_price:'', min_rating:'', teaching_style:'', instant_book:false, featured:false }
  fetchTutors()
}

function changePage(p) { page.value = p; fetchTutors(); window.scrollTo(0,0) }

async function openTutor(t) {
  selected.value = t; mTab.value = 'about'; modalReviews.value = []; reviewsLoading.value = true
  const modal = new Modal(document.getElementById('tutorModal'))
  modal.show()
  try {
    const { data } = await apiGet('/reviews/', { tutor_id: t.id })
    modalReviews.value = data.results || []
  } catch {} finally { reviewsLoading.value = false }
}

async function toggleFav(t) {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  try {
    const { data } = await apiPost(`/tutors/${t.id}/favourite/`)
    const s = new Set(favs.value)
    data.favourited ? s.add(t.id) : s.delete(t.id)
    favs.value = s
    notifStore.toast(data.favourited ? 'Saved to favourites!' : 'Removed from favourites.', 'success')
  } catch {}
}

function msgTutor(t) {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  Modal.getInstance(document.getElementById('tutorModal'))?.hide()
  router.push(`/messages?tutor=${t.id}`)
}

async function confirmBook(form) {
  if (!auth.isAuthenticated) { router.push('/login?next=/tutors'); return }

  const start = new Date(`${form.date}T${form.time}:00`)
  const duration = Number(form.duration)
  const end = new Date(start.getTime() + duration * 60000)
  const price = form.type === 'trial'
    ? Number(selected.value.trial_lesson_price || 0)
    : Number(selected.value.hourly_rate || 0) * duration / 60

  if (Number.isNaN(start.getTime()) || !Number.isFinite(duration) || duration <= 0) {
    notifStore.toast('Please choose a valid date, time, and duration.', 'error')
    return
  }

  booking.value = true
  try {
    if (!selected.value?.user_id) {
      notifStore.toast('Tutor account ID is missing. Please refresh and try again.', 'error')
      return
    }

    const { data } = await apiPost('/scheduling/lessons/', {
      tutor: selected.value.user_id,
      subject: form.subject,
      lesson_type: form.type,
      start_time: start.toISOString(),
      end_time: end.toISOString(),
      price: Number(price.toFixed(2)),
      currency: 'GHS',
      record_session: Boolean(form.record),
      topic: form.topic || '',
      booked_on_behalf: Boolean(form.booked_on_behalf),
      learner_email: form.learner_email || '',
      booker_name: form.booker_name || '',
      booker_phone: form.booker_phone || '',
      booker_relationship: form.booker_relationship || '',
    })

    paymentLesson.value = {
      ...data,
      price: data.price ?? Number(price.toFixed(2)),
      currency: data.currency || 'GHS',
      subject_name: data.subject_name || form.subject,
      tutor_name: selected.value.full_name,
    }

    Modal.getInstance(document.getElementById('tutorModal'))?.hide()
    notifStore.toast('Lesson created. Please complete payment.', 'success')
  } catch(e) {
    notifStore.toast(Object.values(e.response?.data || {}).flat().join(' ') || 'Booking failed.', 'error')
  } finally { booking.value = false }
}

onMounted(async () => {
  const [_, subj] = await Promise.all([fetchTutors(), apiGet('/tutors/subjects/')])
  subjects.value = subj.data?.results || subj.data || []
})
</script>
