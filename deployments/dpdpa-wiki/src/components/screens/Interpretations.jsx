import React from "react";
import KnowledgeCategory from "./KnowledgeCategory";

export default function Interpretations() {
  return (
    <KnowledgeCategory
      title="Interpretations"
      subtitle="Opinionated interpretations, commentary, and advisory positions."
      description="Curated interpretations and explanatory notes mapped back to source law for operational decisions."
      allowedTypes={["Opinion"]}
    />
  );
}

