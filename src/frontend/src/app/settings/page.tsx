'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { API_ENDPOINTS } from '@/utils/api';

export default function SettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formConfig, setFormConfig] = useState({
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    imap_server: '',
    imap_port: 993,
    email_user: '',
    email_password: ''
  });
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  useEffect(() => {
    // Fetch settings on load
    fetch(API_ENDPOINTS.getSettings)
      .then(res => res.json())
      .then(data => {
        setFormConfig({
          smtp_host: data.smtp_host || '',
          smtp_port: data.smtp_port || 587,
          smtp_username: data.smtp_username || '',
          smtp_password: data.smtp_password || '',
          imap_server: data.imap_server || '',
          imap_port: data.imap_port || 993,
          email_user: data.email_user || '',
          email_password: data.email_password || ''
        });
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormConfig(prev => ({
      ...prev,
      [name]: type === 'number' ? parseInt(value) || '' : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      const res = await fetch(API_ENDPOINTS.getSettings, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formConfig)
      });
      const data = await res.json();
      if (res.ok) {
        setMessage({ type: 'success', text: 'Settings saved successfully. It will now override defaults.' });
      } else {
        throw new Error(data.detail || 'Failed to save settings');
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-black flex items-center justify-center text-white">Loading configuration...</div>;
  }

  return (
    <main className="min-h-screen bg-black text-gray-100 font-sans p-6 md:p-12">
      <div className="max-w-3xl mx-auto">
        <div className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500 font-heading">Preferences</h1>
            <p className="text-gray-400 mt-2">Manage your email configuration dynamically</p>
          </div>
          <Link href="/" className="px-4 py-2 border border-gray-700 bg-gray-900 rounded-lg hover:border-blue-500 hover:text-white transition-all text-sm shadow-sm hover:shadow-blue-900/40">
            &larr; Back to Dashboard
          </Link>
        </div>

        {message && (
          <div className={`p-4 mb-6 rounded-lg ${message.type === 'success' ? 'bg-green-900/30 border border-green-800 text-green-300' : 'bg-red-900/30 border border-red-800 text-red-300'}`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8 bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-2xl">
          {/* SMTP Config */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold border-b border-gray-800 pb-2 text-white">SMTP (Outgoing Mail)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Host</label>
                <input name="smtp_host" value={formConfig.smtp_host} onChange={handleChange} className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. smtp.gmail.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Port</label>
                <input name="smtp_port" type="number" value={formConfig.smtp_port} onChange={handleChange} className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Username</label>
                <input name="smtp_username" value={formConfig.smtp_username} onChange={handleChange} className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. user@gmail.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Password / App Password</label>
                <input name="smtp_password" type="password" value={formConfig.smtp_password} onChange={handleChange} className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="••••••••" />
              </div>
            </div>
          </div>

          {/* IMAP Config */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold border-b border-gray-800 pb-2 text-white mt-10">IMAP (Incoming Mail)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Server</label>
                <input name="imap_server" value={formConfig.imap_server} onChange={handleChange} className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. imap.gmail.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Port</label>
                <input name="imap_port" type="number" value={formConfig.imap_port} onChange={handleChange} className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Email Address</label>
                <input name="email_user" value={formConfig.email_user} onChange={handleChange} className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. user@gmail.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Password / App Password</label>
                <input name="email_password" type="password" value={formConfig.email_password} onChange={handleChange} className="w-full bg-black border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="••••••••" />
              </div>
            </div>
          </div>

          <div className="pt-6 flex justify-end">
            <button type="submit" disabled={saving} className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium py-3 px-8 rounded-lg shadow-lg shadow-blue-500/30 transition-all disabled:opacity-50">
              {saving ? 'Saving configuration...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
