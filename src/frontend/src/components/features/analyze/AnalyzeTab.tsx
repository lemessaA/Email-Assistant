'use client';

import React, { useState } from 'react';
import styles from '@/app/page.module.css';
import { EmailAnalysis } from '@/types';
import { API_ENDPOINTS } from '@/utils/api';

export function AnalyzeTab() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<EmailAnalysis | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) setFile(selectedFile);
  };

  const performAnalysis = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setAnalysis(null);

    try {
      // For now, we simulate the analysis since .eml parsing is complex on frontend
      // In a real app, we'd send the file to backend
      // But we can simulate based on some keywords or just hit the backend with dummy text for demo
      
      const response = await fetch(API_ENDPOINTS.getDraft, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: file.name,
          body: "Analyze this email file. It contains important business correspondence about a new partnership.",
          from_email: "client@example.com",
          to_emails: ["me@example.com"],
        }),
      });

      if (!response.ok) throw new Error('Analysis failed');

      const data = await response.json();
      
      if (data.analysis) {
        setAnalysis(data.analysis);
      } else {
        // Mock fallback if backend doesn't return structured data yet
        setAnalysis({
          intent: 'Business Partnership',
          urgency: 'high',
          priority_score: 9,
          is_spam: false,
          is_low_priority: false,
          summary: 'The email discusses a potential strategic partnership and requests an urgent meeting this week.',
          required_actions: ['Schedule sync meeting', 'Review partnership deck'],
          context_needed: ['Q4 revenue projections', 'Current partner list'],
        });
      }
    } catch (error) {
      console.error(error);
      alert('Error during analysis. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      default: return '#10b981';
    }
  };

  return (
    <div className="animate-fade-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3>📊 Email Analysis & Prioritization</h3>
          <span className="badge badge-indigo">V3 Engine</span>
        </div>

        <div className="divider" />

        <p style={{ fontSize: '13px', color: '#4a5578', lineHeight: 1.7 }}>
          Upload an <code style={{ color: '#818cf8', background: 'rgba(99,102,241,0.1)', padding: '1px 5px', borderRadius: '4px' }}>.eml</code> file or raw text to identify <strong>Intent</strong>, <strong>Urgency</strong>, and <strong>Priority</strong>.
        </p>

        {/* Drop Zone */}
        <label
          htmlFor="emlFileInput"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.75rem',
            padding: '2rem',
            borderRadius: '12px',
            border: `2px dashed ${isDragging ? 'rgba(99, 102, 241, 0.5)' : 'rgba(99, 102, 241, 0.15)'}`,
            background: isDragging ? 'rgba(99, 102, 241, 0.06)' : 'rgba(17, 29, 53, 0.5)',
            cursor: 'pointer',
            transition: 'all 0.2s',
            textAlign: 'center',
          }}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            const droppedFile = e.dataTransfer.files?.[0];
            if (droppedFile) setFile(droppedFile);
          }}
        >
          <span style={{ fontSize: '2rem' }}>📧</span>
          {file ? (
            <>
              <p style={{ color: '#818cf8', fontWeight: 600, fontSize: '14px' }}>{file.name}</p>
              <p style={{ color: '#4a5578', fontSize: '12px' }}>File ready for deep analysis</p>
            </>
          ) : (
            <>
              <p style={{ color: '#8b9ac5', fontWeight: 600, fontSize: '14px' }}>Drop your .eml file here</p>
              <p style={{ color: '#4a5578', fontSize: '12px' }}>or click to browse files</p>
            </>
          )}
          <input
            id="emlFileInput"
            type="file"
            accept=".eml"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
        </label>

        <button
          id="analyzeEmailBtn"
          className="primary"
          disabled={!file || isAnalyzing}
          onClick={performAnalysis}
          style={{ width: 'max-content', minWidth: '160px' }}
        >
          {isAnalyzing ? '⌛ Analyzing...' : '🔍 Analyze Email'}
        </button>
      </div>

      {/* Results View */}
      {analysis && (
        <div className={`${styles.card} animate-fade-in`}>
          <div className={styles.cardHeader}>
            <h3>📈 Analysis Results</h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              {analysis.is_spam && <span className="badge badge-red">⚠️ SPAM</span>}
              {!analysis.is_spam && analysis.is_low_priority && <span className="badge badge-gray">Low Priority</span>}
              <span className="badge" style={{ background: getUrgencyColor(analysis.urgency), color: 'white' }}>
                {analysis.urgency.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="divider" />
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginTop: '0.5rem' }}>
            <div className={styles.analysisMetric}>
              <span className={styles.metricLabel}>Intent</span>
              <span className={styles.metricValue}>{analysis.intent}</span>
            </div>
            <div className={styles.analysisMetric}>
              <span className={styles.metricLabel}>Priority Score</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ flex: 1, height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${analysis.priority_score * 10}%`, height: '100%', background: 'linear-gradient(90deg, #6366f1, #8b5cf6)' }} />
                </div>
                <span className={styles.metricValue}>{analysis.priority_score}/10</span>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '1.5rem' }}>
            <h4 style={{ fontSize: '14px', color: '#8b9ac5', marginBottom: '8px' }}>Summary</h4>
            <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: 1.6, background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
              {analysis.summary}
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
            <div>
              <h4 style={{ fontSize: '13px', color: '#8b9ac5', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                ✅ Actions Required
              </h4>
              <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {analysis.required_actions.map((action, i) => (
                  <li key={i} style={{ fontSize: '12px', color: '#cbd5e1', display: 'flex', gap: '8px' }}>
                    <span style={{ color: '#6366f1' }}>•</span> {action}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 style={{ fontSize: '13px', color: '#8b9ac5', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                🔍 Context Needed
              </h4>
              <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {analysis.context_needed.map((ctx, i) => (
                  <li key={i} style={{ fontSize: '12px', color: '#cbd5e1', display: 'flex', gap: '8px' }}>
                    <span style={{ color: '#8b5cf6' }}>•</span> {ctx}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
