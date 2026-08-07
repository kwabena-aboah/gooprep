<template>
  <div class="gp-toast-wrap">
    <TransitionGroup name="toast">
      <div v-for="t in notifStore.toasts" :key="t.id" class="gp-toast" :class="t.type">
        <i class="bi me-2" :class="{'bi-check-circle':t.type==='success','bi-x-circle':t.type==='error','bi-exclamation-triangle':t.type==='warning','bi-info-circle':!t.type||t.type==='info'}"></i>
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>
<script setup>
import { useNotifStore } from '@/stores/notifs'
const notifStore = useNotifStore()
</script>
<style scoped>
.toast-enter-active,.toast-leave-active{transition:all .3s ease}
.toast-enter-from{opacity:0;transform:translateY(16px)}.toast-leave-to{opacity:0;transform:translateY(-8px)}
</style>
