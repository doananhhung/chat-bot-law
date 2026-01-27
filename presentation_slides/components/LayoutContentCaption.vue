<template>
  <div
    class="slidev-layout h-full bg-slate-50 text-slate-800 font-sans relative overflow-hidden"
  >
    <ThemeBackground />
    <div
      class="relative z-10 h-full p-8 border-t-8 border-indigo-600 grid grid-cols-[30%_1fr] gap-8"
    >
      <div
        class="flex flex-col justify-center pr-8 bg-white/60 backdrop-blur-sm rounded-l-lg p-6 border-l-4 border-indigo-500 shadow-sm"
      >
        <h2 class="text-2xl font-bold mb-4 text-indigo-900">
          <slot name="caption-title">{{ captionTitle }}</slot>
        </h2>
        <div class="text-sm text-slate-600 leading-relaxed">
          <slot name="caption" />
        </div>
      </div>
      <div
        class="flex items-center justify-center h-full bg-white/40 backdrop-blur-sm rounded-r-lg border border-white/50 shadow-inner p-4"
      >
        <slot name="default" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ captionTitle?: string }>();
</script>
