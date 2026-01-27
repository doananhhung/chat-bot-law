<template>
  <div
    class="slidev-layout h-full bg-slate-50 text-slate-800 font-sans relative overflow-hidden"
  >
    <ThemeBackground />
    <div
      class="relative z-10 h-full p-6 border-t-8 border-indigo-600 grid grid-rows-[auto_1fr] gap-4"
    >
      <h1
        class="text-3xl font-extrabold tracking-tight uppercase flex items-center gap-3"
      >
        <div
          class="w-2 h-10 bg-gradient-to-b from-indigo-600 to-purple-600 rounded-sm"
        ></div>
        <span
          class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-700 to-purple-700"
        >
          <slot name="title">{{ title }}</slot>
        </span>
      </h1>
      <div class="grid grid-cols-2 gap-6 h-full overflow-hidden">
        <div
          class="column-content bg-white/80 backdrop-blur-sm p-4 shadow-lg border-t-4 border-indigo-500 rounded-lg h-full overflow-y-auto text-sm"
        >
          <slot name="left" />
        </div>
        <div
          class="column-content bg-white/80 backdrop-blur-sm p-4 shadow-lg border-t-4 border-purple-500 rounded-lg h-full overflow-y-auto text-sm"
        >
          <slot name="right" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Hide scrollbar but allow scrolling */
.column-content {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}
.column-content::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}
</style>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ title?: string }>();
</script>
