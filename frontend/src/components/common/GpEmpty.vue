<template>
  <div class="text-center py-5 text-muted">
    <i :class="icon" class="d-block mb-2 opacity-25" style="font-size:3rem"></i>
    <p class="mb-3">{{ message }}</p>
    <RouterLink v-if="actionTo" :to="actionTo" class="btn btn-gp btn-sm"><i v-if="actionIcon" :class="actionIcon" class="me-1"></i>{{ actionLabel }}</RouterLink>
    <button v-else-if="actionLabel" class="btn btn-gp btn-sm" @click="$emit('action')"><i v-if="actionIcon" :class="actionIcon" class="me-1"></i>{{ actionLabel }}</button>
  </div>
</template>
<script setup>
defineProps({icon:{type:String,default:'bi bi-inbox'},message:{type:String,default:'Nothing here yet.'},actionLabel:{type:String,default:''},actionIcon:{type:String,default:''},actionTo:{type:String,default:''}})
defineEmits(['action'])
</script>
