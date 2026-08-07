<template>
  <div>
    <AppNavbar @toggle-sidebar="()=>{}" />
    <div class="py-5" style="background:linear-gradient(135deg,#111,#1a0800)">
      <div class="container text-center py-4">
        <h1 class="text-white fw-800 mb-2">About Gooprep</h1>
        <p class="text-white-50">Ghana's premier tutoring platform, built for African learners</p>
      </div>
    </div>
    <div class="container py-5">
      <div class="row g-5 align-items-center mb-5">
        <div class="col-lg-6">
          <h2 class="fw-800 mb-3">Our Mission</h2>
          <p class="text-muted" style="line-height:1.8">Gooprep was founded with a simple belief: every Ghanaian student deserves access to a world-class tutor, regardless of location. We connect learners with passionate, verified educators through live virtual classrooms powered by BigBlueButton — all with the convenience of mobile money payments.</p>
          <p class="text-muted" style="line-height:1.8">Built by Sikaba Systems and deeply rooted in the Ghanaian context, Gooprep understands the local curriculum, payment landscape, and cultural needs of our learners.</p>
        </div>
        <div class="col-lg-6">
          <div class="row g-3">
            <div v-for="s in stats" :key="s.label" class="col-6">
              <div class="gp-card p-4 text-center">
                <div class="fw-800 text-gp-primary fs-2">{{ s.value }}</div>
                <div class="text-muted small">{{ s.label }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="row g-4 mb-5">
        <div v-for="v in values" :key="v.title" class="col-md-6 col-lg-3">
          <div class="gp-card p-4 text-center h-100">
            <div class="rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" :style="`width:60px;height:60px;background:${v.color}20`">
              <i :class="v.icon" :style="`color:${v.color};font-size:1.5rem`"></i>
            </div>
            <h5 class="fw-700">{{ v.title }}</h5>
            <p class="text-muted small">{{ v.desc }}</p>
          </div>
        </div>
      </div>
      <div class="gp-card p-4 p-md-5 text-center" style="background:linear-gradient(135deg,#111,#1a0800)">
        <h3 class="text-white fw-800 mb-2">Built in Ghana 🇬🇭</h3>
        <p class="text-white-50 mb-4">Gooprep is proudly built by <strong class="text-white">Sikaba Systems</strong>, a Ghanaian software company dedicated to building digital solutions for the African market.</p>
        <RouterLink to="/register" class="btn btn-gp px-5">Join Gooprep Today</RouterLink>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
const stats = [
  { value:'50K+',  label:'Active Students' },
  { value:'2,000+',label:'Verified Tutors' },
  { value:'100K+', label:'Lessons Completed' },
  { value:'4.9★',  label:'Average Rating' },
]
const values = [
  { icon:'bi bi-shield-check',   color:'#10b981', title:'Verified Tutors',   desc:'Every tutor is background-checked and manually reviewed before going live.' },
  { icon:'bi bi-lock',           color:'#6366f1', title:'Secure Payments',   desc:'All transactions are encrypted and processed via Paystack.' },
  { icon:'bi bi-people',         color:'#e63900', title:'Ghana-First',       desc:'Designed for the Ghanaian curriculum, culture, and payment ecosystem.' },
  { icon:'bi bi-robot',          color:'#f59e0b', title:'AI-Powered',        desc:'AI summaries, flashcards, and quizzes automatically generated from every lesson.' },
]
</script>
