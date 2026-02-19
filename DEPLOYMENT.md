# 🚀 KPGU Chatbot Deployment Guide

To make your chatbot work on mobile and the public internet, you need to host both the **Brain (Backend)** and the **Face (Frontend)** online.

## Part 1: Deploy Backend (The Brain) to Render

1.  **Sign Up**: Go to [render.com](https://render.com) and sign up with GitHub.
2.  **New Web Service**:
    *   Click **New +** -> **Web Service**.
    *   Select "Build and deploy from a Git repository".
    *   Connect your GitHub repo: `krunalsakpal679-hue/college-chatbot`.
3.  **Configure**:
    *   **Name**: `kpgu-backend`
    *   **Root Directory**: `backend` (Important!)
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
    *   **Environment Variables** (Add these):
        *   `GOOGLE_API_KEY`: (Paste your Gemini Key here)
        *   `SECRET_KEY`: `any-random-string-here`
        *   `PYTHON_VERSION`: `3.11.0` (Optional, good for stability)
4.  **Deploy**: Click "Create Web Service".
5.  **Copy URL**: Once live, copy the URL (e.g., `https://kpgu-backend.onrender.com`).

---

## Part 2: Connect Frontend (The Face) on Vercel

1.  **Go to Vercel Dashboard**: Open your existing project.
2.  **Settings** -> **Environment Variables**.
3.  **Add New Variable**:
    *   **Key**: `VITE_API_URL`
    *   **Value**: `https://<YOUR-RENDER-URL>.onrender.com/api/v1/chat`
    *   *(Make sure to add `/api/v1/chat` at the end!)*
4.  **Redeploy**:
    *   Go to **Deployments** tab.
    *   Click the **3 dots** on the latest deployment -> **Redeploy**.

## ✅ Done!
Now checking your Vercel app on mobile should work perfectly because it talks to the online Render backend instead of your laptop.
