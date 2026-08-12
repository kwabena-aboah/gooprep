<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-800 mb-0">Referrals</h2>
        <p class="text-muted small mb-0">{{ total }} referred users</p>
      </div>
      <div class="d-flex gap-2">
        <RouterLink to="/admin/exports" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-file-earmark-arrow-down me-1"></i>Export
        </RouterLink>
        <RouterLink to="/admin" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i>Admin Overview
        </RouterLink>
      </div>
    </div>

    <div class="gp-card p-3 mb-3">
      <div class="row g-2">
        <div class="col-md-8">
          <input v-model="search" class="form-control form-control-sm" placeholder="Search user or referrer…" @input="reload" />
        </div>
        <div class="col-md-4">
          <select v-model="role" class="form-select form-select-sm" @change="reload">
            <option value="">All roles</option>
            <option value="student">Students</option>
            <option value="tutor">Tutors</option>
            <option value="institution">Institutions</option>
          </select>
        </div>
      </div>
    </div>

    <GpSpinner v-if="loading" />
    <GpEmpty v-else-if="!referrals.length" icon="bi bi-share" message="No referrals found." />
    <div v-else class="gp-card table-responsive">
      <table class="gp-table">
        <thead>
          <tr><th>User</th><th>Role</th><th>Referrer</th><th>Notes</th><th>Joined</th></tr>
        </thead>
        <tbody>
          <tr v-for="referral in referrals" :key="referral.id">
            <td>
              <div class="d-flex align-items-center gap-2">
                <img :src="referral.avatar_url" class="rounded-circle" width="32" height="32" alt="" />
                <div><div class="small fw-600">{{ referral.full_name }}</div><div class="text-muted small">{{ referral.email }}</div></div>
              </div>
            </td>
            <td><span class="badge bg-light text-dark border text-capitalize">{{ referral.role }}</span></td>
            <td class="small">{{ referral.referrer_name || '—' }}</td>
            <td class="small text-muted">{{ referral.referrer_notes || '—' }}</td>
            <td class="small text-muted">{{ formatDate(referral.date_joined) }}</td>
          </tr>
        </tbody>
      </table>
      <div class="p-3"><GpPagination :page="page" :total-pages="totalPages" @change="changePage" /></div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { apiGet } from '@/utils/api'
import GpEmpty from '@/components/common/GpEmpty.vue'
import GpPagination from '@/components/common/GpPagination.vue'
import GpSpinner from '@/components/common/GpSpinner.vue'

const referrals = ref([])
const loading = ref(true)
const total = ref(0)
const page = ref(1)
const search = ref('')
const role = ref('')
const pageSize = 20
const totalPages = computed(() => Math.ceil(total.value / pageSize))

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-GB') : '—'
}

async function fetchReferrals() {
  loading.value = true
  try {
    const { data } = await apiGet('/admin-panel/referrals/', {
      page: page.value,
      page_size: pageSize,
      search: search.value,
      role: role.value,
    })
    referrals.value = data.results || []
    total.value = data.count || 0
  } catch {
    referrals.value = []
  } finally {
    loading.value = false
  }
}

function reload() {
  page.value = 1
  fetchReferrals()
}

function changePage(value) {
  page.value = value
  fetchReferrals()
}

onMounted(fetchReferrals)
</script>
