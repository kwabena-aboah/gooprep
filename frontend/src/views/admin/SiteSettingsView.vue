<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Site Settings</h2><p class="text-muted small mb-0">Platform-wide configuration</p></div>
      <button class="btn btn-gp btn-sm" @click="save" :disabled="saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
        <i v-else class="bi bi-save me-1"></i>Save All Settings
      </button>
    </div>

    <GpSpinner v-if="loading" />
    <div v-else class="row g-4">
      <!-- General -->
      <div class="col-lg-8">
        <div class="gp-card p-4 mb-4">
          <h5 class="fw-700 mb-4"><i class="bi bi-gear me-2 text-gp-primary"></i>General</h5>
          <div class="row g-3">
            <div class="col-md-6"><label class="form-label small fw-600">Site Name</label><input class="form-control" v-model="s.site_name" /></div>
            <div class="col-md-6"><label class="form-label small fw-600">Support Email</label><input class="form-control" v-model="s.support_email" /></div>
            <div class="col-md-6"><label class="form-label small fw-600">Platform Currency</label>
              <select class="form-select" v-model="s.currency"><option value="GHS">GHS (Ghana Cedi)</option><option value="USD">USD</option><option value="NGN">NGN</option></select>
            </div>
            <div class="col-md-6"><label class="form-label small fw-600">Default Timezone</label>
              <select class="form-select" v-model="s.timezone"><option value="Africa/Accra">Africa/Accra</option><option value="Africa/Lagos">Africa/Lagos</option></select>
            </div>
            <div class="col-12"><label class="form-label small fw-600">Tagline</label><input class="form-control" v-model="s.tagline" /></div>
          </div>
        </div>

        <div class="gp-card p-4 mb-4">
          <h5 class="fw-700 mb-4"><i class="bi bi-percent me-2 text-gp-primary"></i>Financial Settings</h5>
          <div class="row g-3">
            <div class="col-md-6"><label class="form-label small fw-600">Platform Commission (%)</label><input type="number" class="form-control" v-model="s.commission_rate" min="0" max="50" /><div class="form-text">Currently {{ s.commission_rate }}% (tutors keep {{ 100-s.commission_rate }}%)</div></div>
            <div class="col-md-6"><label class="form-label small fw-600">Min Payout (GHS)</label><input type="number" class="form-control" v-model="s.min_payout" min="0" /></div>
            <div class="col-md-6"><label class="form-label small fw-600">Escrow Release (hours)</label><input type="number" class="form-control" v-model="s.escrow_release_hours" min="1" /></div>
            <div class="col-md-6"><label class="form-label small fw-600">Cancellation Window (hours)</label><input type="number" class="form-control" v-model="s.cancellation_hours" min="0" /></div>
          </div>
        </div>

        <div class="gp-card p-4 mb-4">
          <h5 class="fw-700 mb-4"><i class="bi bi-camera-video me-2 text-gp-primary"></i>BigBlueButton</h5>
          <div class="row g-3">
            <div class="col-12"><label class="form-label small fw-600">BBB Server URL</label><input class="form-control" v-model="s.bbb_url" /></div>
            <div class="col-12"><label class="form-label small fw-600">BBB Key</label>
              <div class="input-group"><input :type="showSecret?'text':'password'" class="form-control" v-model="s.bbb_key" /><button class="btn btn-outline-secondary" @click="showSecret=!showSecret"><i class="bi" :class="showSecret?'bi-eye-slash':'bi-eye'"></i></button></div>
            </div>
            <div class="col-12 d-flex gap-2">
              <button class="btn btn-outline-primary btn-sm" @click="testBBB" :disabled="testingBBB">
                <span v-if="testingBBB" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-wifi me-1"></i>Test Connection
              </button>
              <span v-if="bbbResult" class="badge align-self-center" :class="bbbResult.ok?'bg-success':'bg-danger'">{{ bbbResult.msg }}</span>
            </div>
          </div>
        </div>

        <div class="gp-card p-4">
          <h5 class="fw-700 mb-4"><i class="bi bi-toggles me-2 text-gp-primary"></i>Feature Flags</h5>
          <div class="row g-3">
            <div v-for="f in flags" :key="f.key" class="col-md-6">
              <div class="form-check form-switch p-3 border rounded-3" :class="s[f.key]?'border-primary bg-primary-subtle':''">
                <input class="form-check-input" type="checkbox" :id="f.key" v-model="s[f.key]" />
                <label class="form-check-label small fw-600" :for="f.key">
                  <i :class="f.icon" class="me-1 text-gp-primary"></i>{{ f.label }}
                </label>
                <div class="text-muted" style="font-size:.7rem">{{ f.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar stats -->
      <div class="col-lg-4">
        <div class="gp-card p-4 sticky-top" style="top:80px">
          <h5 class="fw-700 mb-3"><i class="bi bi-activity me-2 text-gp-primary"></i>System Health</h5>
          <div v-for="h in health" :key="h.label" class="d-flex align-items-center gap-2 mb-2 p-2 rounded-3 border">
            <div class="rounded-circle flex-shrink-0" :style="`width:10px;height:10px;background:${h.ok?'var(--gp-success)':'var(--gp-danger)'}`"></div>
            <span class="small flex-grow-1">{{ h.label }}</span>
            <span class="text-muted small">{{ h.value }}</span>
          </div>
          <hr />
          <div class="small text-muted text-center">Last check: {{ lastCheck }}</div>
          <button class="btn btn-outline-secondary btn-sm w-100 mt-2" @click="checkHealth">
            <i class="bi bi-arrow-repeat me-1"></i>Recheck
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { useNotifStore } from '@/stores/notifs'
import GpSpinner from '@/components/common/GpSpinner.vue'

const notifStore = useNotifStore()
const loading    = ref(true)
const saving     = ref(false)
const showSecret = ref(false)
const testingBBB = ref(false)
const bbbResult  = ref(null)
const lastCheck  = ref('—')

const s = ref({
  site_name:'Gooprep', support_email:'support@gooprep.com', currency:'GHS',
  timezone:'Africa/Accra', tagline:'Learn Without Limits', commission_rate:15,
  min_payout:50, escrow_release_hours:24, cancellation_hours:24,
  bbb_url:'', bbb_secret:'',
  ai_enabled:true, whatsapp_enabled:true, group_classes_enabled:true,
  institutions_enabled:true, trials_enabled:true, gamification_enabled:true,
})

const flags = [
  { key:'ai_enabled',            label:'AI Assistant',      icon:'bi bi-robot',         desc:'AI study help & lesson summaries' },
  { key:'whatsapp_enabled',      label:'WhatsApp Notify',   icon:'bi bi-whatsapp',       desc:'Notifications via WhatsApp' },
  { key:'group_classes_enabled', label:'Group Classes',     icon:'bi bi-people',         desc:'Enable group lesson enrollment' },
  { key:'institutions_enabled',  label:'Institutions',      icon:'bi bi-building',       desc:'Allow institution accounts' },
  { key:'trials_enabled',        label:'Trial Lessons',     icon:'bi bi-gift',           desc:'Allow tutors to offer trials' },
  { key:'gamification_enabled',  label:'Gamification',      icon:'bi bi-trophy',         desc:'XP, badges, and leaderboard' },
]

const health = ref([
  { label:'Database',  ok:true,  value:'OK' },
  { label:'Redis',     ok:true,  value:'OK' },
  { label:'Celery',    ok:true,  value:'Running' },
  { label:'BBB',       ok:false, value:'Unchecked' },
  { label:'Storage',   ok:true,  value:'OK' },
  { label:'Email',     ok:true,  value:'OK' },
])

async function save() {
  saving.value = true
  try {
    await apiPost('/settings/', s.value)
    notifStore.toast('Settings saved!', 'success')
  } catch(e) { notifStore.toast(Object.values(e.response?.data||{}).flat().join(' ')||'Failed.', 'error') }
  finally { saving.value = false }
}

async function testBBB() {
  testingBBB.value = true; bbbResult.value = null
  try {
    const { data } = await apiPost('/settings/bbb/test/', { url: s.value.bbb_url, secret: s.value.bbb_key })
    bbbResult.value = { ok: data.success, msg: data.success ? 'Connected ✓' : data.message || data.error || 'Failed' }
    health.value.find(h=>h.label==='BBB').ok = data.success
    health.value.find(h=>h.label==='BBB').value = data.success ? 'Online' : 'Offline'
  } catch { bbbResult.value = { ok: false, msg: 'Connection failed' } }
  finally { testingBBB.value = false }
}

async function checkHealth() {
  try {
    const { data } = await apiGet('/settings/health/')
    health.value = data.checks || health.value
    lastCheck.value = new Date().toLocaleTimeString()
  } catch {}
}

onMounted(async () => {
  try {
    const { data } = await apiGet('/settings/')
    Object.assign(s.value, data)
    await checkHealth()
  } catch {} finally { loading.value = false }
})
</script>
