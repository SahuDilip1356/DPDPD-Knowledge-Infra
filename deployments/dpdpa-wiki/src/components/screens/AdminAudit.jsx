import React, { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";

export default function AdminAudit() {
  const [adminKey, setAdminKey] = useState(() => {
    if (typeof window === "undefined") return "";
    return window.sessionStorage.getItem("dpdpa_admin_key") || "";
  });
  const [keyDraft, setKeyDraft] = useState("");
  const [logs, setLogs] = useState([]);
  const [ingestionLogs, setIngestionLogs] = useState([]);
  const [stats, setStats] = useState({
    total_knowledge_objects: 0,
    core_layer_count: 0,
    opinion_layer_count: 0,
    other_layers_count: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAdminData = useCallback(async () => {
    if (!adminKey) return;
    try {
      setLoading(true);
      const options = { headers: { "X-Admin-Key": adminKey } };
      const [statsRes, logsRes, ingestionRes] = await Promise.all([
        apiFetch("/admin/stats", options),
        apiFetch("/admin/search-audit", options),
        apiFetch("/admin/ingestion-audit", options),
      ]);

      if ([statsRes, logsRes, ingestionRes].some((response) => response.status === 401)) {
        window.sessionStorage.removeItem("dpdpa_admin_key");
        setAdminKey("");
        throw new Error("The admin key was rejected. Enter it again.");
      }
      if (!statsRes.ok || !logsRes.ok || !ingestionRes.ok) {
        throw new Error("One or more admin services are unavailable.");
      }

      const [statsData, logsData, ingestionData] = await Promise.all([
        statsRes.json(),
        logsRes.json(),
        ingestionRes.json(),
      ]);
      setStats(statsData);
      setLogs(logsData.logs || []);
      setIngestionLogs(ingestionData.logs || []);
      setError(null);
    } catch (err) {
      console.error("Failed to load admin metrics:", err);
      setError(err.message || "Failed to load admin data.");
    } finally {
      setLoading(false);
    }
  }, [adminKey]);

  useEffect(() => {
    if (!adminKey) {
      setLoading(false);
      return undefined;
    }
    fetchAdminData();
    const interval = setInterval(fetchAdminData, 10000);
    return () => clearInterval(interval);
  }, [adminKey, fetchAdminData]);

  const handleAdminKey = (event) => {
    event.preventDefault();
    const nextKey = keyDraft.trim();
    if (!nextKey) return;
    window.sessionStorage.setItem("dpdpa_admin_key", nextKey);
    setAdminKey(nextKey);
    setKeyDraft("");
  };

  const total = stats.core_layer_count + stats.opinion_layer_count + stats.other_layers_count || 1;
  const corePercent = Math.round((stats.core_layer_count / total) * 100);
  const opinionPercent = Math.round((stats.opinion_layer_count / total) * 100);
  const otherPercent = Math.round((stats.other_layers_count / total) * 100);

  // Filter alerts: either ungrounded search queries, or containing high-risk terms
  const searchAlerts = logs.filter(log => {
    if (log.grounded === false) return true;
    const q = String(log.query || "").toLowerCase();
    return q.includes("penalty") || q.includes("breach") || q.includes("fine") || q.includes("conflict") || q.includes("violation");
  });

  if (!adminKey) {
    return (
      <div className="space-y-6" style={{ maxWidth: "520px" }}>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Admin authorization</h1>
          <p className="text-slate-500 mt-1">Enter the server-issued admin key for this browser tab.</p>
        </div>
        <form onSubmit={handleAdminKey} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
          <label htmlFor="admin-key" className="block text-sm font-semibold text-slate-700">Admin key</label>
          <input
            id="admin-key"
            type="password"
            autoComplete="off"
            value={keyDraft}
            onChange={(event) => setKeyDraft(event.target.value)}
            className="input w-full"
            required
          />
          {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
          <button type="submit" className="btn-primary">Open admin dashboard</button>
        </form>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Admin Audit & Analytics</h1>
        <p className="text-slate-500 mt-1">Monitor real-time compliance search queries, ontology core contents, and expert opinions.</p>
      </div>

      {loading && <div role="status" className="text-sm text-slate-500">Loading live admin data…</div>}
      {error && (
        <div role="alert" className="bg-red-50 border border-red-200 text-red-800 rounded-xl p-4 flex justify-between items-center gap-4">
          <span>{error}</span>
          <button type="button" className="btn-secondary" onClick={fetchAdminData}>Retry</button>
        </div>
      )}

      {/* Layer Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-blue-600 uppercase tracking-wider">Primary Core</div>
          <div className="text-3xl font-bold text-slate-900 mt-2">{stats.core_layer_count}</div>
          <div className="text-xs text-slate-500 mt-1">Layer 1: Act, Rules & Penalties</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-purple-600 uppercase tracking-wider">Expert Opinions</div>
          <div className="text-3xl font-bold text-slate-900 mt-2">{stats.opinion_layer_count}</div>
          <div className="text-xs text-slate-500 mt-1">Layer 4: Law Advisories & Opinions</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Other Authorities</div>
          <div className="text-3xl font-bold text-slate-900 mt-2">{stats.other_layers_count}</div>
          <div className="text-xs text-slate-500 mt-1">Layers 2, 3, 5: Case Laws & Regulatory Alerts</div>
        </div>
      </div>

      {/* Layer Distribution Stacked Bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-slate-900 mb-4">Ontology Layer Distribution</h3>
        <div className="h-6 w-full rounded-full bg-slate-100 flex overflow-hidden">
          <div 
            style={{ width: `${corePercent}%` }} 
            className="bg-blue-500 hover:bg-blue-600 transition-all duration-300"
            title={`Core: ${stats.core_layer_count}`}
          />
          <div 
            style={{ width: `${opinionPercent}%` }} 
            className="bg-purple-500 hover:bg-purple-600 transition-all duration-300"
            title={`Opinions: ${stats.opinion_layer_count}`}
          />
          <div 
            style={{ width: `${otherPercent}%` }} 
            className="bg-emerald-500 hover:bg-emerald-600 transition-all duration-300"
            title={`Others: ${stats.other_layers_count}`}
          />
        </div>
        <div className="flex justify-between items-center text-xs text-slate-500 mt-3">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-blue-500 inline-block" />
            <span>Core Layer 1 ({corePercent}%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-purple-500 inline-block" />
            <span>Expert Opinions Layer 4 ({opinionPercent}%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-emerald-500 inline-block" />
            <span>Others ({otherPercent}%)</span>
          </div>
        </div>
      </div>

      {/* Double Column: Alerts on Left, General Log on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left Column: Search Alerts Panel */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="border-b border-slate-200 px-6 py-4 flex justify-between items-center bg-red-50/50">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <span className="text-red-500">⚠️</span> Search Warning & Grounding Alerts
            </h3>
            <span className="text-xs font-semibold text-red-700 bg-red-100 px-2.5 py-1 rounded-full">
              {searchAlerts.length} Active Alerts
            </span>
          </div>

          <div className="p-4 flex-1 overflow-y-auto max-h-[350px] space-y-3">
            {searchAlerts.length === 0 ? (
              <div className="py-12 text-center text-slate-400 text-sm">
                No active search warning alerts detected.
              </div>
            ) : (
              searchAlerts.map((alert, idx) => (
                <div key={idx} className="p-4 rounded-xl border border-red-100 bg-red-50/20 space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                      alert.grounded === false 
                        ? "bg-purple-100 text-purple-700" 
                        : "bg-red-100 text-red-700"
                    }`}>
                      {alert.grounded === false ? "UNGROUNDED SEARCH" : "HIGH-RISK KEYWORD"}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="font-semibold text-slate-800">"{alert.query}"</p>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {alert.grounded === false 
                      ? "User requested information not covered by active legal evidence coordinates. Potential knowledge gap."
                      : "Search terms contain reference to critical liabilities, breaches, or penalties requiring monitoring."
                    }
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Search Logger Audit Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="border-b border-slate-200 px-6 py-4 flex justify-between items-center bg-slate-50">
            <h3 className="font-semibold text-slate-900">Live Search Queries Audit Log</h3>
            <span className="text-xs font-medium text-slate-500 bg-slate-200 px-2.5 py-1 rounded-full">
              Queries Feed
            </span>
          </div>
          
          <div className="overflow-y-auto max-h-[350px] flex-1">
            {logs.length === 0 ? (
              <div className="py-12 text-center text-slate-400 text-sm">
                No queries logged yet.
              </div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase bg-slate-100/50 sticky top-0 z-10">
                    <th className="px-6 py-3 w-5/12">Time</th>
                    <th className="px-6 py-3 w-5/12">Search query</th>
                    <th className="px-6 py-3 w-2/12">Grounded</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
                  {logs.map((log, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/50">
                      <td className="px-6 py-3 font-mono text-[11px] text-slate-400">
                        {new Date(log.timestamp).toLocaleTimeString()} - {new Date(log.timestamp).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-3 font-medium text-slate-800 max-w-[200px] truncate">
                        "{log.query}"
                      </td>
                      <td className="px-6 py-3">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          log.grounded !== false ? "bg-emerald-100 text-emerald-700" : "bg-purple-100 text-purple-700"
                        }`}>
                          {log.grounded !== false ? "YES" : "NO"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

      </div>

      {/* Full Width Row: Ingestion Activity Feed */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="border-b border-slate-200 px-6 py-4 flex justify-between items-center bg-slate-50">
          <h3 className="font-semibold text-slate-900">Ingestion Factory Activity Feed</h3>
          <span className="text-xs font-medium text-slate-500 bg-slate-200 px-2.5 py-1 rounded-full">
            Pipeline History
          </span>
        </div>

        <div className="overflow-x-auto">
          {ingestionLogs.length === 0 ? (
            <div className="px-6 py-12 text-center text-slate-400 text-sm">
              No document ingestion runs recorded yet.
            </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase bg-slate-100/50">
                  <th className="px-6 py-3.5">Timestamp (UTC)</th>
                  <th className="px-6 py-3.5">Pipeline Transaction ID</th>
                  <th className="px-6 py-3.5 text-center">Draft KOs</th>
                  <th className="px-6 py-3.5 text-center">Published KOs</th>
                  <th className="px-6 py-3.5 text-center">Rejected KOs</th>
                  <th className="px-6 py-3.5">Duration</th>
                  <th className="px-6 py-3.5">Run Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
                {ingestionLogs.map((run, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-[11px] text-slate-400">
                      {new Date(run.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 font-medium text-slate-800">
                      <code>{run.pipeline_id}</code>
                    </td>
                    <td className="px-6 py-3.5 text-center font-semibold text-slate-900">
                      {run.ko_count}
                    </td>
                    <td className="px-6 py-3.5 text-center font-semibold text-blue-600">
                      {run.published_count}
                    </td>
                    <td className="px-6 py-3.5 text-center font-semibold text-red-600">
                      {run.rejected_count}
                    </td>
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-500">
                      {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(2)}s` : "N/A"}
                    </td>
                    <td className="px-6 py-3.5">
                      <span className={`inline-flex px-2 py-0.5 text-xs font-bold rounded-full uppercase ${
                        run.status === "SUCCESS" ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"
                      }`}>
                        {run.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

    </div>
  );
}
