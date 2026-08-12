<template>
  <div>
    <AppNavbar @toggle-sidebar="()=>{}" />

    <!-- Hero -->
    <section style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0800 50%,#0a0a0a 100%);min-height:90vh;display:flex;align-items:center;padding:5rem 0">
      <div class="container">
        <div class="row align-items-center g-5">
          <div class="col-lg-6">
            <!-- <div class="gp-badge mb-3" style="font-size:.85rem;padding:.4rem 1rem">🇬🇭 Ghana's #1 Tutoring Platform</div> -->
            <h1 class="text-white fw-800 mb-4" style="font-size:clamp(2.2rem,5vw,3.8rem);line-height:1.15">
              Learn From <span style="background:linear-gradient(135deg,var(--gp-red),var(--gp-amber));-webkit-background-clip:text;-webkit-text-fill-color:transparent">Expert Tutors</span><br>Anytime, Anywhere
            </h1>
            <p class="text-white-50 mb-4" style="font-size:1.1rem;line-height:1.7">
              Connect with verified Ghanaian tutors via live BigBlueButton classrooms. Pay securely with MTN MoMo, AirtelTigo, or Telecel Cash.
            </p>
            <div class="d-flex gap-3 flex-wrap mb-5">
              <RouterLink to="/register" class="btn btn-gp btn-lg px-4"><i class="bi bi-rocket-takeoff me-2"></i>Get Started Free</RouterLink>
              <RouterLink to="/tutors" class="btn btn-outline-light btn-lg px-4"><i class="bi bi-search me-2"></i>Browse Tutors</RouterLink>
            </div>
            <!-- <div class="d-flex gap-4 flex-wrap">
              <div class="text-center"><div class="fw-800 text-white fs-4">50K+</div><div class="text-white-50 small">Students</div></div>
              <div class="text-center"><div class="fw-800 text-white fs-4">2,000+</div><div class="text-white-50 small">Tutors</div></div>
              <div class="text-center"><div class="fw-800 text-white fs-4">100K+</div><div class="text-white-50 small">Lessons</div></div>
              <div class="text-center"><div class="fw-800 text-white fs-4">4.9★</div><div class="text-white-50 small">Rating</div></div>
            </div> -->
          </div>
          <div class="col-lg-6 d-none d-lg-block">
            <div class="position-relative">
              <div class="rounded-3 overflow-hidden" style="background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);padding:1.5rem">
                <div class="d-flex align-items-center gap-3 mb-4">
                  <div class="rounded-circle d-flex align-items-center justify-content-center" style="width:48px;height:48px;background:linear-gradient(135deg,var(--gp-red),var(--gp-amber))">
                    <i class="bi bi-camera-video-fill text-white fs-5"></i>
                  </div>
                  <div class="text-white">
                    <div class="fw-700">Live Gooprep Classroom</div>
                    <div class="text-white-50 small">HD Video · Whiteboard · Recording</div>
                  </div>
                  <span class="badge bg-danger ms-auto d-flex align-items-center gap-1">
                    <span class="rounded-circle bg-white d-inline-block" style="width:6px;height:6px;animation:pulse 1s infinite"></span>LIVE
                  </span>
                </div>
                <div v-for="feat in heroFeats" :key="feat.label" class="d-flex align-items-center gap-3 p-3 rounded-3 mb-2" style="background:rgba(255,255,255,.05)">
                  <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" :style="`width:40px;height:40px;background:${feat.color}20`">
                    <i :class="feat.icon" :style="`color:${feat.color};font-size:1.1rem`"></i>
                  </div>
                  <div class="text-white small">{{ feat.label }}</div>
                  <i class="bi bi-check-circle-fill text-success ms-auto"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust bar -->
    <section class="py-3" style="background:#f1f5f9;border-bottom:1px solid var(--gp-border)">
      <div class="container">
        <div class="d-flex justify-content-center align-items-center gap-4 flex-wrap">
          <span class="small text-muted fw-600">Trusted payments:</span>
          <span v-for="p in payments" :key="p" class="badge bg-white border text-dark px-3 py-2">{{ p }}</span>
          <span class="badge bg-success text-white px-3 py-2"><i class="bi bi-shield-check me-1"></i>Paystack Secured</span>
        </div>
      </div>
    </section>

    <!-- Subjects -->
    <!-- <section class="py-5" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="fw-800">Popular Subjects</h2>
          <p class="text-muted">Expert tutors across all major subjects and levels</p>
        </div>
        <div class="row g-3 justify-content-center">
          <div v-for="sub in popularSubjects" :key="sub.name" class="col-6 col-md-3 col-lg-2">
            <RouterLink :to="`/tutors?subject=${sub.slug}`" class="gp-card p-3 text-center d-block text-decoration-none">
              <div class="rounded-circle d-flex align-items-center justify-content-center mx-auto mb-2" :style="`width:52px;height:52px;background:${sub.color}20`">
                <i :class="sub.icon" :style="`color:${sub.color};font-size:1.4rem`"></i>
              </div>
              <div class="fw-600 small text-dark">{{ sub.name }}</div>
              <div class="text-muted" style="font-size:.7rem">{{ sub.count }} tutors</div>
            </RouterLink>
          </div>
        </div>
      </div>
    </section> -->

    <!-- How it works -->
    <section class="py-5">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="fw-800">How Gooprep Works</h2>
          <p class="text-muted">Start learning in minutes</p>
        </div>
        <div class="row g-4">
          <div v-for="(step,i) in steps" :key="i" class="col-md-3 text-center">
            <div class="rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" style="width:72px;height:72px;background:linear-gradient(135deg,var(--gp-red),var(--gp-amber))">
              <i :class="step.icon" class="text-white" style="font-size:1.6rem"></i>
            </div>
            <div class="fw-700 mb-1 fw-800">{{ step.title }}</div>
            <div class="text-muted small">{{ step.desc }}</div>
          </div>
        </div>
        <div class="text-center mt-4">
          <RouterLink to="/how-it-works" class="btn btn-gp">Learn More <i class="bi bi-arrow-right ms-1"></i></RouterLink>
        </div>
      </div>
    </section>

    <!-- Featured tutors -->
    <!-- <section class="py-5">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
          <div><h2 class="fw-800 mb-0">Top Tutors</h2><p class="text-muted small mb-0">Highly rated, verified experts</p></div>
          <RouterLink to="/tutors" class="btn btn-gp-outline btn-sm">View All Tutors</RouterLink>
        </div>
        <div class="row g-3">
          <div v-for="t in featuredTutors" :key="t.id" class="col-md-6 col-lg-3">
            <TutorCard :tutor="t" @select="openTutor" @fav="()=>{}" />
          </div>
        </div>
      </div>
    </section> -->

    <!-- Subscription CTA -->
    <section class="py-5" style="background:linear-gradient(135deg,#111,#1a0800)">
      <div class="container text-center">
        <h2 class="text-white fw-800 mb-2">Start Learning Today</h2>
        <p class="text-white-50 mb-4">Book your first trial lesson from GHS 30 · No subscription required</p>
        <div class="d-flex gap-3 justify-content-center flex-wrap">
          <RouterLink to="/register" class="btn btn-gp btn-lg px-5"><i class="bi bi-rocket-takeoff me-2"></i>Sign Up Free</RouterLink>
          <RouterLink to="/subscription" class="btn btn-outline-light btn-lg px-5">View Plans</RouterLink>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet } from '@/utils/api'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import TutorCard from '@/components/tutor/TutorCard.vue'

const router         = useRouter()
const featuredTutors = ref([])

const payments = ['MTN MoMo','AirtelTigo','Telecel Cash','Visa / Mastercard']
const heroFeats = [
  { icon:'bi bi-camera-video-fill', label:'Live Gooprep Classrooms',    color:'#e63900' },
  { icon:'bi bi-robot',             label:'AI Study Assistant & Summaries',    color:'#6366f1' },
  { icon:'bi bi-cash-coin',         label:'Pay with Mobile Money (GHS)',       color:'#10b981' },
  { icon:'bi bi-shield-check',      label:'Verified & Background-checked',     color:'#f59e0b' },
]
const steps = [
  { icon:'bi bi-search',            title:'Find a Tutor',       desc:'Browse verified tutors by subject, price, and availability' },
  { icon:'bi bi-calendar-plus',     title:'Book a Session',     desc:'Schedule instantly or request — choose your time slot' },
  { icon:'bi bi-phone',             title:'Pay with MoMo',      desc:'Secure payment via MTN MoMo, AirtelTigo, or Telecel Cash' },
  { icon:'bi bi-camera-video-fill', title:'Join the Classroom', desc:'HD video, shared whiteboard, and session recording' },
]
const popularSubjects = [
  { name:'Mathematics',   slug:'mathematics',   icon:'bi bi-calculator',    color:'#e63900', count:320 },
  { name:'Physics',       slug:'physics',        icon:'bi bi-lightning',     color:'#6366f1', count:180 },
  { name:'Chemistry',     slug:'chemistry',      icon:'bi bi-flask',         color:'#10b981', count:150 },
  { name:'English',       slug:'english',        icon:'bi bi-book',          color:'#f59e0b', count:280 },
  { name:'Biology',       slug:'biology',        icon:'bi bi-tree',          color:'#22c55e', count:130 },
  { name:'Accounting',    slug:'accounting',     icon:'bi bi-journal-text',  color:'#3b82f6', count:110 },
  { name:'ICT',           slug:'ict',            icon:'bi bi-laptop',        color:'#8b5cf6', count:200 },
  { name:'French',        slug:'french',         icon:'bi bi-translate',     color:'#ec4899', count:90  },
]

function openTutor(t) { router.push(`/tutors/${t.id}`) }

onMounted(async () => {
  try {
    const { data } = await apiGet('/tutors/', { is_featured: true, page_size: 4, ordering: '-average_rating' })
    featuredTutors.value = data.results || []
  } catch {}
})
</script>

<style>
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
</style>
