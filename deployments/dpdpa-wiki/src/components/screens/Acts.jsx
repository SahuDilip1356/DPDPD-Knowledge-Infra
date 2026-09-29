import React from "react";
import KnowledgeCategory from "./KnowledgeCategory";

// Module-level so its identity is stable across renders (it is a hook dependency).
const ALLOWED_TYPES = ["Act"];

export default function Acts() {
  return (
    <KnowledgeCategory
      title="Acts"
      subtitle="Chronological versions of core statutory acts and their applicability."
      description="Statutory enactments with legal effect in India and mapped implementation timeline."
      allowedTypes={ALLOWED_TYPES}
    />
  );
}

