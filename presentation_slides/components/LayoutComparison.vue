<template>
  <div
    class="slidev-layout h-full bg-slate-50 text-slate-800 font-sans relative"
  >
    <ThemeBackground />
    <div
      class="relative z-10 h-full p-6 border-t-4 border-indigo-600 flex flex-col"
    >
      <h1
        class="text-3xl font-extrabold tracking-tight uppercase text-center bg-clip-text text-transparent bg-gradient-to-r from-indigo-700 to-purple-700 mb-4 shrink-0"
      >
        <slot name="title">{{ title }}</slot>
      </h1>
      <div class="grid grid-cols-2 gap-6 flex-1 min-h-0">
        <div
          class="flex flex-col bg-white/80 backdrop-blur-sm rounded-lg shadow-lg border-t-4 border-indigo-500 overflow-auto hide-scrollbar"
        >
          <div class="bg-indigo-50/50 p-3 border-b border-indigo-100 shrink-0">
            <h3
              class="text-lg font-bold text-indigo-900 text-center uppercase tracking-wider"
            >
              <slot name="left-title">{{ leftTitle }}</slot>
            </h3>
          </div>
          <div class="p-4 text-sm">
            <slot name="left" />
          </div>
        </div>
        <div
          class="flex flex-col bg-white/80 backdrop-blur-sm rounded-lg shadow-lg border-t-4 border-purple-500 overflow-auto hide-scrollbar"
        >
          <div class="bg-purple-50/50 p-3 border-b border-purple-100 shrink-0">
            <h3
              class="text-lg font-bold text-purple-900 text-center uppercase tracking-wider"
            >
              <slot name="right-title">{{ rightTitle }}</slot>
            </h3>
          </div>
          <div class="p-4 text-sm">
            <slot name="right" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
</style>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ title?: string; leftTitle?: string; rightTitle?: string }>();
</script>
