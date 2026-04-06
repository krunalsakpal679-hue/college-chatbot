# KPGU AI Assistant - Setup & Startup Guide

This folder contains the complete, redesigned KPGU Chatbot system with the Master Dataset.

## 🚀 Quick Start (One-Click)
Double-click the **`START_KPGU_BOT.bat`** file in this folder. It will:
1.  Open two terminal windows.
2.  Install all required libraries automatically.
3.  Start the Backend (Port 8000).
4.  Start the Frontend (Port 5175).

---

## 💻 How to open in VS Code
1.  Open **VS Code**.
2.  Go to `File` -> `Open Folder...`.
3.  Select this **"ai assistant"** folder on your Desktop.

## 🛠️ How to start manually in VS Code Terminal
If you want to run it yourself inside VS Code:

### 1. Start the Backend
1.  Open a new terminal in VS Code (`Ctrl + ` `).
2.  Type: `cd backend`
3.  Type: `python -m venv venv` (only first time)
4.  Type: `venv\Scripts\activate`
5.  Type: `pip install -r requirements.txt`
6.  Type: `python -m uvicorn main:app --host 127.0.0.1 --port 8001`

### 2. Start the Frontend
1.  Open a **second** terminal window in VS Code (click the `+` icon in terminal).
2.  Type: `cd frontend`
3.  Type: `npm install` (only first time)
4.  Type: `npm run dev -- --port 5175`

---

## 🌐 Accessing the Chatbot
- **Frontend**: [http://localhost:5175](http://localhost:5175)
- **Backend API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Enjoy your KPGU AI Assistant!** 🎓✨
