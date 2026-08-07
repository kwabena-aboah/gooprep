<template>
  <div class="stat-card" :class="color">
    <div class="small opacity-75 mb-1"><i :class="icon" class="me-1"></i>{{ label }}</div>
    <div class="fs-2 fw-800">{{ value }}</div>
    <div class="small opacity-75" v-if="sub">{{ sub }}</div>
  </div>
</template>
<script setup>
defineProps({label:String,value:[String,Number],sub:String,icon:String,color:{type:String,default:'red'}})
</script>
