<template>
  <div
    class="slidev-layout h-full bg-slate-50 text-slate-800 font-sans relative overflow-hidden"
  >
    <ThemeBackground />
    <div
      class="relative z-10 h-full flex flex-col items-center justify-center text-center p-8 border-t-8 border-indigo-600"
    >
      <div
        class="bg-white/70 backdrop-blur-md p-16 rounded-2xl shadow-2xl border border-white/50 relative overflow-hidden"
      >
        <div
          class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"
        ></div>
        <h1
          class="text-9xl font-black bg-clip-text text-transparent bg-gradient-to-br from-indigo-600 to-purple-800 mb-6 drop-shadow-sm"
        >
          <slot name="fact">{{ fact }}</slot>
        </h1>
        <div class="w-32 h-1 bg-gray-200 mx-auto mb-6 rounded-full"></div>
        <p class="text-3xl text-slate-700 font-light max-w-3xl">
          <slot name="description">{{ description }}</slot>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ fact?: string | number; description?: string }>();
</script>
