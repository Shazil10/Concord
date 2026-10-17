import React, { useEffect, useRef, useState } from "react";

const CHECKS = [
  "Load trade",
  "Read our confirmation",
  "Read their confirmation",
  "Custodian status",
  "Look up instructions",
  "Bank and branch",
  "Account vs instructions",
  "Both sides agree",
  "Amounts and dates",
  "Fail cost",
  "Decide",
  "Draft note",
];

type Status = "pass" | "fail";
type Run = { status: Record<number, Status>; notes: Record<number, string> };

const V1: Run = {
  status: {},
  notes: {
    4: "Read an old copy from August: 90052000",
    6: "90052000 matches the old copy",
  },
};

const V2: Run = {
  status: { 6: "fail" },
  notes: {
    4: "Live registry, version 2 from 1 October: 90052002",
    6: "Our confirmation says 90052000. The registry says 90052002.",
  },
};

const TRADES: [string, string, string, string, string, string, string][] = [
  ["T001", "Lumen Markets", "USD 5,450,000", "17 Oct", "Release", "", ""],
  ["T002", "Kite Rowan Securities", "USD 2,540,000", "21 Oct", "Release", "", ""],
  ["T003", "Sable Fund Services", "USD 9,850,000", "19 Oct", "Release", "", ""],
  ["T004", "Veldt Capital", "USD 5,000,000", "20 Oct", "Release", "", ""],
  ["T005", "Quill Asset Management", "EUR 4,050,000", "21 Oct", "Release", "", ""],
  ["T006", "Marlow Brothers", "EUR 2,760,000", "19 Oct", "Release", "", ""],
  ["T007", "Birch Capital", "USD 1,308,000", "19 Oct", "Hold", "Us", "Email"],
  ["T008", "Birch Capital", "EUR 940,000", "17 Oct", "Hold", "Us", "Call"],
  ["T009", "Holm Securities", "USD 5,940,000", "21 Oct", "Hold", "Us", "Email"],
  ["T010", "Holm Securities", "USD 2,725,000", "20 Oct", "Hold", "Us", "Email"],
  ["T011", "Orion Desk", "USD 981,000", "19 Oct", "Hold", "Counterparty", "Email"],
  ["T012", "Pebble Street Capital", "USD 2,500,000", "17 Oct", "Hold", "Counterparty", "Call"],
  ["T013", "Cedar Point Markets", "USD 2,000,000", "22 Oct", "Hold", "Counterparty", "Email"],
  ["T014", "Pebble Street Capital", "USD 763,000", "19 Oct", "Hold", "Counterparty", "Email"],
  ["T015", "Pebble Street Capital", "USD 7,780,000", "21 Oct", "Hold", "Us", "Email"],
  ["T016", "Lumen Markets", "USD 1,635,000", "20 Oct", "Hold", "Us", "Email"],
  ["T017", "Kite Rowan Securities", "USD 1,090,000", "19 Oct", "Hold", "Counterparty", "Email"],
  ["T018", "Sable Fund Services", "USD 3,060,000", "21 Oct", "Hold", "Counterparty", "Email"],
  ["T019", "Quill Asset Management", "EUR 1,500,000", "17 Oct", "Hold", "Counterparty", "Call"],
  ["T020", "Veldt Capital", "USD 5,025,000", "23 Oct", "Hold", "Counterparty", "Email"],
];

const SECTIONS = ["payment", "v1", "prism", "v2", "results"];

function useRunWhenVisible(ref: React.RefObject<HTMLElement>) {
  const [shown, setShown] = useState(0);
  const [runId, setRunId] = useState(0);
  const started = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !started.current) {
          started.current = true;
          setRunId((n) => n + 1);
        }
      },
      { threshold: 0.35 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [ref]);

  useEffect(() => {
    if (runId === 0) return;
    setShown(0);
    let i = 0;
    const t = window.setInterval(() => {
      i += 1;
      setShown(i);
      if (i >= CHECKS.length) window.clearInterval(t);
    }, 140);
    return () => window.clearInterval(t);
  }, [runId]);

  return { shown, done: shown >= CHECKS.length, replay: () => setRunId((n) => n + 1) };
}

function Checklist({ run, shown }: { run: Run; shown: number }) {
  return (
    <ol className="cc-checks">
      {CHECKS.map((name, i) => {
        const visible = i < shown;
        const status = run.status[i] ?? "pass";
        const cls = !visible ? "pending" : status;
        return (
          <li key={name} className={`cc-check ${cls}`}>
            <span className="cc-check-n">{String(i + 1).padStart(2, "0")}</span>
            <span className="cc-check-body">
              <span className="cc-check-name">{name}</span>
              {visible && run.notes[i] && <span className="cc-check-note">{run.notes[i]}</span>}
            </span>
            <span className="cc-check-status">
              {!visible ? "" : status === "pass" ? "Passed" : "Failed"}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

export default function Concord() {
  const [current, setCurrent] = useState(0);
  const [approved, setApproved] = useState(false);
  const refs = useRef<(HTMLElement | null)[]>([]);
  const v1Ref = useRef<HTMLElement>(null);
  const v2Ref = useRef<HTMLElement>(null);
  const v1 = useRunWhenVisible(v1Ref);
  const v2 = useRunWhenVisible(v2Ref);

  useEffect(() => {
    if (!document.getElementById("cc-fonts")) {
      const link = document.createElement("link");
      link.id = "cc-fonts";
      link.rel = "stylesheet";
      link.href =
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap";
      document.head.appendChild(link);
    }
  }, []);

  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            const idx = refs.current.indexOf(e.target as HTMLElement);
            if (idx >= 0) setCurrent(idx);
          }
        });
      },
      { rootMargin: "-45% 0px -45% 0px" }
    );
    refs.current.forEach((el) => el && io.observe(el));
    return () => io.disconnect();
  }, []);

  const go = (idx: number) => {
    const target = Math.max(0, Math.min(SECTIONS.length - 1, idx));
    refs.current[target]?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === "PageDown") {
        e.preventDefault();
        go(current + 1);
      } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
        e.preventDefault();
        go(current - 1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const setRef = (i: number, extra?: React.RefObject<HTMLElement>) => (el: HTMLElement | null) => {
    refs.current[i] = el;
    if (extra) (extra as React.MutableRefObject<HTMLElement | null>).current = el;
  };

  return (
    <div className="cc">
      <style>{CSS}</style>

      <header className="cc-top">
        <div className="cc-wrap cc-top-inner">
          <div className="cc-brand">
            <span className="cc-wordmark">Concord</span>
            <span className="cc-brand-sub">Pre-settlement checks</span>
          </div>
          <div className="cc-top-meta">Northline Treasury · fictional data</div>
        </div>
      </header>

      <main>
        {/* 1 */}
        <section ref={setRef(0)} className="cc-section cc-first">
          <div className="cc-wrap">
            <p className="cc-step">1 of 5 · The payment</p>
            <h1 className="cc-h1">EUR 940,000 is about to be paid to Birch Capital.</h1>
            <p className="cc-lede">
              Before money moves, every party has to agree on where it goes. Concord checks that, for every
              trade, before anything is released.
            </p>

            <dl className="cc-facts">
              <div><dt>Trade</dt><dd>T008 · FX spot</dd></div>
              <div><dt>We pay</dt><dd>EUR 940,000</dd></div>
              <div><dt>Value date</dt><dd>17 Oct 2026 <span className="cc-today">today</span></dd></div>
              <div><dt>Counterparty</dt><dd>Birch Capital</dd></div>
            </dl>

            <table className="cc-table cc-sources">
              <thead>
                <tr><th>Source</th><th>Bank</th><th>Branch</th><th className="num">Account</th></tr>
              </thead>
              <tbody>
                <tr><td>Our confirmation</td><td>Quay and Company</td><td>Frankfurt</td><td className="num mono">90052000</td></tr>
                <tr><td>Their confirmation</td><td>Quay and Company</td><td>Frankfurt</td><td className="num mono">90052000</td></tr>
                <tr className="cc-hl">
                  <td>Instructions on file<span className="cc-sub">since 1 October</span></td>
                  <td>Quay and Company</td><td>Frankfurt</td><td className="num mono">90052002</td>
                </tr>
              </tbody>
            </table>
            <p className="cc-caption">
              Birch Capital emailed its new account on 1 October. Both confirmations still carry the old one, so
              they agree with each other and are both wrong.
            </p>
          </div>
        </section>

        {/* 2 */}
        <section ref={setRef(1, v1Ref)} className="cc-section">
          <div className="cc-wrap">
            <p className="cc-step">2 of 5 · First version</p>
            <h2 className="cc-h2">Concord v1 passes every check, and pays the wrong account.</h2>
            <div className="cc-run">
              <Checklist run={V1} shown={v1.shown} />
              <aside className={`cc-decision ${v1.done ? "in" : ""}`}>
                <p className="cc-label">Decision</p>
                <p className="cc-verdict release">Release</p>
                <div className="cc-outcome bad">
                  EUR 940,000 would have gone to account 90052000, which Birch Capital closed on 1 October.
                </div>
                <p className="cc-note">
                  The same bug released 4 trades worth USD 9.97M and EUR 0.94M. A second bug crashed v1 whenever a
                  counterparty had not sent its confirmation.
                </p>
                <button className="cc-link" onClick={v1.replay}>Run again</button>
              </aside>
            </div>
          </div>
        </section>

        {/* 3 */}
        <section ref={setRef(2)} className="cc-section cc-tint">
          <div className="cc-wrap">
            <p className="cc-step">3 of 5 · Observe</p>
            <h2 className="cc-h2">PRISM caught both bugs on real runs.</h2>
            <div className="cc-cards">
              <div className="cc-card">
                <div className="cc-card-head">
                  <span>Alert · Trace failure alerts</span>
                  <span className="cc-chip red">Fired</span>
                </div>
                <p className="cc-metric">6<span> failed traces in the last hour</span></p>
                <p className="cc-card-foot">Threshold 5. Each failure is a v1 run that ended with no answer.</p>
              </div>
              <div className="cc-card">
                <div className="cc-card-head">
                  <span>Root cause · one cluster</span>
                  <span className="cc-chip">Verified as tool error</span>
                </div>
                <p className="cc-metric">52<span> failed runs, one cause</span></p>
                <p className="cc-card-foot">
                  The agent stopped at step 3 when a confirmation was missing. Separately, v1 read a snapshot of the
                  instructions instead of the live registry.
                </p>
              </div>
            </div>
            <h3 className="cc-h3">One trace, before and after</h3>
            <table className="cc-table cc-trace">
              <thead>
                <tr>
                  <th>Trace</th>
                  <th>Trade</th>
                  <th className="num">Steps</th>
                  <th>Output</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>v1</td>
                  <td>T019 · Quill Asset Management sent no confirmation</td>
                  <td className="num">3 of 12</td>
                  <td className="bad">Empty. Error: missing confirmation</td>
                </tr>
                <tr>
                  <td>v2</td>
                  <td>T019 · same input</td>
                  <td className="num">12 of 12</td>
                  <td className="good">Hold: missing counterparty confirmation, chase required</td>
                </tr>
              </tbody>
            </table>
            <p className="cc-caption">Every run is traced step by step in PRISM by Block Convey.</p>
          </div>
        </section>

        {/* 4 */}
        <section ref={setRef(3, v2Ref)} className="cc-section">
          <div className="cc-wrap">
            <p className="cc-step">4 of 5 · Second version, same payment</p>
            <h2 className="cc-h2">Concord v2 reads the live registry and holds the payment.</h2>
            <div className="cc-run">
              <Checklist run={V2} shown={v2.shown} />
              <aside className={`cc-decision ${v2.done ? "in" : ""}`}>
                <p className="cc-label">Decision</p>
                <p className="cc-verdict hold">Hold</p>
                <dl className="cc-mini">
                  <div><dt>Fault</dt><dd>Us</dd></div>
                  <div><dt>Action</dt><dd>Call, it settles today</dd></div>
                  <div><dt>Est. cost if it fails</dt><dd>EUR 5,129</dd></div>
                </dl>
                <button className="cc-link" onClick={v2.replay}>Run again</button>
              </aside>
            </div>

            <div className="cc-letter">
              <div className="cc-letter-head">
                <div><span>To</span>Birch Capital, settlements</div>
                <div><span>Subject</span>T008 · new euro account before release</div>
              </div>
              <p className="cc-letter-body">
                Birch Capital, your euro account changed on 1 October to 90052002 at Quay and Company, Frankfurt.
                Our confirmation still pays 90052000. Please confirm before we release.
              </p>
              <div className="cc-letter-foot">
                {approved ? (
                  <p className="cc-approved">Approved. Added to the outbox. Not sent.</p>
                ) : (
                  <>
                    <span className="cc-muted">Draft · not sent</span>
                    <div className="cc-actions">
                      <button className="cc-btn ghost">Keep on hold</button>
                      <button className="cc-btn" onClick={() => setApproved(true)}>Approve</button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* 5 */}
        <section ref={setRef(4)} className="cc-section">
          <div className="cc-wrap">
            <p className="cc-step">5 of 5 · Improve</p>
            <h2 className="cc-h2">Twenty trades, before and after.</h2>
            <table className="cc-table cc-score">
              <thead><tr><th></th><th className="num">v1</th><th className="num">v2</th></tr></thead>
              <tbody>
                <tr><td>Right decision</td><td className="num">14 of 20</td><td className="num good">20 of 20</td></tr>
                <tr><td>Paid to a closed account</td><td className="num bad">4</td><td className="num good">0</td></tr>
                <tr><td>Crashed with no answer</td><td className="num bad">2</td><td className="num good">0</td></tr>
                <tr><td>Fault named correctly</td><td className="num">14 of 20</td><td className="num good">20 of 20</td></tr>
              </tbody>
            </table>

            <details className="cc-all">
              <summary>See all 20 trades</summary>
              <table className="cc-table cc-trades">
                <thead>
                  <tr><th>Trade</th><th>Counterparty</th><th className="num">Cash</th><th>Settles</th><th>Decision</th><th>Fault</th><th>Action</th></tr>
                </thead>
                <tbody>
                  {TRADES.map(([id, cp, cash, date, dec, fault, action]) => (
                    <tr key={id}>
                      <td className="mono">{id}</td>
                      <td>{cp}</td>
                      <td className="num mono">{cash}</td>
                      <td>{date}</td>
                      <td><span className={`cc-pill ${dec === "Release" ? "release" : "hold"}`}>{dec}</span></td>
                      <td>{fault}</td>
                      <td className={action === "Call" ? "call" : ""}>{action}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </details>
          </div>
        </section>
      </main>

      <footer className="cc-foot">
        <div className="cc-wrap">Concord · synthetic data · built with Nicrron and Ninoo · traced in PRISM</div>
      </footer>

      <nav className="cc-pager" aria-label="Presenter controls">
        <button onClick={() => go(current - 1)} disabled={current === 0} aria-label="Previous">←</button>
        <span>{current + 1} / {SECTIONS.length}</span>
        <button onClick={() => go(current + 1)} disabled={current === SECTIONS.length - 1}>Next →</button>
      </nav>
    </div>
  );
}

const CSS = `
.cc{--navy:#0B2545;--ink:#22303F;--muted:#5D6B7A;--line:#D9E2EC;--line-2:#E8EEF4;--blue:#0071BC;--blue-50:#EAF4FB;--green:#1E7B45;--green-50:#E9F5EE;--red:#B42318;--red-50:#FCEDEB;--amber:#B54708;--amber-50:#FDF2E3;
  font-family:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:#fff;font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased;min-height:100vh}
.cc *{box-sizing:border-box}
.cc-wrap{max-width:1040px;margin:0 auto;padding:0 32px}
.cc-top{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.96);border-bottom:1px solid var(--line)}
.cc-top-inner{display:flex;align-items:center;justify-content:space-between;height:60px}
.cc-brand{display:flex;align-items:baseline;gap:14px}
.cc-wordmark{font-family:"Source Serif 4",Georgia,serif;font-weight:600;font-size:22px;color:var(--navy);letter-spacing:-.01em}
.cc-brand-sub{font-size:14px;color:var(--muted);padding-left:14px;border-left:1px solid var(--line)}
.cc-top-meta{font-size:14px;color:var(--muted)}

.cc-section{padding:88px 0;border-bottom:1px solid var(--line-2);scroll-margin-top:60px;min-height:calc(100vh - 60px)}
.cc-first{padding-top:72px}
.cc-tint{background:#F6FAFD}
.cc-step{margin:0 0 14px;font-size:14px;font-weight:500;color:var(--blue)}
.cc-h1,.cc-h2{font-family:"Source Serif 4",Georgia,serif;color:var(--navy);font-weight:600;letter-spacing:-.015em;margin:0}
.cc-h1{font-size:46px;line-height:1.12;max-width:760px}
.cc-h2{font-size:34px;line-height:1.2;max-width:760px;margin-bottom:36px}
.cc-lede{font-size:19px;color:var(--muted);max-width:640px;margin:18px 0 40px}

.cc-facts{display:grid;grid-template-columns:repeat(4,1fr);margin:0 0 32px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.cc-facts>div{padding:16px 20px 16px 0}
.cc-facts>div+div{padding-left:20px;border-left:1px solid var(--line-2)}
.cc-facts dt,.cc-mini dt{font-size:13px;color:var(--muted);margin-bottom:4px}
.cc-facts dd,.cc-mini dd{margin:0;font-weight:600;color:var(--navy)}
.cc-today{display:inline-block;margin-left:6px;font-size:12px;font-weight:600;color:var(--red);background:var(--red-50);padding:1px 7px;border-radius:4px;vertical-align:2px}

.cc-table{width:100%;border-collapse:collapse;font-size:15px}
.cc-table th{text-align:left;font-weight:500;font-size:13px;color:var(--muted);padding:10px 14px;border-bottom:1px solid var(--line)}
.cc-table td{padding:14px;border-bottom:1px solid var(--line-2);color:var(--ink)}
.cc-table .num{text-align:right}
.mono{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:14px;font-variant-numeric:tabular-nums}
.cc-sources td:first-child{font-weight:500;color:var(--navy)}
.cc-sub{display:block;font-size:13px;font-weight:400;color:var(--muted)}
.cc-hl td{background:var(--blue-50)}
.cc-hl td:last-child{color:var(--blue);font-weight:600}
.cc-caption{color:var(--muted);font-size:15px;margin:16px 0 0;max-width:680px}

.cc-run{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:48px;align-items:start}
.cc-checks{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
.cc-check{display:grid;grid-template-columns:34px 1fr auto;gap:12px;align-items:baseline;padding:11px 12px 11px 4px;border-bottom:1px solid var(--line-2);transition:background .2s ease,color .2s ease}
.cc-check-n{font-size:13px;color:#9AA7B4;font-variant-numeric:tabular-nums}
.cc-check-name{font-size:15px;color:var(--navy)}
.cc-check-note{display:block;font-size:13px;color:var(--muted);margin-top:2px}
.cc-check-status{font-size:13px;font-weight:600;min-width:52px;text-align:right}
.cc-check.pending .cc-check-name{color:#A7B3BF}
.cc-check.pass .cc-check-status{color:var(--green)}
.cc-check.fail{background:var(--red-50)}
.cc-check.fail .cc-check-status,.cc-check.fail .cc-check-note{color:var(--red)}

.cc-decision{position:sticky;top:96px;border:1px solid var(--line);border-radius:6px;padding:24px;opacity:.25;transition:opacity .35s ease}
.cc-decision.in{opacity:1}
.cc-label{margin:0;font-size:13px;color:var(--muted)}
.cc-verdict{font-family:"Source Serif 4",Georgia,serif;font-size:40px;font-weight:600;margin:2px 0 18px;line-height:1.1}
.cc-verdict.release{color:var(--green)}
.cc-verdict.hold{color:var(--amber)}
.cc-outcome{padding:14px 16px;border-radius:6px;font-size:15px;font-weight:500}
.cc-outcome.bad{background:var(--red-50);color:var(--red);border-left:3px solid var(--red)}
.cc-note{font-size:14px;color:var(--muted);margin:16px 0 0}
.cc-mini{margin:0;display:grid;gap:14px}
.cc-link{margin-top:18px;background:none;border:0;padding:0;color:var(--blue);font:inherit;font-size:14px;cursor:pointer}
.cc-link:hover{text-decoration:underline}

.cc-cards{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.cc-card{background:#fff;border:1px solid var(--line);border-radius:6px;padding:22px 24px}
.cc-card-head{display:flex;justify-content:space-between;align-items:center;font-size:14px;color:var(--muted);margin-bottom:14px}
.cc-chip{font-size:12px;font-weight:600;padding:2px 8px;border-radius:4px;background:var(--blue-50);color:var(--blue)}
.cc-chip.red{background:var(--red-50);color:var(--red)}
.cc-metric{font-family:"Source Serif 4",Georgia,serif;font-size:44px;font-weight:600;color:var(--navy);margin:0 0 10px;line-height:1}
.cc-metric span{font-family:"Inter",system-ui,sans-serif;font-size:16px;font-weight:500;color:var(--ink);margin-left:8px}
.cc-h3{font-family:"Source Serif 4",Georgia,serif;font-weight:600;font-size:20px;color:var(--navy);margin:48px 0 12px}
.cc-trace{background:#fff;border:1px solid var(--line);border-radius:6px;overflow:hidden}
.cc-trace th.num,.cc-trace td.num{text-align:right;white-space:nowrap}
.cc-trace td:first-child{font-weight:600;width:56px}
.cc-trace td.bad{color:var(--red)}
.cc-trace td.good{color:var(--green)}
.cc-trace tr:last-child td{border-bottom:0}
.cc-card-foot{margin:0;font-size:15px;color:var(--muted)}

.cc-letter{margin-top:40px;border:1px solid var(--line);border-radius:6px;max-width:720px}
.cc-letter-head{padding:14px 20px;border-bottom:1px solid var(--line-2);font-size:14px;display:grid;gap:4px}
.cc-letter-head span{display:inline-block;width:72px;color:var(--muted)}
.cc-letter-body{margin:0;padding:20px;font-size:16px;color:var(--navy);background:var(--blue-50)}
.cc-letter-foot{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;border-top:1px solid var(--line-2);min-height:64px}
.cc-muted{font-size:14px;color:var(--muted)}
.cc-actions{display:flex;gap:10px}
.cc-btn{font:inherit;font-size:15px;font-weight:500;padding:9px 18px;border-radius:6px;border:1px solid var(--blue);background:var(--blue);color:#fff;cursor:pointer;transition:background .15s ease}
.cc-btn:hover{background:#005C99}
.cc-btn.ghost{background:#fff;color:var(--navy);border-color:var(--line)}
.cc-btn.ghost:hover{background:#F4F7FA}
.cc-btn:focus-visible,.cc-link:focus-visible,.cc-pager button:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.cc-approved{margin:0;font-weight:500;color:var(--green)}

.cc-score{max-width:640px}
.cc-score td:first-child{color:var(--navy);font-weight:500}
.cc-score .good{color:var(--green);font-weight:600}
.cc-score .bad{color:var(--red);font-weight:600}
.cc-all{margin-top:36px}
.cc-all summary{cursor:pointer;color:var(--blue);font-size:15px;font-weight:500;margin-bottom:12px}
.cc-trades td{padding:10px 14px;font-size:14px}
.cc-pill{font-size:12px;font-weight:600;padding:2px 8px;border-radius:4px}
.cc-pill.release{background:var(--green-50);color:var(--green)}
.cc-pill.hold{background:var(--amber-50);color:var(--amber)}
.cc-trades .call{color:var(--red);font-weight:600}

.cc-foot{padding:28px 0 96px;font-size:13px;color:var(--muted)}
.cc-pager{position:fixed;right:24px;bottom:24px;display:flex;align-items:center;gap:12px;background:#fff;border:1px solid var(--line);border-radius:6px;padding:6px 6px 6px 12px;box-shadow:0 2px 10px rgba(11,37,69,.08);font-size:14px;color:var(--muted);z-index:20}
.cc-pager button{font:inherit;font-size:14px;border:1px solid var(--line);background:#fff;color:var(--navy);border-radius:4px;padding:6px 12px;cursor:pointer}
.cc-pager button:last-child{background:var(--blue);color:#fff;border-color:var(--blue)}
.cc-pager button:disabled{opacity:.4;cursor:default}

@media (max-width:820px){
  .cc-h1{font-size:34px}.cc-h2{font-size:26px}
  .cc-facts{grid-template-columns:1fr 1fr}
  .cc-facts>div+div{border-left:0;padding-left:0}
  .cc-run,.cc-cards{grid-template-columns:1fr}
  .cc-decision{position:static}
  .cc-brand-sub{display:none}
}
@media (max-width:560px){
  .cc-wrap{padding:0 20px}
  .cc-top-meta{display:none}
  .cc-section{padding:56px 0}
  .cc-h1{font-size:30px}
  .cc-table{display:block;overflow-x:auto}
  .cc-table th,.cc-table td{padding:10px 8px}
  .cc-letter-foot{flex-wrap:wrap;gap:12px}
  .cc-pager{display:none}
}
`;
