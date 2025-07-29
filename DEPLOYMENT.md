# 🚀 MedExplain Deployment Guide

## Free Deployment Stack

- **Frontend**: Netlify (Free tier)
- **Backend**: Render (Free tier) 
- **Database**: ChromaDB (File-based, included)
- **Cost**: Only OpenAI API usage (~$3-15/month)

## 📋 Deployment Steps

### 1. Deploy Backend to Render

1. **Create Render Account**: Go to [render.com](https://render.com) and sign up
2. **Connect GitHub**: Link your GitHub account
3. **Create Web Service**:
   - Choose "Build and deploy from a Git repository"
   - Select your `medexplain` repository
   - Configure:
     - **Name**: `medexplain-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python backend_server.py`
     - **Instance Type**: `Free`

4. **Set Environment Variables** in Render Dashboard:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ENVIRONMENT=production
   PORT=8000
   HOST=0.0.0.0
   ```

5. **Deploy**: Click "Create Web Service"

### 2. Deploy Frontend to Netlify

1. **Create Netlify Account**: Go to [netlify.com](https://netlify.com) and sign up
2. **Connect GitHub**: Link your GitHub account  
3. **Create New Site**:
   - Choose "Import from Git"
   - Select your `medexplain` repository
   - Configure:
     - **Base directory**: `frontend`
     - **Build command**: `npm run build`
     - **Publish directory**: `frontend/dist`

4. **Set Environment Variables** in Netlify Dashboard:
   ```
   VITE_API_URL=https://medexplain-backend.onrender.com
   ```
   *(Replace with your actual Render backend URL)*

5. **Deploy**: Netlify will automatically build and deploy

### 3. Update CORS Settings

After deployment, update the CORS origins in `backend_server.py`:

```python
allowed_origins.extend([
    "https://your-app-name.netlify.app",  # Replace with actual URL
])
```

Commit and push to trigger a new deployment.

## 🌐 Your Live URLs

After deployment, you'll have:

- **Frontend**: `https://your-app-name.netlify.app`
- **Backend API**: `https://medexplain-backend.onrender.com`
- **API Docs**: `https://medexplain-backend.onrender.com/docs`

## 🔧 Environment Variables

### Backend (Render)
```env
OPENAI_API_KEY=your_key_here
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
```

### Frontend (Netlify)
```env
VITE_API_URL=https://medexplain-backend.onrender.com
```

## 📊 Monitoring & Costs

### Free Tier Limits
- **Render**: 750 hours/month (24/7 uptime)
- **Netlify**: 100GB bandwidth, 300 build minutes/month

### Expected Costs
- **Hosting**: $0 (within free tiers)
- **OpenAI API**: ~$3-15/month depending on usage

## 🚨 Important Notes

- **First Deploy**: Backend may take 10-15 minutes on first deployment
- **Cold Starts**: Free tier has ~30 second cold start delays
- **SSL**: Both platforms provide free SSL certificates
- **Custom Domain**: Available on both platforms (optional)

## 🔧 Local Development

To run locally after deployment setup:

```bash
# Backend
python backend_server.py

# Frontend (in separate terminal)
cd frontend
npm run dev
```

## 📱 Mobile Responsive

The React frontend is fully mobile responsive and will work perfectly on all devices.

## 🎯 Next Steps

1. **Monitor Usage**: Set up OpenAI API usage alerts
2. **Custom Domain** (optional): Configure custom domain on Netlify
3. **Analytics**: Add Google Analytics or similar
4. **Monitoring**: Set up uptime monitoring (UptimeRobot, etc.)

Your MedExplain app is now live and accessible worldwide! 🎉