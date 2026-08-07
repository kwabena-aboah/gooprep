<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5"
       style="background:linear-gradient(135deg,#111 0%,#1a0800 50%,#111 100%)">
    <div style="width:100%;max-width:420px;padding:1rem">
      <div class="text-center mb-4">
        <RouterLink to="/"><img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:52px" /></RouterLink>
        <h4 class="text-white fw-700 mt-3 mb-1">Reset Your Password</h4>
        <p class="text-white-50 small">Enter your email and we'll send a reset link.</p>
      </div>

      <div class="gp-card p-4 p-md-5">
        <!-- Step 1: Request -->
        <template v-if="step === 1">
          <div v-if="error" class="alert alert-danger small py-2">{{ error }}</div>
          <div class="mb-3">
            <label class="form-label small fw-600">Email address</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-envelope text-muted"></i></span>
              <input type="email" class="form-control" v-model="email"
                     placeholder="you@example.com" @keyup.enter="requestReset" autofocus />
            </div>
          </div>
          <button class="btn btn-gp w-100 py-2 mb-3" @click="requestReset" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-send me-2"></i>Send Reset Link
          </button>
          <p class="text-center small text-muted mb-0">
            <RouterLink to="/login" class="text-gp-primary">← Back to Sign In</RouterLink>
          </p>
        </template>

        <!-- Step 2: Email sent -->
        <template v-else-if="step === 2">
          <div class="text-center py-3">
            <div class="rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center"
                 style="width:72px;height:72px;background:linear-gradient(135deg,var(--gp-red),var(--gp-amber))">
              <i class="bi bi-envelope-check-fill text-white fs-2"></i>
            </div>
            <h5 class="fw-700 mb-2">Check your inbox!</h5>
            <p class="text-muted small mb-3">
              We've sent a reset link to <strong>{{ email }}</strong>. Expires in 24 hours.
            </p>
            <p class="text-muted small">
              Didn't receive it?
              <button class="btn btn-link btn-sm p-0 text-gp-primary" @click="step = 1">Try again</button>
            </p>
            <RouterLink to="/login" class="btn btn-gp btn-sm mt-2">← Back to Sign In</RouterLink>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { apiPost } from '@/utils/api'

const email   = ref('')
const step    = ref(1)
const loading = ref(false)
const error   = ref('')

async function requestReset() {
  if (!email.value) { error.value = 'Please enter your email.'; return }
  loading.value = true; error.value = ''
  try {
    await apiPost('/auth/password/reset/', { email: email.value })
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.email?.[0] || e.response?.data?.detail || 'Failed to send reset email.'
  } finally { loading.value = false }
}
</script>
