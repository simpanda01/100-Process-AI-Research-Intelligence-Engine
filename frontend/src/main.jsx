import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "http://127.0.0.1:8000/api";

function App() {
  const [stats, setStats] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [top, setTop] = useState([]);
  const [human, setHuman] = useState([]);
  const [selected, setSelected] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [search, setSearch] = useState("");
  const [industry, setIndustry] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  const [form, setForm] = useState({
    name: "",
    industry: "Retail",
    description: "",
  });

  async function load() {
    const [s, p, t, h] = await Promise.all([
      fetch(`${API}/stats`).then((r) => r.json()),

      fetch(
        `${API}/processes?search=${encodeURIComponent(
          search
        )}&industry=${encodeURIComponent(industry)}`
      ).then((r) => r.json()),

      fetch(`${API}/rankings/top?limit=10`).then((r) => r.json()),

      fetch(`${API}/rankings/human-led?limit=10`).then((r) => r.json()),
    ]);

    setStats(s);
    setProcesses(p);
    setTop(t);
    setHuman(h);
  }

  useEffect(() => {
    load();
  }, []);

  async function selectProcess(id) {
    const p = await fetch(`${API}/processes/${id}`).then((r) => r.json());

    const e = await fetch(`${API}/processes/${id}/evidence`).then((r) =>
      r.json()
    );

    setSelected(p);
    setEvidence(e);
  }

  async function analyze(id) {
    setBusy(true);
    setMessage("Analyzing process...");

    try {
      await fetch(`${API}/processes/${id}/analyze`, {
        method: "POST",
      });

      setMessage("Analysis completed.");

      await load();
      await selectProcess(id);
    } catch (e) {
      setMessage(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function analyzeAll() {
    setBusy(true);
    setMessage("Analyzing all 100 processes...");

    try {
      const r = await fetch(`${API}/analyze-all`, {
        method: "POST",
      });

      const d = await r.json();

      setMessage(`Completed ${d.completed} processes.`);

      await load();
    } catch (e) {
      setMessage(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function addProcess(e) {
    e.preventDefault();

    setBusy(true);
    setMessage("Creating process...");

    try {
      const r = await fetch(`${API}/processes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!r.ok) {
        throw new Error("Could not create process");
      }

      const p = await r.json();

      setForm({
        name: "",
        industry: "Retail",
        description: "",
      });

      await load();
      await selectProcess(p.id);

      setMessage("Process created. Now click Analyze.");
    } catch (e) {
      setMessage(e.message);
    } finally {
      setBusy(false);
    }
  }

  function handleIndustryChange(e) {
    const value = e.target.value;

    setIndustry(value);

    // Load processes using the newly selected industry.
    const url = `${API}/processes?search=${encodeURIComponent(
      search
    )}&industry=${encodeURIComponent(value)}`;

    fetch(url)
      .then((r) => r.json())
      .then((data) => setProcesses(data))
      .catch((e) => setMessage(e.message));
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>Enterprise AI Process Intelligence</h1>
          <p>
            100-Process AI Research &amp; Intelligence Engine
          </p>
        </div>

        <button disabled={busy} onClick={analyzeAll}>
          Analyze All
        </button>
      </header>

      {message && <div className="notice">{message}</div>}

      <div className="stats">
        <Stat
          t="Total Processes"
          v={stats?.total_processes ?? "-"}
        />

        <Stat
          t="Analyzed"
          v={stats?.analyzed_processes ?? "-"}
        />

        <Stat
          t="High Potential"
          v={stats?.high_ai_potential ?? "-"}
        />

        <Stat
          t="Avg AI Score"
          v={stats?.average_ai_score ?? "-"}
        />
      </div>

      <div className="grid">
        <section className="panel">
          <h2>Add New Process</h2>

          <form onSubmit={addProcess}>
            <input
              placeholder="Process name"
              value={form.name}
              onChange={(e) =>
                setForm({
                  ...form,
                  name: e.target.value,
                })
              }
              required
            />

            <input
              placeholder="Industry"
              value={form.industry}
              onChange={(e) =>
                setForm({
                  ...form,
                  industry: e.target.value,
                })
              }
              required
            />

            <textarea
              placeholder="Describe the process"
              value={form.description}
              onChange={(e) =>
                setForm({
                  ...form,
                  description: e.target.value,
                })
              }
              required
            />

            <button disabled={busy}>Add Process</button>
          </form>
        </section>

        <section className="panel">
          <h2>Top 10 AI Opportunities</h2>

          {top.map((p, i) => (
            <div
              className="row"
              key={p.id}
              onClick={() => selectProcess(p.id)}
            >
              <b>
                #{i + 1} {p.name}
              </b>

              <span>{p.ai_score}</span>
            </div>
          ))}

          {!top.length && (
            <p>Analyze processes to populate rankings.</p>
          )}
        </section>
      </div>

      <section className="panel">
        <div className="toolbar">
          <h2>Process Library</h2>

          <input
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                load();
              }
            }}
          />

          <select
            value={industry}
            onChange={handleIndustryChange}
          >
            <option value="">All Industries</option>
            <option value="Banking">Banking</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Logistics">Logistics</option>
            <option value="Manufacturing">Manufacturing</option>
            <option value="Retail">Retail</option>
          </select>

          <button onClick={load}>Search</button>
        </div>

        <div className="process-list">
          {processes.map((p) => (
            <div className="process-card" key={p.id}>
              <div
                className="clickable"
                onClick={() => selectProcess(p.id)}
              >
                <h3>{p.name}</h3>

                <p>
                  <b>{p.industry}</b> — {p.description}
                </p>

                {p.analysis && (
                  <div className="badges">
                    <span>
                      AI Score: {p.analysis.ai_score}
                    </span>

                    <span>
                      {p.analysis.automation_potential}
                    </span>
                  </div>
                )}
              </div>

              <button
                disabled={busy}
                onClick={() => analyze(p.id)}
              >
                {p.analysis ? "Re-analyze" : "Analyze"}
              </button>
            </div>
          ))}
        </div>
      </section>

      <div className="grid">
        <section className="panel">
          <h2>Human-Led Candidates</h2>

          {human.map((p) => (
            <div className="row" key={p.id}>
              <b>{p.name}</b>

              <span>{p.human_criticality_score}</span>
            </div>
          ))}
        </section>

        <section className="panel detail">
          <h2>
            {selected ? selected.name : "Process Details"}
          </h2>

          {!selected && <p>Select a process.</p>}

          {selected && !selected.analysis && (
            <p>Not analyzed yet.</p>
          )}

          {selected?.analysis && (
            <>
              <Detail
                t="Business Purpose"
                x={selected.analysis.business_purpose}
              />

              <Detail
                t="Key Activities"
                x={selected.analysis.key_activities}
              />

              <Detail
                t="Current Challenges"
                x={selected.analysis.current_challenges}
              />

              <Detail
                t="AI Opportunity"
                x={selected.analysis.ai_opportunity}
              />

              <Detail
                t="Human Involvement"
                x={selected.analysis.human_involvement}
              />

              <Detail
                t="Technologies"
                x={selected.analysis.technologies}
              />

              <Detail
                t="Business Benefit"
                x={selected.analysis.business_benefit}
              />

              <Detail
                t="Risks"
                x={selected.analysis.risks}
              />

              <Detail
                t="Reasoning"
                x={selected.analysis.reasoning}
              />

              <h3>Evidence</h3>

              {evidence.map((e, i) => (
                <div className="evidence" key={i}>
                  <b>{e.title}</b>

                  <small>
                    {e.source_type} — {e.source}
                  </small>

                  <p
                    dangerouslySetInnerHTML={{
                      __html: e.snippet,
                    }}
                  />

                  {e.url && (
                    <a
                      href={e.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open source
                    </a>
                  )}
                </div>
              ))}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

function Stat({ t, v }) {
  return (
    <div className="stat">
      <span>{t}</span>
      <strong>{v}</strong>
    </div>
  );
}

function Detail({ t, x }) {
  return (
    <div className="detail-block">
      <h3>{t}</h3>
      <p>{x}</p>
    </div>
  );
}

createRoot(document.getElementById("root")).render(
  <App />
);