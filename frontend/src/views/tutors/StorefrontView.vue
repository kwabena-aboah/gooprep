<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">My Storefront</h2><p class="text-muted small mb-0">Customise your public tutor profile</p></div>
      <div class="d-flex gap-2">
        <span v-if="!profile.slug" class="text-muted small align-self-center">Save to create your preview link</span>
        <a v-if="profile.slug" :href="`/tutor/${profile.slug}`" target="_blank" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-eye me-1"></i>Preview
        </a>
        <button class="btn btn-gp btn-sm" @click="save" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-save me-1"></i>Save
        </button>
      </div>
    </div>

    <GpSpinner v-if="loading" />
    <div v-else class="row g-4">
      <div class="col-lg-8">
        <!-- Profile card -->
        <div class="gp-card p-4 mb-4">
          <h5 class="fw-700 mb-4"><i class="bi bi-person-badge me-2 text-gp-primary"></i>Profile Information</h5>
          <div class="mb-3"><label class="form-label small fw-600">Headline *</label><input class="form-control" v-model="form.headline" /></div>
          <div class="row g-3 mb-3">
            <div class="col-md-6"><label class="form-label small fw-600">Hourly Rate (GHS)</label><div class="input-group"><span class="input-group-text">GHS</span><input type="number" class="form-control" v-model="form.hourly_rate" min="20" /></div></div>
            <div class="col-md-6"><label class="form-label small fw-600">Response Time (min)</label><input type="number" class="form-control" v-model="form.response_time" min="5" /></div>
            <div class="col-md-6"><label class="form-label small fw-600">Teaching Style</label>
              <select class="form-select" v-model="form.teaching_style">
                <option v-for="s in styles" :key="s" :value="s">{{ s.charAt(0).toUpperCase()+s.slice(1) }}</option>
              </select>
            </div>
            <div class="col-md-6"><label class="form-label small fw-600">Teaching Language</label><input class="form-control" v-model="form.language" placeholder="English, Twi…" /></div>
          </div>
          <div class="mb-3"><label class="form-label small fw-600">Bio</label><textarea class="form-control" rows="6" v-model="form.bio"></textarea><div class="d-flex justify-content-between"><div class="form-text">Min 100 chars</div><div class="text-muted small">{{ form.bio.length }}/1500</div></div></div>
          <div class="mb-3"><label class="form-label small fw-600">Intro Video URL</label><input class="form-control" v-model="form.intro_video_url" placeholder="https://youtube.com/…" /></div>
        </div>

        <!-- Offers -->
        <div class="gp-card p-4 mb-4">
          <h5 class="fw-700 mb-3"><i class="bi bi-gift me-2 text-gp-primary"></i>Special Offers</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <div class="form-check form-switch mb-2"><input class="form-check-input" type="checkbox" v-model="form.trial_lesson_enabled" /><label class="form-check-label small fw-600">Trial lesson</label></div>
              <input v-if="form.trial_lesson_enabled" type="number" class="form-control form-control-sm" v-model="form.trial_lesson_price" placeholder="Price (GHS)" />
            </div>
            <div class="col-md-6">
              <div class="form-check form-switch mb-2"><input class="form-check-input" type="checkbox" v-model="form.instant_book" /><label class="form-check-label small fw-600">Instant Book</label></div>
              <div class="form-check form-switch"><input class="form-check-input" type="checkbox" v-model="form.record_by_default" /><label class="form-check-label small fw-600">Record lessons by default</label></div>
            </div>
          </div>
        </div>

        <!-- Packages -->
        <div class="gp-card p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-700 mb-0"><i class="bi bi-box me-2 text-gp-primary"></i>Lesson Packages</h5>
            <button class="btn btn-sm btn-gp-outline" @click="addPkg"><i class="bi bi-plus me-1"></i>Add Package</button>
          </div>
          <div v-for="(p,i) in form.packages" :key="i" class="gp-card-flat p-3 mb-2">
            <div class="row g-2">
              <div class="col-md-4"><input class="form-control form-control-sm" v-model="p.name" placeholder="Package name" /></div>
              <div class="col-md-2"><input type="number" class="form-control form-control-sm" v-model="p.lessons" placeholder="# lessons" /></div>
              <div class="col-md-3"><input type="number" class="form-control form-control-sm" v-model="p.price" placeholder="GHS" /></div>
              <div class="col-md-2"><input class="form-control form-control-sm" v-model="p.validity" placeholder="30 days" /></div>
              <div class="col-md-1 d-flex align-items-center"><button class="btn btn-sm btn-outline-danger" @click="form.packages.splice(i,1)"><i class="bi bi-x"></i></button></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Preview sidebar -->
      <div class="col-lg-4">
        <div class="gp-card p-4 sticky-top" style="top:80px">
          <div class="text-center mb-3">
            <div class="position-relative d-inline-block">
              <img :src="auth.user?.avatar_url || fallback"
                   class="rounded-circle" width="80" height="80"
                   style="object-fit:cover;border:3px solid var(--gp-red)" />
            </div>
            <h5 class="fw-700 mt-2 mb-0">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</h5>
            <div class="text-muted small text-truncate px-2">{{ form.headline }}</div>
            <div class="fw-700 text-gp-primary mt-1">GHS {{ form.hourly_rate }}/hr</div>
            <div v-if="profile.subjects_list?.length" class="d-flex flex-wrap justify-content-center gap-1 mt-2">
              <span v-for="subject in profile.subjects_list.slice(0, 4)" :key="subject.id" class="gp-badge small">{{ subject.name }}</span>
              <span v-if="profile.subjects_list.length > 4" class="text-muted small align-self-center">+{{ profile.subjects_list.length - 4 }} more</span>
            </div>
          </div>
          <hr />
          <div class="small">
            <div class="d-flex align-items-center gap-2 mb-1"><i class="bi bi-lightning-fill text-warning"></i><span>{{ form.instant_book?'Instant Book':'Request only' }}</span></div>
            <div class="d-flex align-items-center gap-2 mb-1"><i class="bi bi-clock text-primary"></i><span>Responds in ~{{ form.response_time }}m</span></div>
            <div v-if="form.trial_lesson_enabled" class="d-flex align-items-center gap-2"><i class="bi bi-gift-fill text-gp-primary"></i><span>Trial GHS {{ form.trial_lesson_price }}</span></div>
          </div>
          <div class="mt-3">
            <div class="small fw-600 mb-2 text-muted">Profile URL</div>
            <div class="input-group input-group-sm">
              <span class="input-group-text text-muted" style="font-size:.7rem">gooprep.com/tutor/</span>
              <input class="form-control form-control-sm" v-model="form.slug" placeholder="your-name" />
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
import { apiGet, apiPatch } from '@/utils/api'
import GpSpinner from '@/components/common/GpSpinner.vue'

const auth       = useAuthStore()
const notifStore = useNotifStore()
const loading    = ref(true)
const saving     = ref(false)
const profile    = ref({})
const styles     = ['interactive','structured','flexible','practical','visual']
const fallback   = computed(() => `https://ui-avatars.com/api/?name=${encodeURIComponent(auth.user?.first_name||'T')}&background=e63900&color=fff`)

const form = ref({
  headline:'', bio:'', hourly_rate:60, response_time:60, teaching_style:'interactive',
  language:'English', intro_video_url:'', slug:'', instant_book:true,
  trial_lesson_enabled:false, trial_lesson_price:30, record_by_default:true,
  packages: [],
})

function addPkg() { form.value.packages.push({ name:'', lessons:5, price:250, validity:'30 days' }) }

async function save() {
  saving.value = true
  try {
    const { data } = await apiPatch('/tutors/my-profile/', form.value)
    profile.value = data
    Object.keys(form.value).forEach(k => { if (data[k] !== undefined) form.value[k] = data[k] })
    notifStore.toast('Storefront saved!', 'success')
  } catch(e) {
    notifStore.toast(Object.values(e.response?.data||{}).flat().join(' ')||'Failed to save storefront.','error')
  }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const { data } = await apiGet('/tutors/my-profile/')
    profile.value = data
    Object.keys(form.value).forEach(k => { if (data[k] !== undefined) form.value[k] = data[k] })
  } catch {} finally { loading.value = false }
})
</script>
