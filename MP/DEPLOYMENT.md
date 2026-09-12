# CAREVIBE Deployment and Setup Guide

This guide describes how to run and deploy the CAREVIBE mental wellness assistant application.

---

## 💻 Local Development Setup

### Method 1: Automated Script (Recommended)
Double-click `run_project.bat` in the root folder. This automatically:
1. Launches the Flask backend in a separate terminal window.
2. Opens the frontend `smart_mha_ui_draft.html` page in your default browser.

### Method 2: Manual Start
1. Ensure MongoDB is running locally on port `27017`.
2. Open a terminal and navigate to the backend folder:
   ```bash
   cd carevibe-backend
   ```
3. Activate the virtual environment:
   * **Windows**: `venv\Scripts\activate`
   * **macOS/Linux**: `source venv/bin/activate`
4. Start the server:
   ```bash
   python app.py
   ```
5. Open `smart_mha_ui_draft.html` in any browser.

---

## 🐳 Containerized Setup (Docker Compose)

Docker compiles both Flask and MongoDB together in isolated sandboxes, eliminating dependency mismatch issues.

### Requirements
* Docker Desktop installed on your system.

### Running with Docker
1. Set your `GEMINI_API_KEY` (if using AI chatbot features) in your system environment or in the `.env` file in the root.
2. Run the following command from the root directory:
   ```bash
   docker-compose up --build
   ```
3. The backend container pings MongoDB automatically and serves APIs on `http://localhost:5000`. You can open `smart_mha_ui_draft.html` in your browser.

---

## ☁️ Cloud Deployment

For university major project evaluations, it is recommended to host the project live.

### 1. Backend API Deployment (Render / Railway)
You can deploy the Flask backend to free web hosting services like [Render](https://render.com) or [Railway](https://railway.app):

1. **GitHub Repository**: Push your workspace to your GitHub account.
2. **Database setup**: Create a free MongoDB database cluster on [MongoDB Atlas](https://www.mongodb.com/atlas/database) and copy the connection string.
3. **Deploy to Render**:
   * Create a new **Web Service** on Render connected to your GitHub repository.
   * Set root directory: `MP/carevibe-backend` (or root if restructuring).
   * Runtime: `Python` (or select Docker to use the `Dockerfile` automatically).
   * **Environment Variables**:
     * `MONGODB_URI`: *Your MongoDB Atlas connection string*
     * `SECRET_KEY`: *Any random secure string*
     * `GEMINI_API_KEY`: *Your Google Generative AI API Key*
     * `FLASK_ENV`: `production`

### 2. Frontend Hosting (Netlify / Vercel / GitHub Pages)
Because the frontend is static HTML/CSS/JS, it can be hosted for free:

1. **Deploy to Netlify**:
   * Drag and drop the `MP` folder containing `smart_mha_ui_draft.html` onto the Netlify dashboard.
   * Rename `smart_mha_ui_draft.html` to `index.html` in your folder to make it the default root homepage.
2. **Configure API connection**:
   * In `index.html` (formerly `smart_mha_ui_draft.html`), locate `const API_BASE_URL = 'http://localhost:5000/api';` around line 3911.
   * Replace `'http://localhost:5000/api'` with your deployed Render service URL (e.g. `'https://carevibe-backend.onrender.com/api'`).
