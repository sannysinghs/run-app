import subprocess
import time
import re
import os

# Set your app's package name and activity name
package_name = "com.dyson.codelab_compose"
activity_name = "com.dyson.codelab_compose.MainActivity"
tag_name = "RxLoggingExtensions"
MAX_BOUND = 10000

# Define the regex pattern for the target log message format
start_log_pattern = re.compile(r"GATT connected:(\d+)")
# Define the regex pattern for the target log message format
end_log_pattern = re.compile(r"GATT disconnected:(\d+)")
scan_end_pattern = True

# Number of times to repeat the process
num_repeats = 20

def search_and_get_log_message(pattern, append_to_log = False): 
    logs = []
    timeout_seconds = 30  # Maximum time to wait for the log message
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        logcat_output = subprocess.check_output(["adb", "logcat", "-d"]).decode("utf-8")
        match = pattern.search(logcat_output)
        if match:
            if append_to_log:
                logs.append(match.group(1))   # Extract the match from the first capturing group
            break
        time.sleep(1)
    return logs

def get_output_filename(): 
    # Get the absolute path of the current script
    script_path = os.path.abspath(__file__)

    # Get the directory containing the script
    script_directory = os.path.dirname(script_path)

    return f"{script_directory}/output.txt"

def main():
    results = []
    # get the device details 
    times = 0
    device = subprocess.check_output(["adb", "shell", "getprop", "ro.product.model"]).decode("utf-8")
    while times < num_repeats: 
        subprocess.check_output(["adb", "logcat", "-c"]).decode("utf-8")
        subprocess.run(["adb", "shell", "am", "start", "-n", f"{package_name}/{activity_name}"])
        start_groups = search_and_get_log_message(start_log_pattern, True)
        if len(start_groups) > 0: 
            timeInMills = int(start_groups[0])
            if (timeInMills <= MAX_BOUND):
                results.append(timeInMills) 
                times += 1
        # provide buffer to avoid flakiness
        time.sleep(3)
        # Move the app background
        subprocess.run(["adb", "shell", "input", "keyevent", "3"])
        if scan_end_pattern: 
            search_and_get_log_message(end_log_pattern)
        # Close the activity
        subprocess.run(["adb", "shell", "am", "force-stop", package_name])

    with open(get_output_filename(), 'w') as file: 
        for r in results: 
            if file.tell() != 0:
                file.write('\n')
            file.write(f"{r}")

    print(f"Script finished! Output file ${get_output_filename()}")
if __name__ == "__main__":
    main()