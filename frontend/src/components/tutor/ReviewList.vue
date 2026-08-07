<template>
  <div>
    <div v-if="showSummary&&reviews.length" class="gp-card p-4 mb-4">
      <div class="row align-items-center g-3">
        <div class="col-auto text-center">
          <div class="fw-800 text-gp-primary" style="font-size:3.5rem;line-height:1">{{ avgRating }}</div>
          <div class="gp-stars mb-1"><i v-for="n in 5" :key="n" class="bi bi-star-fill" :class="{' opacity-25':n>Math.round(avgRating)}"></i></div>
          <div class="text-muted small">{{ reviews.length }} reviews</div>
        </div>
        <div class="col">
          <div v-for="n in [5,4,3,2,1]" :key="n" class="d-flex align-items-center gap-2 mb-1">
            <span class="text-muted small" style="width:12px">{{ n }}</span>
            <i class="bi bi-star-fill text-warning small"></i>
            <div class="gp-progress flex-grow-1" style="height:8px"><div class="gp-progress-bar" :style="`width:${ratingPct(n)}%`"></div></div>
            <span class="text-muted small" style="width:28px;text-align:right">{{ ratingPct(n) }}%</span>
          </div>
        </div>
      </div>
    </div>
    <GpSpinner v-if="loading"/>
    <GpEmpty v-else-if="!reviews.length" icon="bi bi-star" message="No reviews yet."/>
    <div v-else>
      <div v-for="r in visible" :key="r.id" class="gp-card p-4 mb-3">
        <div class="d-flex align-items-center gap-2 mb-2">
          <img :src="r.reviewer_avatar||fb(r.reviewer_name)" class="rounded-circle" width="38" height="38" style="object-fit:cover"/>
          <div><div class="fw-700 small">{{ r.reviewer_name }}</div><div class="gp-stars" style="font-size:.75rem"><i v-for="n in r.rating" :key="n" class="bi bi-star-fill"></i></div></div>
          <span class="ms-auto text-muted small">{{ timeAgo(r.created_at) }}</span>
        </div>
        <p class="small mb-0 text-muted">{{ r.content }}</p>
      </div>
      <button v-if="reviews.length>4&&!showAll" class="btn btn-link btn-sm text-gp-primary p-0" @click="showAll=true">Show all {{ reviews.length }} reviews</button>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import GpSpinner from '@/components/common/GpSpinner.vue'
import GpEmpty   from '@/components/common/GpEmpty.vue'
import { timeAgo } from '@/utils/helpers'
const props = defineProps({reviews:{type:Array,default:()=>[]},loading:{type:Boolean,default:false},showSummary:{type:Boolean,default:true}})
const showAll=ref(false)
const visible=computed(()=>showAll.value?props.reviews:props.reviews.slice(0,4))
const avgRating=computed(()=>(!props.reviews.length?'0.0':(props.reviews.reduce((a,r)=>a+r.rating,0)/props.reviews.length).toFixed(1)))
const ratingPct=n=>(!props.reviews.length?0:Math.round(props.reviews.filter(r=>r.rating===n).length/props.reviews.length*100))
const fb=name=>`https://ui-avatars.com/api/?name=${encodeURIComponent(name||'U')}&background=e2e8f0&color=64748b`
</script>
