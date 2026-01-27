<template>
  <div
    class="slidev-layout h-full bg-slate-50 text-slate-800 font-sans relative overflow-hidden"
  >
    <ThemeBackground />
    <div
      class="relative z-10 h-full p-6 border-t-8 border-indigo-600 grid grid-rows-[1fr_auto] gap-4"
    >
      <div
        class="bg-white/50 backdrop-blur-sm rounded-lg overflow-hidden flex items-center justify-center shadow-lg border border-white/60 p-2"
      >
        <slot name="image" />
      </div>
      <div
        class="text-center py-4 bg-white/80 backdrop-blur-sm rounded-lg shadow-sm border-t-2 border-purple-400"
      >
        <h3 class="text-xl font-bold text-indigo-900">
          <slot name="title">{{ title }}</slot>
        </h3>
        <p class="text-sm text-slate-500 mt-1 font-medium">
          <slot name="caption">{{ caption }}</slot>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ title?: string; caption?: string }>();
</script>
