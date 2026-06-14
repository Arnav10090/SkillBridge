# SkillBridge — Keep-Alive Setup

Render's **free tier** spins down web services after **15 minutes of inactivity**.
When the first request arrives afterward, the service cold-starts (30–60 s delay),
which causes the frontend to appear broken.

This document explains how to keep the backend awake **for free** using an
external HTTP scheduler — no backend code changes, no cron inside Render.

---

## Architecture Overview

```
cron-job.org (or UptimeRobot)
        │
        │  GET /api/health   every 10 min
        │
        ▼
https://<your-service>.onrender.com
        │
        │  instant 200 OK  {"status":"ok", "timestamp":"..."}
        │
        ▼
   Render keeps the dyno alive
```

The external scheduler runs **outside** the Render service. Even when the
backend is sleeping it can receive incoming HTTP connections — the ping itself
wakes it up, and subsequent user requests find it already warm.

---

## Deployment Details

| Item | Value |
|---|---|
| Backend platform | Render Web Service (free tier) |
| Backend service name | `skillbridge-api` |
| Backend region | Oregon (`us-west-2`) |
| Backend URL | `https://<your-service-name>.onrender.com` |
| Health endpoint | `GET https://<your-service-name>.onrender.com/api/health` |
| Expected response | `{"status":"ok","timestamp":"<ISO_TIMESTAMP>"}` |
| Expected HTTP status | `200 OK` |
| Frontend platform | Vercel |
| Frontend environment var | `VITE_API_URL=https://<your-service-name>.onrender.com` |

> **Replace `<your-service-name>`** with the actual subdomain shown in your
> Render dashboard (e.g., `skillbridge-api-abc1.onrender.com`).

---

## Option A — cron-job.org (Preferred, 100% Free)

### Why this is preferred
- Completely free, no credit card
- Up to 5-minute granularity on free plan (10-minute works fine)
- Simple HTTP GET — no account upgrade needed
- Reliable uptime history visible in dashboard

### Setup Steps

1. **Create a free account** at [https://cron-job.org](https://cron-job.org)

2. **Create a new cron job** — click *"Create cronjob"*

3. **Fill in the form:**

   | Field | Value |
   |---|---|
   | Title | `SkillBridge Keep-Alive` |
   | URL | `https://<your-service-name>.onrender.com/api/health` |
   | Request method | `GET` |
   | Schedule | Every 10 minutes (see below) |
   | Enable | ✅ Yes |
   | Notifications on failure | ✅ Recommended — enter your email |

4. **Set the schedule** (custom cron expression):
   ```
   */10 * * * *
   ```
   *(Every 10 minutes, 24 × 7)*

5. **Save** the cron job.

6. **Verify**: Wait 10 minutes, then check the *"History"* tab — you should
   see green `200` entries.

### Screenshot reference
- Dashboard → "Cronjobs" → "Create cronjob"
- In the schedule section, select "Custom" and enter `*/10 * * * *`

---

## Option B — UptimeRobot (Free, 5-minute intervals)

### Why this is an alternative
- Free plan supports 50 monitors at 5-minute intervals
- Sends alerts by email/Slack when the service goes down
- Good if you also want uptime monitoring as a bonus

### Setup Steps

1. **Create a free account** at [https://uptimerobot.com](https://uptimerobot.com)

2. **Add a new monitor** — click *"Add New Monitor"*

3. **Fill in the form:**

   | Field | Value |
   |---|---|
   | Monitor Type | `HTTP(s)` |
   | Friendly Name | `SkillBridge API Health` |
   | URL | `https://<your-service-name>.onrender.com/api/health` |
   | Monitoring Interval | `5 minutes` |
   | HTTP Method | `GET` (default) |
   | Alert Contacts | Add your email |

4. **Click "Create Monitor".**

5. **Verify**: The monitor should show "Up" status within 5 minutes.
   The first check may show "New" briefly — that is normal.

---

## Verification Steps

### 1. Manual verification (curl)
```bash
curl -v https://<your-service-name>.onrender.com/api/health
```

Expected output:
```
HTTP/2 200
content-type: application/json

{"status":"ok","timestamp":"2025-01-01T12:00:00.000000+00:00"}
```

### 2. Using the health check script
```bash
# Set your backend URL
export BACKEND_URL=https://<your-service-name>.onrender.com

# Run the check
bash scripts/check-health.sh
```

Expected output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SkillBridge — Backend Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Endpoint : https://<your-service-name>.onrender.com/api/health
  Timeout  : 15s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  HTTP Status : 200
  Response    : {"status":"ok","timestamp":"..."}

✓ HEALTHY — backend is awake and responding correctly.
```

### 3. Checking scheduler history
- **cron-job.org**: Dashboard → Cronjobs → click your job → History tab
- **UptimeRobot**: Dashboard → click your monitor → Response Time graph

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `curl: (6) Could not resolve host` | Wrong URL / typo | Copy URL from Render dashboard |
| HTTP 502 / 503 | Service is cold-starting | Wait 60 s and retry; the scheduler will also retry |
| HTTP 404 | Old deploy without `/api/health` | Redeploy after merging this change |
| HTTP 200 but body is wrong | Cached old response | Hard-refresh or try incognito |
| cron-job.org shows "Failed" | Network timeout during cold start | Increase the timeout in cron-job.org settings to 30 s |
| Render still sleeping | Scheduler interval too long | Confirm interval is ≤ 14 minutes |

---

## Environment Variables Reference

### Backend (set in Render dashboard → Environment)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string (or SQLite for local) |
| `LLM_PROVIDER` | Yes | `groq` or `ollama` |
| `GROQ_API_KEY` | If using Groq | Your Groq API key |
| `GROQ_MODEL` | Optional | Default: `llama-3.1-8b-instant` |
| `SECRET_KEY` | Yes | Random secret for security |

### Frontend (set in Vercel dashboard → Settings → Environment Variables)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | Yes | Full URL of Render backend (no trailing slash) |

Example:
```
VITE_API_URL=https://skillbridge-api-abc1.onrender.com
```

> ⚠️ **Do not** add `VITE_` prefix to secret variables — they are embedded in
> the browser bundle and visible to anyone.

---

## Deployment Checklist

- [ ] Backend deployed to Render and health endpoint returns 200:
      `curl https://<service>.onrender.com/api/health`
- [ ] Frontend deployed to Vercel with `VITE_API_URL` set to Render URL
- [ ] cron-job.org job created with `*/10 * * * *` schedule pointing to
      `https://<service>.onrender.com/api/health`
- [ ] (Optional) UptimeRobot monitor created as a backup alerting layer
- [ ] First scheduler execution confirmed green in history tab
- [ ] End-to-end test: upload resume + JD via live frontend → results appear
