"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight, Zap, Shield, Globe } from 'lucide-react';

export const Hero = () => {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center pt-20 overflow-hidden bg-black text-white">
      {/* Dynamic Background Blobs */}
      <motion.div 
        animate={{ 
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
          rotate: [0, 90, 0]
        }}
        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        className="absolute top-[-20%] right-[-10%] w-[60%] h-[60%] bg-blue-600/20 blur-[150px] rounded-full" 
      />
      <motion.div 
        animate={{ 
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
          rotate: [0, -90, 0]
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="absolute bottom-[-20%] left-[-10%] w-[60%] h-[60%] bg-purple-600/20 blur-[150px] rounded-full" 
      />

      <div className="container mx-auto px-6 z-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full glass border border-white/10 mb-8"
        >
          <Zap className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-bold uppercase tracking-widest font-outfit">Next-Gen Digital Agency</span>
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
          className="text-6xl md:text-9xl font-bold tracking-tighter leading-[0.9] font-outfit mb-8"
        >
          <span className="text-gradient">ENGINEERING</span> <br /> 
          THE EXTRAORDINARY.
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="text-white/60 text-lg md:text-xl max-w-2xl mx-auto mb-10 font-outfit"
        >
          We build high-performance digital products that merge cutting-edge technology 
          with futuristic aesthetics. Powered by Autonomous Agentic AI.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-6"
        >
          <button className="group relative px-8 py-4 bg-white text-black rounded-full font-bold text-lg hover:scale-105 transition-all duration-300 flex items-center font-outfit">
            Start a Project
            <ArrowUpRight className="ml-2 w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
          </button>
          <button className="px-8 py-4 glass text-white rounded-full font-bold text-lg hover:bg-white/10 transition-all duration-300 font-outfit border border-white/20">
            View Analytics
          </button>
        </motion.div>

        {/* Floating Features */}
        <div className="mt-24 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto pb-20">
          {[
            { icon: Globe, text: "Global Reach" },
            { icon: Shield, text: "Secured Scale" },
            { icon: Zap, text: "Fast Engine" },
            { icon: Rocket, text: "AI Native" }
          ].map((item, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1 + (i * 0.1) }}
              className="flex flex-col items-center space-y-2"
            >
              <item.icon className="w-6 h-6 text-white/40" />
              <span className="text-[10px] uppercase tracking-widest text-white/40 font-bold font-outfit">{item.text}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

const Rocket = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-5c1.62-2.2 5-3 5-3"/><path d="M12 15v5s3.03-.55 5-2c2.2-1.62 3-5 3-5"/></svg>
);
