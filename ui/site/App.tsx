import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, ReactNode } from "react";

// Concord: a scroll-driven story for Money Talks 2026 · AI × Finance. A cover and four chapters, one glance each.
// Northline Treasury and every counterparty, account and amount here is synthetic.

// --- Types and content -----------------------------------------------------

type Tone = "plain" | "tint" | "dark";
type PillTone = "green" | "red" | "amber" | "blue";
type RunStatus = "pass" | "fail" | "skip";
type RowState = RunStatus | "current" | "pending";
type SectionRefs = { current: (HTMLElement | null)[] };
type ChapterProps = { setRef: (el: HTMLElement | null) => void };

const FONT_LINK_ID = "concord-fonts";
const FONT_HREF =
  "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600" +
  "&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400;1,8..60,600&display=swap";

/** Section 0 is the cover, so chapter n lives at section index n. */
const CHAPTERS: { id: string; name: string; tone: Tone }[] = [
  { id: "payment", name: "The payment", tone: "plain" },
  { id: "usual", name: "What usually happens", tone: "tint" },
  { id: "run", name: "Watch Concord", tone: "plain" },
  { id: "receipts", name: "The receipts", tone: "dark" },
];
const SECTION_IDS = ["cover", ...CHAPTERS.map((c) => c.id)];

const CHECKS = [
  "Load trade", "Read our confirmation", "Read their confirmation", "Custodian status",
  "Look up instructions", "Bank and branch", "Account vs instructions", "Both sides agree",
  "Amounts and dates", "Fail cost", "Decide", "Draft note",
];

/** Concord's run on T008: one entry per check, in the same order as CHECKS. */
const RUN: { status: RunStatus; note?: ReactNode }[] = [
  { status: "pass", note: <>T008 · FX spot · <N>EUR 940,000</N></> },
  { status: "pass", note: <>Account <N>90052000</N>, Quay and Company Frankfurt</> },
  { status: "pass", note: <>Account <N>90052000</N>, Quay and Company Frankfurt</> },
  { status: "pass", note: "Open" },
  { status: "pass", note: <>Live registry, version 2, updated 1 Oct · <N>90052002</N></> },
  { status: "pass", note: "Quay and Company, Frankfurt — correct" },
  { status: "fail", note: <>Confirmations say <N>90052000</N>. Registry says <N>90052002</N>. Birch Capital closed <N>90052000</N> on 1 Oct.</> },
  { status: "skip" }, { status: "skip" }, { status: "skip" }, { status: "skip" }, { status: "skip" },
];

/** Step (number of resolved checks) at which each part of the decision card fills in. */
const AT = { verdict: 7, fault: 8, action: 9, cost: 10, note: 11, buttons: 12 };

const TIMELINE_MS = 1400;
type TimelinePoint = { date: string; label: ReactNode; pos: number; tone: "neutral" | "amber" | "red"; align: "start" | "center" | "end" };
const TIMELINE: TimelinePoint[] = [
  { date: "17 Sep", label: "trade agreed", pos: 0, tone: "neutral", align: "start" },
  { date: "1 Oct", label: <>Birch Capital changes account <N>(90052000 → 90052002)</N></>, pos: 46.7, tone: "amber", align: "center" },
  { date: "17 Oct", label: "value date today", pos: 100, tone: "red", align: "end" },
];

const RECEIPTS = [
  { label: "Right decision", v1: "14 of 20", v2: "20 of 20" },
  { label: "Paid to a closed account", v1: "4", v2: "0" },
  { label: "Crashed with no answer", v1: "2", v2: "0" },
];

/** One trade, before and after the fix. "same inputs" is the PRISM rubric phrase: keep it verbatim. */
const PRISM_CASES: { title: string; trade: ReactNode; steps: string; output: ReactNode; result: ReactNode }[] = [
  {
    title: "v1 — before", trade: <>T019 · Quill Asset Management · <N>USD 1.635M</N></>, steps: "3 of 12",
    output: <span className="case-empty">(empty)</span>, result: <Pill tone="red">Crashed · missing confirmation</Pill>,
  },
  {
    title: "v2 — after", trade: <>T019 · <span className="em">same inputs</span></>, steps: "12 of 12",
    output: <q className="case-quote">Hold — Quill Asset Management has not sent its confirmation. Chase before value date.</q>,
    result: <Pill tone="amber">Hold · fault: Quill</Pill>,
  },
];

const titleId = (section: number) => `${SECTION_IDS[section]}-title`;
const pad = (n: number) => String(n).padStart(2, "0");

// --- Hooks -----------------------------------------------------------------

/** Loads Source Serif 4 and Inter once, without touching index.html. */
function useGoogleFonts() {
  useEffect(() => {
    if (document.getElementById(FONT_LINK_ID)) return;
    document.head.appendChild(Object.assign(document.createElement("link"), { id: FONT_LINK_ID, rel: "stylesheet", href: FONT_HREF }));
  }, []);
}

const REDUCED_QUERY = "(prefers-reduced-motion: reduce)";

function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(
    () => typeof window !== "undefined" && !!window.matchMedia && window.matchMedia(REDUCED_QUERY).matches
  );
  useEffect(() => {
    if (!window.matchMedia) return;
    const mq = window.matchMedia(REDUCED_QUERY);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

/** True from the first moment the element is meaningfully on screen. Never resets. */
function useInViewOnce<T extends Element>(threshold = 0.2) {
  const ref = useRef<T | null>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el || inView) return;
    if (!("IntersectionObserver" in window)) return setInView(true);
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) (setInView(true), io.disconnect());
    }, { threshold });
    io.observe(el);
    return () => io.disconnect();
  }, [inView, threshold]);
  return [ref, inView] as const;
}

/** Counts 0 → total, one step every stepMs, once active. Reduced motion jumps to the end. */
function useSequence(active: boolean, total: number, stepMs: number, startDelayMs = 0) {
  const reduced = usePrefersReducedMotion();
  const [step, setStep] = useState(0);
  useEffect(() => {
    if (!active) return;
    if (reduced) return setStep(total);
    let i = 0;
    let interval = 0;
    const start = window.setTimeout(() => {
      interval = window.setInterval(() => {
        i += 1;
        setStep(i);
        if (i >= total) window.clearInterval(interval);
      }, stepMs);
    }, startDelayMs);
    return () => (window.clearTimeout(start), window.clearInterval(interval));
  }, [active, reduced, total, stepMs, startDelayMs]);
  return step;
}

/** Index of the section most in view, by visible height, so a section taller than the screen still wins while it fills it. */
function useActiveSection(sections: SectionRefs) {
  const [active, setActive] = useState(0);
  useEffect(() => {
    const els = sections.current;
    if (!("IntersectionObserver" in window)) return;
    const visible = new Map<Element, number>();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => visible.set(e.target, e.isIntersecting ? e.intersectionRect.height : 0));
      let best = -1;
      let bestPx = 0;
      els.forEach((el, i) => {
        const px = el ? visible.get(el) ?? 0 : 0;
        if (px > bestPx) [best, bestPx] = [i, px];
      });
      if (best >= 0) setActive(best);
    }, { threshold: Array.from({ length: 21 }, (_, i) => i / 20) });
    els.forEach((el) => el && io.observe(el));
    return () => io.disconnect();
  }, [sections]);
  return active;
}

/** ArrowDown / PageDown: next section. ArrowUp / PageUp: previous. Home: cover. */
function useSectionKeys(sections: SectionRefs, goTo: (index: number) => void) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
      const t = e.target as HTMLElement | null;
      if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
      const els = sections.current;
      let target = -1;
      if (e.key === "Home") target = 0;
      else if (e.key === "ArrowDown" || e.key === "PageDown") target = els.findIndex((el) => !!el && el.getBoundingClientRect().top > 8);
      else if (e.key === "ArrowUp" || e.key === "PageUp") els.forEach((el, i) => { if (el && el.getBoundingClientRect().top < -8) target = i; });
      if (target < 0) return;
      e.preventDefault();
      goTo(target);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sections, goTo]);
}

// --- Building blocks -------------------------------------------------------

/** Monospaced, tabular figures for money and account numbers. */
function N({ children }: { children: ReactNode }) {
  return <span className="num">{children}</span>;
}

function Pill({ tone, children }: { tone: PillTone; children: ReactNode }) {
  return <span className={`pill pill-${tone}`}>{children}</span>;
}

function Chapter({ n, setRef, children }: ChapterProps & { n: number; children: ReactNode }) {
  const { id, tone } = CHAPTERS[n - 1];
  return (
    <section id={id} ref={setRef} aria-labelledby={titleId(n)} className={`section tone-${tone}`}>
      <div className="wrap">{children}</div>
    </section>
  );
}

function Eyebrow({ n }: { n: number }) {
  return <p className="eyebrow">{`${n} of ${CHAPTERS.length} · ${CHAPTERS[n - 1].name}`}</p>;
}

/** Chapter headline. Focusable (tabIndex -1) so section jumps can move focus here. */
function Title({ n, className = "h2", children }: { n: number; className?: string; children: ReactNode }) {
  return <h2 id={titleId(n)} tabIndex={-1} className={className}>{children}</h2>;
}

/** Fades its direct children in on first intersection: 8px rise, 400ms, staggered (60ms default). */
function Reveal({ children, className = "", stagger, delay }: { children: ReactNode; className?: string; stagger?: number; delay?: number }) {
  const [ref, inView] = useInViewOnce<HTMLDivElement>(0.2);
  const style = { "--stagger": stagger && `${stagger}ms`, "--delay": delay && `${delay}ms` } as CSSProperties;
  return <div ref={ref} className={`reveal ${inView ? "is-in" : ""} ${className}`} style={style}>{children}</div>;
}

function Fact({ label, children }: { label: string; children: ReactNode }) {
  return <dl className="fact"><dt>{label}</dt><dd>{children}</dd></dl>;
}

/** Hidden on the cover; fades in once chapter 1 is the main section in view. */
function ChapterCounter({ active }: { active: number }) {
  const shown = active > 0;
  const chapter = CHAPTERS[Math.max(0, active - 1)];
  return (
    <header className={`masthead on-${chapter.tone} ${shown ? "is-shown" : ""}`} aria-hidden={!shown}>
      <p className="counter">
        <span className="sr-only">Chapter </span>
        <span className="counter-num num">{`${Math.max(1, active)} / ${CHAPTERS.length}`}</span>
        <span key={chapter.id} className="counter-title">{chapter.name}</span>
      </p>
    </header>
  );
}

// --- Cover -----------------------------------------------------------------

function Cover({ setRef, onStart }: ChapterProps & { onStart: () => void }) {
  return (
    <section id="cover" ref={setRef} aria-labelledby={titleId(0)} className="section cover">
      <div className="wrap cover-inner">
        <h1 id={titleId(0)} tabIndex={-1} className="wordmark">Concord<span className="wordmark-dot">.</span></h1>
        <p className="cover-line">Pre-settlement checks that read what you read.</p>
        <div className="cover-actions">
          <button type="button" className="btn btn-ghost btn-lg" onClick={onStart}>See the demo <span aria-hidden="true">↓</span></button>
          <button type="button" className="btn btn-ghost btn-lg" onClick={onStart}>How it works <span aria-hidden="true">↓</span></button>
        </div>
      </div>
      <p className="cover-caption">Money Talks 2026 · AI × Finance · Northline Treasury · synthetic data</p>
    </section>
  );
}

// --- Chapter 1 · The payment and the quiet change --------------------------

function Timeline() {
  const [ref, inView] = useInViewOnce<HTMLDivElement>(0.5);
  return (
    <div ref={ref} className={`timeline ${inView ? "is-in" : ""}`}>
      <div className="tl-track" aria-hidden="true">
        <span className="tl-fill" />
        <span className="tl-risk" style={{ left: `${TIMELINE[1].pos}%` }} />
      </div>
      <ol className="tl-points">
        {TIMELINE.map((p) => {
          const style = { "--pos": `${p.pos}%`, "--at": `${Math.round((p.pos / 100) * TIMELINE_MS)}ms` } as CSSProperties;
          return (
            <li key={p.date} className={`tl-point tl-${p.tone} tl-${p.align}`} style={style}>
              <span className="tl-date">{p.date}</span>
              <span className="tl-dot" aria-hidden="true" />
              <span className="tl-label">{p.label}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

function ChapterPayment({ setRef }: ChapterProps) {
  return (
    <Chapter n={1} setRef={setRef}>
      <Reveal>
        <Eyebrow n={1} />
        <Title n={1} className="display">EUR 940,000 is about to leave the firm.</Title>
        <p className="subtitle">A routine Friday afternoon.</p>
        <p className="lede">
          At 14:02, Northline Treasury agreed to pay Birch Capital. The money moves Monday. Every detail has to match first.
        </p>
      </Reveal>
      <Reveal className="facts" stagger={120} delay={200}>
        <Fact label="Trade">T008 · FX spot</Fact>
        <Fact label="Pay"><N>EUR 940,000</N></Fact>
        <Fact label="To">Birch Capital</Fact>
        <Fact label="Value date">17 Oct 2026 · <span className="text-red">today</span></Fact>
      </Reveal>
      <Timeline />
      <Reveal>
        <p className="caption-serif">
          Both parties’ confirmations still show the old account. They agree with each other, and they are both wrong.
        </p>
      </Reveal>
    </Chapter>
  );
}

// --- Chapter 2 · What usually happens --------------------------------------

function ChapterUsual({ setRef }: ChapterProps) {
  const [listRef, inView] = useInViewOnce<HTMLOListElement>(0.35);
  const done = useSequence(inView, CHECKS.length, 120, 300);
  return (
    <Chapter n={2} setRef={setRef}>
      <Reveal>
        <Eyebrow n={2} />
        <Title n={2}>A human analyst sees 20 of these a day.</Title>
        <p className="lede">
          Open the confirmation. Open the counterparty’s email. Open the registry. Match twelve things. If one is off,
          chase it. Repeat 20 times before 5 pm.
        </p>
      </Reveal>
      <div className="split">
        <div className="split-spacer" aria-hidden="true" />
        <ol ref={listRef} className="ticks" aria-label="The twelve manual checks">
          {CHECKS.map((name, i) => (
            <li key={name} className={`tick ${i < done ? "is-done" : ""}`}>
              <span className="tick-n num">{pad(i + 1)}</span>
              <span className="tick-name">{name}</span>
              <span className="tick-done" aria-hidden={i >= done}>(done)</span>
            </li>
          ))}
        </ol>
      </div>
      <Reveal>
        <blockquote className="pullquote"><p>“The ones that bite you are the quiet ones. Everything looked right.”</p></blockquote>
      </Reveal>
    </Chapter>
  );
}

// --- Chapter 3 · Concord runs through T008 ---------------------------------

function StatusPill({ state }: { state: RowState }) {
  if (state === "pass") return <Pill tone="green">Passed</Pill>;
  if (state === "fail") return <Pill tone="red">Failed</Pill>;
  if (state === "current") return <Pill tone="blue">Checking</Pill>;
  if (state === "skip") return <span className="run-dash">—</span>;
  return null;
}

function DecisionRow({ label, ready, children }: { label: string; ready: boolean; children: ReactNode }) {
  return (
    <div>
      <dt>{label}</dt>
      {ready ? <dd key="value" className="fade-in">{children}</dd> : <dd key="wait" className="is-placeholder">—</dd>}
    </div>
  );
}

function DecisionCard({ step }: { step: number }) {
  const hold = step >= AT.verdict;
  return (
    <div className={`card decision ${hold ? "is-hold" : ""}`}>
      <p className="decision-label">Decision</p>
      <p key={hold ? "hold" : "wait"} className={`verdict ${hold ? "is-set fade-in" : ""}`}>{hold ? "Hold" : "—"}</p>
      <dl className="decision-rows">
        <DecisionRow label="Fault" ready={step >= AT.fault}>
          Us, Northline Treasury
          <span className="decision-sub">Birch Capital sent the new account on 1 Oct. Our confirmation was never updated.</span>
        </DecisionRow>
        <DecisionRow label="Action" ready={step >= AT.action}>Call Birch settlements, today</DecisionRow>
        <DecisionRow label="Est. cost if it fails" ready={step >= AT.cost}><N>EUR 5,129</N></DecisionRow>
      </dl>
    </div>
  );
}

function DraftNote({ shown, ready }: { shown: boolean; ready: boolean }) {
  const [outcome, setOutcome] = useState<"open" | "held" | "approved">("open");
  const statusRef = useRef<HTMLParagraphElement | null>(null);

  // Approve removes the buttons, so hand focus to the confirmation line.
  useEffect(() => {
    if (outcome === "approved") statusRef.current?.focus();
  }, [outcome]);

  return (
    <article className={`card letter ${shown ? "is-in" : ""}`} aria-hidden={!shown} aria-labelledby="draft-subject">
      <dl className="letter-head">
        <div><dt>To</dt><dd>Birch Capital, settlements</dd></div>
        <div><dt>Subject</dt><dd id="draft-subject">T008 — please re-confirm new euro account</dd></div>
      </dl>
      <div className="letter-body">
        <p>
          Hi — our confirmation for T008 still shows account <N>90052000</N> at Quay and Company, Frankfurt. The
          registry has your new account <N>90052002</N> as of 1 October. Please re-confirm so we can release before close.
        </p>
        <p>Thanks,<br />Northline Treasury.</p>
      </div>
      <div className="letter-foot">
        <p className="letter-label" role="status">{outcome === "held" ? "Kept on hold · not sent" : "Draft · not sent"}</p>
        {outcome === "approved" ? (
          <p ref={statusRef} tabIndex={-1} className="approved" role="status">Approved. Added to the outbox. Not sent.</p>
        ) : ready && (
          <>
            <button type="button" className="btn btn-ghost" onClick={() => setOutcome("held")}>Keep on hold</button>
            <button type="button" className="btn btn-primary" onClick={() => setOutcome("approved")}>Approve</button>
          </>
        )}
      </div>
    </article>
  );
}

function ChapterRun({ setRef }: ChapterProps) {
  const [listRef, inView] = useInViewOnce<HTMLOListElement>(0.3);
  const step = useSequence(inView, CHECKS.length, 180, 250);
  const running = inView && step < CHECKS.length;

  return (
    <Chapter n={3} setRef={setRef}>
      <Reveal>
        <Eyebrow n={3} />
        <Title n={3} className="h2 h2-wide">Twelve checks. Half a second. Step seven catches it.</Title>
      </Reveal>
      <div className="run">
        <ol ref={listRef} className="run-list" aria-label="Concord's twelve checks on T008">
          {CHECKS.map((name, i) => {
            const { status, note } = RUN[i];
            const state: RowState = i < step ? status : running && i === step ? "current" : "pending";
            return (
              <li key={name} className={`run-row is-${state}`}>
                <span className="run-n num">{pad(i + 1)}</span>
                <span className="run-body">
                  <span className="run-name">{name}</span>
                  {/* Notes stay in the layout while hidden so rows don't jump as they resolve. */}
                  {note && <span className="run-note" aria-hidden={i >= step}>{note}</span>}
                </span>
                <span className="run-status"><StatusPill state={state} /></span>
              </li>
            );
          })}
        </ol>
        <aside className="run-side" aria-label="Decision">
          <DecisionCard step={step} />
          <DraftNote shown={step >= AT.note} ready={step >= AT.buttons} />
        </aside>
      </div>
    </Chapter>
  );
}

// --- Chapter 4 · The receipts ----------------------------------------------

function ChapterReceipts({ setRef }: ChapterProps) {
  return (
    <Chapter n={4} setRef={setRef}>
      <Reveal>
        <Eyebrow n={4} />
        <Title n={4}>Every run is traced.</Title>
        <p className="lede">
          We built Concord on Nicrron and traced every step with PRISM by Block Convey. The first version missed four
          payments and crashed on two. We fixed it. The second version got all twenty right, <span className="em">same inputs</span>.
        </p>
      </Reveal>
      <Reveal delay={120}>
        <table className="receipts">
          <thead>
            <tr><th scope="col">Measure</th><th scope="col">v1 (before)</th><th scope="col">v2 (after)</th></tr>
          </thead>
          <tbody>
            {RECEIPTS.map((r) => (
              <tr key={r.label}><th scope="row">{r.label}</th><td className="num">{r.v1}</td><td className="num is-good">{r.v2}</td></tr>
            ))}
          </tbody>
        </table>
      </Reveal>
      <Reveal delay={120}>
        <article className="prism" aria-labelledby="prism-title">
          <h3 id="prism-title" className="prism-eyebrow">What PRISM caught — one example</h3>
          <div className="cases">
            {PRISM_CASES.map((c) => (
              <div key={c.title} className="case">
                <h4 className="case-title">{c.title}</h4>
                <dl className="case-rows">
                  <div><dt>Trade</dt><dd>{c.trade}</dd></div>
                  <div><dt>Steps completed</dt><dd><N>{c.steps}</N></dd></div>
                  <div><dt>Output</dt><dd>{c.output}</dd></div>
                  <div><dt>Result</dt><dd>{c.result}</dd></div>
                </dl>
              </div>
            ))}
          </div>
        </article>
        <p className="caption receipts-caption">
          PRISM alert fired at 6 failures. Root cause flagged one shared bug across 52 runs. We shipped the fix and
          re-ran the same twenty trades.
        </p>
      </Reveal>
    </Chapter>
  );
}

// --- Page ------------------------------------------------------------------

export default function Concord() {
  useGoogleFonts();
  const reduced = usePrefersReducedMotion();
  const sectionRefs = useRef<(HTMLElement | null)[]>([]);
  const setters = useMemo(() => SECTION_IDS.map((_, i) => (el: HTMLElement | null) => { sectionRefs.current[i] = el; }), []);
  const active = useActiveSection(sectionRefs);

  /** Scrolls a section to the top and moves focus to its heading, so keyboard and screen reader users land with it. */
  const goTo = useCallback((index: number) => {
    sectionRefs.current[index]?.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
    document.getElementById(titleId(index))?.focus({ preventScroll: true });
  }, [reduced]);
  const startStory = useCallback(() => goTo(1), [goTo]);
  useSectionKeys(sectionRefs, goTo);

  return (
    <div className="concord">
      <style>{CSS}</style>
      <ChapterCounter active={active} />
      <main>
        <Cover setRef={setters[0]} onStart={startStory} />
        <ChapterPayment setRef={setters[1]} />
        <ChapterUsual setRef={setters[2]} />
        <ChapterRun setRef={setters[3]} />
        <ChapterReceipts setRef={setters[4]} />
      </main>
      <footer className="footer">
        <p>Concord · Money Talks 2026 · AI × Finance · built with Nicrron · traced in PRISM by Block Convey · synthetic data</p>
      </footer>
    </div>
  );
}

// --- Styles ----------------------------------------------------------------

const CSS = `
/* Host reset: neutralises the default Vite index.css (centred flex body, dark scheme). */
:root { color-scheme: light; } html, body { margin: 0; padding: 0; background: #FFFFFF; }
body { display: block; min-width: 0; place-items: normal; } #root { width: 100%; max-width: none; margin: 0; padding: 0; text-align: left; }

.concord {
  --white: #FFFFFF; --tint: #EAF4FB; --navy: #0B2545; --ink: #22303F; --muted: #5D6B7A; --faint: #9AA7B4;
  --line: #D9E2EC; --line-strong: #C3D3E2; --blue: #0071BC; --blue-hover: #005E9C;
  --green: #1E7B45; --green-soft: #E7F3EC; --red: #B42318; --red-soft: #FBEAE8;
  --amber: #B54708; --amber-soft: #FCF0E3;
  --on-dark: #FFFFFF; --on-dark-muted: rgba(255, 255, 255, 0.72); --on-dark-faint: rgba(255, 255, 255, 0.45);
  --on-dark-line: rgba(255, 255, 255, 0.2); --on-dark-accent: #8EC8F0; --on-dark-good: #9ADBB2;
  --serif: "Source Serif 4", Georgia, "Times New Roman", serif;
  --sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, monospace;
  --content: 1040px; --narrow: 880px;
  --ease: cubic-bezier(0.2, 0.7, 0.2, 1);
  font-family: var(--sans); font-size: 16px; line-height: 1.6; color: var(--ink); background: var(--white);
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
}
.concord *, .concord *::before, .concord *::after { box-sizing: border-box; }
.concord :where(h1, h2, h3, h4, p, blockquote, dl, dd, ol, ul) { margin: 0; padding: 0; }
.concord [tabindex="-1"]:focus { outline: none; }
.sr-only { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
.num { font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 0.92em; letter-spacing: 0; white-space: nowrap; }
.text-red { color: var(--red); }

/* Sections */
.section { position: relative; display: flex; align-items: center; min-height: 100vh; padding: 72px 0; }
.tone-tint { background: var(--tint); }
.tone-dark { background: var(--navy); color: var(--on-dark); }
.wrap { width: 100%; max-width: calc(var(--content) + 64px); margin: 0 auto; padding: 0 32px; }

/* Type */
.eyebrow { margin-bottom: 16px; font-size: 13px; font-weight: 500; color: var(--blue); }
.wordmark, .display, .h2, .verdict { font-family: var(--serif); font-weight: 600; color: var(--navy); }
.display, .h2 { text-wrap: balance; }
.display { max-width: 920px; font-size: clamp(38px, 5.2vw, 56px); line-height: 1.1; letter-spacing: -0.015em; }
.h2 { max-width: 760px; font-size: clamp(30px, 3.4vw, 40px); line-height: 1.15; letter-spacing: -0.01em; }
.h2-wide { max-width: none; }
.subtitle { margin-top: 12px; font-family: var(--serif); font-style: italic; font-size: clamp(20px, 2vw, 24px); line-height: 1.35; color: var(--muted); }
.lede { max-width: 640px; margin-top: 20px; font-size: 19px; line-height: 1.6; color: var(--muted); }
.caption { font-size: 14px; line-height: 1.5; color: var(--muted); }
.caption-serif { max-width: 640px; font-family: var(--serif); font-style: italic; font-size: 19px; line-height: 1.45; color: var(--muted); text-wrap: pretty; }
.em { font-weight: 500; color: var(--navy); }

/* Reveal */
.reveal > * { opacity: 0; transform: translateY(8px); transition: opacity 400ms var(--ease), transform 400ms var(--ease); transition-delay: calc(var(--delay, 0ms) + var(--i, 0) * var(--stagger, 60ms)); }
.reveal.is-in > * { opacity: 1; transform: none; }
.reveal > :nth-child(2) { --i: 1; } .reveal > :nth-child(3) { --i: 2; }
.reveal > :nth-child(4) { --i: 3; } .reveal > :nth-child(5) { --i: 4; }
.fade-in { animation: fade-in 400ms var(--ease) both; }
@keyframes fade-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }

/* Shared surfaces */
.card { background: var(--white); border: 1px solid var(--line); border-radius: 6px; }
.pill { display: inline-block; padding: 2px 8px; border-radius: 4px; font-family: var(--sans); font-size: 12px; font-weight: 500; line-height: 1.5; white-space: nowrap; }
.pill-green { background: var(--green-soft); color: var(--green); } .pill-red { background: var(--red-soft); color: var(--red); }
.pill-amber { background: var(--amber-soft); color: var(--amber); } .pill-blue { background: var(--tint); color: var(--blue); }
.btn { padding: 10px 16px; border: 1px solid transparent; border-radius: 4px; font-family: var(--sans); font-size: 14px; font-weight: 500; line-height: 1; cursor: pointer; transition: background-color 150ms, border-color 150ms, color 150ms; }
.btn:focus { outline: none; } .btn:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
.btn-lg { padding: 13px 22px; font-size: 15px; }
.btn-ghost { border-color: var(--line); background: transparent; color: var(--navy); } .btn-ghost:hover { border-color: var(--line-strong); background: var(--tint); }
.btn-primary { border-color: var(--blue); background: var(--blue); color: var(--white); } .btn-primary:hover { border-color: var(--blue-hover); background: var(--blue-hover); }

/* Chapter counter */
.masthead { position: fixed; top: 20px; right: 24px; z-index: 10; opacity: 0; visibility: hidden; transition: opacity 400ms var(--ease), visibility 0s linear 400ms; }
.masthead.is-shown { opacity: 1; visibility: visible; transition: opacity 400ms var(--ease); }
.counter { display: flex; align-items: baseline; gap: 10px; padding: 6px 12px; border-radius: 4px; font-size: 13px; color: var(--muted); background: rgba(255, 255, 255, 0.9); transition: background-color 300ms, color 300ms; }
.counter-num { font-size: 12px; color: var(--muted); }
.counter-title { font-family: var(--serif); font-style: italic; font-size: 14px; color: var(--navy); animation: fade-in 400ms var(--ease) both; }
.masthead.on-tint .counter { background: rgba(234, 244, 251, 0.92); } .masthead.on-dark .counter { background: rgba(11, 37, 69, 0.92); }
.masthead.on-dark .counter-num { color: var(--on-dark-muted); } .masthead.on-dark .counter-title { color: var(--on-dark); }

/* Cover */
.cover { min-height: 100vh; min-height: 100svh; padding: 96px 0; text-align: center; }
.cover-inner { display: flex; flex-direction: column; align-items: center; }
.cover-inner > *, .cover-caption { animation: fade 900ms var(--ease) both; }
.cover-inner > :nth-child(2) { animation-delay: 120ms; } .cover-inner > :nth-child(3) { animation-delay: 240ms; }
.wordmark { font-size: clamp(56px, 19vw, 72px); line-height: 1; letter-spacing: -0.02em; }
.wordmark-dot { color: var(--blue); }
.cover-line { margin-top: 20px; font-size: 20px; line-height: 1.5; color: var(--muted); }
.cover-actions { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; margin-top: 40px; }
.cover-caption { position: absolute; left: 0; right: 0; bottom: 32px; padding: 0 20px; font-size: 13px; color: var(--muted); animation-delay: 360ms; }

/* 1 · The payment */
.facts { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 48px; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.fact { padding: 18px 24px; } .fact:first-child { padding-left: 0; } .fact + .fact { border-left: 1px solid var(--line); }
.fact dt { margin-bottom: 6px; font-size: 12px; color: var(--muted); } .fact dd { font-size: 16px; font-weight: 600; color: var(--navy); }
.timeline { position: relative; height: 124px; margin: 56px 0 28px; }
.tl-track { position: absolute; top: 42px; left: 0; right: 0; height: 2px; background: var(--line); }
.tl-fill { position: absolute; inset: 0; background: var(--navy); transform: scaleX(0); transform-origin: left top; transition: transform ${TIMELINE_MS}ms linear; }
.tl-risk { position: absolute; top: 0; right: 0; bottom: 0; opacity: 0; background: repeating-linear-gradient(90deg, var(--amber) 0 6px, transparent 6px 10px); transition: opacity 600ms var(--ease) ${TIMELINE_MS}ms; }
.timeline.is-in .tl-fill { transform: none; } .timeline.is-in .tl-risk { opacity: 1; }
.tl-points { list-style: none; }
.tl-point { position: absolute; top: 0; left: var(--pos); width: 240px; display: flex; flex-direction: column; align-items: center; text-align: center; transform: translateX(-50%); }
.tl-start { align-items: flex-start; text-align: left; transform: translateX(-7px); }
.tl-end { align-items: flex-end; text-align: right; transform: translateX(calc(-100% + 7px)); }
.tl-point > * { opacity: 0; transform: translateY(6px); transition: opacity 500ms var(--ease) var(--at), transform 500ms var(--ease) var(--at); }
.timeline.is-in .tl-point > * { opacity: 1; transform: none; }
.tl-date { height: 24px; margin-bottom: 12px; font-size: 13px; font-weight: 600; line-height: 24px; color: var(--navy); }
.tl-dot { position: relative; width: 14px; height: 14px; border: 2px solid var(--navy); border-radius: 50%; background: var(--white); color: var(--navy); }
.tl-dot::after { content: ""; position: absolute; inset: -2px; border: 2px solid currentColor; border-radius: 50%; opacity: 0; }
.tl-amber .tl-dot { border-color: var(--amber); background: var(--amber); color: var(--amber); }
.tl-red .tl-dot { border-color: var(--red); background: var(--red); color: var(--red); }
.timeline.is-in .tl-amber .tl-dot::after { animation: tl-pulse 1600ms ease-out 950ms 1 forwards; }
@keyframes tl-pulse { from { transform: scale(1); opacity: 0.6; } to { transform: scale(3.2); opacity: 0; } }
.tl-label { margin-top: 14px; font-size: 14px; line-height: 1.45; color: var(--muted); }
.tl-amber .tl-label, .tl-amber .tl-date { color: var(--amber); } .tl-red .tl-label, .tl-red .tl-date { color: var(--red); }

/* 2 · What usually happens */
.split { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 6fr); gap: 72px; margin-top: 32px; }
.ticks { list-style: none; border-top: 1px solid var(--line); }
.tick { display: grid; grid-template-columns: 32px minmax(0, 1fr) auto; gap: 12px; align-items: baseline; padding: 5px 4px; border-bottom: 1px solid var(--line); font-size: 14px; color: var(--muted); transition: color 200ms; }
.tick-n { font-size: 12px; color: var(--faint); } .tick-done { font-size: 13px; color: var(--green); opacity: 0; transition: opacity 240ms; }
.tick.is-done { color: var(--ink); } .tick.is-done .tick-n { color: var(--muted); } .tick.is-done .tick-done { opacity: 0.85; }
.pullquote { max-width: 640px; margin: 40px auto 0; text-align: center; font-family: var(--serif); font-style: italic; font-size: 24px; line-height: 1.4; color: var(--muted); text-wrap: balance; }

/* 3 · Watch Concord */
.run { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr); gap: 56px; align-items: start; margin-top: 40px; }
.run-list { list-style: none; border-top: 1px solid var(--line); }
.run-row { display: grid; grid-template-columns: 32px minmax(0, 1fr) 84px; gap: 12px; align-items: start; padding: 9px 12px 9px 8px; border-bottom: 1px solid var(--line); transition: background-color 240ms; }
.run-n { padding-top: 3px; font-size: 12px; color: var(--faint); }
.run-name { display: block; font-size: 15px; font-weight: 500; color: var(--navy); transition: color 200ms; }
.run-note { display: block; margin-top: 1px; font-size: 13px; line-height: 1.5; color: var(--muted); opacity: 0; transition: opacity 300ms; }
.run-status { justify-self: end; min-height: 22px; } .run-dash { color: var(--faint); }
.run-row.is-pending .run-name, .run-row.is-skip .run-name, .run-row.is-skip .run-n { color: var(--faint); }
.run-row.is-current { background: var(--tint); }
.run-row.is-pass .run-note, .run-row.is-fail .run-note { opacity: 1; }
.run-row.is-fail { background: var(--red-soft); box-shadow: inset 2px 0 0 var(--red); }
.run-row.is-fail .run-note, .run-row.is-fail .run-n { color: var(--red); }
.run-side { position: sticky; top: 88px; display: grid; gap: 20px; }
.decision { position: relative; overflow: hidden; padding: 22px 28px 18px; }
.decision::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--amber); transform: scaleX(0); transform-origin: left; transition: transform 500ms var(--ease); }
.decision.is-hold::before { transform: scaleX(1); }
.decision-label { font-size: 12px; color: var(--muted); }
.verdict { margin: 2px 0 14px; font-size: 40px; line-height: 1.15; color: var(--faint); } .verdict.is-set { color: var(--amber); }
.decision-rows > div { display: grid; grid-template-columns: 136px minmax(0, 1fr); gap: 12px; padding: 11px 0; border-top: 1px solid var(--line); font-size: 14px; }
.decision-rows dt { color: var(--muted); } .decision-rows dd { font-weight: 500; color: var(--navy); }
.decision-rows dd.is-placeholder { font-weight: 400; color: var(--faint); }
.decision-sub { display: block; margin-top: 2px; font-size: 13px; font-weight: 400; color: var(--muted); text-wrap: pretty; }
.letter { overflow: hidden; opacity: 0; transform: translateY(8px); transition: opacity 500ms var(--ease), transform 500ms var(--ease); }
.letter.is-in { opacity: 1; transform: none; }
.letter-head { display: grid; gap: 4px; padding: 14px 20px; border-bottom: 1px solid var(--line); font-size: 13px; }
.letter-head > div { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 8px; }
.letter-head dt { color: var(--muted); } .letter-head dd { font-weight: 500; color: var(--navy); }
.letter-body { display: grid; gap: 12px; padding: 18px 20px; background: var(--tint); font-family: var(--serif); font-size: 16px; line-height: 1.55; color: var(--ink); }
.letter-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; min-height: 62px; padding: 12px 20px; border-top: 1px solid var(--line); }
.letter-label { margin-right: auto; font-size: 13px; color: var(--muted); }
.approved { font-size: 14px; font-weight: 500; color: var(--green); }

/* 4 · The receipts */
.tone-dark .eyebrow { color: var(--on-dark-accent); }
.tone-dark .h2, .tone-dark .em { color: var(--on-dark); }
.tone-dark .lede { color: var(--on-dark-muted); }
.receipts { width: 100%; max-width: var(--narrow); margin-top: 28px; border-collapse: collapse; font-size: 15px; }
.receipts th, .receipts td { padding: 10px 16px 10px 0; border-bottom: 1px solid var(--on-dark-line); text-align: left; }
.receipts thead th { border-top: 1px solid var(--on-dark-line); font-size: 13px; font-weight: 500; color: var(--on-dark-muted); }
.receipts tbody th { font-weight: 500; color: var(--on-dark); }
.receipts td { color: var(--on-dark-muted); } .receipts td.is-good { font-weight: 600; color: var(--on-dark-good); }
.prism { max-width: var(--narrow); margin-top: 28px; padding: 18px 24px 6px; border: 1px solid var(--on-dark-line); border-radius: 6px; background: rgba(255, 255, 255, 0.03); }
.prism-eyebrow { font-size: 13px; font-weight: 500; color: var(--on-dark-accent); }
.cases { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 12px; }
.case { padding: 0 24px 12px 0; } .case + .case { padding: 0 0 12px 24px; border-left: 1px solid var(--on-dark-line); }
.case-title { font-size: 14px; font-weight: 600; color: var(--on-dark); }
.case-rows { margin-top: 8px; }
.case-rows > div { display: grid; grid-template-columns: 116px minmax(0, 1fr); gap: 12px; padding: 7px 0; border-top: 1px solid var(--on-dark-line); font-size: 14px; line-height: 1.5; }
.case-rows dt { color: var(--on-dark-muted); } .case-rows dd { color: var(--on-dark); }
.case-empty { font-style: italic; color: var(--on-dark-faint); } .case-quote { font-family: var(--serif); font-style: italic; font-size: 15px; }
.tone-dark .receipts-caption { max-width: var(--narrow); margin-top: 14px; color: var(--on-dark-muted); }

/* Footer */
.footer { padding: 28px 32px 40px; border-top: 1px solid var(--line); text-align: center; font-size: 13px; color: var(--muted); }

/* Responsive */
@media (max-width: 900px) {
  .split, .run { grid-template-columns: minmax(0, 1fr); gap: 40px; }
  .split-spacer { display: none; } .run-side { position: static; }
}
@media (max-width: 760px) {
  .facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .fact:nth-child(3) { padding-left: 0; border-left: 0; } .fact:nth-child(n + 3) { border-top: 1px solid var(--line); }
  .cases { grid-template-columns: minmax(0, 1fr); } .case { padding-right: 0; }
  .case + .case { padding: 16px 0 12px; border-left: 0; border-top: 1px solid var(--on-dark-line); }
}
@media (max-width: 559px) {
  .masthead { display: none; }
  .section { padding: 64px 0; } .wrap { padding: 0 20px; } .lede { font-size: 17px; }
  .facts { grid-template-columns: minmax(0, 1fr); margin-top: 40px; }
  .fact, .fact:first-child, .fact:nth-child(3) { padding: 14px 0; border-left: 0; }
  .fact + .fact { border-left: 0; border-top: 1px solid var(--line); }
  .timeline { height: auto; margin: 44px 0 28px; }
  .tl-track { top: 10px; bottom: 31px; left: 6px; right: auto; width: 2px; height: auto; }
  .tl-fill { transform: scaleY(0); } .tl-risk { display: none; }
  .tl-points { display: grid; gap: 28px; }
  .tl-point, .tl-start, .tl-end { position: static; display: grid; grid-template-columns: 14px minmax(0, 1fr); column-gap: 16px; align-items: start; width: auto; text-align: left; transform: none; }
  .tl-dot { grid-column: 1; grid-row: 1 / span 2; margin-top: 3px; }
  .tl-date { grid-column: 2; height: auto; margin: 0; line-height: 1.5; }
  .tl-label { grid-column: 2; margin-top: 2px; }
  .pullquote { font-size: 21px; }
  .run-row { grid-template-columns: 26px minmax(0, 1fr) auto; padding-right: 6px; }
  .decision { padding: 20px; }
  .decision-rows > div, .case-rows > div { grid-template-columns: minmax(0, 1fr); gap: 2px; }
  .letter-label { flex: 1 0 100%; } .letter-foot .btn { flex: 1; }
  .receipts { font-size: 14px; } .prism { padding: 18px 18px 6px; }
}

/* Reduced motion: no transitions, final states immediately. */
@media (prefers-reduced-motion: reduce) {
  .concord *, .concord *::before, .concord *::after { animation: none !important; transition: none !important; }
  .reveal > *, .tl-point > * { opacity: 1 !important; transform: none !important; }
  .tl-fill { transform: none !important; } .tl-risk { opacity: 1 !important; }
}
`;
