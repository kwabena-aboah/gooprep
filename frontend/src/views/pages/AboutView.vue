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
          <p class="text-muted" style="line-height:1.8">Bridging the Gap Between Students & Educators
            Gooprep is an innovative tutoring and learning marketplace designed to bridge the gap between students and qualified tutors through technology-driven education.

            We provide a platform where students, learners, parents, professionals, and educators can connect seamlessly for online and in-person academic support.</p>
          <p class="text-muted" style="line-height:1.8">Whether preparing for BECE, WASSCE, university exams, professional certifications, or personal skill development, Gooprep provides a reliable ecosystem that supports learning and academic excellence.</p>
        </div>
        <div class="col-lg-6">
          <div class="row g-5 align-items-center mb-5">
            <div class="col-6">
                <h2 class="fw-800 text-gp-primary fs-2">Our Mission</h2>
                <p class="text-muted" style="line-height:1.8">To make quality education accessible and affordable by connecting learners with trusted tutors and educational opportunities through a modern and interactive learning platform.

                We aim to simplify learning experiences while promoting academic excellence, digital learning innovation, and educational empowerment across Ghana and beyond.</p>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="row g-5 align-items-center mb-5">
            <div class="col-lg-6">
              <h2>Our Vision</h2>
              <p class="text-muted" style="line-height:1.8">To become Africa’s leading digital tutoring and educational support platform by building a trusted ecosystem where students and educators can teach, learn, and grow together.</p>
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
        <h3 class="text-white fw-800 mb-2">A Future Where Education Is Accessible, Engaging, and Transformative for Everyone</h3>
        <p class="text-white-50 mb-4">Empowering students. Supporting educators. Building futures. <br> <strong class="text-white">Teach. Learn. Grow</strong></p>
        <RouterLink to="/register" class="btn btn-gp px-5">Join Gooprep Today</RouterLink>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
// const stats = [
//   { value:'50K+',  label:'Active Students' },
//   { value:'2,000+',label:'Verified Tutors' },
//   { value:'100K+', label:'Lessons Completed' },
//   { value:'4.9★',  label:'Average Rating' },
// ]
const values = [
  { icon:'bi bi-shield-check',   color:'#10b981', title:'Teach',   desc:'Connecting students with passionate and qualified educators dedicated to sharing knowledge and guiding learners toward success.' },
  { icon:'bi bi-lock',           color:'#6366f1', title:'Learn',   desc:'Learning should be engaging, personalized, and accessible to everyone regardless of location or background.' },
  { icon:'bi bi-people',         color:'#e63900', title:'Grow',       desc:'Personal, academic, and professional development through quality education, mentorship, and continuous improvement.' },
  // { icon:'bi bi-robot',          color:'#f59e0b', title:'AI-Powered',        desc:'AI summaries, flashcards, and quizzes automatically generated from every lesson.' },
]
</script>
