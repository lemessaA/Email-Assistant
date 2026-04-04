'use client';

import React from 'react';
import styles from '@/app/page.module.css';

export function AnalyzeTab() {
  return (
    <div className="animate-fade-in">
       <div className={`${styles.card} glass-panel`}>
          <div className={styles.cardHeader}>
            <h3>Email Analysis</h3>
          </div>
          <div className={styles.formGroup}>
            <label>Upload email (.eml)</label>
            <input type="file" accept=".eml" />
          </div>
          <button className="primary" style={{ width: 'max-content' }}>Analyze Email</button>
       </div>
    </div>
  );
}
