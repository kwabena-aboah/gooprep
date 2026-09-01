<template>
  <div>
    <AppNavbar @toggle-sidebar="()=>{}" />

    <header class="about-hero">
      <div class="container py-5">
        <div class="row align-items-center g-5 py-lg-4">
          <div class="col-lg-7">
            <span class="about-eyebrow">WHO WE ARE</span>
            <h1 class="display-3 text-white fw-800 mb-3">Education That<br><span class="about-gradient-text">Transforms Lives</span></h1>
            <p class="lead text-white-50 mb-4">Teach. Learn. Grow.</p>
            <p class="text-white-50 mb-0" style="max-width:600px;line-height:1.8">A trusted learning community connecting students, parents, professionals, and educators through technology-driven education.</p>
          </div>
          <div class="col-lg-5">
            <div class="about-hero-card">
              <i class="bi bi-mortarboard-fill text-gp-primary fs-1 mb-3"></i>
              <div class="h4 text-white fw-700 mb-2">Learning without limits</div>
              <p class="text-white-50 small mb-0">Quality academic support, meaningful connections, and opportunities to grow — wherever you are.</p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main>
      <section class="container py-5">
        <div class="row align-items-center g-5 py-lg-4">
          <div class="col-lg-6">
            <span class="section-kicker">ABOUT GOOPREP</span>
            <h2 class="display-6 fw-800 mb-4">Bridging the Gap Between Students & Educators</h2>
          </div>
          <div class="col-lg-6">
            <p class="text-muted about-copy">Gooprep is an innovative tutoring and learning marketplace designed to bridge the gap between students and qualified tutors through technology-driven education.</p>
            <p class="text-muted about-copy">We provide a platform where students, learners, parents, professionals, and educators can connect seamlessly for online and in-person academic support.</p>
            <p class="text-muted about-copy mb-0">Whether preparing for BECE, WASSCE, university exams, professional certifications, or personal skill development, Gooprep provides a reliable ecosystem that supports learning and academic excellence.</p>
          </div>
        </div>
        <blockquote class="about-quote mt-5 mb-0">“More than just a tutoring platform — a growing educational community focused on empowering learners and creating opportunities for educators.”</blockquote>
      </section>

      <section class="about-soft-section py-5">
        <div class="container">
          <div class="text-center mb-5"><span class="section-kicker">OUR FOUNDATION</span><h2 class="fw-800">Everything We Do Is Built on Three Pillars</h2></div>
          <div class="row g-4">
            <div v-for="pillar in pillars" :key="pillar.title" class="col-md-4">
              <div class="gp-card p-4 h-100 about-feature-card"><div class="about-icon" :style="`background:${pillar.color}18;color:${pillar.color}`">{{ pillar.emoji }}</div><h4 class="fw-800">{{ pillar.title }}</h4><p class="text-muted small mb-0">{{ pillar.desc }}</p></div>
            </div>
          </div>
        </div>
      </section>

      <section class="container py-5">
        <div class="row g-4 py-lg-4">
          <div class="col-lg-6"><div class="about-purpose-card h-100"><span class="section-kicker">OUR PURPOSE</span><h2 class="fw-800 mt-2">Our Mission</h2><p class="text-muted about-copy mb-0">To make quality education accessible and affordable by connecting learners with trusted tutors and educational opportunities through a modern and interactive learning platform.<br><br>We aim to simplify learning experiences while promoting academic excellence, digital learning innovation, and educational empowerment across Ghana and beyond.</p></div></div>
          <div class="col-lg-6"><div class="about-purpose-card h-100 dark-card"><span class="about-eyebrow">THE FUTURE WE’RE BUILDING</span><h2 class="text-white fw-800 mt-2">Our Vision</h2><p class="text-white-50 about-copy mb-0">To become Africa’s leading digital tutoring and educational support platform by building a trusted ecosystem where students and educators can teach, learn, and grow together.</p></div></div>
        </div>
      </section>

      <section class="about-soft-section py-5"><div class="container"><div class="text-center mb-5"><span class="section-kicker">WHAT DRIVES US</span><h2 class="fw-800">Our Core Values</h2></div><div class="row g-4"><div v-for="value in values" :key="value.title" class="col-md-6 col-lg-3"><div class="gp-card p-4 h-100"><div class="about-icon" :style="`background:${value.color}18;color:${value.color}`">{{ value.emoji }}</div><h5 class="fw-800">{{ value.title }}</h5><p class="text-muted small mb-0">{{ value.desc }}</p></div></div></div></div></section>

      <section class="container py-5"><div class="text-center mb-5"><span class="section-kicker">OUR SERVICES</span><h2 class="fw-800">What We Offer</h2></div><div class="row g-3"><div v-for="service in services" :key="service.title" class="col-md-6 col-lg-4"><div class="service-card"><span class="service-emoji">{{ service.emoji }}</span><div><h6 class="fw-800 mb-1">{{ service.title }}</h6><p class="text-muted small mb-0">{{ service.desc }}</p></div></div></div></div></section>

      <section class="container pb-5"><div class="about-cta text-center"><span class="about-eyebrow">OUR COMMITMENT</span><h2 class="text-white fw-800 mt-2 mb-3">A Future Where Education Is Accessible, Engaging, and Transformative for Everyone</h2><p class="text-white-50 mb-4">Empowering students. Supporting educators. Building futures.<br><strong class="text-white">Teach. Learn. Grow.</strong></p><RouterLink to="/register" class="btn btn-gp px-5">Get Started Today <i class="bi bi-arrow-right ms-2"></i></RouterLink></div></section>
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const pillars = [
  { emoji:'🎓', title:'Teach', color:'#e63900', desc:'Connecting students with passionate and qualified educators dedicated to sharing knowledge and guiding learners toward success.' },
  { emoji:'📘', title:'Learn', color:'#6366f1', desc:'Learning should be engaging, personalized, and accessible to everyone regardless of location or background.' },
  { emoji:'🌿', title:'Grow', color:'#10b981', desc:'Personal, academic, and professional development through quality education, mentorship, and continuous improvement.' },
]
const values = [
  { emoji:'⭐', title:'Excellence', color:'#f59e0b', desc:'High-quality educational support and exceptional learning experiences that create positive impact.' },
  { emoji:'♿', title:'Accessibility', color:'#6366f1', desc:'Education should be available to everyone, regardless of location, background, or financial situation.' },
  { emoji:'💡', title:'Innovation', color:'#e63900', desc:'Technology and creative solutions that improve delivery, communication, and engagement.' },
  { emoji:'🤝', title:'Collaboration', color:'#10b981', desc:'Partnerships between students, tutors, schools, and stakeholders create stronger communities.' },
]
const services = [
  { emoji:'💻', title:'Online Tutoring Sessions', desc:'Learn from anywhere with certified tutors and flexible scheduling.' },
  { emoji:'👥', title:'In-Person Tutoring Support', desc:'Face-to-face sessions with qualified tutors near you.' },
  { emoji:'✏️', title:'Exam Preparation Classes', desc:'BECE, WASSCE, university exams, and professional certifications.' },
  { emoji:'🔁', title:'Remedial & Academic Support', desc:'Targeted support to help students catch up and build confidence.' },
  { emoji:'🏆', title:'International Competition Training', desc:'Coaching for local and global academic competitions.' },
  { emoji:'💬', title:'Gooprep Messenger', desc:'Built-in student-tutor communication for seamless lesson delivery.' },
]
</script>

<style scoped>
.about-hero,.about-cta{background:linear-gradient(135deg,#0a0a0a,#1a0800 55%,#0a0a0a)}
.about-hero{min-height:520px;display:flex;align-items:center}.about-eyebrow,.section-kicker{font-size:.75rem;font-weight:800;letter-spacing:.14em}.about-eyebrow{color:#f5a800}.section-kicker{color:var(--gp-red)}.about-gradient-text{background:linear-gradient(135deg,var(--gp-red),var(--gp-amber));-webkit-background-clip:text;-webkit-text-fill-color:transparent}.about-hero-card{padding:2rem;border:1px solid rgba(255,255,255,.14);border-radius:1rem;background:rgba(255,255,255,.06)}.about-soft-section{background:#fff8f5}.about-copy{line-height:1.8}.about-quote{border-left:4px solid var(--gp-red);padding:1rem 1.5rem;color:#64748b;font-style:italic;line-height:1.7}.about-feature-card{border:0}.about-icon{width:54px;height:54px;display:grid;place-items:center;border-radius:1rem;font-size:1.7rem;margin-bottom:1.25rem}.about-purpose-card{padding:2rem;border-radius:1rem;background:#fff8f5}.dark-card{background:linear-gradient(135deg,#111,#1a0800)}.service-card{height:100%;display:flex;gap:1rem;align-items:flex-start;padding:1.25rem;border:1px solid var(--gp-border);border-radius:.85rem;background:#fff}.service-emoji{font-size:1.7rem}.about-cta{padding:3.5rem 2rem;border-radius:1rem}.about-cta h2{max-width:760px;margin-inline:auto}@media(max-width:576px){.about-hero{min-height:auto}.about-hero h1{font-size:2.7rem}.about-cta{padding:2.5rem 1.25rem}}
</style>
