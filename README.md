# Here are your Instructions
# 🚀 Running SightMate PWA on Your Localhost

Here's a complete guide to set up and run the SightMate PWA on your local computer:

## 📋 Prerequisites

Make sure you have these installed:
- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **Python** (v3.8 or higher) - [Download here](https://python.org/)
- **MongoDB** (Community Edition) - [Download here](https://www.mongodb.com/try/download/community)
- **Git** - [Download here](https://git-scm.com/)

## 📁 Project Structure

First, create the project structure:

```bash
mkdir sightmate-pwa
cd sightmate-pwa
mkdir backend frontend
```

## 🔧 Backend Setup (FastAPI + Gemini AI)

### 1. Create Backend Files

**Create `backend/requirements.txt`:**
```txt
fastapi==0.104.1
uvicorn==0.24.0
pymongo==4.6.0
python-multipart==0.0.6
google-generativeai==0.3.2
pillow==10.1.0
python-dotenv==1.0.1
```

**Create `backend/.env`:**
```env
MONGO_URL=mongodb://localhost:27017/
GEMINI_API_KEY=AIzaSyAP9BzGHp9iwOv2TWZlcuqDy2Jx0itpMow
DB_NAME=sightmate
```

**Create `backend/server.py`:** (Copy the complete server.py code I created earlier)

### 2. Install Backend Dependencies

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎨 Frontend Setup (React PWA)

### 1. Create React App

```bash
cd ../frontend
npx create-react-app . --template pwa
```

### 2. Install Additional Dependencies

```bash
npm install
# or
yarn install
```

### 3. Create Frontend Files

**Create `frontend/.env`:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Replace `frontend/src/App.js`** with the App.js code I created

**Replace `frontend/src/App.css`** with the App.css code I created

**Create `frontend/public/manifest.json`** with the manifest code I created

**Create `frontend/public/sw.js`** with the service worker code I created

### 4. Update package.json Scripts

Add these scripts to `frontend/package.json`:
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

## 🗄️ MongoDB Setup

### 1. Start MongoDB

**On Windows:**
```bash
# If installed as service, it should start automatically
# Or manually start with:
mongod
```

**On macOS:**
```bash
# Using Homebrew:
brew services start mongodb-community

# Or manually:
mongod --config /usr/local/etc/mongod.conf
```

**On Linux:**
```bash
sudo systemctl start mongod
# or
sudo service mongod start
```

### 2. Verify MongoDB is Running

```bash
# Test connection
mongo
# or
mongosh
```

## 🚀 Running the Application

### 1. Start Backend (Terminal 1)

```bash
cd backend
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Start FastAPI server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
✅ Gemini AI configured successfully
```

### 2. Start Frontend (Terminal 2)

```bash
cd frontend
npm start
# or
yarn start
```

The React app will start on `http://localhost:3000`

## 🧪 Testing the Setup

### 1. Test Backend API

Open `http://localhost:8001` in your browser - you should see:
```json
{"message": "SightMate API is running"}
```

### 2. Test Frontend

Open `http://localhost:3000` - you should see the SightMate interface with:
- Camera interface
- Large accessibility buttons
- Voice command features

### 3. Test Camera Functionality

1. Click "Start Camera" - browser will ask for camera permission
2. Allow camera access
3. Try any of the analysis buttons:
   - **Detect Objects**
   - **Read Text** 
   - **Detect Money**
   - **Identify Colors**

## 🔧 Troubleshooting

### Common Issues:

**1. Camera not working:**
- Make sure you're accessing via `http://localhost:3000` (not `127.0.0.1`)
- Allow camera permissions in browser
- Try Chrome/Firefox (better camera support)

**2. Backend API errors:**
- Check if MongoDB is running: `mongosh` or `mongo`
- Verify Gemini API key is correct in `.env`
- Check backend terminal for error messages

**3. CORS issues:**
- Make sure backend is running on port 8001
- Frontend should be on port 3000
- Check that REACT_APP_BACKEND_URL is set correctly

**4. Voice features not working:**
- Voice recognition works best in Chrome
- Make sure microphone permissions are allowed
- Text-to-speech should work in all modern browsers

## 📱 PWA Features

To test PWA functionality:
1. Open the app in Chrome on mobile
2. Look for "Install App" prompt
3. Add to home screen
4. Test offline functionality

## 🎯 Quick Start Commands

**Full startup sequence:**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Terminal 2 (Frontend):
```bash
cd frontend  
npm start
```

Terminal 3 (MongoDB - if not running as service):
```bash
mongod
```

Then open `http://localhost:3000` in your browser! 🎉

The app should now be fully functional with all AI vision features working on your local machine!
