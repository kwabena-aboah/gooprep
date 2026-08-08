<template>
  <div>
    <!-- Public nav if not logged in -->
    <nav v-if="!auth.isAuthenticated" class="gp-navbar mb-4">
      <RouterLink to="/" class="me-auto logo"><img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:36px" /></RouterLink>
      <RouterLink to="/login" class="btn btn-sm btn-outline-light me-2">Log in</RouterLink>
      <RouterLink to="/register" class="btn btn-sm btn-gp">Sign up</RouterLink>
    </nav>

    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!profile" icon="bi bi-person-x" message="Tutor not found." action-label="Browse Tutors" action-to="/tutors" />

    <div v-else>
      <!-- Hero banner -->
      <div class="rounded-3 mb-4 p-4 p-md-5 position-relative overflow-hidden" style="background:linear-gradient(135deg,#111,#1a0800);min-height:200px">
        <div class="row align-items-center g-4 position-relative" style="z-index:1">
          <div class="col-auto">
            <div class="position-relative">
              <img :src="profile.avatar_url || fallback" class="rounded-circle" width="100" height="100"
                   style="object-fit:cover;border:4px solid var(--gp-red)" />
              <span v-if="profile.is_online" class="position-absolute bottom-0 end-0 online-dot" style="width:18px;height:18px;border:3px solid #111"></span>
            </div>
          </div>
          <div class="col text-white">
            <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
              <h2 class="fw-800 mb-0">{{ profile.full_name }}</h2>
              <span v-if="profile.is_top_rated" class="badge bg-warning-subtle text-warning"><i class="bi bi-award-fill me-1"></i>Top Rated</span>
              <span v-if="profile.is_featured" class="badge bg-primary-subtle text-primary"><i class="bi bi-star-fill me-1"></i>Featured</span>
            </div>
            <p class="text-white-50 mb-2">{{ profile.headline }}</p>
            <div class="d-flex flex-wrap gap-3 text-white-50 small">
              <span><i class="bi bi-star-fill text-warning me-1"></i>{{ profile.average_rating }} ({{ profile.total_reviews }} reviews)</span>
              <span><i class="bi bi-book me-1"></i>{{ profile.total_lessons }} lessons</span>
              <span><i class="bi bi-people me-1"></i>{{ profile.total_students }} students</span>
              <span><i class="bi bi-briefcase me-1"></i>{{ profile.years_experience }}yr exp</span>
              <span v-if="profile.city"><i class="bi bi-geo-alt me-1"></i>{{ profile.city }}, {{ profile.country }}</span>
            </div>
          </div>
          <div class="col-auto d-flex flex-column gap-2">
            <div class="fw-800 text-white text-center fs-3">GHS {{ profile.hourly_rate }}<span class="text-white-50 fw-400 small">/hr</span></div>
            <button class="btn btn-gp" @click="activeTab='schedule'"><i class="bi bi-calendar-plus me-2"></i>Book Lesson</button>
            <button class="btn btn-outline-light btn-sm" @click="sendMsg"><i class="bi bi-chat me-2"></i>Message</button>
            <button class="btn btn-outline-light btn-sm" @click="toggleFav">
              <i class="bi me-2" :class="isFav?'bi-heart-fill text-danger':'bi-heart'"></i>{{ isFav ? 'Saved' : 'Save' }}
            </button>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Main content -->
        <div class="col-lg-8">
          <ul class="nav nav-tabs mb-4">
            <li class="nav-item" v-for="t in tabs" :key="t">
              <button class="nav-link fw-600 small" :class="{ active: activeTab===t }" @click="activeTab=t">{{ t }}</button>
            </li>
          </ul>

          <!-- About tab -->
          <div v-if="activeTab==='About'">
            <div class="gp-card p-4 mb-4" v-if="profile.bio">
              <h5 class="fw-700 mb-3">About Me</h5>
              <p class="text-muted" style="line-height:1.8">{{ profile.bio }}</p>
            </div>
            <div class="gp-card p-4 mb-4" v-if="profile.intro_video_url">
              <h5 class="fw-700 mb-3"><i class="bi bi-play-circle me-2 text-gp-primary"></i>Introduction Video</h5>
              <video :src="profile.intro_video_url" class="w-100 rounded-3" controls style="max-height:300px;background:#000"></video>
            </div>
            <div class="row g-3 mb-4">
              <div class="col-6 col-md-3" v-for="s in statCards" :key="s.label">
                <div class="gp-card p-3 text-center">
                  <i :class="s.icon" class="fs-3 text-gp-primary d-block mb-1"></i>
                  <div class="fw-800 fs-4 text-gp-primary">{{ s.value }}</div>
                  <div class="text-muted small">{{ s.label }}</div>
                </div>
              </div>
            </div>
            <div class="gp-card p-4 mb-4">
              <h5 class="fw-700 mb-3">Subjects</h5>
              <div class="d-flex flex-wrap gap-2">
                <span v-for="s in profile.subjects_list" :key="s.id" class="gp-badge px-3 py-2">{{ s.name }}</span>
              </div>
            </div>
            <div class="row g-4">
              <div class="col-md-6" v-if="profile.education?.length">
                <div class="gp-card p-4">
                  <h5 class="fw-700 mb-3"><i class="bi bi-mortarboard me-2 text-gp-primary"></i>Education</h5>
                  <div v-for="e in profile.education" :key="e.institution" class="mb-2">
                    <div class="fw-600 small">{{ e.degree }}</div>
                    <div class="text-muted small">{{ e.institution }} · {{ e.year }}</div>
                  </div>
                </div>
              </div>
              <div class="col-md-6" v-if="profile.certifications?.length">
                <div class="gp-card p-4">
                  <h5 class="fw-700 mb-3"><i class="bi bi-patch-check me-2 text-success"></i>Certifications</h5>
                  <div v-for="c in profile.certifications" :key="c.name" class="d-flex gap-2 mb-2">
                    <i class="bi bi-check-circle-fill text-success mt-1 flex-shrink-0"></i>
                    <div><div class="fw-600 small">{{ c.name }}</div><div class="text-muted small">{{ c.issuer }} · {{ c.year }}</div></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Reviews tab -->
          <ReviewList v-if="activeTab==='Reviews'" :reviews="reviews" :loading="reviewsLoading" />

          <!-- Schedule / Book tab -->
          <div v-if="activeTab==='schedule'">
            <div class="gp-card p-4 mb-4">
              <h5 class="fw-700 mb-3">Weekly Availability</h5>
              <div v-if="!availability.length" class="text-muted small">No availability set. Contact tutor directly.</div>
              <div class="row g-2">
                <div v-for="slot in availability" :key="slot.id" class="col-md-6">
                  <div class="border rounded-3 p-3 d-flex align-items-center gap-2">
                    <i class="bi bi-clock text-gp-primary"></i>
                    <span class="small fw-600">{{ days[slot.day_of_week] }}</span>
                    <span class="text-muted small ms-2">{{ slot.start_time }} – {{ slot.end_time }}</span>
                  </div>
                </div>
              </div>
            </div>
            <BookingWidget :tutor="profile" :loading="booking" @book="confirmBook" />
          </div>

          <PaymentPrompt
            v-if="paymentLesson"
            :lesson="paymentLesson"
            :tutor-name="profile.full_name"
            @cancel="paymentLesson = null"
          />
        </div>

        <!-- Sidebar -->
        <div class="col-lg-4">
          <div class="gp-card p-4 sticky-top" style="top:80px">
            <div class="d-flex justify-content-between align-items-baseline mb-3">
              <span class="fw-800 fs-2 text-gp-primary">GHS {{ profile.hourly_rate }}</span>
              <span class="text-muted small">/hr</span>
            </div>
            <div v-if="profile.trial_lesson_enabled" class="gp-card-flat p-3 mb-3 text-center" style="background:rgba(230,57,0,.05);border:1px solid rgba(230,57,0,.2)">
              <div class="fw-600 small text-gp-primary"><i class="bi bi-gift-fill me-1"></i>Trial lesson</div>
              <div class="fw-800 text-gp-primary">GHS {{ profile.trial_lesson_price }}</div>
            </div>
            <div class="d-grid gap-2 mb-3">
              <button class="btn btn-gp py-2" @click="activeTab='schedule'"><i class="bi bi-calendar-plus me-2"></i>Book a Lesson</button>
              <button class="btn btn-gp-outline" @click="sendMsg"><i class="bi bi-chat me-2"></i>Send Message</button>
              <button class="btn btn-outline-secondary" @click="toggleFav">
                <i class="bi me-2" :class="isFav?'bi-heart-fill text-danger':'bi-heart'"></i>{{ isFav?'Saved':'Save Tutor' }}
              </button>
            </div>
            <div class="gp-card-flat p-3" style="background:var(--gp-surface)">
              <div class="fw-600 small mb-2"><i class="bi bi-camera-video me-1 text-gp-primary"></i>Live via BigBlueButton</div>
              <div class="d-flex flex-wrap gap-1">
                <span v-for="f in ['HD Video','Whiteboard','Recording','Screen Share','Chat']" :key="f" class="badge bg-primary-subtle text-primary small">{{ f }}</span>
              </div>
            </div>
          </div>
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
import GpSpinner    from '@/components/common/GpSpinner.vue'
import GpEmpty      from '@/components/common/GpEmpty.vue'
import ReviewList   from '@/components/tutor/ReviewList.vue'
import BookingWidget from '@/components/scheduling/BookingWidget.vue'
import PaymentPrompt from '@/components/payments/PaymentPrompt.vue'

const route      = useRoute()
const router     = useRouter()
const auth       = useAuthStore()
const notifStore = useNotifStore()
const loading    = ref(true)
const profile    = ref(null)
const reviews    = ref([])
const reviewsLoading = ref(false)
const availability = ref([])
const isFav      = ref(false)
const activeTab  = ref('About')
const booking    = ref(false)
const paymentLesson = ref(null)
const tabs       = ['About', 'Reviews', 'schedule']
const days       = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
const fallback   = computed(() => `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.value?.full_name||'T')}&background=e63900&color=fff`)
const statCards  = computed(() => profile.value ? [
  { icon:'bi bi-calendar-check', label:'Lessons',    value: profile.value.total_lessons },
  { icon:'bi bi-people',         label:'Students',   value: profile.value.total_students },
  { icon:'bi bi-star-fill',      label:'Avg Rating', value: profile.value.average_rating },
  { icon:'bi bi-chat-dots',      label:'Response',   value: profile.value.response_time+'m' },
] : [])

async function sendMsg() {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  router.push(`/messages?tutor=${profile.value?.id}`)
}

async function toggleFav() {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  try {
    const { data } = await apiPost(`/tutors/${profile.value.id}/favourite/`)
    isFav.value = data.favourited
    notifStore.toast(isFav.value ? 'Saved!' : 'Removed.', 'success')
  } catch {}
}

async function confirmBook(form) {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  booking.value = true
  const start = new Date(`${form.date}T${form.time}:00`)
  const end   = new Date(start.getTime() + parseInt(form.duration)*60000)
  const price = form.type === 'trial'
    ? profile.value.trial_lesson_price
    : (profile.value.hourly_rate * form.duration / 60).toFixed(2)

  try {
    const { data } = await apiPost('/scheduling/lessons/', {
      tutor: profile.value.id, subject: form.subject, lesson_type: form.type,
      start_time: start.toISOString(), end_time: end.toISOString(),
      price, currency: 'GHS', record_session: form.record, topic: form.topic,
    })
    paymentLesson.value = { ...data, price, start_time: start.toISOString(), subject_name: profile.value.subjects_list?.find(s => s.id === form.subject)?.name }
  } catch (e) {
    notifStore.toast(Object.values(e.response?.data || {}).flat().join(' ') || 'Failed to create lesson.', 'error')
  } finally {
    booking.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await apiGet(`/tutors/${route.params.id}/`)
    profile.value = data
    reviewsLoading.value = true
    const [rev, avail] = await Promise.all([
      apiGet('/reviews/', { tutor_id: data.id, page_size: 30 }),
      apiGet(`/tutors/${data.id}/availability/`),
    ])
    reviews.value      = rev.data?.results || []
    availability.value = Array.isArray(avail.data) ? avail.data : (avail.data?.results || [])
    reviewsLoading.value = false
  } catch(e) { console.error(e) }
  finally { loading.value = false }
})
</script>
