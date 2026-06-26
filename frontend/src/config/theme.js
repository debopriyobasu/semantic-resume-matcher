// Centralized application theme and metadata configuration
export const APP_CONFIG = {
  name: "Semantic Resume Matcher",
  version: "1.1.0",
  description: "Enterprise-grade, local & offline resume-to-job matching system",
  pollingIntervalMs: 3000,
  dashboardRefreshIntervalMs: 10000,
};

export const COLORS = {
  primary: {
    gradientStart: 'hsl(245, 85%, 65%)', // Electric Indigo
    gradientEnd: 'hsl(185, 80%, 55%)',   // Cyan
  },
  success: 'hsl(152, 70%, 50%)',         // Emerald Green
  warning: 'hsl(38, 95%, 55%)',          // Amber
  error: 'hsl(0, 80%, 60%)',             // Coral Red
  neutral: {
    text: 'hsl(210, 40%, 98%)',
    textSecondary: 'hsl(215, 20%, 75%)',
    bg: 'hsl(222, 47%, 11%)',
    cardBg: 'rgba(30, 41, 59, 0.4)',
    border: 'rgba(255, 255, 255, 0.08)',
  }
};
