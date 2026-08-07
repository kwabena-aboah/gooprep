<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Learning Hub</h2><p class="text-muted small mb-0">Your notes, flashcards, and study materials</p></div>
      <RouterLink to="/tutors" class="btn btn-gp btn-sm"><i class="bi bi-search me-1"></i>Find a Tutor</RouterLink>
    </div>

    <GpSpinner v-if="loading" />
    <div v-else>
      <!-- Learning stats -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3"><StatCard label="Lessons Done" :value="stats.completed" icon="bi bi-calendar-check" color="red" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Hours Learned" :value="stats.hours" icon="bi bi-clock-history" color="green" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Subjects" :value="stats.subjects" icon="bi bi-book" color="amber" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Day Streak" :value="auth.user?.streak_days||0" icon="bi bi-fire" color="blue" /></div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-4">
        <li v-for="t in tabs" :key="t.key" class="nav-item">
          <button class="nav-link small fw-600" :class="{active:tab===t.key}" @click="tab=t.key">
            <i :class="t.icon" class="me-1"></i>{{ t.label }}
          </button>
        </li>
      </ul>

      <!-- Notes -->
      <div v-if="tab==='notes'">
        <GpEmpty v-if="!notes.length" icon="bi bi-journal-text" message="No notes yet. They appear automatically after lessons." />
        <div v-else class="row g-3">
          <div v-for="n in notes" :key="n.id" class="col-md-6">
            <div class="gp-card p-4">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="fw-700 small">{{ n.subject_name || 'Study Notes' }}</div>
                <span class="text-muted" style="font-size:.7rem">{{ timeAgo(n.lesson_date) }}</span>
              </div>
              <div class="text-muted small mb-3" style="max-height:100px;overflow:hidden">{{ n.ai_summary }}</div>
              <button class="btn btn-sm btn-gp-outline w-100" @click="openNote(n)">
                <i class="bi bi-journal-richtext me-1"></i>View Full Notes
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Flashcards -->
      <div v-if="tab==='flashcards'">
        <div class="mb-3 d-flex gap-2 flex-wrap">
          <select class="form-select form-select-sm" v-model="fcFilter" style="width:auto">
            <option value="">All Subjects</option>
            <option v-for="s in subjectList" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <GpEmpty v-if="!filteredCards.length" icon="bi bi-card-text" message="No flashcards yet." />
        <FlashcardDeck v-else :cards="filteredCards" />
      </div>

      <!-- Quiz -->
      <div v-if="tab==='quiz'">
        <div class="mb-3">
          <select class="form-select form-select-sm" v-model="quizFilter" style="width:auto">
            <option value="">All Subjects</option>
            <option v-for="s in subjectList" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <GpEmpty v-if="!filteredQuiz.length" icon="bi bi-patch-question" message="No quizzes yet. Complete lessons to unlock." />
        <QuizWidget v-else :questions="filteredQuiz" />
      </div>

      <!-- Favourite tutors -->
      <div v-if="tab==='favourites'">
        <GpEmpty v-if="!favourites.length" icon="bi bi-heart" message="No favourite tutors yet."
                 action-label="Browse Tutors" action-to="/tutors" />
        <div v-else class="row g-3">
          <div v-for="t in favourites" :key="t.id" class="col-md-6 col-lg-4">
            <TutorCard :tutor="t" :is-fav="true" @select="openTutor" @fav="removeFav" />
          </div>
        </div>
      </div>
    </div>

    <!-- Note detail modal -->
    <div class="modal fade" id="noteModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content" v-if="activeNote">
          <div class="modal-header">
            <h5 class="modal-title fw-700">{{ activeNote.subject_name }} — Notes</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="gp-card p-3 mb-4" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)">
              <div class="fw-600 small mb-1"><i class="bi bi-robot me-1 text-gp-primary"></i>AI Summary</div>
              <p class="small mb-0 text-muted">{{ activeNote.ai_summary }}</p>
            </div>
            <FlashcardDeck v-if="activeNote.ai_flashcards?.length" :cards="activeNote.ai_flashcards" class="mb-4" />
            <QuizWidget v-if="activeNote.ai_quiz?.length" :questions="activeNote.ai_quiz" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Modal } from 'bootstrap'
import { useAuthStore } from '@/stores/auth'
import { apiGet, apiPost } from '@/utils/api'
import { timeAgo } from '@/utils/helpers'
import GpSpinner     from '@/components/common/GpSpinner.vue'
import GpEmpty       from '@/components/common/GpEmpty.vue'
import StatCard      from '@/components/common/StatCard.vue'
import TutorCard     from '@/components/tutor/TutorCard.vue'
import FlashcardDeck from '@/components/student/FlashcardDeck.vue'
import QuizWidget    from '@/components/student/QuizWidget.vue'

const auth       = useAuthStore()
const route      = useRoute()
const loading    = ref(true)
const tab        = ref(route.name==='knowledge-base'?'notes':route.name==='assessments'?'quiz':'notes')
const notes      = ref([])
const flashcards = ref([])
const quizzes    = ref([])
const favourites = ref([])
const fcFilter   = ref('')
const quizFilter = ref('')
const activeNote = ref(null)
const stats      = ref({ completed:0, hours:'0', subjects:0 })

const tabs = [
  { key:'notes',      label:'Notes & Summaries', icon:'bi bi-journal-richtext' },
  { key:'flashcards', label:'Flashcards',         icon:'bi bi-card-text' },
  { key:'quiz',       label:'Practice Quizzes',   icon:'bi bi-patch-question' },
  { key:'favourites', label:'Favourite Tutors',   icon:'bi bi-heart' },
]

const subjectList     = computed(() => [...new Set(notes.value.map(n=>n.subject_name).filter(Boolean))])
const filteredCards   = computed(() => fcFilter.value ? flashcards.value.filter(c=>c.subject===fcFilter.value) : flashcards.value)
const filteredQuiz    = computed(() => quizFilter.value ? quizzes.value.filter(q=>q.subject===quizFilter.value) : quizzes.value)

function openNote(n) { activeNote.value = n; new Modal(document.getElementById('noteModal')).show() }
function openTutor(t) { window.location.href = `/tutors/${t.id}` }

async function removeFav(t) {
  await apiPost(`/tutors/${t.id}/favourite/`)
  favourites.value = favourites.value.filter(f => f.id !== t.id)
}

onMounted(async () => {
  try {
    const [lessons, favs] = await Promise.all([ apiGet('/scheduling/lessons/'), apiGet('/tutors/favourites/') ])
    const completed = (lessons.data?.results||[]).filter(l=>l.status==='completed')
    stats.value = {
      completed: completed.length,
      hours: (completed.reduce((a,l)=>a+(l.duration_minutes||0),0)/60).toFixed(1),
      subjects: new Set(completed.map(l=>l.subject_name).filter(Boolean)).size,
    }
    notes.value = completed.filter(l=>l.ai_summary)
    flashcards.value = completed.flatMap(l=>(l.ai_flashcards||[]).map(c=>({...c,subject:l.subject_name})))
    quizzes.value    = completed.flatMap(l=>(l.ai_quiz||[]).map(q=>({...q,subject:l.subject_name})))
    favourites.value = favs.data?.results || []
  } catch {} finally { loading.value = false }
})
</script>
