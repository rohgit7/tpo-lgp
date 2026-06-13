import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import client from "../api/client";
import Plotly from "plotly.js-dist-min";

export default function DashboardPage() {
  const { fileId } = useParams();
  const [summary, setSummary] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [messages, setMessages] = useState([]);
const [query, setQuery] = useState("");
const [chatLoading, setChatLoading] = useState(false);
  useEffect(() => {
  client.get(`/summary/${fileId}`)
    .then(res => {
      console.log("summary:", res.data);
      setSummary(res.data);
    })
    .catch(err => console.error("summary error:", err));

  client.get(`/visualize/${fileId}`)
  .then(res => {
    const parsed = typeof res.data === "string" ? JSON.parse(res.data) : res.data;
    console.log("parsed chart:", parsed);
    setChartData(parsed);
    client.get(`/anomalies/${fileId}`)
  .then(res => setAnomalies(res.data))
  .catch(err => console.error("anomalies error:", err));
  })
  .catch(err => console.error("visualize error:", err));
}, [fileId]);
useEffect(() => {
  if (chartData) {
    Plotly.newPlot("plotly-chart", chartData.data, chartData.layout, { responsive: true });
  }
}, [chartData]);
const handleChat = async () => {
  if (!query.trim()) return;

  const userMessage = { role: "user", text: query };
  setMessages(prev => [...prev, userMessage]);
  setQuery("");
  setChatLoading(true);

  try {
    const res = await client.post(`/chat/${fileId}`, { query });
    const botMessage = { role: "bot", text: res.data.answer };
    setMessages(prev => [...prev, botMessage]);
  } catch (err) {
  console.error("chat error:", err);
  setMessages(prev => [...prev, { role: "bot", text: "Something went wrong." }]);

  } finally {
    setChatLoading(false);
  }
};

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-2xl font-bold mb-6">Shakun AI Dashboard</h1>
      {summary ? (
  <div className="grid grid-cols-3 gap-4 mb-8">
    <div className="bg-white p-6 rounded-xl shadow">
      <p className="text-gray-500 text-sm">Total Rows</p>
      <p className="text-3xl font-bold">{summary.rows}</p>
    </div>
    <div className="bg-white p-6 rounded-xl shadow">
      <p className="text-gray-500 text-sm">Total Amount</p>
      <p className="text-3xl font-bold">{summary.total_amount?.toFixed(2)}</p>
    </div>
    <div className="bg-white p-6 rounded-xl shadow">
      <p className="text-gray-500 text-sm">Anomalies Detected</p>
      <p className="text-3xl font-bold text-red-500">{summary.anomaly_count}</p>
    </div>
  </div>
) : (
  <p className="text-gray-400">Loading summary...</p>
)}
{chartData ? (
  <div className="bg-white p-6 rounded-xl shadow mb-8">
    <h2 className="text-lg font-semibold mb-4">Money Flow</h2>
   <div id="plotly-chart" style={{ width: "100%", height: "400px" }}></div>
  </div>
) : (
  <p className="text-gray-400">Loading chart...</p>
)
}<div className="bg-white p-6 rounded-xl shadow mb-8">
  <h2 className="text-lg font-semibold mb-4">Anomalies Detected</h2>
  {anomalies ? (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
          <tr>
            {anomalies.anomalies.length > 0 &&
              Object.keys(anomalies.anomalies[0]).map(col => (
                <th key={col} className="px-4 py-3">{col}</th>
              ))
            }
          </tr>
        </thead>
        <tbody>
          {anomalies.anomalies.map((row, i) => (
            <tr key={i} className="border-t hover:bg-red-50">
              {Object.values(row).map((val, j) => (
                <td key={j} className="px-4 py-3">{String(val)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {anomalies.count === 0 && (
        <p className="text-gray-400 text-center py-4">No anomalies found!</p>
      )}
    </div>
  ) : (
    <p className="text-gray-400">Loading anomalies...</p>
  )}
</div>
<div className="bg-white p-6 rounded-xl shadow mb-8">
  <h2 className="text-lg font-semibold mb-4">Chat with your Data</h2>
  
  <div className="h-64 overflow-y-auto border rounded-lg p-4 mb-4 flex flex-col gap-3">
    {messages.length === 0 && (
      <p className="text-gray-400 text-sm text-center">Ask anything about your data...</p>
    )}
    {messages.map((msg, i) => (
      <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
        <div className={`px-4 py-2 rounded-xl max-w-xs text-sm ${msg.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"}`}>
          {msg.text}
        </div>
      </div>
    ))}
    {chatLoading && (
      <div className="flex justify-start">
        <div className="px-4 py-2 rounded-xl bg-gray-100 text-gray-500 text-sm">Thinking...</div>
      </div>
    )}
  </div>

  <div className="flex gap-2">
    <input
      type="text"
      value={query}
      onChange={e => setQuery(e.target.value)}
      onKeyDown={e => e.key === "Enter" && handleChat()}
      placeholder="Ask a question..."
      className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
    <button
      onClick={handleChat}
      disabled={chatLoading}
      className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
    >
      Send
    </button>
  </div>
</div>
    </div>
    
  );
}