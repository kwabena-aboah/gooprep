<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5"
       style="background:linear-gradient(135deg,#111 0%,#1a0800 50%,#111 100%)">
    <div style="width:100%;max-width:440px;padding:1rem">
      <div class="text-center mb-4">
        <RouterLink to="/"><img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:60px" /></RouterLink>
        <p class="text-white-50 mt-2">Welcome back! Sign in to continue.</p>
      </div>
      <div class="gp-card p-4 p-md-5">
        <div v-if="auth.error" class="alert alert-danger small py-2 d-flex align-items-center gap-2">
          <i class="bi bi-exclamation-circle-fill"></i>{{ auth.error }}
        </div>
        <div class="d-grid mb-4">
          <a href="/api/auth/google/" class="btn btn-outline-secondary d-flex align-items-center justify-content-center gap-2">
            <strong>G</strong> Continue with Google
          </a>
        </div>
        <div class="d-flex align-items-center gap-2 mb-4">
          <hr class="flex-grow-1"><span class="text-muted small">or email</span><hr class="flex-grow-1">
        </div>
        <div class="mb-3">
          <label class="form-label small fw-600">Email address</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-envelope text-muted"></i></span>
            <input type="email" class="form-control" v-model="email"
                   placeholder="you@example.com" @keyup.enter="submit" autofocus />
          </div>
        </div>
        <div class="mb-1">
          <label class="form-label small fw-600">Password</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-lock text-muted"></i></span>
            <input :type="showPw ? 'text' : 'password'" class="form-control"
                   v-model="password" placeholder="••••••••" @keyup.enter="submit" />
            <button class="btn btn-outline-secondary" type="button" @click="showPw = !showPw">
              <i class="bi" :class="showPw ? 'bi-eye-slash' : 'bi-eye'"></i>
            </button>
          </div>
        </div>
        <div class="text-end mb-4">
          <RouterLink to="/forgot-password" class="small text-gp-primary">Forgot password?</RouterLink>
        </div>
        <button class="btn btn-gp w-100 py-2 mb-3" @click="submit" :disabled="auth.loading">
          <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-box-arrow-in-right me-2"></i>Sign In
        </button>
        <p class="text-center small text-muted mb-0">
          No account? <RouterLink to="/register" class="text-gp-primary fw-600">Sign up free</RouterLink>
        </p>
      </div>
      <div class="d-flex justify-content-center gap-4 mt-4 flex-wrap">
        <span class="text-white-50 small"><i class="bi bi-shield-lock me-1 text-success"></i>SSL secured</span>
        <span class="text-white-50 small"><i class="bi bi-people me-1 text-primary"></i>50K+ learners</span>
        <span class="text-white-50 small"><i class="bi bi-star-fill me-1 text-warning"></i>4.9 rated</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const email = ref('')
const password = ref('')
const showPw = ref(false)
async function submit() {
  const { ok } = await auth.login(email.value, password.value)
  if (ok) router.push(route.query.next || '/dashboard')
}
</script>
