<template>
  <nav class="gp-navbar">
    <button class="btn btn-link text-white p-0 me-2 d-lg-none" @click="$emit('toggle-sidebar')">
      <i class="bi bi-list fs-4"></i>
    </button>
    <RouterLink to="/" class="me-auto d-flex align-items-center logo">
      <img src="@/assets/img/gooprep_logo.png" alt="Gooprep" style="height:36px;width:auto;object-fit:contain" />
    </RouterLink>
    <template v-if="!auth.isAuthenticated">
      <RouterLink to="/login"    class="btn btn-sm btn-outline-light me-2">Log in</RouterLink>
      <RouterLink to="/register" class="btn btn-sm btn-gp">Sign up free</RouterLink>
    </template>
    <template v-else>
      <RouterLink
        v-if="auth.isTutor || auth.isStudent"
        class="btn btn-sm btn-gp-outline text-white border-white me-3 d-none d-md-inline-flex align-items-center"
        :to="auth.isTutor ? '/tutor-onboarding' : '/student-onboarding'"
      >
        <i class="bi bi-clipboard-check me-1"></i>Continue onboarding
      </RouterLink>
      <div class="dropdown me-3 flex-shrink-0">
        <button type="button" class="btn btn-link text-white p-0 position-relative" data-bs-toggle="dropdown" aria-label="Notifications">
          <i class="bi bi-bell fs-5"></i>
          <span v-if="notifStore.unreadCount > 0" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size:.6rem">{{ notifStore.unreadCount }}</span>
        </button>
        <div class="dropdown-menu dropdown-menu-end shadow border-0" style="width:320px;max-height:420px;overflow-y:auto">
          <div class="d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
            <span class="fw-700 small">Notifications</span>
            <button class="btn btn-link btn-sm text-primary p-0 small" @click="notifStore.markAllRead">Mark all read</button>
          </div>
          <div v-if="!notifStore.notifications.length" class="px-3 py-4 text-center text-muted small">
            <i class="bi bi-bell-slash d-block fs-3 mb-1 opacity-25"></i>No notifications
          </div>
          <RouterLink v-for="n in notifStore.notifications.slice(0,6)" :key="n.id" to="/notifications"
                      class="dropdown-item py-2 border-bottom small" :class="{'bg-light fw-600':!n.is_read}"
                      @click="notifStore.markRead([n.id])">
            <div class="d-flex gap-2">
              <i class="bi mt-1 flex-shrink-0" :class="[notifIcon(n.notification_type),'text-primary']" style="font-size:.9rem"></i>
              <div class="overflow-hidden">
                <div class="fw-600 text-truncate">{{ n.title }}</div>
                <div class="text-muted text-truncate">{{ n.message }}</div>
                <div class="text-muted" style="font-size:.7rem">{{ timeAgo(n.created_at) }}</div>
              </div>
            </div>
          </RouterLink>
          <RouterLink to="/notifications" class="dropdown-item text-center small text-primary py-2 fw-600">View all</RouterLink>
        </div>
      </div>
      <div class="dropdown">
        <button class="btn btn-link p-0 d-flex align-items-center gap-2" data-bs-toggle="dropdown">
          <img :src="avatar" class="rounded-circle" width="34" height="34" style="object-fit:cover;border:2px solid rgba(255,255,255,.3)" />
          <span class="text-white d-none d-md-inline small fw-500">{{ auth.user?.first_name }}</span>
          <i class="bi bi-chevron-down text-white-50 small"></i>
        </button>
        <ul class="dropdown-menu dropdown-menu-end shadow border-0" style="min-width:200px">
          <li>
            <div class="px-3 py-2 border-bottom">
              <div class="fw-700 small">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</div>
              <div class="text-muted" style="font-size:.7rem;text-transform:capitalize">{{ auth.user?.role }}</div>
            </div>
          </li>
          <li><RouterLink class="dropdown-item small" to="/dashboard"><i class="bi bi-speedometer2 me-2 text-primary"></i>Dashboard</RouterLink></li>
          <li><RouterLink class="dropdown-item small" to="/profile"><i class="bi bi-person me-2 text-primary"></i>Profile</RouterLink></li>
          <li v-if="auth.isTutor || auth.isStudent"><RouterLink class="dropdown-item small" :to="auth.isTutor ? '/tutor-onboarding' : '/student-onboarding'"><i class="bi bi-clipboard-check me-2 text-primary"></i>Continue onboarding</RouterLink></li>
          <li v-if="auth.isTutor"><RouterLink class="dropdown-item small" to="/earnings"><i class="bi bi-wallet2 me-2 text-primary"></i>Earnings</RouterLink></li>
          <li v-if="auth.isAdmin"><RouterLink class="dropdown-item small" to="/admin"><i class="bi bi-shield-check me-2 text-primary"></i>Admin</RouterLink></li>
          <li><RouterLink class="dropdown-item small" to="/settings"><i class="bi bi-gear me-2 text-primary"></i>Settings</RouterLink></li>
          <li><hr class="dropdown-divider my-1"></li>
          <li><button class="dropdown-item small text-danger" @click="logout"><i class="bi bi-box-arrow-right me-2"></i>Sign out</button></li>
        </ul>
      </div>
    </template>
  </nav>
</template>
<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
import { timeAgo, notifIcon } from '@/utils/helpers'
defineEmits(['toggle-sidebar'])
const auth = useAuthStore(); const notifStore = useNotifStore(); const router = useRouter()
const avatar = computed(() => auth.user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(auth.user?.first_name||'U')}&background=e63900&color=fff`)
async function logout() { await auth.logout(); router.push('/login') }
</script>
