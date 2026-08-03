import React, { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";

/**
 * Bridges course state (owned by CertificationCourse) to the surrounding shell.
 *
 * CertificationCourse keeps all its own state — this context only mirrors the
 * slice the progress rail needs to render, plus a registry for the actions the
 * rail needs to fire back into the course (jumping to a module).
 */
const CourseProgressContext = createContext(null);

const INITIAL_PROGRESS = {
  phase: "onboarding",       // onboarding | diagnostic | learning | certificate
  activeTab: "curriculum",   // curriculum | interactive | exam | certificate
  currentModuleId: 0,
  completedModules: [],
  certIssued: false,
  userName: "",
  selectedLevel: "essentials"
};

function sameProgress(prev, next) {
  return Object.keys(next).every((key) => {
    const a = prev[key];
    const b = next[key];
    if (Array.isArray(a) && Array.isArray(b)) {
      return a.length === b.length && a.every((value, i) => value === b[i]);
    }
    return a === b;
  });
}

export function CourseProgressProvider({ children }) {
  const [progress, setProgress] = useState(INITIAL_PROGRESS);
  const actionsRef = useRef({});

  // Stable identity — safe to list in a useEffect dependency array.
  const publish = useCallback((next) => {
    setProgress((prev) => (sameProgress(prev, next) ? prev : { ...prev, ...next }));
  }, []);

  const registerActions = useCallback((actions) => {
    actionsRef.current = actions;
  }, []);

  const goToModule = useCallback((moduleId) => {
    actionsRef.current.goToModule?.(moduleId);
  }, []);

  const value = useMemo(
    () => ({ progress, publish, registerActions, goToModule }),
    [progress, publish, registerActions, goToModule]
  );

  return <CourseProgressContext.Provider value={value}>{children}</CourseProgressContext.Provider>;
}

export function useCourseProgress() {
  const ctx = useContext(CourseProgressContext);
  if (!ctx) {
    throw new Error("useCourseProgress must be used inside a CourseProgressProvider");
  }
  return ctx;
}

export default CourseProgressContext;
