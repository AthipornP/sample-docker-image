// Simple in-memory session store for demo (not for production)
const sessions = {};

export function setSession(sid, data) {
  sessions[sid] = data;
}

export function getSession(sid) {
  return sessions[sid];
}

export function clearSession(sid) {
  delete sessions[sid];
}
