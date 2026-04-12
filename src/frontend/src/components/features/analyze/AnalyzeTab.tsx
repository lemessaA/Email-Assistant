'use client';

import React, { useState } from 'react';
import styles from '@/app/page.module.css';

export function AnalyzeTab() {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setFileName(file.name);
  };

  return (
    <div className="animate-fade-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h3>📊 Email Analysis</h3>
          <span className="badge badge-indigo">AI-Powered</span>
        </div>

        <div className="divider" />

        <p style={{ fontSize: '13px', color: '#4a5578', lineHeight: 1.7 }}>
          Upload an <code style={{ color: '#818cf8', background: 'rgba(99,102,241,0.1)', padding: '1px 5px', borderRadius: '4px' }}>.eml</code> file to extract insights, sentiment, and key information using AI analysis.
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
            padding: '2.5rem',
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
            const file = e.dataTransfer.files?.[0];
            if (file) setFileName(file.name);
          }}
        >
          <span style={{ fontSize: '2.5rem' }}>📧</span>
          {fileName ? (
            <>
              <p style={{ color: '#818cf8', fontWeight: 600, fontSize: '14px' }}>{fileName}</p>
              <p style={{ color: '#4a5578', fontSize: '12px' }}>File selected — ready to analyze</p>
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
          disabled={!fileName}
          style={{ width: 'max-content' }}
        >
          🔍 Analyze Email
        </button>
      </div>

      {/* Placeholder for results */}
      <div className={styles.card} style={{ opacity: fileName ? 1 : 0.4, pointerEvents: fileName ? 'auto' : 'none' }}>
        <div className={styles.cardHeader}>
          <h3>📈 Analysis Results</h3>
        </div>
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          color: '#4a5578',
          fontSize: '13px',
        }}>
          Results will appear here after analysis.
        </div>
      </div>
    </div>
  );
}
