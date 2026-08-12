<template>
  <div>
    <AppNavbar @toggle-sidebar="()=>{}" />
    <div class="py-5" style="background:linear-gradient(135deg,#111,#1a0800)">
      <div class="container text-center py-4">
        <h1 class="text-white fw-800 mb-2">Frequently Asked Questions</h1>
        <p class="text-white-50">Everything you need to know about Gooprep</p>
      </div>
    </div>
    <div class="container py-5" style="max-width:800px">
      <div class="d-flex gap-2 mb-4 flex-wrap justify-content-center">
        <button v-for="cat in categories" :key="cat"
                class="btn btn-sm" :class="activeCategory===cat?'btn-gp':'btn-outline-secondary'"
                @click="activeCategory=cat">{{ cat }}</button>
      </div>
      <div class="accordion" id="faqAccordion">
        <div v-for="(faq,i) in filtered" :key="i" class="accordion-item border mb-2 rounded-3 overflow-hidden">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed fw-600" type="button"
                    data-bs-toggle="collapse" :data-bs-target="`#faq${i}`">
              {{ faq.q }}
            </button>
          </h2>
          <div :id="`faq${i}`" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
            <div class="accordion-body text-muted small" style="line-height:1.8">{{ faq.a }}</div>
          </div>
        </div>
      </div>
      <div class="text-center mt-5">
        <p class="text-muted mb-3">Still have questions?</p>
        <a href="mailto:support@gooprep.com" class="btn btn-gp">
          <i class="bi bi-envelope me-2"></i>Contact Support
        </a>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const categories    = ['All','Students','Tutors','Payments','Technical']
const activeCategory = ref('All')
const faqs = [
  { cat:'Students', q:'How do I find a tutor?',           a:'Browse tutors at /tutors, filter by subject, price, and availability. You can also use the AI search to describe what you need.' },
  { cat:'Students', q:'Can I try a tutor before committing?', a:'Yes! Many tutors offer 30-minute trial lessons at a reduced rate. Look for the "Trial available" badge on tutor cards.' },
  { cat:'Students', q:'What happens if a tutor cancels?',  a:'You receive a full refund to your original payment method within 1–3 business days. You can also reschedule at no extra cost.' },
  { cat:'Students', q:'Are sessions recorded?',            a:'Yes, by default sessions are recorded and available in your lesson history within 1 hour of completion.' },
  { cat:'Tutors',   q:'How do I become a tutor?',          a:'Sign up, select "I want to Teach", and complete the onboarding form. Our team reviews applications within 24–48 hours.' },
  { cat:'Tutors',   q:'How much can I earn?',              a:'Tutors set their own rates (GHS 20–200+/hr). Gooprep takes a 20% platform fee. Top tutors earn GHS 3,000–10,000/month.' },
  { cat:'Tutors',   q:'When do I get paid?',               a:'Request a payout anytime (minimum GHS 50). Funds arrive in your MoMo or bank account within 1–2 business days.' },
  { cat:'Payments', q:'What payment methods are accepted?', a:'MTN MoMo, AirtelTigo Money, Telecel Cash, and Visa/Mastercard. All payments are processed by Paystack.' },
  { cat:'Payments', q:'Is my money safe?',                  a:'Yes. Payments are held in escrow and only released to the tutor 24 hours after lesson completion, giving you time to raise disputes.' },
  { cat:'Payments', q:'How do I get a refund?',            a:'Contact support within 48 hours of the lesson. Approved refunds are returned to your original payment method within 3 business days.' },
  { cat:'Technical',q:'What do I need for a lesson?',      a:'A stable internet connection, camera, and microphone. Sessions run in your browser — no downloads needed (Gooprep Virtual Classroom is web-based).' },
  { cat:'Technical',q:'Is there a mobile app?',            a:'Gooprep is fully mobile-responsive and works great on any mobile browser. A dedicated app is coming soon.' },
]

const filtered = computed(() => activeCategory.value === 'All' ? faqs : faqs.filter(f => f.cat === activeCategory.value))
</script>
