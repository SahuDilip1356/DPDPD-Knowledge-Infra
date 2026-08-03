import React, { useState, useEffect } from "react";
import { SaralPrivacyLogo } from "../ui/SaralPrivacyLogo";
import { useCourseProgress } from "../CourseProgressContext";
import {
  INDUSTRY_PROFILES,
  ROLE_PROFILES,
  DIAGNOSTIC_QUESTIONS,
  MODULES_DATA,
  CERTIFICATION_EXAM_QUESTIONS,
  CAPABILITY_ACTION_PLAN_TEMPLATE
} from "../../data/certificationData";

export default function CertificationCourse({ onNavigate }) {
  // Navigation & State
  const [phase, setPhase] = useState("onboarding"); // onboarding | diagnostic | learning | certificate
  const [activeTab, setActiveTab] = useState("curriculum"); // curriculum | interactive | exam | certificate
  
  // User Onboarding State
  const [userName, setUserName] = useState("");
  const [userOrg, setUserOrg] = useState("");
  const [selectedIndustry, setSelectedIndustry] = useState("recruitment");
  const [selectedRole, setSelectedRole] = useState("hr");
  const [selectedLevel, setSelectedLevel] = useState("essentials"); // aware | essentials | champion | sector | partner

  // Diagnostic State
  const [diagAnswers, setDiagAnswers] = useState({});
  const [diagSubmitted, setDiagSubmitted] = useState(false);
  const [diagScore, setDiagScore] = useState(0);

  // Learning Progress State
  const [currentModuleId, setCurrentModuleId] = useState(1);
  const [completedModules, setCompletedModules] = useState([0]);

  // Interactive Exercises State
  const [dataHuntFound, setDataHuntFound] = useState([]);
  const [fieldMinimization, setFieldMinimization] = useState({
    name: true,
    phone: true,
    email: true,
    aadhaar: false,
    religion: false,
    fatherSalary: false
  });
  const [formNoticeFixed, setFormNoticeFixed] = useState(false);
  const [accessMatrix, setAccessMatrix] = useState({
    juniorRecruiter: "limited",
    seniorDpo: "full",
    thirdPartyVendor: "none"
  });
  const [retentionPeriod, setRetentionPeriod] = useState("2years");
  const [breachSequence, setBreachSequence] = useState([]);

  // Final Exam State
  const [examAnswers, setExamAnswers] = useState({});
  const [examSubmitted, setExamSubmitted] = useState(false);
  const [certIssued, setCertIssued] = useState(false);

  // ── Progress rail bridge ───────────────────────────────────────
  // CourseShell renders the module rail from this mirrored slice, and jumps
  // modules through the action it registers here.
  const { publish, registerActions } = useCourseProgress();

  useEffect(() => {
    publish({ phase, activeTab, currentModuleId, completedModules, certIssued, userName, selectedLevel });
  }, [publish, phase, activeTab, currentModuleId, completedModules, certIssued, userName, selectedLevel]);

  useEffect(() => {
    registerActions({
      goToModule: (modId) => {
        setCurrentModuleId(modId);
        setActiveTab("interactive");
      }
    });
  }, [registerActions]);

  // Helper data getters
  const currentIndustryObj = INDUSTRY_PROFILES.find(i => i.id === selectedIndustry) || INDUSTRY_PROFILES[0];
  const currentRoleObj = ROLE_PROFILES.find(r => r.id === selectedRole) || ROLE_PROFILES[0];
  const certificateId = `CERT-DPDPA-2026-${Math.floor(10000 + Math.random() * 90000)}`;

  // Handle Diagnostic Completion
  const handleDiagnosticSubmit = () => {
    let score = 0;
    DIAGNOSTIC_QUESTIONS.forEach((q) => {
      if (diagAnswers[q.id] === q.correctAnswer) score += 1;
    });
    setDiagScore(score);
    setDiagSubmitted(true);
    setPhase("learning");
    setCurrentModuleId(1);
  };

  // Handle Interactive Exercise Progress
  const markModuleCompleted = (modId) => {
    if (!completedModules.includes(modId)) {
      setCompletedModules([...completedModules, modId]);
    }
    if (modId < MODULES_DATA.length - 1) {
      setCurrentModuleId(modId + 1);
    } else {
      setActiveTab("exam");
    }
  };

  // Handle Exam Submit
  const handleExamSubmit = () => {
    if (!userName.trim()) {
      alert("Please enter your Full Name in the header before issuing your certificate.");
      return;
    }
    setExamSubmitted(true);
    setCertIssued(true);
    setPhase("certificate");
    setActiveTab("certificate");
  };

  // Calculate Exam Score
  const calculateExamScore = () => {
    let score = 0;
    CERTIFICATION_EXAM_QUESTIONS.forEach((q) => {
      if (examAnswers[q.id] === q.correctAnswer) score += 1;
    });
    return score;
  };

  return (
    <div className="certification-screen flex flex-col gap-6" style={{ paddingBottom: "50px" }}>
      
      {/* ── 1. HERO BRANDING & REGISTRATION BAR ────────────────────────────────────── */}
      <div 
        className="card"
        style={{
          background: "linear-gradient(135deg, #14213D 0%, #1A4FA3 100%)",
          color: "#FFFFFF",
          padding: "28px 32px",
          borderRadius: "20px",
          boxShadow: "0 12px 32px rgba(20, 33, 61, 0.2)",
          position: "relative",
          overflow: "hidden"
        }}
      >
        <div style={{ position: "absolute", right: "-10px", top: "-20px", opacity: 0.1, fontSize: "190px", pointerEvents: "none" }}>
          🛡️
        </div>

        <div className="flex justify-between items-start flex-wrap gap-4" style={{ position: "relative", zIndex: 2 }}>
          <div className="flex flex-col gap-2" style={{ maxWidth: "720px" }}>
            <div className="flex items-center gap-2">
              <span style={{ background: "#FF9933", color: "#FFFFFF", fontSize: "11px", fontWeight: 800, padding: "3px 10px", borderRadius: "9999px", textTransform: "uppercase" }}>
                SaralPrivacy Capability System
              </span>
              <span style={{ background: "rgba(255,255,255,0.15)", color: "#86EFAC", fontSize: "11px", fontWeight: 700, padding: "3px 10px", borderRadius: "9999px" }}>
                ✓ Industry-Adaptive DPDPA Business Certification
              </span>
            </div>

            <h1 style={{ fontSize: "26px", fontWeight: 900, margin: "6px 0", color: "#FFFFFF", lineHeight: 1.2 }}>
              SaralPrivacy Certified DPDPA Business Practitioner
            </h1>
            <p style={{ fontSize: "14px", color: "#E2E8F0", margin: 0, lineHeight: 1.5 }}>
              Learn DPDPA through your actual business workflows. Prove practical capability, create a 30-day compliance action plan, and earn a verified digital credential.
            </p>
          </div>

          {/* User Registration Inputs */}
          <div style={{ background: "rgba(255, 255, 255, 0.1)", backdropFilter: "blur(12px)", padding: "18px", borderRadius: "14px", border: "1px solid rgba(255, 255, 255, 0.2)", minWidth: "290px" }}>
            <div style={{ fontSize: "11px", fontWeight: 800, color: "#86EFAC", textTransform: "uppercase", marginBottom: "6px" }}>
              👤 Candidate Registration:
            </div>
            <input 
              type="text" 
              placeholder="Your Full Name (For Certificate)..." 
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              style={{ width: "100%", padding: "8px 12px", borderRadius: "8px", border: "1px solid #CBD5E1", fontSize: "13px", marginBottom: "8px" }}
            />
            <input 
              type="text" 
              placeholder="Company / Organization Name..." 
              value={userOrg}
              onChange={(e) => setUserOrg(e.target.value)}
              style={{ width: "100%", padding: "8px 12px", borderRadius: "8px", border: "1px solid #CBD5E1", fontSize: "13px" }}
            />
          </div>
        </div>
      </div>

      {/* ── 2. STACKABLE CERTIFICATION LADDER SELECTOR ────────────────────────────── */}
      <div className="card flex flex-col gap-3" style={{ background: "#FFFFFF", padding: "20px 24px", borderRadius: "16px", border: "1px solid var(--border)" }}>
        <div style={{ fontSize: "12px", fontWeight: 800, color: "#1A4FA3", textTransform: "uppercase" }}>
          🏅 Select Your Certification Level:
        </div>
        <div className="grid grid-5 gap-2">
          {[
            { id: "aware", level: "L1", title: "DPDPA Aware", duration: "30 Mins", target: "All Employees & Staff", bg: "#EFF6FF", color: "#1A4FA3" },
            { id: "essentials", level: "L2", title: "Business Essentials", duration: "90 Mins", target: "Founders, HR & Managers", bg: "#F0FDF4", color: "#166534", recommended: true },
            { id: "champion", level: "L3", title: "Privacy Champion", duration: "5 Hours", target: "Internal DPO & Leads", bg: "#FEF3C7", color: "#92400E" },
            { id: "sector", level: "L4", title: "Sector Practitioner", duration: "3 Hours", target: "Recruitment / CA / Health", bg: "#F3E8FF", color: "#6B21A8" },
            { id: "partner", level: "L5", title: "Implementation Pro", duration: "2 Days", target: "Consultants & CA Firms", bg: "#F1F5F9", color: "#334155" }
          ].map((item) => (
            <div 
              key={item.id}
              onClick={() => setSelectedLevel(item.id)}
              style={{
                background: selectedLevel === item.id ? item.bg : "#FAFAFA",
                border: selectedLevel === item.id ? `2px solid ${item.color}` : "1px solid #E2E8F0",
                borderRadius: "12px",
                padding: "12px",
                cursor: "pointer",
                position: "relative",
                transition: "all 150ms ease"
              }}
            >
              {item.recommended && (
                <span style={{ position: "absolute", top: "-8px", right: "8px", background: "#FF9933", color: "#FFFFFF", fontSize: "9px", fontWeight: 800, padding: "2px 6px", borderRadius: "9999px" }}>
                  CORE
                </span>
              )}
              <div style={{ fontSize: "10px", fontWeight: 800, color: item.color }}>{item.level} • {item.duration}</div>
              <div style={{ fontSize: "13px", fontWeight: 800, color: "var(--brand-navy)", margin: "2px 0" }}>{item.title}</div>
              <div style={{ fontSize: "11px", color: "var(--brand-slate)" }}>{item.target}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── 3. PHASE 1: ONBOARDING & INDUSTRY/ROLE DIAGNOSTIC START ──────────────── */}
      {phase === "onboarding" && (
        <div className="card flex flex-col gap-6" style={{ background: "#FFFFFF", padding: "28px", borderRadius: "16px", border: "1px solid var(--border)" }}>
          <div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
              🎯 Personalize Your Industry Learning Context
            </h2>
            <p className="text-small text-muted" style={{ margin: "4px 0 0 0" }}>
              SaralPrivacy adapts legal scenarios to your exact business role and operating tools.
            </p>
          </div>

          <div className="grid grid-2 gap-6">
            {/* Industry Selector */}
            <div className="flex flex-col gap-3">
              <label style={{ fontSize: "13px", fontWeight: 800, color: "var(--brand-navy)" }}>
                1. Select Your Business Industry:
              </label>
              <div className="flex flex-col gap-2">
                {INDUSTRY_PROFILES.map((ind) => (
                  <div
                    key={ind.id}
                    onClick={() => setSelectedIndustry(ind.id)}
                    style={{
                      background: selectedIndustry === ind.id ? "#EFF6FF" : "#F8FAFC",
                      border: selectedIndustry === ind.id ? "2px solid #1A4FA3" : "1px solid #E2E8F0",
                      borderRadius: "12px",
                      padding: "12px 16px",
                      cursor: "pointer",
                      display: "flex",
                      gap: "12px",
                      alignItems: "center"
                    }}
                  >
                    <span style={{ fontSize: "24px" }}>{ind.icon}</span>
                    <div>
                      <div style={{ fontSize: "14px", fontWeight: 800, color: "var(--brand-navy)" }}>{ind.name}</div>
                      <div style={{ fontSize: "12px", color: "var(--brand-slate)" }}>Scenario: {ind.storyTitle}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Role Selector */}
            <div className="flex flex-col gap-3">
              <label style={{ fontSize: "13px", fontWeight: 800, color: "var(--brand-navy)" }}>
                2. Select Your Work Role:
              </label>
              <div className="flex flex-col gap-2">
                {ROLE_PROFILES.map((r) => (
                  <div
                    key={r.id}
                    onClick={() => setSelectedRole(r.id)}
                    style={{
                      background: selectedRole === r.id ? "#F0FDF4" : "#F8FAFC",
                      border: selectedRole === r.id ? "2px solid #166534" : "1px solid #E2E8F0",
                      borderRadius: "12px",
                      padding: "12px 16px",
                      cursor: "pointer",
                      display: "flex",
                      gap: "12px",
                      alignItems: "center"
                    }}
                  >
                    <span style={{ fontSize: "24px" }}>{r.icon}</span>
                    <div>
                      <div style={{ fontSize: "14px", fontWeight: 800, color: "var(--brand-navy)" }}>{r.name}</div>
                      <div style={{ fontSize: "11px", color: "var(--brand-slate)" }}>Focus: {r.focus}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div style={{ background: "#FEF3C7", border: "1px solid #FCD34D", padding: "14px 18px", borderRadius: "12px", fontSize: "13px" }}>
            <div style={{ fontWeight: 800, color: "#92400E" }}>💡 Active Case Study Context:</div>
            <div style={{ color: "#78350F", marginTop: "2px" }}>
              You will complete simulations as <strong>{currentRoleObj.name}</strong> inside <strong>{currentIndustryObj.storyTitle}</strong> ({currentIndustryObj.description}).
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setPhase("diagnostic")}
              className="btn btn-primary"
              style={{ padding: "14px 28px", fontSize: "14px", fontWeight: 800 }}
            >
              Start 5-Minute Baseline Diagnostic ►
            </button>
          </div>

          {/* 12 Learning Modules Curriculum Preview */}
          <div style={{ borderTop: "2px dashed #E2E8F0", margin: "32px 0 24px 0" }}></div>

          <div style={{ textAlign: "center", margin: "20px 0 30px" }}>
            <h2 style={{ fontSize: "28px", fontWeight: 800, color: "#00509e", margin: "0 0 8px 0" }}>
              📚 Learning Modules Curriculum Syllabus
            </h2>
            <p style={{ fontSize: "14px", color: "var(--brand-slate)", margin: 0 }}>
              Complete all 12 modules through interactive business simulations to unlock your DPDPA certification
            </p>
          </div>

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap: "24px",
            marginBottom: "20px"
          }}>
            {MODULES_DATA.filter(m => m.id > 0).map((mod) => {
              let mainColor = "#00509e";
              let badgeGradient = "linear-gradient(135deg, #00509e 0%, #0066cc 100%)";
              if (mod.theme === "orange") {
                mainColor = "#ff6b35";
                badgeGradient = "linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%)";
              } else if (mod.theme === "indigo") {
                mainColor = "#5e35b1";
                badgeGradient = "linear-gradient(135deg, #5e35b1 0%, #7e57c2 100%)";
              }

              const promptRegistration = () => {
                alert("Please fill in candidate details and click 'Start 5-Minute Baseline Diagnostic' above to start this module!");
                window.scrollTo({ top: 0, behavior: 'smooth' });
              };

              return (
                <div
                  key={mod.id}
                  onClick={promptRegistration}
                  className="module-card-interactive"
                  style={{
                    background: "#FFFFFF",
                    border: `3px solid ${mainColor}`,
                    borderRadius: "15px",
                    padding: "24px",
                    position: "relative",
                    cursor: "pointer",
                    transition: "all 0.3s ease"
                  }}
                >
                  {/* Number badge */}
                  <div style={{
                    position: "absolute",
                    top: "16px",
                    right: "16px",
                    width: "44px",
                    height: "44px",
                    background: badgeGradient,
                    color: "#FFFFFF",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "18px",
                    fontWeight: "bold",
                    boxShadow: "0 3px 8px rgba(0,0,0,0.15)"
                  }}>
                    {mod.id}
                  </div>

                  {/* Title */}
                  <h3 style={{
                    color: mainColor,
                    fontSize: "17px",
                    fontWeight: 800,
                    margin: "0 0 16px 0",
                    paddingRight: "50px"
                  }}>
                    {mod.title}
                  </h3>

                  {/* Syllabus Checklist */}
                  <ul style={{
                    listStyle: "none",
                    padding: 0,
                    margin: "0 0 20px 0"
                  }}>
                    {mod.syllabus?.map((item, idx) => (
                      <li
                        key={idx}
                        style={{
                          padding: "6px 0 6px 24px",
                          position: "relative",
                          color: "#4A5568",
                          fontSize: "13px",
                          lineHeight: "1.4"
                        }}
                      >
                        <span style={{
                          position: "absolute",
                          left: 0,
                          color: "#28a745",
                          fontWeight: "bold"
                        }}>
                          ✓
                        </span>
                        {item}
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <div style={{
                    padding: "10px 16px",
                    background: badgeGradient,
                    color: "#FFFFFF",
                    textAlign: "center",
                    borderRadius: "8px",
                    fontWeight: "bold",
                    fontSize: "13px",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
                  }}>
                    Start Module {mod.id} →
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── 4. PHASE 2: ADAPTIVE DIAGNOSTIC ASSESSMENT ────────────────────────────── */}
      {phase === "diagnostic" && (
        <div className="card flex flex-col gap-6" style={{ background: "#FFFFFF", padding: "28px", borderRadius: "16px", border: "1px solid var(--border)" }}>
          <div>
            <div style={{ fontSize: "12px", fontWeight: 800, color: "#1A4FA3", textTransform: "uppercase" }}>
              STEP 01 OF 03 • DIAGNOSTIC BASELINE
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "var(--brand-navy)", margin: "4px 0 0 0" }}>
              📋 5-Question Adaptive Privacy Baseline Assessment
            </h2>
            <p className="text-small text-muted" style={{ margin: "4px 0 0 0" }}>
              Measures your baseline comprehension, risk recognition, and decision maturity to personalize your module sequence.
            </p>
          </div>

          <div className="flex flex-col gap-5">
            {DIAGNOSTIC_QUESTIONS.map((q, idx) => (
              <div key={q.id} style={{ background: "#F8FAFC", border: "1px solid #E2E8F0", borderRadius: "14px", padding: "18px" }}>
                <div style={{ fontSize: "11px", fontWeight: 800, color: "#64748B", textTransform: "uppercase", marginBottom: "4px" }}>
                  QUESTION 0{idx + 1} • COMPETENCY: {q.competency.toUpperCase().replace("_", " ")}
                </div>
                <h4 style={{ fontSize: "15px", fontWeight: 800, color: "var(--brand-navy)", margin: "0 0 12px 0", lineHeight: 1.4 }}>
                  {q.question}
                </h4>

                <div className="flex flex-col gap-2">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = diagAnswers[q.id] === optIdx;
                    return (
                      <div
                        key={optIdx}
                        onClick={() => setDiagAnswers({ ...diagAnswers, [q.id]: optIdx })}
                        style={{
                          background: isSelected ? "#EFF6FF" : "#FFFFFF",
                          border: isSelected ? "2px solid #1A4FA3" : "1px solid #CBD5E1",
                          borderRadius: "10px",
                          padding: "10px 14px",
                          fontSize: "13px",
                          fontWeight: isSelected ? 700 : 500,
                          color: isSelected ? "#1A4FA3" : "#334155",
                          cursor: "pointer"
                        }}
                      >
                        {isSelected ? "🔘 " : "⚪ "}{opt}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center">
            <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--brand-slate)" }}>
              Answered: {Object.keys(diagAnswers).length} / {DIAGNOSTIC_QUESTIONS.length} Questions
            </span>
            <button
              onClick={handleDiagnosticSubmit}
              className="btn btn-primary"
              style={{ padding: "12px 28px", fontSize: "14px", fontWeight: 800 }}
            >
              Analyze Score & Unlock Module Journey ►
            </button>
          </div>
        </div>
      )}

      {/* ── 5. PHASE 3: 12-MODULE INTERACTIVE CAPABILITY JOURNEY ─────────────────── */}
      {phase === "learning" && (
        <div className="flex flex-col gap-6">
          
          {/* Navigation Tabs */}
          <div style={{ display: "flex", gap: "12px", borderBottom: "2px solid var(--border)", paddingBottom: "2px" }}>
            <button
              onClick={() => setActiveTab("curriculum")}
              style={{
                padding: "10px 18px",
                fontSize: "13px",
                fontWeight: 800,
                color: activeTab === "curriculum" ? "var(--brand-navy)" : "var(--brand-slate)",
                background: "none",
                border: "none",
                borderBottom: activeTab === "curriculum" ? "3px solid var(--brand-green)" : "3px solid transparent",
                cursor: "pointer"
              }}
            >
              📚 Learning Modules
            </button>
            <button
              onClick={() => setActiveTab("interactive")}
              style={{
                padding: "10px 18px",
                fontSize: "13px",
                fontWeight: 800,
                color: activeTab === "interactive" ? "var(--brand-navy)" : "var(--brand-slate)",
                background: "none",
                border: "none",
                borderBottom: activeTab === "interactive" ? "3px solid var(--brand-green)" : "3px solid transparent",
                cursor: "pointer"
              }}
            >
              ⚡ Interactive Module {currentModuleId}: {MODULES_DATA[currentModuleId]?.title.split(":")[1] || "Practice"}
            </button>
            <button
              onClick={() => setActiveTab("exam")}
              style={{
                padding: "10px 18px",
                fontSize: "13px",
                fontWeight: 800,
                color: activeTab === "exam" ? "var(--brand-navy)" : "var(--brand-slate)",
                background: "none",
                border: "none",
                borderBottom: activeTab === "exam" ? "3px solid var(--brand-green)" : "3px solid transparent",
                cursor: "pointer"
              }}
            >
              📝 Final Certification Exam ({CERTIFICATION_EXAM_QUESTIONS.length} Qs)
            </button>
          </div>

          {/* TAB 1: CURRICULUM LIST */}
          {activeTab === "curriculum" && (
            <div className="flex flex-col gap-4">
              <div style={{ background: "#F0FDF4", border: "1px solid #86EFAC", padding: "16px 20px", borderRadius: "14px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: "12px", fontWeight: 800, color: "#166534", textTransform: "uppercase" }}>Diagnostic Baseline Result:</div>
                  <div style={{ fontSize: "16px", fontWeight: 800, color: "#14213D" }}>Score: {diagScore} / {DIAGNOSTIC_QUESTIONS.length} ({diagScore >= 4 ? "Advanced Baseline" : "Foundation Path Assigned"})</div>
                </div>
                <button
                  onClick={() => { setActiveTab("interactive"); setCurrentModuleId(1); }}
                  className="btn btn-primary"
                  style={{ padding: "10px 20px", fontSize: "13px", fontWeight: 800 }}
                >
                  Resume Module {currentModuleId} ►
                </button>
              </div>

              <div style={{ textAlign: "center", margin: "20px 0 30px" }}>
                <h2 style={{ fontSize: "28px", fontWeight: 800, color: "#00509e", margin: "0 0 8px 0" }}>
                  📚 Learning Modules
                </h2>
                <p style={{ fontSize: "14px", color: "var(--brand-slate)", margin: 0 }}>
                  Complete all 12 modules before taking the certification exam
                </p>
              </div>

              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
                gap: "24px",
                marginBottom: "40px"
              }}>
                {MODULES_DATA.filter(m => m.id > 0).map((mod) => {
                  const isCompleted = completedModules.includes(mod.id);
                  const isCurrent = currentModuleId === mod.id;
                  
                  let mainColor = "#00509e";
                  let hoverColor = "#0066cc";
                  let badgeGradient = "linear-gradient(135deg, #00509e 0%, #0066cc 100%)";
                  if (mod.theme === "orange") {
                    mainColor = "#ff6b35";
                    hoverColor = "#ff8c42";
                    badgeGradient = "linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%)";
                  } else if (mod.theme === "indigo") {
                    mainColor = "#5e35b1";
                    hoverColor = "#7e57c2";
                    badgeGradient = "linear-gradient(135deg, #5e35b1 0%, #7e57c2 100%)";
                  }

                  return (
                    <div
                      key={mod.id}
                      onClick={() => { setCurrentModuleId(mod.id); setActiveTab("interactive"); }}
                      className="module-card-interactive"
                      style={{
                        background: "#FFFFFF",
                        border: `3px solid ${mainColor}`,
                        borderRadius: "15px",
                        padding: "24px",
                        position: "relative",
                        cursor: "pointer",
                        boxShadow: isCurrent ? `0 10px 25px rgba(0,0,0,0.15)` : "none",
                        transition: "all 0.3s ease"
                      }}
                    >
                      <div style={{
                        position: "absolute",
                        top: "16px",
                        right: "16px",
                        width: "44px",
                        height: "44px",
                        background: badgeGradient,
                        color: "#FFFFFF",
                        borderRadius: "50%",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "18px",
                        fontWeight: "bold",
                        boxShadow: "0 3px 8px rgba(0,0,0,0.15)"
                      }}>
                        {mod.id}
                      </div>

                      <h3 style={{
                        color: mainColor,
                        fontSize: "18px",
                        fontWeight: 800,
                        margin: "0 0 16px 0",
                        paddingRight: "50px"
                      }}>
                        {mod.title}
                      </h3>

                      <ul style={{
                        listStyle: "none",
                        padding: 0,
                        margin: "0 0 20px 0"
                      }}>
                        {mod.syllabus?.map((item, idx) => (
                          <li
                            key={idx}
                            style={{
                              padding: "6px 0 6px 24px",
                              position: "relative",
                              color: "#4A5568",
                              fontSize: "13px",
                              lineHeight: "1.4"
                            }}
                          >
                            <span style={{
                              position: "absolute",
                              left: 0,
                              color: "#28a745",
                              fontWeight: "bold"
                            }}>
                              ✓
                            </span>
                            {item}
                          </li>
                        ))}
                      </ul>

                      <div style={{
                        padding: "10px 16px",
                        background: badgeGradient,
                        color: "#FFFFFF",
                        textAlign: "center",
                        borderRadius: "8px",
                        fontWeight: "bold",
                        fontSize: "13px",
                        boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
                      }}>
                        {isCompleted ? "✓ Completed" : `Start Module ${mod.id} →`}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 2: INTERACTIVE MODULE ENGINE */}
          {activeTab === "interactive" && (
            <div className="card flex flex-col gap-6" style={{ background: "#FFFFFF", padding: "28px", borderRadius: "16px", border: "1px solid var(--border)" }}>
              {/* Module Header */}
              <div className="flex justify-between items-start border-bottom pb-3">
                <div>
                  <span style={{ fontSize: "11px", fontWeight: 800, background: "#EFF6FF", color: "#1A4FA3", padding: "3px 10px", borderRadius: "9999px", textTransform: "uppercase" }}>
                    Module {currentModuleId} of 12 • {currentIndustryObj.name} Track
                  </span>
                  <h2 style={{ fontSize: "22px", fontWeight: 800, color: "var(--brand-navy)", margin: "8px 0 2px 0" }}>
                    {MODULES_DATA[currentModuleId]?.title}
                  </h2>
                  <p style={{ fontSize: "13px", color: "var(--brand-slate)", margin: 0 }}>
                    {MODULES_DATA[currentModuleId]?.summary}
                  </p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "11px", fontWeight: 800, color: "#64748B" }}>Active Context</div>
                  <div style={{ fontSize: "12px", fontWeight: 800, color: "#1A4FA3" }}>{currentIndustryObj.storyTitle}</div>
                </div>
              </div>

              {/* Story Context Banner */}
              {MODULES_DATA[currentModuleId]?.storySnippet && (
                <div style={{ background: "#F8FAFC", borderLeft: "4px solid #1A4FA3", padding: "14px 18px", borderRadius: "0 10px 10px 0", fontSize: "13px" }}>
                  <div style={{ fontWeight: 800, color: "#1A4FA3" }}>📖 Case Study Scenario ({currentIndustryObj.name}):</div>
                  <div style={{ color: "#334155", marginTop: "2px", lineHeight: 1.5 }}>
                    {MODULES_DATA[currentModuleId].storySnippet}
                  </div>
                </div>
              )}

              {/* ── INTERACTIVE EXERCISES BY MODULE TYPE ──────────────────────────────── */}
              
              {/* MODULE 1: PERSONAL DATA HUNT */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "data_hunt" && (
                <div style={{ background: "#F1F5F9", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "10px" }}>
                    🔍 Interactive Exercise: Click on all 4 items on this office desk that contain Digital Personal Data:
                  </div>
                  <div className="grid grid-2 gap-3">
                    {[
                      { id: "cv", name: "Candidate CV PDF on Google Drive", isPersonal: true, desc: "Contains Name, Phone, Address & Photo (Sec 2t)" },
                      { id: "weather", name: "Public Weather Forecast Sheet", isPersonal: false, desc: "Non-personal public environmental data" },
                      { id: "aadhaar", name: "Recruiter WhatsApp Chat with Aadhaar Photo", isPersonal: true, desc: "Unencrypted Aadhaar Direct Identifier" },
                      { id: "cctv", name: "Office Waiting Room CCTV Recording", isPersonal: true, desc: "Biometric & Visual Personal Data" },
                      { id: "calculator", name: "Company GST Rate Calculator", isPersonal: false, desc: "Standard tax formula spreadsheet" },
                      { id: "notes", name: "Interview Evaluation Notes with Candidate Name", isPersonal: true, desc: "Indirect combined personal evaluation" }
                    ].map((item) => {
                      const isFound = dataHuntFound.includes(item.id);
                      return (
                        <div
                          key={item.id}
                          onClick={() => {
                            if (!dataHuntFound.includes(item.id)) {
                              setDataHuntFound([...dataHuntFound, item.id]);
                            }
                          }}
                          style={{
                            background: isFound ? (item.isPersonal ? "#DCFCE7" : "#FEF2F2") : "#FFFFFF",
                            border: isFound ? (item.isPersonal ? "2px solid #166534" : "2px solid #991B1B") : "1px solid #CBD5E1",
                            padding: "12px",
                            borderRadius: "10px",
                            cursor: "pointer"
                          }}
                        >
                          <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A" }}>
                            {isFound ? (item.isPersonal ? "✅ Personal Data" : "❌ Non-Personal Data") : "📌 Click to Inspect: " + item.name}
                          </div>
                          {isFound && <div style={{ fontSize: "11px", color: "#475569", marginTop: "4px" }}>{item.desc}</div>}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* MODULE 2: FOLLOW THE CV */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "follow_the_cv" && (
                <div style={{ background: "#F1F5F9", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "12px" }}>
                    🗺️ Click each station in the recruitment flow to trace how 1 Candidate CV generates multiple copies:
                  </div>
                  <div className="flex flex-col gap-3">
                    {[
                      { step: 1, label: "1. Job Portal Intake", copy: "+1 Copy (Database Source)" },
                      { step: 2, label: "2. Recruiter Local Desktop Download", copy: "+1 Shadow Copy (Unencrypted)" },
                      { step: 3, label: "3. Shared via Recruiter Team WhatsApp Group", copy: "+1 Distributed Copy (Mobile Devices)" },
                      { step: 4, label: "4. Uploaded to Company ATS Cloud", copy: "+1 Centralized Copy" },
                      { step: 5, label: "5. Shared with External Enterprise Client (Email)", copy: "+1 Third-Party Copy" },
                      { step: 6, label: "6. Retained in Google Drive Archives", copy: "+1 Backup Copy" }
                    ].map((station) => (
                      <div 
                        key={station.step} 
                        onClick={() => {
                          if (!breachSequence.includes(station.step)) {
                            setBreachSequence([...breachSequence, station.step]);
                          }
                        }}
                        style={{
                          background: breachSequence.includes(station.step) ? "#EFF6FF" : "#FFFFFF",
                          border: breachSequence.includes(station.step) ? "2px solid #1A4FA3" : "1px solid #E2E8F0",
                          padding: "10px 14px",
                          borderRadius: "8px",
                          cursor: "pointer",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center"
                        }}
                      >
                        <span style={{ fontSize: "13px", fontWeight: 700 }}>{station.label}</span>
                        <span style={{ fontSize: "12px", color: "#1A4FA3", fontWeight: 800 }}>
                          {breachSequence.includes(station.step) ? station.copy : "➕ Click to Trace"}
                        </span>
                      </div>
                    ))}
                    <div style={{ fontSize: "13px", fontWeight: 800, color: "#14213D", textAlign: "right", marginTop: "8px" }}>
                      Total copies traced: {breachSequence.length} of 6
                    </div>
                  </div>
                </div>
              )}

              {/* MODULE 3: NEED IT OR REMOVE IT (DATA MINIMIZATION) */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "need_it_or_remove_it" && (
                <div style={{ background: "#F8FAFC", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "10px" }}>
                    📋 Data Minimizer: Toggle off fields that violate Purpose Limitation (Sec 4 & 6):
                  </div>
                  <div className="flex flex-col gap-2">
                    {[
                      { key: "name", label: "Full Name", necessary: true },
                      { key: "phone", label: "Mobile Number", necessary: true },
                      { key: "email", label: "Email Address", necessary: true },
                      { key: "aadhaar", label: "Aadhaar Card Scan (Initial Screening)", necessary: false },
                      { key: "religion", label: "Religion & Caste Info", necessary: false },
                      { key: "fatherSalary", label: "Parent Monthly Salary", necessary: false }
                    ].map((f) => (
                      <div key={f.key} className="flex justify-between items-center" style={{ background: "#FFFFFF", padding: "10px 14px", borderRadius: "8px", border: "1px solid #E2E8F0" }}>
                        <span style={{ fontSize: "13px", fontWeight: 700 }}>{f.label} {f.necessary ? "(Statutory Mandatory)" : "(Excessive Field)"}</span>
                        <button
                          onClick={() => setFieldMinimization({ ...fieldMinimization, [f.key]: !fieldMinimization[f.key] })}
                          className={`btn ${fieldMinimization[f.key] ? "btn-primary" : "btn-secondary"}`}
                          style={{ padding: "4px 12px", fontSize: "11px" }}
                        >
                          {fieldMinimization[f.key] ? "KEEP FIELD" : "REMOVE FIELD ✓"}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* MODULE 4: FIX THE FORM (NOTICE & CONSENT) */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "fix_the_form" && (
                <div style={{ background: "#FEF2F2", padding: "20px", borderRadius: "14px", border: "1px solid #FCA5A5" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#991B1B", marginBottom: "6px" }}>
                    ⚠️ Illegal Consent Notice Detected (Pre-ticked & Bundled Dark Pattern):
                  </div>
                  <div style={{ background: "#FFFFFF", padding: "14px", borderRadius: "8px", fontSize: "12px", color: "#334155", fontFamily: "monospace", marginBottom: "12px" }}>
                    {!formNoticeFixed ? (
                      `"By submitting this form, you agree to all present and future processing of your data by us and our third-party advertising partners." [☑ Pre-Ticked Box]`
                    ) : (
                      `"We process your contact details solely to evaluate your application. You may withdraw consent at any time by contacting our DPO at dpo@simplestaff.in. [ ☐ I Agree to Privacy Terms ]"`
                    )}
                  </div>
                  <button
                    onClick={() => setFormNoticeFixed(!formNoticeFixed)}
                    className="btn btn-primary"
                    style={{ padding: "8px 16px", fontSize: "12px", fontWeight: 800 }}
                  >
                    {formNoticeFixed ? "Reset Notice" : "Fix Notice to Section 5 Compliant Text ✨"}
                  </button>
                </div>
              )}

              {/* MODULE 5: Access Boundaries */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "who_should_see_it" && (
                <div style={{ background: "#F8FAFC", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "12px" }}>
                    🔐 Minimization matrix: Set the correct DPDPA access permissions for each role:
                  </div>
                  <div className="flex flex-col gap-3">
                    {[
                      { key: "juniorRecruiter", label: "Junior Recruiter (Candidate Sourcing)", options: ["none", "limited", "full"] },
                      { key: "seniorDpo", label: "DPO / Privacy Lead (Governance)", options: ["none", "limited", "full"] },
                      { key: "thirdPartyVendor", label: "Third-Party Marketing Vendor (Remarketing)", options: ["none", "limited", "full"] }
                    ].map((roleItem) => (
                      <div key={roleItem.key} className="flex justify-between items-center" style={{ background: "#FFFFFF", padding: "10px 14px", borderRadius: "8px", border: "1px solid #E2E8F0" }}>
                        <span style={{ fontSize: "13px", fontWeight: 700 }}>{roleItem.label}</span>
                        <div className="flex gap-2">
                          {roleItem.options.map((opt) => (
                            <button
                              key={opt}
                              onClick={() => setAccessMatrix({ ...accessMatrix, [roleItem.key]: opt })}
                              className="btn"
                              style={{
                                padding: "4px 8px",
                                fontSize: "11px",
                                background: accessMatrix[roleItem.key] === opt ? "#1A4FA3" : "#F1F5F9",
                                color: accessMatrix[roleItem.key] === opt ? "#FFFFFF" : "#334155"
                              }}
                            >
                              {opt.toUpperCase()}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                    {accessMatrix.juniorRecruiter === "limited" && accessMatrix.seniorDpo === "full" && accessMatrix.thirdPartyVendor === "none" && (
                      <div style={{ fontSize: "12px", color: "#166534", fontWeight: 800, textAlign: "center", marginTop: "6px" }}>
                        ✓ Access boundaries correctly configured to the Need-to-Know principle!
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* MODULE 6: BUILD A RETENTION RULE */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "build_retention_rule" && (
                <div style={{ background: "#F1F5F9", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "12px" }}>
                    ⏱️ Match statutory & operational records to their correct DPDPA retention rule:
                  </div>
                  <div className="flex flex-col gap-3">
                    {[
                      { label: "Client Invoices (Income Tax Act)", options: [{ v: "7years", l: "7 Years (Statutory Requirement)" }, { v: "permanent", l: "Permanent" }] },
                      { label: "Candidate CVs (Unused Sourcing Profiles)", options: [{ v: "2years", l: "2 Years (Defined Business Purpose)" }, { v: "7years", l: "7 Years" }] },
                      { label: "CCTV Footprints (Safety)", options: [{ v: "30days", l: "30 Days (Security Standard)" }, { v: "permanent", l: "Permanent" }] }
                    ].map((record, i) => (
                      <div key={i} className="flex justify-between items-center" style={{ background: "#FFFFFF", padding: "10px 14px", borderRadius: "8px", border: "1px solid #E2E8F0" }}>
                        <span style={{ fontSize: "13px", fontWeight: 700 }}>{record.label}</span>
                        <select 
                          value={retentionPeriod} 
                          onChange={(e) => setRetentionPeriod(e.target.value)}
                          style={{ padding: "4px 8px", borderRadius: "6px", border: "1px solid #CBD5E1", fontSize: "12px" }}
                        >
                          {record.options.map(o => (
                            <option key={o.v} value={o.v}>{o.l}</option>
                          ))}
                        </select>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* MODULE 7: DSAR WORKFLOW */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "dsar_workflow" && (
                <div style={{ background: "#F8FAFC", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "12px" }}>
                    📩 Click steps in sequence to handle a candidate access or erasure request:
                  </div>
                  <div className="grid grid-2 gap-2">
                    {[
                      { id: "dsar_1", label: "1. Receive & Authenticate Identity" },
                      { id: "dsar_2", label: "2. Record Request in Audit Log" },
                      { id: "dsar_3", label: "3. Query Data across Systems & Backups" },
                      { id: "dsar_4", label: "4. Apply Statutory Retention Holds" },
                      { id: "dsar_5", label: "5. Fulfill Request & Notify Principal" }
                    ].map((stepItem) => (
                      <div 
                        key={stepItem.id}
                        onClick={() => {
                          if (!dataHuntFound.includes(stepItem.id)) {
                            setDataHuntFound([...dataHuntFound, stepItem.id]);
                          }
                        }}
                        style={{
                          background: dataHuntFound.includes(stepItem.id) ? "#F0FDF4" : "#FFFFFF",
                          border: dataHuntFound.includes(stepItem.id) ? "2px solid #166534" : "1px solid #CBD5E1",
                          padding: "10px 14px",
                          borderRadius: "8px",
                          cursor: "pointer",
                          fontSize: "12px",
                          fontWeight: 700
                        }}
                      >
                        {dataHuntFound.includes(stepItem.id) ? "✓ Completed: " + stepItem.label : "⭕ Pending: " + stepItem.label}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* MODULE 8: REVIEW THE VENDOR */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "review_the_vendor" && (
                <div style={{ background: "#F1F5F9", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "12px" }}>
                    🤝 Verify compliance checklist before executing third-party contract:
                  </div>
                  <div className="flex flex-col gap-2">
                    {[
                      "Vendor has verified security controls matching ISO 27001",
                      "Automated deletion schedules at termination are guaranteed in contract",
                      "Data Hosting localization inside India is verified",
                      "Data Processing Agreement (DPA) signed by authorized signatory"
                    ].map((item, index) => (
                      <div key={index} className="flex items-center gap-3" style={{ background: "#FFFFFF", padding: "10px 14px", borderRadius: "8px", border: "1px solid #CBD5E1" }}>
                        <input type="checkbox" defaultChecked={index < 2} style={{ width: "16px", height: "16px" }} />
                        <span style={{ fontSize: "12px", fontWeight: 600 }}>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* MODULE 9: LOST LAPTOP BREACH SIMULATION */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "lost_laptop_breach" && (
                <div style={{ background: "#EFF6FF", padding: "20px", borderRadius: "14px", border: "1px solid #93C5FD" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#1E40AF", marginBottom: "8px" }}>
                    🚨 Emergency Incident Protocol: Click to execute 72-Hour Response Order:
                  </div>
                  <div className="flex flex-col gap-2">
                    {[
                      { step: 1, title: "1. Lock Remote Laptop Access & Contain Breach", desc: "Revoke cloud credentials immediately." },
                      { step: 2, title: "2. Notify Data Protection Board of India (DPBI)", desc: "Mandatory Rule 7 notification within 72 Hours." },
                      { step: 3, title: "3. Notify Affected Data Principals", desc: "Send mitigation guidance to affected individuals." }
                    ].map((s) => (
                      <div key={s.step} style={{ background: "#FFFFFF", padding: "10px 14px", borderRadius: "8px", border: "1px solid #CBD5E1", fontSize: "12px" }}>
                        <div style={{ fontWeight: 800, color: "#1A4FA3" }}>{s.title}</div>
                        <div style={{ color: "#475569" }}>{s.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* MODULE 10: PRIVACY REGISTER */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "privacy_register" && (
                <div style={{ background: "#F8FAFC", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "12px" }}>
                    🛡️ Verify your 5 mandatory compliance registers are configured:
                  </div>
                  <div className="grid grid-2 gap-3">
                    {[
                      { name: "Personal Data Inventory Register", active: true },
                      { name: "Consent Log & Proof Ledger", active: true },
                      { name: "DSAR Request & Erasure Log", active: false },
                      { name: "SaaS Vendor / Processor Register", active: true },
                      { name: "Breach Incident Register", active: false }
                    ].map((reg, i) => (
                      <div key={i} style={{ background: "#FFFFFF", padding: "12px", borderRadius: "10px", border: "1px solid #CBD5E1", display: "flex", justifyContent: "space-between", itemsCenter: "center" }}>
                        <span style={{ fontSize: "12px", fontWeight: 700 }}>{reg.name}</span>
                        <span style={{ fontSize: "10px", fontWeight: 800, background: reg.active ? "#DCFCE7" : "#FEF2F2", color: reg.active ? "#15803D" : "#991B1B", padding: "2px 6px", borderRadius: "4px" }}>
                          {reg.active ? "ACTIVE" : "INACTIVE"}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* MODULE 11: CAPSTONE SIMULATION */}
              {MODULES_DATA[currentModuleId]?.interactiveType === "capstone_simulation" && (
                <div style={{ background: "#F1F5F9", padding: "20px", borderRadius: "14px", border: "1px solid #CBD5E1" }}>
                  <div style={{ fontSize: "13px", fontWeight: 800, color: "#0F172A", marginBottom: "10px" }}>
                    🎓 DPDPA Capstone: Check top 4 compliance priority remediation points to submit:
                  </div>
                  <div className="flex flex-col gap-2">
                    {[
                      "Audit candidate forms & remove Aadhaar number scans from initial screen",
                      "Publish DPO contact info and set up clear DSAR email inbox",
                      "Implement role-based access to customer files on Drive",
                      "Sign Data Processing Agreements with all key SaaS vendors"
                    ].map((item, index) => (
                      <div key={index} className="flex items-center gap-3" style={{ background: "#FFFFFF", padding: "10px 14px", borderRadius: "8px", border: "1px solid #CBD5E1" }}>
                        <input type="checkbox" defaultChecked={true} style={{ width: "16px", height: "16px" }} />
                        <span style={{ fontSize: "12px", fontWeight: 700 }}>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* SARALPRIVACY TOOL BRIDGE CTA */}
              {MODULES_DATA[currentModuleId]?.toolBridge && (
                <div style={{ background: "#F0FDF4", border: "1px solid #86EFAC", padding: "16px 20px", borderRadius: "12px", display: "flex", justifyContent: "space-between", itemsCenter: "center" }}>
                  <div>
                    <div style={{ fontSize: "11px", fontWeight: 800, color: "#166534", textTransform: "uppercase" }}>SaralPrivacy Tool Bridge:</div>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#14213D" }}>{MODULES_DATA[currentModuleId].toolBridge.text}</div>
                  </div>
                  <button
                    onClick={() => onNavigate && onNavigate(MODULES_DATA[currentModuleId].toolBridge.actionScreen)}
                    className="btn btn-secondary"
                    style={{ padding: "8px 16px", fontSize: "12px", fontWeight: 800, background: "#166534", color: "#FFFFFF", border: "none" }}
                  >
                    {MODULES_DATA[currentModuleId].toolBridge.buttonText}
                  </button>
                </div>
              )}

              {/* Module Navigation Footer */}
              <div className="flex justify-between items-center pt-3 border-top">
                <button
                  disabled={currentModuleId <= 1}
                  onClick={() => setCurrentModuleId(currentModuleId - 1)}
                  className="btn btn-secondary"
                  style={{ padding: "10px 20px", fontSize: "13px" }}
                >
                  ◄ Previous Module
                </button>
                <button
                  onClick={() => markModuleCompleted(currentModuleId)}
                  className="btn btn-primary"
                  style={{ padding: "10px 24px", fontSize: "13px", fontWeight: 800 }}
                >
                  {currentModuleId < 12 ? "Complete Module & Advance ►" : "Proceed to Final Certification Exam ►"}
                </button>
              </div>
            </div>
          )}

          {/* TAB 3: FINAL CERTIFICATION EXAM */}
          {activeTab === "exam" && (
            <div className="card flex flex-col gap-6" style={{ background: "#FFFFFF", padding: "28px", borderRadius: "16px", border: "1px solid var(--border)" }}>
              <div>
                <h2 style={{ fontSize: "20px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
                  📝 DPDPA Business Practitioner Final Examination
                </h2>
                <p className="text-small text-muted" style={{ margin: "4px 0 0 0" }}>
                  Answer all 10 real-world scenario questions to issue your Verified Credential and 30-Day Action Plan.
                </p>
              </div>

              <div className="flex flex-col gap-5">
                {CERTIFICATION_EXAM_QUESTIONS.map((q, idx) => (
                  <div key={q.id} style={{ background: "#F8FAFC", border: "1px solid #E2E8F0", borderRadius: "14px", padding: "18px" }}>
                    <div style={{ fontSize: "11px", fontWeight: 800, color: "#1A4FA3", marginBottom: "4px" }}>
                      QUESTION 0{idx + 1} OF 10
                    </div>
                    <h4 style={{ fontSize: "15px", fontWeight: 800, color: "var(--brand-navy)", margin: "0 0 12px 0", lineHeight: 1.4 }}>
                      {q.question}
                    </h4>

                    <div className="flex flex-col gap-2">
                      {q.options.map((opt, optIdx) => {
                        const isSelected = examAnswers[q.id] === optIdx;
                        return (
                          <div
                            key={optIdx}
                            onClick={() => setExamAnswers({ ...examAnswers, [q.id]: optIdx })}
                            style={{
                              background: isSelected ? "#EFF6FF" : "#FFFFFF",
                              border: isSelected ? "2px solid #1A4FA3" : "1px solid #CBD5E1",
                              borderRadius: "10px",
                              padding: "10px 14px",
                              fontSize: "13px",
                              fontWeight: isSelected ? 700 : 500,
                              color: isSelected ? "#1A4FA3" : "#334155",
                              cursor: "pointer"
                            }}
                          >
                            {isSelected ? "🔘 " : "⚪ "}{opt}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-between items-center">
                <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--brand-slate)" }}>
                  Selected: {Object.keys(examAnswers).length} / {CERTIFICATION_EXAM_QUESTIONS.length} Questions
                </span>
                <button
                  onClick={handleExamSubmit}
                  className="btn btn-primary"
                  style={{ padding: "12px 28px", fontSize: "14px", fontWeight: 800 }}
                >
                  Submit Final Exam & Issue Credential 🎓
                </button>
              </div>
            </div>
          )}

        </div>
      )}

      {/* ── 6. PHASE 5: DUAL CREDENTIAL STUDIO (CERTIFICATE & CAPABILITY REPORT) ─── */}
      {phase === "certificate" && (
        <div className="flex flex-col gap-6 items-center">
          
          {/* Dual Tabs */}
          <div style={{ display: "flex", gap: "12px" }}>
            <button
              onClick={() => setActiveTab("certificate")}
              style={{
                padding: "10px 20px",
                fontSize: "14px",
                fontWeight: 800,
                color: activeTab === "certificate" ? "#FFFFFF" : "#1E293B",
                background: activeTab === "certificate" ? "#14213D" : "#E2E8F0",
                borderRadius: "10px",
                border: "none",
                cursor: "pointer"
              }}
            >
              📜 Verified Certificate
            </button>
            <button
              onClick={() => setActiveTab("report")}
              style={{
                padding: "10px 20px",
                fontSize: "14px",
                fontWeight: 800,
                color: activeTab === "report" ? "#FFFFFF" : "#1E293B",
                background: activeTab === "report" ? "#166534" : "#E2E8F0",
                borderRadius: "10px",
                border: "none",
                cursor: "pointer"
              }}
            >
              📊 Capability Report & 30-Day Action Plan
            </button>
          </div>

          {/* TAB A: VERIFIED CERTIFICATE CARD */}
          {activeTab === "certificate" && (
            <div 
              id="certificate-print-area"
              style={{
                width: "100%",
                maxWidth: "840px",
                background: "#FFFFFF",
                border: "12px solid #14213D",
                borderRadius: "20px",
                padding: "48px 40px",
                boxShadow: "0 20px 50px rgba(0,0,0,0.12)",
                position: "relative",
                textAlign: "center"
              }}
            >
              {/* Header */}
              <div className="flex justify-between items-center" style={{ borderBottom: "2px solid #E2E8F0", paddingBottom: "20px", marginBottom: "28px" }}>
                <SaralPrivacyLogo size={40} showTagline={false} />
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "10px", fontWeight: 800, color: "#64748B", textTransform: "uppercase" }}>Certificate Verification ID</div>
                  <div className="text-mono" style={{ fontSize: "13px", fontWeight: 800, color: "#1A4FA3" }}>{certificateId}</div>
                </div>
              </div>

              <div style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "2px", color: "#D97706", textTransform: "uppercase", marginBottom: "10px" }}>
                OFFICIAL DEMONSTRATED COMPLIANCE COMPETENCY CREDENTIAL
              </div>

              <h1 style={{ fontSize: "30px", fontWeight: 900, color: "#14213D", fontFamily: "Georgia, serif", margin: "0 0 14px 0" }}>
                Certificate of Completion
              </h1>

              <p style={{ fontSize: "14px", color: "#64748B", margin: "0 0 14px 0" }}>
                This digital credential certifies that
              </p>

              <div style={{ fontSize: "26px", fontWeight: 800, color: "#1A4FA3", borderBottom: "2px solid #1A4FA3", display: "inline-block", padding: "0 24px 4px 24px", marginBottom: "14px" }}>
                {userName || "DPDPA Practitioner Candidate"}
              </div>

              {userOrg && (
                <div style={{ fontSize: "14px", fontWeight: 700, color: "#334155", marginBottom: "18px" }}>
                  Representing: <span style={{ color: "#14213D" }}>{userOrg}</span> ({currentIndustryObj.name})
                </div>
              )}

              <p style={{ fontSize: "13px", color: "#475569", maxWidth: "640px", margin: "0 auto 28px auto", lineHeight: 1.6 }}>
                has successfully completed the <strong>SaralPrivacy DPDPA Business Practitioner Course</strong>, demonstrating verified competency across <strong>Digital Personal Data Protection Act (2023)</strong> obligations, <strong>DPDP Rules</strong>, and the <strong>OPERATE 7-Pillar Framework</strong>.
              </p>

              {/* Footer Details */}
              <div className="flex justify-between items-end" style={{ borderTop: "2px solid #E2E8F0", paddingTop: "20px", marginTop: "20px" }}>
                <div style={{ textAlign: "left" }}>
                  <div style={{ fontSize: "12px", fontWeight: 800, color: "#14213D" }}>SaralPrivacy Board of Review</div>
                  <div style={{ fontSize: "11px", color: "#64748B" }}>Digital Personal Data Protection Infrastructure</div>
                  <div style={{ fontSize: "11px", color: "#138808", fontWeight: 700, marginTop: "2px" }}>✓ Verified Statutory Ledger</div>
                </div>

                <div style={{ background: "#F0FDF4", border: "2px solid #86EFAC", padding: "8px 14px", borderRadius: "10px", textAlign: "center" }}>
                  <div style={{ fontSize: "18px" }}>🛡️</div>
                  <div style={{ fontSize: "9px", fontWeight: 800, color: "#166534" }}>VERIFIED BADGE</div>
                </div>

                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "12px", fontWeight: 800, color: "#14213D" }}>Issue Date</div>
                  <div style={{ fontSize: "12px", color: "#64748B" }}>{new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
                  <div style={{ fontSize: "11px", color: "#1A4FA3", fontWeight: 700, marginTop: "2px" }}>Exam Score: {calculateExamScore()} / 10</div>
                </div>
              </div>

            </div>
          )}

          {/* TAB B: BUSINESS CAPABILITY REPORT & 30-DAY ACTION PLAN */}
          {activeTab === "report" && (
            <div className="card flex flex-col gap-6" style={{ width: "100%", maxWidth: "840px", background: "#FFFFFF", padding: "32px", borderRadius: "20px", border: "1px solid var(--border)" }}>
              <div>
                <span style={{ fontSize: "11px", fontWeight: 800, background: "#F0FDF4", color: "#166534", padding: "3px 10px", borderRadius: "9999px", textTransform: "uppercase" }}>
                  Executive Compliance Deliverable
                </span>
                <h2 style={{ fontSize: "22px", fontWeight: 800, color: "var(--brand-navy)", margin: "6px 0 2px 0" }}>
                  📊 DPDPA Business Capability Report & 30-Day Action Plan
                </h2>
                <p style={{ fontSize: "13px", color: "#64748B", margin: 0 }}>
                  Prepared for <strong>{userName}</strong> ({userOrg || currentIndustryObj.storyTitle})
                </p>
              </div>

              {/* Competency Mastery Grid */}
              <div className="flex flex-col gap-3">
                <div style={{ fontSize: "13px", fontWeight: 800, color: "var(--brand-navy)" }}>1. Competency Mastery Assessment:</div>
                <div className="grid grid-2 gap-3">
                  {[
                    { domain: "Personal Data Discovery", status: "Mastered ✓", score: "92%" },
                    { domain: "Notice & Consent Alignment", status: "Mastered ✓", score: "88%" },
                    { domain: "Retention & Deletion Rules", status: "Developing", score: "75%" },
                    { domain: "Vendor Risk Controls", status: "Mastered ✓", score: "90%" },
                    { domain: "72-Hr Breach Protocol", status: "Mastered ✓", score: "95%" }
                  ].map((c, i) => (
                    <div key={i} className="flex justify-between items-center" style={{ background: "#F8FAFC", padding: "10px 14px", borderRadius: "8px", border: "1px solid #E2E8F0", fontSize: "12px" }}>
                      <span style={{ fontWeight: 700, color: "#334155" }}>{c.domain}</span>
                      <span style={{ fontWeight: 800, color: "#166534" }}>{c.status} ({c.score})</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 30-Day Action Plan Table */}
              <div className="flex flex-col gap-3">
                <div style={{ fontSize: "13px", fontWeight: 800, color: "var(--brand-navy)" }}>2. 30-Day Prioritized Implementation Roadmap:</div>
                <div className="flex flex-col gap-3">
                  {CAPABILITY_ACTION_PLAN_TEMPLATE.map((phaseItem, idx) => (
                    <div key={idx} style={{ background: "#FAFAFA", border: "1px solid #E2E8F0", borderRadius: "10px", padding: "14px" }}>
                      <div className="flex justify-between items-center" style={{ marginBottom: "6px" }}>
                        <span style={{ fontSize: "11px", fontWeight: 800, background: "#1A4FA3", color: "#FFFFFF", padding: "2px 8px", borderRadius: "6px" }}>
                          {phaseItem.dayRange}
                        </span>
                        <span style={{ fontSize: "12px", fontWeight: 800, color: "var(--brand-navy)" }}>{phaseItem.phase}</span>
                      </div>
                      <ul style={{ margin: "4px 0 0 16px", padding: 0, fontSize: "12px", color: "#475569", lineHeight: 1.5 }}>
                        {phaseItem.actions.map((act, actIdx) => (
                          <li key={actIdx}>{act}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button 
              onClick={() => window.print()} 
              className="btn btn-primary" 
              style={{ padding: "12px 24px", fontSize: "14px", fontWeight: 800 }}
            >
              🖨️ Print / Download PDF Credential & Report
            </button>
            <button 
              onClick={() => alert(`Share your credential on LinkedIn!\n\nI am proud to share that I have completed the SaralPrivacy DPDPA Business Practitioner Masterclass (Verification ID: ${certificateId})!`)} 
              className="btn btn-secondary" 
              style={{ padding: "12px 24px", fontSize: "14px", fontWeight: 800, background: "#0A66C2", color: "#FFFFFF", border: "none" }}
            >
              💼 Share Credential on LinkedIn
            </button>
          </div>

        </div>
      )}

    </div>
  );
}
