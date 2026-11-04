'use client';
import { motion, useReducedMotion } from 'motion/react';

export function AgentMark({ state = 'ready', small = false }: { state?: 'ready' | 'working' | 'waiting' | 'done' | 'paused' | 'failed'; small?: boolean }) {
  const reduced = useReducedMotion();
  return <span className={`ag-mark ag-mark-${state} ${small ? 'ag-mark-small' : ''}`} aria-hidden="true">
    {[0, 1, 2, 3].map(index => <motion.i key={index}
      animate={state === 'working' && !reduced ? { scaleY: [1, .45, 1], opacity: [1, .45, 1] } : { scaleY: 1, opacity: 1 }}
      transition={{ duration: 1.2, repeat: state === 'working' && !reduced ? Infinity : 0, delay: index * .13 }} />)}
  </span>;
}
