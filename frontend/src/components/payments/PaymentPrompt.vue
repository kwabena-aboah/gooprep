<template>
  <div class="payment-backdrop" role="presentation" @click.self="$emit('cancel')">
    <section class="payment-dialog gp-card" role="dialog" aria-modal="true" aria-labelledby="payment-title">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div>
          <div class="text-gp-primary mb-2"><i class="bi bi-shield-check fs-3"></i></div>
          <h4 id="payment-title" class="fw-800 mb-1">Complete your booking</h4>
          <p class="text-muted small mb-0">Pay securely to confirm your lesson with {{ tutorName }}.</p>
        </div>
        <button type="button" class="btn-close" aria-label="Close" @click="$emit('cancel')"></button>
      </div>

      <div class="payment-summary rounded-3 p-3 mb-3">
        <div class="d-flex justify-content-between small mb-1">
          <span>Lesson</span><strong>{{ lessonLabel }}</strong>
        </div>
        <div class="d-flex justify-content-between small mb-1">
          <span>Schedule</span><strong>{{ scheduleLabel }}</strong>
        </div>
        <div class="d-flex justify-content-between border-top pt-2 mt-2">
          <span class="fw-700">Total</span><strong class="text-gp-primary">GHS {{ amount }}</strong>
        </div>
      </div>

      <div v-if="errorMessage" class="alert alert-danger small mb-3" role="alert">
        <i class="bi bi-exclamation-triangle me-1"></i>{{ errorMessage }}
      </div>
      <div v-else class="alert alert-info small mb-3">
        <i class="bi bi-info-circle me-1"></i>
        You’ll be redirected to Paystack to complete payment by card or mobile money.
      </div>

      <div class="d-flex gap-2">
        <button type="button" class="btn btn-outline-secondary flex-grow-1" @click="$emit('cancel')" :disabled="loading">Pay later</button>
        <button type="button" class="btn btn-gp flex-grow-1" @click="startPayment" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-lock-fill me-1"></i>{{ loading ? 'Starting payment…' : `Pay GHS ${amount}` }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { apiPost } from '@/utils/api'

const props = defineProps({
  lesson: { type: Object, required: true },
  tutorName: { type: String, default: 'your tutor' },
})
defineEmits(['cancel'])

const loading = ref(false)
const errorMessage = ref('')
const amount = computed(() => Number(props.lesson.price || 0).toFixed(2))
const lessonLabel = computed(() => props.lesson.subject_name || 'Tutoring lesson')
const scheduleLabel = computed(() => {
  if (!props.lesson.start_time) return 'Selected schedule'
  return new Date(props.lesson.start_time).toLocaleString('en-GB', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
})

async function startPayment() {
  if (!props.lesson.id) {
    errorMessage.value = 'The lesson was created without an ID. Please try booking again.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await apiPost('/payments/initiate/', {
      lesson_id: props.lesson.id,
      payment_method: 'card',
    })

    if (!data.authorization_url) {
      throw new Error(data.error || 'Paystack did not return a payment link.')
    }

    window.location.assign(data.authorization_url)
  } catch (error) {
    const responseError = error.response?.data?.error
    errorMessage.value = responseError || error.message || 'Payment could not be started. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.payment-backdrop { position: fixed; inset: 0; z-index: 1050; display: grid; place-items: center; padding: 1rem; background: rgba(15, 23, 42, .55); }
.payment-dialog { width: min(100%, 460px); padding: 1.5rem; box-shadow: 0 1rem 3rem rgba(0, 0, 0, .2); }
.payment-summary { background: var(--gp-surface); }
</style>
