import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import { 
  Orbit, ArrowUpRight, Play, ChevronDown, 
  Layers, Zap, Cpu, Shield, Wifi, Users,
  MessageSquare, Layout, Sparkles, Send,
  Paperclip, X
} from 'lucide-react';
import { marked } from 'marked';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// --- ANIMATION CONSTANTS ---
const EASE = [0.16, 1, 0.3, 1];

const useActiveSection = (sectionIds) => {
  const [activeSection, setActiveSection] = useState("");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { threshold: 0.2, rootMargin: "-20% 0px -20% 0px" }
    );

    sectionIds.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [sectionIds]);

  return activeSection;
};

// --- COMPONENTS ---

const BlurText = ({ text, delay = 0, className = "" }) => {
  const words = text.split(" ");
  return (
    <motion.div 
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className={cn("flex flex-wrap gap-x-[0.3em]", className)}
    >
      {words.map((word, i) => (
        <motion.span
          key={i}
          variants={{
            hidden: { filter: 'blur(12px)', opacity: 0, y: 40 },
            visible: { 
              filter: 'blur(0px)', 
              opacity: 1, 
              y: 0,
              transition: { duration: 0.8, ease: EASE, delay: delay + (i * 0.08) }
            }
          }}
          className="inline-block"
        >
          {word}
        </motion.span>
      ))}
    </motion.div>
  );
};

const Section = ({ children, className = "", id }) => (
  <motion.section
    id={id}
    initial={{ opacity: 0, filter: 'blur(10px)' }}
    whileInView={{ opacity: 1, filter: 'blur(0px)' }}
    viewport={{ once: true, margin: "-100px" }}
    transition={{ duration: 1, ease: EASE }}
    className={cn("relative z-10", className)}
  >
    {children}
  </motion.section>
);

const Navbar = ({ activeSection }) => (
  <nav className="fixed top-6 left-0 right-0 z-50 px-6 lg:px-12 flex justify-between items-center pointer-events-none">
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="p-3 liquid-glass rounded-full pointer-events-auto cursor-pointer flex items-center gap-3"
      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
    >
      <Orbit className="w-6 h-6 text-indigo-400 animate-pulse-slow" />
      <span className="font-heading italic text-xl pr-2 text-white">Assistant AI .</span>
    </motion.div>

    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="hidden md:flex items-center gap-1 p-2 liquid-glass rounded-full pointer-events-auto bg-white/5 relative"
    >
      {['Control Deck', 'Domains', 'Intro', 'Orchestration', 'Agent Roster', 'Performance'].map((item) => {
        const id = item.toLowerCase().replace(' ', '-');
        const isActive = activeSection === id;
        return (
          <a 
            key={item} 
            href={`#${id}`} 
            className={cn(
              "px-5 py-2 text-[10px] font-bold transition-colors uppercase tracking-[0.2em] rounded-full relative z-10",
              isActive ? "text-white" : "text-white/40 hover:text-white/70"
            )}
          >
            {item}
            {isActive && (
              <motion.div 
                layoutId="nav-pill"
                className="absolute inset-0 bg-indigo-500/20 ring-1 ring-indigo-500/40 rounded-full -z-10"
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
              />
            )}
          </a>
        );
      })}
    </motion.div>
  </nav>
);

const Hero = () => {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "30%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 1], [1, 1.1]);

  useEffect(() => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'video';
    link.href = "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260306_115329_5e00c9c5-4d69-49b7-94c3-9c31c60bb644.mp4";
    document.head.appendChild(link);
  }, []);

  return (
    <header id="intro" ref={containerRef} className="relative h-screen flex items-center justify-center overflow-hidden">
      <motion.div style={{ y, scale }} className="absolute inset-0 z-0">
        <video 
          autoPlay loop muted playsInline
          className="w-full h-full object-cover opacity-80"
        >
          <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260306_115329_5e00c9c5-4d69-49b7-94c3-9c31c60bb644.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#02040A]/20 to-[#02040A]" />
      </motion.div>

      <motion.div style={{ opacity }} className="relative z-10 text-center px-6 max-w-5xl">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, ease: EASE }}
          className="inline-flex items-center gap-2 px-4 py-1 liquid-glass rounded-full mb-8"
        >
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span className="text-xs uppercase tracking-[0.3em] font-medium text-white/80">V2.0 Orchestrator Core</span>
        </motion.div>

        <BlurText 
          text="Venture Past the Sky of Intelligence" 
          className="font-heading text-7xl md:text-9xl mb-8 leading-[0.9] italic text-balance"
        />

        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: EASE, delay: 0.8 }}
          className="font-body text-xl md:text-2xl text-white/60 mb-12 max-w-2xl mx-auto leading-relaxed"
        >
          Assistant AI is the first multi-agent orchestration bridge designed for total task autonomy and professional evolution.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: EASE, delay: 1 }}
          className="flex flex-col md:flex-row items-center justify-center gap-6"
        >
        </motion.div>
      </motion.div>
    </header>
  );
};

const MissionBlock = () => (
  <Section id="orchestration" className="py-40 px-6 flex flex-col items-center text-center">
    <motion.div 
      initial={{ height: 0 }}
      whileInView={{ height: 100 }}
      viewport={{ once: true }}
      className="w-[1.2px] bg-gradient-to-b from-transparent via-indigo-500 to-transparent mb-12"
    />
    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 blur-[150px] rounded-full -z-10" />
    <BlurText 
      text="We are not just building tools. We are engineering the next great chapter of human productivity." 
      className="max-w-4xl font-heading text-4xl md:text-6xl italic leading-tight text-white/90"
      delay={0.2}
    />
  </Section>
);

const AgentRoster = () => (
  <Section id="agent-roster" className="py-32 px-6 lg:px-12 grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-[1600px] mx-auto">
    <div className="relative group">
      <div className="h-[750px] liquid-glass rounded-[3rem] overflow-hidden">
        <img 
          src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1600&auto=format&fit=crop" 
          className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110 opacity-60"
          alt="Orchestrator Core"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#02040A] via-transparent to-transparent" />
        <div className="absolute bottom-16 left-16">
          <div className="flex items-center gap-3 mb-3">
            <p className="text-xs uppercase tracking-[0.4em] text-indigo-400 font-bold">Core Infrastructure</p>
            <span className="bg-indigo-500/20 text-indigo-400 px-3 py-1 rounded-full text-[10px] font-bold border border-indigo-500/30 uppercase tracking-widest">Powered by Gemini 1.5 Pro</span>
          </div>
          <h3 className="font-heading text-6xl italic mb-4">Orchestrator-1</h3>
          <p className="font-body text-white/60 text-lg max-w-sm">The apex intelligence layer coordinating specialized agents with zero-latency synchronization.</p>
        </div>
      </div>
    </div>

    <div className="flex flex-col justify-center">
      <h2 className="font-heading text-5xl mb-12">Universal Engineering</h2>
      <div className="grid grid-cols-2 gap-6">
        {[
          { label: 'Latency', value: '42ms', icon: Zap },
          { label: 'Integrity', value: '99.9%', icon: Shield },
          { label: 'Intelligence', value: '1.5 Pro', icon: Cpu },
          { label: 'Tool Access', value: '450+', icon: Layers },
          { label: 'Uptime', value: '100%', icon: Wifi },
          { label: 'Success', value: '94%', icon: Users },
        ].map((stat, i) => (
          <motion.div 
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="liquid-glass p-8 rounded-3xl"
          >
            <stat.icon className="w-6 h-6 text-indigo-400 mb-6" />
            <p className="text-3xl font-heading italic mb-1">{stat.value}</p>
            <p className="text-xs uppercase tracking-widest text-white/40">{stat.label}</p>
          </motion.div>
        ))}
      </div>
    </div>
  </Section>
);

const CapabilitiesGrid = () => (
  <Section id="performance" className="py-32 px-6 lg:px-12 max-w-[1600px] mx-auto text-center relative">
    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/5 blur-[180px] rounded-full -z-10" />
    <h2 className="font-heading text-6xl mb-20">Engineering the Impossible</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {[
        { title: 'Autonomous Execution', desc: 'Delegated tasks are handled independently from start to finish.', icon: Zap },
        { title: 'Career Trajectory', desc: 'Predictive analytics for optimizing your professional path.', icon: Users },
        { title: 'MCP Integration', desc: 'Plugs directly into the Model Context Protocol for boundless tool access.', icon: Layers },
        { title: 'Context Retention', desc: 'Long-term memory across sessions using advanced persistence.', icon: Cpu },
        { title: 'Shielded Privacy', desc: 'Total isolation of local data with high-grade encryption.', icon: Shield },
        { title: 'Dual-Engine Gemini Synthesis', desc: 'Dynamically switches between Gemini 1.5 Pro and Flash for optimal performance.', icon: Wifi },
      ].map((card, i) => (
        <motion.div 
          key={card.title}
          whileHover={{ y: -8 }}
          className="liquid-glass-strong p-10 rounded-[2.5rem] text-left group"
        >
          <div className="w-16 h-16 rounded-2xl border border-white/10 flex items-center justify-center mb-8 bg-white/5 transition-colors group-hover:border-indigo-500/50">
            <card.icon className="w-7 h-7 text-white/80 group-hover:text-indigo-400 transition-colors" />
          </div>
          <h4 className="font-heading text-3xl mb-4 italic">{card.title}</h4>
          <p className="font-body text-white/50 leading-relaxed">{card.desc}</p>
        </motion.div>
      ))}
    </div>
  </Section>
);

const JourneyTimeline = () => (
  <Section className="py-40 px-6 lg:px-12 max-w-[1200px] mx-auto">
    <div className="text-center mb-24">
      <h2 className="font-heading text-6xl mb-6 italic">The Intelligence Cycle</h2>
      <p className="font-body text-white/50 tracking-widest uppercase text-xs">A frictionless transition from request to result</p>
    </div>

    <div className="relative">
      <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-gradient-to-b from-transparent via-indigo-500/50 to-transparent -translate-x-1/2 hidden md:block" />
      
      {[
        { title: 'Input Synthesis', desc: 'Your request is parsed for intent and complex requirements.', step: '01' },
        { title: 'Agent Selection', desc: 'The orchestrator identifies the best specialists for the task.', step: '02' },
        { title: 'Tool Calibration', desc: 'Active MCP tools are connected and executed in parallel.', step: '03' },
        { title: 'Final Resolution', desc: 'The response is validated and delivered with full context.', step: '04' },
      ].map((item, i) => (
        <div key={item.title} className={cn("relative mb-24 md:flex items-center justify-between group", i % 2 === 1 ? "md:flex-row-reverse" : "")}>
          <div className="hidden md:block absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
            <div className="w-3 h-3 bg-indigo-500 rounded-full shadow-[0_0_15px_#6366f1] group-hover:scale-150 transition-transform" />
          </div>
          <div className="md:w-[45%]">
            <motion.div 
              initial={{ opacity: 0, x: i % 2 === 0 ? -40 : 40 }}
              whileInView={{ opacity: 1, x: 0 }}
              className="liquid-glass p-10 rounded-[2.5rem]"
            >
              <p className="font-heading text-4xl text-indigo-500/30 mb-4">{item.step}</p>
              <h4 className="font-heading text-3xl mb-4">{item.title}</h4>
              <p className="font-body text-white/60 leading-relaxed">{item.desc}</p>
            </motion.div>
          </div>
          <div className="md:w-[45%] h-px" />
        </div>
      ))}
    </div>
  </Section>
);

const IntelligenceDomains = () => (
  <Section id="domains" className="py-32 px-6 lg:px-12 max-w-[1600px] mx-auto">
    <div className="flex justify-between items-end mb-16">
      <h2 className="font-heading text-6xl">Intelligence Domains</h2>
      <a href="#" className="uppercase tracking-[0.2em] text-xs font-bold text-indigo-400 hover:text-white transition-colors pb-2 border-b border-indigo-500">Explore All Modules</a>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {[
        { title: 'Task Matrix', img: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80', span: true },
        { title: 'Career Nexus', img: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80', span: false },
        { title: 'Deep Knowledge', img: 'https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?auto=format&fit=crop&q=80', span: false },
        { title: 'Uptime Guard', img: 'https://images.unsplash.com/photo-1551288049-bbbda5366391?auto=format&fit=crop&q=80', span: false },
        { title: 'Control Deck', img: 'https://images.unsplash.com/photo-1544006659-f0b21f04cb1d?auto=format&fit=crop&q=80', span: true },
      ].map((item, i) => (
        <motion.div 
          key={item.title}
          whileHover={{ scale: 0.98 }}
          className={cn("h-[400px] rounded-[3rem] overflow-hidden relative group", item.span ? "md:col-span-2" : "md:col-span-1")}
        >
          <img 
            src={item.img} 
            className="w-full h-full object-cover grayscale transition-all duration-1000 group-hover:grayscale-0 group-hover:scale-110 opacity-70"
            alt={item.title}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#02040A] via-transparent to-transparent opacity-80" />
          <div className="absolute bottom-10 left-10 right-10 flex justify-between items-end">
            <h4 className="font-heading text-4xl">{item.title}</h4>
            <button className="p-3 liquid-glass rounded-full group-hover:bg-white group-hover:text-black transition-all">
              <ArrowUpRight className="w-5 h-5" />
            </button>
          </div>
        </motion.div>
      ))}
    </div>
  </Section>
);

const AssistantChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [liveDuration, setLiveDuration] = useState(0);
  const scrollRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    let interval;
    if (isTyping) {
      setLiveDuration(0);
      interval = setInterval(() => {
        setLiveDuration(prev => Number((prev + 0.01).toFixed(2)));
      }, 10);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isTyping]);

  useEffect(() => {
    fetch('/history').then(r => r.json()).then(data => {
      setMessages(data.history || []);
    });
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() && !selectedFile) return;
    const userMsg = input;
    const fileToUpload = selectedFile;
    
    setInput('');
    setSelectedFile(null);
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: userMsg,
      file: fileToUpload ? fileToUpload.name : null 
    }]);
    setIsTyping(true);

    try {
      const formData = new FormData();
      formData.append('text', userMsg);
      if (fileToUpload) {
        formData.append('file', fileToUpload);
      }

      const response = await fetch('/query', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        const errMsg = errData?.detail || `Server error (${response.status})`;
        setMessages(prev => [...prev, { role: 'bot', content: `⚠️ ${errMsg}` }]);
        return;
      }

      const data = await response.json();
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: data.response, 
        agent: data.metadata?.agent,
        duration: data.metadata?.duration,
        tokens: data.metadata?.tokens,
        tps: data.metadata?.tps
      }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'bot', content: "Error connecting to orchestrator." }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <Section id="control-deck" className="py-32 px-6 lg:px-12 max-w-[1200px] mx-auto">
      <div className="text-center mb-16">
        <h2 className="font-heading text-5xl mb-4 italic">Integrated Command</h2>
        <p className="font-body text-white/40 tracking-[0.2em] uppercase text-xs">Direct Neural Link to Orchestrator Core</p>
      </div>

      <div className="liquid-glass-strong rounded-[3rem] h-[700px] flex flex-col overflow-hidden">
        <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/5">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_10px_#22c55e]" />
            <span className="text-xs font-bold tracking-widest uppercase text-white/60">Active Session</span>
          </div>
          <div className="flex gap-4">
            <MessageSquare className="w-4 h-4 text-white/40" />
            <Layout className="w-4 h-4 text-white/40" />
          </div>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto p-10 space-y-8 scroll-smooth scrollbar-hide">
          {messages.map((msg, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn("flex flex-col max-w-[85%]", msg.role === 'user' ? "ml-auto items-end" : "items-start")}
            >
              {msg.agent && <span className="text-[10px] uppercase tracking-widest text-indigo-400 font-bold mb-2">{msg.agent.replace('_', ' ')} System</span>}
              <div className={cn(
                "p-6 rounded-[2rem] group",
                msg.role === 'user' ? "bg-indigo-600 text-white rounded-br-none" : "liquid-glass rounded-bl-none text-white/90"
              )}>
                {msg.file && (
                  <div className="mb-3 px-3 py-1.5 bg-black/20 rounded-xl flex items-center gap-2 text-[10px] font-mono text-white/60 w-fit">
                    <Paperclip className="w-3 h-3" /> {msg.file}
                  </div>
                )}
                <div 
                  className="prose prose-invert max-w-none text-sm leading-relaxed" 
                  dangerouslySetInnerHTML={{ __html: marked.parse(msg.content || "") }} 
                />
                {msg.role === 'bot' && msg.duration !== undefined && (
                  <div className="mt-4 pt-4 border-t border-white/5 flex items-center gap-4 text-[9px] uppercase tracking-[0.2em] font-mono text-white/20">
                    <span>{msg.duration}s</span>
                    <span className="w-1 h-1 bg-white/10 rounded-full" />
                    <span>{msg.tokens} tokens</span>
                    <span className="w-1 h-1 bg-white/10 rounded-full" />
                    <span>{msg.tps} t/s</span>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {isTyping && (
            <div className="flex flex-col items-start gap-4 p-6 liquid-glass rounded-[2rem] w-64 border border-white/5">
              <div className="flex gap-2">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
              <div className="text-[9px] uppercase tracking-[0.2em] font-mono text-indigo-400/60 animate-pulse">
                Neural Mapping: {liveDuration.toFixed(1)}s
              </div>
            </div>
          )}
        </div>

        <div className="p-8 bg-white/5 min-h-28 border-t border-white/5">
          {selectedFile && (
            <div className="mb-4 flex items-center gap-3 animate-in slide-in-from-bottom-2 duration-300">
              <div className="px-4 py-2 liquid-glass rounded-2xl flex items-center gap-3 text-[10px] font-bold tracking-widest uppercase border border-white/10 text-white/60">
                <Paperclip className="w-3 h-3 text-indigo-400" />
                {selectedFile.name}
                <button onClick={() => setSelectedFile(null)} className="hover:text-red-400 transition-colors">
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}
          <div className="liquid-glass rounded-[2rem] flex items-center pr-2 focus-within:ring-1 ring-indigo-500/50 transition-all border border-white/5">
            <input 
              type="file" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={(e) => setSelectedFile(e.target.files[0])}
            />
            <button 
              onClick={() => fileInputRef.current.click()}
              className="p-5 text-white/30 hover:text-white transition-colors"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Enter your command..."
              className="flex-1 bg-transparent border-none focus:ring-0 text-white p-4 font-body tracking-wide outline-none placeholder:text-white/20"
            />
            <button 
              onClick={handleSend}
              disabled={!input.trim() && !selectedFile}
              className="px-8 py-4 m-1 rounded-2xl bg-white text-black hover:bg-white/90 disabled:opacity-20 transition-all font-bold uppercase tracking-widest text-[10px]"
            >
              <Send className="w-4 h-4 mr-2 inline" /> Send
            </button>
          </div>
        </div>
      </div>
    </Section>
  );
};

const FAQSection = () => {
  const [openIndex, setOpenIndex] = useState(null);
  const faqs = [
    { q: "How does the orchestrator select agents?", a: "The core intelligence layer evaluates the intent and context of your query, matching it against the specialized knowledge profiles of our agent roster." },
    { q: "Is my task data processed locally?", a: "Yes. Assistant AI prioritizes local execution and leverages encrypted bridges for external model routing, ensuring your data remains isolated." },
    { q: "Can I add custom agents to the roster?", a: "The current ADK architecture supports seamless integration of custom agents through our modular specialist API." },
    { q: "How secure is the MCP integration?", a: "The Model Context Protocol integration uses high-level isolation layers to ensure tools only access the specific context granted by the user." },
  ];

  return (
    <Section className="py-32 px-6 lg:px-12 max-w-[1000px] mx-auto text-center">
      <h2 className="font-heading text-5xl mb-20 italic">Common Inquiries</h2>
      <div className="space-y-4">
        {faqs.map((faq, i) => (
          <div key={i} className="text-left">
            <button 
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
              className="w-full p-8 liquid-glass rounded-3xl flex justify-between items-center group transition-all"
            >
              <span className="font-heading text-2xl italic group-hover:text-indigo-400 transition-colors">{faq.q}</span>
              <ChevronDown className={cn("w-6 h-6 text-white/30 transition-transform duration-500", openIndex === i ? "rotate-180" : "")} />
            </button>
            <AnimatePresence>
              {openIndex === i && (
                <motion.div 
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.5, ease: EASE }}
                  className="overflow-hidden"
                >
                  <div className="p-10 font-body text-white/50 leading-relaxed text-lg border-x border-white/5 bg-white/[0.01] rounded-b-3xl">
                    {faq.a}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </Section>
  );
};

const Footer = () => (
  <footer className="pt-32 pb-16 px-6 lg:px-12 border-t border-white/5 relative bg-[#02040A] overflow-hidden">
    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1px] bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent" />
    <div className="max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-20 lg:gap-12 mb-20">
      <div className="lg:col-span-5">
        <div className="flex items-center gap-3 mb-8">
          <Orbit className="w-8 h-8 text-indigo-500" />
          <span className="font-heading italic text-3xl">Assistant AI .</span>
        </div>
        <h2 className="font-heading text-6xl italic leading-[0.9] text-balance mb-12">The universe of intelligence is calling.</h2>
        <div className="flex gap-4 p-2 liquid-glass rounded-3xl max-w-md">
          <input type="email" placeholder="Your coordinates (email)" className="flex-1 bg-transparent border-none focus:ring-0 px-6 font-body text-sm outline-none" />
          <button className="bg-white text-black px-8 py-3 rounded-2xl font-bold hover:bg-indigo-100 transition-all uppercase tracking-widest text-xs">Authorize</button>
        </div>
      </div>
      
      <div className="lg:col-span-1" />
      
      <div className="lg:col-span-3">
        <h5 className="text-white/30 uppercase tracking-[0.2em] text-[10px] font-bold mb-8">Intelligence Operations</h5>
        <ul className="space-y-4 font-body text-lg text-white/60">
          <li><a href="#" className="hover:text-white transition-colors">Orchestration Core</a></li>
          <li><a href="#" className="hover:text-white transition-colors">Agent Marketplace</a></li>
          <li><a href="#" className="hover:text-white transition-colors">Developer Portal</a></li>
          <li><a href="#" className="hover:text-white transition-colors">MCP Registry</a></li>
        </ul>
      </div>

      <div className="lg:col-span-3">
        <h5 className="text-white/30 uppercase tracking-[0.2em] text-[10px] font-bold mb-8">Strategic Nodes</h5>
        <ul className="space-y-4 font-body text-lg text-white/60">
          <li><a href="#" className="hover:text-white transition-colors">Security Protocol</a></li>
          <li><a href="#" className="hover:text-white transition-colors">Ethics Guidelines</a></li>
          <li><a href="#" className="hover:text-white transition-colors">Performance Telemetry</a></li>
          <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
        </ul>
      </div>
    </div>

    <div className="pt-16 border-t border-white/5 max-w-[1600px] mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
      <p className="text-white/20 text-xs font-medium uppercase tracking-[0.3em]">© 2026 Assistant AI. All rights reserved.</p>
      <div className="flex gap-12">
        <span className="text-white/20 text-xs font-medium uppercase tracking-[0.3em]">Privacy Interface</span>
        <span className="text-white/20 text-xs font-medium uppercase tracking-[0.3em]">Terms of Logic</span>
      </div>
      <div className="flex gap-8 items-center grayscale opacity-30">
        <span className="font-heading italic text-xl">ADK v1.2</span>
        <span className="font-heading italic text-xl">MCP Enabled</span>
      </div>
    </div>
  </footer>
);

export default function App() {
  const activeSection = useActiveSection(['control-deck', 'domains', 'intro', 'orchestration', 'agent-roster', 'performance']);

  return (
    <div className="min-h-screen relative selection:bg-indigo-500/30 selection:text-indigo-200">
      <Navbar activeSection={activeSection} />
      <main>
        <AssistantChat />
        <IntelligenceDomains />
        <Hero />
        <MissionBlock />
        <AgentRoster />
        <CapabilitiesGrid />
        <JourneyTimeline />
        <FAQSection />
      </main>
      <Footer />
    </div>
  );
}
