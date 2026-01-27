import { defineMermaidSetup } from "@slidev/types";

export default defineMermaidSetup(() => {
  return {
    theme: "base",
    themeVariables: {
      // Subgraph styling
      clusterBkg: "#e0e7ff", // indigo-100
      clusterBorder: "#6366f1", // indigo-500
      clusterTextColor: "#000000", // black - for subgraph titles

      // Primary node styling (default)
      primaryColor: "#c7d2fe", // indigo-200
      primaryTextColor: "#1e1b4b", // indigo-950
      primaryBorderColor: "#6366f1", // indigo-500

      // Secondary node styling (for variety)
      secondaryColor: "#ddd6fe", // violet-200
      secondaryTextColor: "#1e1b4b",
      secondaryBorderColor: "#8b5cf6", // violet-500

      // Tertiary node styling
      tertiaryColor: "#e0e7ff", // indigo-100
      tertiaryTextColor: "#1e1b4b",
      tertiaryBorderColor: "#6366f1",

      // Node background (fixes black fill issue)
      nodeBkg: "#c7d2fe",
      nodeTextColor: "#1e1b4b",
      nodeBorder: "#6366f1",

      // Main background
      mainBkg: "#c7d2fe",
      background: "#f8fafc",

      // Line/edge styling
      lineColor: "#6366f1",
      textColor: "#1e1b4b",

      // Edge label styling (fixes label color issue)
      edgeLabelBackground: "#ffffff",

      // Sequence diagram styling (fixes gray text issue)
      actorTextColor: "#000000", // participant names
      actorBkg: "#c7d2fe", // participant box background
      actorBorder: "#6366f1",
      actorLineColor: "#6366f1",
      signalColor: "#000000", // arrow labels
      signalTextColor: "#000000", // message text on arrows
      labelTextColor: "#000000",
      loopTextColor: "#000000",
      noteTextColor: "#000000",
      noteBkgColor: "#fef3c7", // amber-100 for notes
      noteBorderColor: "#f59e0b", // amber-500
      activationBkgColor: "#ddd6fe", // violet-200
      activationBorderColor: "#8b5cf6",
      sequenceNumberColor: "#ffffff",
    },
    flowchart: {
      defaultRenderer: "elk",
      useMaxWidth: false,
      htmlLabels: true,
      curve: "basis",
    },
    elk: {
      nodePlacementStrategy: "NETWORK_SIMPLEX",
    },
  };
});


