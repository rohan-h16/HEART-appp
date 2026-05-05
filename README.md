# 💕 Heart Website — Deploy Guide

## Files in this folder
- `app.py`          → The full website + admin panel
- `requirements.txt`→ Python packages
- `Procfile`        → Tells Railway how to start the app

---

## 🔐 Change Your Admin Password (IMPORTANT!)
Open `app.py` and find these two lines near the top:

```python
ADMIN_USERNAME = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "love1234")
```

You will set these as secret environment variables on Railway (see Step 4).

---

## 🚀 Deploy to Railway (Free Hosting)

### Step 1 — Create a GitHub repo
1. Go to https://github.com and sign in (or create a free account)
2. Click **New repository** → name it `heart-website`
3. Set it to **Private** (so only you see the code)
4. Click **Create repository**
5. Upload all 3 files: `app.py`, `requirements.txt`, `Procfile`

### Step 2 — Sign up on Railway
1. Go to https://railway.app
2. Click **Login with GitHub**

### Step 3 — Deploy
1. On Railway dashboard click **New Project**
2. Choose **Deploy from GitHub repo**
3. Select your `heart-website` repo
4. Railway will auto-detect and deploy it ✅

### Step 4 — Set Secret Environment Variables
In Railway → your project → **Variables** tab, add:

| Variable      | Value              |
|---------------|--------------------|
| `ADMIN_USER`  | (your chosen username) |
| `ADMIN_PASS`  | (your chosen password) |
| `SECRET_KEY`  | (any random string, e.g. `xK9#mP2$love`) |

### Step 5 — Get your shareable link
Railway gives you a public URL like:
```
https://heart-website-production.up.railway.app
```
Share THIS link with anyone! 💕

---

## 👀 View Your Secret Name List
Go to:
```
https://your-railway-url.up.railway.app/admin
```
Login with your username & password → see every name + date/time.

---

## 🖥️ Run Locally in VS Code (for testing)
```bash
pip install flask gunicorn
python app.py
```
Then open: http://127.0.0.1:5000
Admin panel: http://127.0.0.1:5000/admin
Default login: admin / love1234
