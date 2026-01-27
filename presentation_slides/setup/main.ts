import { defineAppSetup } from "@slidev/types";
import mermaid from "mermaid/dist/mermaid.esm.mjs";
import elkLayouts from "@mermaid-js/layout-elk";

// Register the ELK layout loader with Mermaid
mermaid.registerLayoutLoaders(elkLayouts);

export default defineAppSetup(() => {
  // You can add other app setup logic here if needed
});
