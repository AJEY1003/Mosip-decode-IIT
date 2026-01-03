"""
Script to start the OCR frontend development server
"""
import subprocess
import sys
import os
import platform
import webbrowser
import time

def start_frontend():
    """
    Start the React frontend development server
    """
    print("🚀 Starting OCR & Verification Engine Frontend Server...")
    print("🔧 Using Vite for development")
    
    # Change to the frontend directory
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    # Check if node and npm are available
    try:
        import shutil
        if not shutil.which('npm'):
            print("❌ npm not found. Please install Node.js and npm.")
            print("🔗 Download from: https://nodejs.org/")
            sys.exit(1)
    except ImportError:
        print("⚠️ Unable to check for npm. Make sure Node.js is installed.")
    
    # Install dependencies if node_modules doesn't exist
    node_modules_path = os.path.join(frontend_dir, 'node_modules')
    if not os.path.exists(node_modules_path):
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    # Command to start the frontend dev server
    cmd = ['npm', 'run', 'dev']
    
    try:
        print("✅ Starting frontend server on http://localhost:3000")
        print("💡 Press Ctrl+C to stop the server")
        
        # Start the subprocess
        process = subprocess.Popen(cmd, cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Try to open the browser after a short delay
        def open_browser():
            time.sleep(3)  # Wait for the server to start
            try:
                webbrowser.open('http://localhost:3000')
                print("🌐 Opening browser at http://localhost:3000")
            except Exception as e:
                print(f"⚠️ Could not automatically open browser: {e}")
                print("🔗 Please manually navigate to http://localhost:3000")
        
        # Start browser opening in a separate thread
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.start()
        
        # Print output from the subprocess
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped by user")
        process.terminate()
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_frontend()