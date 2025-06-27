
from mcp.server.fastmcp import FastMCP
import psutil
import os
import re
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("ProcessManager")

def is_root_access_allowed():
    return os.environ.get("ALLOW_ROOT") == "Y"

def get_current_username():
    return psutil.Process().username()

@mcp.tool()
def list_processes(username: Optional[str] = None):
    """List running processes. Defaults to the current user."""
    if username is None:
        username = get_current_username()
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        if proc.info['username'] == username:
            processes.append(f"{proc.info['pid']}: {proc.info['name']}")
    return "\n".join(processes)

@mcp.tool()
def find_processes(pattern: str, username: Optional[str] = None):
    """Find processes by regex pattern in name or command line."""
    if username is None:
        username = get_current_username()
    
    matched_processes = []
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"Invalid regex pattern: {e}"

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline']):
        if proc.info['username'] == username:
            # Check name
            if regex.search(proc.info['name']):
                matched_processes.append(f"{proc.info['pid']}: {proc.info['name']}")
                continue # Avoid adding the same process twice
            
            # Check command line
            cmdline = ' '.join(proc.info['cmdline'])
            if regex.search(cmdline):
                matched_processes.append(f"{proc.info['pid']}: {proc.info['name']}")

    return "\n".join(matched_processes)


@mcp.tool()
def get_process_info(pid: int):
    """Get detailed information about a process."""
    try:
        proc = psutil.Process(pid)
        if proc.username() == 'root' and not is_root_access_allowed():
            return "Access to root processes is not allowed. Set ALLOW_ROOT=Y to override."
        return str(proc.as_dict())
    except psutil.NoSuchProcess:
        return f"No such process with PID: {pid}"

@mcp.tool()
def terminate_process(pid: int):
    """Terminate a process."""
    try:
        proc = psutil.Process(pid)
        if proc.username() == 'root' and not is_root_access_allowed():
            return "Terminating root processes is not allowed. Set ALLOW_ROOT=Y to override."
        proc.terminate()
        return f"Process {pid} terminated."
    except psutil.NoSuchProcess:
        return f"No such process with PID: {pid}"

@mcp.tool()
def get_process_by_port(port: int, protocol: str = 'tcp', username: Optional[str] = None):
    """Get process information for a specific port and protocol (user processes only)."""
    import socket
    
    try:
        # Determine the expected socket type based on protocol
        expected_socket_type = socket.SOCK_STREAM if protocol.lower() == 'tcp' else socket.SOCK_DGRAM
        
        # Get target username (use current user if not provided)
        if username is None:
            target_username = get_current_username()
        else:
            target_username = username
        
        # Iterate through processes owned by the target user
        matching_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                # Skip processes not owned by target user
                if proc.info['username'] != target_username:
                    continue
                    
                # Get network connections for this user process
                try:
                    process_obj = psutil.Process(proc.info['pid'])
                    connections = process_obj.net_connections(kind='inet')
                    
                    for conn in connections:
                        # Check if this connection matches our criteria
                        if (conn.laddr.port == port and 
                            conn.status == 'LISTEN' and 
                            conn.type == expected_socket_type):
                            
                            matching_processes.append(process_obj)
                            
                            # Return the first matching process
                            return str(process_obj.as_dict())
                            
                except psutil.AccessDenied:
                    # Skip processes we can't access
                    continue
                except psutil.NoSuchProcess:
                    # Process disappeared while we were checking
                    continue
                except Exception as e:
                    continue
                    
            except Exception as e:
                continue
                
        return f"No process found for user '{target_username}' listening on port {port} with protocol {protocol}"
        
    except Exception as e:
        logger.error(f"Top-level exception: {type(e).__name__}: {e}")
        return f"Error in get_process_by_port: {type(e).__name__}: {e}"

@mcp.tool()
def get_user_info():
    """Get the current user's ID, group ID, and username."""
    try:
        username = get_current_username()
        uid = os.getuid()
        gid = os.getgid()
        return {
            "username": username,
            "uid": uid,
            "gid": gid,
        }
    except Exception as e:
        return f"Error getting user info: {e}"

if __name__ == "__main__":
    mcp.run()

