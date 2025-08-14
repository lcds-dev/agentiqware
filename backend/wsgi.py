"""
WSGI entry point for App Engine
"""

from main import app

# For App Engine deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)