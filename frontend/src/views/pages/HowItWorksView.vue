<template>
  <div>
    <AppNavbar @toggle-sidebar="()=>{}" />
    <div class="py-5" style="background:linear-gradient(135deg,#111,#1a0800)">
      <div class="container text-center py-4">
        <h1 class="text-white fw-800 mb-2">How Gooprep Works</h1>
        <p class="text-white-50">From sign-up to your first lesson in minutes</p>
      </div>
    </div>
    <div class="container py-5">
      <!-- For students -->
      <div class="row align-items-center g-5 mb-5">
        <div class="col-lg-6">
          <div class="gp-badge mb-3">For Students</div>
          <h2 class="fw-800 mb-4">Start Learning Today</h2>
          <div v-for="(s,i) in studentSteps" :key="i" class="d-flex gap-3 mb-4">
            <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 fw-800 text-white" style="width:48px;height:48px;min-width:48px;background:linear-gradient(135deg,var(--gp-red),var(--gp-amber));font-size:1.1rem">{{ i+1 }}</div>
            <div><h5 class="fw-700 mb-1">{{ s.title }}</h5><p class="text-muted small mb-0">{{ s.desc }}</p></div>
          </div>
          <RouterLink to="/register" class="btn btn-gp mt-2"><i class="bi bi-mortarboard me-2"></i>Start Learning</RouterLink>
        </div>
        <div class="col-lg-6">
          <div class="gp-card p-4" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)">
            <div v-for="f in studentFeats" :key="f.label" class="d-flex align-items-start gap-3 mb-3">
              <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" :style="`width:40px;height:40px;background:${f.color}20`">
                <i :class="f.icon" :style="`color:${f.color};font-size:1.1rem`"></i>
              </div>
              <div><div class="fw-600">{{ f.label }}</div><div class="text-muted small">{{ f.desc }}</div></div>
            </div>
          </div>
        </div>
      </div>

      <hr class="my-5" />

      <!-- For tutors -->
      <div class="row align-items-center g-5 mb-5">
        <div class="col-lg-6 order-lg-2">
          <div class="gp-badge mb-3">For Tutors</div>
          <h2 class="fw-800 mb-4">Earn Teaching Online</h2>
          <div v-for="(s,i) in tutorSteps" :key="i" class="d-flex gap-3 mb-4">
            <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 fw-800 text-white" style="width:48px;height:48px;min-width:48px;background:linear-gradient(135deg,var(--gp-red),var(--gp-amber));font-size:1.1rem">{{ i+1 }}</div>
            <div><h5 class="fw-700 mb-1">{{ s.title }}</h5><p class="text-muted small mb-0">{{ s.desc }}</p></div>
          </div>
          <RouterLink to="/register?role=tutor" class="btn btn-gp mt-2"><i class="bi bi-person-video3 me-2"></i>Become a Tutor</RouterLink>
        </div>
        <div class="col-lg-6 order-lg-1">
          <div class="gp-card p-4" style="background:linear-gradient(135deg,#0a0a0a,#1a0800)">
            <div class="text-center text-white mb-3">
              <div class="fw-800 fs-1" style="color:var(--gp-amber)">GHS 40–120</div>
              <div class="text-white-50">per hour · you keep 80%</div>
            </div>
            <div v-for="f in tutorFeats" :key="f" class="d-flex align-items-center gap-2 mb-2 text-white-50 small">
              <i class="bi bi-check-circle-fill text-success"></i>{{ f }}
            </div>
          </div>
        </div>
      </div>

      <!-- FAQ snippet -->
      <div class="text-center mt-5">
        <h3 class="fw-800 mb-3">Still have questions?</h3>
        <RouterLink to="/faq" class="btn btn-gp-outline me-2">Read FAQ</RouterLink>
        <a href="mailto:support@gooprep.com" class="btn btn-outline-secondary">Contact Support</a>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const studentSteps = [
  { title:'Create a free account',   desc:'Sign up in under 2 minutes as a student or institution.' },
  { title:'Browse & filter tutors',  desc:'Search by subject, price, rating, or availability.' },
  { title:'Book your first session', desc:'Choose a time, pay securely with mobile money or card.' },
  { title:'Join the classroom',      desc:'Click Join to enter your live Gooprep Virtual Room session.' },
]
const studentFeats = [
  { icon:'bi bi-search',            color:'#e63900', label:'Smart Tutor Matching',  desc:'AI-powered recommendations based on your goals' },
  { icon:'bi bi-camera-video-fill', color:'#6366f1', label:'Live HD Classrooms',   desc:'Gooprep Virtual Room with whiteboard and screen sharing' },
  { icon:'bi bi-robot',             color:'#10b981', label:'AI Study Assistant',   desc:'Instant homework help and lesson summaries' },
  { icon:'bi bi-trophy',            color:'#f59e0b', label:'Gamified Learning',    desc:'Earn XP, badges, and maintain streaks' },
]
const tutorSteps = [
  { title:'Apply as a tutor', desc:'Fill in your profile, subjects, and hourly rate.' },
  { title:'Get verified',     desc:'Our team reviews your application within 24–48 hours.' },
  { title:'Set availability', desc:'Choose your weekly teaching schedule and go live.' },
  { title:'Earn & get paid',  desc:'Receive payouts to MoMo or bank within 2 business days.' },
]
const tutorFeats = [
  'Keep 80% of every lesson fee','Instant or scheduled bookings',
  'Automatic lesson recordings','AI-generated lesson summaries',
  'WhatsApp notifications','Payout to MTN MoMo or bank',
]
</script>
