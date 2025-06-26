# scanner_process.py
import sys
import socket
import socks
import ipaddress
import json
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from smb.SMBConnection import SMBConnection
from smb import smb_structs
from smb.base import NotConnectedError, SMBTimeout
from smb.smb_structs import ProtocolError as SMBProtocolError

def check_smb_host(host, user, password, quick_scan, use_proxy, proxy_port):
    """Checks a single host and returns a result dictionary or None."""
    try:
        if use_proxy:
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", proxy_port)
        else:
            socks.set_default_proxy(None) # Make sure proxy is disabled
        socket.socket = socks.socksocket
        smb_structs.socket = socks.socksocket
        smb_structs.SUPPORT_NTLMv2 = True
        smb_structs.SUPPORT_NTLMv1 = False
    except Exception as e:
        return None

    conn = None
    try:
        # Use a unique client name for each connection attempt to avoid conflicts
        client_name = f'pysmb-scan-{os.urandom(4).hex()}'
        conn = SMBConnection(user, password, client_name, host, use_ntlm_v2=True, is_direct_tcp=True)
        if not conn.connect(host, 445, timeout=5):
            return None

        shares = conn.listShares(timeout=5)
        share_info = []
        for share in shares:
            if not share.name.endswith('$'):
                permissions = ""
                if not quick_scan:
                    perms_list = []
                    try:
                        # Check for READ access
                        conn.listPath(share.name, '/', timeout=5)
                        perms_list.append('READ')
                    except (Exception):
                        pass # Can't read
                    try:
                        # Check for WRITE access
                        temp_dir = f'temp_check_{os.urandom(4).hex()}'
                        conn.createDirectory(share.name, f'/{temp_dir}')
                        conn.deleteDirectory(share.name, f'/{temp_dir}')
                        perms_list.append('WRITE')
                    except (Exception):
                        pass # Can't write
                    permissions = ", ".join(perms_list) if perms_list else "NO_ACCESS"
                else:
                    permissions = "N/A (Quick Scan)"

                share_info.append({'name': share.name, 'permissions': permissions})

        if share_info:
            return {'host': host, 'status': 'success', 'shares': share_info}
        return None
    except (Exception):
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subnet", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", default="")
    # --- MODIFIED: Proxy port is no longer required if --no-proxy is used ---
    parser.add_argument("--proxy-port", type=int) 
    parser.add_argument("--no-proxy", action='store_true')
    parser.add_argument("--quick-scan", action='store_true')
    args = parser.parse_args()

    # --- MODIFIED: Conditional proxy setup for the main process ---
    if not args.no_proxy:
        if args.proxy_port is None:
            print("STATUS:Error - Proxy port required but not provided.", flush=True)
            return
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", args.proxy_port)
    else:
        socks.set_default_proxy(None)
    socket.socket = socks.socksocket

    try:
        network = ipaddress.ip_network(args.subnet, strict=False)
        hosts_to_scan = [str(host) for host in network.hosts()]
    except ValueError:
        print("STATUS:Invalid Subnet", flush=True)
        return

    print(f"STATUS:Stage 1: Port scanning {len(hosts_to_scan)} hosts...", flush=True)
    open_hosts = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_host = {executor.submit(port_check, host, not args.no_proxy, args.proxy_port): host for host in hosts_to_scan}
        for future in as_completed(future_to_host):
            if future.result():
                open_hosts.append(future.result())

    print(f"STATUS:Stage 2: Enumerating shares on {len(open_hosts)} live hosts...", flush=True)
    with ThreadPoolExecutor(max_workers=25) as executor:
        future_to_host = {executor.submit(check_smb_host, host, args.user, args.password, args.quick_scan, not args.no_proxy, args.proxy_port): host for host in open_hosts}
        processed_count = 0
        total_to_process = len(open_hosts)
        for future in as_completed(future_to_host):
            processed_count += 1
            print(f"STATUS:Enumerating... ({processed_count}/{total_to_process})", flush=True)
            result = future.result()
            if result:
                print(f"RESULT:{json.dumps(result)}", flush=True)

    print("STATUS:Scanner process finished.", flush=True)

def port_check(host, use_proxy, proxy_port):
    """Dedicated port check function for the process."""
    try:
        # Each thread needs its own proxy setting
        if use_proxy:
            thread_socket = socks.socksocket()
            thread_socket.set_proxy(socks.SOCKS5, "127.0.0.1", proxy_port)
        else:
            thread_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        thread_socket.settimeout(2.0)
        thread_socket.connect((host, 445))
        thread_socket.close()
        return host
    except (Exception):
        return None

if __name__ == "__main__":
    main()
