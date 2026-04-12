'use client';

import React from 'react';
import styles from '@/app/page.module.css';

export function HistoryTab() {
  return (
    <div className="animate-fade-up">
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3>🕓 Email History</h3>
          <span className="badge badge-indigo">0 Records</span>
        </div>

        <div className="divider" />

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '3rem 2rem',
          gap: '1rem',
          textAlign: 'center',
        }}>
          <span style={{ fontSize: '3rem', opacity: 0.5 }}>📭</span>
          <div>
            <p style={{ color: '#8b9ac5', fontWeight: 600, marginBottom: '0.35rem' }}>No history yet</p>
            <p style={{ color: '#4a5578', fontSize: '13px', maxWidth: '300px' }}>
              Your sent and processed emails will appear here so you can review them anytime.
            </p>
          </div>
          <button id="refreshHistoryBtn" className="secondary" style={{ marginTop: '0.5rem' }}>
            🔄 Refresh
          </button>
        </div>
      </div>
    </div>
  );
}
