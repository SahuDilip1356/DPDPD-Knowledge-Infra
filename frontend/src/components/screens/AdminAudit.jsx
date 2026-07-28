import React, { useState, useEffect } from "react";

export default function AdminAudit() {
  const [logs, setLogs] = useState([]);
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

      setError(null);
    } catch (err) {
      console.error("Failed to load admin metrics:", err);
      // Fallback mock statistics for local offline sandbox testing
      setStats({
        total_knowledge_objects: 5,
        core_layer_count: 3,
        opinion_layer_count: 1,
        other_layers_count: 1
      });
      setLogs([
        { timestamp: new Date().toISOString(), query: "What is the penalty for a data breach?" },
        { timestamp: new Date(Date.now() - 3600000).toISOString(), query: "Section 10 Significant Data Fiduciary" },
        { timestamp: new Date(Date.now() - 7200000).toISOString(), query: "Puttaswamy privacy judgment 2017" }
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

      {/* Search Logger Audit Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="border-b border-slate-200 px-6 py-4 flex justify-between items-center bg-slate-50">
          <h3 className="font-semibold text-slate-900">Live Search Queries Audit Log</h3>
          <span className="text-xs font-medium text-slate-500 bg-slate-200 px-2.5 py-1 rounded-full">
            Real-time Monitoring
          </span>
        </div>
        
        {logs.length === 0 ? (
          <div className="px-6 py-12 text-center text-slate-500">
            No queries logged yet. Search strings will appear here in real-time as users query the chatbot.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase bg-slate-100/50">
                  <th className="px-6 py-3 w-1/3">Time (UTC)</th>
                  <th className="px-6 py-3 w-2/3">Search query</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
                {logs.map((log, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50">
                    <td className="px-6 py-3 font-mono text-xs text-slate-400">
                      {new Date(log.timestamp).toLocaleTimeString()} - {new Date(log.timestamp).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-3 font-medium text-slate-800">
                      "{log.query}"
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
