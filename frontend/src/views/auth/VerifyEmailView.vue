<template>
  <div class="container py-5" style="max-width:560px">
    <div class="gp-card p-5 text-center">
      <i class="bi" :class="loading ? 'bi-envelope-paper text-primary' : verified ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'" style="font-size:3rem"></i>
      <h2 class="fw-800 mt-3">{{ loading ? 'Verifying your email…' : verified ? 'Email verified' : 'Verification failed' }}</h2>
      <p class="text-muted">{{ message }}</p>
      <RouterLink v-if="verified" to="/dashboard" class="btn btn-gp">Continue to Gooprep</RouterLink>
      <RouterLink v-else to="/login" class="btn btn-outline-secondary">Go to login</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiGet } from '@/utils/api'

const route = useRoute()
const loading = ref(true)
const verified = ref(false)
const message = ref('')

onMounted(async () => {
  try {
    const { data } = await apiGet('/auth/verify-email/', { token: route.query.token })
    verified.value = Boolean(data.verified)
    message.value = data.detail || 'Your email address is now verified.'
  } catch (error) {
    message.value = error.response?.data?.error || 'This verification link is invalid or expired.'
  } finally {
    loading.value = false
  }
})
</script>
