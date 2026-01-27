<template>
  <div class="slidev-layout h-full bg-slate-50 relative overflow-hidden">
    <ThemeBackground />
    <div class="relative z-10 h-full">
      <div
        v-if="placeholder"
        class="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none select-none"
      >
        <span
          class="text-6xl font-black text-indigo-900 uppercase tracking-widest border-4 border-indigo-900 p-8 transform -rotate-12"
          >BLANK CANVAS</span
        >
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ placeholder?: boolean }>();
</script>
