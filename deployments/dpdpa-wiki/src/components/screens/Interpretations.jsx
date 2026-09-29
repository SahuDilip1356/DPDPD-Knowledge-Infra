import React from "react";
import KnowledgeCategory from "./KnowledgeCategory";

// Module-level so its identity is stable across renders (it is a hook dependency).
const ALLOWED_TYPES = ["Opinion"];

export default function Interpretations() {
  return (
    <KnowledgeCategory
      title="Interpretations"
      subtitle="Opinionated interpretations, commentary, and advisory positions."
      description="Curated interpretations and explanatory notes mapped back to source law for operational decisions."
      allowedTypes={ALLOWED_TYPES}
    />
  );
}

