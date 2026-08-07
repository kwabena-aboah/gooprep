<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">Moderation</h2><p class="text-muted small mb-0">Flagged reviews and content</p></div>
      <select class="form-select form-select-sm" v-model="typeFilter" @change="fetch" style="width:auto">
        <option value="">All Types</option>
        <option value="review">Reviews</option>
        <option value="message">Messages</option>
        <option value="profile">Profiles</option>
      </select>
    </div>

    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!items.length" icon="bi bi-shield-check" message="Nothing to moderate — all clear!" />
    <div v-else>
      <div v-for="item in items" :key="item.id" class="gp-card p-4 mb-3">
        <div class="d-flex justify-content-between align-items-start mb-3 flex-wrap gap-2">
          <div class="d-flex align-items-center gap-2">
            <span class="badge" :class="item.content_type==='review'?'bg-warning-subtle text-warning':item.content_type==='message'?'bg-danger-subtle text-danger':'bg-info-subtle text-info'">
              <i class="bi me-1" :class="item.content_type==='review'?'bi-star':'bi-flag'"></i>{{ item.content_type }}
            </span>
            <span class="text-muted small">Flagged {{ timeAgo(item.created_at) }} · {{ item.flag_count }} report(s)</span>
          </div>
          <span class="badge" :class="item.status==='resolved'?'bg-success-subtle text-success':'bg-warning-subtle text-warning'">{{ item.status }}</span>
        </div>

        <div class="gp-card-flat p-3 mb-3" style="background:#fff8f5">
          <div class="small fw-600 text-muted mb-1">Flagged Content</div>
          <div class="small">{{ item.content }}</div>
          <div class="text-muted mt-1" style="font-size:.7rem">by {{ item.author_name }}</div>
        </div>

        <div class="mb-3">
          <div class="small fw-600 text-muted mb-1">Flag Reason(s)</div>
          <div class="d-flex flex-wrap gap-1">
            <span v-for="r in (item.reasons||[])" :key="r" class="badge bg-danger-subtle text-danger small">{{ r }}</span>
          </div>
        </div>

        <div v-if="item.status !== 'resolved'" class="d-flex gap-2 flex-wrap">
          <button class="btn btn-success btn-sm" @click="moderate(item,'approve')">
            <i class="bi bi-check-circle me-1"></i>Keep Content
          </button>
          <button class="btn btn-danger btn-sm" @click="moderate(item,'remove')">
            <i class="bi bi-trash me-1"></i>Remove Content
          </button>
          <button class="btn btn-warning btn-sm" @click="moderate(item,'warn')">
            <i class="bi bi-exclamation-triangle me-1"></i>Warn Author
          </button>
          <button class="btn btn-outline-danger btn-sm" @click="moderate(item,'ban')">
            <i class="bi bi-ban me-1"></i>Ban User
          </button>
        </div>
        <div v-else class="text-success small"><i class="bi bi-check-circle me-1"></i>Resolved: {{ item.resolution }}</div>
      </div>
      <GpPagination :page="page" :total-pages="totalPages" @change="p=>{page=p;fetch()}" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { timeAgo } from '@/utils/helpers'
import { useNotifStore } from '@/stores/notifs'
import GpSpinner    from '@/components/common/GpSpinner.vue'
import GpEmpty      from '@/components/common/GpEmpty.vue'
import GpPagination from '@/components/common/GpPagination.vue'

const notifStore = useNotifStore()
const items      = ref([])
const loading    = ref(true)
const total      = ref(0)
const page       = ref(1)
const typeFilter = ref('')
const totalPages = computed(() => Math.ceil(total.value / 15))

async function fetch() {
  loading.value = true
  const params = { page: page.value, page_size: 15 }
  if (typeFilter.value) params.content_type = typeFilter.value
  try {
    const { data } = await apiGet('/admin-panel/moderation/', params)
    items.value = data.results || []; total.value = data.count || 0
  } catch {} finally { loading.value = false }
}

async function moderate(item, action) {
  try {
    await apiPost(`/admin-panel/moderation/${item.id}/action/`, { action })
    item.status = 'resolved'
    item.resolution = action
    notifStore.toast(`Content ${action}d.`, 'success')
  } catch { notifStore.toast('Action failed.', 'error') }
}

onMounted(fetch)
</script>
