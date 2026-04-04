'use client';

import { useState } from 'react';
import styles from './page.module.css';

import { AppConfig, ComposeState, Message, TabState, MODELS, TEMPLATES } from '@/types';
import { Sidebar } from '@/components/layout/Sidebar';
import { ComposeTab } from '@/components/features/compose/ComposeTab';
import { ProcessTab } from '@/components/features/process/ProcessTab';
import { AnalyzeTab } from '@/components/features/analyze/AnalyzeTab';
import { HistoryTab } from '@/components/features/history/HistoryTab';

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabState>('Compose');
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

  // Handlers
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
      const response = await fetch('http://localhost:8000/api/v1/email/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: composeState.subject || 'No Subject',
          body: composeState.body || 'Draft an email.',
          from_email: config.senderEmail || 'user@example.com',
          to_emails: composeState.to ? [composeState.to] : [],
          cc_emails: composeState.cc ? [composeState.cc] : [],
          priority: config.priority.toLowerCase(),
          metadata: { tone: config.tone }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to draft email');
      }

      const data = await response.json();
      
      setConversation((prev) => [
        ...prev,
        { role: 'assistant', content: data.draft || 'Unable to generate draft.' },
      ]);
      
      // Auto-fill body with the generated draft
      if (data.draft) {
        setComposeState(prev => ({ ...prev, body: data.draft }));
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
      const response = await fetch('http://localhost:8000/api/v1/email/send', {
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

  const clearConversation = () => {
    setConversation([]);
  };

  const clearAllData = () => {
    clearConversation();
    setComposeState({
      to: '',
      subject: '',
      cc: '',
      bcc: '',
      body: '',
    });
  };

  return (
    <div className={styles.container}>
      <Sidebar 
        config={config} 
        onConfigChange={handleConfigChange} 
        onClear={clearAllData} 
      />

      <main className={styles.mainContent}>
        <header className={styles.header}>
          <h1 className="animate-fade-in">🤖 Assist Me for My Email</h1>
          <p>Intelligent email processing powered by advanced AI</p>
        </header>

        <nav className={styles.tabs}>
          {(['Compose', 'Analyze', 'Process', 'History'] as TabState[]).map((tab) => (
            <button
              key={tab}
              className={`${styles.tab} ${activeTab === tab ? styles.active : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'Compose' && '📧 '}
              {tab === 'Analyze' && '📊 '}
              {tab === 'Process' && '🔄 '}
              {tab === 'History' && '📚 '}
              {tab}
            </button>
          ))}
        </nav>

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

      </main>
    </div>
  );
}
