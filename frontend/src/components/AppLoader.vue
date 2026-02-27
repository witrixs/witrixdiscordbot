<script setup lang="ts">
defineProps<{
  size?: 'sm' | 'md' | 'lg'
}>()
</script>

<template>
  <div class="loader" :class="[`loader--${size ?? 'md'}`]" role="status" aria-label="Загрузка">
    <div class="loader-spinner" />
  </div>
</template>

<style scoped>
.loader {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.loader--sm {
  --loader-size: 20px;
  --loader-border: 2px;
}

.loader--md {
  --loader-size: 40px;
  --loader-border: 3px;
}

.loader--lg {
  --loader-size: 56px;
  --loader-border: 4px;
}

.loader-spinner {
  width: var(--loader-size);
  height: var(--loader-size);
  border: var(--loader-border) solid var(--loader-track);
  border-top-color: #5865f2;
  border-radius: 50%;
  animation: loader-spin 0.8s linear infinite;
}

@keyframes loader-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
