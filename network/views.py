from django.shortcuts import render
from .forms import NetworkForm
from .mongodb import get_db
from datetime import datetime
import random
import ipaddress

lease_table = {}

def generate_ipv4():
    base = ipaddress.IPv4Address("192.168.1.0")
    while True:
        offset = random.randint(2, 254)
        ip = str(base + offset)
        if ip not in lease_table.values():
            return ip

def eui64_from_mac(mac):
    parts = mac.split(":")
    mac_bytes = [int(p, 16) for p in parts]

    mac_bytes[0] ^= 0b00000010

    eui64 = mac_bytes[:3] + [0xFF, 0xFE] + mac_bytes[3:]

    ipv6_parts = [
        (eui64[i] << 8) + eui64[i + 1]
        for i in range(0, 8, 2)
    ]
    ipv6_addr = "2001:db8::{:x}:{:x}:{:x}:{:x}".format(*ipv6_parts)
    return ipv6_addr

def index(request):
    assigned_ip = None
    mac_address = None
    dhcp_version = None

    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            mac_address = form.cleaned_data['mac_address']
            dhcp_version = form.cleaned_data['dhcp_version']

            lease_key = f"{mac_address}_{dhcp_version}"

            if lease_key in lease_table:
                assigned_ip = lease_table[lease_key]
                print(f"DEBUG: Existing lease found: {assigned_ip}")
            else:
                if dhcp_version == 'DHCPv4':
                    assigned_ip = generate_ipv4()
                elif dhcp_version == 'DHCPv6':
                    assigned_ip = eui64_from_mac(mac_address)
                lease_table[lease_key] = assigned_ip
                print(f"DEBUG: New IP assigned: {assigned_ip}")

            # Save to MongoDB
            collection = get_db()
            collection.insert_one({
                "mac_address": mac_address,
                "dhcp_version": dhcp_version,
                "assigned_ip": assigned_ip,
                "lease_time": "3600 seconds",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            print("DEBUG: Saved to MongoDB")

    else:
        form = NetworkForm()

    return render(request, 'network/index.html', {
        'form': form,
        'assigned_ip': assigned_ip,
        'mac_address': mac_address,
        'dhcp_version': dhcp_version
    })

def leases(request):
    collection = get_db()
    all_leases = list(collection.find())
    return render(request, 'network/leases.html', {
        'leases': all_leases
    })
