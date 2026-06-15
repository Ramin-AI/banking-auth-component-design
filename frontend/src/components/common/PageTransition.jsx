// pagetransition component
// wraps page content with a smooth fade + slide-up entrance animation.

import React, { useEffect, useState } from 'react';
import './PageTransition.css';

const PageTransition = ({ children }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Trigger the entrance animation on the next frame
    const raf = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <div className={`page-transition ${visible ? 'page-transition--visible' : ''}`}>
      {children}
    </div>
  );
};

export default PageTransition;
