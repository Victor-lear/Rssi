# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 00:02:25 2023

@author: Hoai-Nam Nguyen
"""

import requests
import json
import pandas as pd 
#import math
#from math import pow
#import numpy as np
import datetime

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Login
username='apiUser'
password='x564#kdHrtNb563abcde'
vMM_aosip='140.118.151.248'

# Create CLI input ap-name list
IY = []
# IY.append(['B1F_AP01','B1F_AP03','B1F_AP05'])
IY.append(['1F_AP01','1F_AP03','1F_AP05','1F_AP07'])
IY.append(['2F_AP01','2F_AP03','2F_AP05'])
IY.append(['3F_AP01','3F_AP03','3F_AP05','3F_AP07','3F_AP09'])
IY.append(['4F_AP01','4F_AP03','4F_AP05','4F_AP07'])
IY.append(['5F_AP01','5F_AP03','5F_AP05','5F_AP07','5F_AP09'])
IY.append(['6F_AP01','6F_AP03','6F_AP05','6F_AP07','6F_AP09'])
IY.append(['7F_AP01','7F_AP03','7F_AP05','7F_AP07','7F_AP09'])
IY.append(['8F_AP01','8F_AP03','8F_AP05','8F_AP07','8F_AP09'])
IY.append(['9F_AP01','9F_AP03','9F_AP05','9F_AP07'])
IY.append(['10F_AP01','10F_AP03','10F_AP05','10F_AP07'])
IY.append(['11F_AP01'])

# Create floor list
f = []
# f.append('B1F')
f.append('1F')
f.append('2F')
f.append('3F')
f.append('4F')
f.append('5F')
f.append('6F') 
f.append('7F')
f.append('8F')
f.append('9F') 
f.append('10F')
f.append('11F')

# =============================================================================

# Login controller functions

#Get the token to access vMM information  -- via API
def authentication(username,password,aosip):
    
    url_login = "https://" + aosip + ":4343/v1/api/login"
    payload_login = 'username=' + username + '&password=' + password
    headers = {'Content-Type': 'application/json'}
    get_uidaruba = requests.post(url_login, data=payload_login, headers=headers, verify=False)

    if get_uidaruba.status_code != 200:
        print('Status:', get_uidaruba.status_code, 'Headers:', get_uidaruba.headers,'Error Response:', get_uidaruba.reason)
        uidaruba = "error"

    else:
        uidaruba = get_uidaruba.json()["_global_result"]['UIDARUBA']
        return uidaruba

#show command
def show_command(aosip,uidaruba,command):
    url_login = 'https://' + aosip + ':4343/v1/configuration/showcommand?command='+command+'&UIDARUBA=' + uidaruba
    aoscookie = dict(SESSION = uidaruba)
    AOS_response = requests.get(url_login, cookies=aoscookie, verify=False)
    
    if AOS_response.status_code != 200:
        print('Status:', AOS_response.status_code, 'Headers:', AOS_response.headers,'Error Response:', AOS_response.reason)
        AOS_response = 'error'

    else:
        AOS_response = AOS_response.json()
        
    return AOS_response

#Get the token to access vMM information  -- via API
token = authentication(username,password,vMM_aosip)

# Retrieve and process data from API

def main_loc(IY, floor):    
    df = {}
    
    for ap in IY:
        command = 'show+ap+monitor+ap-list+ap-name+IY_'+ap
        list_ap_database = show_command(vMM_aosip,token,command)
        df[ap] = pd.DataFrame(list_ap_database['Monitored AP Table'])
        df[ap]['curr-rssi'] = pd.to_numeric(df[ap]['curr-rssi'])
        df[ap] = df[ap][(df[ap]['ap-type']!='valid')
                                            &(df[ap]['essid']!='eduroam')
                                            &(df[ap]['essid']!='sensor')
                                            &(df[ap]['essid']!='NTUST-PEAP')
                                            &(df[ap]['essid']!='NTUST-UAM')][['essid','bssid','curr-rssi','ap-type', 'chan']]
        df[ap] = df[ap][(df[ap]['curr-rssi']>0)& (df[ap]['curr-rssi']<60)]

    try:
        ap1_int = df[IY[0]]['bssid']
    except Exception:
        ap1_int = None

    try:
        ap3_int = df[IY[1]]['bssid']
    except Exception:
        ap3_int = None

    try:
        ap5_int = df[IY[2]]['bssid']
    except Exception:
        ap5_int = None

    try:
        ap7_int = df[IY[3]]['bssid']
    except Exception:
        ap7_int = None

    try:
        ap9_int = df[IY[4]]['bssid']
    except Exception:
        ap9_int = None

    # Group all the interfering APs on a floor

    ap13_int = pd.concat([ap1_int,ap3_int]).reset_index(drop=True).drop_duplicates()
    try:
        ap57_int = pd.concat([ap5_int,ap7_int]).reset_index(drop=True).drop_duplicates()
        ap_all_int = pd.concat([ap13_int,ap57_int]).reset_index(drop=True).drop_duplicates()
        ap_all_int = pd.concat([ap_all_int,ap9_int]).reset_index(drop=True).drop_duplicates()
    except Exception:
        ap_all_int = ap1_int.reset_index(drop=True).drop_duplicates()
    ap_all = pd.DataFrame(ap_all_int).reset_index(drop=True)
    ap_all['essid'], ap_all['ap type'], ap_all['channel']= '','',''
    for i in range(len(ap)):
        try:
            ap_all[IY[i][-4:]] = None
        except Exception:
            pass
    ap_all['mon AP number'] = None

    for i in range(len(ap_all)):
        no_ap = 0

        for ap in IY:
            try:
            # Get essid
                ap_all['essid'][i] = list(df[ap][(df[ap]['bssid']==ap_all['bssid'][i])]['essid'])[0]
                ap_all['ap type'][i] = list(df[ap][(df[ap]['bssid']==ap_all['bssid'][i])]['ap-type'])[0]
                ap_all['channel'][i] = list(df[ap][(df[ap]['bssid']==ap_all['bssid'][i])]['chan'])[0]
            # Get rssi
                if df[ap]['bssid'].str.contains(ap_all['bssid'][i]).any():
                    ap_all[ap[-4:]][i] = -list(df[ap][df[ap]['bssid']==ap_all['bssid'][i]]['curr-rssi'])[0] 
                    no_ap+=1
            except Exception:
                pass
        ap_all['mon AP number'][i] = no_ap

    ap_all = ap_all[(ap_all['mon AP number']>0)].sort_values('essid').reset_index(drop=True).drop_duplicates()


    ap_all['xloc'], ap_all['yloc'], ap_all['floor'] = '', '', ''
    ap_all_int = ap_all['bssid']
        
    ap_all['floor'] = floor
        
    return ap_all

# =============================================================================

# Run code

df0 = main_loc(IY[0], f[0])
try:
    df1 = main_loc(IY[1], f[1])
    dfa = df0.append(df1, ignore_index=True)
except Exception:
    pass
try:
    df2 = main_loc(IY[2], f[2])
    dfa = dfa.append(df2, ignore_index=True)
except Exception:
    pass
try:
    df3 = main_loc(IY[3], f[3])
    dfa = dfa.append(df3, ignore_index=True)
except Exception:
    pass
try:
    df4 = main_loc(IY[4], f[4])
    dfa = dfa.append(df4, ignore_index=True)
except Exception:
    pass
try:
    df5 = main_loc(IY[5], f[5])
    dfa = dfa.append(df5, ignore_index=True)
except Exception:
    pass
try:
    df6 = main_loc(IY[6], f[6])
    dfa = dfa.append(df6, ignore_index=True)
except Exception:
    pass
try:
    df7 = main_loc(IY[7], f[7])
    dfa = dfa.append(df7, ignore_index=True)
except Exception:
    pass
try:
    df8 = main_loc(IY[8], f[8])
    dfa = dfa.append(df8, ignore_index=True)
except Exception:
    pass
try:
    df9 = main_loc(IY[9], f[9])
    dfa = dfa.append(df9, ignore_index=True)
except Exception:
    pass
try:
    df10 = main_loc(IY[10], f[10])
    dfa = dfa.append(df10, ignore_index=True)
except Exception:
    pass

# =============================================================================

# Add datetime (GMT +8) and timestamp

#import datetime
from datetime import timedelta

ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fz")
ts
n = 8
# Subtract 8 hours from datetime object
ts = ts - timedelta(hours=n)
ts_tw_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ts_tw = datetime.datetime.now()

data_json = json.loads(dfa.to_json(orient='records'))

for i in range(len(data_json)):
    data_json[i]['ts'] = ts 
    data_json[i]['DatetimeStr'] = ts_tw_str
    data_json[i]['Datetime'] = ts_tw

# =============================================================================

# Store json data to MongoDB
from datetime import datetime, timedelta
from pymongo import MongoClient



client = MongoClient("140.118.70.40",27017)
db = client['WiFi_Dashboard_Data']
col=db["Int_Localization2"]
## Set time to auto-delete MongoDB
#previous_day = datetime.now() - timedelta(days=30) 
# col.delete_many({"Datetime": {"$lt": previous_day}})
col.insert_many(data_json)
print('Done!')