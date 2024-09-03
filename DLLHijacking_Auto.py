import subprocess
import sys
import os
import time
import psutil
from colorama import init
import pyfiglet
from termcolor import colored

init()
G  = '\033[32m' 
O  = '\033[33m' 
Y = '\033[93m'
BOLD = '\033[1m'
END = '\033[0m'


print(colored(pyfiglet.figlet_format("Auto DLL Hijacing (Procmon)", font="standard"), "red" ))
print(O+"Created By Rishabh Sharma"+END)

try:
    from procmon_parser import load_configuration, dump_configuration, Rule
    import procmon_parser
    import psutil
    import colorama
    import pyfiglet
except ImportError:
    print("procmon_parser not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "procmon_parser"])
    import procmon_parser
    print("psutil not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil
    print("colorama not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    import colorama
    from colorama import init
    print("pyfiglet not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyfiglet"])
    import pyfiglet

# Get the directory of the currently running script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Ask the user for the process name
print(G+BOLD+"\nProcmon Data Collection Start..."+END)
process_name_Directory = input("Please enter the process name Directory (e.g., C:\\Program Files\\Chrome.exe): ")
process_name = input("Please enter the process name (e.g., Chrome.exe): ")
# Ask the user for the sleep time
sleep_time = int(input("Enter the number of seconds to run the program: "))


# Store the process name in a variable and print it
print(O+f"\nSelected process: {process_name}"+END)

# Execute the user-specified process
#try:
#    user_process = subprocess.Popen(process_name_Directory, shell=True)
    #user_process = subprocess.Popen(f'start /MIN "" "{process_name_Directory}"', shell=True)
#    print(f"Process {process_name} started.")
#except Exception as e:
#    print(f"Failed to start process {process_name}: {e}")
#    sys.exit(1)

# Ask the user for the sleep time
#sleep_time = int(input("Enter the number of seconds to run the program: "))

pmc_file_path = os.path.join(script_dir, "ProcmonConfiguration.pmc")

try:
    with open(pmc_file_path, "rb") as f:
        config = load_configuration(f)
except FileNotFoundError:
    print(f"Error: The file {pmc_file_path} does not exist.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)

valuecheck = config["DestructiveFilter"]
print("\n")
print("Default Config File")
defaultconfig = config["FilterRules"]
print(defaultconfig)

print("\nAdding Rule")
new_rules = [Rule('Process_Name', 'contains', process_name)]
config["FilterRules"] = new_rules + config["FilterRules"]
print(config["FilterRules"])

with open("temp_newrule.pmc", "wb") as f:
    dump_configuration(config, f)
    print("New rule .pmc file is temp_newrule.pmc")

#print("\nChecking new rule...")
#with open("temp_newrule.pmc", "rb") as f:
#    config = load_configuration(f)
#print("\nCheck updated new rule with your process name...")
#print(config["FilterRules"])

with open('Filter_CSV.pmc', "rb") as f:
    config = load_configuration(f)
valuecheck = config["DestructiveFilter"]
print("\n")
print("Default CSV Filter Config File")
defaultconfig = config["FilterRules"]
print(defaultconfig)
print("\nUpdating CSV Filter Rule")
new_rules = [Rule('Process_Name', 'contains', process_name)]
config["FilterRules"] = new_rules + config["FilterRules"]
print(config["FilterRules"])

with open("temp_Filter_CSV.pmc", "wb") as f:
    dump_configuration(config, f)
    print("New CSV Filter rule .pmc file is temp_Filter_CSV.pmc")
    print(G+BOLD+f"\nCapturing Logs In Procmon....Be patient for {sleep_time} seconds..."+END)

# Get the current working directory
working_directory = os.path.dirname(os.path.abspath(__file__))

# Absolute paths to the ProcMon executable and configuration files
procmon_path = os.path.join(working_directory, "Procmon64.exe")
backing_file = os.path.join(working_directory, "PM.PML")
config_file = os.path.join(working_directory, "temp_newrule.pmc")



# Command to run ProcMon
command = f'"{procmon_path}" /Backingfile "{backing_file}" /LoadConfig "{config_file}" /Minimized /Quiet /Runtime {sleep_time} /AcceptEula'

# Start ProcMon in the background
procmon_process = subprocess.Popen(command, shell=True)

time.sleep(10)

try:
    user_process = subprocess.Popen(process_name_Directory, shell=True)
    #user_process = subprocess.Popen(f'start /MIN "" "{process_name_Directory}"', shell=True)
    print(f"Process {process_name} started.")
except Exception as e:
    print(f"Failed to start process {process_name}: {e}")
    sys.exit(1)

    
# Wait for the user-defined time
time.sleep(50)


# Terminate ProcMon
os.system("Procmon64.exe /Terminate")

# Optionally, wait a bit for ProcMon to close properly
time.sleep(3)

print("\nProcMon has been stopped.")

print("\nConverting file to output.csv...")
command1 = f'Procmon64.exe /Quiet /Minimized /Openlog PM.PML /LoadConfig temp_Filter_CSV.pmc /SaveApplyFilter /SaveAs output.csv'
procmon_process = subprocess.Popen(command1, shell=True)
time.sleep(4)
os.system("Procmon64.exe /Terminate")

# Clean up temporary files
os.remove('temp_newrule.pmc')
os.remove('temp_Filter_CSV.pmc')
os.remove('PM.PML')
print("\nTask Finished.....")

# Terminate the user-specified process and its children
def terminate_process_and_children(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.terminate()
        parent.terminate()
        gone, still_alive = psutil.wait_procs(children, timeout=5)
        for p in still_alive:
            p.kill()
        parent.kill()
        print(f"Process {process_name} and its children have been terminated.")
    except psutil.NoSuchProcess:
        print(f"Process {pid} does not exist.")

terminate_process_and_children(user_process.pid)
