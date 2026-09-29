import React from "react";
import KnowledgeCategory from "./KnowledgeCategory";

export default function Acts() {
  return (
    <KnowledgeCategory
      title="Acts"
      subtitle="Chronological versions of core statutory acts and their applicability."
      description="Statutory enactments with legal effect in India and mapped implementation timeline."
      allowedTypes={["Act"]}
    />
  );
}

