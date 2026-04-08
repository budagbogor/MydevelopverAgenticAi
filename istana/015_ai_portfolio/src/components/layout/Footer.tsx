"use client";

import React from 'react';
import { Rocket, Mail, X } from 'lucide-react';

const GithubIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.393 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
);

const LinkedinIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/></svg>
);

export const Footer = () => {
  return (
    <footer className="bg-black pt-24 pb-12 px-6 border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2 mb-6">
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <Rocket className="text-white w-5 h-5" />
              </div>
              <span className="text-xl font-bold font-outfit tracking-tighter">DARK<span className="text-blue-500">SKY</span></span>
            </div>
            <p className="text-white/40 max-w-sm font-outfit text-sm leading-relaxed">
              We are a futuristic digital agency empowering brands with autonomous AI solutions 
              and premium digital experiences. Built for the next era of the web.
            </p>
          </div>

          <div>
            <h4 className="text-white font-bold font-outfit mb-6">RESOURCES</h4>
            <ul className="space-y-4 text-sm text-white/40 font-outfit">
              <li className="hover:text-white transition-colors cursor-pointer">Our Services</li>
              <li className="hover:text-white transition-colors cursor-pointer">Case Studies</li>
              <li className="hover:text-white transition-colors cursor-pointer">Design System</li>
              <li className="hover:text-white transition-colors cursor-pointer">AI Research</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-bold font-outfit mb-6">CONTACT</h4>
            <ul className="space-y-4 text-sm text-white/40 font-outfit">
              <li className="flex items-center space-x-2">
                <Mail className="w-4 h-4" />
                <span>hello@darksky.agency</span>
              </li>
              <li className="hover:text-white transition-colors cursor-pointer">General Inquiries</li>
              <li className="hover:text-white transition-colors cursor-pointer">Press Kit</li>
            </ul>
          </div>
        </div>

        <div className="pt-12 border-t border-white/5 flex flex-col md:flex-row justify-between items-center space-y-6 md:space-y-0">
          <p className="text-[10px] uppercase tracking-widest font-bold text-white/20 font-outfit">
            © 2026 DARKSKY AGENTIC AI. ALL RIGHTS RESERVED.
          </p>
          <div className="flex space-x-6">
             <div className="w-5 h-5 text-white/20 hover:text-white transition-colors cursor-pointer">
                <X size={20} />
             </div>
             <div className="w-5 h-5 text-white/20 hover:text-white transition-colors cursor-pointer">
                <GithubIcon />
             </div>
             <div className="w-5 h-5 text-white/20 hover:text-white transition-colors cursor-pointer">
                <LinkedinIcon />
             </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
