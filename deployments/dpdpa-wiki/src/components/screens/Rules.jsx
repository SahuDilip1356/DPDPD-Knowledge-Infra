import React from "react";
import KnowledgeCategory from "./KnowledgeCategory";

export default function Rules() {
  return (
    <KnowledgeCategory
      title="Rules"
      subtitle="Administrative rules, notifications, and implementation directives."
      description="Regulatory rules and notifications issued under the DPDP Act, with effective dates and dependencies."
      allowedTypes={["Rule"]}
    />
  );
}

