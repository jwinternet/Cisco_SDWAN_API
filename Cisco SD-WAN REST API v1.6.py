#!/usr/bin/python3.4

################################################################################
# Branch Network Health Program
# - Used for doing a a health check of a branch network
# - Last modified - 7/26/19
################################################################################
# To Do List
# - 
################################################################################

import requests
import sys
import json
import os
import pprint
import subprocess
import socket
#import netmiko
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

################################################################################
# FORMATTING LEGEND:
#  tab, newline, vertical tab, formfeed, and carriage return ('\t\n\v\f\r').
################################################################################

SDWAN_VMANAGE = '10.10.20.90'
SDWAN_USERNAME = input('Username: ')
SDWAN_PASSWORD = getpass.getpass('Password: ')
the_id = input("Enter the branch ID: ")

def hostname_resolves(hostname):
        try:
                socket.gethostbyname(hostname)
                return 1
        except socket.error:
                return 0

viptela_a_hostname = "u-" + the_id + "-a01a"
viptela_b_hostname = "u-" + the_id + "-a01b"
viptela_a_resolves = hostname_resolves(viptela_a_hostname)

branch_validated = False
while not branch_validated:
        if viptela_a_resolves == 1:
                branch_validated = True
        else:
                print("That branch ID is invalid.")
                quit()

print("\nBranch ID: " + the_id)
addr1 = socket.gethostbyname_ex(viptela_a_hostname)
addr2 = str(addr1[2])
viptela_a_ip = addr2.replace('[','').replace(']','').replace('\'','')
addr4 = viptela_a_ip[:-3]
print("Branch Subnet: " + addr4 + "0\n")

addr1 = socket.gethostbyname_ex(viptela_b_hostname)
addr2 = str(addr1[2])
viptela_b_ip = addr2.replace('[','').replace(']','').replace('\'','')

################################################################################

class rest_api_lib:
    def __init__(self, vmanage_ip, username, password):
        self.vmanage_ip = vmanage_ip
        self.session = {}
        self.login(self.vmanage_ip, username, password)

    def login(self, vmanage_ip, username, password):
        """Login to vmanage"""
        base_url_str = 'https://%s:443'%vmanage_ip
        login_action = '/j_security_check'
        login_data = {'j_username' : username, 'j_password' : password}
        login_url = base_url_str + login_action
        sess = requests.session()
        login_response = sess.post(url=login_url, data=login_data, verify=False)

        if b'<html>' in login_response.content:
            print ("Login Failed")
            sys.exit(0)

        self.session[vmanage_ip] = sess

    def get_request(self, mount_point):
        """GET request"""
        url = "https://%s:443/dataservice/%s"%(self.vmanage_ip, mount_point)
        response = self.session[self.vmanage_ip].get(url, verify=False).json()
        data = response
        return data

################################################################################
# Main Program
################################################################################

sdwanp = rest_api_lib(SDWAN_VMANAGE, SDWAN_USERNAME, SDWAN_PASSWORD)

def system_status(nodes):
    sys_status = ('device/system/status?deviceId=' + nodes)
    response = (sdwanp.get_request(sys_status))
    items = response['data']
    table = list()
    for item in items:
        tr = [
            item['config_date/date-time-string'],
            item['uptime']]
        table.append(tr)
    print('\nSystem Status:')
    print("CLOCK\t\t\t\t\tUPTIME")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))

def hardware_environment(nodes):
    hw_env = ('device/hardware/environment?deviceId=' + nodes)
    response = (sdwanp.get_request(hw_env))
    items = response['data']
    table = list()
    for item in items:
        tr = [
            item['hw-item'],
            item['hw-dev-index'],
            item['status']]
        table.append(tr)
    print('\nHardware Status:')
    print("HARDWARE\t\t\tNUMBER\t\tSTATUS")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))

def bfd_sessions(nodes):
    bfd_sess = ('device/bfd/sessions?deviceId=' + nodes + '&&&')
    response = (sdwanp.get_request(bfd_sess))
    items = response['data']
    table = list()
    for item in items:
        tr = [
            item['state'],
            item['local-color'],
            item['uptime']]
        table.append(tr)
    print('\nBFD Session Status:')
    print("STATE\t\tCOLOR\t\t\tUPTIME")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))

def app_route_stats(nodes):
    app_route = ('device/app-route/statistics?deviceId=' + nodes + '&&&')
    response = (sdwanp.get_request(app_route))
    items = response['data']
    table = list()
    for item in items:
        tr = [
            item['local-color'],
            item['loss'],
            item['average-latency'],
            item['average-jitter']]
        table.append(tr)
    print('\nApp Route Stats:')
    print("TLOC COLOR\t\tLOSS\t\tLATENCY\t\tJITTER")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))

def interface_description(nodes):
    int_desc = ('device/interface?deviceId=' + nodes + '&&&')
    response = (sdwanp.get_request(int_desc))
    items = response['data']
    table = list()
    for item in items:
        tr = [
            item['ifname'],
            item['if-oper-status']]
            #item['desc']]
        table.append(tr)
    print('\nInterface Descriptions:')
    print("INTERFACE\t\tSTATUS\t\tDESCRIPTION")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))

################################################################################

if __name__ == "__main__":
    print("\n\nVIPTELA A STATUS")
    system_status(viptela_a_ip)
    hardware_environment(viptela_a_ip)
    bfd_sessions(viptela_a_ip)
    app_route_stats(viptela_a_ip)
    interface_description(viptela_a_ip)
    print("\n\nVIPTELA B STATUS")
    system_status(viptela_b_ip)
    hardware_environment(viptela_b_ip)
    bfd_sessions(viptela_b_ip)
    app_route_stats(viptela_b_ip)
    interface_description(viptela_b_ip)

print('\n\r')

################################################################################
# End of script.
