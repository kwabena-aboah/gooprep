<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">My Students</h2><p class="text-muted small mb-0">{{ total }} students you've taught</p></div>
      <div class="input-group" style="max-width:280px">
        <span class="input-group-text"><i class="bi bi-search text-muted"></i></span>
        <input class="form-control form-control-sm" v-model="search" placeholder="Search students…" @input="debouncedFetch" />
      </div>
    </div>
    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!students.length" icon="bi bi-people" message="No students yet. Share your profile to get booked!" />
    <div v-else>
      <div class="row g-3">
        <div v-for="s in students" :key="s.id" class="col-md-6 col-lg-4">
          <div class="gp-card p-4">
            <div class="d-flex gap-3 mb-3">
              <img :src="s.avatar_url || fallback(s.full_name)" class="rounded-circle flex-shrink-0"
                   width="52" height="52" style="object-fit:cover;border:2px solid var(--gp-red)" />
              <div class="overflow-hidden">
                <div class="fw-700 text-truncate">{{ s.full_name }}</div>
                <div class="text-muted small">{{ s.total_lessons_with_me }} lessons together</div>
                <div class="text-muted small">Last: {{ timeAgo(s.last_lesson_at) }}</div>
              </div>
            </div>
            <div class="d-flex gap-1 flex-wrap mb-3">
              <span v-for="sub in (s.subjects||[]).slice(0,3)" :key="sub" class="gp-badge">{{ sub }}</span>
            </div>
            <div class="row g-2 text-center mb-3">
              <div class="col-4"><div class="fw-700 text-gp-primary">{{ s.total_lessons_with_me }}</div><div class="text-muted" style="font-size:.7rem">Lessons</div></div>
              <div class="col-4"><div class="fw-700 text-success">{{ s.completion_rate }}%</div><div class="text-muted" style="font-size:.7rem">Completed</div></div>
              <div class="col-4"><div class="fw-700 text-warning">{{ s.avg_rating || '—' }}</div><div class="text-muted" style="font-size:.7rem">Avg Rating</div></div>
            </div>
            <div class="d-grid gap-1">
              <button class="btn btn-gp btn-sm" @click="msgStudent(s)"><i class="bi bi-chat me-1"></i>Message</button>
              <RouterLink :to="`/lessons?student=${s.id}`" class="btn btn-sm btn-outline-secondary">View Lessons</RouterLink>
            </div>
          </div>
        </div>
      </div>
      <GpPagination :page="page" :total-pages="totalPages" @change="p=>{page=p;fetchStudents()}" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet, apiPost } from '@/utils/api'
import { timeAgo, debounce } from '@/utils/helpers'
import GpSpinner    from '@/components/common/GpSpinner.vue'
import GpEmpty      from '@/components/common/GpEmpty.vue'
import GpPagination from '@/components/common/GpPagination.vue'

const router   = useRouter()
const students = ref([])
const loading  = ref(true)
const total    = ref(0)
const page     = ref(1)
const search   = ref('')
const fallback = name => `https://ui-avatars.com/api/?name=${encodeURIComponent(name||'S')}&background=e2e8f0&color=64748b`
const totalPages = computed(() => Math.ceil(total.value / 12))
const debouncedFetch = debounce(() => { page.value=1; fetchStudents() }, 350)

async function fetchStudents() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 12 }
    if (search.value) params.search = search.value
    const { data } = await apiGet('/tutors/my-students/', params)
    students.value = data.results || []; total.value = data.count || 0
  } catch { students.value = [] }
  finally { loading.value = false }
}

async function msgStudent(s) {
  try {
    await apiPost('/messaging/conversations/', { user_id: s.id })
    router.push(`/messages?student=${s.id}`)
  } catch { router.push('/messages') }
}

onMounted(fetchStudents)
</script>
