<template>
  <div class="tutor-profile-page">

    <!-- Public navigation -->
    <nav v-if="!auth.isAuthenticated" class="gp-navbar mb-4">
      <RouterLink to="/" class="me-auto logo">
        <img
          src="@/assets/img/gooprep_logo.png"
          alt="Gooprep"
          style="height:36px"
        />
      </RouterLink>

      <RouterLink
        to="/login"
        class="btn btn-sm btn-outline-light me-2"
      >
        Log in
      </RouterLink>

      <RouterLink
        to="/register"
        class="btn btn-sm btn-gp"
      >
        Sign up
      </RouterLink>
    </nav>

    <!-- Page loading -->
    <GpSpinner v-if="loading" />

    <!-- Tutor not found -->
    <GpEmpty
      v-else-if="!profile"
      icon="bi bi-person-x"
      message="Tutor not found."
      action-label="Browse Tutors"
      action-to="/tutors"
    />

    <!-- Tutor profile -->
    <div v-else>

      <!-- =========================================================
           HERO
      ========================================================== -->
      <div
        class="rounded-3 mb-4 p-4 p-md-5 position-relative overflow-hidden"
        style="
          background:linear-gradient(135deg,#111,#1a0800);
          min-height:200px;
        "
      >
        <div
          class="row align-items-center g-4 position-relative"
          style="z-index:1"
        >

          <!-- Avatar -->
          <div class="col-auto">
            <div class="position-relative">

              <img
                :src="profile.avatar_url || fallback"
                class="rounded-circle"
                width="100"
                height="100"
                alt="Tutor avatar"
                style="
                  object-fit:cover;
                  border:4px solid var(--gp-red);
                "
              />

              <span
                v-if="profile.is_online"
                class="position-absolute bottom-0 end-0 online-dot"
                style="
                  width:18px;
                  height:18px;
                  border:3px solid #111;
                "
              ></span>

            </div>
          </div>

          <!-- Tutor information -->
          <div class="col text-white">

            <div
              class="d-flex align-items-center gap-2 flex-wrap mb-1"
            >

              <h2 class="fw-800 mb-0">
                {{ profile.full_name }}
              </h2>

              <span
                v-if="profile.is_top_rated"
                class="badge bg-warning-subtle text-warning"
              >
                <i class="bi bi-award-fill me-1"></i>
                Top Rated
              </span>

              <span
                v-if="profile.is_featured"
                class="badge bg-primary-subtle text-primary"
              >
                <i class="bi bi-star-fill me-1"></i>
                Featured
              </span>

            </div>

            <p class="text-white-50 mb-2">
              {{ profile.headline }}
            </p>

            <div
              class="d-flex flex-wrap gap-3 text-white-50 small"
            >

              <span>
                <i class="bi bi-star-fill text-warning me-1"></i>
                {{ profile.average_rating || 0 }}
                ({{ profile.total_reviews || 0 }} reviews)
              </span>

              <span>
                <i class="bi bi-book me-1"></i>
                {{ profile.total_lessons || 0 }} lessons
              </span>

              <span>
                <i class="bi bi-people me-1"></i>
                {{ profile.total_students || 0 }} students
              </span>

              <span>
                <i class="bi bi-briefcase me-1"></i>
                {{ profile.years_experience || 0 }}yr exp
              </span>

              <span v-if="profile.city">
                <i class="bi bi-geo-alt me-1"></i>
                {{ profile.city }}, {{ profile.country }}
              </span>

            </div>
          </div>

          <!-- Hero actions -->
          <div class="col-auto d-flex flex-column gap-2">

            <div class="fw-800 text-white text-center fs-3">
              GHS {{ formatMoney(profile.hourly_rate) }}
              <span class="text-white-50 fw-400 small">
                /hr
              </span>
            </div>

            <button
              type="button"
              class="btn btn-gp"
              @click="goToSchedule"
            >
              <i class="bi bi-calendar-plus me-2"></i>
              Book Lesson
            </button>

            <button
              type="button"
              class="btn btn-outline-light btn-sm"
              @click="sendMsg"
            >
              <i class="bi bi-chat me-2"></i>
              Message
            </button>

            <button
              type="button"
              class="btn btn-outline-light btn-sm"
              @click="toggleFav"
            >
              <i
                class="bi me-2"
                :class="
                  isFav
                    ? 'bi-heart-fill text-danger'
                    : 'bi-heart'
                "
              ></i>

              {{ isFav ? 'Saved' : 'Save' }}
            </button>

          </div>

        </div>
      </div>

      <!-- =========================================================
           MAIN CONTENT
      ========================================================== -->
      <div class="row g-4">

        <!-- Main column -->
        <div class="col-lg-8">

          <!-- Tabs -->
          <ul class="nav nav-tabs mb-4">

            <li
              v-for="tab in tabs"
              :key="tab.key"
              class="nav-item"
            >
              <button
                type="button"
                class="nav-link fw-600 small"
                :class="{
                  active: activeTab === tab.key
                }"
                @click="activeTab = tab.key"
              >
                {{ tab.label }}
              </button>
            </li>

          </ul>

          <!-- =====================================================
               ABOUT
          ====================================================== -->
          <div v-if="activeTab === 'About'">

            <div
              v-if="profile.bio"
              class="gp-card p-4 mb-4"
            >
              <h5 class="fw-700 mb-3">
                About Me
              </h5>

              <p
                class="text-muted"
                style="line-height:1.8"
              >
                {{ profile.bio }}
              </p>
            </div>

            <!-- Intro video -->
            <div
              v-if="profile.intro_video_url"
              class="gp-card p-4 mb-4"
            >

              <h5 class="fw-700 mb-3">
                <i
                  class="bi bi-play-circle me-2 text-gp-primary"
                ></i>
                Introduction Video
              </h5>

              <video
                :src="profile.intro_video_url"
                class="w-100 rounded-3"
                controls
                style="
                  max-height:300px;
                  background:#000;
                "
              ></video>

            </div>

            <!-- Statistics -->
            <div class="row g-3 mb-4">

              <div
                v-for="stat in statCards"
                :key="stat.label"
                class="col-6 col-md-3"
              >
                <div class="gp-card p-3 text-center">

                  <i
                    :class="stat.icon"
                    class="fs-3 text-gp-primary d-block mb-1"
                  ></i>

                  <div
                    class="fw-800 fs-4 text-gp-primary"
                  >
                    {{ stat.value }}
                  </div>

                  <div class="text-muted small">
                    {{ stat.label }}
                  </div>

                </div>
              </div>

            </div>

            <!-- Subjects -->
            <div class="gp-card p-4 mb-4">

              <h5 class="fw-700 mb-3">
                Subjects
              </h5>

              <div class="d-flex flex-wrap gap-2">

                <span
                  v-for="subject in subjects"
                  :key="subject.id"
                  class="gp-badge px-3 py-2"
                >
                  {{ subject.name }}
                </span>

                <span
                  v-if="!subjects.length"
                  class="text-muted small"
                >
                  No subjects listed.
                </span>

              </div>
            </div>

            <!-- Education / Certifications -->
            <div class="row g-4">

              <!-- Education -->
              <div
                v-if="profile.education?.length"
                class="col-md-6"
              >

                <div class="gp-card p-4">

                  <h5 class="fw-700 mb-3">
                    <i
                      class="bi bi-mortarboard me-2 text-gp-primary"
                    ></i>
                    Education
                  </h5>

                  <div
                    v-for="education in profile.education"
                    :key="education.institution"
                    class="mb-2"
                  >

                    <div class="fw-600 small">
                      {{ education.degree }}
                    </div>

                    <div class="text-muted small">
                      {{ education.institution }}
                      <span v-if="education.year">
                        · {{ education.year }}
                      </span>
                    </div>

                  </div>

                </div>

              </div>

              <!-- Certifications -->
              <div
                v-if="profile.certifications?.length"
                class="col-md-6"
              >

                <div class="gp-card p-4">

                  <h5 class="fw-700 mb-3">
                    <i
                      class="bi bi-patch-check me-2 text-success"
                    ></i>
                    Certifications
                  </h5>

                  <div
                    v-for="certification in profile.certifications"
                    :key="certification.name"
                    class="d-flex gap-2 mb-2"
                  >

                    <i
                      class="
                        bi
                        bi-check-circle-fill
                        text-success
                        mt-1
                        flex-shrink-0
                      "
                    ></i>

                    <div>

                      <div class="fw-600 small">
                        {{ certification.name }}
                      </div>

                      <div class="text-muted small">
                        {{ certification.issuer }}

                        <span
                          v-if="certification.year"
                        >
                          · {{ certification.year }}
                        </span>
                      </div>

                    </div>

                  </div>

                </div>

              </div>

            </div>

          </div>

          <!-- =====================================================
               REVIEWS
          ====================================================== -->
          <ReviewList
            v-else-if="activeTab === 'Reviews'"
            :reviews="reviews"
            :loading="reviewsLoading"
          />

          <!-- =====================================================
               SCHEDULE / BOOK
          ====================================================== -->
          <div v-else-if="activeTab === 'Schedule'">

            <!-- Availability -->
            <div class="gp-card p-4 mb-4">

              <h5 class="fw-700 mb-3">
                Weekly Availability
              </h5>

              <div
                v-if="!availability.length"
                class="text-muted small"
              >
                No availability set. Contact tutor directly.
              </div>

              <div
                v-else
                class="row g-2"
              >

                <div
                  v-for="slot in availability"
                  :key="slot.id"
                  class="col-md-6"
                >

                  <div
                    class="
                      border
                      rounded-3
                      p-3
                      d-flex
                      align-items-center
                      gap-2
                    "
                  >

                    <i
                      class="
                        bi
                        bi-clock
                        text-gp-primary
                      "
                    ></i>

                    <span class="small fw-600">
                      {{ getDayName(slot.day_of_week) }}
                    </span>

                    <span
                      class="
                        text-muted
                        small
                        ms-2
                      "
                    >
                      {{ slot.start_time }}
                      –
                      {{ slot.end_time }}
                    </span>

                  </div>

                </div>

              </div>

            </div>

            <!-- Booking error -->
            <div
              v-if="bookingError"
              class="alert alert-danger mb-4"
              role="alert"
            >
              <i
                class="
                  bi
                  bi-exclamation-triangle-fill
                  me-2
                "
              ></i>

              {{ bookingError }}

              <button
                type="button"
                class="btn-close float-end"
                aria-label="Close"
                @click="bookingError = ''"
              ></button>
            </div>

            <!-- Booking widget -->
            <BookingWidget
              :tutor="profile"
              :loading="booking"
              :allow-on-behalf="canBookOnBehalf"
              @book="confirmBook"
            />

          </div>

          <!-- =====================================================
               PAYMENT PROMPT
          ====================================================== -->
          <div
            v-if="paymentLesson"
            class="mt-4"
          >

            <PaymentPrompt
              :lesson="paymentLesson"
              :tutor-name="profile.full_name"
              @cancel="closePaymentPrompt"
            />

          </div>

        </div>

        <!-- =======================================================
             SIDEBAR
        ======================================================== -->
        <div class="col-lg-4">

          <div
            class="gp-card p-4 sticky-top"
            style="top:80px"
          >

            <div
              class="
                d-flex
                justify-content-between
                align-items-baseline
                mb-3
              "
            >

              <span
                class="
                  fw-800
                  fs-2
                  text-gp-primary
                "
              >
                GHS {{ formatMoney(profile.hourly_rate) }}
              </span>

              <span class="text-muted small">
                /hr
              </span>

            </div>

            <!-- Trial lesson -->
            <div
              v-if="profile.trial_lesson_enabled"
              class="
                gp-card-flat
                p-3
                mb-3
                text-center
              "
              style="
                background:rgba(230,57,0,.05);
                border:1px solid rgba(230,57,0,.2)
              "
            >

              <div
                class="
                  fw-600
                  small
                  text-gp-primary
                "
              >
                <i class="bi bi-gift-fill me-1"></i>
                Trial lesson
              </div>

              <div
                class="
                  fw-800
                  text-gp-primary
                "
              >
                GHS
                {{ formatMoney(profile.trial_lesson_price) }}
              </div>

            </div>

            <div class="d-grid gap-2 mb-3">

              <button
                type="button"
                class="btn btn-gp py-2"
                @click="goToSchedule"
              >
                <i
                  class="
                    bi
                    bi-calendar-plus
                    me-2
                  "
                ></i>
                Book a Lesson
              </button>

              <button
                type="button"
                class="btn btn-gp-outline"
                @click="sendMsg"
              >
                <i
                  class="
                    bi
                    bi-chat
                    me-2
                  "
                ></i>
                Send Message
              </button>

              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="toggleFav"
              >

                <i
                  class="bi me-2"
                  :class="
                    isFav
                      ? 'bi-heart-fill text-danger'
                      : 'bi-heart'
                  "
                ></i>

                {{ isFav ? 'Saved' : 'Save Tutor' }}

              </button>

            </div>

            <!-- BigBlueButton -->
            <div
              class="gp-card-flat p-3"
              style="background:var(--gp-surface)"
            >

              <div class="fw-600 small mb-2">

                <i
                  class="
                    bi
                    bi-camera-video
                    me-1
                    text-gp-primary
                  "
                ></i>

                Live via BigBlueButton

              </div>

              <div class="d-flex flex-wrap gap-1">

                <span
                  v-for="feature in meetingFeatures"
                  :key="feature"
                  class="
                    badge
                    bg-primary-subtle
                    text-primary
                    small
                  "
                >
                  {{ feature }}
                </span>

              </div>

            </div>

          </div>

        </div>

      </div>

    </div>

  </div>
</template>


<script setup>
import {
  ref,
  computed,
  onMounted
} from 'vue'

import {
  useRoute,
  useRouter
} from 'vue-router'

import {
  useAuthStore
} from '@/stores/auth'

import {
  useNotifStore
} from '@/stores/notifs'

import {
  apiGet,
  apiPost
} from '@/utils/api'

import GpSpinner
  from '@/components/common/GpSpinner.vue'

import GpEmpty
  from '@/components/common/GpEmpty.vue'

import ReviewList
  from '@/components/tutor/ReviewList.vue'

import BookingWidget
  from '@/components/scheduling/BookingWidget.vue'

import PaymentPrompt
  from '@/components/payments/PaymentPrompt.vue'


/* ============================================================
   ROUTER / STORES
============================================================ */

const route = useRoute()
const router = useRouter()

const auth = useAuthStore()
const notifStore = useNotifStore()


/* ============================================================
   STATE
============================================================ */

const loading = ref(true)

const profile = ref(null)

const reviews = ref([])

const reviewsLoading = ref(false)

const availability = ref([])

const isFav = ref(false)

const activeTab = ref('About')

const booking = ref(false)

const paymentLesson = ref(null)

const bookingError = ref('')


/* ============================================================
   CONSTANTS
============================================================ */

const tabs = [
  {
    key: 'About',
    label: 'About'
  },
  {
    key: 'Reviews',
    label: 'Reviews'
  },
  {
    key: 'Schedule',
    label: 'Schedule & Book'
  }
]

const days = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
]

const meetingFeatures = [
  'HD Video',
  'Whiteboard',
  'Recording',
  'Screen Share',
  'Chat'
]


/* ============================================================
   COMPUTED
============================================================ */

const fallback = computed(() => {
  const name =
    profile.value?.full_name || 'Tutor'

  return (
    `https://ui-avatars.com/api/?name=` +
    `${encodeURIComponent(name)}` +
    `&background=e63900&color=fff`
  )
})


const subjects = computed(() => {
  return Array.isArray(profile.value?.subjects_list)
    ? profile.value.subjects_list
    : []
})


const statCards = computed(() => {
  if (!profile.value) {
    return []
  }

  return [
    {
      icon: 'bi bi-calendar-check',
      label: 'Lessons',
      value: profile.value.total_lessons || 0
    },
    {
      icon: 'bi bi-people',
      label: 'Students',
      value: profile.value.total_students || 0
    },
    {
      icon: 'bi bi-star-fill',
      label: 'Avg Rating',
      value: profile.value.average_rating || 0
    },
    {
      icon: 'bi bi-chat-dots',
      label: 'Response',
      value: profile.value.response_time
        ? `${profile.value.response_time}m`
        : 'N/A'
    }
  ]
})


/*
 * Determine whether the current user can book
 * on behalf of another learner.
 *
 * We support both:
 *
 * auth.isStudent
 * auth.isAdmin
 *
 * and common role-based auth stores.
 */

const canBookOnBehalf = computed(() => {
  if (!auth.isAuthenticated) {
    return false
  }

  if (auth.isAdmin === true) {
    return true
  }

  if (auth.isStudent === true) {
    return true
  }

  const role =
    auth.user?.role ||
    auth.user?.user_type ||
    auth.user?.account_type

  return [
    'student',
    'Student',
    'admin',
    'Admin'
  ].includes(role)
})


/* ============================================================
   HELPERS
============================================================ */

function formatMoney(value) {
  const number = Number(value)

  if (!Number.isFinite(number)) {
    return '0.00'
  }

  return number.toFixed(2)
}


function getDayName(day) {
  const index = Number(day)

  if (
    Number.isInteger(index) &&
    index >= 0 &&
    index < days.length
  ) {
    return days[index]
  }

  return day ?? ''
}


function getBookingError(error) {
  const data = error?.response?.data

  if (!data) {
    return 'Failed to create lesson. Please try again.'
  }

  /*
   * DRF commonly returns:
   *
   * {
   *   field: ["Error message"]
   * }
   */

  if (typeof data === 'string') {
    return data
  }

  if (data.detail) {
    return Array.isArray(data.detail)
      ? data.detail.join(' ')
      : String(data.detail)
  }

  const messages = []

  Object.entries(data).forEach(
    ([field, value]) => {

      if (Array.isArray(value)) {
        messages.push(
          `${field}: ${value.join(' ')}`
        )
      } else if (value) {
        messages.push(
          `${field}: ${value}`
        )
      }

    }
  )

  return messages.length
    ? messages.join(' ')
    : 'Failed to create lesson. Please try again.'
}


function getSubjectName(subjectId) {
  if (!subjectId) {
    return ''
  }

  const subject = subjects.value.find(
    item =>
      String(item.id) === String(subjectId)
  )

  return subject?.name || ''
}


/* ============================================================
   NAVIGATION
============================================================ */

function goToSchedule() {
  activeTab.value = 'Schedule'

  /*
   * Give Vue time to render the Schedule tab,
   * then scroll the booking section into view.
   */

  setTimeout(() => {

    const element =
      document.querySelector(
        '.tutor-profile-page .nav-tabs'
      )

    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }

  }, 50)
}


function sendMsg() {
  if (!auth.isAuthenticated) {
    router.push('/login')
    return
  }

  if (!profile.value?.id) {
    return
  }

  router.push(
    `/messages?tutor=${profile.value.id}`
  )
}


/* ============================================================
   FAVOURITES
============================================================ */

async function toggleFav() {

  if (!auth.isAuthenticated) {
    router.push('/login')
    return
  }

  if (!profile.value?.id) {
    return
  }

  try {

    const { data } = await apiPost(
      `/tutors/${profile.value.id}/favourite/`
    )

    isFav.value =
      Boolean(data?.favourited)

    notifStore.toast(
      isFav.value
        ? 'Tutor saved!'
        : 'Tutor removed from saved tutors.',
      'success'
    )

  } catch (error) {

    console.error(
      'Favourite error:',
      error
    )

    notifStore.toast(
      'Unable to update favourites.',
      'error'
    )

  }
}


/* ============================================================
   BOOKING
============================================================ */

async function confirmBook(form) {

  /*
   * Always clear previous errors.
   */

  bookingError.value = ''

  /*
   * User must be authenticated.
   */

  if (!auth.isAuthenticated) {
    router.push('/login')
    return
  }

  /*
   * Make sure tutor profile exists.
   */

  if (!profile.value) {
    bookingError.value =
      'Tutor information is not available.'

    return
  }

  /*
   * Validate form.
   */

  if (!form?.date) {
    bookingError.value =
      'Please select a lesson date.'

    return
  }

  if (!form?.time) {
    bookingError.value =
      'Please select a lesson time.'

    return
  }

  const duration =
    Number(form.duration)

  if (
    !Number.isFinite(duration) ||
    duration <= 0
  ) {
    bookingError.value =
      'Please select a valid lesson duration.'

    return
  }

  /*
   * Create local start/end Date objects.
   */

  const start = new Date(
    `${form.date}T${form.time}:00`
  )

  if (Number.isNaN(start.getTime())) {
    bookingError.value =
      'Invalid lesson date or time.'

    return
  }

  const end = new Date(
    start.getTime() +
    duration * 60 * 1000
  )

  /*
   * Calculate lesson price.
   */

  let price

  if (form.type === 'trial') {

    price = Number(
      profile.value.trial_lesson_price || 0
    )

  } else {

    price =
      Number(profile.value.hourly_rate || 0) *
      duration /
      60

  }

  if (!Number.isFinite(price)) {
    bookingError.value =
      'Unable to calculate lesson price.'

    return
  }

  /*
   * Tutor ID.
   *
   * Some APIs expose user_id while others expose id.
   */

  const tutorId = profile.value.user_id

  if (!tutorId) {
    bookingError.value =
      'Tutor account ID is missing.'

    return
  }

  /*
   * Normalize the "book on behalf" value.
   */

  const bookedOnBehalf =
    Boolean(form.booked_on_behalf)

  /*
   * Prepare request.
   */

  const payload = {

    tutor: tutorId,

    subject: form.subject || null,

    lesson_type:
      form.type || 'regular',

    start_time:
      start.toISOString(),

    end_time:
      end.toISOString(),

    price:
      Number(price.toFixed(2)),

    currency: 'GHS',

    record_session:
      Boolean(form.record),

    topic:
      form.topic || '',

    booked_on_behalf:
      bookedOnBehalf,

    learner_email:
      form.learner_email || '',

    booker_name:
      form.booker_name ||
      auth.user?.full_name ||
      auth.user?.name ||
      '',

    booker_phone:
      form.booker_phone ||
      auth.user?.phone ||
      '',

    booker_email:
      auth.user?.email || '',

    booker_relationship:
      bookedOnBehalf
        ? (
            form.booker_relationship ||
            'Parent/Guardian'
          )
        : ''

  }

  /*
   * Debug information.
   *
   * Keep this during development.
   * Remove or disable before production.
   */

  console.log(
    '[Booking] Payload:',
    payload
  )

  booking.value = true

  try {
    console.log('========== BOOKING REQUEST ==========')
    console.log('Tutor:', profile.value)
    console.log('Form:', form)
    console.log('Payload:', payload)
    console.log('======================================')
    const response =
      await apiPost(
        '/scheduling/lessons/',
        payload
      )

    const data =
      response?.data

    console.log(
      '[Booking] API response:',
      data
    )

    if (!data) {
      throw new Error(
        'The server did not return the created lesson.'
      )
    }

    /*
     * Find subject name for payment screen.
     */

    const subjectName =
      getSubjectName(form.subject)

    /*
     * IMPORTANT:
     *
     * This is what causes PaymentPrompt
     * to appear.
     */

    paymentLesson.value = {

      ...data,

      price:
        data.price ??
        Number(price.toFixed(2)),

      currency:
        data.currency ||
        'GHS',

      start_time:
        data.start_time ||
        start.toISOString(),

      end_time:
        data.end_time ||
        end.toISOString(),

      subject_name:
        data.subject_name ||
        subjectName,

      tutor_name:
        profile.value.full_name

    }

    console.log(
      '[Booking] Payment lesson:',
      paymentLesson.value
    )

    /*
     * Make sure the user can see the payment prompt.
     */

    setTimeout(() => {

      const paymentElement =
        document.querySelector(
          '.tutor-profile-page .payment-prompt'
        )

      if (paymentElement) {

        paymentElement.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        })

      }

    }, 100)

    notifStore.toast(
      'Lesson created. Please complete payment.',
      'success'
    )

  } catch (error) {

    console.error(
      '[Booking] Failed:',
      error
    )

    console.error(
      '[Booking] Server response:',
      error?.response?.data
    )

    bookingError.value =
      getBookingError(error)

    notifStore.toast(
      bookingError.value,
      'error'
    )

  } finally {

    booking.value = false

  }
}


/* ============================================================
   PAYMENT
============================================================ */

function closePaymentPrompt() {
  paymentLesson.value = null
}


/* ============================================================
   INITIAL LOAD
============================================================ */

async function loadTutorProfile() {

  loading.value = true

  try {

    const tutorId =
      route.params.id

    if (!tutorId) {
      throw new Error(
        'Tutor ID is missing from the URL.'
      )
    }

    /*
     * Load tutor profile first.
     */

    const profileResponse =
      await apiGet(
        `/tutors/${tutorId}/`
      )

    profile.value =
      profileResponse?.data || null

    if (!profile.value) {
      return
    }

    /*
     * Load reviews and availability
     * independently so one failure doesn't
     * destroy the whole page.
     */

    reviewsLoading.value = true

    const [
      reviewsResponse,
      availabilityResponse
    ] = await Promise.allSettled([

      apiGet(
        '/reviews/',
        {
          tutor_id: profile.value.id,
          page_size: 30
        }
      ),

      apiGet(
        `/tutors/${profile.value.id}/availability/`
      )

    ])

    /*
     * Reviews
     */

    if (
      reviewsResponse.status === 'fulfilled'
    ) {

      const data =
        reviewsResponse.value?.data

      reviews.value =
        Array.isArray(data)
          ? data
          : (
              Array.isArray(data?.results)
                ? data.results
                : []
            )

    } else {

      console.error(
        'Failed to load reviews:',
        reviewsResponse.reason
      )

      reviews.value = []

    }

    /*
     * Availability
     */

    if (
      availabilityResponse.status === 'fulfilled'
    ) {

      const data =
        availabilityResponse.value?.data

      availability.value =
        Array.isArray(data)
          ? data
          : (
              Array.isArray(data?.results)
                ? data.results
                : []
            )

    } else {

      console.error(
        'Failed to load availability:',
        availabilityResponse.reason
      )

      availability.value = []

    }

  } catch (error) {

    console.error(
      'Failed to load tutor profile:',
      error
    )

    profile.value = null

  } finally {

    reviewsLoading.value = false

    loading.value = false

  }
}


/* ============================================================
   MOUNT
============================================================ */

onMounted(() => {
  loadTutorProfile()
})
</script>