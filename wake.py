#!/usr/bin/env python3
import sys, socket, binascii, xml.etree.ElementTree as ET
from pathlib import Path
from ArgParser import ArgParser
import subprocess


TYPE_MAP = {
    "int": int,
    "str": str,
    "float": float,
    "bool": bool
}

CFG = Path.home() / ".wol_hosts.xml"

json_path = Path(__file__).parent / "args.json"

def usage():
    print("Usage: wake <device-name> | wake --list")
    sys.exit(1)

def load_hosts():
    # Error if config file is missing
    if not CFG.exists():
        print(f"[ERROR] Config XML not found: {CFG}")
        sys.exit(2)

    attributes = ["mac", "address", "port", "protocol"]

    root = ET.parse(CFG).getroot()

    # Default Values
    defaults = root.find("defaults") or ET.Element("defaults", {})
    defval = lambda k, d=None: defaults.attrib.get(k, d)

    hosts = {}
    for h in root.findall("host"):
        name = h.attrib.get("name")
        if not name:
            continue
        
        cur_packet = {}
        for at in attributes:
            cur_packet[at] = h.attrib.get(at, defval(at))
        
        hosts[name] = cur_packet

    return hosts

def wol(mac, address, port):
    mac_bytes = binascii.unhexlify(mac.replace(":", "").replace("-", ""))
    packet = b"\xff"*6 + mac_bytes*16
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # allow broadcast when address is a LAN broadcast
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception:
        pass
    s.sendto(packet, (address, int(port)))
    s.close()

def list_hosts():
    hosts = load_hosts()
    print()
    print("   Hosts \t\t    MAC Address \t    Address:Port")
    print("----------------------------------------------------------------------")
    for n in sorted(hosts):
        h = hosts[n]
        print(f"{n:16}\t {h['mac']}\t {h['address']}:{h['port']}")
    print()

def list_ssh_hosts():
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        print("[ERROR] No SSH config found at ~/.ssh/config")
        return

    hosts = []
    with open(ssh_config) as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith("host "):
                # Ignore wildcards like '*'
                parts = line.split()
                if len(parts) > 1 and parts[1] != "*":
                    hosts.append(parts[1])

    if not hosts:
        print("[INFO] No SSH hosts found in ~/.ssh/config")
        return

    print()
    print("   SSH Hosts")
    print("-------------------")
    for h in sorted(hosts):
        print(h)
    print()


def get_host_details(host_name):
    hosts = load_hosts()

    if host_name not in hosts:
        print(f"[ERROR] Host '{host_name}' not specified. Try 'wake --list'.")
        sys.exit(3)
    
    return hosts[host_name]

def wol_via_ssh(h, ssh_host):
    """
    Relay a Wake-on-LAN command via SSH to another machine.
    - h: dictionary with 'mac'
    - ssh_host: host alias from ~/.ssh/config or ssh.json
    """
    mac = h["mac"]

    # Command that will run remotely
    remote_cmd = f"wakeonlan {mac}"

    try:
        subprocess.run(
            ["ssh", ssh_host, remote_cmd],
            check=True
        )
        print(f"[SUCCESS] Sent WoL to {mac} via SSH host '{ssh_host}'")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] SSH WoL failed: {e}")
        sys.exit(4)

def main():
    if len(sys.argv) < 2:
        usage()

    # Delete the file/command and parse args
    del sys.argv[0]
    argParser = ArgParser("args.json").build()
    args = argParser.parse_args(sys.argv)

    # List hosts
    if args.list:
        list_hosts()
        return
    if args.ssh == "list":
        list_ssh_hosts()
        return

    host_name = args.name

    h = get_host_details(host_name)

    if args.ssh:
        wol_via_ssh(h, args.ssh)
    else:
        wol(h["mac"], h["address"], h["port"])
        print(f"[SUCCESS] Sent WoL to {host_name} ({h['mac']}) via {h['address']}:{h['port']}")

if __name__ == "__main__":
    main()