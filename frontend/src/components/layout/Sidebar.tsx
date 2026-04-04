'use client';

import React from 'react';
import styles from '@/app/page.module.css';
import { AppConfig, MODELS, TONES, PRIORITIES, TEMPLATES } from '@/types';

interface SidebarProps {
  config: AppConfig;
  onConfigChange: (key: keyof AppConfig, value: any) => void;
  onClear: () => void;
}

export function Sidebar({ config, onConfigChange, onClear }: SidebarProps) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.sidebarHeader}>
        <h2>🤖 🔛 Assistant</h2>
      </div>

      <div className={styles.sidebarSection}>
        <h3>Configuration</h3>
        <div className={styles.formGroup}>
          <label>Your Email (Sender)</label>
          <input
            type="email"
            placeholder="your-email@gmail.com"
            value={config.senderEmail}
            onChange={(e) => onConfigChange('senderEmail', e.target.value)}
          />
        </div>
      </div>

      <div className={styles.sidebarSection}>
        <h3>✨ AI Configuration</h3>
        
        <div className={styles.formGroup}>
          <label>🤖 LLM Model</label>
          <select
            value={config.model}
            onChange={(e) => onConfigChange('model', e.target.value)}
          >
            {MODELS.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className={styles.formGroup}>
          <label>📝 Response Tone</label>
          <select
            value={config.tone}
            onChange={(e) => onConfigChange('tone', e.target.value)}
          >
            {TONES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className={styles.formGroup}>
          <label>⚡ Priority Level</label>
          <select
            value={config.priority}
            onChange={(e) => onConfigChange('priority', e.target.value)}
          >
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        <div className={styles.formGroup}>
          <label>📋 Templates</label>
          <select
            value={config.template}
            onChange={(e) => onConfigChange('template', e.target.value)}
          >
            {Object.keys(TEMPLATES).map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className={styles.formGroup} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <input
            type="checkbox"
            id="autoSend"
            checked={config.autoRes}
            onChange={(e) => onConfigChange('autoRes', e.target.checked)}
            style={{ width: 'auto' }}
          />
          <label htmlFor="autoSend" style={{ margin: 0 }}>Auto-send responses</label>
        </div>
      </div>

      <div className={styles.sidebarSection}>
        <h3>📊 Statistics</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <span>Emails</span>
            <strong>0</strong>
          </div>
          <div className={styles.statCard}>
            <span>Avg Time</span>
            <strong>45s</strong>
          </div>
        </div>
      </div>

      <button className="secondary" onClick={onClear} style={{ marginTop: 'auto' }}>
        🗑️ Clear All Data
      </button>
    </aside>
  );
}
