'use client';

import React from 'react';
import Link from 'next/link';
import styles from '@/app/page.module.css';
import { AppConfig, MODELS, TONES, PRIORITIES, TEMPLATES } from '@/types';

interface SidebarProps {
  config: AppConfig;
  onConfigChange: (key: keyof AppConfig, value: any) => void;
  onClear: () => void;
}

const SelectField = ({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) => (
  <div className={styles.formGroup}>
    <label className="form-label">{label}</label>
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map((o) => (
        <option key={o} value={o}>{o}</option>
      ))}
    </select>
  </div>
);

export function Sidebar({ config, onConfigChange, onClear }: SidebarProps) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.sidebarInner}>

        {/* Brand */}
        <div className={styles.sidebarBrand}>
          <div className={styles.brandIcon}>✉️</div>
          <div className={styles.brandText}>
            <span className={styles.brandName}>MailAssist</span>
            <span className={styles.brandTagline}>AI-powered inbox</span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className={styles.sidebarSection}>
          <p className="section-title">Navigation</p>
          <Link href="/settings" className={styles.quickActionLink} style={{ textDecoration: 'none' }}>
            <span>⚙️</span>
            <span>Settings</span>
          </Link>
        </div>

        {/* Sender Email */}
        <div className={styles.sidebarSection}>
          <p className="section-title">Identity</p>
          <div className={styles.formGroup}>
            <label className="form-label">Sender Email</label>
            <input
              id="senderEmail"
              type="email"
              placeholder="you@gmail.com"
              value={config.senderEmail}
              onChange={(e) => onConfigChange('senderEmail', e.target.value)}
            />
          </div>
        </div>

        {/* AI Config */}
        <div className={styles.sidebarSection}>
          <p className="section-title">AI Configuration</p>

          <SelectField
            label="LLM Model"
            value={config.model}
            onChange={(v) => onConfigChange('model', v)}
            options={MODELS}
          />

          <SelectField
            label="Response Tone"
            value={config.tone}
            onChange={(v) => onConfigChange('tone', v)}
            options={TONES}
          />

          <SelectField
            label="Priority Level"
            value={config.priority}
            onChange={(v) => onConfigChange('priority', v)}
            options={PRIORITIES}
          />

          <SelectField
            label="Template"
            value={config.template}
            onChange={(v) => onConfigChange('template', v)}
            options={Object.keys(TEMPLATES)}
          />

          <div className={styles.checkboxRow}>
            <input
              type="checkbox"
              id="autoSend"
              checked={config.autoRes}
              onChange={(e) => onConfigChange('autoRes', e.target.checked)}
            />
            <label htmlFor="autoSend">Auto-send responses</label>
          </div>
        </div>

        {/* Stats */}
        <div className={styles.sidebarSection}>
          <p className="section-title">Statistics</p>
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

        {/* Footer Clear */}
        <div className={styles.sidebarFooter}>
          <button
            id="clearAllBtn"
            className="danger"
            onClick={onClear}
            style={{ width: '100%' }}
          >
            🗑️ Clear All Data
          </button>
        </div>

      </div>
    </aside>
  );
}
