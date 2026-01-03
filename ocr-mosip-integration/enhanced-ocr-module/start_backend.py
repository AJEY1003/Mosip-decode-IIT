"""
Script to start the OCR backend server
"""
import subprocess
import sys
import os

def start_backend():
    """
    Start the FastAPI backend server
    """
    print("🚀 Starting OCR & Verification Engine Backend Server...")
    print("🔧 Using FastAPI with uvicorn")
    
    # Change to the backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    
    # Command to start the server
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"  # Enable auto-reload during development
    ]
    
    try:
        print("✅ Starting server on http://localhost:8000")
        print("💡 Press Ctrl+C to stop the server")
        
        # Start the subprocess
        process = subprocess.Popen(cmd, cwd=backend_dir)
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        process.terminate()
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_backend()