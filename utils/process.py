import psutil
import subprocess
import time

def find_or_start_chromium(logger):
    target_args = "--remote-debugging-port=9222 --remote-allow-origins=*"
    
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if ('chromium' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower()) \
            and target_args in cmdline:
                logger.log_event("Found running Chromium process that meets criteria, PID: {}, Commandline string: '{}'".format(proc.info['pid'], cmdline))
                return proc.info['pid']
            elif ('chromium' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower()):
                ogger.log_event("Found running Chromium process that does not meet criteria with PID: {}, Commandline string: '{}'; killing it".format(proc.info['pid'], cmdline))
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    logger.log_event("Starting new Chromium process with correct arguments.")
    process = subprocess.Popen(["chromium", "--remote-debugging-port=9222", "--remote-allow-origins=*"], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)

    # Wait for the process to complete and capture the output
    stdout, stderr = process.communicate()
    return_code = process.returncode

    if return_code != 0:
        logger.log_event("Recieved error code {} attempting to open Chromium process. stdout: '{}', stderr: '{}'"
            .format(return_code, stdout, stderr))
        return None
    else:
        logger.log_event("Result from open Chromium process was: '{}'".format(stdout))
    

    # At this point we know there wasn't an error in starting the process, so it might just be taking
    # some time to finish start. However, we don't want to keep trying forever. 500 seconds is probably
    # too long but anything else is gonna break my OCD
    chromium_pid = None
    max_retries = 100
    cur_retries = 0
    while chromium_pid = None and cur_retries < max_retries:
        time.sleep(5)
        
        for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'])
                if ('chromium' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower()) \
                and target_args in cmdline:
                    logger.log_event("Found PID of new Chromium process, {}, after {} retries".format(proc.info['pid'], cur_retries))
                    chromium_pid = proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        cur_retries = cur_retries + 1

    return chromium_pid