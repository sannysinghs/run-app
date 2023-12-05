import subprocess
import time
import re

# Set your app's package name and activity name
package_name = "com.local.samplelog"
activity_name = "com.local.samplelog.MainActivity"

# Define the regex pattern for the target log message format
target_log_pattern = re.compile(r"sample message (\d+)")


# Number of times to repeat the process
num_repeats = 5
logs = []

for _ in range(num_repeats):
    # Launch the activity
    subprocess.run(["adb", "shell", "am", "start", "-n", f"{package_name}/{activity_name}"])

    # Wait for the target log message
    log_found = False
    timeout_seconds = 10  # Maximum time to wait for the log message
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        logcat_output = subprocess.check_output(["adb", "logcat", "-d"]).decode("utf-8")

        match = target_log_pattern.search(logcat_output)
        
        if match:
            extracted_pattern = match.group(1)  # Extract the match from the first capturing group
            logs.append(extracted_pattern)
            break
        time.sleep(1)

    # Close the activity
    subprocess.run(["adb", "shell", "am", "force-stop", package_name])

print(logs)