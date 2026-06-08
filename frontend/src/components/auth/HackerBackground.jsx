// hackerbackground component
// renders the animated grid of hoverable squares with scanning green line,
// replicating the hacker login form background effect.

import React, { useMemo } from 'react';

const SPAN_COUNT = 260;

const HackerBackground = ({ children }) => {
  const spans = useMemo(
    () => Array.from({ length: SPAN_COUNT }, (_, i) => <span key={i} className="grid-span" />),
    []
  );

  return (
    <section className="auth-section">
      {spans}
      {children}
    </section>
  );
};

export default HackerBackground;
