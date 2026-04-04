'use client';

import React from 'react';
import styles from '@/app/page.module.css';

export function HistoryTab() {
  return (
    <div className="animate-fade-in">
       <div className={`${styles.card} glass-panel`}>
          <div className={styles.cardHeader}>
            <h3>📚 History</h3>
            <p style={{ color: '#94a3b8', marginTop: '1rem' }}>No history available yet.</p>
          </div>
       </div>
    </div>
  );
}
