import React from 'react';
import { motion } from 'framer-motion';

const Header: React.FC = () => {
  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className="container py-6 flex justify-between items-center"
    >
      <div className="text-2xl font-bold">AuraAI</div>
      <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-300">
        <a href="#services" className="hover:text-white transition-colors">Services</a>
        <a href="#case-studies" className="hover:text-white transition-colors">Case Studies</a>
        <a href="#contact" className="hover:text-white transition-colors">Contact</a>
      </nav>
      <button className="px-4 py-2 bg-primary-accent text-white rounded-lg hover:opacity-90 transition-opacity">Get Started</button>
    </motion.header>
  );
};

export default Header;