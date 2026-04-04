'use client';

import React from 'react';
import styles from '@/app/page.module.css';
import { ComposeState, Message } from '@/types';

interface ComposeTabProps {
  state: ComposeState;
  onChange: (key: keyof ComposeState, value: string) => void;
  conversation: Message[];
  onGenerateResponse: () => void;
  onClearConversation: () => void;
  onSendEmail: () => void;
  isGenerating: boolean;
  isSending: boolean;
}

export function ComposeTab({
  state,
  onChange,
  conversation,
  onGenerateResponse,
  onClearConversation,
  onSendEmail,
  isGenerating,
  isSending,
}: ComposeTabProps) {
  return (
    <div className={`${styles.grid} animate-fade-in`}>
      <div className={`${styles.card} glass-panel`}>
        <div className={styles.cardHeader}>
          <h3>Compose Email</h3>
        </div>
        
        <div className={styles.formGroup}>
          <label>To</label>
          <input
            type="email"
            placeholder="recipient@example.com"
            value={state.to}
            onChange={(e) => onChange('to', e.target.value)}
          />
        </div>

        <div className={styles.formGroup}>
          <label>Subject</label>
          <input
            type="text"
            placeholder="Email subject..."
            value={state.subject}
            onChange={(e) => onChange('subject', e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className={styles.formGroup} style={{ flex: 1 }}>
            <label>CC</label>
            <input
              type="text"
              value={state.cc}
              onChange={(e) => onChange('cc', e.target.value)}
            />
          </div>
          <div className={styles.formGroup} style={{ flex: 1 }}>
            <label>BCC</label>
            <input
              type="text"
              value={state.bcc}
              onChange={(e) => onChange('bcc', e.target.value)}
            />
          </div>
        </div>

        <div className={styles.formGroup}>
          <label>Email Content</label>
          <textarea
            rows={10}
            placeholder="Type your email here..."
            value={state.body}
            onChange={(e) => onChange('body', e.target.value)}
          />
        </div>

        <div className={styles.cardActions}>
          <button 
            className="primary" 
            style={{ flex: 1 }} 
            onClick={onSendEmail}
            disabled={isSending}
          >
            {isSending ? '📤 Sending...' : '📤 Send Email'}
          </button>
          <button className="secondary" style={{ flex: 1 }}>💾 Save Draft</button>
        </div>
      </div>

      <div className={`${styles.card} glass-panel`}>
        <div className={styles.cardHeader}>
          <h3>AI Assistant</h3>
        </div>
        
        <div className={styles.buttonGrid}>
          <button className="secondary">✨ Improve Tone</button>
          <button className="secondary">📝 Check Grammar</button>
        </div>
        <button className="secondary" style={{ marginBottom: '1rem' }}>🔍 Add Context</button>
        <button 
          className="primary" 
          onClick={onGenerateResponse}
          disabled={isGenerating}
        >
          {isGenerating ? '🤖 Generating...' : '🤖 Generate Response'}
        </button>

        {conversation.length > 0 && (
          <div style={{ marginTop: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h4 style={{ color: 'var(--foreground)' }}>💬 Conversation</h4>
              <button 
                className="secondary" 
                onClick={onClearConversation} 
                style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}
              >
                Clear
              </button>
            </div>
            <div className={styles.messageList}>
              {conversation.map((msg, i) => (
                <div key={i} className={`${styles.message} ${styles[msg.role]}`}>
                  <p style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
