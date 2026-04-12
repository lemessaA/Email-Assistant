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
    <div className="animate-fade-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

      {/* Control Card */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3>⚡ Real-Time Email Processing</h3>
          <span className="badge badge-warning">Live</span>
        </div>

        <div className="divider" />

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div className={styles.formGroup} style={{ flex: 1, marginBottom: 0 }}>
            <label className="form-label">Auto-refresh Interval</label>
            <select id="refreshInterval">
              <option>30 seconds</option>
              <option>60 seconds</option>
              <option>5 minutes</option>
            </select>
          </div>
          <button
            id="checkNowBtn"
            className="primary"
            onClick={checkNow}
            disabled={isFetching}
            style={{ flexShrink: 0 }}
          >
            {isFetching ? (
              <><span className="spinner" /> Checking…</>
            ) : (
              <>🔍 Check Now</>
            )}
          </button>
        </div>
      </div>

      {/* Stats Card */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3>📊 Email Dashboard</h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
          {[
            { label: 'Incoming', value: emails.length, icon: '📥' },
            { label: 'Fetched',  value: emails.length, icon: '📤' },
            { label: 'Processed', value: 0, icon: '✅' },
            { label: 'Pending',  value: emails.length, icon: '⏳' },
          ].map((s) => (
            <div key={s.label} className={styles.statCard}>
              <span>{s.icon} {s.label}</span>
              <strong>{s.value}</strong>
            </div>
          ))}
        </div>

        {emails.length === 0 ? (
          <div style={{
            marginTop: '1rem',
            padding: '2rem',
            textAlign: 'center',
            color: '#4a5578',
            background: 'rgba(99, 102, 241, 0.03)',
            borderRadius: '10px',
            border: '1px dashed rgba(99, 102, 241, 0.12)',
          }}>
            <p style={{ fontSize: '24px', marginBottom: '0.5rem' }}>📭</p>
            <p style={{ fontSize: '13px' }}>No emails yet. Click <strong style={{ color: '#818cf8' }}>Check Now</strong> to fetch unread messages.</p>
          </div>
        ) : (
          <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {emails.map((e, i) => (
              <div key={i} style={{
                padding: '1rem 1.25rem',
                borderRadius: '10px',
                background: 'rgba(17, 29, 53, 0.8)',
                border: '1px solid rgba(99, 102, 241, 0.1)',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.25rem',
              }}>
                <p style={{ fontWeight: 600, color: '#c4c9ff', fontSize: '13px' }}>
                  <span style={{ color: '#4a5578', marginRight: '0.5rem' }}>From</span>
                  {e.from || e.sender}
                </p>
                <p style={{ fontWeight: 600, fontSize: '13px', color: '#e2e8ff' }}>{e.subject}</p>
                <p style={{
                  fontSize: '12px',
                  color: '#4a5578',
                  overflow: 'hidden',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                }}>
                  {e.body}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
