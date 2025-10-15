const SESSION_KEY = 'ecommerce_session_id';

export const sessionManager = {
  getSessionId(): string {
    let sessionId = localStorage.getItem(SESSION_KEY);

    if (!sessionId) {
      sessionId = crypto.randomUUID();
      localStorage.setItem(SESSION_KEY, sessionId);
    }

    return sessionId;
  },

  clearSession(): void {
    localStorage.removeItem(SESSION_KEY);
  },
};
