import React from "react";
import { BentoGrid, BentoGridItem } from "./ui/BentoGrid";
import { motion } from "framer-motion";
import { Bot, Target, TrendingUp, PenTool, BarChart, Settings } from "lucide-react";

export function LandingPage() {
  return (
    <div className="min-h-screen w-full bg-brand-dark bg-dot-white/[0.2] relative flex flex-col items-center justify-center p-4">
      <div className="absolute pointer-events-none inset-0 flex items-center justify-center bg-brand-dark [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]"></div>
      <header className="w-full max-w-7xl mx-auto mb-12">
         <h1 className="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">AI Marketing Agency</h1>
         <p className="text-neutral-300 max-w-lg mt-2">Transforming Brands with Data-Driven AI Strategies.</p>
      </header>
      <BentoGrid className="max-w-4xl mx-auto">
        {items.map((item, i) => (
          <BentoGridItem
            key={i}
            title={item.title}
            description={item.description}
            header={item.header}
            icon={item.icon}
            className={item.className}
          />
        ))}
      </BentoGrid>
    </div>
  );
}

const Skeleton = () => (
    <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        transition={{ duration: 0.5 }}
        className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800"
    ></motion.div>
);

const items = [
  {
    title: "AI-Powered Ad Campaigns",
    description: "Optimize ad spend with predictive analytics and automated bidding.",
    header: <Skeleton />,
    className: "md:col-span-2",
    icon: <Bot className="h-4 w-4 text-neutral-400" />,
  },
  {
    title: "Content Personalization",
    description: "Deliver hyper-personalized content that resonates with your audience.",
    header: <Skeleton />,
    className: "md:col-span-1",
    icon: <PenTool className="h-4 w-4 text-neutral-400" />,
  },
  {
    title: "Predictive Lead Scoring",
    description: "Focus your sales team on the most promising leads.",
    header: <Skeleton />,
    className: "md:col-span-1",
    icon: <Target className="h-4 w-4 text-neutral-400" />,
  },
  {
    title: "Market Trend Analysis",
    description: "Stay ahead of the curve with real-time market insights.",
    header: <Skeleton />,
    className: "md:col-span-2",
    icon: <TrendingUp className="h-4 w-4 text-neutral-400" />,
  },
];