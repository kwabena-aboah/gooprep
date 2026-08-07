<template>
  <div class="gp-card p-3 h-100 d-flex flex-column" style="cursor:pointer" @click="$emit('select',tutor)">
    <div class="d-flex gap-3 mb-3">
      <div class="position-relative flex-shrink-0">
        <img :src="tutor.avatar_url||fb" class="rounded-circle" width="64" height="64" style="object-fit:cover;border:3px solid var(--gp-red)"/>
        <span v-if="tutor.is_online" class="position-absolute bottom-0 end-0 online-dot"></span>
      </div>
      <div class="overflow-hidden flex-grow-1">
        <div class="fw-700 text-truncate">{{ tutor.full_name }}</div>
        <div class="text-muted small text-truncate" style="font-size:.8rem">{{ tutor.headline }}</div>
        <div class="gp-stars small"><i class="bi bi-star-fill"></i> {{ tutor.average_rating }} <span class="text-muted">({{ tutor.total_reviews }})</span></div>
      </div>
      <button class="btn btn-link p-0 text-muted align-self-start" @click.stop="$emit('fav',tutor)">
        <i class="bi" :class="isFav?'bi-heart-fill text-danger':'bi-heart'"></i>
      </button>
    </div>
    <div class="d-flex flex-wrap gap-1 mb-3">
      <span v-for="s in (tutor.subjects_list||[]).slice(0,3)" :key="s.id" class="gp-badge">{{ s.name }}</span>
    </div>
    <div class="mt-auto">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <span class="fw-700 text-gp-primary fs-5">GHS {{ tutor.hourly_rate }}<span class="text-muted fw-400 small">/hr</span></span>
        <span v-if="tutor.trial_lesson_enabled" class="badge bg-warning-subtle text-warning small">Trial</span>
      </div>
      <div class="d-flex gap-1 flex-wrap">
        <span v-if="tutor.instant_book" class="badge bg-success-subtle text-success small"><i class="bi bi-lightning-fill me-1"></i>Instant</span>
        <span class="badge bg-light text-muted border small"><i class="bi bi-book me-1"></i>{{ tutor.total_lessons }}</span>
      </div>
    </div>
  </div>
</template>
<script setup>
const props = defineProps({tutor:{type:Object,required:true},isFav:{type:Boolean,default:false}})
defineEmits(['select','fav'])
const fb = `https://ui-avatars.com/api/?name=${encodeURIComponent(props.tutor?.full_name||'T')}&background=e63900&color=fff`
</script>
