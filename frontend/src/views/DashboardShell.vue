<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'

const route = useRoute()
const pageTitle = computed(() => {
  const t = (route.meta.title as string) ?? 'Панель'
  return t.replace(/\s*—\s*Witrix Bot\s*$/, '').trim() || 'Панель'
})
</script>

<template>
  <DashboardLayout>
    <template #title>{{ pageTitle }}</template>
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </DashboardLayout>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
