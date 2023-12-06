import subprocess
import time
import re

# Set your app's package name and activity name
package_name = "com.dyson.codelab_compose"
activity_name = "com.dyson.codelab_compose.MainActivity"

# Define the regex pattern for the target log message format
start_log_pattern = re.compile(r" GATT connected, time: (\d+)")
# Define the regex pattern for the target log message format
end_log_pattern = re.compile(r" GATT disconnected, time: (\d+)")

# Number of times to repeat the process
num_repeats = 20

def search_and_get_log_message(pattern): 
    logs = []
    timeout_seconds = 30  # Maximum time to wait for the log message
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        logcat_output = subprocess.check_output(["adb", "logcat", "-d", "-s", f"{package_name}", "ble_debug"]).decode("utf-8")
        match = pattern.search(logcat_output)
        if match:
            logs.append(match.group(1))   # Extract the match from the first capturing group
            break
        time.sleep(1)
    return logs

def main():
    results = []
    # get the device details 
    device = subprocess.check_output(["adb", "shell", "getprop", "ro.product.model"]).decode("utf-8")
    for _ in range(num_repeats):
        subprocess.check_output(["adb", "logcat", "-c"]).decode("utf-8")
        subprocess.run(["adb", "shell", "am", "start", "-n", f"{package_name}/{activity_name}"])
        start_groups = search_and_get_log_message(start_log_pattern)
        if len(start_groups) > 0: 
            results.append(int(start_groups[0])) 
        # provide buffer to avoid flakiness
        time.sleep(3)    
        # Move the app background
        subprocess.run(["adb", "shell", "input", "keyevent", "3"])
        end_groups = search_and_get_log_message(end_log_pattern)
        if len(end_groups) > 0: 
            print("disconnect log found")
        # Close the activity
        subprocess.run(["adb", "shell", "am", "force-stop", package_name])

    print(device)
    print(results)
    print(f"average: {sum(results) / len(results)} ")

if __name__ == "__main__":
    main()