# ════════════════════════════════════════════════════════════════
# InnAgent AI — Vercel Serverless Entry Point
# Wraps the FastAPI app for Vercel's Python runtime
# ════════════════════════════════════════════════════════════════

from backend.main import app

# Vercel looks for an `app` variable in this file
# The FastAPI app is already ASGI-compatible, which Vercel supports
