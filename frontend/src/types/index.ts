export interface Message {
  role: string;
  content: string;
}

export interface AppConfig {
  senderEmail: string;
  model: string;
  tone: string;
  priority: string;
  autoRes: boolean;
  template: string;
}

export interface ComposeState {
  to: string;
  subject: string;
  cc: string;
  bcc: string;
  body: string;
}

export type TabState = 'Compose' | 'Analyze' | 'Process' | 'History';

export const MODELS = [
  'llama-3.1-8b-instant',
  'llama-3.1-70b-versatile',
  'llama-3.1-405b-instruct',
];

export const TONES = ['Formal', 'Professional', 'Casual', 'Friendly'];
export const PRIORITIES = ['Low', 'Normal', 'High', 'Urgent'];

export const TEMPLATES = {
  None: '',
  'Meeting Request': "I'd like to schedule a meeting to discuss...",
  'Follow-up': 'Just following up on our previous conversation...',
  'Information Request': 'Could you please provide more information about...',
  'Thank You': 'Thank you for your email and for...',
};
