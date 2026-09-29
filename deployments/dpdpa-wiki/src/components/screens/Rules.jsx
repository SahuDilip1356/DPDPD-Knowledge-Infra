import React from "react";
import KnowledgeCategory from "./KnowledgeCategory";

// Module-level so its identity is stable across renders (it is a hook dependency).
const ALLOWED_TYPES = ["Rule"];

export default function Rules() {
  return (
    <KnowledgeCategory
      title="Rules"
      subtitle="Administrative rules, notifications, and implementation directives."
      description="Regulatory rules and notifications issued under the DPDP Act, with effective dates and dependencies."
      allowedTypes={ALLOWED_TYPES}
    />
  );
}

