<script setup lang="ts">
defineProps<{
  width?: string
  height?: string
  borderRadius?: string
}>()
</script>

<template>
  <div
    class="skeleton"
    :style="{
      width: width ?? '100%',
      height: height ?? '1rem',
      borderRadius: borderRadius ?? '8px',
    }"
  />
</template>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.06) 0%,
    rgba(255, 255, 255, 0.12) 50%,
    rgba(255, 255, 255, 0.06) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shine 1.2s ease-in-out infinite;
}

@keyframes skeleton-shine {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
