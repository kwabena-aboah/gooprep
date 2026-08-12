<template>
  <div class="gp-card p-4">

    <!-- =========================================================
         HEADER / PRICE
    ========================================================== -->
    <div class="d-flex justify-content-between align-items-baseline mb-3">
      <div>
        <span class="fw-800 fs-2 text-gp-primary">
          GHS {{ formatMoney(tutor.hourly_rate) }}
        </span>

        <span class="text-muted small">
          /hr
        </span>
      </div>

      <span
        v-if="tutor.instant_book"
        class="badge bg-success-subtle text-success"
      >
        <i class="bi bi-lightning-fill me-1"></i>
        Instant
      </span>
    </div>


    <!-- =========================================================
         TRIAL LESSON
    ========================================================== -->
    <div
      v-if="tutor.trial_lesson_enabled"
      class="d-flex align-items-center gap-2 p-3 rounded-3 mb-3"
      style="
        background:rgba(230,57,0,.06);
        border:1px solid rgba(230,57,0,.15);
      "
    >
      <i class="bi bi-gift-fill text-gp-primary fs-5"></i>

      <div class="small">
        <div class="fw-600">
          Trial lesson available
        </div>

        <div class="text-muted">
          GHS {{ formatMoney(tutor.trial_lesson_price) }}
          · 30 min
        </div>
      </div>

      <button
        type="button"
        class="btn btn-sm btn-outline-danger ms-auto"
        @click="selectTrial"
        :disabled="loading"
      >
        Select
      </button>
    </div>


    <!-- =========================================================
         BOOKING ERROR
    ========================================================== -->
    <div
      v-if="validationError"
      class="alert alert-danger py-2 small"
      role="alert"
    >
      <i class="bi bi-exclamation-triangle-fill me-1"></i>
      {{ validationError }}
    </div>


    <!-- =========================================================
         DATE / TIME
    ========================================================== -->
    <div class="row g-2 mb-3">

      <div class="col-6">
        <label
          for="booking-date"
          class="form-label small fw-600"
        >
          Date *
        </label>

        <input
          id="booking-date"
          v-model="form.date"
          type="date"
          class="form-control form-control-sm"
          :min="today"
          :disabled="loading"
          @change="clearValidationError"
        />
      </div>


      <div class="col-6">
        <label
          for="booking-time"
          class="form-label small fw-600"
        >
          Time *
        </label>

        <input
          id="booking-time"
          v-model="form.time"
          type="time"
          class="form-control form-control-sm"
          :disabled="loading"
          @change="clearValidationError"
        />
      </div>

    </div>


    <!-- =========================================================
         SUBJECT
    ========================================================== -->
    <div
      v-if="subjects.length"
      class="mb-3"
    >
      <label
        for="booking-subject"
        class="form-label small fw-600"
      >
        Subject *
      </label>

      <select
        id="booking-subject"
        v-model="form.subject"
        class="form-select form-select-sm"
        :disabled="loading"
        @change="clearValidationError"
      >
        <option
          v-for="subject in subjects"
          :key="subject.id"
          :value="subject.id"
        >
          {{ subject.name }}
        </option>
      </select>
    </div>

    <div
      v-else
      class="alert alert-warning py-2 small"
    >
      <i class="bi bi-info-circle me-1"></i>
      No subjects are available for this tutor.
    </div>


    <!-- =========================================================
         LESSON TYPE
    ========================================================== -->
    <div class="mb-3">

      <label class="form-label small fw-600">
        Lesson Type
      </label>

      <div class="row g-2">

        <!-- Regular -->
        <div class="col-6">
          <button
            type="button"
            class="btn w-100 text-start"
            :class="
              form.type === 'regular'
                ? 'btn-gp'
                : 'btn-outline-secondary'
            "
            :disabled="loading"
            @click="selectRegular"
          >
            <i class="bi bi-person-video3 me-2"></i>

            <span>
              <strong>Regular</strong>

              <small class="d-block opacity-75">
                Standard lesson
              </small>
            </span>
          </button>
        </div>


        <!-- Trial -->
        <div
          v-if="tutor.trial_lesson_enabled"
          class="col-6"
        >
          <button
            type="button"
            class="btn w-100 text-start"
            :class="
              form.type === 'trial'
                ? 'btn-gp'
                : 'btn-outline-secondary'
            "
            :disabled="loading"
            @click="selectTrial"
          >
            <i class="bi bi-gift me-2"></i>

            <span>
              <strong>Trial</strong>

              <small class="d-block opacity-75">
                30 minutes
              </small>
            </span>
          </button>
        </div>

      </div>
    </div>


    <!-- =========================================================
         DURATION
    ========================================================== -->
    <div class="mb-3">

      <label
        for="booking-duration"
        class="form-label small fw-600"
      >
        Duration
      </label>

      <select
        id="booking-duration"
        v-model="form.duration"
        class="form-select form-select-sm"
        :disabled="loading || form.type === 'trial'"
        @change="clearValidationError"
      >
        <option value="30">
          30 minutes
        </option>

        <option value="60">
          1 hour
        </option>

        <option value="90">
          1.5 hours
        </option>

        <option value="120">
          2 hours
        </option>
      </select>

      <div
        v-if="form.type === 'trial'"
        class="form-text small"
      >
        Trial lessons are fixed at 30 minutes.
      </div>
    </div>


    <!-- =========================================================
         TOPIC
    ========================================================== -->
    <div class="mb-3">

      <label
        for="booking-topic"
        class="form-label small fw-600"
      >
        Topic
      </label>

      <input
        id="booking-topic"
        v-model="form.topic"
        type="text"
        class="form-control form-control-sm"
        placeholder="What would you like to cover?"
        maxlength="300"
        :disabled="loading"
        @input="clearValidationError"
      />

    </div>


    <!-- =========================================================
         RECORD SESSION
    ========================================================== -->
    <div class="border rounded-3 p-3 mb-3">

      <div class="form-check">

        <input
          id="record-session"
          v-model="form.record"
          class="form-check-input"
          type="checkbox"
          :disabled="loading"
        />

        <label
          for="record-session"
          class="form-check-label small"
        >
          <span class="fw-600">
            Record this lesson
          </span>

          <span class="d-block text-muted">
            The recording can be made available after the lesson.
          </span>
        </label>

      </div>

    </div>


    <!-- =========================================================
         BOOK ON BEHALF
    ========================================================== -->
    <div
      v-if="allowOnBehalf"
      class="border rounded-3 p-3 mb-3"
      :class="{
        'border-danger':
          form.booked_on_behalf && onBehalfError
      }"
    >

      <div class="form-check">

        <input
          id="booking-on-behalf"
          v-model="form.booked_on_behalf"
          class="form-check-input"
          type="checkbox"
          :disabled="loading"
          @change="handleOnBehalfChange"
        />

        <label
          for="booking-on-behalf"
          class="form-check-label small fw-600"
        >
          <i class="bi bi-person-plus-fill me-1"></i>
          Book for a student
        </label>

      </div>


      <div
        v-if="!form.booked_on_behalf"
        class="text-muted small mt-2"
      >
        Select this option if you are booking the lesson for another student.
      </div>


      <div
        v-if="form.booked_on_behalf"
        class="mt-3"
      >

        <div class="small fw-600 mb-2 text-gp-primary">
          Student / Booker Information
        </div>


        <!-- Learner email -->
        <div class="mb-2">

          <label
            for="learner-email"
            class="form-label small fw-600"
          >
            Student email *
          </label>

          <input
            id="learner-email"
            v-model.trim="form.learner_email"
            type="email"
            class="form-control form-control-sm"
            placeholder="student@example.com"
            autocomplete="email"
            :disabled="loading"
            @input="clearValidationError"
          />

        </div>


        <!-- Booker name -->
        <div class="mb-2">

          <label
            for="booker-name"
            class="form-label small fw-600"
          >
            Parent/Guardian name *
          </label>

          <input
            id="booker-name"
            v-model.trim="form.booker_name"
            type="text"
            class="form-control form-control-sm"
            placeholder="Full name"
            autocomplete="name"
            :disabled="loading"
            @input="clearValidationError"
          />

        </div>


        <!-- Booker phone -->
        <div class="mb-2">

          <label
            for="booker-phone"
            class="form-label small fw-600"
          >
            Parent/Guardian phone *
          </label>

          <input
            id="booker-phone"
            v-model.trim="form.booker_phone"
            type="tel"
            class="form-control form-control-sm"
            placeholder="e.g. 024 123 4567"
            autocomplete="tel"
            :disabled="loading"
            @input="clearValidationError"
          />

        </div>


        <!-- Relationship -->
        <div class="mb-0">

          <label
            for="booker-relationship"
            class="form-label small fw-600"
          >
            Relationship
          </label>

          <select
            id="booker-relationship"
            v-model="form.booker_relationship"
            class="form-select form-select-sm"
            :disabled="loading"
          >
            <option value="Parent/Guardian">
              Parent / Guardian
            </option>

            <option value="Relative">
              Relative
            </option>

            <option value="Sponsor">
              Sponsor
            </option>

            <option value="Other">
              Other
            </option>
          </select>

        </div>

      </div>

    </div>


    <!-- =========================================================
         PRICE SUMMARY
    ========================================================== -->
    <div
      class="gp-card-flat p-3 mb-3"
      style="background:var(--gp-surface)"
    >

      <div class="d-flex justify-content-between small mb-1">

        <span>
          Lesson ({{ form.duration }} min)
        </span>

        <span>
          GHS {{ lessonCost }}
        </span>

      </div>


      <div class="d-flex justify-content-between small text-muted mb-1">

        <span>
          Platform fee (20%)
        </span>

        <span>
          GHS {{ fee }}
        </span>

      </div>


      <div class="d-flex justify-content-between fw-700 border-top pt-2">

        <span>
          Total
        </span>

        <span class="text-gp-primary">
          GHS {{ total }}
        </span>

      </div>

    </div>


    <!-- =========================================================
         SUBMISSION ERROR
    ========================================================== -->
    <div
      v-if="onBehalfError"
      class="alert alert-warning py-2 small mb-3"
    >
      <i class="bi bi-info-circle-fill me-1"></i>
      {{ onBehalfError }}
    </div>


    <!-- =========================================================
         BOOK BUTTON
    ========================================================== -->
    <button
      type="button"
      class="btn btn-gp w-100 py-2"
      :disabled="disabled"
      @click="submitBooking"
    >

      <span
        v-if="loading"
        class="spinner-border spinner-border-sm me-2"
        role="status"
        aria-hidden="true"
      ></span>

      <i
        v-else
        class="bi bi-calendar-check me-2"
      ></i>

      <span v-if="loading">
        Creating Lesson...
      </span>

      <span v-else>
        {{
          tutor.instant_book
            ? 'Book Instantly'
            : 'Request Lesson'
        }}
      </span>

    </button>


    <!-- Security/help text -->
    <div class="text-center text-muted small mt-2">

      <i class="bi bi-shield-check me-1"></i>

      You will review payment before being charged.

    </div>

  </div>
</template>


<script setup>

import {
  computed,
  reactive,
  ref,
  watch
} from 'vue'


/* ============================================================
   PROPS
============================================================ */

const props = defineProps({

  tutor: {
    type: Object,
    required: true
  },

  loading: {
    type: Boolean,
    default: false
  },

  allowOnBehalf: {
    type: Boolean,
    default: false
  }

})


/* ============================================================
   EVENTS
============================================================ */

const emit = defineEmits([
  'book'
])


/* ============================================================
   FORM
============================================================ */

const form = reactive({

  date: '',

  time: '10:00',

  duration: '60',

  subject: '',

  type: 'regular',

  topic: '',

  record: true,

  booked_on_behalf: false,

  learner_email: '',

  booker_name: '',

  booker_phone: '',

  booker_relationship: 'Parent/Guardian'

})


/* ============================================================
   LOCAL STATE
============================================================ */

const validationError = ref('')

const onBehalfError = ref('')


/* ============================================================
   TODAY
============================================================ */

const today = computed(() => {

  const now = new Date()

  const year = now.getFullYear()

  const month = String(
    now.getMonth() + 1
  ).padStart(2, '0')

  const day = String(
    now.getDate()
  ).padStart(2, '0')

  return `${year}-${month}-${day}`

})


/* ============================================================
   SUBJECTS
============================================================ */

const subjects = computed(() => {

  if (
    !Array.isArray(
      props.tutor?.subjects_list
    )
  ) {
    return []
  }

  return props.tutor.subjects_list

})


/* ============================================================
   INITIAL SUBJECT
============================================================ */

watch(
  () => props.tutor?.subjects_list,

  (newSubjects) => {

    if (
      !form.subject &&
      Array.isArray(newSubjects) &&
      newSubjects.length
    ) {

      form.subject =
        newSubjects[0].id

    }

  },

  {
    immediate: true
  }
)


/* ============================================================
   PRICE
============================================================ */

const lessonCost = computed(() => {

  const duration =
    Number(form.duration) || 0

  const hourlyRate =
    Number(
      props.tutor?.hourly_rate || 0
    )

  let cost = 0

  if (form.type === 'trial') {

    cost =
      Number(
        props.tutor?.trial_lesson_price || 0
      )

  } else {

    cost =
      hourlyRate *
      duration /
      60

  }

  return cost.toFixed(2)

})


const fee = computed(() => {

  const cost =
    Number(lessonCost.value) || 0

  return (
    cost * 0.20
  ).toFixed(2)

})


const total = computed(() => {

  const cost =
    Number(lessonCost.value) || 0

  const platformFee =
    cost * 0.20

  return (
    cost + platformFee
  ).toFixed(2)

})


/* ============================================================
   BUTTON DISABLED STATE
============================================================ */

const tutorAccountId = computed(() => (
  props.tutor?.user_id || props.tutor?.id || null
))

const disabled = computed(() => {

  if (props.loading) {
    return true
  }

  if (!props.tutor?.user_id) {
    return true
  }

  if (!form.date) {
    return true
  }

  if (!form.time) {
    return true
  }

  if (!form.subject) {
    return true
  }

  if (
    form.booked_on_behalf &&
    (
      !form.learner_email ||
      !form.booker_name ||
      !form.booker_phone
    )
  ) {
    return true
  }

  return false

})


/* ============================================================
   FORMAT MONEY
============================================================ */

function formatMoney(value) {

  const amount =
    Number(value)

  if (!Number.isFinite(amount)) {
    return '0.00'
  }

  return amount.toFixed(2)

}


/* ============================================================
   CLEAR ERRORS
============================================================ */

function clearValidationError() {

  validationError.value = ''

  onBehalfError.value = ''

}


/* ============================================================
   LESSON TYPE
============================================================ */

function selectRegular() {

  form.type = 'regular'

  if (form.duration === '30') {
    form.duration = '60'
  }

  clearValidationError()

}


function selectTrial() {

  if (!props.tutor?.trial_lesson_enabled) {
    return
  }

  form.type = 'trial'

  form.duration = '30'

  clearValidationError()

}


/* ============================================================
   BOOK ON BEHALF
============================================================ */

function handleOnBehalfChange() {

  clearValidationError()

  if (!form.booked_on_behalf) {

    form.learner_email = ''

    form.booker_name = ''

    form.booker_phone = ''

    form.booker_relationship =
      'Parent/Guardian'

  }

}


/* ============================================================
   BUILD DATETIME
============================================================ */

/*
 * Converts:
 *
 * 2026-08-13
 * 10:00
 *
 * into:
 *
 * 2026-08-13T10:00:00
 *
 * Django parse_datetime() can understand this.
 */

function buildDateTime(date, time) {

  if (!date || !time) {
    return null
  }

  return `${date}T${time}:00`

}


/* ============================================================
   CALCULATE END TIME
============================================================ */

function buildEndDateTime() {

  if (!form.date || !form.time) {
    return null
  }

  const duration =
    Number(form.duration)

  if (
    !Number.isFinite(duration) ||
    duration <= 0
  ) {
    return null
  }

  const start =
    new Date(
      `${form.date}T${form.time}:00`
    )

  if (Number.isNaN(start.getTime())) {
    return null
  }

  const end =
    new Date(
      start.getTime() +
      duration * 60 * 1000
    )

  /*
   * We deliberately format the datetime
   * without converting it to UTC.
   *
   * This keeps the selected Ghana/local
   * lesson time intact.
   */

  const year =
    end.getFullYear()

  const month =
    String(
      end.getMonth() + 1
    ).padStart(2, '0')

  const day =
    String(
      end.getDate()
    ).padStart(2, '0')

  const hours =
    String(
      end.getHours()
    ).padStart(2, '0')

  const minutes =
    String(
      end.getMinutes()
    ).padStart(2, '0')

  const seconds = '00'

  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`

}


/* ============================================================
   VALIDATION
============================================================ */

function validateBooking() {

  validationError.value = ''

  onBehalfError.value = ''


  /* Tutor */

  if (!tutorAccountId.value) {

    validationError.value =
      'Unable to identify the tutor account. Please refresh the page and try again.'

    return false

  }


  /* Date */

  if (!form.date) {

    validationError.value =
      'Please select a lesson date.'

    return false

  }


  /* Prevent past dates */

  if (form.date < today.value) {

    validationError.value =
      'Please select today or a future date.'

    return false

  }


  /* Time */

  if (!form.time) {

    validationError.value =
      'Please select a lesson time.'

    return false

  }


  /* Subject */

  if (!form.subject) {

    validationError.value =
      'Please select a subject.'

    return false

  }


  /* Duration */

  const duration =
    Number(form.duration)

  if (
    !Number.isFinite(duration) ||
    duration <= 0
  ) {

    validationError.value =
      'Please select a valid lesson duration.'

    return false

  }


  /* Trial */

  if (
    form.type === 'trial' &&
    duration !== 30
  ) {

    validationError.value =
      'Trial lessons must be 30 minutes.'

    return false

  }


  /* Price */

  const price =
    Number(lessonCost.value)

  if (
    !Number.isFinite(price) ||
    price < 0
  ) {

    validationError.value =
      'Unable to calculate the lesson price.'

    return false

  }


  /* Start datetime */

  const startTime =
    buildDateTime(
      form.date,
      form.time
    )

  if (!startTime) {

    validationError.value =
      'Unable to create the lesson start time.'

    return false

  }


  /* End datetime */

  const endTime =
    buildEndDateTime()

  if (!endTime) {

    validationError.value =
      'Unable to calculate the lesson end time.'

    return false

  }


  /* On behalf */

  if (form.booked_on_behalf) {

    if (!form.learner_email) {

      onBehalfError.value =
        'Please enter the student email.'

      return false

    }


    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    if (
      !emailPattern.test(
        form.learner_email
      )
    ) {

      onBehalfError.value =
        'Please enter a valid student email.'

      return false

    }


    if (!form.booker_name) {

      onBehalfError.value =
        'Please enter the parent/guardian name.'

      return false

    }


    if (!form.booker_phone) {

      onBehalfError.value =
        'Please enter the parent/guardian phone number.'

      return false

    }

  }


  return true

}


/* ============================================================
   SUBMIT BOOKING
============================================================ */

function submitBooking() {

  if (props.loading) {
    return
  }


  if (!validateBooking()) {
    return
  }


  /*
   * IMPORTANT:
   *
   * props.tutor.id      = TutorProfile ID
   * props.tutor.user_id = Django User ID
   *
   * Lesson.tutor points to AUTH_USER_MODEL,
   * therefore we MUST send user_id.
   */

  const tutorUserId =
    Number(
      props.tutor.user_id
    )


  if (
    !Number.isInteger(tutorUserId) ||
    tutorUserId <= 0
  ) {

    validationError.value =
      'Invalid tutor account ID. Please refresh the page and try again.'

    return

  }


  const startTime =
    buildDateTime(
      form.date,
      form.time
    )


  const endTime =
    buildEndDateTime()


  /*
   * This payload now matches the Django Lesson
   * creation logic in views.py.
   */

  const bookingData = {

    /* Django User ID */
    tutor:
      tutorUserId,

    /* Subject primary key */
    subject:
      form.subject,

    /* Lesson model field */
    lesson_type:
      form.type,

    /* Django DateTimeField values */
    start_time:
      startTime,

    end_time:
      endTime,

    /* Explicit duration */
    duration_minutes:
      Number(form.duration),

    /* Lesson price */
    price:
      Number(lessonCost.value),

    currency:
      'GHS',

    /* Lesson recording */
    record_session:
      Boolean(form.record),

    /* Optional topic */
    topic:
      form.topic?.trim() || '',

    /* Book on behalf */
    booked_on_behalf:
      Boolean(
        form.booked_on_behalf
      ),

    /*
     * The backend currently uses learner_email
     * to find the actual student.
     */
    learner_email:
      form.booked_on_behalf
        ? form.learner_email.trim().toLowerCase()
        : '',

    booker_name:
      form.booked_on_behalf
        ? form.booker_name.trim()
        : '',

    booker_relationship:
      form.booked_on_behalf
        ? (
            form.booker_relationship ||
            'Parent/Guardian'
          )
        : '',

    booker_phone:
      form.booked_on_behalf
        ? form.booker_phone.trim()
        : '',

    booker_email:
      form.booked_on_behalf
        ? form.booker_email?.trim() || ''
        : '',

    notes:
      ''

  }


  console.log(
    '[BookingWidget] Tutor profile ID:',
    props.tutor.id
  )

  console.log(
    '[BookingWidget] Django user ID:',
    props.tutor.user_id
  )

  console.log(
    '[BookingWidget] Sending booking:',
    bookingData
  )


  // Emit the widget form shape expected by TutorProfileView.
  // The parent owns the API request and builds the final payload.
  emit(
    'book',
    {
      ...form,
      duration: Number(form.duration),
      record: Boolean(form.record)
    }
  )

}

</script>