import os
import pwd
import grp
import sys

PROC_DIR = "/proc"

def get_process_info(pid):
    """Extract process information from /proc/[pid]/status."""
    try:
        status_file = os.path.join(PROC_DIR, pid, "status")
        with open(status_file, "r") as f:
            lines = f.readlines()
        
        process_info = {}
        for line in lines:
            if line.startswith("Pid:"):
                process_info['pid'] = line.split()[1]
            elif line.startswith("PPid:"):
                process_info['ppid'] = line.split()[1]
            elif line.startswith("Uid:"):
                process_info['uid'] = line.split()[1]
            elif line.startswith("Gid:"):
                process_info['gid'] = line.split()[1]
            elif line.startswith("State:"):
                process_info['state'] = line.split()[1]
        
        # Get command name
        cmd_file = os.path.join(PROC_DIR, pid, "comm")
        with open(cmd_file, "r") as f:
            process_info['command'] = f.read().strip()
        
        # Map UID and GID to usernames and group names
        process_info['uname'] = pwd.getpwuid(int(process_info['uid'])).pw_name
        process_info['gname'] = grp.getgrgid(int(process_info['gid'])).gr_name
        
        return process_info
    except Exception:
        return None  # If any error occurs (e.g., permissions), skip this process.

def display_processes(processes):
    """Print process information in a table format."""
    print(f"{'PID':<6}{'PPID':<6}{'UID':<6}{'UName':<10}{'GID':<6}{'GName':<10}{'State':<6}{'Command':<15}")
    print("-" * 65)
    for proc in processes:
        print(f"{proc['pid']:<6}{proc['ppid']:<6}{proc['uid']:<6}{proc['uname']:<10}{proc['gid']:<6}{proc['gname']:<10}{proc['state']:<6}{proc['command']:<15}")

def main():
    # Determine if we should show all processes or just current user's
    show_all = len(sys.argv) > 1 and sys.argv[1] == "-a"
    current_uid = os.getuid()
    
    processes = []
    for pid in os.listdir(PROC_DIR):
        if pid.isdigit():  # Only numeric directories are PIDs
            info = get_process_info(pid)
            if info:
                if show_all or int(info['uid']) == current_uid:
                    processes.append(info)
    
    # Display the collected process information
    display_processes(processes)

if __name__ == "__main__":
    main()
