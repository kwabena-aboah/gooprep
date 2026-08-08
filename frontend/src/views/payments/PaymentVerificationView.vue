<template>
  <div class="container py-5 text-center" style="max-width:560px">
    <div class="gp-card p-5">
      <div v-if="loading">
        <span class="spinner-border text-primary mb-3"></span>
        <h4>Verifying payment…</h4>
        <p class="text-muted">Please wait while we confirm your Paystack payment.</p>
      </div>
      <div v-else>
        <i class="bi fs-1 mb-3" :class="success ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'"></i>
        <h4>{{ success ? 'Payment successful' : 'Payment could not be verified' }}</h4>
        <p class="text-muted">{{ message }}</p>
        <RouterLink class="btn btn-gp" to="/lessons">View my lessons</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiGet } from '@/utils/api'

const route = useRoute()
const loading = ref(true)
const success = ref(false)
const message = ref('')

onMounted(async () => {
  const reference = route.query.reference
  if (!reference) {
    message.value = 'No payment reference was provided.'
    loading.value = false
    return
  }
  try {
    const { data } = await apiGet('/payments/verify/', { reference })
    success.value = data.paid === true
    message.value = data.message || (success.value ? 'Your payment has been confirmed.' : 'Payment was not completed.')
  } catch (error) {
    message.value = error.response?.data?.error || 'Payment verification failed.'
  } finally {
    loading.value = false
  }
})
</script>
