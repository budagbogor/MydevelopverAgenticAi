import React from 'react';
import { motion } from 'framer-motion';
import BentoCard from './BentoCard';
import { BrainCircuit, Target, LineChart, ShieldCheck, Bot, BarChart } from 'lucide-react';
import { BentoGridItem } from '../types';

const features: BentoGridItem[] = [
  {
    id: 1,
    title: 'Predictive Analytics',
    description: 'Anticipate market trends and customer behavior with our AI-powered predictive models.',
    icon: LineChart,
    className: 'md:col-span-2',
  },
  {
    id: 2,
    title: 'Hyper-Personalization',
    description: 'Deliver unique customer experiences at scale by tailoring content and offers in real-time.',
    icon: Target,
    className: 'md:col-span-1',
  },
  {
    id: 3,
    title: 'AI Content Generation',
    description: 'Generate high-quality, on-brand content for blogs, social media, and ads in seconds.',
    icon: BrainCircuit,
    className: 'md:col-span-1',
  },
  {
    id: 4,
    title: 'Automated Ad Campaigns',
    description: 'Optimize your ad spend with AI algorithms that manage bidding, targeting, and creative automatically.',
    icon: Bot,
    className: 'md:col-span-2',
  },
];

const BentoGrid: React.FC = () => {
  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="container grid grid-cols-1 md:grid-cols-3 gap-6 mb-20"
    >
      {features.map((feature) => (
        <motion.div key={feature.id} variants={itemVariants}>
           <BentoCard {...feature} />
        </motion.div>
      ))}
    </motion.div>
  );
};

export default BentoGrid;