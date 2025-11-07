# Deployment Guide for Render

This guide will help you deploy the NEP Timetable Generator API to Render.

## Prerequisites

1. GitHub account
2. Render account (sign up at https://render.com)
3. Git installed locally

## Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   ```

2. **Add all files**:
   ```bash
   git add .
   ```

3. **Commit**:
   ```bash
   git commit -m "Initial commit - NEP Timetable Generator API"
   ```

4. **Create GitHub repository**:
   - Go to https://github.com/new
   - Create a new repository (e.g., `nep-timetable-generator`)
   - **Don't** initialize with README, .gitignore, or license

5. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/nep-timetable-generator.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Deploy on Render

### Option A: Using render.yaml (Recommended)

1. **Go to Render Dashboard**:
   - Visit https://dashboard.render.com
   - Click "New +" → "Blueprint"

2. **Connect GitHub**:
   - Connect your GitHub account if not already connected
   - Select your repository: `nep-timetable-generator`

3. **Render will automatically detect render.yaml**:
   - The `render.yaml` file contains all configuration
   - Click "Apply" to deploy

### Option B: Manual Setup

1. **Create New Web Service**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `nep-timetable-generator` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or choose paid plan)

3. **Environment Variables** (Optional):
   - `PYTHON_VERSION`: `3.10.0`
   - `PORT`: `10000` (Render sets this automatically)

4. **Health Check Path**: `/health`

5. **Click "Create Web Service"**

## Step 3: Verify Deployment

Once deployed, Render will provide a URL like:
```
https://nep-timetable-generator.onrender.com
```

### Test the API:

1. **Health Check**:
   ```bash
   curl https://nep-timetable-generator.onrender.com/health
   ```

2. **API Info**:
   ```bash
   curl https://nep-timetable-generator.onrender.com/api/info
   ```

3. **Generate Timetable**:
   ```bash
   curl -X POST https://nep-timetable-generator.onrender.com/api/generate \
     -H "Content-Type: application/json" \
     -d @example_request.json
   ```

## Step 4: Update Your Code

After making changes:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

Render will automatically rebuild and redeploy your service.

## Configuration Files

### render.yaml
Contains Render service configuration. Automatically detected by Render.

### Procfile
Alternative way to specify start command (used if render.yaml is not present).

### .gitignore
Excludes unnecessary files from Git repository.

## Environment Variables

You can set environment variables in Render dashboard:
- **Settings** → **Environment** → **Add Environment Variable**

Common variables:
- `FLASK_DEBUG`: `False` (for production)
- `PYTHON_VERSION`: `3.10.0`

## Troubleshooting

### Build Fails
- Check `requirements.txt` for all dependencies
- Verify Python version compatibility
- Check build logs in Render dashboard

### Service Won't Start
- Verify `gunicorn` is in requirements.txt
- Check start command: `gunicorn app:app`
- Review logs in Render dashboard

### API Not Responding
- Verify health check endpoint: `/health`
- Check service is running (not sleeping on free plan)
- Review application logs

### Free Plan Limitations
- Services sleep after 15 minutes of inactivity
- First request after sleep may take 30-60 seconds
- Consider upgrading to paid plan for always-on service

## Production Recommendations

1. **Use Paid Plan**: Keeps service always running
2. **Add Monitoring**: Set up alerts for service health
3. **Enable Logs**: Monitor application logs regularly
4. **Rate Limiting**: Consider adding rate limiting for production
5. **HTTPS**: Automatically enabled by Render
6. **Custom Domain**: Add your own domain in Render settings

## Testing Locally Before Deploy

Test with gunicorn locally:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app:app --bind 0.0.0.0:5000

# Test
curl http://localhost:5000/health
```

## Support

- Render Documentation: https://render.com/docs
- Render Status: https://status.render.com
- Issues: Create an issue in your GitHub repository

