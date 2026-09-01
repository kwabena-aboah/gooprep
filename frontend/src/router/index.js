import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const routes=[
  {path:'/',name:'home',component: () => import('@/views/pages/HomeView.vue')},
  {path:'/login',name:'login',component: () => import('@/views/auth/LoginView.vue'),meta:{guest:true}},
  {path:'/register',name:'register',component: () => import('@/views/auth/RegisterView.vue'),meta:{guest:true}},
  {path:'/forgot-password',name:'forgot',component: () => import('@/views/auth/ForgotPasswordView.vue'),meta:{guest:true}},
  {path:'/reset-password',name:'reset',component: () => import('@/views/auth/ResetPasswordView.vue'),meta:{guest:true}},
  {path:'/verify-email',name:'verify-email',component: () => import('@/views/auth/VerifyEmailView.vue')},
  {path:'/how-it-works',name:'how-it-works',component: () => import('@/views/pages/HowItWorksView.vue')},
  {path:'/about',name:'about',component: () => import('@/views/pages/AboutView.vue')},
  {path:'/faq',name:'faq',component: () => import('@/views/pages/FaqView.vue')},
  {path:'/subscription',redirect:'/dashboard'},
  {path:'/institution-onboarding',name:'institution-onboarding',component: () => import('@/views/institutions/InstitutionOnboardingView.vue'),meta:{auth:true,role:'institution'}},
  {path:'/institution',name:'institution',component: () => import('@/views/institutions/InstitutionView.vue'),meta:{auth:true,role:'institution'}},
  {path:'/admin/institutions',name:'admin-institutions',component: () => import('@/views/admin/InstitutionApprovalsView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/privacy',name:'privacy',component: () => import('@/views/pages/StaticPageView.vue'),props:{pageType:'privacy'}},
  {path:'/terms',name:'terms',component: () => import('@/views/pages/StaticPageView.vue'),props:{pageType:'terms'}},
  {path:'/ip-policy',name:'ip-policy',component: () => import('@/views/pages/StaticPageView.vue'),props:{pageType:'ip_policy'}},
  {path:'/cookie-policy',name:'cookie',component: () => import('@/views/pages/StaticPageView.vue'),props:{pageType:'cookie'}},
  {path:'/refund-policy',name:'refund',component: () => import('@/views/pages/StaticPageView.vue'),props:{pageType:'refund'}},
  {path:'/tutors',name:'tutor-search',component: () => import('@/views/tutors/TutorSearchView.vue')},
  {path:'/tutors/:id',name:'tutor-profile',component: () => import('@/views/tutors/TutorProfileView.vue')},
  {path:'/tutor/:slug',name:'tutor-public-profile',component: () => import('@/views/tutors/TutorProfileView.vue')},
  {path:'/group-classes',name:'group-classes',component: () => import('@/views/students/GroupClassesView.vue')},
  {path:'/student-onboarding',name:'student-onboarding',component: () => import('@/views/students/StudentOnboardingView.vue'),meta:{auth:true,role:'student'}},
  {path:'/dashboard',name:'dashboard',component: () => import('@/views/dashboard/DashboardView.vue'),meta:{auth:true}},
  {path:'/profile',name:'profile',component: () => import('@/views/auth/ProfileView.vue'),meta:{auth:true}},
  {path:'/settings',name:'settings',component: () => import('@/views/auth/ProfileView.vue'),meta:{auth:true}},
  {path:'/notifications',name:'notifications',component: () => import('@/views/auth/NotificationsView.vue'),meta:{auth:true}},
  {path:'/messages',name:'messages',component: () => import('@/views/messaging/MessagesView.vue'),meta:{auth:true}},
  {path:'/payments',name:'payments',component: () => import('@/views/payments/PaymentsView.vue'),meta:{auth:true}},
  {path:'/payments/verify',name:'payment-verify',component: () => import('@/views/payments/PaymentVerificationView.vue')},
  {path:'/achievements',name:'achievements',component: () => import('@/views/dashboard/AchievementsView.vue'),meta:{auth:true}},
  {path:'/leaderboard',name:'leaderboard',component: () => import('@/views/dashboard/AchievementsView.vue'),meta:{auth:true}},
  {path:'/lessons',name:'lessons',component: () => import('@/views/scheduling/LessonsView.vue'),meta:{auth:true}},
  {path:'/lessons/:id/join',name:'lesson-join',component: () => import('@/views/scheduling/LessonRoomView.vue'),meta:{auth:true}},
  {path:'/lessons/:id/reschedule',name:'reschedule',component: () => import('@/views/scheduling/RescheduleView.vue'),meta:{auth:true}},
  {path:'/learning',name:'learning',component: () => import('@/views/students/LearningView.vue'),meta:{auth:true,role:'student'}},
  {path:'/knowledge-base',name:'knowledge-base',component: () => import('@/views/students/LearningView.vue'),meta:{auth:true,role:'student'}},
  {path:'/assessments',name:'assessments',component: () => import('@/views/students/LearningView.vue'),meta:{auth:true,role:'student'}},
  {path:'/tutor-onboarding',name:'onboarding',component: () => import('@/views/tutors/OnboardingView.vue'),meta:{auth:true,role:'tutor'}},
  {path:'/availability',name:'availability',component: () => import('@/views/tutors/AvailabilityView.vue'),meta:{auth:true,role:'tutor'}},
  {path:'/earnings',name:'earnings',component: () => import('@/views/tutors/EarningsView.vue'),meta:{auth:true,role:'tutor'}},
  {path:'/my-students',name:'my-students',component: () => import('@/views/tutors/MyStudentsView.vue'),meta:{auth:true,role:'tutor'}},
  {path:'/storefront',name:'my-storefront',component: () => import('@/views/tutors/StorefrontView.vue'),meta:{auth:true,role:'tutor'}},
  {path:'/admin',name:'admin',component: () => import('@/views/admin/AdminDashboardView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/tutors',name:'admin-tutors',component: () => import('@/views/admin/TutorApprovalsView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/users',name:'admin-users',component: () => import('@/views/admin/UsersView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/referrals',name:'admin-referrals',component: () => import('@/views/admin/ReferralsView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/students',name:'admin-students',component: () => import('@/views/admin/StudentApprovalsView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/revenue',name:'admin-revenue',component: () => import('@/views/admin/RevenueView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/disputes',name:'admin-disputes',component: () => import('@/views/admin/DisputesView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/bbb',name:'admin-bbb',component: () => import('@/views/admin/BbbRoomsView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/moderation',name:'admin-mod',component: () => import('@/views/admin/ModerationView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/settings',name:'admin-settings',component: () => import('@/views/admin/SiteSettingsView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/admin/exports',name:'admin-exports',component: () => import('@/views/admin/ExportsView.vue'),meta:{auth:true,role:'admin'}},
  {path:'/:pathMatch(.*)*',name:'not-found',redirect:'/'},
]
// const router=createRouter({history:createWebHistory('/demo/'),routes,scrollBehavior:()=>({top:0,behavior:'smooth'})}) // sub directory config
const router=createRouter({history:createWebHistory(''),routes,scrollBehavior:()=>({top:0,behavior:'smooth'})})
router.beforeEach((to,from,next)=>{
  const auth=useAuthStore()
  if(to.meta.guest&&auth.isAuthenticated)return next({name:'dashboard'})
  if(to.meta.auth&&!auth.isAuthenticated)return next({name:'login',query:{next:to.fullPath}})
  if(to.meta.role&&auth.user?.role!==to.meta.role&&auth.user?.role!=='admin')return next({name:'dashboard'})
  next()
})
export default router
