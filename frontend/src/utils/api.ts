/**
 * API Configuration
 * Fallback to localhost if NEXT_PUBLIC_API_URL is not set
 */
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  getDraft: `${API_BASE_URL}/api/v1/email/draft`,
  sendEmail: `${API_BASE_URL}/api/v1/email/send`,
  getSettings: `${API_BASE_URL}/api/v1/settings/`,
  getUnread: `${API_BASE_URL}/api/v1/email/emails/unread`,
};
