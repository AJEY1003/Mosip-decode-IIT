"""
Script to start the complete OCR & Verification Engine system (both backend and frontend)
"""
import subprocess
import sys
import os
import threading
import time
import webbrowser
import signal
import atexit

class OCRSystemStarter:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_started = False
        self.frontend_started = False
        
    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting OCR Backend Server...")
        
        backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
        
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        try:
            self.backend_process = subprocess.Popen(cmd, cwd=backend_dir)
            self.backend_started = True
            print("✅ Backend server started on http://localhost:8000")
            
            # Wait for the process
            self.backend_process.wait()
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            self.backend_started = False
    
    def start_frontend(self):
        """Start the frontend server"""
        print("🚀 Starting OCR Frontend Server...")
        
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
        
        # Check if dependencies are installed
        node_modules_path = os.path.join(frontend_dir, 'node_modules')
        if not os.path.exists(node_modules_path):
            print("📦 Installing frontend dependencies...")
            try:
                subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
                print("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError:
                print("❌ Failed to install dependencies")
                self.frontend_started = False
                return
        
        cmd = ['npm', 'run', 'dev']
        
        try:
            self.frontend_process = subprocess.Popen(
                cmd, 
                cwd=frontend_dir, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            self.frontend_started = True
            print("✅ Frontend server started on http://localhost:3000")
            
            # Print frontend output
            while True:
                output = self.frontend_process.stdout.readline()
                if output == '' and self.frontend_process.poll() is not None:
                    break
                if output:
                    print(f"[FRONTEND] {output.strip()}")
            
            self.frontend_process.wait()
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            self.frontend_started = False
    
    def start_system(self):
        """Start both backend and frontend servers"""
        print("🌟 Starting Smart OCR & Verification Engine System...")
        print("="*60)
        
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=self.start_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start frontend in a separate thread
        frontend_thread = threading.Thread(target=self.start_frontend)
        frontend_thread.daemon = True
        frontend_thread.start()
        
        # Wait for both threads
        try:
            # Wait for a moment to ensure both are running
            time.sleep(5)
            
            print("\n" + "="*60)
            print("🎉 Smart OCR & Verification Engine is running!")
            print("🔧 Backend: http://localhost:8000")
            print("🎨 Frontend: http://localhost:3000")
            print("📊 Health Check: http://localhost:8000/health")
            print("\n💡 Press Ctrl+C to stop the system")
            print("="*60)
            
            # Try to open browser
            try:
                time.sleep(3)  # Wait a bit more for servers to fully start
                webbrowser.open('http://localhost:3000')
                print("🌐 Opening browser automatically...")
            except Exception as e:
                print(f"⚠️ Could not open browser automatically: {e}")
                print("🔗 Please manually navigate to http://localhost:3000")
            
            # Wait for threads to complete
            backend_thread.join()
            frontend_thread.join()
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down OCR & Verification Engine...")
            self.stop_system()
    
    def stop_system(self):
        """Stop both servers"""
        print("🛑 Stopping system...")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                print("✅ Backend server stopped")
            except:
                pass
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                print("✅ Frontend server stopped")
            except:
                pass
        
        print("👋 OCR & Verification Engine stopped safely")

def main():
    starter = OCRSystemStarter()
    
    # Register cleanup function
    def cleanup():
        starter.stop_system()
    
    atexit.register(cleanup)
    
    try:
        starter.start_system()
    except KeyboardInterrupt:
        starter.stop_system()

if __name__ == "__main__":
    main()