<template>
  <div style="max-width:760px;margin:0 auto">
    <div class="text-center mb-5">
      <h2 class="fw-800 mb-1">Become a Gooprep Tutor</h2>
      <p class="text-muted">Complete your profile to start earning with Ghana's #1 tutoring platform.</p>
      <!-- Progress -->
      <div class="d-flex gap-2 justify-content-center mt-4">
        <div v-for="(s,i) in steps" :key="i"
             class="d-flex align-items-center gap-2">
          <div class="rounded-circle d-flex align-items-center justify-content-center fw-700"
               style="width:36px;height:36px;font-size:.85rem;transition:all .3s"
               :style="step>i?'background:var(--gp-red);color:#fff':step===i?'background:#fff;color:var(--gp-red);border:2px solid var(--gp-red)':'background:#e2e8f0;color:#94a3b8'">
            <i v-if="step>i" class="bi bi-check-lg"></i>
            <span v-else>{{ i+1 }}</span>
          </div>
          <span class="small d-none d-md-inline" :class="step>=i?'fw-600':'text-muted'">{{ s }}</span>
          <div v-if="i<steps.length-1" class="flex-grow-1" style="width:32px;height:2px;background:#e2e8f0"></div>
        </div>
      </div>
    </div>

    <!-- Step 0: Basic info -->
    <div v-if="step===0" class="gp-card p-4 p-md-5">
      <h5 class="fw-700 mb-4"><i class="bi bi-person-circle me-2 text-gp-primary"></i>Basic Information</h5>
      <div class="row g-3">
        <div class="col-12">
          <label class="form-label small fw-600">Profile Headline *</label>
          <input class="form-control" v-model="form.headline" placeholder="e.g. Experienced Maths & Physics Tutor · 5 Years" />
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-600">Years of Experience *</label>
          <input type="number" class="form-control" v-model="form.years_experience" min="0" max="50" />
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-600">Hourly Rate (GHS) *</label>
          <div class="input-group">
            <span class="input-group-text">GHS</span>
            <input type="number" class="form-control" v-model="form.hourly_rate" min="20" placeholder="50" />
          </div>
          <div class="form-text">Suggested: GHS 40–120/hr for Ghanaian market</div>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-600">Teaching Style *</label>
          <select class="form-select" v-model="form.teaching_style">
            <option value="interactive">Interactive & Discussion</option>
            <option value="structured">Structured & Syllabus-based</option>
            <option value="flexible">Flexible & Student-led</option>
            <option value="practical">Practical & Problem-solving</option>
            <option value="visual">Visual & Diagram-heavy</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-600">Date of birth *</label>
          <input type="date" class="form-control" v-model="form.date_of_birth" required />
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-600">Gender *</label>
          <select class="form-select" v-model="form.gender" required><option value="">Select gender</option><option>Female</option><option>Male</option><option>Non-binary</option><option>Prefer not to say</option></select>
        </div>
        <div class="col-md-6"><label class="form-label small fw-600">City *</label><input class="form-control" v-model="form.city" required placeholder="Accra, Kumasi…" /></div>
        <div class="col-md-6"><label class="form-label small fw-600">Address *</label><input class="form-control" v-model="form.address" required placeholder="Residential address" /></div>
        <div class="col-12">
          <label class="form-label small fw-600">Bio *</label>
          <textarea class="form-control" rows="5" v-model="form.bio"
                    placeholder="Tell students about your background, teaching philosophy, and what makes you great…"></textarea>
          <div class="d-flex justify-content-between">
            <div class="form-text">Min 100 characters</div>
            <div class="text-muted small">{{ form.bio.length }}/1500</div>
          </div>
        </div>
        <div class="col-12">
          <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" v-model="form.instant_book" />
            <label class="form-check-label small fw-600">Enable Instant Book <span class="text-muted fw-400">(students book without waiting)</span></label>
          </div>
        </div>
        <div class="col-md-6">
          <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" v-model="form.trial_lesson_enabled" />
            <label class="form-check-label small fw-600">Offer trial lessons</label>
          </div>
        </div>
        <div v-if="form.trial_lesson_enabled" class="col-md-6">
          <label class="form-label small fw-600">Trial Price (GHS)</label>
          <input type="number" class="form-control" v-model="form.trial_lesson_price" min="0" />
        </div>
      </div>
    </div>

    <!-- Step 1: Subjects -->
    <div v-if="step===1" class="gp-card p-4 p-md-5">
      <h5 class="fw-700 mb-4"><i class="bi bi-book me-2 text-gp-primary"></i>Subjects & Education</h5>
      <div class="mb-4">
        <label class="form-label small fw-600">Subjects You Teach *</label>
        <div class="row g-2">
          <div v-for="s in allSubjects" :key="s.id" class="col-6 col-md-4">
            <div class="form-check p-2 border rounded-3"
                 :class="form.subjects.includes(s.id)?'border-primary bg-primary-subtle':''">
              <input class="form-check-input" type="checkbox" :id="`s${s.id}`"
                     :value="s.id" v-model="form.subjects" />
              <label class="form-check-label small" :for="`s${s.id}`">{{ s.name }}</label>
            </div>
          </div>
        </div>
        <div class="form-text mt-2">{{ form.subjects.length }} selected</div>
      </div>
      <h6 class="fw-700 mb-3">Education</h6>
      <div v-for="(e,i) in form.education" :key="i" class="gp-card-flat p-3 mb-2">
        <div class="row g-2">
          <div class="col-md-5"><input class="form-control form-control-sm" v-model="e.institution" placeholder="University / School" /></div>
          <div class="col-md-4"><input class="form-control form-control-sm" v-model="e.degree" placeholder="Degree / Certificate" /></div>
          <div class="col-md-2"><input type="number" class="form-control form-control-sm" v-model="e.year" placeholder="Year" /></div>
          <div class="col-md-1 d-flex align-items-center">
            <button class="btn btn-sm btn-outline-danger" @click="form.education.splice(i,1)"><i class="bi bi-x"></i></button>
          </div>
        </div>
      </div>
      <button class="btn btn-sm btn-gp-outline mt-1" @click="form.education.push({institution:'',degree:'',year:''})">
        <i class="bi bi-plus me-1"></i>Add Education
      </button>
    </div>

    <!-- Step 2: Media -->
    <div v-if="step===2" class="gp-card p-4 p-md-5">
      <h5 class="fw-700 mb-4"><i class="bi bi-camera-video me-2 text-gp-primary"></i>Profile Photo & Video</h5>
      <div class="row g-4">
        <div class="col-md-6">
          <label class="form-label small fw-600">Profile Photo *</label>
          <div class="text-center p-4 border-2 border-dashed rounded-3" style="border:2px dashed var(--gp-border)">
            <img v-if="avatarPrev" :src="avatarPrev" class="rounded-circle mb-2" width="80" height="80" style="object-fit:cover" />
            <i v-else class="bi bi-camera d-block fs-1 text-muted mb-2"></i>
            <label class="btn btn-sm btn-gp-outline">
              Choose Photo <input type="file" class="d-none" accept="image/*" @change="setAvatar" />
            </label>
            <div class="form-text">JPG/PNG, max 5MB, square preferred</div>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-600">Intro Video URL <span class="text-muted fw-400">(optional)</span></label>
          <input class="form-control mb-2" v-model="form.intro_video_url" placeholder="https://youtube.com/…" />
          <div class="form-text">Link a 1-2 min intro video from YouTube or Vimeo to boost bookings by 70%.</div>
          <div v-if="form.intro_video_url" class="mt-3">
            <iframe :src="embedUrl" class="w-100 rounded-3" height="160" frameborder="0" allowfullscreen></iframe>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Identity & documents -->
    <div v-if="step===3" class="gp-card p-4 p-md-5">
      <h5 class="fw-700 mb-4"><i class="bi bi-file-earmark-lock me-2 text-gp-primary"></i>Identity & Professional Documents</h5>
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label small fw-600">Identity document type *</label>
          <select class="form-select" v-model="form.identity_document_type">
            <option value="" disabled>Select document type</option>
            <option v-for="option in identityOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-600">Identity document *</label>
          <input class="form-control" type="file" accept="image/*,.pdf" @change="setIdentityDocument" />
          <div class="form-text">JPG, PNG or PDF. Maximum 10MB.</div>
          <div v-if="identityFile" class="small text-success mt-1"><i class="bi bi-check-circle me-1"></i>{{ identityFile.name }}</div>
        </div>
        <div class="col-12">
          <label class="form-label small fw-600">Professional certificates and other documents <span class="text-muted fw-400">(optional)</span></label>
          <input class="form-control" type="file" accept="image/*,.pdf" multiple @change="setSupportingDocuments" />
          <div class="form-text">Upload certificates, degrees or other supporting documents in image/PDF format.</div>
          <div v-if="supportingFiles.length" class="small text-muted mt-1">{{ supportingFiles.length }} file(s) selected</div>
        </div>
      </div>
    </div>

    <!-- Step 4: Preview -->
    <div v-if="step===4" class="gp-card p-4 p-md-5">
      <h5 class="fw-700 mb-4"><i class="bi bi-eye me-2 text-gp-primary"></i>Preview & Submit</h5>
      <div class="gp-card p-4 mb-4" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)">
        <div class="d-flex gap-3 align-items-start mb-3">
          <img :src="avatarPrev || fallback" class="rounded-circle flex-shrink-0"
               width="72" height="72" style="object-fit:cover;border:3px solid var(--gp-red)" />
          <div>
            <h5 class="fw-700 mb-0">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</h5>
            <div class="text-muted small">{{ form.headline }}</div>
            <div class="mt-1"><span class="fw-700 text-gp-primary">GHS {{ form.hourly_rate }}/hr</span> · {{ form.years_experience }} years exp</div>
          </div>
        </div>
        <p class="text-muted small mb-2">{{ form.bio.slice(0,200) }}{{ form.bio.length>200?'…':'' }}</p>
        <div class="d-flex flex-wrap gap-1">
          <span v-for="sid in form.subjects.slice(0,5)" :key="sid" class="gp-badge">
            {{ allSubjects.find(s=>s.id===sid)?.name }}
          </span>
        </div>
      </div>
      <div class="alert alert-info small"><i class="bi bi-info-circle me-2"></i>Your profile will be reviewed by our team within 24–48 hours. You'll be notified by email.</div>
      <div class="form-check mb-3">
        <input class="form-check-input" type="checkbox" v-model="agreedTerms" />
        <label class="form-check-label small">I agree to Gooprep's <RouterLink to="/terms" target="_blank" class="text-gp-primary">Tutor Terms</RouterLink> and <RouterLink to="/privacy" target="_blank" class="text-gp-primary">Privacy Policy</RouterLink></label>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="alert alert-danger small mt-3">{{ error }}</div>

    <!-- Navigation -->
    <div class="d-flex justify-content-between mt-4">
      <button class="btn btn-outline-secondary" @click="step--" :disabled="step===0">
        <i class="bi bi-chevron-left me-1"></i>Back
      </button>
      <button v-if="step<steps.length-1" class="btn btn-gp" @click="next" :disabled="!stepValid">
        Next <i class="bi bi-chevron-right ms-1"></i>
      </button>
      <button v-else class="btn btn-gp px-4" @click="submit" :disabled="!agreedTerms||submitting">
        <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-send me-2"></i>Submit for Review
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost, apiUpload } from '@/utils/api'

const auth       = useAuthStore()
const notifStore = useNotifStore()
const router     = useRouter()
const step       = ref(0)
const submitting = ref(false)
const error      = ref('')
const agreedTerms= ref(false)
const allSubjects= ref([])
const avatarPrev = ref('')
const avatarFile = ref(null)
const identityFile = ref(null)
const supportingFiles = ref([])
const identityOptions = [
  { value:'ghana_passport_card', label:'Ghana passport card' },
  { value:'voters_id_card', label:"Voter's ID card" },
  { value:'drivers_license', label:"Driver's license" },
  { value:'other_id', label:'Other identity document' },
]

const steps = ['Basic Info','Subjects','Media','Documents','Preview']
const form  = ref({
  headline:'', years_experience:1, hourly_rate:60, teaching_style:'interactive',
  city:'', bio:'', instant_book:false, trial_lesson_enabled:false, trial_lesson_price:30,
  subjects:[], education:[], intro_video_url:'', identity_document_type:'',
})
const draftKey = computed(() => `gooprep:tutor-onboarding:${auth.user?.id || 'guest'}`)

function saveDraft() {
  localStorage.setItem(draftKey.value, JSON.stringify({
    form: form.value,
    step: step.value,
  }))
}
function restoreDraft(profile) {
  try {
    const draft = JSON.parse(localStorage.getItem(draftKey.value) || '{}')
    if (draft.form) Object.assign(form.value, draft.form)
    if (Number.isInteger(draft.step)) step.value = Math.min(draft.step, steps.length - 1)
  } catch { /* Ignore invalid drafts. */ }
  if (profile) {
    const backendForm = {
      headline: profile.headline, bio: profile.bio, years_experience: profile.years_experience,
      hourly_rate: profile.hourly_rate, teaching_style: profile.teaching_style,
      intro_video_url: profile.intro_video_url, identity_document_type: profile.identity_document_type,
      education: profile.education, subjects: (profile.subjects_list || []).map(s => s.id),
    }
    Object.entries(backendForm).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '' && !(Array.isArray(value) && !value.length)) form.value[key] = value
    })
  }
}
watch([form, step], saveDraft, { deep: true })

const fallback = computed(() =>
  `https://ui-avatars.com/api/?name=${encodeURIComponent(auth.user?.first_name||'T')}&background=e63900&color=fff`)

const embedUrl = computed(() => {
  const u = form.value.intro_video_url
  if (u.includes('youtu')) {
    const id = u.split('v=')[1]?.split('&')[0] || u.split('/').pop()
    return `https://www.youtube.com/embed/${id}`
  }
  if (u.includes('vimeo')) return `https://player.vimeo.com/video/${u.split('/').pop()}`
  return u
})

const stepValid = computed(() => {
  if (step.value===0) return form.value.headline && form.value.hourly_rate>0 && form.value.bio.length>=100 && form.value.date_of_birth && form.value.gender && form.value.city && form.value.address
  if (step.value===1) return form.value.subjects.length>0
  if (step.value===3) return !!form.value.identity_document_type && !!identityFile.value
  return true
})

function next() { if (stepValid.value) step.value++ }

function setAvatar(e) {
  avatarFile.value = e.target.files[0]
  if (avatarFile.value) avatarPrev.value = URL.createObjectURL(avatarFile.value)
}

function setIdentityDocument(e) { identityFile.value = e.target.files[0] || null }
function setSupportingDocuments(e) { supportingFiles.value = Array.from(e.target.files || []) }

async function submit() {
  submitting.value = true; error.value = ''
  try {
    if (avatarFile.value) {
      const fd = new FormData(); fd.append('avatar', avatarFile.value)
      await apiUpload('/auth/users/me/', fd)
      await auth.fetchMe()
    }
    const fd = new FormData()
    Object.entries({
      headline: form.value.headline, bio: form.value.bio,
      years_experience: form.value.years_experience, hourly_rate: form.value.hourly_rate,
      teaching_style: form.value.teaching_style, city: form.value.city, address: form.value.address,
      date_of_birth: form.value.date_of_birth, gender: form.value.gender,
      instant_book: form.value.instant_book, trial_lesson_enabled: form.value.trial_lesson_enabled,
      trial_lesson_price: form.value.trial_lesson_price,
      education: JSON.stringify(form.value.education),
      intro_video_url: form.value.intro_video_url,
      identity_document_type: form.value.identity_document_type,
    }).forEach(([key, value]) => fd.append(key, value))
    form.value.subjects.forEach(subject => fd.append('subjects', subject))
    fd.append('identity_document', identityFile.value)
    supportingFiles.value.forEach(file => fd.append('documents', file))
    fd.append('document_type', 'professional_certificate')
    await apiUpload('/tutors/onboarding/', fd, 'post')
    localStorage.removeItem(draftKey.value)
    notifStore.toast('Application submitted! We\'ll review within 24–48h.', 'success')
    setTimeout(() => router.push('/dashboard'), 1800)
  } catch(e) {
    error.value = Object.values(e.response?.data||{}).flat().join(' ') || 'Submission failed.'
  } finally { submitting.value = false }
}

onMounted(async () => {
  const [{ data: subjectsData }, { data: onboardingData }] = await Promise.all([
    apiGet('/tutors/subjects/'),
    apiGet('/tutors/onboarding/'),
  ])
  allSubjects.value = Array.isArray(subjectsData) ? subjectsData : (subjectsData.results || [])
  restoreDraft(onboardingData?.profile)
})
</script>
