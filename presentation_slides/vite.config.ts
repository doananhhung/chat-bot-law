import { defineConfig } from "vite";

export default defineConfig({
  resolve: {
    alias: {
      dayjs: "dayjs/esm",
    },
  },
  optimizeDeps: {
    include: ["@braintree/sanitize-url"],
  },
});
