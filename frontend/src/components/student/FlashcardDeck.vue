<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="fw-700 mb-0">Flashcards ({{ cards.length }})</h6>
      <button class="btn btn-sm btn-outline-secondary" @click="resetDeck"><i class="bi bi-arrow-counterclockwise me-1"></i>Reset</button>
    </div>
    <div class="row g-3">
      <div v-for="(c,i) in cards" :key="i" class="col-md-6">
        <div class="flashcard-flip" :class="{flipped:flipped.has(i)}" @click="flip(i)">
          <div class="flashcard-inner">
            <div class="flashcard-front p-3"><div class="small opacity-75 mb-1 text-uppercase fw-600" style="font-size:.65rem">Question</div><strong>{{ c.q }}</strong><div class="mt-2 small opacity-60">Click to reveal</div></div>
            <div class="flashcard-back p-3"><div class="small mb-1 text-muted text-uppercase fw-600" style="font-size:.65rem">Answer</div>{{ c.a }}</div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="cards.length" class="text-center mt-3 text-muted small">{{ flipped.size }}/{{ cards.length }} revealed</div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
defineProps({cards:{type:Array,default:() => []}})
const flipped=ref(new Set())
const resetDeck = () => {
  flipped.value = new Set()
}
const flip=i=>{const s=new Set(flipped.value);s.has(i)?s.delete(i):s.add(i);flipped.value=s}
</script>
