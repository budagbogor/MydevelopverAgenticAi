import React from 'react';
import { motion } from 'framer-motion';

const Hero: React.FC = () => {
  return (
    <div className="container text-center py-20 md:py-32">
      <motion.h1 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50 tracking-tighter"
      >
        Next-Gen AI Marketing
      </motion.h1>
      <motion.p 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.2 }}
        className="mt-6 text-lg max-w-2xl mx-auto text-text-secondary"
      >
        We leverage cutting-edge AI to build marketing strategies that deliver unparalleled results and futuristic brand experiences.
      </motion.p>
    </div>
  );
};

export default Hero;