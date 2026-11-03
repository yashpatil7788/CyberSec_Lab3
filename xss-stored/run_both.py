"""
run_both.py — starts both servers at once
Usage: python run_both.py
"""
import subprocess, sys, os, time, webbrowser

base   = os.path.dirname(os.path.abspath(__file__))
python = sys.executable

p1 = subprocess.Popen([python, os.path.join(base, "app_vulnerable.py")])
p2 = subprocess.Popen([python, os.path.join(base, "app_secure.py")])

time.sleep(1.5)
webbrowser.open("http://127.0.0.1:5000")
time.sleep(0.3)
webbrowser.open("http://127.0.0.1:5001")

print("\n  Both servers running.")
print("  Vulnerable → http://127.0.0.1:5000")
print("  Secure     → http://127.0.0.1:5001")
print("\n  Press Ctrl+C to stop both.\n")

try:
    p1.wait()
except KeyboardInterrupt:
    p1.terminate()
    p2.terminate()
