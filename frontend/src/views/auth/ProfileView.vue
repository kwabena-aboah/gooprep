<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-800 mb-0">My Profile</h2>
        <p class="text-muted small mb-0">Manage your personal information and preferences</p>
      </div>
      <button class="btn btn-gp btn-sm" @click="save" :disabled="saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
        <i v-else class="bi bi-save me-1"></i>Save Changes
      </button>
    </div>

    <GpSpinner v-if="loading" />
    <div v-else class="row g-4">
      <!-- Left: Avatar -->
      <div class="col-lg-3">
        <div class="gp-card p-4 text-center mb-3">
          <div class="position-relative d-inline-block mb-3">
            <img :src="avatarPreview || form.avatar_url || fallback"
                 class="rounded-circle" width="96" height="96"
                 style="object-fit:cover;border:4px solid var(--gp-red)" />
            <label class="position-absolute bottom-0 end-0 rounded-circle d-flex align-items-center justify-content-center"
                   style="width:28px;height:28px;background:var(--gp-red);cursor:pointer">
              <i class="bi bi-camera-fill text-white" style="font-size:.7rem"></i>
              <input type="file" accept="image/*" class="d-none" @change="previewAvatar" />
            </label>
          </div>
          <h5 class="fw-700 mb-0">{{ form.first_name }} {{ form.last_name }}</h5>
          <div class="text-muted small text-capitalize">{{ form.role }}</div>
          <span class="gp-badge mt-2 d-inline-block">{{ (form.subscription_plan || 'Free').toUpperCase() }}</span>
          <hr />
          <div class="row g-2 text-center">
            <div class="col-4"><div class="fw-700 text-gp-primary">{{ form.total_points || 0 }}</div><div class="text-muted" style="font-size:.7rem">Points</div></div>
            <div class="col-4"><div class="fw-700 text-warning">{{ form.level || 1 }}</div><div class="text-muted" style="font-size:.7rem">Level</div></div>
            <div class="col-4"><div class="fw-700 text-danger">{{ form.streak_days || 0 }}</div><div class="text-muted" style="font-size:.7rem">Streak</div></div>
          </div>
        </div>
      </div>

      <!-- Right: Tabs -->
      <div class="col-lg-9">
        <div class="gp-card">
          <ul class="nav nav-tabs px-4 pt-3">
            <li v-for="t in tabs" :key="t.key" class="nav-item">
              <button class="nav-link small fw-600" :class="{ active: tab === t.key }" @click="tab = t.key">
                <i :class="t.icon" class="me-1"></i>{{ t.label }}
              </button>
            </li>
          </ul>
          <div class="p-4">
            <!-- Personal -->
            <div v-if="tab === 'personal'" class="row g-3">
              <div class="col-md-6"><label class="form-label small fw-600">First Name</label><input class="form-control" v-model="form.first_name" /></div>
              <div class="col-md-6"><label class="form-label small fw-600">Last Name</label><input class="form-control" v-model="form.last_name" /></div>
              <div class="col-12"><label class="form-label small fw-600">Email</label><input class="form-control" :value="form.email" disabled /><div class="form-text">Contact support to change your email.</div></div>
              <div class="col-md-6"><label class="form-label small fw-600">Phone</label><input class="form-control" v-model="form.phone" placeholder="+233 24 000 0000" /></div>
              <div class="col-md-6"><label class="form-label small fw-600">Date of Birth</label><input type="date" class="form-control" v-model="form.date_of_birth" /></div>
              <div class="col-md-6"><label class="form-label small fw-600">City</label><input class="form-control" v-model="form.city" placeholder="Accra" /></div>
              <div class="col-md-6"><label class="form-label small fw-600">Country</label>
                <select class="form-select" v-model="form.country"><option value="Ghana">Ghana</option><option value="Nigeria">Nigeria</option><option value="Kenya">Kenya</option><option value="Other">Other</option></select>
              </div>
              <div class="col-12"><label class="form-label small fw-600">Bio</label><textarea class="form-control" rows="4" v-model="form.bio" placeholder="Tell us about yourself…"></textarea></div>
            </div>

            <!-- Preferences -->
            <div v-if="tab === 'prefs'" class="row g-3">
              <div class="col-md-6"><label class="form-label small fw-600">Timezone</label>
                <select class="form-select" v-model="form.timezone">
                  <option v-for="tz in timezones" :key="tz" :value="tz">{{ tz }}</option>
                </select>
              </div>
              <div class="col-md-6"><label class="form-label small fw-600">Language</label>
                <select class="form-select" v-model="form.language"><option value="en">English</option><option value="fr">French</option></select>
              </div>
              <div class="col-12"><h6 class="fw-700 mb-3 mt-2">Notification Preferences</h6></div>
              <div v-for="n in notifOpts" :key="n.key" class="col-md-6">
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" :id="n.key" v-model="form[n.key]" />
                  <label class="form-check-label small" :for="n.key"><i :class="n.icon" class="me-1 text-gp-primary"></i>{{ n.label }}</label>
                </div>
              </div>
            </div>

            <!-- Security -->
            <div v-if="tab === 'security'" style="max-width:480px">
              <h6 class="fw-700 mb-3">Change Password</h6>
              <div class="mb-3"><label class="form-label small fw-600">Current Password</label><input type="password" class="form-control" v-model="pw.current" /></div>
              <div class="mb-3"><label class="form-label small fw-600">New Password</label><input type="password" class="form-control" v-model="pw.new1" /></div>
              <div class="mb-3"><label class="form-label small fw-600">Confirm New Password</label><input type="password" class="form-control" v-model="pw.new2" /></div>
              <button class="btn btn-gp btn-sm" @click="changePassword" :disabled="pwLoading">
                <span v-if="pwLoading" class="spinner-border spinner-border-sm me-1"></span>Update Password
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiPost, apiUpload } from '@/utils/api'
import GpSpinner from '@/components/common/GpSpinner.vue'

const auth        = useAuthStore()
const notifStore  = useNotifStore()
const loading     = ref(true)
const saving      = ref(false)
const tab         = ref('personal')
const form        = ref({})
const avatarPreview = ref('')
const pw          = ref({ current: '', new1: '', new2: '' })
const pwLoading   = ref(false)

const tabs = [
  { key: 'personal', label: 'Personal Info',  icon: 'bi bi-person' },
  { key: 'prefs',    label: 'Preferences',    icon: 'bi bi-sliders' },
  { key: 'security', label: 'Security',       icon: 'bi bi-shield-lock' },
]
const notifOpts = [
  { key: 'notify_email',    label: 'Email',    icon: 'bi bi-envelope' },
  { key: 'notify_sms',      label: 'SMS',      icon: 'bi bi-phone' },
  { key: 'notify_push',     label: 'Push',     icon: 'bi bi-bell' },
  { key: 'notify_whatsapp', label: 'WhatsApp', icon: 'bi bi-whatsapp' },
]
const timezones = ['Africa/Accra','Africa/Lagos','Africa/Nairobi','Europe/London','America/New_York']
const fallback  = computed(() =>
  `https://ui-avatars.com/api/?name=${encodeURIComponent(form.value.first_name || 'U')}&background=e63900&color=fff`)

onMounted(async () => {
  form.value = await auth.fetchMe() || {}
  loading.value = false
})

function previewAvatar(e) {
  const file = e.target.files[0]

  if (!file) return

  if (!file.type.startsWith('image/')) {
    notifStore.toast('Only image files are allowed.', 'error')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    notifStore.toast('Image must be less than 5MB.', 'error')
    return
  }

  avatarPreview.value = URL.createObjectURL(file)
  form.value._avatarFile = file
}

async function save() {
  saving.value = true
  try {
    if (form.value._avatarFile) {
      const fd = new FormData(); fd.append('avatar', form.value._avatarFile)
      await apiUpload('/auth/users/me/', fd)
    }
    const allowed = ['first_name','last_name','phone','bio','timezone','language','country','city','date_of_birth','notify_email','notify_sms','notify_push','notify_whatsapp']
    const payload = Object.fromEntries(allowed.map(k => [k, form.value[k]]))
    await auth.updateProfile(payload)
    notifStore.toast('Profile saved!', 'success')
  } catch { notifStore.toast('Failed to save.', 'error') }
  finally { saving.value = false }
}

async function changePassword() {
  if (pw.value.new1.length < 8) {
    notifStore.toast('Password must be at least 8 characters.', 'error')
    return
  }
  try {
    await apiPost('/auth/password/change/', { old_password: pw.value.current, new_password1: pw.value.new1, new_password2: pw.value.new2 })
    notifStore.toast('Password changed!', 'success')
    pw.value = { current: '', new1: '', new2: '' }
  } catch (e) {
    notifStore.toast(Object.values(e.response?.data || {}).flat().join(' ') || 'Failed.', 'error')
  } finally { pwLoading.value = false }
}
</script>
