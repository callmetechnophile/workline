'use client';

import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, Bot, User, Trash2, Cpu, HelpCircle, Loader2, Volume2, VolumeX } from 'lucide-react';

interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
  timestamp: Date;
}

interface ConnectionChatbotProps {
  projectContext?: {
    bom?: any[];
    wiring?: any;
    power?: any;
    datasheets?: any[];
  };
  apiBase?: string;
}

export default function ConnectionChatbot({ projectContext = { bom: [], wiring: {}, power: {}, datasheets: [] }, apiBase = '' }: ConnectionChatbotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [playingMessageIndex, setPlayingMessageIndex] = useState<number | null>(null);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          sender: 'bot',
          text: "🔧 [System Connection Assistant Online]: I am connected to your project's active schematics, pin maps, and power thresholds. Ask me about electrical connections, pin compatibilities, or debugging logic rail issues.",
          timestamp: new Date()
        }
      ]);
    }
  }, []);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      audioElement?.pause();
    };
  }, [audioElement]);

  const handleSpeak = async (text: string, idx: number) => {
    if (playingMessageIndex === idx) {
      audioElement?.pause();
      setPlayingMessageIndex(null);
      return;
    }

    audioElement?.pause();
    setPlayingMessageIndex(idx);

    try {
      const res = await fetch(`${apiBase}/api/speech/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.onended = () => {
          setPlayingMessageIndex(null);
        };
        audio.play();
        setAudioElement(audio);
      } else {
        setPlayingMessageIndex(null);
      }
    } catch (err) {
      console.error("Audio playback error:", err);
      setPlayingMessageIndex(null);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const queryText = textToSend || input;
    if (!queryText.trim() || isLoading) return;

    // Clear input
    if (!textToSend) setInput("");

    // Add user message
    const userMsg: ChatMessage = {
      sender: 'user',
      text: queryText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch(`${apiBase}/api/workspace/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: queryText,
          context: {
            bom: projectContext?.bom || [],
            wiring: projectContext?.wiring || [],
            power: projectContext?.power || {},
            datasheets: projectContext?.datasheets || []
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: data.reply,
          timestamp: new Date()
        }]);
      } else {
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: "⚠️ Error: Connection Assistant failed to reach the model.",
          timestamp: new Date()
        }]);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: "⚠️ Network Error: Check if your local backend is running.",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        sender: 'bot',
        text: "🔧 [System Connection Assistant Online]: Conversation cleared. How can I help you debug your wiring configuration?",
        timestamp: new Date()
      }
    ]);
  };

  const quickPrompts = [
    "Why is my MPU6050 not responding?",
    "SG90 Servo wire connections?",
    "Overcurrent and voltage risks check?",
    "I2C protocol pins compatibility?"
  ];

  return (
    <div className="glass-panel border border-blue-500/20 bg-zinc-950/40 rounded-xl overflow-hidden h-[540px] flex flex-col font-mono">
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900/40 p-4 shrink-0">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
            Connection Assistant Terminal
          </h3>
          <span className="text-[9px] bg-cyan-950/60 border border-cyan-800 text-cyan-400 px-2 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse">
            Llama-Nemotron
          </span>
        </div>
        <button
          onClick={handleClear}
          title="Clear Conversation"
          className="text-slate-500 hover:text-slate-300 transition-all cursor-pointer p-1 hover:bg-slate-800/40 rounded"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 bg-slate-950/20">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 max-w-[85%] ${
              msg.sender === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-7 h-7 rounded-full shrink-0 flex items-center justify-center border text-xs ${
                msg.sender === 'user'
                  ? 'border-blue-800 bg-blue-950/60 text-blue-400'
                  : 'border-cyan-800 bg-cyan-950/60 text-cyan-400'
              }`}
            >
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Bubble */}
            <div
              className={`p-3 rounded-lg border text-xs leading-relaxed break-words whitespace-pre-wrap ${
                msg.sender === 'user'
                  ? 'bg-blue-950/20 border-blue-900/60 text-slate-100'
                  : 'bg-cyan-950/10 border-cyan-900/60 text-cyan-200'
              }`}
            >
              {msg.text}
              <div className="flex items-center justify-between gap-4 mt-2 pt-1.5 border-t border-slate-800/40 text-[9px]">
                {msg.sender === 'bot' ? (
                  <button
                    onClick={() => handleSpeak(msg.text, idx)}
                    className="flex items-center gap-1.5 text-cyan-400/70 hover:text-cyan-400 font-bold transition-all cursor-pointer select-none"
                  >
                    {playingMessageIndex === idx ? (
                      <>
                        <VolumeX className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Stop</span>
                      </>
                    ) : (
                      <>
                        <Volume2 className="w-3.5 h-3.5" />
                        <span>Speak</span>
                      </>
                    )}
                  </button>
                ) : (
                  <div />
                )}
                <span className="text-slate-500 font-mono">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 mr-auto items-center">
            <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center border border-cyan-800 bg-cyan-950/60 text-cyan-400">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3 rounded-lg border bg-cyan-950/10 border-cyan-900/60 text-cyan-400/80 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
              <span className="text-xs">Analyzing schematics constraints...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      <div className="p-3 border-t border-slate-900 bg-slate-950/30 flex flex-wrap gap-2 shrink-0">
        {quickPrompts.map((promptText) => (
          <button
            key={promptText}
            onClick={() => handleSend(promptText)}
            disabled={isLoading}
            className="text-[9px] text-slate-400 border border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:text-slate-200 px-2.5 py-1 rounded transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {promptText}
          </button>
        ))}
      </div>

      {/* Input area */}
      <div className="p-3 border-t border-slate-900 bg-slate-950/40 shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Ask about protocol conflicts, overcurrent, logic matching..."
            className="flex-1 bg-slate-950 border border-slate-800 focus:border-cyan-800 outline-none text-xs px-3.5 py-2.5 rounded text-slate-100 placeholder-slate-600 disabled:opacity-50 font-mono"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-cyan-950 border border-cyan-800 hover:bg-cyan-900 text-cyan-400 px-4 rounded transition-all flex items-center justify-center shrink-0 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
