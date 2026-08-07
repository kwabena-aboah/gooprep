<template>
  <div>
    <!-- Public nav for guests -->
    <nav v-if="!auth.isAuthenticated" class="gp-navbar mb-4">
      <RouterLink to="/" class="me-auto logo"><img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:36px" /></RouterLink>
      <RouterLink to="/login" class="btn btn-sm btn-outline-light me-2">Log in</RouterLink>
      <RouterLink to="/register" class="btn btn-sm btn-gp">Sign up</RouterLink>
    </nav>

    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Group Classes</h2><p class="text-muted small mb-0">Live sessions with expert tutors — up to 10 students</p></div>
      <div class="d-flex gap-2">
        <select class="form-select form-select-sm" v-model="subjectFilter" @change="fetchClasses" style="width:auto">
          <option value="">All Subjects</option>
          <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
        <select class="form-select form-select-sm" v-model="levelFilter" @change="fetchClasses" style="width:auto">
          <option value="">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>
    </div>

    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!classes.length" icon="bi bi-people-fill" message="No group classes scheduled. Check back soon!" />

    <div v-else class="row g-4">
      <div v-for="c in classes" :key="c.id" class="col-md-6 col-lg-4">
        <div class="gp-card h-100 overflow-hidden">
          <!-- Header colour -->
          <div class="p-4 position-relative" style="background:linear-gradient(135deg,#111,#1a0800)">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="badge bg-primary-subtle text-primary small">{{ c.subject_name }}</span>
              <span class="badge" :class="spotsLeft(c)>3?'bg-success-subtle text-success':spotsLeft(c)>0?'bg-warning-subtle text-warning':'bg-danger-subtle text-danger'">
                {{ spotsLeft(c) > 0 ? `${spotsLeft(c)} spots left` : 'Full' }}
              </span>
            </div>
            <h5 class="fw-700 text-white mb-1">{{ c.title }}</h5>
            <div class="text-white-50 small">by {{ c.tutor_name }}</div>
          </div>
          <div class="p-4 d-flex flex-column flex-grow-1">
            <p class="text-muted small mb-3">{{ truncate(c.description, 120) }}</p>
            <div class="d-flex flex-wrap gap-2 mb-3">
              <span class="badge bg-light text-dark border small"><i class="bi bi-calendar3 me-1"></i>{{ fmtDateTime(c.start_time) }}</span>
              <span class="badge bg-light text-dark border small"><i class="bi bi-clock me-1"></i>{{ c.duration_minutes }} min</span>
              <span class="badge bg-light text-dark border small"><i class="bi bi-bar-chart me-1"></i>{{ c.level }}</span>
              <span class="badge bg-light text-dark border small"><i class="bi bi-people me-1"></i>{{ c.enrolled }}/{{ c.max_students }}</span>
            </div>
            <!-- Seat bar -->
            <div class="mb-3">
              <div class="gp-progress" style="height:6px">
                <div class="gp-progress-bar" :style="`width:${Math.round(c.enrolled/c.max_students*100)}%;background:${spotsLeft(c)>3?'var(--gp-success)':spotsLeft(c)>0?'var(--gp-warning)':'var(--gp-danger)'}`"></div>
              </div>
              <div class="text-muted small mt-1">{{ c.enrolled }}/{{ c.max_students }} enrolled</div>
            </div>
            <div class="mt-auto d-flex align-items-center justify-content-between">
              <span class="fw-700 text-gp-primary fs-5">GHS {{ c.price }}<span class="text-muted fw-400 small">/person</span></span>
              <button class="btn btn-gp btn-sm" @click="enroll(c)" :disabled="spotsLeft(c)===0 || enrolling===c.id">
                <span v-if="enrolling===c.id" class="spinner-border spinner-border-sm"></span>
                <span v-else>{{ c.is_enrolled ? 'Enrolled ✓' : 'Enroll Now' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <GpPagination :page="page" :total-pages="totalPages" @change="p=>{page=p;fetchClasses()}" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDateTime, truncate } from '@/utils/helpers'
import GpSpinner    from '@/components/common/GpSpinner.vue'
import GpEmpty      from '@/components/common/GpEmpty.vue'
import GpPagination from '@/components/common/GpPagination.vue'

const auth       = useAuthStore()
const notifStore = useNotifStore()
const router     = useRouter()
const classes    = ref([])
const subjects   = ref([])
const loading    = ref(true)
const enrolling  = ref(null)
const total      = ref(0)
const page       = ref(1)
const subjectFilter = ref('')
const levelFilter   = ref('')
const totalPages = computed(() => Math.ceil(total.value / 12))
const spotsLeft  = c => c.max_students - c.enrolled

async function fetchClasses() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 12, ordering: 'start_time' }
    if (subjectFilter.value) params.subject = subjectFilter.value
    if (levelFilter.value) params.level = levelFilter.value
    const { data } = await apiGet('/courses/group-classes/', params)
    classes.value = data.results || []; total.value = data.count || 0
  } catch { classes.value = [] }
  finally { loading.value = false }
}

async function enroll(c) {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  if (c.is_enrolled) { notifStore.toast('Already enrolled!','info'); return }
  enrolling.value = c.id
  try {
    await apiPost(`/courses/group-classes/${c.id}/enroll/`)
    c.is_enrolled = true; c.enrolled++
    notifStore.toast('Enrolled! Check your lessons.','success')
  } catch(e) { notifStore.toast(e.response?.data?.detail||'Enrollment failed.','error') }
  finally { enrolling.value = null }
}

onMounted(async () => {
  const [_, subj] = await Promise.all([fetchClasses(), apiGet('/tutors/subjects/')])
  subjects.value = Array.isArray(subj.data) ? subj.data : (subj.data?.results || [])
})
</script>
