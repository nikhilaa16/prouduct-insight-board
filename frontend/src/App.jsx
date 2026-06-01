import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie
} from 'recharts';
import { 
  MessageSquare, AlertTriangle, Lightbulb, Star, Filter, 
  Send, RefreshCw, Layers, CheckCircle2, Database, Search
} from 'lucide-react';

export default function App() {
  const [feedback, setFeedback] = useState([]);
  const [stats, setStats] = useState({
    total_count: 0,
    bug_count: 0,
    feature_count: 0,
    praise_count: 0,
    average_urgency: 0.0,
    category_distribution: {},
    type_distribution: {}
  });

  // Form states
  const [rawText, setRawText] = useState('');
  const [source, setSource] = useState('App Store');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(null);

  // Filters
  const [filterCategory, setFilterCategory] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Roadmap states
  const [roadmap, setRoadmap] = useState('');
  const [roadmapLoading, setRoadmapLoading] = useState(false);

  // Chat states
  const [chatQuery, setChatQuery] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    {
      role: 'assistant',
      text: "Hello! I am your AI Co-Pilot. Ask me anything about your customer support logs (e.g. 'Are there any checkout bugs?' or 'What are the main performance issues?')."
    }
  ]);

  // Load Data
  const fetchData = async () => {
    try {
      let url = '/api/feedback/list';
      const params = [];
      if (filterCategory) params.push(`category=${filterCategory}`);
      if (filterType) params.push(`feedback_type=${filterType}`);
      if (filterStatus) params.push(`status=${filterStatus}`);
      if (params.length > 0) url += `?${params.join('&')}`;

      const [listRes, statsRes] = await Promise.all([
        axios.get(url),
        axios.get('/api/feedback/stats')
      ]);
      setFeedback(listRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error("Error fetching data:", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filterCategory, filterType, filterStatus]);

  // Submit Feedback
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!rawText.trim()) return;
    setLoading(true);
    try {
      await axios.post('/api/feedback/submit', {
        raw_text: rawText,
        source: source,
        customer_email: email || null
      });
      setRawText('');
      setEmail('');
      await fetchData();
    } catch (err) {
      alert("Error submitting feedback: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Update Status
  const handleStatusChange = async (itemId, newStatus) => {
    setStatusLoading(itemId);
    try {
      await axios.post(`/api/feedback/${itemId}/status`, { status: newStatus });
      await fetchData();
    } catch (err) {
      console.error("Error updating status:", err);
    } finally {
      setStatusLoading(null);
    }
  };

  // Prepopulate Demo Batch
  const handleLoadSampleData = async () => {
    setLoading(true);
    const samples = [
      { raw_text: "Can you please add a Dark Mode option? My eyes hurt when coding at night.", source: "Play Store", email: "developer12@gmail.com" },
      { raw_text: "The checkout keeps failing when using Apple Pay. The payment screen just hangs forever.", source: "iOS App", email: "sarah.connor@hotmail.com" },
      { raw_text: "Amazing application! It saved me hours of work today. Kudos to the dev team.", source: "App Store", email: "john_doe@gmail.com" },
      { raw_text: "The login authentication token expires too quickly. I have to log back in every 5 minutes.", source: "Web Portal", email: "security_analyst@company.com" },
      { raw_text: "The main grid dashboard rendering is extremely slow on mobile Safari browsers.", source: "App Store", email: "safari_tester@gmail.com" }
    ];

    try {
      for (const sample of samples) {
        await axios.post('/api/feedback/submit', sample);
      }
      await fetchData();
    } catch (err) {
      console.error("Error loading sample data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Generate Roadmap
  const handleGenerateRoadmap = async () => {
    setRoadmapLoading(true);
    try {
      const res = await axios.post('/api/roadmap/generate');
      setRoadmap(res.data.roadmap);
    } catch (err) {
      console.error("Error generating roadmap:", err);
    } finally {
      setRoadmapLoading(false);
    }
  };

  // Handle Chat Submit
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatQuery.trim() || chatLoading) return;
    
    const userMessage = { role: 'user', text: chatQuery };
    setChatHistory(prev => [...prev, userMessage]);
    setChatQuery('');
    setChatLoading(true);

    try {
      const res = await axios.post('/api/chat', { query: userMessage.text });
      const assistantMessage = {
        role: 'assistant',
        text: res.data.answer,
        sources: res.data.sources
      };
      setChatHistory(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Error communicating with chat API:", err);
      setChatHistory(prev => [
        ...prev,
        { role: 'assistant', text: "Error: Failed to connect to the AI search engine." }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  // Theme Constants (Zinc / Electric Blue & Sky Glow Premium Palette)
  const THEME = {
    bg: 'bg-[#09090B]',
    card: 'bg-[#18181B]',
    border: 'border-[#27272A]',
    accentPrimary: '#2563EB',   // Electric Blue Accent
    accentSecondary: '#38BDF8', // Sky Glow Accent
    success: '#22C55E',         // Success Green
    warning: '#F59E0B',         // Warning Orange
    critical: '#EF4444',        // Critical Red
    textSecondary: 'text-[#94a3b8]' // Muted Slate
  };

  const COLORS = {
    Bug: THEME.critical,
    'Feature Request': THEME.warning,
    Praise: THEME.success,
    Login: '#a855f7',
    Payment: THEME.accentPrimary,
    'UI/UX': THEME.accentSecondary,
    Performance: '#6366f1',
    Others: '#64748b'
  };

  // Chart data mapping
  const categoryData = Object.entries(stats.category_distribution).map(([name, value]) => ({
    name, value, color: COLORS[name] || COLORS.Others
  }));

  const typeData = Object.entries(stats.type_distribution).map(([name, value]) => ({
    name, value, color: COLORS[name] || COLORS.Others
  }));

  // Local text search filter
  const filteredFeedback = feedback.filter(item => {
    const textMatches = item.raw_text.toLowerCase().includes(searchQuery.toLowerCase()) || 
                        (item.ai_summary && item.ai_summary.toLowerCase().includes(searchQuery.toLowerCase()));
    return textMatches;
  });

  return (
    <div className="min-h-screen bg-[#09090B] text-slate-100 flex flex-col font-sans">
      
      {/* Header bar */}
      <header className="border-b border-[#27272A] bg-[#18181B]/60 backdrop-blur-md px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4 sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-[#2563EB] to-[#38BDF8] p-2.5 rounded-xl shadow-lg shadow-[#2563EB]/20">
            <Layers className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-slate-50 to-slate-200 bg-clip-text text-transparent">
              FeedLoop AI
            </h1>
            <p className="text-xs text-[#94a3b8] font-medium">Customer Experience & Support Analytics Engine</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/20 text-[#22C55E] text-xs font-semibold">
            <Database className="h-3.5 w-3.5" />
            <span>Connected: PostgreSQL (feedloop_db)</span>
          </div>
          <button 
            onClick={fetchData} 
            className="p-2 text-slate-400 hover:text-[#38BDF8] hover:bg-[#27272A]/50 rounded-lg border border-[#27272A] transition-all duration-200"
            title="Refresh Data"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </header>

      {/* Main 2-Column Layout */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Form & Metrics (1/3 Width) */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          
          {/* Submission Card */}
          <section className="bg-[#18181B]/80 backdrop-blur-sm border border-[#27272A] rounded-2xl p-6 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-[#2563EB]/5 rounded-full blur-3xl pointer-events-none"></div>
            
            <h2 className="text-md font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-[#38BDF8]" />
              Ingest Support Ticket
            </h2>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div>
                <label className="block text-xs font-medium text-[#94a3b8] mb-1">Raw Customer Log / Email Message</label>
                <textarea
                  required
                  rows={3}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Paste raw support request or review..."
                  className="w-full text-sm bg-[#09090B]/70 border border-[#27272A] rounded-xl px-3 py-2 text-slate-200 placeholder-slate-650 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition-all duration-200 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-[#94a3b8] mb-1">Ticket Source</label>
                  <select
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    className="w-full text-xs bg-[#09090B]/70 border border-[#27272A] rounded-lg px-2 py-2 text-slate-300 focus:outline-none focus:border-[#2563EB] transition-all duration-200"
                  >
                    <option value="App Store">App Store</option>
                    <option value="Play Store">Play Store</option>
                    <option value="Web Portal">Web Portal</option>
                    <option value="iOS App">iOS App</option>
                    <option value="Email Support">Email Support</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-[#94a3b8] mb-1">Customer Email (Optional)</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@example.com"
                    className="w-full text-xs bg-[#09090B]/70 border border-[#27272A] rounded-lg px-2.5 py-2 text-slate-200 placeholder-slate-700 focus:outline-none focus:border-[#2563EB] transition-all duration-200"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#38BDF8] hover:brightness-110 text-white font-bold text-sm transition-all duration-200 shadow-md active:scale-98 disabled:opacity-50"
              >
                {loading ? <RefreshCw className="h-4 w-4 animate-spin text-white" /> : <Send className="h-4 w-4 text-white" />}
                Analyze with FeedLoop AI
              </button>
            </form>

            <div className="relative flex py-2 items-center">
              <div className="flex-grow border-t border-[#27272A]"></div>
              <span className="flex-shrink mx-4 text-slate-600 text-[10px] uppercase font-bold tracking-wider">OR</span>
              <div className="flex-grow border-t border-[#27272A]"></div>
            </div>

            <button
              onClick={handleLoadSampleData}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-xl bg-[#27272A]/30 hover:bg-[#27272A]/85 border border-[#27272A] text-[#38BDF8] font-medium text-xs transition-all duration-200 active:scale-98"
            >
              <Database className="h-3.5 w-3.5 text-[#38BDF8]" />
              Load Simulated Feedback Batch
            </button>
          </section>

          {/* Quick Metrics */}
          <section className="grid grid-cols-2 gap-4">
            <div className="bg-[#18181B]/80 border border-[#27272A] rounded-2xl p-4 flex flex-col justify-between shadow-lg">
              <span className="text-xs text-[#94a3b8] font-semibold">Total Audited</span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-3xl font-bold text-white">{stats.total_count}</span>
                <span className="text-xs text-slate-500 font-medium">tickets</span>
              </div>
            </div>

            <div className="bg-[#18181B]/80 border border-[#27272A] rounded-2xl p-4 flex flex-col justify-between shadow-lg">
              <span className="text-xs text-[#EF4444] font-semibold flex items-center gap-1.5">
                <AlertTriangle className="h-3.5 w-3.5 animate-pulse" />
                Active Defects
              </span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-3xl font-bold text-[#EF4444]">{stats.bug_count}</span>
                <span className="text-xs text-slate-500 font-medium">unresolved</span>
              </div>
            </div>

            <div className="bg-[#18181B]/80 border border-[#27272A] rounded-2xl p-4 flex flex-col justify-between shadow-lg">
              <span className="text-xs text-[#F59E0B] font-semibold flex items-center gap-1.5">
                <Lightbulb className="h-3.5 w-3.5" />
                Feature Ideas
              </span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-3xl font-bold text-[#F59E0B]">{stats.feature_count}</span>
                <span className="text-xs text-slate-500 font-medium">requests</span>
              </div>
            </div>

            <div className="bg-[#18181B]/80 border border-[#27272A] rounded-2xl p-4 flex flex-col justify-between shadow-lg">
              <span className="text-xs text-[#38BDF8] font-semibold flex items-center gap-1.5">
                <Star className="h-3.5 w-3.5 text-[#38BDF8]" />
                Avg Urgency
              </span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-3xl font-bold text-[#38BDF8]">{stats.average_urgency}</span>
                <span className="text-xs text-slate-500 font-medium">/ 5.0</span>
              </div>
            </div>
          </section>

        </div>

        {/* Right Column: Charts & Live Logs (2/3 Width) */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          
          {/* Charts section */}
          {stats.total_count > 0 && (
            <section className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-[#18181B]/40 border border-[#27272A] rounded-2xl p-6 shadow-lg">
              
              {/* Category distribution */}
              <div>
                <h3 className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-4">Category Load</h3>
                <div className="h-44 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={categoryData} margin={{ left: -20, bottom: -5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                      <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} />
                      <YAxis stroke="#94a3b8" fontSize={10} allowDecimals={false} tickLine={false} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#18181B', borderColor: '#27272A', borderRadius: '8px' }}
                        labelClassName="text-slate-400 text-xs font-semibold"
                        itemStyle={{ fontSize: '11px', color: '#f8fafc' }}
                      />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {categoryData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Type breakdown */}
              <div>
                <h3 className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-4">Issue Mix</h3>
                <div className="h-44 w-full flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={typeData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={70}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {typeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#18181B', borderColor: '#27272A', borderRadius: '8px' }}
                        itemStyle={{ fontSize: '11px', color: '#f8fafc' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  {/* Legend */}
                  <div className="flex flex-col gap-2.5 text-xs text-slate-300 pr-6">
                    {typeData.map((entry) => (
                      <div key={entry.name} className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }}></span>
                        <span className="font-medium text-[#94a3b8]">{entry.name}:</span>
                        <span className="font-bold text-slate-200">{entry.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

            </section>
          )}

          {/* Conversational AI Chat Panel */}
          <section className="bg-[#18181B]/80 backdrop-blur-sm border border-[#27272A] rounded-2xl p-6 shadow-xl flex flex-col gap-4 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-[#38BDF8]/5 rounded-full blur-3xl pointer-events-none"></div>
            
            <div className="flex justify-between items-center border-b border-[#27272A] pb-3">
              <h2 className="text-md font-semibold text-slate-200 flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-[#38BDF8]" />
                Conversational RAG Chat Co-Pilot
              </h2>
              <span className="text-[10px] bg-[#38BDF8]/10 text-[#38BDF8] border border-[#38BDF8]/20 px-2 py-0.5 rounded-full font-bold">
                Local Semantic Index
              </span>
            </div>

            {/* Chat Output Window */}
            <div className="flex flex-col gap-3 h-48 overflow-y-auto pr-1 text-xs">
              {chatHistory.map((msg, index) => (
                <div key={index} className={`flex flex-col gap-1.5 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`px-3 py-2 rounded-2xl max-w-[85%] leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-gradient-to-tr from-[#2563EB] to-[#38BDF8] text-white rounded-tr-none font-medium' 
                      : 'bg-[#09090B]/60 border border-[#27272A] text-slate-200 rounded-tl-none'
                  }`}>
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                    
                    {/* Render matching sources if present */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-[#27272A] flex flex-col gap-1">
                        <span className="text-[10px] text-[#38BDF8] font-bold uppercase tracking-wider">Semantic Sources:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {msg.sources.map((src, srcIdx) => (
                            <span 
                              key={srcIdx} 
                              className="text-[9px] bg-[#27272A]/50 border border-[#27272A] text-slate-400 px-1.5 py-0.5 rounded font-mono"
                              title={src.document.text}
                            >
                              #{src.document.id} ({Math.round(src.score * 100)}%)
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex items-start">
                  <div className="px-3 py-2 rounded-2xl rounded-tl-none bg-[#09090B]/60 border border-[#27272A] text-slate-400 flex items-center gap-2">
                    <RefreshCw className="h-3 w-3 animate-spin text-[#38BDF8]" />
                    <span>Searching vector database...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input Bar */}
            <form onSubmit={handleChatSubmit} className="flex gap-2">
              <input
                type="text"
                required
                value={chatQuery}
                onChange={(e) => setChatQuery(e.target.value)}
                placeholder="Ask AI Co-Pilot: 'Are there reports of payment errors?'"
                className="flex-1 text-xs bg-[#09090B]/70 border border-[#27272A] rounded-xl px-3 py-2 text-slate-200 placeholder-slate-650 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition-all duration-200"
              />
              <button
                type="submit"
                disabled={chatLoading}
                className="bg-gradient-to-r from-[#2563EB] to-[#38BDF8] hover:brightness-110 p-2.5 rounded-xl text-white transition-all duration-200 active:scale-95 disabled:opacity-50 flex items-center justify-center"
              >
                <Send className="h-4 w-4 text-white" />
              </button>
            </form>
          </section>

          {/* Ticket Queue */}
          <section className="bg-[#18181B]/80 backdrop-blur-sm border border-[#27272A] rounded-2xl p-6 shadow-xl flex-1 flex flex-col">
            
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
              <h2 className="text-md font-semibold text-slate-200 flex items-center gap-2">
                <Filter className="h-4 w-4 text-[#2563EB]" />
                Live Ticket Queue
              </h2>

              {/* Filtering Controls */}
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative text-xs">
                  <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-600" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search logs..."
                    className="bg-[#09090B]/70 border border-[#27272A] rounded-lg pl-8 pr-2.5 py-1.5 text-slate-300 placeholder-slate-700 focus:outline-none focus:border-[#2563EB]"
                  />
                </div>

                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="text-xs bg-[#09090B]/70 border border-[#27272A] rounded-lg px-2.5 py-1.5 text-slate-400 focus:outline-none focus:border-[#2563EB]"
                >
                  <option value="">All Categories</option>
                  <option value="Login">Login</option>
                  <option value="Payment">Payment</option>
                  <option value="UI/UX">UI/UX</option>
                  <option value="Performance">Performance</option>
                  <option value="Others">Others</option>
                </select>

                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="text-xs bg-[#09090B]/70 border border-[#27272A] rounded-lg px-2.5 py-1.5 text-slate-400 focus:outline-none focus:border-[#2563EB]"
                >
                  <option value="">All Types</option>
                  <option value="Bug">Bugs</option>
                  <option value="Feature Request">Features</option>
                  <option value="Praise">Praise</option>
                </select>
              </div>
            </div>

            {/* Ticket Table */}
            <div className="overflow-x-auto flex-1 rounded-xl border border-[#27272A] bg-[#09090B]/40">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-[#27272A] bg-[#18181B]/50 text-slate-400 font-semibold uppercase tracking-wider">
                    <th className="py-3 px-4">Urgency</th>
                    <th className="py-3 px-4">AI Summary</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4">Type</th>
                    <th className="py-3 px-4">Source</th>
                    <th className="py-3 px-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#27272A]/60">
                  {filteredFeedback.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-[#94a3b8] font-medium">
                        No support tickets in queue. Try importing samples!
                      </td>
                    </tr>
                  ) : (
                    filteredFeedback.map((item) => (
                      <tr key={item.id} className="hover:bg-[#27272A]/20 group transition-colors duration-150">
                        {/* Urgency Badge */}
                        <td className="py-3 px-4 font-bold">
                          <span className={`px-2 py-0.5 rounded-full flex items-center justify-center w-7 h-5 ${
                            item.urgency_score >= 4 ? 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20' :
                            item.urgency_score === 3 ? 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/20' :
                            'bg-[#27272A]/30 text-slate-400 border border-[#27272A]'
                          }`}>
                            {item.urgency_score}
                          </span>
                        </td>
                        
                        {/* Summary & description */}
                        <td className="py-3 px-4 max-w-xs md:max-w-sm">
                          <div className="font-medium text-slate-200 group-hover:text-white truncate" title={item.raw_text}>
                            {item.ai_summary || "No summary"}
                          </div>
                          <div className="text-[10px] text-[#94a3b8] truncate max-w-[240px]">
                            {item.raw_text}
                          </div>
                        </td>

                        {/* Category */}
                        <td className="py-3 px-4">
                          <span 
                            className="px-2 py-0.5 rounded font-semibold text-[10px]" 
                            style={{ 
                                backgroundColor: `${COLORS[item.category] || COLORS.Others}10`, 
                                color: COLORS[item.category] || COLORS.Others,
                                border: `1px solid ${COLORS[item.category] || COLORS.Others}20`
                            }}
                          >
                            {item.category}
                          </span>
                        </td>

                        {/* Type */}
                        <td className="py-3 px-4">
                          <span 
                            className="px-2 py-0.5 rounded font-semibold text-[10px]"
                            style={{ 
                                backgroundColor: `${COLORS[item.feedback_type] || COLORS.Others}10`, 
                                color: COLORS[item.feedback_type] || COLORS.Others,
                                border: `1px solid ${COLORS[item.feedback_type] || COLORS.Others}20`
                            }}
                          >
                            {item.feedback_type}
                          </span>
                        </td>

                        {/* Source */}
                        <td className="py-3 px-4 text-[#94a3b8]">
                          {item.source}
                        </td>

                        {/* Status Select */}
                        <td className="py-3 px-4">
                          {statusLoading === item.id ? (
                            <RefreshCw className="h-3.5 w-3.5 animate-spin text-[#2563EB]" />
                          ) : (
                            <select
                              value={item.status}
                              onChange={(e) => handleStatusChange(item.id, e.target.value)}
                              className={`bg-[#09090B] border text-[10px] font-semibold rounded px-1.5 py-0.5 focus:outline-none transition-colors duration-200 ${
                                item.status === 'Resolved' ? 'border-[#22C55E]/40 text-[#22C55E] bg-[#22C55E]/5' :
                                item.status === 'In-Progress' ? 'border-[#2563EB]/40 text-[#2563EB] bg-[#2563EB]/5' :
                                item.status === 'Reviewed' ? 'border-[#27272A] text-slate-300 bg-[#18181B]' :
                                'border-[#EF4444]/40 text-[#EF4444] bg-[#EF4444]/5'
                              }`}
                            >
                              <option value="New">New</option>
                              <option value="Reviewed">Reviewed</option>
                              <option value="In-Progress">In-Progress</option>
                              <option value="Resolved">Resolved</option>
                            </select>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

          </section>

        </div>

      </main>

      {/* AI Sprint Roadmap Planner Section */}
      {stats.total_count > 0 && (
        <section className="max-w-7xl mx-auto w-full px-6 pb-12">
          <div className="bg-gradient-to-b from-[#18181B] to-[#09090B] border border-[#27272A] rounded-2xl p-6 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#2563EB]/5 rounded-full blur-3xl pointer-events-none"></div>

            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <div>
                <h2 className="text-base font-bold text-slate-200 flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-[#38BDF8] animate-pulse" />
                  FeedLoop AI Co-Pilot
                </h2>
                <p className="text-xs text-[#94a3b8] mt-1">Compile prioritized engineering roadmaps directly from unresolved customer defects.</p>
              </div>

              <button
                onClick={handleGenerateRoadmap}
                disabled={roadmapLoading}
                className="flex items-center gap-2 py-2 px-5 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#38BDF8] hover:brightness-110 text-white font-bold text-xs transition-all duration-200 active:scale-98 disabled:opacity-50"
              >
                {roadmapLoading ? <RefreshCw className="h-4 w-4 animate-spin text-white" /> : <Layers className="h-4 w-4 text-white" />}
                Generate AI Sprint Roadmap
              </button>
            </div>

            {/* Generated Roadmap Display */}
            {roadmap && (
              <div className="bg-[#09090B]/80 border border-[#27272A] rounded-xl p-5 overflow-y-auto text-xs text-slate-350 leading-relaxed font-mono whitespace-pre-wrap">
                {roadmap}
              </div>
            )}

          </div>
        </section>
      )}

      {/* Footer bar */}
      <footer className="border-t border-[#27272A] bg-slate-950/20 px-6 py-4 text-center text-[10px] text-slate-650 font-semibold tracking-wide">
        &copy; 2026 FEEDLOOP CX ENGINE &bull; POWERED BY FASTAPI & REACT &bull; ENFORCING SCHEMA VALIDATION
      </footer>

    </div>
  );
}
