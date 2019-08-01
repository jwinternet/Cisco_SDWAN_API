#! /usr/bin/env python

import requests
import sys
import json
import os
import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SDWAN_IP = '10.10.20.90'
SDWAN_USERNAME = input('Username: ')
SDWAN_PASSWORD = input('Password: ')
NODE_IP = input('Enter device IP: ')

class rest_api_lib:
    def __init__(self, vmanage_ip, username, password):
        self.vmanage_ip = vmanage_ip
        self.session = {}
        self.login(self.vmanage_ip, username, password)

    def login(self, vmanage_ip, username, password):
        """Login to vmanage"""
        base_url_str = 'https://%s:8443/'%vmanage_ip
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
        url = "https://%s:8443/dataservice/%s"%(self.vmanage_ip, mount_point)
        response = self.session[self.vmanage_ip].get(url, verify=False)
        data = response.content
        return data

sdwanp = rest_api_lib(SDWAN_IP, SDWAN_USERNAME, SDWAN_PASSWORD)

def system_status():
    sys_status = ('device/system/status?deviceId=' + NODE_IP)
    response = json.loads(sdwanp.get_request(sys_status))
    items = response['data']
    table = list()
    for item in items:
        tr = [
            item['config_date/date-time-string'],
            item['uptime']]
        table.append(tr)
    print('\nSystem Status:')
    print("CLOCK                              UPTIME")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))

def hardware_environment():
    hw_env = ('device/hardware/environment?deviceId=' + NODE_IP)
    response = json.loads(sdwanp.get_request(hw_env))
    items = response['data']
    table = list()
    for item in items:
        tr = [
            item['hw-item'],
            item['hw-dev-index'],
            item['status']]
        table.append(tr)
    print('\nPower Supply Status:')
    print("POWER SUPPLY           #       STATUS")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))

def bfd_sessions():
    bfd_sess = ('device/bfd/sessions?deviceId=' + NODE_IP + '&&&')
    response = json.loads(sdwanp.get_request(bfd_sess))
    items = response['data']
    table = list()
    for item in items:
        tr = [
            item['state'],
            item['color'],
            item['uptime']]
        table.append(tr)
    print('\nBFD Session Status:')
    print("STATE   COLOR       UPTIME")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))

def app_route_stats():
    app_route = ('device/app-route/statistics?deviceId=' + NODE_IP + '&&&')
    response = json.loads(sdwanp.get_request(app_route))
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
    print("COLOR     LOSS  LATENCY  JITTER")
    s = [[str(e) for e in row] for row in table]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t\t'.join('{{:{}}}'.format(x) for x in lens)
    tab = [fmt.format(*row) for row in s]
    print('\n'.join(tab))



'''
def interface_description():
    int_desc = ('device/interface/synced?deviceId=' + NODE_IP + '&&&')
    response = json.loads(sdwanp.get_request(int_desc))
    items = response['data']
    headers = ["Interface", "Status", "Description"]
    table = list()

    for item in items:
        tr = [item['ifname'], item['if-oper-status'], item['desc']]
        table.append(tr)
    print('\nApp Route Stats:')
    print(headers)
    print(*table, sep = "\n")
'''

if __name__ == "__main__":
    system_status()
    hardware_environment()
    bfd_sessions()
    app_route_stats()
    #interface_description()
