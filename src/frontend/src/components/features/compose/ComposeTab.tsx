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
    <div className={`${styles.grid} animate-fade-up`}>
      {/* Left — Compose Form */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3>✏️ Compose Email</h3>
          <span className="badge badge-indigo">New Message</span>
        </div>

        <div className="divider" style={{ margin: '0 0 0.25rem' }} />

        <div className={styles.formGroup}>
          <label className="form-label">To</label>
          <input
            id="compose-to"
            type="email"
            placeholder="recipient@example.com"
            value={state.to}
            onChange={(e) => onChange('to', e.target.value)}
          />
        </div>

        <div className={styles.formGroup}>
          <label className="form-label">Subject</label>
          <input
            id="compose-subject"
            type="text"
            placeholder="What's this email about?"
            value={state.subject}
            onChange={(e) => onChange('subject', e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <div className={styles.formGroup} style={{ flex: 1 }}>
            <label className="form-label">CC</label>
            <input
              id="compose-cc"
              type="text"
              placeholder="cc@example.com"
              value={state.cc}
              onChange={(e) => onChange('cc', e.target.value)}
            />
          </div>
          <div className={styles.formGroup} style={{ flex: 1 }}>
            <label className="form-label">BCC</label>
            <input
              id="compose-bcc"
              type="text"
              placeholder="bcc@example.com"
              value={state.bcc}
              onChange={(e) => onChange('bcc', e.target.value)}
            />
          </div>
        </div>

        <div className={styles.formGroup} style={{ flex: 1 }}>
          <label className="form-label">Email Body</label>
          <textarea
            id="compose-body"
            rows={10}
            placeholder="Start writing your email here, or use the AI assistant to generate a draft..."
            value={state.body}
            onChange={(e) => onChange('body', e.target.value)}
            style={{ resize: 'vertical', minHeight: '180px' }}
          />
        </div>

        <div className={styles.cardActions}>
          <button
            id="sendEmailBtn"
            className="primary"
            style={{ flex: 1 }}
            onClick={onSendEmail}
            disabled={isSending}
          >
            {isSending ? (
              <><span className="spinner" /> Sending…</>
            ) : (
              <>📤 Send Email</>
            )}
          </button>
          <button id="saveDraftBtn" className="secondary" style={{ flex: 1 }}>
            💾 Save Draft
          </button>
        </div>
      </div>

      {/* Right — AI Panel */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3>🤖 AI Assistant</h3>
          <span className="badge badge-indigo">GPT-Powered</span>
        </div>

        <div className="divider" style={{ margin: '0 0 0.25rem' }} />

        <p style={{ fontSize: '12px', color: '#4a5578', lineHeight: 1.7 }}>
          Use AI tools to improve, generate, or analyse your email content.
        </p>

        <div className={styles.buttonGrid}>
          <button id="improveToneBtn" className="secondary">✨ Improve Tone</button>
          <button id="checkGrammarBtn" className="secondary">📝 Check Grammar</button>
        </div>

        <button id="addContextBtn" className="secondary" style={{ width: '100%' }}>
          🔍 Add Context
        </button>

        <button
          id="generateResponseBtn"
          className="primary"
          style={{ width: '100%' }}
          onClick={onGenerateResponse}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <><span className="spinner" /> Generating…</>
          ) : (
            <>🤖 Generate Draft</>
          )}
        </button>

        {/* Conversation History */}
        {conversation.length > 0 && (
          <div style={{ marginTop: '0.5rem', flex: 1, minHeight: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <p className="section-title" style={{ marginBottom: 0 }}>💬 Conversation</p>
              <button
                id="clearConversationBtn"
                className="secondary"
                onClick={onClearConversation}
                style={{ padding: '0.25rem 0.65rem', fontSize: '11px' }}
              >
                Clear
              </button>
            </div>
            <div className={styles.messageList}>
              {conversation.map((msg, i) => (
                <div
                  key={i}
                  className={`${styles.message} ${styles[msg.role]}`}
                  style={{ animationDelay: `${i * 0.05}s` }}
                >
                  <p style={{ whiteSpace: 'pre-wrap', fontSize: '13px', lineHeight: 1.65 }}>{msg.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
