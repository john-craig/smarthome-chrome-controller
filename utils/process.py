import psutil
import subprocess
import time

def find_or_start_chromium(logger=None):
    target_args = "--remote-debugging-port=9222 --remote-allow-origins=*"
    
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if ('chromium' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower()) \
            and target_args in cmdline:
                if logger:
                    logger.log_event("Found running Chromium process that meets criteria, PID: {}, Commandline string: '{}'".format(proc.info['pid'], cmdline))
                return proc.info['pid']
            elif ('chromium' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower()):
                if logger:
                    logger.log_event("Found running Chromium process that does not meet criteria with PID: {}, Commandline string: '{}'; killing it".format(proc.info['pid'], cmdline))
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if logger:
        logger.log_event("Starting new Chromium process with correct arguments.")
    subprocess.Popen(["chromium", "--remote-debugging-port=9222", "--remote-allow-origins=*"])
    
    # Wait for a short while to ensure the process has started
    time.sleep(2)
    
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if ('chromium' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower()) \
            and target_args in cmdline:
                if logger:
                    logger.log_event("PID of new Chromium process is {}".format(proc.info['pid']))
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if logger:
        logger.log_event("Unable to find PID of new Chrome process")

    return None