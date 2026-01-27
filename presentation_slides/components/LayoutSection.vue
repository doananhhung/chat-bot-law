<template>
  <div
    class="slidev-layout h-full bg-slate-50 text-slate-800 font-sans relative overflow-hidden"
  >
    <ThemeBackground />
    <div
      class="relative z-10 h-full flex flex-col justify-center px-16 border-l-[16px] border-indigo-600"
    >
      <h1
        class="text-5xl font-extrabold text-indigo-900 mb-6 bg-white/60 backdrop-blur-sm p-4 inline-block rounded-r-lg shadow-sm"
      >
        <slot name="title">{{ title }}</slot>
      </h1>
      <div
        class="text-xl text-slate-600 max-w-4xl bg-white/40 backdrop-blur-sm p-6 rounded-lg border-l-4 border-purple-400"
      >
        <slot name="default" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ title?: string }>();
</script>
