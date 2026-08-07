<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="fw-700 mb-0">Practice Quiz ({{ questions.length }})</h6>
      <button v-if="done" class="btn btn-sm btn-outline-primary" @click="Object.keys(answers).forEach(k => delete answers[k])"><i class="bi bi-arrow-repeat me-1"></i>Retry</button>
    </div>
    <div v-if="done" class="gp-card p-3 mb-3 text-center" style="background:linear-gradient(135deg,#fff8f5,#fff3e0)">
      <div class="fw-800 text-gp-primary fs-2">{{ score }}/{{ questions.length }}</div>
      <div class="text-muted small">{{ score===questions.length?'🎉 Perfect!':score>=questions.length*0.7?'👏 Well done!':'📚 Keep practising!' }}</div>
    </div>
    <div v-for="(q,qi) in questions" :key="qi" class="gp-card p-3 mb-3">
      <div class="fw-600 small mb-2">Q{{ qi+1 }}. {{ q.question }}</div>
      <div class="d-grid gap-1">
        <button v-for="opt in q.options" :key="opt" class="btn btn-sm text-start" :class="ac(qi,opt)" :disabled="!!answers[qi]" @click="answer(qi,opt,q.answer)">{{ opt }}</button>
      </div>
      <div v-if="answers[qi]" class="small mt-2" :class="answers[qi].correct?'text-success':'text-danger'">
        <i class="bi me-1" :class="answers[qi].correct?'bi-check-circle':'bi-x-circle'"></i>{{ answers[qi].correct?'Correct!':'Answer: '+q.answer }}
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
const props=defineProps({questions:{type:Array,default:() => []}})
const answers=ref({})
const done=computed(()=>Object.keys(answers.value).length===props.questions.length)
const score=computed(()=>Object.values(answers.value).filter(a=>a.correct).length)
function answer(qi,opt,correctAnswer){answers.value={...answers.value,[qi]:{opt,correct:opt.startsWith(correctAnswer)}}}
function ac(qi,opt){const a=answers.value[qi];if(!a)return 'btn-outline-secondary';if(a.opt===opt)return a.correct?'btn-success':'btn-danger';if(opt.startsWith(props.questions[qi]?.answer)&&!a.correct)return 'btn-outline-success';return 'btn-outline-secondary opacity-50'}
</script>
