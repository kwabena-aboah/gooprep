<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-800 mb-0">Notifications</h2>
        <p class="text-muted small mb-0">{{ notifStore.unreadCount }} unread</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary btn-sm" @click="notifStore.markAllRead" :disabled="!notifStore.unreadCount">
          <i class="bi bi-check2-all me-1"></i>Mark all read
        </button>
        <select class="form-select form-select-sm" v-model="typeFilter" style="width:auto">
          <option value="">All Types</option>
          <option value="lesson_booked">Lesson Booked</option>
          <option value="lesson_reminder">Reminders</option>
          <option value="lesson_completed">Completed</option>
          <option value="payment_received">Payments</option>
          <option value="review_received">Reviews</option>
          <option value="message_received">Messages</option>
          <option value="system">System</option>
        </select>
      </div>
    </div>

    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!filtered.length"
             icon="bi bi-bell-slash"
             message="You're all caught up!" />

    <div v-else>
      <div v-for="(group, label) in grouped" :key="label" class="mb-4">
        <div class="d-flex align-items-center gap-2 mb-3">
          <hr class="flex-grow-1">
          <span class="text-muted small fw-600 px-2">{{ label }}</span>
          <hr class="flex-grow-1">
        </div>
        <div v-for="n in group" :key="n.id"
             class="gp-card p-3 mb-2 d-flex align-items-start gap-3"
             :class="{ 'border-start border-3 border-primary': !n.is_read }"
             style="cursor:pointer" @click="open(n)">
          <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
               :style="`width:44px;height:44px;background:${nColor(n.notification_type)}20`">
            <i :class="`bi ${notifIcon(n.notification_type)}`"
               :style="`color:${nColor(n.notification_type)};font-size:1.2rem`"></i>
          </div>
          <div class="flex-grow-1 overflow-hidden">
            <div class="d-flex justify-content-between gap-2">
              <div class="fw-600 small" :class="{ 'text-dark': !n.is_read }">{{ n.title }}</div>
              <span class="text-muted flex-shrink-0" style="font-size:.7rem">{{ timeAgo(n.created_at) }}</span>
            </div>
            <div class="text-muted small text-truncate">{{ n.message }}</div>
          </div>
          <div v-if="!n.is_read" class="flex-shrink-0 mt-1">
            <div class="rounded-circle bg-primary" style="width:8px;height:8px"></div>
          </div>
        </div>
      </div>

      <div class="text-center mt-4" v-if="hasMore">
        <button class="btn btn-outline-secondary btn-sm" @click="loadMore" :disabled="loadingMore">
          <span v-if="loadingMore" class="spinner-border spinner-border-sm me-1"></span>
          Load more
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotifStore } from '@/stores/notifs'
import { apiGet } from '@/utils/api'
import { timeAgo, notifIcon } from '@/utils/helpers'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'

const notifStore  = useNotifStore()
const router      = useRouter()
const loading     = ref(true)
const loadingMore = ref(false)
const hasMore     = ref(false)
const page        = ref(1)
const typeFilter  = ref('')

const colorMap = {
  lesson_booked:'#10b981', lesson_reminder:'#f59e0b', lesson_completed:'#10b981',
  lesson_cancelled:'#ef4444', payment_received:'#10b981', review_received:'#f59e0b',
  message_received:'#6366f1', system:'#64748b',
}
const nColor = type => colorMap[type] || '#64748b'

const filtered = computed(() =>
  typeFilter.value
    ? notifStore.notifications.filter(n => n.notification_type === typeFilter.value)
    : notifStore.notifications
)

const grouped = computed(() => {
  const groups = {}
  const today = new Date(); today.setHours(0,0,0,0)
  const yesterday = new Date(today); yesterday.setDate(yesterday.getDate() - 1)
  filtered.value.forEach(n => {
    const d = new Date(n.created_at); d.setHours(0,0,0,0)
    const label = +d === +today ? 'Today' : +d === +yesterday ? 'Yesterday'
      : d.toLocaleDateString('en-GB', { weekday:'long', day:'numeric', month:'long' })
    if (!groups[label]) groups[label] = []
    groups[label].push(n)
  })
  return groups
})

async function loadMore() {
  loadingMore.value = true; page.value++
  try {
    const { data } = await apiGet('/auth/notifications/', { page: page.value, page_size: 30 })
    notifStore.notifications.push(...(data.results || []))
    hasMore.value = !!data.next
  } catch {} finally { loadingMore.value = false }
}

function open(n) {
  if (!n.is_read) notifStore.markRead([n.id])
  if (n.link) router.push(n.link)
}

onMounted(async () => {
  await notifStore.fetchNotifs()
  loading.value = false
})
</script>
