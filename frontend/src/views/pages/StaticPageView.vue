<template>
  <div>
    <AppNavbar @toggle-sidebar="()=>{}" />
    <div class="py-4" style="background:linear-gradient(135deg,#111,#1a0800)">
      <div class="container text-center py-3">
        <h1 class="text-white fw-800 mb-1">{{ title }}</h1>
        <p class="text-white-50 small">Last updated: January 2025</p>
      </div>
    </div>
    <div class="container py-5" style="max-width:780px">
      <GpSpinner v-if="loading" />
      <div v-else-if="content" class="gp-card p-4 p-md-5" style="line-height:1.9" v-html="content"></div>
      <div v-else class="gp-card p-4 p-md-5" style="line-height:1.9">
        <div v-html="fallbackContent"></div>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiGet } from '@/utils/api'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import GpSpinner from '@/components/common/GpSpinner.vue'

const props = defineProps({ pageType: { type: String, default: '' } })
const route   = useRoute()
const loading = ref(true)
const content = ref('')
const pageKey = computed(() => props.pageType || route.name?.replace('-','_') || 'privacy')

const titles = {
  privacy:'Privacy Policy', terms:'Terms of Service', ip_policy:'Intellectual Property Policy',
  cookie:'Cookie Policy', refund:'Refund Policy',
}
const title = computed(() => titles[pageKey.value] || 'Legal')

const fallbackContent = computed(() => `
<h3>Introduction</h3>
<p>This ${title.value} governs your use of the Gooprep platform. By using Gooprep, you agree to this policy.</p>
<h3>Contact Us</h3>
<p>For questions about this policy, please email <a href="mailto:support@gooprep.com">support@gooprep.com</a>.</p>
<p class="text-muted small mt-4">© 2026 All rights reserved.</p>
`)

onMounted(async () => {
  try {
    const { data } = await apiGet(`/settings/pages/${pageKey.value}/`)
    content.value = data.content || ''
  } catch {}
  finally { loading.value = false }
})
</script>
