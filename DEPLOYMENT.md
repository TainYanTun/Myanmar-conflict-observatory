# Deployment Guide: Myanmar Conflict Observatory (MCO)

This document provides technical instructions for deploying the MCO framework to production cloud environments. The system is designed to run as a multi-container architecture using **Docker** and **PostgreSQL**.

---

## 🚀 Deployment Options

### Option A: Railway.app (Recommended / Easiest)
Railway is ideal for this project because it natively supports `docker-compose.yml`.

1.  **Connect GitHub:** Link your repository to Railway.
2.  **Automatic Detection:** Railway will detect the `docker-compose.yml` and provision both the **Streamlit App** and the **PostgreSQL Database**.
3.  **Environment Variables:** Add the following keys in the Railway "Variables" tab:
    - `ACLED_EMAIL`
    - `ACLED_PASSWORD`
    - `POSTGRES_USER`
    - `POSTGRES_PASSWORD`
    - `POSTGRES_DB`
4.  **Networking:** Railway automatically handles the internal DNS so `app` can talk to `db`.

### Option B: Render.com
Render is excellent for a split-service architecture (Web + Managed DB).

1.  **New PostgreSQL:** Create a "Managed PostgreSQL" instance first. Copy the **Internal Database URL**.
2.  **New Web Service:** Create a "Web Service" pointing to your repository.
3.  **Docker Command:** Select "Docker" as the runtime.
4.  **Environment Variables:**
    - Set `DB_URL` to the Internal Database URL copied in step 1.
    - Set `ACLED_EMAIL` and `ACLED_PASSWORD`.
5.  **Health Check:** Set the health check path to `/_stcore/health`.

---

## 🔐 Security & Secrets

**CRITICAL:** Never commit your `.env` file. In a production environment:
- Use the cloud provider's **Secret Manager** or **Environment Variables** UI.
- The `startup.sh` script is designed to fail gracefully if `ACLED` credentials are missing, falling back to local CSV if available.

---

## 💾 Data Persistence & Sync

### 1. Database Volume
In `docker-compose.yml`, we use:
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```
If you are deploying to a VPS (DigitalOcean Droplet, AWS EC2), ensure this volume is backed up. On managed platforms like Render/Railway, the database persistence is handled by the provider.

### 2. API Rate Limiting
The current `startup.sh` runs `update_data.py` on every boot. 
- **Recommendation:** If deploying on a platform that puts apps to "sleep" (like Render Free Tier), move the data update to a **Cron Job** (Scheduled Task) to run once every 24 hours to avoid hitting ACLED API rate limits.

---

## 🛠 Troubleshooting Production

### Port Mapping
Streamlit defaults to `8501`. Our `Dockerfile` is configured to expose this port. If your cloud provider uses a dynamic `$PORT`, the `STREAMLIT_SERVER_PORT` environment variable in the `Dockerfile` will ensure compatibility.

### Database Connection Issues
If the app cannot find the database:
1. Verify the `DB_URL` follows the format: `postgresql://user:password@hostname:5432/dbname`.
2. Ensure the `db` service has finished its health check before the `app` service starts (handled automatically by our `depends_on` logic in `docker-compose.yml`).

---

## 📈 Scalability Roadmap
For larger deployments:
1. **Redis Caching:** Use Redis to store Streamlit session state for multiple concurrent users.
2. **Read-Replicas:** Use a read-replica database if geospatial query volume becomes high.
3. **S3 Storage:** Move archived CSVs from `data/` to an S3 bucket for long-term audit logs.
