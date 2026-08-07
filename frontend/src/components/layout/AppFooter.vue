<template>
  <footer style="background:#0a0a0a;color:#94a3b8;padding:4rem 0 1.5rem">
    <div class="container">
      <div class="row g-4 mb-4">
        <div class="col-lg-4">
          <img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:44px;margin-bottom:1rem" />
          <p class="small opacity-75">Ghana's leading tutoring platform. Expert tutors, live BigBlueButton classrooms, AI-powered learning, and mobile money payments.</p>
          <div class="d-flex gap-3 mt-3">
            <a href="#" class="text-muted fs-5"><i class="bi bi-facebook"></i></a>
            <a href="#" class="text-muted fs-5"><i class="bi bi-twitter-x"></i></a>
            <a href="#" class="text-muted fs-5"><i class="bi bi-instagram"></i></a>
            <a href="#" class="text-muted fs-5"><i class="bi bi-linkedin"></i></a>
          </div>
        </div>
        <div class="col-6 col-lg-2">
          <h6 style="color:#fff;font-weight:700;margin-bottom:1rem">Platform</h6>
          <RouterLink to="/tutors" class="footer-link">Find Tutors</RouterLink>
          <RouterLink to="/group-classes" class="footer-link">Group Classes</RouterLink>
          <RouterLink to="/subscription" class="footer-link">Pricing</RouterLink>
        </div>
        <div class="col-6 col-lg-2">
          <h6 style="color:#fff;font-weight:700;margin-bottom:1rem">Company</h6>
          <RouterLink to="/about" class="footer-link">About Us</RouterLink>
          <RouterLink to="/how-it-works" class="footer-link">How It Works</RouterLink>
          <RouterLink to="/faq" class="footer-link">FAQ</RouterLink>
        </div>
        <div class="col-6 col-lg-2">
          <h6 style="color:#fff;font-weight:700;margin-bottom:1rem">Legal</h6>
          <RouterLink to="/privacy" class="footer-link">Privacy Policy</RouterLink>
          <RouterLink to="/terms" class="footer-link">Terms of Service</RouterLink>
          <RouterLink to="/cookie-policy" class="footer-link">Cookies</RouterLink>
          <RouterLink to="/refund-policy" class="footer-link">Refunds</RouterLink>
        </div>
        <div class="col-6 col-lg-2">
          <h6 style="color:#fff;font-weight:700;margin-bottom:1rem">Support</h6>
          <a href="mailto:support@gooprep.com" class="footer-link">Contact Us</a>
          <RouterLink to="/faq" class="footer-link">Help Centre</RouterLink>
        </div>
      </div>
      <hr style="border-color:rgba(255,255,255,.1)">
      <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
        <span class="small opacity-50">© 2025 Gooprep. Made with ❤️ in Ghana 🇬🇭</span>
        <div class="d-flex gap-2">
          <span class="badge bg-success small"><i class="bi bi-shield-check me-1"></i>Paystack Secured</span>
          <span class="badge bg-primary small"><i class="bi bi-camera-video me-1"></i>BigBlueButton</span>
        </div>
      </div>
    </div>
  </footer>
</template>
<style scoped>
.footer-link{color:#64748b;font-size:.875rem;display:block;margin-bottom:.4rem;transition:color .2s;text-decoration:none}
.footer-link:hover{color:#f5a800}
</style>
