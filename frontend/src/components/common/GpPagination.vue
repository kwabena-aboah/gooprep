<template>
  <div v-if="totalPages>1" class="d-flex justify-content-center gap-1 mt-4">
    <button class="btn btn-sm btn-outline-secondary" :disabled="page===1" @click="$emit('change',page-1)"><i class="bi bi-chevron-left"></i></button>
    <button v-for="p in visiblePages" :key="p" class="btn btn-sm" :class="p===page?'btn-gp':'btn-outline-secondary'" @click="$emit('change',p)">{{ p }}</button>
    <button class="btn btn-sm btn-outline-secondary" :disabled="page===totalPages" @click="$emit('change',page+1)"><i class="bi bi-chevron-right"></i></button>
  </div>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({page:Number,totalPages:Number})
defineEmits(['change'])
const visiblePages = computed(()=>{const pages=[],start=Math.max(1,props.page-2),end=Math.min(props.totalPages,props.page+2);for(let i=start;i<=end;i++)pages.push(i);return pages})
</script>
