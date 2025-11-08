# Environment Variables Setup Guide

## Do You Need .env Files?

**Short answer:** Optional for local development, **required for production** with custom configurations.

## When You Need .env Files

### ✅ You DON'T need .env files if:
- Running locally with default settings (port 5000)
- Using default Flask debug mode
- Testing with the provided examples
- All defaults work for you

### ✅ You DO need .env files if:
- Deploying to production (Render, Heroku, AWS, etc.)
- Using a custom port
- Connecting to a database
- Using API keys or secrets
- Different configs for dev/staging/prod

## Setup Instructions

### For Flask API (Backend)

1. **Copy the example file:**
   ```bash
   cd ML
   cp .env.example .env
   ```

2. **Edit `.env` with your values:**
   ```env
   PORT=5000
   FLASK_DEBUG=False
   ```

3. **For production:**
   ```env
   PORT=10000
   FLASK_DEBUG=False
   ```

**Note:** The Flask app will work without a `.env` file using defaults:
- `PORT=5000` (default)
- `FLASK_DEBUG=False` (default)

### For Node.js Frontend

1. **Copy the example file:**
   ```bash
   cd your-nodejs-project
   cp examples/.env.example .env
   ```

2. **Edit `.env` with your API URL:**
   ```env
   API_URL=http://localhost:5000
   ```

3. **For production:**
   ```env
   API_URL=https://your-app.onrender.com
   ```

### For React Frontend

1. **Create `.env` in your React project root:**
   ```env
   REACT_APP_API_URL=http://localhost:5000
   ```

2. **For production:**
   ```env
   REACT_APP_API_URL=https://your-app.onrender.com
   ```

**Important:** React requires `REACT_APP_` prefix for environment variables!

## Environment Variables Reference

### Flask API Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Server port number |
| `FLASK_DEBUG` | `False` | Enable Flask debug mode (True/False) |

### Node.js Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_URL` | `http://localhost:5000` | Flask API base URL |

### React Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:5000` | Flask API base URL (must start with `REACT_APP_`) |

## Loading Environment Variables

### Python (Flask)

The Flask app automatically reads from `os.environ`, so no special loading needed. If you want to use `.env` files, install `python-dotenv`:

```bash
pip install python-dotenv
```

Then add to `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

### Node.js

Install `dotenv`:
```bash
npm install dotenv
```

Then in your code:
```javascript
require('dotenv').config();
const apiUrl = process.env.API_URL;
```

### React

React automatically loads `.env` files from the project root. Just create `.env` with `REACT_APP_` prefix variables.

## Production Deployment

### Render.com / Heroku

Set environment variables in the dashboard:
- Go to your service settings
- Add environment variables
- No `.env` file needed (set in dashboard)

### Local Production Testing

Create `.env.production`:
```env
PORT=10000
FLASK_DEBUG=False
```

## Security Notes

⚠️ **Never commit `.env` files to Git!**

- ✅ `.env` files are already in `.gitignore`
- ✅ Commit `.env.example` files (they have no secrets)
- ✅ Use environment variables in production dashboards
- ❌ Don't hardcode secrets in code
- ❌ Don't commit `.env` files

## Quick Start (No .env Needed)

If you just want to test locally, you can skip `.env` files entirely:

**Flask API:**
```bash
python app.py
# Runs on http://localhost:5000 (default)
```

**Node.js/React:**
```javascript
// Just use the default URL
const API_URL = 'http://localhost:5000';
```

## Examples

### Example 1: Local Development (No .env)
```bash
# Flask
python app.py  # Uses defaults

# React
# Set in code: const API_URL = 'http://localhost:5000';
```

### Example 2: Custom Port (With .env)
```bash
# .env
PORT=8080

# Flask
python app.py  # Runs on port 8080
```

### Example 3: Production (Environment Variables in Dashboard)
```bash
# No .env file needed
# Set PORT=10000 in Render/Heroku dashboard
```

## Troubleshooting

**Problem:** Environment variables not loading
- **Solution:** Make sure `.env` file is in the correct directory (same as the script)

**Problem:** React variables not working
- **Solution:** Must use `REACT_APP_` prefix and restart dev server

**Problem:** Port already in use
- **Solution:** Change `PORT` in `.env` or set it when running:
  ```bash
  PORT=8080 python app.py
  ```

---

**TL;DR:** You don't need `.env` files for basic local development, but they're useful for custom configurations and required for production deployments.

