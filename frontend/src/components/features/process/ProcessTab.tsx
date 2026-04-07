'use client';

import React, { useState } from 'react';
import styles from '@/app/page.module.css';
import { API_ENDPOINTS } from '@/utils/api';

export function ProcessTab() {
  const [emails, setEmails] = useState<any[]>([]);
  const [isFetching, setIsFetching] = useState(false);

  const checkNow = async () => {
    setIsFetching(true);
    try {
      const response = await fetch(API_ENDPOINTS.getUnread);
      if (response.ok) {
        const data = await response.json();
        if (data.emails) {
          setEmails(data.emails);
        } else {
          alert('No new emails found.');
        }
      } else {
        throw new Error('Failed to fetch emails');
      }
    } catch (error: any) {
      alert('Error fetching emails: ' + error.message);
    } finally {
      setIsFetching(false);
    }
  };
  return (
    <div className="animate-fade-in">
      <div className={`${styles.card} glass-panel`} style={{ marginBottom: '2rem' }}>
        <div className={styles.cardHeader}>
          <h3>🔄 Real-Time Email Processing</h3>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div className={styles.formGroup} style={{ flex: 1, marginBottom: 0 }}>
            <label>Auto-refresh Interface</label>
            <select>
              <option>30s</option>
              <option>60s</option>
              <option>300s</option>
            </select>
          </div>
          <button 
            className="primary" 
            onClick={checkNow} 
            disabled={isFetching}
          >
            {isFetching ? '🔍 Checking...' : '🔍 Check Now'}
          </button>
        </div>
      </div>

      <div className={`${styles.card} glass-panel`}>
        <div className={styles.cardHeader}>
          <h3>📊 Email Status Dashboard</h3>
        </div>
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <span>📥 Incoming</span>
            <strong>{emails.length}</strong>
          </div>
          <div className={styles.statCard}>
            <span>📤 Fetched</span>
            <strong>{emails.length}</strong>
          </div>
          <div className={styles.statCard}>
            <span>✅ Processed</span>
            <strong>0</strong>
          </div>
          <div className={styles.statCard}>
            <span>⏳ Pending</span>
            <strong>{emails.length}</strong>
          </div>
        </div>
        
        {emails.length === 0 ? (
          <div style={{ marginTop: '2rem', textAlign: 'center', color: '#94a3b8' }}>
            <p>No current unread emails to display. Click 'Check Now' to fetch emails.</p>
          </div>
        ) : (
          <div style={{ marginTop: '2rem' }}>
            {emails.map((e, i) => (
              <div key={i} className={styles.message} style={{ background: 'rgba(255, 255, 255, 0.05)', marginBottom: '1rem', border: '1px solid var(--border)' }}>
                <p><strong>From:</strong> {e.from || e.sender}</p>
                <p><strong>Subject:</strong> {e.subject}</p>
                <p className="line-clamp-2" style={{ color: '#94a3b8', marginTop: '0.5rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{e.body}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
