import React from "react";
import KnowledgeCategory from "./KnowledgeCategory";

// Module-level so its identity is stable across renders (it is a hook dependency).
const ALLOWED_TYPES = ["Circular", "Case", "Judgement", "Notification"];

export default function Discussions() {
  return (
    <KnowledgeCategory
      title="Discussions"
      subtitle="Guidance notes, circulars, and linked regulatory discussion threads."
      description="Non-core inputs that affect implementation planning, conflict posture, and interpretation quality."
      allowedTypes={ALLOWED_TYPES}
    />
  );
}

