CREATE TABLE IF NOT EXISTS certificates (
  certificate_number TEXT PRIMARY KEY,
  recipient_name TEXT NOT NULL,
  course_title TEXT NOT NULL,
  issue_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'valid' CHECK (status IN ('valid', 'revoked')),
  hours REAL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  revoked_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_certificates_status
ON certificates(status);
