<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-800 mb-0">Learning Hub</h2>
        <p class="text-muted small mb-0">Your notes, flashcards, quizzes, and progress reports</p>
      </div>
      <RouterLink to="/tutors" class="btn btn-gp btn-sm"><i class="bi bi-search me-1"></i>Find a Tutor</RouterLink>
    </div>

    <GpSpinner v-if="loading" />
    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3"><StatCard label="Lessons Done" :value="stats.completed" icon="bi bi-calendar-check" color="red" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Hours Learned" :value="stats.hours" icon="bi bi-clock-history" color="green" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Subjects" :value="stats.subjects" icon="bi bi-book" color="amber" /></div>
        <div class="col-6 col-lg-3"><StatCard label="Day Streak" :value="auth.user?.streak_days || 0" icon="bi bi-fire" color="blue" /></div>
      </div>

      <ul class="nav nav-tabs mb-4">
        <li v-for="item in tabs" :key="item.key" class="nav-item">
          <button class="nav-link small fw-600" :class="{ active: tab === item.key }" @click="tab = item.key">
            <i :class="item.icon" class="me-1"></i>{{ item.label }}
          </button>
        </li>
      </ul>

      <div v-if="tab === 'notes'">
        <GpEmpty v-if="!notes.length" icon="bi bi-journal-text" message="No notes yet. They appear automatically after lessons." />
        <div v-else class="row g-3">
          <div v-for="note in notes" :key="note.id" class="col-md-6">
            <div class="gp-card p-4">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <strong class="small">{{ note.subject_name || 'Study Notes' }}</strong>
                <span class="text-muted" style="font-size:.7rem">{{ timeAgo(note.lesson_date || note.start_time) }}</span>
              </div>
              <div class="text-muted small mb-3" style="max-height:100px;overflow:hidden">{{ note.ai_summary }}</div>
              <button class="btn btn-sm btn-gp-outline w-100" @click="openNote(note)">View Full Notes</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="tab === 'flashcards'">
        <div class="mb-3 d-flex gap-2 flex-wrap align-items-center">
          <input v-model="generationTopic" class="form-control form-control-sm" placeholder="Topic for new flashcards…" style="max-width:260px" />
          <button class="btn btn-sm btn-gp" :disabled="generating || !generationTopic.trim()" @click="generateFlashcards">
            <span v-if="generating" class="spinner-border spinner-border-sm me-1"></span>Generate Flashcards
          </button>
          <select class="form-select form-select-sm" v-model="fcFilter" style="width:auto">
            <option value="">All Subjects</option>
            <option v-for="subject in subjectList" :key="subject" :value="subject">{{ subject }}</option>
          </select>
        </div>
        <GpEmpty v-if="!filteredCards.length" icon="bi bi-card-text" message="No flashcards yet." />
        <FlashcardDeck v-else :cards="filteredCards" />
      </div>

      <div v-if="tab === 'quiz'">
        <div class="mb-3 d-flex gap-2 flex-wrap align-items-center">
          <input v-model="generationTopic" class="form-control form-control-sm" placeholder="Topic for a new quiz…" style="max-width:260px" />
          <button class="btn btn-sm btn-gp" :disabled="generating || !generationTopic.trim()" @click="generateQuiz">
            <span v-if="generating" class="spinner-border spinner-border-sm me-1"></span>Generate Quiz
          </button>
          <select class="form-select form-select-sm" v-model="quizFilter" style="width:auto">
            <option value="">All Subjects</option>
            <option v-for="subject in subjectList" :key="subject" :value="subject">{{ subject }}</option>
          </select>
        </div>
        <GpEmpty v-if="!filteredQuiz.length" icon="bi bi-patch-question" message="No quizzes yet." />
        <QuizWidget v-else :questions="filteredQuiz" />
      </div>

      <div v-if="tab === 'progress'">
        <GpEmpty v-if="!progress.length" icon="bi bi-graph-up-arrow" message="Complete lessons to build your progress report." />
        <div v-else class="row g-3">
          <div v-for="item in progress" :key="item.subject_id" class="col-md-6">
            <div class="gp-card p-4">
              <div class="d-flex justify-content-between mb-2"><strong>{{ item.subject_name }}</strong><span class="text-gp-primary fw-700">{{ item.lessons_completed }} lessons</span></div>
              <div class="small text-muted mb-2">Score: {{ item.score_after || 0 }}%</div>
              <div class="gp-progress" style="height:8px"><div class="gp-progress-bar" :style="`width:${Math.min(100, Math.max(0, item.score_after || 0))}%`"></div></div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="tab === 'favourites'">
        <GpEmpty v-if="!favourites.length" icon="bi bi-heart" message="No favourite tutors yet." action-label="Browse Tutors" action-to="/tutors" />
        <div v-else class="row g-3">
          <div v-for="tutor in favourites" :key="tutor.id" class="col-md-6 col-lg-4">
            <TutorCard :tutor="tutor" :is-fav="true" @select="openTutor" @fav="removeFav" />
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="noteModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content" v-if="activeNote">
          <div class="modal-header"><h5 class="modal-title fw-700">{{ activeNote.subject_name }} — Notes</h5><button class="btn-close" data-bs-dismiss="modal"></button></div>
          <div class="modal-body">
            <div class="gp-card p-3 mb-4"><p class="small mb-0 text-muted">{{ activeNote.ai_summary }}</p></div>
            <FlashcardDeck v-if="activeNote.ai_flashcards?.length" :cards="activeNote.ai_flashcards" class="mb-4" />
            <QuizWidget v-if="activeNote.ai_quiz?.length" :questions="activeNote.ai_quiz" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Modal } from 'bootstrap'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiGet, apiPost } from '@/utils/api'
import { timeAgo } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty from '@/components/common/GpEmpty.vue'
import StatCard from '@/components/common/StatCard.vue'
import TutorCard from '@/components/tutor/TutorCard.vue'
import FlashcardDeck from '@/components/student/FlashcardDeck.vue'
import QuizWidget from '@/components/student/QuizWidget.vue'

const auth = useAuthStore()
const route = useRoute()
const loading = ref(true)
const tab = ref(route.name === 'assessments' ? 'quiz' : 'notes')
const notes = ref([])
const flashcards = ref([])
const quizzes = ref([])
const favourites = ref([])
const progress = ref([])
const fcFilter = ref('')
const quizFilter = ref('')
const generationTopic = ref('')
const generating = ref(false)
const activeNote = ref(null)
const stats = ref({ completed: 0, hours: '0', subjects: 0 })

const tabs = [
  { key: 'notes', label: 'Notes & Summaries', icon: 'bi bi-journal-richtext' },
  { key: 'flashcards', label: 'Flashcards', icon: 'bi bi-card-text' },
  { key: 'quiz', label: 'Practice Quizzes', icon: 'bi bi-patch-question' },
  { key: 'progress', label: 'Progress Report', icon: 'bi bi-graph-up-arrow' },
  { key: 'favourites', label: 'Favourite Tutors', icon: 'bi bi-heart' },
]

const subjectList = computed(() => [...new Set(notes.value.map(note => note.subject_name).filter(Boolean))])
const filteredCards = computed(() => fcFilter.value ? flashcards.value.filter(card => card.subject === fcFilter.value) : flashcards.value)
const filteredQuiz = computed(() => quizFilter.value ? quizzes.value.filter(quiz => quiz.subject === quizFilter.value) : quizzes.value)

function openNote(note) { activeNote.value = note; new Modal(document.getElementById('noteModal')).show() }
function openTutor(tutor) { window.location.href = `/tutors/${tutor.id}` }
async function removeFav(tutor) { await apiPost(`/tutors/${tutor.id}/favourite/`); favourites.value = favourites.value.filter(item => item.id !== tutor.id) }

async function generateFlashcards() {
  generating.value = true
  try {
    const { data } = await apiPost('/ai/generate-flashcards/', { topic: generationTopic.value, subject: fcFilter.value })
    flashcards.value.push(...(data.cards || []).map(card => ({ ...card, subject: fcFilter.value || 'General' })))
    tab.value = 'flashcards'
  } finally { generating.value = false }
}

async function generateQuiz() {
  generating.value = true
  try {
    const { data } = await apiPost('/ai/generate-quiz/', { topic: generationTopic.value, subject: quizFilter.value })
    quizzes.value.push(...(data.questions || []).map(question => ({ ...question, subject: quizFilter.value || 'General' })))
    tab.value = 'quiz'
  } finally { generating.value = false }
}

onMounted(async () => {
  try {
    const [lessonsResponse, favouritesResponse, progressResponse] = await Promise.all([
      apiGet('/scheduling/lessons/'),
      apiGet('/tutors/favourites/'),
      apiGet('/ai/progress/'),
    ])
    const completed = (lessonsResponse.data?.results || []).filter(lesson => lesson.status === 'completed')
    stats.value = {
      completed: completed.length,
      hours: (completed.reduce((sum, lesson) => sum + (lesson.duration_minutes || 0), 0) / 60).toFixed(1),
      subjects: new Set(completed.map(lesson => lesson.subject_name).filter(Boolean)).size,
    }
    notes.value = completed.filter(lesson => lesson.ai_summary)
    flashcards.value = completed.flatMap(lesson => (lesson.ai_flashcards || []).map(card => ({ ...card, subject: lesson.subject_name })))
    quizzes.value = completed.flatMap(lesson => (lesson.ai_quiz || []).map(quiz => ({ ...quiz, subject: lesson.subject_name })))
    favourites.value = favouritesResponse.data?.results || []
    progress.value = progressResponse.data?.results || []
  } finally { loading.value = false }
})
</script>
