"use client";

import React from "react";
import { Cloud, Cpu, Sparkles } from "lucide-react";

export default function SocialProof() {
  return (
    <section
      id="social-proof"
      className="bg-white text-black py-28 md:py-40 flex flex-col justify-center font-sans relative border-b border-black"
    >
      <div className="max-w-7xl mx-auto w-full px-6 flex flex-col gap-14">
        
        {/* Stark Top Divider Line */}
        <div className="w-full h-[1px] bg-black"></div>

        {/* Credentials Headline */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 select-none">
          <div className="space-y-1">
            <span className="text-[11px] font-bold tracking-widest text-[#f5a623] uppercase">
              05 / CREDENTIALS
            </span>
            <h3 className="font-serif text-3xl sm:text-4xl font-bold tracking-tight uppercase leading-none">
              Enterprise Grade AI Architecture
            </h3>
          </div>
          <p className="text-sm font-bold tracking-widest uppercase font-mono text-neutral-500 border border-neutral-300 px-4 py-2 self-start md:self-center">
            POWERED BY GEMINI + VERTEX AI
          </p>
        </div>

        {/* Logo strip row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 mt-4">
          
          {/* Google Cloud Block */}
          <div className="flex items-center gap-4 border border-black p-6 hover:bg-black hover:text-white transition-colors duration-300 select-none">
            <div className="w-10 h-10 border border-black bg-black text-white flex items-center justify-center font-bold">
              <Cloud className="w-5 h-5 text-[#f5a623]" />
            </div>
            <div>
              <h4 className="font-serif text-lg font-bold tracking-tight uppercase">
                Google Cloud
              </h4>
              <p className="font-mono text-[9px] tracking-wider uppercase text-neutral-400">
                SANDBOX INGEST PIPELINE
              </p>
            </div>
          </div>

          {/* Vertex AI Block */}
          <div className="flex items-center gap-4 border border-black p-6 hover:bg-black hover:text-white transition-colors duration-300 select-none">
            <div className="w-10 h-10 border border-black bg-black text-white flex items-center justify-center font-bold">
              <Cpu className="w-5 h-5 text-[#f5a623]" />
            </div>
            <div>
              <h4 className="font-serif text-lg font-bold tracking-tight uppercase">
                Vertex AI
              </h4>
              <p className="font-mono text-[9px] tracking-wider uppercase text-neutral-400">
                MULTI-AGENT ORCHESTRATION
              </p>
            </div>
          </div>

          {/* Gemini 2.5 Pro Block */}
          <div className="flex items-center gap-4 border border-black p-6 hover:bg-black hover:text-white transition-colors duration-300 select-none">
            <div className="w-10 h-10 border border-black bg-black text-white flex items-center justify-center font-bold">
              <Sparkles className="w-5 h-5 text-[#f5a623]" />
            </div>
            <div>
              <h4 className="font-serif text-lg font-bold tracking-tight uppercase">
                Google Gemini
              </h4>
              <p className="font-mono text-[9px] tracking-wider uppercase text-neutral-400">
                EXPLAINABLE LOGIC ENGINE
              </p>
            </div>
          </div>

        </div>

        {/* Stark Bottom Divider Line */}
        <div className="w-full h-[1px] bg-black"></div>

      </div>
    </section>
  );
}
