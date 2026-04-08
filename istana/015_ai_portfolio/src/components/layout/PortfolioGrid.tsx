"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { PortfolioItem } from '@/services/portfolio';

interface PortfolioGridProps {
  items: PortfolioItem[];
}

export const PortfolioGrid = ({ items }: PortfolioGridProps) => {
  return (
    <section id="portfolio" className="py-24 bg-black px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 space-y-4 md:space-y-0">
          <div>
            <h2 className="text-4xl md:text-6xl font-bold font-outfit tracking-tighter uppercase">Selected <br /> <span className="text-white/40">Works.</span></h2>
          </div>
          <p className="max-w-xs text-white/50 text-sm font-outfit">
            A curated selection of our most innovative digital experiences and AI-powered products, driven by Markdown CMS.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[300px]">
          {items.map((project, i) => (
            <motion.div
              key={project.slug}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, duration: 0.8 }}
              className={cn(
                "group relative rounded-3xl overflow-hidden glass border border-white/5 cursor-pointer",
                project.size === 'lg' ? "md:col-span-2 md:row-span-2" : "",
                project.size === 'md' ? "md:row-span-2" : ""
              )}
            >
              {/* Decorative Gradient Background from Markdown data */}
              <div className={cn(
                "absolute inset-0 bg-gradient-to-br opacity-20 group-hover:opacity-40 transition-opacity duration-500",
                project.color
              )} />
              
              <div className="absolute inset-0 p-8 flex flex-col justify-end">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[10px] uppercase tracking-widest font-bold text-white/40 font-outfit mb-1">{project.category}</p>
                    <h3 className="text-2xl font-bold font-outfit">{project.title}</h3>
                  </div>
                  <div className="w-12 h-12 rounded-full glass flex items-center justify-center opacity-0 group-hover:opacity-100 translate-y-4 group-hover:translate-y-0 transition-all duration-300">
                    <ArrowUpRight className="w-6 h-6" />
                  </div>
                </div>
              </div>

              {/* Hover Overlay */}
              <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
