# Environment Variables for Deployment

## For Render.com Deployment

**You DON'T need a `.env` file for Render!** 

Render automatically:
- Sets `PORT` (you don't need to set it)
- Reads environment variables from `render.yaml` or dashboard

### What Render Does Automatically:
- ✅ Sets `PORT` automatically (from `$PORT` environment variable)
- ✅ Uses Python version from `render.yaml` (Python 3.11)

### Optional: Set in Render Dashboard

If you want to set additional variables, go to:
**Render Dashboard → Your Service → Environment → Add Environment Variable**

**Recommended for Production:**
```
FLASK_DEBUG=False
```

**Note:** `render.yaml` already has `PORT` and `PYTHON_VERSION` configured, so you don't need to add them.

---

## For Local Development (Optional)

If you want to use a `.env` file locally, create `ML/.env`:

```env
# Flask API Environment Variables
PORT=5000
FLASK_DEBUG=False
```

**To use .env file locally, install python-dotenv:**
```bash
pip install python-dotenv
```

Then add to `app.py` (at the top, after imports):
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

---

## For Other Platforms (Heroku, AWS, etc.)

### Heroku
Set via Heroku CLI or dashboard:
```bash
heroku config:set FLASK_DEBUG=False
heroku config:set PORT=5000  # Usually auto-set
```

### AWS / Docker
Set in your deployment configuration or docker-compose.yml:
```yaml
environment:
  - PORT=5000
  - FLASK_DEBUG=False
```

---

## Summary

### ✅ For Render Deployment:
**You don't need a .env file!** Just deploy - Render handles everything.

If you want to set `FLASK_DEBUG`:
1. Go to Render Dashboard
2. Your Service → Environment
3. Add: `FLASK_DEBUG` = `False`

### ✅ For Local Development:
Create `ML/.env`:
```env
PORT=5000
FLASK_DEBUG=False
```

### ✅ Environment Variables Used:

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `5000` | No | Server port (auto-set by Render) |
| `FLASK_DEBUG` | `False` | No | Enable debug mode (set to False for production) |
| `PYTHON_VERSION` | - | No | Python version (set in render.yaml) |

---

## Quick Answer for Render:

**Nothing!** Just deploy. Render automatically sets `PORT` and uses your `render.yaml` configuration.

If you want to be extra safe, set in Render Dashboard:
- `FLASK_DEBUG` = `False`

That's it! 🚀

