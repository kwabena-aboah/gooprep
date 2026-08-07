<template>
  <div>
    <template v-if="isPublicLayout">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </Transition>
      </RouterView>
    </template>
    <template v-else>
      <AppNavbar @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <div class="gp-layout">
        <AppSidebar :open="sidebarOpen" @close="sidebarOpen = false" />
        <main class="gp-main" :class="{ 'no-sidebar': !sidebarOpen && isMobile }">
          <RouterView v-slot="{ Component }">
            <Transition name="page" mode="out-in">
              <component :is="Component" :key="$route.path" />
            </Transition>
          </RouterView>
        </main>
      </div>
      <RouterLink to="/messages" class="gp-fab" title="Messages">
        <i class="bi bi-chat-dots-fill"></i>
        <span class="gp-fab-badge" v-if="notifStore.unreadCount > 0">{{ notifStore.unreadCount }}</span>
      </RouterLink>
    </template>
    <AppToasts />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'

import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppToasts from '@/components/layout/AppToasts.vue'

const route = useRoute()

const authStore = useAuthStore()
const notifStore = useNotifStore()

const sidebarOpen = ref(window.innerWidth >= 992)
const isMobile = ref(window.innerWidth < 992)

const PUBLIC_ROUTES = [
  'home',
  'login',
  'register',
  'forgot',
  'reset',
  'how-it-works',
  'about',
  'faq',
  'subscription',
  'privacy',
  'terms',
  'ip-policy',
  'cookie',
  'refund',
  'tutor-search',
  'tutor-profile',
  'tutor-storefront',
  'group-classes',
  'lesson-join',
]

const isPublicRoute = computed(() =>
  PUBLIC_ROUTES.includes(route.name)
)

const isPublicLayout = computed(() =>
  isPublicRoute.value || !authStore.isAuthenticated
)

const handleResize = () => {
  isMobile.value = window.innerWidth < 992

  if (!isMobile.value) {
    sidebarOpen.value = true
  }
}

const initializeNotifications = async () => {
  if (!authStore.isAuthenticated) return

  try {
    await notifStore.fetchNotifs()
    notifStore.connectWS()
  } catch (err) {
    console.error(err)
  }
}

onMounted(async () => {
  try {
    if (authStore.accessToken && !authStore.user) {
      await authStore.fetchMe()
    }

    await initializeNotifications()
  } catch (err) {
    console.error('Failed to initialize authentication.', err)
  }

  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  notifStore.disconnectWS()
})

watch(
  () => authStore.isAuthenticated,
  async (authenticated) => {
    if (authenticated) {
      await initializeNotifications()
    } else {
      notifStore.disconnectWS()
    }
  }
)
</script>