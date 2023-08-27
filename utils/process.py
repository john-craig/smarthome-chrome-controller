import psutil
import subprocess
import time

def find_or_start_chromium():
    target_args = "--remote-debugging-port=9222 --remote-allow-origins=*"
    
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'chromium' in proc.info['name'].lower() and target_args in cmdline:
                return proc.info['pid']
            elif 'chromium' in proc.info['name'].lower():
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    subprocess.Popen(["chromium", "--remote-debugging-port=9222", "--remote-allow-origins=*"])
    
    # Wait for a short while to ensure the process has started
    time.sleep(2)
    
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'chromium' in proc.info['name'].lower() and target_args in cmdline:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return None