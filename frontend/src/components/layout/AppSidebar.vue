<template>
  <div v-if="open && isMobile" class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-lg-none" style="z-index:1019" @click="$emit('close')"></div>
  <aside class="gp-sidebar" :class="{ hidden: !open }">
    <div class="p-3 border-bottom">
      <div class="d-flex align-items-center gap-2 mb-2">
        <div class="position-relative">
          <img :src="avatar" class="rounded-circle" width="42" height="42" style="object-fit:cover;border:2px solid var(--gp-red)" />
          <span class="position-absolute bottom-0 end-0 online-dot" style="width:9px;height:9px"></span>
        </div>
        <div class="overflow-hidden">
          <div class="fw-700 small text-truncate">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</div>
          <div class="text-muted" style="font-size:.7rem;text-transform:capitalize">{{ auth.user?.role }}</div>
        </div>
      </div>
      <div class="d-flex justify-content-between mb-1" style="font-size:.7rem">
        <span class="text-muted">Level {{ auth.user?.level || 1 }}</span>
        <span class="text-gp-primary fw-600">{{ auth.user?.total_points || 0 }} pts</span>
      </div>
      <div class="gp-progress"><div class="gp-progress-bar" :style="`width:${xpPct}%`"></div></div>
    </div>
    <nav class="py-2 pb-5">
      <div class="sidebar-section">Main</div>
      <RouterLink class="sidebar-link" :class="{active:isActive('/dashboard')}" to="/dashboard"><i class="bi bi-speedometer2"></i>Dashboard</RouterLink>
      <RouterLink class="sidebar-link" :class="{active:isActive('/lessons')}" to="/lessons"><i class="bi bi-calendar-check"></i>My Lessons</RouterLink>
      <RouterLink class="sidebar-link" :class="{active:isActive('/messages')}" to="/messages">
        <i class="bi bi-chat-dots"></i>Messages
        <span v-if="notifStore.unreadCount>0" class="ms-auto badge bg-primary rounded-pill small">{{ notifStore.unreadCount }}</span>
      </RouterLink>
      <template v-if="auth.isStudent">
        <div class="sidebar-section">Learning</div>
        <RouterLink class="sidebar-link" :class="{active:isActive('/tutors')}" to="/tutors"><i class="bi bi-search"></i>Find Tutors</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/group-classes')}" to="/group-classes"><i class="bi bi-people"></i>Group Classes</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/learning')}" to="/learning"><i class="bi bi-map"></i>Learning Paths</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/knowledge-base')}" to="/knowledge-base"><i class="bi bi-journal-richtext"></i>Knowledge Base</RouterLink>
      </template>
      <template v-if="auth.isTutor">
        <div class="sidebar-section">Teaching</div>
        <RouterLink class="sidebar-link" :class="{active:isActive('/my-students')}" to="/my-students"><i class="bi bi-person-lines-fill"></i>My Students</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/availability')}" to="/availability"><i class="bi bi-clock"></i>Availability</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/storefront')}" to="/storefront"><i class="bi bi-shop"></i>My Storefront</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/earnings')}" to="/earnings"><i class="bi bi-wallet2"></i>Earnings</RouterLink>
      </template>
      <template v-if="auth.isAdmin">
        <div class="sidebar-section">Administration</div>
        <RouterLink class="sidebar-link" :class="{active:route.path==='/admin'}" to="/admin"><i class="bi bi-graph-up-arrow"></i>Overview</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/admin/tutors')}" to="/admin/tutors"><i class="bi bi-person-badge"></i>Tutor Approvals</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/admin/users')}" to="/admin/users"><i class="bi bi-people-fill"></i>Users</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/admin/revenue')}" to="/admin/revenue"><i class="bi bi-currency-dollar"></i>Revenue</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/admin/disputes')}" to="/admin/disputes"><i class="bi bi-exclamation-triangle"></i>Disputes</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/admin/bbb')}" to="/admin/bbb"><i class="bi bi-camera-video"></i>BBB Rooms</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/admin/moderation')}" to="/admin/moderation"><i class="bi bi-shield-check"></i>Moderation</RouterLink>
        <RouterLink class="sidebar-link" :class="{active:isActive('/admin/settings')}" to="/admin/settings"><i class="bi bi-sliders"></i>Site Settings</RouterLink>
      </template>
      <div class="sidebar-section">Account</div>
      <RouterLink class="sidebar-link" :class="{active:isActive('/profile')}" to="/profile"><i class="bi bi-person-circle"></i>Profile</RouterLink>
      <RouterLink class="sidebar-link" :class="{active:isActive('/payments')}" to="/payments"><i class="bi bi-credit-card"></i>Payments</RouterLink>
      <RouterLink class="sidebar-link" :class="{active:isActive('/achievements')}" to="/achievements"><i class="bi bi-trophy"></i>Achievements</RouterLink>
      <RouterLink class="sidebar-link" :class="{active:isActive('/notifications')}" to="/notifications">
        <i class="bi bi-bell"></i>Notifications
        <span v-if="notifStore.unreadCount>0" class="ms-auto badge bg-danger rounded-pill small">{{ notifStore.unreadCount }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>
<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifStore } from '@/stores/notifs'
defineProps({ open: Boolean })
defineEmits(['close'])
const auth = useAuthStore(); const notifStore = useNotifStore(); const route = useRoute()
const isMobile = ref(window.innerWidth < 992)
const avatar = computed(() => auth.user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(auth.user?.first_name||'U')}&background=e63900&color=fff`)
const xpPct  = computed(() => Math.round(((auth.user?.total_points||0)%500)/5))
const isActive = path => route.path.startsWith(path)
function onResize() { isMobile.value = window.innerWidth < 992 }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))
</script>
