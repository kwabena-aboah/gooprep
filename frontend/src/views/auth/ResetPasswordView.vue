<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5"
       style="background:linear-gradient(135deg,#111 0%,#1a0800 50%,#111 100%)">
    <div style="width:100%;max-width:420px;padding:1rem">
      <div class="text-center mb-4">
        <RouterLink to="/"><img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:52px" /></RouterLink>
      </div>
      <div class="gp-card p-4 p-md-5">
        <template v-if="step === 1">
          <h5 class="fw-700 mb-3">Set New Password</h5>
          <div v-if="error" class="alert alert-danger small py-2">{{ error }}</div>
          <div class="mb-3">
            <label class="form-label small fw-600">New Password</label>
            <div class="input-group">
              <input :type="showPw ? 'text' : 'password'" class="form-control"
                     v-model="pw" placeholder="Min 8 characters" />
              <button class="btn btn-outline-secondary" @click="showPw = !showPw">
                <i class="bi" :class="showPw ? 'bi-eye-slash' : 'bi-eye'"></i>
              </button>
            </div>
            <div class="d-flex gap-1 mt-2" v-if="pw">
              <div v-for="n in 4" :key="n" class="flex-grow-1 rounded" style="height:4px;transition:background .3s"
                   :style="{ background: n <= strength ? color : '#e2e8f0' }"></div>
            </div>
          </div>
          <div class="mb-4">
            <label class="form-label small fw-600">Confirm Password</label>
            <input :type="showPw ? 'text' : 'password'" class="form-control"
                   v-model="pw2"
                   :class="{ 'is-invalid': pw2 && pw !== pw2 }"
                   placeholder="Repeat password" />
            <div class="invalid-feedback">Passwords do not match.</div>
          </div>
          <button class="btn btn-gp w-100 py-2" @click="submit"
                  :disabled="loading || !pw || pw !== pw2">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-shield-lock me-2"></i>Update Password
          </button>
        </template>

        <template v-else>
          <div class="text-center py-3">
            <div class="rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center"
                 style="width:72px;height:72px;background:#dcfce7">
              <i class="bi bi-check-circle-fill text-success fs-2"></i>
            </div>
            <h5 class="fw-700 mb-2">Password Updated!</h5>
            <p class="text-muted small mb-3">Your password has been reset successfully.</p>
            <RouterLink to="/login" class="btn btn-gp">Sign In Now</RouterLink>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { apiPost } from '@/utils/api'

const route  = useRoute()
const pw     = ref('')
const pw2    = ref('')
const showPw = ref(false)
const step   = ref(1)
const loading = ref(false)
const error  = ref('')

const strength = computed(() => {
  const p = pw.value; if (!p) return 0
  let s = 0
  if (p.length >= 8) s++; if (/[A-Z]/.test(p)) s++
  if (/[0-9]/.test(p)) s++; if (/[^A-Za-z0-9]/.test(p)) s++
  return Math.max(1, s)
})
const colors = ['#ef4444','#f59e0b','#3b82f6','#10b981']
const color  = computed(() => colors[strength.value - 1])

async function submit() {
  loading.value = true; error.value = ''
  try {
    await apiPost('/auth/password/reset/confirm/', {
      uid: route.query.uid, token: route.query.token,
      new_password1: pw.value, new_password2: pw2.value,
    })
    step.value = 2
  } catch (e) {
    error.value = Object.values(e.response?.data || {}).flat().join(' ') || 'Invalid or expired link.'
  } finally { loading.value = false }
}
</script>
