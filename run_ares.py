import uvicorn
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

if __name__ == "__main__":
    print("Starting ARES Unified Server on Port 9001...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=9001, reload=False)
