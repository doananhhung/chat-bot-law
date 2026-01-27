<template>
  <div
    class="slidev-layout h-full bg-slate-50 text-slate-800 font-sans relative overflow-hidden"
  >
    <ThemeBackground />
    <div
      class="relative z-10 h-full flex flex-col justify-center items-center text-center p-12 border-t-8 border-indigo-600"
    >
      <div
        class="w-24 h-2 bg-gradient-to-r from-indigo-600 to-purple-600 mb-8 rounded-full"
      ></div>
      <h1
        class="text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-700 to-purple-700 mb-6 drop-shadow-sm"
      >
        <slot name="title">{{ title }}</slot>
      </h1>
      <p class="text-2xl text-slate-600 font-light max-w-3xl">
        <slot name="subtitle">{{ subtitle }}</slot>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ title?: string; subtitle?: string }>();
</script>
