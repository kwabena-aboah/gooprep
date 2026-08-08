<template>
  <div>
    <AppNavbar @toggle-sidebar="() => {}" />
    <div class="py-5" style="background:linear-gradient(135deg,#111,#1a0800)">
      <div class="container text-center py-4">
        <h1 class="text-white fw-800 mb-2">Plans & Pricing</h1>
        <p class="text-white-50">Start free — upgrade when you're ready</p>
        <div class="d-inline-flex gap-2 mt-3 p-1 rounded-pill" style="background:rgba(255,255,255,.1)">
          <button class="btn btn-sm rounded-pill px-4" :class="billing==='monthly'?'btn-gp':'text-white-50'" @click="billing='monthly'">Monthly</button>
          <button class="btn btn-sm rounded-pill px-4" :class="billing==='annual'?'btn-gp':'text-white-50'" @click="billing='annual'">Annual <span class="badge bg-success ms-1">-20%</span></button>
        </div>
      </div>
    </div>

    <div class="container py-5">
      <div class="row g-4 justify-content-center mb-5">
        <div v-for="plan in plans" :key="plan.name" class="col-md-6 col-lg-4">
          <div class="plan-card" :class="{ featured: plan.featured }">
            <div v-if="plan.featured" class="text-center mb-3"><span class="plan-badge"><i class="bi bi-star-fill me-1"></i>Most Popular</span></div>
            <h4 class="fw-800 mb-1">{{ plan.name }}</h4>
            <p class="text-muted small mb-3">{{ plan.desc }}</p>
            <div class="mb-4"><span class="fw-800" style="font-size:2.5rem">GHS {{ billing==='annual'?plan.annualPrice:plan.monthlyPrice }}</span><span class="text-muted small">/month</span></div>
            <div class="mb-4"><div v-for="f in plan.features" :key="f.label" class="d-flex align-items-start gap-2 mb-2"><i class="bi mt-1 flex-shrink-0" :class="f.included?'bi-check-circle-fill text-success':'bi-x-circle text-muted'"></i><span class="small" :class="f.included?'':'text-muted'">{{ f.label }}</span></div></div>
            <button v-if="plan.name === 'Pro'" class="btn mt-auto w-100 py-2" :class="plan.featured?'btn-gp':'btn-gp-outline'" @click="subscribe(plan)" :disabled="subscribing === plan.name"><span v-if="subscribing === plan.name" class="spinner-border spinner-border-sm me-1"></span>{{ subscribing === plan.name ? 'Starting…' : plan.cta }}</button>
            <RouterLink v-else :to="plan.cta_link" class="btn mt-auto w-100 py-2" :class="plan.featured?'btn-gp':'btn-gp-outline'">{{ plan.cta }}</RouterLink>
          </div>
        </div>
      </div>

      <div class="gp-card p-4">
        <h4 class="fw-800 text-center mb-4">Full Feature Comparison</h4>
        <div class="table-responsive"><table class="gp-table text-center"><thead><tr><th class="text-start">Feature</th><th v-for="p in plans" :key="p.name">{{ p.name }}</th></tr></thead>
          <tbody><tr v-for="row in comparisonRows" :key="row.label"><td class="text-start small fw-600">{{ row.label }}</td><td v-for="p in plans" :key="p.name" class="small"><template v-if="row[p.name] === true"><i class="bi bi-check-circle-fill text-success"></i></template><template v-else-if="row[p.name] === false"><i class="bi bi-x-circle text-muted"></i></template><template v-else>{{ row[p.name] }}</template></td></tr></tbody></table></div>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { apiPost } from '@/utils/api'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const billing = ref('monthly')
const router = useRouter()
const auth = useAuthStore()
const notifStore = useNotifStore()
const subscribing = ref('')
const plans = [
  { name:'Free', desc:'Perfect for getting started', featured:false, monthlyPrice:0, annualPrice:0, cta:'Get Started', cta_link:'/register', features:[
    {label:'2 lessons/month',included:true},{label:'1:1 tutor sessions',included:true},{label:'AI assistant (5 queries/day)',included:true},{label:'Lesson recordings',included:false},{label:'AI summaries & flashcards',included:false},{label:'Group classes',included:false},
  ]},
  { name:'Pro', desc:'For serious learners', featured:true, monthlyPrice:89, annualPrice:71, cta:'Start Pro', cta_link:'/register', features:[
    {label:'Unlimited lessons',included:true},{label:'1:1 tutor sessions',included:true},{label:'AI assistant (unlimited)',included:true},{label:'All lesson recordings',included:true},{label:'AI summaries & flashcards',included:true},{label:'Group classes',included:true},
  ]},
  { name:'Institution', desc:'For schools & organisations', featured:false, monthlyPrice:499, annualPrice:399, cta:'Start Institution', cta_link:'/subscription', features:[
    {label:'Unlimited lessons',included:true},{label:'Bulk student enrolment',included:true},{label:'AI assistant (unlimited)',included:true},{label:'All lesson recordings',included:true},{label:'Progress reporting',included:true},{label:'Dedicated account manager',included:true},
  ]},
]
const comparisonRows = [
  {label:'Lessons per month',Free:'2',Pro:'Unlimited',Institution:'Unlimited'},
  {label:'AI Study Assistant',Free:'5/day',Pro:true,Institution:true},
  {label:'Lesson Recordings',Free:false,Pro:true,Institution:true},
  {label:'Flashcards & Quizzes',Free:false,Pro:true,Institution:true},
  {label:'Group Classes',Free:false,Pro:true,Institution:true},
  {label:'WhatsApp Reminders',Free:true,Pro:true,Institution:true},
  {label:'Priority Support',Free:false,Pro:true,Institution:true},
  {label:'Bulk Enrolment',Free:false,Pro:false,Institution:true},
  {label:'Progress Reports',Free:false,Pro:false,Institution:true},
]
async function subscribe(plan) {
  if (!auth.isAuthenticated) { router.push({name:'login',query:{next:'/subscription'}}); return }
  subscribing.value = plan.name
  try {
    const { data } = await apiPost('/payments/subscriptions/', { plan: plan.name.toLowerCase(), billing_cycle: billing.value })
    if (!data.authorization_url) throw new Error(data.error || 'Could not start subscription payment.')
    window.location.assign(data.authorization_url)
  } catch (error) {
    notifStore.toast(error.response?.data?.error || error.message || 'Subscription payment failed.', 'error')
  } finally { subscribing.value = '' }
}
</script>
