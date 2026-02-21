# 🚀 KPGU Chatbot Deployment Guide

Follow these steps to put your chatbot online for everyone to use.

## Part 1: Deploy Backend to Render

1.  **Preparation**: Make sure you have pushed the latest code (including the `runtime.txt` and `backend/data/` folder) to your GitHub.
2.  **Create Web Service**:
    *   Go to [Render.com](https://render.com) -> **New +** -> **Web Service**.
    *   Connect your repository: `krunalsakpal679-hue/college-chatbot`.
3.  **Configure Settings**:
    *   **Name**: `kpgu-chatbot-backend`
    *   **Root Directory**: `backend` (⚠️ **CRITICAL: Do not forget this!**)
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
4.  **Add Environment Variables**:
    *   Click **Advanced** -> **Add Environment Variable**:
        *   `GOOGLE_API_KEY`: (Your Gemini Key)
        *   `SECRET_KEY`: (Any random text like `kpgu-secret-123`)
        *   `PYTHON_VERSION`: `3.11.9`
5.  **🚀 The Most Important Step**:
    *   If you already tried to deploy and it failed, click the **Manual Deploy** button on your dashboard and select **"Clear Build Cache & Deploy"**. 
    *   This ensures the server downloads my new fixes (like the `SECRET_KEY` fix).

## Part 2: Deploy Frontend to Vercel

1.  **Preparation**: Push your latest code to GitHub.
2.  **Create Project**:
    *   Go to [Vercel.com](https://vercel.com) and click **"Add New"** -> **"Project"**.
    *   Import your repository: `krunalsakpal679-hue/college-chatbot`.
3.  **Configure Project Settings**:
    *   **Framework Preset**: `Vite`.
    *   **Root Directory**: `frontend`.
    *   **Build Command**: `npm run build`
    *   **Output Directory**: `dist`
4.  **Add Environment Variables**:
    *   Go to **Settings** -> **Environment Variables**.
    *   Add:
        *   **Key**: `VITE_API_URL`
        *   **Value**: `https://college-chatbot-backend-5o9u.onrender.com/api/v1/chat`
5.  **Deploy**:
    *   Go to the **Deployments** tab.
    *   Click **"Redeploy"** on the latest item.

✅ **Success!** Your KPGU Chatbot is now fully live. The Vercel frontend will talk to the Render backend, providing accurate college information from your database.
