import React from 'react';
import { motion } from 'framer-motion';
import { BentoGridItem } from '../types';

const BentoCard: React.FC<BentoGridItem> = ({ title, description, icon: Icon, className }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      className={`glassmorphism-card p-6 flex flex-col justify-between ${className}`}
    >
      <div>
        <Icon className="h-8 w-8 mb-4 text-primary-accent" />
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-sm text-text-secondary">{description}</p>
      </div>
    </motion.div>
  );
};

export default BentoCard;