<template>
  <div class="gp-card p-4">
    <div class="d-flex justify-content-between align-items-baseline mb-3">
      <span class="fw-800 fs-2 text-gp-primary">GHS {{ tutor.hourly_rate }}</span>
      <span class="text-muted small">/hr</span>
    </div>
    <div v-if="tutor.trial_lesson_enabled" class="d-flex align-items-center gap-2 p-2 rounded-3 mb-3" style="background:rgba(230,57,0,.06);border:1px solid rgba(230,57,0,.15)">
      <i class="bi bi-gift-fill text-gp-primary"></i>
      <div class="small"><div class="fw-600">Trial lesson available</div><div class="text-muted">GHS {{ tutor.trial_lesson_price }} · 30 min</div></div>
    </div>
    <div class="row g-2 mb-2">
      <div class="col-6"><label class="form-label small fw-600">Date *</label><input type="date" class="form-control form-control-sm" v-model="form.date" :min="today"/></div>
      <div class="col-6"><label class="form-label small fw-600">Time *</label><input type="time" class="form-control form-control-sm" v-model="form.time"/></div>
    </div>
    <div class="mb-2"><label class="form-label small fw-600">Duration</label>
      <select class="form-select form-select-sm" v-model="form.duration"><option value="30">30 min</option><option value="60">1 hour</option><option value="90">1.5 hours</option><option value="120">2 hours</option></select>
    </div>
    <div class="mb-3"><label class="form-label small fw-600">Topic</label><input class="form-control form-control-sm" v-model="form.topic" placeholder="What to cover?"/></div>
    <div class="gp-card-flat p-3 mb-3" style="background:var(--gp-surface)">
      <div class="d-flex justify-content-between small mb-1"><span>Lesson ({{ form.duration }} min)</span><span>GHS {{ lessonCost }}</span></div>
      <div class="d-flex justify-content-between small text-muted mb-1"><span>Platform fee (15%)</span><span>GHS {{ fee }}</span></div>
      <div class="d-flex justify-content-between fw-700 border-top pt-2"><span>Total</span><span class="text-gp-primary">GHS {{ total }}</span></div>
    </div>
    <button class="btn btn-gp w-100 py-2" @click="$emit('book',form)" :disabled="loading||!form.date||!form.time">
      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
      <i v-else class="bi bi-calendar-check me-2"></i>{{ tutor.instant_book?'Book Instantly':'Request Lesson' }}
    </button>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
const props = defineProps({tutor:{type:Object,required:true},loading:{type:Boolean,default:false}})
defineEmits(['book'])
const today=new Date().toISOString().split('T')[0]
const form=ref({date:'',time:'10:00',duration:'60',subject:props.tutor?.subjects_list?.[0]?.id||'',type:'regular',topic:'',record:true})
const lessonCost=computed(()=>form.value.type==='trial'?parseFloat(props.tutor.trial_lesson_price||0).toFixed(2):(parseFloat(props.tutor.hourly_rate||0)*parseInt(form.value.duration)/60).toFixed(2))
const fee=computed(()=>(parseFloat(lessonCost.value)*0.15).toFixed(2))
const total=computed(()=>(parseFloat(lessonCost.value)*1.15).toFixed(2))
</script>
