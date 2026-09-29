import React from "react";
import KnowledgeCategory from "./KnowledgeCategory";

export default function Discussions() {
  return (
    <KnowledgeCategory
      title="Discussions"
      subtitle="Guidance notes, circulars, and linked regulatory discussion threads."
      description="Non-core inputs that affect implementation planning, conflict posture, and interpretation quality."
      allowedTypes={["Circular", "Case", "Judgement", "Notification"]}
    />
  );
}

