import React, { useState, useEffect } from "react";

export default function AdminAudit() {
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

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      
      // Fetch stats
      const statsRes = await fetch("http://localhost:8000/admin/stats");
      const statsData = await statsRes.json();
      setStats(statsData);

      // Fetch search logs
      const logsRes = await fetch("http://localhost:8000/admin/search-audit");
      const logsData = await logsRes.json();
      setLogs(logsData.logs || []);

      // Fetch Ingestion logs
      const ingestionRes = await fetch("http://localhost:8000/admin/ingestion-audit");
      const ingestionData = await ingestionRes.json();
      setIngestionLogs(ingestionData.logs || []);

      setError(null);
    } catch (err) {
      console.error("Failed to load admin metrics:", err);
      // Fallback mock statistics for local offline sandbox testing
      setStats({
        total_knowledge_objects: 45,
        core_layer_count: 24,
        opinion_layer_count: 8,
        other_layers_count: 13
      });
      
      setLogs([
        { timestamp: new Date().toISOString(), query: "What is the penalty for a data breach?", grounded: true },
        { timestamp: new Date(Date.now() - 1800000).toISOString(), query: "Bilingual consent notice court splits", grounded: false },
        { timestamp: new Date(Date.now() - 3600000).toISOString(), query: "Section 10 Significant Data Fiduciary obligations", grounded: true },
        { timestamp: new Date(Date.now() - 7200000).toISOString(), query: "Quantum computing data encryption laws in India", grounded: false },
        { timestamp: new Date(Date.now() - 10800000).toISOString(), query: "Puttaswamy privacy judgment 2017 details", grounded: true }
      ]);

      setIngestionLogs([
        { timestamp: new Date().toISOString(), pipeline_id: "pipeline-20260728-024941", ko_count: 3, published_count: 2, rejected_count: 1, duration_ms: 1489.19, status: "SUCCESS" },
        { timestamp: new Date(Date.now() - 86400000).toISOString(), pipeline_id: "pipeline-20260727-142201", ko_count: 5, published_count: 5, rejected_count: 0, duration_ms: 2450.4, status: "SUCCESS" }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
    // Poll logs every 10 seconds for real-time tracking
    const interval = setInterval(fetchAdminData, 10000);
    return () => clearInterval(interval);
  }, []);

  const total = stats.core_layer_count + stats.opinion_layer_count + stats.other_layers_count || 1;
  const corePercent = Math.round((stats.core_layer_count / total) * 100);
  const opinionPercent = Math.round((stats.opinion_layer_count / total) * 100);
  const otherPercent = Math.round((stats.other_layers_count / total) * 100);

  // Filter alerts: either ungrounded search queries, or containing high-risk terms
  const searchAlerts = logs.filter(log => {
    if (log.grounded === false) return true;
    const q = log.query.toLowerCase();
    return q.includes("penalty") || q.includes("breach") || q.includes("fine") || q.includes("conflict") || q.includes("violation");
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Admin Audit & Analytics</h1>
        <p className="text-slate-500 mt-1">Monitor real-time compliance search queries, ontology core contents, and expert opinions.</p>
      </div>

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
