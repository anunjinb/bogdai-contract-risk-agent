/* ============================================================
   BogdAI — Contract Risk Monitoring
   Single-file React app. Reads analysis JSON, no external calls.
   Visual language: BogdAI Design System (cream / ink / blue).
   ============================================================ */
const { useState, useEffect, useRef, useCallback } = React;

/* ---------- Embedded sample analysis (the demo contract) ---------- */
const SAMPLE_REPORT = {
  schema_version: "1.0",
  analysis_id: "BDA-F9CE5F67",
  contract_name: "test_contract_1.txt",
  source_document: "test_contract_1.txt",
  analysis_date: "2026-06-09",
  analysis_mode: "synthetic_demo",
  overall_assessment: {
    overall_risk_level: "CRITICAL",
    risk_score: 83,
    summary: "4 high-risk clause(s), 2 medium-risk clause(s) identified. Key issues: Pricing – Vague Adjustment Language; Liability – Missing or Unlimited Cap; Liability – Absent Liability Cap Clause.",
    human_review_required: true,
  },
  risk_breakdown: { high: 4, medium: 2, low: 0, informational: 0 },
  flags: [
    {
      flag_id: "FLAG-001", clause: "7.1", title: "Pricing – Vague Adjustment Language",
      risk_category: "Financial", risk_level: "HIGH", risk_score: 80,
      issue: "Vague pricing adjustment terms without a defined cap or review mechanism expose the buyer to unpredictable cost increases.",
      clause_excerpt: "[Synthetic excerpt] The contract states: 'Pricing Terms — price may change.' Refer to the full contract text for the exact language.",
      business_impact: "Uncapped pricing adjustments can create budget overruns and contract disputes, destabilizing procurement planning.",
      patient_impact: "Uncontrolled cost increases may force formulary changes or reduce treatment access for patients on budget-constrained programs.",
      reasoning_steps: [
        { step: 1, observation: "The contract contains language matching the pattern \"price may change\", which is associated with a known risk area.", inference: "The identified language in 'Pricing – Vague Adjustment Language' creates potential financial exposure that requires evaluation." },
        { step: 2, observation: "The grounded knowledge source states: \"Vague pricing adjustment language without a defined cap or structured review process materially increases financial dispute risk.\"", inference: "The contract language in 'Pricing – Vague Adjustment Language' appears misaligned with the expected standard described in the knowledge source." },
        { step: 3, observation: "This clause affects regulated pharma supply and hospital operations under the Financial category.", inference: "The risk level is HIGH because vague pricing adjustment terms without a defined cap or review mechanism expose the buyer to unpredictable cost increases." },
      ],
      recommendation: "Define a maximum annual price adjustment percentage, tie any adjustment to a published index (e.g., CPI), and require 90-day advance notice.",
      citations: [{ citation_id: "CIT-001", source_title: "Synthetic Pharma Contracting Guidelines", source_document: "synthetic_pharma_contracting_guidelines.md", section: "Pricing Terms", quoted_evidence: "Vague pricing adjustment language without a defined cap or structured review process materially increases financial dispute risk.", grounding_layer: "Foundry IQ", retrieval_confidence: 0.87 }],
      confidence: 0.83, needs_human_review: true,
    },
    {
      flag_id: "FLAG-002", clause: "9.3", title: "Liability – Missing or Unlimited Cap",
      risk_category: "Legal", risk_level: "HIGH", risk_score: 88,
      issue: "The contract imposes unlimited liability or explicitly removes any liability cap, creating extreme financial risk exposure.",
      clause_excerpt: "[Synthetic excerpt] The contract states: 'Liability — unlimited liability.' Refer to the full contract text for the exact language.",
      business_impact: "Unlimited liability exposure can result in catastrophic financial loss in the event of breach, product recall, or regulatory action.",
      patient_impact: "Excessive liability exposure may deter suppliers from contracting, risking supply disruption and treatment delays.",
      reasoning_steps: [
        { step: 1, observation: "The contract contains language matching the pattern \"unlimited liability\", which is associated with a known risk area.", inference: "The identified language in 'Liability – Missing or Unlimited Cap' creates potential legal exposure that requires evaluation." },
        { step: 2, observation: "The grounded knowledge source states: \"Pharma contracts should define explicit liability caps, exclusions, and a structured review process to protect both parties.\"", inference: "The contract language in 'Liability – Missing or Unlimited Cap' appears misaligned with the expected standard described in the knowledge source." },
        { step: 3, observation: "This clause affects regulated pharma supply and hospital operations under the Legal category.", inference: "The risk level is HIGH because the contract imposes unlimited liability or explicitly removes any liability cap, creating extreme financial risk exposure." },
      ],
      recommendation: "Negotiate a mutual liability cap tied to contract value or insurance coverage. Define exclusions clearly (e.g., gross negligence, fraud).",
      citations: [{ citation_id: "CIT-002", source_title: "Synthetic Pharma Contracting Guidelines", source_document: "synthetic_pharma_contracting_guidelines.md", section: "Liability and Indemnification", quoted_evidence: "Pharma contracts should define explicit liability caps, exclusions, and a structured review process to protect both parties.", grounding_layer: "Foundry IQ", retrieval_confidence: 0.89 }],
      confidence: 0.88, needs_human_review: true,
    },
    {
      flag_id: "FLAG-003", clause: "9.3", title: "Liability – Absent Liability Cap Clause",
      risk_category: "Legal", risk_level: "HIGH", risk_score: 85,
      issue: "No explicit liability cap or limitation clause was found. This leaves financial exposure undefined.",
      clause_excerpt: "[Synthetic excerpt] The contract states: 'Liability — liability cap.' Refer to the full contract text for the exact language.",
      business_impact: "Without a liability cap, both parties face unpredictable financial exposure in any dispute or breach scenario.",
      patient_impact: "Supplier withdrawal risk increases when liability terms are open-ended, potentially impacting treatment supply continuity.",
      reasoning_steps: [
        { step: 1, observation: "The contract contains language matching the pattern \"liability cap\", which is associated with a known risk area.", inference: "The identified language in 'Liability – Absent Liability Cap Clause' creates potential legal exposure that requires evaluation." },
        { step: 2, observation: "The grounded knowledge source states: \"Pharma contracts should define explicit liability caps, exclusions, and a structured review process to protect both parties.\"", inference: "The contract language in 'Liability – Absent Liability Cap Clause' appears misaligned with the expected standard described in the knowledge source." },
        { step: 3, observation: "This clause affects regulated pharma supply and hospital operations under the Legal category.", inference: "The risk level is HIGH because no explicit liability cap or limitation clause was found. This leaves financial exposure undefined." },
      ],
      recommendation: "Add a clearly defined mutual liability cap clause specifying maximum liability amounts, exclusions, and indemnification obligations.",
      citations: [{ citation_id: "CIT-003", source_title: "Synthetic Pharma Contracting Guidelines", source_document: "synthetic_pharma_contracting_guidelines.md", section: "Liability and Indemnification", quoted_evidence: "Pharma contracts should define explicit liability caps, exclusions, and a structured review process to protect both parties.", grounding_layer: "Foundry IQ", retrieval_confidence: 0.85 }],
      confidence: 0.85, needs_human_review: true,
    },
    {
      flag_id: "FLAG-004", clause: "5.4", title: "Supply Chain – Delivery Without Escalation Timeline",
      risk_category: "Operational", risk_level: "HIGH", risk_score: 82,
      issue: "Delivery terms conditioned on availability without a defined escalation timeline or substitution process create supply continuity risk.",
      clause_excerpt: "[Synthetic excerpt] The contract states: 'Delivery / Supply Obligations — subject to availability.' Refer to the full contract text for the exact language.",
      business_impact: "Open-ended delivery terms prevent effective inventory planning and can lead to treatment stock-outs.",
      patient_impact: "Supply interruptions without escalation obligations may directly delay patient access to critical treatments.",
      reasoning_steps: [
        { step: 1, observation: "The contract contains language matching the pattern \"subject to availability\", which is associated with a known risk area.", inference: "The identified language in 'Supply Chain – Delivery Without Escalation Timeline' creates potential operational exposure that requires evaluation." },
        { step: 2, observation: "The grounded knowledge source states: \"Procurement contracts must define delivery timelines, escalation paths, and contingency obligations when primary supply is unavailable.\"", inference: "The contract language in 'Supply Chain – Delivery Without Escalation Timeline' appears misaligned with the expected standard described in the knowledge source." },
        { step: 3, observation: "This clause affects regulated pharma supply and hospital operations under the Operational category.", inference: "The risk level is HIGH because delivery terms conditioned on availability without a defined escalation timeline or substitution process create supply continuity risk." },
      ],
      recommendation: "Specify maximum delivery lead times, define escalation steps when availability is constrained, and require advance notification of supply interruptions.",
      citations: [{ citation_id: "CIT-004", source_title: "Synthetic Healthcare Procurement Rules", source_document: "synthetic_healthcare_procurement_rules.md", section: "Supply Continuity and Escalation", quoted_evidence: "Procurement contracts must define delivery timelines, escalation paths, and contingency obligations when primary supply is unavailable.", grounding_layer: "Foundry IQ", retrieval_confidence: 0.88 }],
      confidence: 0.84, needs_human_review: true,
    },
    {
      flag_id: "FLAG-005", clause: "4.2", title: "Audit Rights – Missing or Unclear",
      risk_category: "Compliance", risk_level: "MEDIUM", risk_score: 60,
      issue: "Audit rights are absent or insufficiently defined, limiting visibility into supplier compliance, quality, and pricing.",
      clause_excerpt: "[Synthetic excerpt] The contract states: 'Audit Rights — audit rights.' Refer to the full contract text for the exact language.",
      business_impact: "Without clear audit rights, billing discrepancies and non-compliance may go undetected until significant damage has occurred.",
      patient_impact: "Inadequate audit rights may mask quality or GMP compliance gaps that affect product safety.",
      reasoning_steps: [
        { step: 1, observation: "The contract contains language matching the pattern \"audit rights\", which is associated with a known risk area.", inference: "The identified language in 'Audit Rights – Missing or Unclear' creates potential compliance exposure that requires evaluation." },
        { step: 2, observation: "The grounded knowledge source states: \"Contracts with regulated suppliers should include defined audit rights with clear scope, frequency, and escalation procedures.\"", inference: "The contract language in 'Audit Rights – Missing or Unclear' appears misaligned with the expected standard described in the knowledge source." },
        { step: 3, observation: "This clause affects regulated pharma supply and hospital operations under the Compliance category.", inference: "The risk level is MEDIUM because audit rights are absent or insufficiently defined, limiting visibility into supplier compliance, quality, and pricing." },
      ],
      recommendation: "Include clear audit rights specifying frequency, scope, notice period, records access, and remediation obligations.",
      citations: [{ citation_id: "CIT-005", source_title: "Synthetic Compliance Policy", source_document: "synthetic_compliance_policy.md", section: "Audit and Oversight", quoted_evidence: "Contracts with regulated suppliers should include defined audit rights with clear scope, frequency, and escalation procedures.", grounding_layer: "Foundry IQ", retrieval_confidence: 0.82 }],
      confidence: 0.69, needs_human_review: false,
    },
    {
      flag_id: "FLAG-006", clause: "5.4", title: "Termination – Convenience Termination Without Adequate Notice",
      risk_category: "Operational", risk_level: "MEDIUM", risk_score: 65,
      issue: "Termination for convenience clause may allow abrupt contract end without sufficient transition time, risking supply disruption.",
      clause_excerpt: "[Synthetic excerpt] The contract states: 'Termination — terminate for convenience.' Refer to the full contract text for the exact language.",
      business_impact: "Abrupt termination without a wind-down period disrupts procurement planning and may require emergency sourcing.",
      patient_impact: "Sudden termination of a drug supply contract can interrupt patient treatment programs with no transition plan.",
      reasoning_steps: [
        { step: 1, observation: "The contract contains language matching the pattern \"terminate for convenience\", which is associated with a known risk area.", inference: "The identified language in 'Termination – Convenience Termination Without Adequate Notice' creates potential operational exposure that requires evaluation." },
        { step: 2, observation: "The grounded knowledge source states: \"Healthcare procurement contracts should require adequate notice periods for termination to protect supply continuity and patient care.\"", inference: "The contract language in 'Termination – Convenience Termination Without Adequate Notice' appears misaligned with the expected standard described in the knowledge source." },
        { step: 3, observation: "This clause affects regulated pharma supply and hospital operations under the Operational category.", inference: "The risk level is MEDIUM because termination for convenience clause may allow abrupt contract end without sufficient transition time, risking supply disruption." },
      ],
      recommendation: "Require a minimum 90-day notice for termination for convenience. Include transition obligations and supply bridge commitments.",
      citations: [{ citation_id: "CIT-006", source_title: "Synthetic Healthcare Procurement Rules", source_document: "synthetic_healthcare_procurement_rules.md", section: "Contract Termination", quoted_evidence: "Healthcare procurement contracts should require adequate notice periods for termination to protect supply continuity and patient care.", grounding_layer: "Foundry IQ", retrieval_confidence: 0.79 }],
      confidence: 0.71, needs_human_review: false,
    },
  ],
  agent_trace: [
    { agent_name: "Contract Intake Agent", role: "Prepared the uploaded contract for analysis.", tool_used: null, output: "Detected contract 'test_contract_1.txt' with 17 sections and 831 words. Synthetic: True." },
    { agent_name: "Clause Extraction Agent", role: "Identified contract clauses relevant to pharma and healthcare risk.", tool_used: null, output: "Extracted compliance, pricing, liability, reporting, and delivery clauses." },
    { agent_name: "Grounding Agent", role: "Retrieved supporting evidence from approved synthetic knowledge sources.", tool_used: "Foundry IQ (local synthetic fallback)", output: "Retrieved citations for 6 risk flags from 3 synthetic knowledge source(s)." },
    { agent_name: "Risk Reasoning Agent", role: "Compared contract language against grounded rules and inferred risk severity.", tool_used: null, output: "Assigned risk levels and produced step-by-step reasoning." },
    { agent_name: "Verifier Agent", role: "Checked for unsupported claims, missing citations, and unsafe recommendations.", tool_used: null, output: "Marked 4 high-risk flags as requiring human legal/compliance review." },
    { agent_name: "Report Agent", role: "Formatted the final JSON response for UI display.", tool_used: null, output: "Generated structured risk report." },
  ],
  grounding_summary: {
    iq_layer_used: "Foundry IQ",
    knowledge_sources_used: ["synthetic_healthcare_procurement_rules.md", "synthetic_pharma_contracting_guidelines.md", "synthetic_compliance_policy.md"],
    total_citations: 6, unsupported_claims_detected: 0,
  },
  safety_and_limits: {
    synthetic_data_only: true, contains_pii: false,
    legal_advice_disclaimer: "This analysis is for hackathon demonstration only and does not replace legal, regulatory, clinical, or compliance review.",
    requires_human_approval_before_action: true,
  },
  ui_hints: { primary_badge: "CRITICAL RISK", recommended_next_action: "Send to compliance reviewer immediately", show_agent_trace: true, show_citations: true },
};

/* ---------- Risk level → palette ---------- */
function riskTone(level) {
  const L = (level || "").toUpperCase();
  if (L === "CRITICAL" || L === "HIGH")
    return { fg: "text-red", bg: "bg-redwash", border: "border-red", dot: "bg-red", barVar: "var(--red)" };
  if (L === "MEDIUM")
    return { fg: "text-amber", bg: "bg-amberwash", border: "border-amber", dot: "bg-amber", barVar: "var(--amber)" };
  return { fg: "text-green", bg: "bg-greenwash", border: "border-green", dot: "bg-green", barVar: "var(--green)" };
}
const pct = (n) => `${Math.round(n * 100)}%`;

/* ============================================================
   ICONS — line-first, 1.5px stroke (BogdAI iconography)
   ============================================================ */
function Glyph({ size = 26, className = "" }) {
  const rays = [];
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * Math.PI * 2 - Math.PI / 2;
    const r1 = 7.4, r2 = 11.2, cx = 12, cy = 12;
    rays.push(<line key={i} x1={cx + Math.cos(a) * r1} y1={cy + Math.sin(a) * r1} x2={cx + Math.cos(a) * r2} y2={cy + Math.sin(a) * r2} />);
  }
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" className={className}>
      <circle cx="12" cy="12" r="4" fill="currentColor" stroke="none" />
      {rays}
    </svg>
  );
}
const Ic = {
  arrow: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M5 12h14M13 6l6 6-6 6" /></svg>),
  upload: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 16V4M7 9l5-5 5 5" /><path d="M4 17v2a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-2" /></svg>),
  file: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M14 3v5h5" /><path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z" /></svg>),
  chevron: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M6 9l6 6 6-6" /></svg>),
  alert: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 9v4M12 17h.01" /><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" /></svg>),
  shield: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z" /></svg>),
  check: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M20 6 9 17l-5-5" /></svg>),
  sun: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>),
  moon: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" /></svg>),
  doc: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M14 3v5h5" /><path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z" /><path d="M8 12h8M8 16h6" /></svg>),
  quote: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" stroke="none" {...p}><path d="M7 7h4v4c0 3-2 5-4 5v-2c1 0 2-1 2-3H7zM15 7h4v4c0 3-2 5-4 5v-2c1 0 2-1 2-3h-2z" /></svg>),
  reset: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M3 12a9 9 0 1 0 3-6.7L3 8" /><path d="M3 3v5h5" /></svg>),
};

/* ---------- Small primitives ---------- */
function Eyebrow({ children, className = "" }) {
  return <div className={`font-mono text-[11px] uppercase tracking-eye text-fg3 ${className}`}>{children}</div>;
}
function RiskBadge({ level, size = "sm" }) {
  const t = riskTone(level);
  const pad = size === "lg" ? "px-3.5 py-1.5 text-[13px]" : "px-2.5 py-1 text-[11px]";
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-mono uppercase tracking-eye font-medium ${t.bg} ${t.fg} ${pad}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${t.dot}`}></span>{level}
    </span>
  );
}
function Button({ variant = "ink", size = "md", className = "", children, ...rest }) {
  const base = "inline-flex items-center justify-center gap-2 rounded-full font-medium leading-none transition-all duration-200 active:translate-y-px cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed";
  const sizes = { md: "px-5 py-3 text-sm", lg: "px-7 py-4 text-[15px]", sm: "px-4 py-2.5 text-[13px]" };
  const variants = {
    blue: "bg-accent text-white hover:bg-accentdeep border border-transparent",
    ink: "bg-fg text-bg hover:opacity-90 border border-transparent",
    outline: "bg-transparent text-fg border border-linestrong hover:bg-fg hover:text-bg",
    ghost: "bg-transparent text-fg border border-transparent hover:bg-surface2",
  };
  return <button className={`${base} ${sizes[size]} ${variants[variant]} ${className}`} {...rest}>{children}</button>;
}

/* ============================================================
   APP ROOT
   ============================================================ */
function App() {
  const [stage, setStage] = useState("upload"); // upload | analyzing | report
  const [report, setReport] = useState(null);
  const [fileName, setFileName] = useState("");
  const [dark, setDark] = useState(() => {
    const s = localStorage.getItem("bogdai-theme");
    if (s) return s === "dark";
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("bogdai-theme", dark ? "dark" : "light");
  }, [dark]);

  const beginAnalysis = useCallback((data, name) => {
    setReport(data);
    setFileName(name || data.contract_name);
    setStage("analyzing");
  }, []);

  const reset = useCallback(() => {
    setStage("upload");
    window.scrollTo({ top: 0 });
  }, []);

  return (
    <div className="min-h-screen bg-bg">
      <TopBar stage={stage} dark={dark} onToggle={() => setDark((d) => !d)} onReset={reset} fileName={fileName} report={report} />
      {stage === "upload" && <UploadScreen onLoad={beginAnalysis} />}
      {stage === "analyzing" && <AnalyzingScreen report={report} fileName={fileName} onDone={() => setStage("report")} />}
      {stage === "report" && <ReportView report={report} />}
    </div>
  );
}

/* ---------- Top bar ---------- */
function TopBar({ stage, dark, onToggle, onReset, fileName, report }) {
  return (
    <header className="sticky top-0 z-50 border-b border-line" style={{ background: "color-mix(in srgb, var(--bg) 86%, transparent)", backdropFilter: "saturate(140%) blur(10px)", WebkitBackdropFilter: "saturate(140%) blur(10px)" }}>
      <div className="max-w-[1180px] mx-auto px-5 sm:px-8 h-16 flex items-center gap-4">
        <button onClick={onReset} className="flex items-center gap-2.5 group" title="BogdAI home">
          <span className="text-accent"><Glyph size={24} /></span>
          <span className="text-[19px] font-semibold tracking-[-0.015em] text-fg">Bogd<span className="text-accent">AI</span></span>
        </button>
        {stage === "report" && (
          <span className="hidden sm:flex items-center gap-2 ml-1 pl-4 border-l border-line text-fg2 text-[13px] font-mono truncate max-w-[240px]">
            <span className="text-fg3"><Ic.file width={14} height={14} /></span>
            <span className="truncate">{fileName}</span>
          </span>
        )}
        <div className="ml-auto flex items-center gap-2">
          {stage === "report" && (
            <Button variant="ghost" size="sm" onClick={onReset}>
              <Ic.reset width={15} height={15} /> New analysis
            </Button>
          )}
          <button onClick={onToggle} title="Toggle theme" className="w-9 h-9 grid place-items-center rounded-full border border-line text-fg2 hover:text-fg hover:border-linestrong transition-colors">
            {dark ? <Ic.sun width={17} height={17} /> : <Ic.moon width={17} height={17} />}
          </button>
        </div>
      </div>
    </header>
  );
}

/* ============================================================
   SCREEN 1 — UPLOAD
   ============================================================ */
function UploadScreen({ onLoad }) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    setError("");
    const name = file.name;
    const lower = name.toLowerCase();
    // If a JSON report is dropped, parse and use it directly.
    if (lower.endsWith(".json")) {
      const r = new FileReader();
      r.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          if (!data.overall_assessment || !data.flags) throw new Error("bad");
          onLoad(data, name);
        } catch (_) {
          setError("That file isn't a valid BogdAI analysis report.");
        }
      };
      r.readAsText(file);
      return;
    }
    if (lower.endsWith(".txt") || lower.endsWith(".pdf")) {
      // No backend in this demo — run the contract through the sample pipeline.
      onLoad(SAMPLE_REPORT, name);
      return;
    }
    setError("Please upload a .txt or .pdf contract, or a .json report.");
  };

  return (
    <main className="max-w-[1180px] mx-auto px-5 sm:px-8">
      <div className="min-h-[calc(100vh-4rem)] flex flex-col justify-center py-16">
        <div className="max-w-[640px] anim-fadeUp">
          <Eyebrow className="text-accent">Contract risk monitoring</Eyebrow>
          <h1 className="font-serif text-[clamp(40px,6vw,68px)] leading-[1.02] tracking-[-0.028em] text-fg mt-4 mb-5" style={{ textWrap: "balance" }}>
            Know the risk before<br className="hidden sm:block" /> you sign.
          </h1>
          <p className="text-fg2 text-[19px] leading-[1.5] max-w-[52ch]">
            AI-powered contract risk monitoring for pharma teams. Upload an agreement and BogdAI grounds every flag in your policy library — with reasoning you can audit.
          </p>
        </div>

        <div
          className={`mt-12 max-w-[720px] rounded-xl border bg-surface transition-colors duration-200 anim-fadeUp ${dragOver ? "border-accent" : "border-line"}`}
          style={{ animationDelay: "90ms" }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
        >
          <div className="p-8 sm:p-10 flex flex-col items-center text-center">
            <div className={`w-14 h-14 grid place-items-center rounded-full border transition-colors ${dragOver ? "border-accent text-accent bg-accentwash" : "border-line text-fg2"}`}>
              <Ic.upload width={24} height={24} />
            </div>
            <h2 className="font-serif text-[26px] tracking-[-0.018em] text-fg mt-5 mb-1.5">Upload a contract</h2>
            <p className="text-fg2 text-[15px] max-w-[42ch]">Drag and drop a file here, or browse. We accept <span className="font-mono text-[13px] text-fg">.txt</span> and <span className="font-mono text-[13px] text-fg">.pdf</span> agreements.</p>
            <div className="flex flex-col sm:flex-row gap-3 mt-7 w-full sm:w-auto">
              <Button variant="blue" size="lg" onClick={() => inputRef.current && inputRef.current.click()}>
                <Ic.upload width={17} height={17} /> Choose file
              </Button>
              <Button variant="outline" size="lg" onClick={() => onLoad(SAMPLE_REPORT, SAMPLE_REPORT.contract_name)}>
                Use sample contract <Ic.arrow width={15} height={15} />
              </Button>
            </div>
            <input ref={inputRef} type="file" accept=".txt,.pdf,.json" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
            {error && <p className="text-red text-[13px] mt-4">{error}</p>}
          </div>
          <div className="border-t border-line px-8 sm:px-10 py-4 flex items-center gap-2.5 text-fg3">
            <Ic.shield width={15} height={15} />
            <span className="text-[12.5px] leading-snug">Synthetic demonstration only. Nothing you upload leaves your browser.</span>
          </div>
        </div>

        <div className="mt-10 flex flex-wrap items-center gap-x-6 gap-y-2 text-fg3 anim-fadeUp" style={{ animationDelay: "160ms" }}>
          {["Grounded in Foundry IQ", "Auditable reasoning", "Human-in-the-loop"].map((t) => (
            <span key={t} className="flex items-center gap-2 text-[13px]">
              <span className="text-accent"><Ic.check width={15} height={15} /></span>{t}
            </span>
          ))}
        </div>
      </div>
    </main>
  );
}

/* ============================================================
   SCREEN 1.5 — ANALYZING (cycles through the agent pipeline)
   ============================================================ */
function AnalyzingScreen({ report, fileName, onDone }) {
  const agents = report.agent_trace;
  const [active, setActive] = useState(0);

  useEffect(() => {
    const STEP = 620;
    const timers = agents.map((_, i) => setTimeout(() => setActive(i + 1), STEP * (i + 1)));
    const end = setTimeout(onDone, STEP * (agents.length + 1) + 240);
    return () => { timers.forEach(clearTimeout); clearTimeout(end); };
  }, []);

  return (
    <main className="max-w-[1180px] mx-auto px-5 sm:px-8">
      <div className="min-h-[calc(100vh-4rem)] flex flex-col justify-center py-16">
        <div className="max-w-[680px] mx-auto w-full">
          <div className="flex items-center gap-3 mb-8">
            <span className="w-4 h-4 rounded-full border-2 border-line border-t-accent spin"></span>
            <Eyebrow>Analyzing · {fileName}</Eyebrow>
          </div>
          <h2 className="font-serif text-[clamp(30px,4vw,44px)] tracking-[-0.022em] leading-[1.06] text-fg mb-10" style={{ textWrap: "balance" }}>
            Six agents are reviewing your contract.
          </h2>
          <ol className="flex flex-col">
            {agents.map((a, i) => {
              const done = i < active;
              const current = i === active;
              return (
                <li key={i} className="flex items-start gap-4 py-3.5 border-t border-line first:border-t-0" style={{ opacity: done || current ? 1 : 0.38, transition: "opacity 300ms ease" }}>
                  <span className={`mt-0.5 w-6 h-6 shrink-0 grid place-items-center rounded-full border text-[12px] font-mono transition-colors duration-300 ${done ? "bg-accent border-accent text-white" : current ? "border-accent text-accent" : "border-line text-fg3"}`}>
                    {done ? <Ic.check width={13} height={13} /> : current ? <span className="w-1.5 h-1.5 rounded-full bg-accent" style={{ animation: "pulse 1s ease-in-out infinite" }}></span> : i + 1}
                  </span>
                  <div className="min-w-0">
                    <div className="text-fg text-[15px] font-medium">{a.agent_name}</div>
                    <div className="text-fg2 text-[13.5px] leading-snug">{done ? a.output : a.role}</div>
                  </div>
                </li>
              );
            })}
          </ol>
        </div>
      </div>
    </main>
  );
}

/* ============================================================
   REPORT VIEW — sticky section nav + all screens
   ============================================================ */
const SECTIONS = [
  { id: "summary", label: "Risk summary" },
  { id: "flags", label: "Flagged clauses" },
  { id: "trace", label: "Agent trace" },
  { id: "safety", label: "Safety" },
];

function ReportView({ report }) {
  const [activeSec, setActiveSec] = useState("summary");
  const refs = { summary: useRef(null), flags: useRef(null), trace: useRef(null), safety: useRef(null) };

  const scrollTo = (id) => {
    const el = refs[id].current;
    if (!el) return;
    const y = el.getBoundingClientRect().top + window.scrollY - 116;
    window.scrollTo({ top: y, behavior: "smooth" });
  };

  useEffect(() => {
    const onScroll = () => {
      const pos = window.scrollY + 160;
      let cur = "summary";
      for (const s of SECTIONS) {
        const el = refs[s.id].current;
        if (el && el.offsetTop <= pos) cur = s.id;
      }
      setActiveSec(cur);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div>
      <SectionNav active={activeSec} onNav={scrollTo} report={report} />
      <main className="max-w-[1180px] mx-auto px-5 sm:px-8 pb-28">
        <div ref={refs.summary} className="scroll-mt-28"><RiskSummary report={report} /></div>
        <div ref={refs.flags} className="scroll-mt-28"><FlaggedClauses report={report} /></div>
        <div ref={refs.trace} className="scroll-mt-28"><AgentTrace report={report} /></div>
        <div ref={refs.safety} className="scroll-mt-28"><SafetyNotice report={report} /></div>
      </main>
    </div>
  );
}

function SectionNav({ active, onNav }) {
  return (
    <nav className="sticky top-16 z-40 border-b border-line bg-bg/95" style={{ backdropFilter: "blur(8px)", WebkitBackdropFilter: "blur(8px)" }}>
      <div className="max-w-[1180px] mx-auto px-5 sm:px-8">
        <div className="flex gap-1 overflow-x-auto -mb-px" style={{ scrollbarWidth: "none" }}>
          {SECTIONS.map((s) => (
            <button key={s.id} onClick={() => onNav(s.id)}
              className={`relative whitespace-nowrap px-3.5 py-3.5 text-[13.5px] transition-colors ${active === s.id ? "text-fg" : "text-fg2 hover:text-fg"}`}>
              {s.label}
              <span className={`absolute left-3.5 right-3.5 bottom-0 h-0.5 rounded-full transition-opacity ${active === s.id ? "bg-accent opacity-100" : "opacity-0"}`}></span>
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
}

/* ---------- SCREEN 2 — RISK SUMMARY ---------- */
function RiskSummary({ report }) {
  const oa = report.overall_assessment;
  const rb = report.risk_breakdown;
  const t = riskTone(oa.overall_risk_level);
  const metrics = [
    { label: "Total flags", value: report.flags.length, tone: "fg" },
    { label: "High risk", value: rb.high, tone: "red" },
    { label: "Medium risk", value: rb.medium, tone: "amber" },
    { label: "Citations", value: report.grounding_summary.total_citations, tone: "accent" },
  ];
  const toneText = { fg: "text-fg", red: "text-red", amber: "text-amber", accent: "text-accent" };

  return (
    <section className="pt-12 sm:pt-16">
      {oa.human_review_required && (
        <div className={`flex items-start gap-3 rounded-xl border ${t.border} ${t.bg} px-5 py-4 mb-10`}>
          <span className={`${t.fg} mt-0.5 shrink-0`}><Ic.alert width={19} height={19} /></span>
          <div>
            <div className={`text-[14px] font-semibold ${t.fg}`}>Human review required</div>
            <p className="text-fg2 text-[13.5px] leading-snug mt-0.5">{report.ui_hints.recommended_next_action}. Do not act on these findings without sign-off from legal or compliance.</p>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-[1.1fr_1fr] gap-10 lg:gap-16 items-start">
        <div>
          <Eyebrow>Overall assessment · {report.analysis_id}</Eyebrow>
          <h1 className={`font-serif text-[clamp(48px,7.5vw,88px)] leading-[0.98] tracking-[-0.03em] mt-4 ${t.fg}`}>{oa.overall_risk_level}<span className="text-fg3"> risk</span></h1>
          <p className="text-fg2 text-[17px] leading-[1.55] mt-5 max-w-[54ch]" style={{ textWrap: "pretty" }}>{oa.summary}</p>

          <div className="mt-8">
            <div className="flex items-end justify-between mb-2.5">
              <Eyebrow>Risk score</Eyebrow>
              <div className="font-serif text-fg leading-none"><span className="text-[34px]" style={{ color: t.barVar }}>{oa.risk_score}</span><span className="text-fg3 text-[18px]"> / 100</span></div>
            </div>
            <div className="h-2.5 rounded-full bg-surface2 border border-line overflow-hidden">
              <div className="h-full rounded-full anim-fadeIn" style={{ width: `${oa.risk_score}%`, background: t.barVar, animation: "barGrow 900ms cubic-bezier(0.2,0.7,0.2,1) both" }}></div>
            </div>
            <div className="flex justify-between mt-2 font-mono text-[10.5px] uppercase tracking-eye text-fg3">
              <span>Low</span><span>Medium</span><span>High</span><span>Critical</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          {metrics.map((m) => (
            <div key={m.label} className="rounded-xl border border-line bg-surface p-5 sm:p-6 transition-colors duration-200 hover:border-linestrong">
              <div className={`font-serif text-[clamp(34px,5vw,48px)] leading-none ${toneText[m.tone]}`}>{m.value}</div>
              <div className="text-fg2 text-[13px] mt-2">{m.label}</div>
            </div>
          ))}
        </div>
      </div>
      <hr className="border-0 border-t border-line mt-14 sm:mt-16" />
    </section>
  );
}

/* ---------- SCREEN 3 — FLAGGED CLAUSES ---------- */
function FlaggedClauses({ report }) {
  const [openId, setOpenId] = useState(report.flags[0] ? report.flags[0].flag_id : null);
  return (
    <section className="pt-14 sm:pt-16">
      <div className="flex items-end justify-between gap-6 flex-wrap mb-8">
        <div>
          <Eyebrow className="text-accent">Findings</Eyebrow>
          <h2 className="font-serif text-[clamp(30px,4vw,46px)] tracking-[-0.022em] leading-[1.05] text-fg mt-3">Flagged clauses</h2>
        </div>
        <p className="text-fg2 text-[14px] font-mono">{report.flags.length} clause{report.flags.length !== 1 ? "s" : ""} need attention</p>
      </div>
      <div className="flex flex-col gap-4">
        {report.flags.map((f, i) => (
          <FlagCard key={f.flag_id} flag={f} index={i} open={openId === f.flag_id} onToggle={() => setOpenId(openId === f.flag_id ? null : f.flag_id)} />
        ))}
      </div>
      <hr className="border-0 border-t border-line mt-14 sm:mt-16" />
    </section>
  );
}

function FlagCard({ flag, index, open, onToggle }) {
  const t = riskTone(flag.risk_level);
  return (
    <div className="rounded-xl border border-line bg-surface overflow-hidden transition-colors duration-200" style={{ borderLeft: `3px solid ${t.barVar}` }}>
      <button onClick={onToggle} className="w-full text-left p-5 sm:p-6 flex gap-4 sm:gap-5 items-start hover:bg-surface2/50 transition-colors">
        <div className="hidden sm:flex flex-col items-center pt-0.5 w-14 shrink-0">
          <span className="font-mono text-[10px] uppercase tracking-eye text-fg3">Clause</span>
          <span className="font-serif text-[26px] leading-none text-fg mt-1">{flag.clause}</span>
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2.5 flex-wrap mb-2">
            <RiskBadge level={flag.risk_level} />
            <span className="font-mono text-[11px] uppercase tracking-eye text-fg3">{flag.risk_category}</span>
            <span className="sm:hidden font-mono text-[11px] uppercase tracking-eye text-fg3">· Clause {flag.clause}</span>
          </div>
          <h3 className="font-serif text-[21px] sm:text-[23px] leading-[1.15] tracking-[-0.012em] text-fg">{flag.title}</h3>
          <p className="text-fg2 text-[14.5px] leading-[1.55] mt-2 max-w-[68ch]" style={{ textWrap: "pretty" }}>{flag.issue}</p>
        </div>
        <span className={`shrink-0 text-fg3 mt-1 transition-transform duration-300 ${open ? "rotate-180" : ""}`}><Ic.chevron width={20} height={20} /></span>
      </button>

      {open && (
        <div className="px-5 sm:px-6 pb-6 anim-fadeIn">
          <div className="sm:ml-[76px] border-t border-line pt-6 grid gap-7">
            {/* clause excerpt */}
            <div className="rounded-lg bg-surface2 border border-line px-4 py-3">
              <p className="font-mono text-[12.5px] leading-[1.6] text-fg2">{flag.clause_excerpt}</p>
            </div>

            {/* impact split */}
            <div className="grid sm:grid-cols-2 gap-5">
              <div>
                <Eyebrow className="mb-2">Business impact</Eyebrow>
                <p className="text-fg2 text-[14px] leading-[1.55]">{flag.business_impact}</p>
              </div>
              <div>
                <Eyebrow className="mb-2">Patient impact</Eyebrow>
                <p className="text-fg2 text-[14px] leading-[1.55]">{flag.patient_impact}</p>
              </div>
            </div>

            {/* reasoning steps */}
            <div>
              <Eyebrow className="mb-3.5">Reasoning</Eyebrow>
              <ol className="flex flex-col gap-3.5">
                {flag.reasoning_steps.map((s) => (
                  <li key={s.step} className="flex gap-3.5">
                    <span className="shrink-0 w-6 h-6 grid place-items-center rounded-full border border-line font-mono text-[12px] text-fg2">{s.step}</span>
                    <div className="min-w-0 pt-0.5">
                      <p className="text-fg text-[14px] leading-[1.55]">{s.observation}</p>
                      <p className="text-fg2 text-[13.5px] leading-[1.55] mt-1 pl-3 border-l-2 border-line">{s.inference}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>

            {/* recommendation */}
            <div className="rounded-lg border border-accent/30 bg-accentwash px-4 py-3.5">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-accent"><Ic.check width={15} height={15} /></span>
                <span className="font-mono text-[11px] uppercase tracking-eye text-accent">Recommendation</span>
              </div>
              <p className="text-fg text-[14px] leading-[1.55]">{flag.recommendation}</p>
            </div>

            {/* citations */}
            {flag.citations.map((c) => (
              <div key={c.citation_id} className="rounded-lg border border-line p-4">
                <div className="flex items-center justify-between gap-3 flex-wrap mb-2.5">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-fg3 shrink-0"><Ic.doc width={15} height={15} /></span>
                    <span className="text-fg text-[13.5px] font-medium truncate">{c.source_title}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="font-mono text-[10px] uppercase tracking-eye text-accent bg-accentwash px-2 py-0.5 rounded-full">{c.grounding_layer}</span>
                    <span className="font-mono text-[11px] text-fg2">{pct(c.retrieval_confidence)} conf.</span>
                  </div>
                </div>
                <div className="flex gap-2.5">
                  <span className="text-fg3 shrink-0 mt-0.5"><Ic.quote width={15} height={15} /></span>
                  <p className="text-fg2 text-[13.5px] leading-[1.55] italic">{c.quoted_evidence}</p>
                </div>
                <div className="font-mono text-[11px] text-fg3 mt-2.5 pl-[26px]">{c.source_document} · {c.section}</div>
              </div>
            ))}

            <div className="flex items-center gap-2 text-fg3 font-mono text-[11px] uppercase tracking-eye">
              <span>Model confidence {pct(flag.confidence)}</span>
              {flag.needs_human_review && <span className="text-amber">· Flagged for human review</span>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ---------- SCREEN 4 — AGENT TRACE ---------- */
function AgentTrace({ report }) {
  return (
    <section className="pt-14 sm:pt-16">
      <div className="mb-9">
        <Eyebrow className="text-accent">Pipeline</Eyebrow>
        <h2 className="font-serif text-[clamp(30px,4vw,46px)] tracking-[-0.022em] leading-[1.05] text-fg mt-3">Agent trace</h2>
        <p className="text-fg2 text-[16px] leading-[1.5] mt-3 max-w-[56ch]">Every analysis runs through six specialized agents. Each step is recorded so the result can be audited end to end.</p>
      </div>
      <ol className="relative">
        <span className="absolute left-[15px] top-2 bottom-2 w-px bg-line" aria-hidden="true"></span>
        {report.agent_trace.map((a, i) => (
          <li key={i} className="relative flex gap-5 pb-7 last:pb-0">
            <span className="relative z-10 shrink-0 w-8 h-8 grid place-items-center rounded-full bg-surface border border-line font-mono text-[12px] text-fg2">{i + 1}</span>
            <div className="min-w-0 pt-0.5">
              <div className="flex items-center gap-3 flex-wrap">
                <h3 className="font-serif text-[20px] tracking-[-0.012em] text-fg leading-tight">{a.agent_name}</h3>
                {a.tool_used && <span className="font-mono text-[10.5px] uppercase tracking-eye text-accent bg-accentwash px-2 py-0.5 rounded-full">{a.tool_used}</span>}
              </div>
              <p className="text-fg2 text-[14px] leading-[1.5] mt-1">{a.role}</p>
              <p className="text-fg text-[14px] leading-[1.55] mt-2.5 rounded-lg bg-surface2 border border-line px-3.5 py-2.5">{a.output}</p>
            </div>
          </li>
        ))}
      </ol>
      <hr className="border-0 border-t border-line mt-14 sm:mt-16" />
    </section>
  );
}

/* ---------- SCREEN 5 — SAFETY NOTICE ---------- */
function SafetyNotice({ report }) {
  const s = report.safety_and_limits;
  const items = [
    { on: s.synthetic_data_only, label: "Synthetic data only", desc: "All contracts and citations in this demo are fabricated for demonstration. No real agreements or patient data are involved." },
    { on: !s.contains_pii, label: "No personal data", desc: "This analysis contains no PII and was produced without access to confidential records." },
    { on: s.requires_human_approval_before_action, label: "Human approval required", desc: "Findings are advisory. A qualified reviewer must approve before any action is taken on this contract." },
  ];
  return (
    <section className="pt-14 sm:pt-16">
      <div className="rounded-2xl border border-amber/40 bg-amberwash overflow-hidden">
        <div className="px-6 sm:px-9 py-7 sm:py-8 border-b border-amber/30">
          <div className="flex items-start gap-3.5">
            <span className="text-amber mt-0.5 shrink-0"><Ic.alert width={22} height={22} /></span>
            <div>
              <Eyebrow className="text-amber">Safety notice</Eyebrow>
              <h2 className="font-serif text-[clamp(24px,3vw,34px)] tracking-[-0.018em] leading-[1.1] text-fg mt-2 max-w-[34ch]">This is a hackathon demonstration, not legal advice.</h2>
              <p className="text-fg2 text-[15px] leading-[1.55] mt-3 max-w-[60ch]">{s.legal_advice_disclaimer}</p>
            </div>
          </div>
        </div>
        <div className="grid sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-amber/25">
          {items.map((it) => (
            <div key={it.label} className="px-6 sm:px-7 py-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-5 h-5 grid place-items-center rounded-full bg-amber text-bg shrink-0"><Ic.check width={12} height={12} /></span>
                <span className="text-fg text-[14px] font-semibold">{it.label}</span>
              </div>
              <p className="text-fg2 text-[13px] leading-[1.55]">{it.desc}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-10 flex items-center justify-between gap-4 flex-wrap text-fg3">
        <span className="flex items-center gap-2 text-[13px]"><span className="text-accent"><Glyph size={18} /></span> BogdAI · Quiet infrastructure for ambitious teams</span>
        <span className="font-mono text-[11px] uppercase tracking-eye">Analysis {report.analysis_id} · {report.analysis_date}</span>
      </div>
    </section>
  );
}

/* ---------- Mount ---------- */
ReactDOM.createRoot(document.getElementById("root")).render(<App />);
