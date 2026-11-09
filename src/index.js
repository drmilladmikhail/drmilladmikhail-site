const JSON_HEADERS = { "content-type": "application/json; charset=utf-8" };

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...JSON_HEADERS, ...headers },
  });
}

function allowedOrigin(request, env) {
  const origin = request.headers.get("Origin");
  const allowed = (env.ALLOWED_ORIGINS || "https://drmilladmikhail.com,https://www.drmilladmikhail.com")
    .split(",").map((value) => value.trim()).filter(Boolean);
  return origin && allowed.includes(origin) ? origin : null;
}

function corsHeaders(request, env) {
  const origin = allowedOrigin(request, env);
  return origin ? {
    "access-control-allow-origin": origin,
    "access-control-allow-methods": "GET,POST,PATCH,OPTIONS",
    "access-control-allow-headers": "Content-Type,Authorization",
    "access-control-max-age": "86400",
    "vary": "Origin",
  } : {};
}

async function authorized(request, env) {
  const supplied = request.headers.get("Authorization") || "";
  if (!env.ADMIN_API_KEY || !supplied.startsWith("Bearer ")) return false;
  const candidate = supplied.slice(7);
  const encoder = new TextEncoder();
  const [a, b] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(candidate)),
    crypto.subtle.digest("SHA-256", encoder.encode(env.ADMIN_API_KEY)),
  ]);
  const x = new Uint8Array(a);
  const y = new Uint8Array(b);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

function validCertificateNumber(value) {
  return /^DMMA-20\d{2}-\d{4}$/.test(value);
}

export default {
  async fetch(request, env) {
    const cors = corsHeaders(request, env);
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      if (!allowedOrigin(request, env)) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: cors });
    }

    if (!url.pathname.startsWith("/api/")) return json({ error: "Not found" }, 404, cors);

    try {
      const publicMatch = url.pathname.match(/^\/api\/certificates\/([^/]+)$/);
      if (request.method === "GET" && publicMatch) {
        const number = decodeURIComponent(publicMatch[1]).toUpperCase();
        if (!validCertificateNumber(number)) return json({ error: "Invalid certificate number" }, 400, cors);
        const record = await env.DB.prepare(
          "SELECT certificate_number, recipient_name, course_title, issue_date, status, hours FROM certificates WHERE certificate_number = ?"
        ).bind(number).first();

        if (!record) return json({ status: "not_found" }, 404, cors);
        return json({
          status: record.status === "revoked" ? "revoked" : "valid",
          certificateNumber: record.certificate_number,
          recipientName: record.recipient_name,
          courseTitle: record.course_title,
          issueDate: record.issue_date,
          hours: record.hours,
          issuer: "Dr. Millad Mikhail Mental Health Academy",
          notice: "Verification confirms issuance by the Academy only; it does not represent academic or professional accreditation.",
        }, 200, cors);
      }

      if (url.pathname === "/api/admin/certificates" && request.method === "POST") {
        if (!(await authorized(request, env))) return json({ error: "Unauthorized" }, 401, cors);
        const body = await request.json();
        const number = String(body.certificateNumber || "").trim().toUpperCase();
        const recipient = String(body.recipientName || "").trim();
        const course = String(body.courseTitle || "").trim();
        const issueDate = String(body.issueDate || "").trim();
        const hours = body.hours == null || body.hours === "" ? null : Number(body.hours);

        if (!validCertificateNumber(number) || !recipient || !course || !/^\d{4}-\d{2}-\d{2}$/.test(issueDate)) {
          return json({ error: "Provide a valid certificateNumber, recipientName, courseTitle and YYYY-MM-DD issueDate." }, 400, cors);
        }
        if (recipient.length > 120 || course.length > 180 || (hours !== null && (!Number.isFinite(hours) || hours < 0 || hours > 1000))) {
          return json({ error: "One or more fields exceed allowed limits." }, 400, cors);
        }

        try {
          await env.DB.prepare(
            "INSERT INTO certificates (certificate_number, recipient_name, course_title, issue_date, status, hours) VALUES (?, ?, ?, ?, 'valid', ?)"
          ).bind(number, recipient, course, issueDate, hours).run();
        } catch {
          return json({ error: "Certificate number already exists or the record could not be saved." }, 409, cors);
        }
        return json({ success: true, certificateNumber: number }, 201, cors);
      }

      const revokeMatch = url.pathname.match(/^\/api\/admin\/certificates\/([^/]+)\/revoke$/);
      if (request.method === "PATCH" && revokeMatch) {
        if (!(await authorized(request, env))) return json({ error: "Unauthorized" }, 401, cors);
        const number = decodeURIComponent(revokeMatch[1]).toUpperCase();
        if (!validCertificateNumber(number)) return json({ error: "Invalid certificate number" }, 400, cors);
        const result = await env.DB.prepare(
          "UPDATE certificates SET status = 'revoked', revoked_at = CURRENT_TIMESTAMP WHERE certificate_number = ? AND status = 'valid'"
        ).bind(number).run();
        if (!result.meta.changes) return json({ error: "Certificate not found or already revoked." }, 404, cors);
        return json({ success: true, certificateNumber: number, status: "revoked" }, 200, cors);
      }

      return json({ error: "Not found" }, 404, cors);
    } catch {
      return json({ error: "The request could not be completed." }, 500, cors);
    }
  },
};
