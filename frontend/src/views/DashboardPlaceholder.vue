<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const title = computed(() => {
  if (route.path.includes('servers')) return 'Серверы'
  if (route.path.includes('settings')) return 'Настройки'
  return 'Раздел'
})
</script>

<template>
  <div class="placeholder">
    <h1 class="placeholder-title">{{ title }}</h1>
    <p class="placeholder-text">Скоро здесь появится функционал.</p>
  </div>
</template>

<style scoped>
.placeholder {
  padding: 2rem 0;
  text-align: center;
}
.placeholder-title {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
}
.placeholder-text {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-muted);
}
</style>
