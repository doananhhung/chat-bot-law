<template>
  <div class="absolute inset-0 z-0 pointer-events-none overflow-hidden">
    <!-- 1. Corporate Structure in Background shapes -->
    <div
      class="absolute top-0 right-0 w-1/3 h-full bg-blue-50/70 skew-x-12 transform origin-top-right"
    ></div>

    <!-- 2. Vibrant Soft Gradients -->
    <div
      class="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-purple-200/80 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob"
    ></div>
    <div
      class="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-indigo-200/80 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000"
    ></div>

    <!-- Optional: Subtle Grid Texture -->
    <div
      class="absolute inset-0 opacity-[0.03]"
      style="
        background-image: radial-gradient(#6366f1 1px, transparent 1px);
        background-size: 32px 32px;
      "
    ></div>
  </div>
</template>
