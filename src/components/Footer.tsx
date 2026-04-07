import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="container text-center py-8 mt-10 border-t border-glass-border">
      <p className="text-text-secondary text-sm">&copy; {new Date().getFullYear()} AuraAI. All Rights Reserved.</p>
    </footer>
  );
};

export default Footer;