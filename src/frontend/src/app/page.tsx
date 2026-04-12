'use client';

import { useState } from 'react';
import styles from './page.module.css';

import { AppConfig, ComposeState, Message, TabState, MODELS, TEMPLATES } from '@/types';
import { Sidebar } from '@/components/layout/Sidebar';
import { ComposeTab } from '@/components/features/compose/ComposeTab';
import { ProcessTab } from '@/components/features/process/ProcessTab';
import { AnalyzeTab } from '@/components/features/analyze/AnalyzeTab';
import { HistoryTab } from '@/components/features/history/HistoryTab';
import { API_ENDPOINTS } from '@/utils/api';

const TAB_ICONS: Record<string, string> = {
  Compose: '✏️',
  Analyze: '📊',
  Process: '⚡',
  History: '🕓',
};

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabState>('Compose');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [config, setConfig] = useState<AppConfig>({
    senderEmail: '',
    model: MODELS[0],
    tone: 'Professional',
    priority: 'Normal',
    autoRes: false,
    template: 'None',
  });

  const [composeState, setComposeState] = useState<ComposeState>({
    to: '',
    subject: '',
    cc: '',
    bcc: '',
    body: '',
  });

  const [conversation, setConversation] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const handleConfigChange = (key: keyof AppConfig, value: any) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
    if (key === 'template') {
      setComposeState((prev) => ({
        ...prev,
        body: TEMPLATES[value as keyof typeof TEMPLATES] || '',
      }));
    }
  };

  const handleComposeChange = (key: keyof ComposeState, value: string) => {
    setComposeState((prev) => ({ ...prev, [key]: value }));
  };

  const generateResponse = async () => {
    if (!composeState.subject && !composeState.body) return;

    setConversation((prev) => [
      ...prev,
      { role: 'user', content: `Draft an email to ${composeState.to || '[recipient]'} about ${composeState.subject || '[subject]'} with tone ${config.tone}.` },
    ]);

    setIsGenerating(true);
    try {
      const response = await fetch(API_ENDPOINTS.getDraft, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: composeState.subject || 'No Subject',
          body: composeState.body || 'Draft an email.',
          from_email: config.senderEmail || 'user@example.com',
          to_emails: composeState.to ? [composeState.to] : [],
          cc_emails: composeState.cc ? [composeState.cc] : [],
          priority: config.priority.toLowerCase(),
          metadata: { tone: config.tone },
        }),
      });

      if (!response.ok) throw new Error('Failed to draft email');

      const data = await response.json();

      setConversation((prev) => [
        ...prev,
        { role: 'assistant', content: data.draft || 'Unable to generate draft.' },
      ]);

      if (data.draft) {
        setComposeState((prev) => ({ ...prev, body: data.draft }));
      }
    } catch (error) {
      console.error(error);
      setConversation((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${error}` },
      ]);
    } finally {
      setIsGenerating(false);
    }
  };

  const sendEmail = async () => {
    if (!composeState.to || !composeState.subject || !composeState.body) {
      alert("Please fill 'To', 'Subject', and 'Body' fields.");
      return;
    }

    setIsSending(true);
    try {
      const response = await fetch(API_ENDPOINTS.sendEmail, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: composeState.subject,
          body: composeState.body,
          from_email: config.senderEmail || 'user@example.com',
          to_emails: [composeState.to],
          cc_emails: composeState.cc ? [composeState.cc] : [],
          priority: config.priority.toLowerCase(),
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to send email');
      }

      alert('Email sent successfully!');
      clearAllData();
    } catch (error: any) {
      alert('Error sending email: ' + error.message);
    } finally {
      setIsSending(false);
    }
  };

  const clearConversation = () => setConversation([]);

  const clearAllData = () => {
    clearConversation();
    setComposeState({ to: '', subject: '', cc: '', bcc: '', body: '' });
  };

  return (
    <div className={styles.container}>
      {/* Mobile overlay */}
      <div
        className={`${styles.sidebarOverlay} ${sidebarOpen ? styles.visible : ''}`}
        onClick={() => setSidebarOpen(false)}
        aria-hidden="true"
      />

      <Sidebar
        config={config}
        onConfigChange={handleConfigChange}
        onClear={clearAllData}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className={styles.mainContent}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerInner}>
            {/* Hamburger — mobile only */}
            <button
              id="sidebarToggle"
              className={styles.hamburger}
              onClick={() => setSidebarOpen((o) => !o)}
              aria-label="Toggle sidebar"
            >
              ☰
            </button>

            <div className={styles.headerLeft}>
              <h1>AI Email Assistant</h1>
              <p>Intelligent email processing powered by advanced language models</p>
            </div>
            <div className={styles.headerRight}>
              <div className={styles.statusPill}>
                <span className={styles.statusDot} />
                System Online
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className={styles.tabs}>
          {(['Compose', 'Analyze', 'Process', 'History'] as TabState[]).map((tab) => (
            <button
              key={tab}
              id={`tab-${tab.toLowerCase()}`}
              className={`${styles.tab} ${activeTab === tab ? styles.active : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              <span className={styles.tabIcon}>{TAB_ICONS[tab]}</span>
              {tab}
            </button>
          ))}
        </nav>

        {/* Tab Content */}
        <div className={styles.contentArea}>
          {activeTab === 'Compose' && (
            <ComposeTab
              state={composeState}
              onChange={handleComposeChange}
              conversation={conversation}
              onGenerateResponse={generateResponse}
              onClearConversation={clearConversation}
              onSendEmail={sendEmail}
              isGenerating={isGenerating}
              isSending={isSending}
            />
          )}

          {activeTab === 'Process' && <ProcessTab />}
          {activeTab === 'Analyze' && <AnalyzeTab />}
          {activeTab === 'History' && <HistoryTab />}
        </div>
      </main>
    </div>
  );
}

