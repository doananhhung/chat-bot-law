<template>
  <div
    class="slidev-layout h-full bg-slate-50 text-slate-800 font-sans relative overflow-hidden"
  >
    <ThemeBackground />
    <div
      class="relative z-10 h-full p-8 border-t-8 border-indigo-600 grid grid-rows-[auto_1fr] gap-6"
    >
      <h1
        class="text-4xl font-extrabold tracking-tight uppercase text-center bg-clip-text text-transparent bg-gradient-to-r from-indigo-700 to-purple-700"
      >
        <slot name="title">{{ title }}</slot>
      </h1>
      <div class="grid grid-cols-2 gap-10 h-full">
        <div
          class="flex flex-col bg-white/80 backdrop-blur-sm rounded-lg shadow-lg border-t-4 border-indigo-500 overflow-hidden"
        >
          <div class="bg-indigo-50/50 p-4 border-b border-indigo-100">
            <h3
              class="text-xl font-bold text-indigo-900 text-center uppercase tracking-wider"
            >
              <slot name="left-title">{{ leftTitle }}</slot>
            </h3>
          </div>
          <div class="p-6 flex-1 overflow-y-auto">
            <slot name="left" />
          </div>
        </div>
        <div
          class="flex flex-col bg-white/80 backdrop-blur-sm rounded-lg shadow-lg border-t-4 border-purple-500 overflow-hidden"
        >
          <div class="bg-purple-50/50 p-4 border-b border-purple-100">
            <h3
              class="text-xl font-bold text-purple-900 text-center uppercase tracking-wider"
            >
              <slot name="right-title">{{ rightTitle }}</slot>
            </h3>
          </div>
          <div class="p-6 flex-1 overflow-y-auto">
            <slot name="right" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeBackground from "./ThemeBackground.vue";
defineProps<{ title?: string; leftTitle?: string; rightTitle?: string }>();
</script>
