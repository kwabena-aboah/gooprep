<template>
  <div>
    <nav v-if="!auth.isAuthenticated" class="gp-navbar mb-4">
      <RouterLink to="/" class="me-auto logo">
        <img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:36px" />
      </RouterLink>
      <RouterLink to="/login" class="btn btn-sm btn-outline-light me-2">Log in</RouterLink>
      <RouterLink to="/register" class="btn btn-sm btn-gp">Sign up</RouterLink>
    </nav>

    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Group Classes</h2><p class="text-muted small mb-0">Live sessions with expert tutors</p></div>
      <div class="d-flex gap-2 align-items-center flex-wrap">
        <button v-if="selectedClasses.size" class="btn btn-gp btn-sm" :disabled="bulkEnrolling" @click="bulkEnroll">
          <span v-if="bulkEnrolling" class="spinner-border spinner-border-sm me-1"></span>Enroll {{ selectedClasses.size }} selected
        </button>
        <select v-model="subjectFilter" class="form-select form-select-sm" @change="fetchClasses" style="width:auto">
          <option value="">All Subjects</option><option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
        </select>
        <select v-model="levelFilter" class="form-select form-select-sm" @change="fetchClasses" style="width:auto">
          <option value="">All Levels</option><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option>
        </select>
      </div>
    </div>

    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!classes.length" icon="bi bi-people-fill" message="No group classes scheduled." />
    <div v-else class="row g-4">
      <div v-for="groupClass in classes" :key="groupClass.id" class="col-md-6 col-lg-4">
        <div class="gp-card h-100 overflow-hidden">
          <div class="p-4" style="background:linear-gradient(135deg,#111,#1a0800)">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="badge bg-primary-subtle text-primary small">{{ groupClass.subject_name || 'General' }}</span>
              <div class="d-flex gap-2 align-items-center">
                <input v-if="!groupClass.is_enrolled && spotsLeft(groupClass) > 0" class="form-check-input" type="checkbox" :checked="selectedClasses.has(groupClass.id)" @change="toggleSelected(groupClass.id)" />
                <span class="badge" :class="spotsLeft(groupClass) ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">{{ spotsLeft(groupClass) ? `${spotsLeft(groupClass)} spots left` : 'Full' }}</span>
              </div>
            </div>
            <h5 class="fw-700 text-white mb-1">{{ groupClass.title }}</h5><div class="text-white-50 small">by {{ groupClass.tutor_name }}</div>
          </div>
          <div class="p-4 d-flex flex-column h-100">
            <p class="text-muted small mb-3">{{ truncate(groupClass.description, 120) }}</p>
            <div class="d-flex flex-wrap gap-2 mb-3"><span class="badge bg-light text-dark border small">{{ fmtDateTime(groupClass.start_time) }}</span><span class="badge bg-light text-dark border small">{{ groupClass.duration_minutes }} min</span><span class="badge bg-light text-dark border small">{{ groupClass.enrolled }}/{{ groupClass.max_students }}</span></div>
            <div class="mb-3"><div class="gp-progress" style="height:6px"><div class="gp-progress-bar" :style="`width:${Math.min(100, groupClass.enrolled / groupClass.max_students * 100)}%`"></div></div></div>
            <div class="mt-auto d-flex justify-content-between align-items-center"><span class="fw-700 text-gp-primary">GHS {{ groupClass.price }}</span><button class="btn btn-gp btn-sm" :disabled="groupClass.is_enrolled || !spotsLeft(groupClass) || enrolling === groupClass.id" @click="enroll(groupClass)"><span v-if="enrolling === groupClass.id" class="spinner-border spinner-border-sm"></span><span v-else>{{ groupClass.is_enrolled ? 'Enrolled ✓' : 'Enroll Now' }}</span></button></div>
          </div>
        </div>
      </div>
    </div>
    <GpPagination :page="page" :total-pages="totalPages" @change="changePage" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDateTime, truncate } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty from '@/components/common/GpEmpty.vue'
import GpPagination from '@/components/common/GpPagination.vue'

const auth = useAuthStore(); const notifStore = useNotifStore(); const router = useRouter()
const classes = ref([]); const subjects = ref([]); const loading = ref(true); const enrolling = ref(null); const bulkEnrolling = ref(false); const selectedClasses = ref(new Set()); const total = ref(0); const page = ref(1); const subjectFilter = ref(''); const levelFilter = ref('')
const totalPages = computed(() => Math.ceil(total.value / 12)); const spotsLeft = item => Math.max(0, item.max_students - item.enrolled)
function changePage(value) { page.value = value; fetchClasses() }
function toggleSelected(id) { const next = new Set(selectedClasses.value); next.has(id) ? next.delete(id) : next.add(id); selectedClasses.value = next }
async function fetchClasses() { loading.value = true; try { const params = { page: page.value, page_size: 12 }; if (subjectFilter.value) params.subject = subjectFilter.value; if (levelFilter.value) params.level = levelFilter.value; const { data } = await apiGet('/courses/group-classes/', params); classes.value = data.results || []; total.value = data.count || 0 } catch { classes.value = [] } finally { loading.value = false } }
async function enroll(item) { if (!auth.isAuthenticated) { router.push('/login'); return }; enrolling.value = item.id; try { await apiPost(`/courses/group-classes/${item.id}/enroll/`); item.is_enrolled = true; item.enrolled += 1; notifStore.toast('Enrolled successfully.', 'success') } catch (error) { notifStore.toast(error.response?.data?.error || 'Enrollment failed.', 'error') } finally { enrolling.value = null } }
async function bulkEnroll() { if (!auth.isAuthenticated) { router.push('/login'); return }; bulkEnrolling.value = true; try { const { data } = await apiPost('/courses/group-classes/bulk-enroll/', { class_ids: [...selectedClasses.value] }); const enrolled = new Set(data.enrolled || []); classes.value.forEach(item => { if (enrolled.has(item.id)) { item.is_enrolled = true; item.enrolled += 1 } }); selectedClasses.value = new Set(); notifStore.toast(`Enrolled in ${enrolled.size} group class(es).`, 'success') } catch (error) { notifStore.toast(error.response?.data?.error || 'Bulk enrollment failed.', 'error') } finally { bulkEnrolling.value = false } }
onMounted(async () => { const [_, response] = await Promise.all([fetchClasses(), apiGet('/tutors/subjects/')]); subjects.value = Array.isArray(response.data) ? response.data : (response.data?.results || []) })
</script>
