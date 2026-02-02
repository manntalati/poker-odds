import uvicorn
import threading
import time
import sys
from pyngrok import ngrok, conf

import os
import signal
import subprocess

def kill_existing_process(port=8000):
    try:
        # Initial cleanup: Find processes using the port and kill them
        command = f"lsof -ti :{port}"
        pids = subprocess.check_output(command, shell=True).decode().split()
        for pid in pids:
            print(f"Killing existing process on port {port} (PID: {pid})")
            os.kill(int(pid), signal.SIGKILL)
        time.sleep(1)
    except subprocess.CalledProcessError:
        pass # No process found
    except Exception as e:
        print(f"Warning cleaning up port: {e}")

def start_server():
    # Kill old instance
    kill_existing_process(8000)
    # Start the FastAPI server on port 8000
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="error")

def main():
    print("---------------------------------------------------------")
    print("Starting Poker Odds Bot (Secure Mobile Access)")
    print("---------------------------------------------------------")

    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait a moment for server to spin up
    time.sleep(2)

    try:
        # Open a Ngrok tunnel to the server
        # This provides a public HTTPS URL that mobile phones prefer
        public_url = ngrok.connect(8000).public_url
        print("\n" + "="*60)
        print(f"SUCCESS! Your App is Live.")
        print("="*60)
        print(f"access this URL on your phone:\n")
        print(f"   {public_url}")
        print("\n" + "="*60 + "\n")
        print("Press Ctrl+C to stop.")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        print("\n" + "!"*60)
        print("ERROR STARTING TUNNEL")
        print("!"*60)
        print(f"Error: {e}")
        print("-" * 60)
        print("Common Solution: You likely need an Ngrok Auth Token.")
        print("1. Go to https://dashboard.ngrok.com/get-started/your-authtoken")
        print("2. Run this command in terminal:")
        print("   ngrok config add-authtoken YOUR_TOKEN_HERE")
        print("3. Then run this script again.")
        print("!"*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
