<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div><h2 class="fw-800 mb-0">User Management</h2><p class="text-muted small mb-0">{{ total }} total users</p></div>
      <div class="d-flex gap-2 flex-wrap">
        <div class="input-group input-group-sm"><span class="input-group-text"><i class="bi bi-search text-muted"></i></span><input class="form-control" v-model="search" placeholder="Search…" @input="debouncedFetch" style="width:200px" /></div>
        <select class="form-select form-select-sm" v-model="roleFilter" @change="fetchUsers" style="width:auto">
          <option value="">All Roles</option><option value="student">Students</option>
          <option value="tutor">Tutors</option><option value="institution">Institutions</option>
        </select>
      </div>
    </div>
    <GpSpinner v-if="loading" />
    <div v-else class="gp-card">
      <div class="table-responsive">
        <table class="gp-table">
          <thead><tr><th>User</th><th>Role</th><th>Plan</th><th>Joined</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>
                <div class="d-flex align-items-center gap-2">
                  <img :src="u.avatar_url||fallback(u.full_name)" class="rounded-circle" width="32" height="32" style="object-fit:cover" />
                  <div><div class="small fw-600">{{ u.full_name }}</div><div class="text-muted" style="font-size:.7rem">{{ u.email }}</div></div>
                </div>
              </td>
              <td><span class="badge bg-light text-dark border small text-capitalize">{{ u.role }}</span></td>
              <td><span class="gp-badge small">{{ u.subscription_plan||'Free' }}</span></td>
              <td class="small text-muted">{{ fmtDate(u.date_joined) }}</td>
              <td><span class="badge small" :class="u.is_active?'bg-success-subtle text-success':'bg-danger-subtle text-danger'">{{ u.is_active?'Active':'Suspended' }}</span></td>
              <td>
                <div class="d-flex gap-1">
                  <button class="btn btn-xs btn-outline-secondary" @click="impersonate(u)" title="View as user"><i class="bi bi-person-video"></i></button>
                  <button class="btn btn-xs btn-outline-warning" @click="toggleActive(u)" :title="u.is_active?'Suspend':'Activate'">
                    <i class="bi" :class="u.is_active?'bi-pause-circle':'bi-play-circle'"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="p-3"><GpPagination :page="page" :total-pages="totalPages" @change="p=>{page=p;fetchUsers()}" /></div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { fmtDate, debounce } from '@/utils/helpers'
import { useNotifStore } from '@/stores/notifs'
import GpSpinner    from '@/components/common/GpSpinner.vue'
import GpPagination from '@/components/common/GpPagination.vue'
const notifStore = useNotifStore()
const users = ref([]); const loading = ref(true); const total = ref(0)
const page = ref(1); const search = ref(''); const roleFilter = ref('')
const totalPages = computed(() => Math.ceil(total.value/20))
const fallback = n => `https://ui-avatars.com/api/?name=${encodeURIComponent(n||'U')}&background=e2e8f0&color=64748b`
const debouncedFetch = debounce(()=>{ page.value=1; fetchUsers() }, 350)
async function fetchUsers() {
  loading.value = true
  const params = { page: page.value, page_size:20 }
  if (search.value) params.search = search.value
  if (roleFilter.value) params.role = roleFilter.value
  try { const { data } = await apiGet('/admin-panel/users/', params); users.value=data.results||[]; total.value=data.count||0 }
  catch {} finally { loading.value = false }
}
async function toggleActive(u) {
  try { await apiPost(`/admin-panel/users/${u.id}/toggle-active/`); u.is_active=!u.is_active; notifStore.toast(u.is_active?'User activated':'User suspended','success') }
  catch { notifStore.toast('Action failed.','error') }
}
function impersonate(u) { window.open(`/admin-panel/users/${u.id}/impersonate/`,'_blank') }
onMounted(fetchUsers)
</script>
