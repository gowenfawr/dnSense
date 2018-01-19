#!/usr/bin/python3

import bisect
import collections
import datetime
import dns.resolver as dr
import sys
import time

dName = collections.namedtuple('dName', ['expiry', 'name'])
dNames = []

# Future: Fork thread for each IP in resolvers

# Lookup and sorted insertion based on record expiry
def cacheify_Name(item):
    global dNames
    answers = dr.query(item.name)
    # Default to this, but tweak later
    ttl = time.time()+1
    for answer in answers.response.answer:
        # Note, answers.expiration is the /least/ TTL of all answers
        # Many providers have name TTL of 60s and CNAME -> IP of 1s!
        if str(answer.name) == item.name+'.':
            ttl += answer.ttl
            break
    bisect.insort(dNames, dName(ttl, item.name))


# create a list of tuples (name, expiry) based on input file
def create_List(file):
    global dNames
    with open(file, 'r') as fp:
        for line in fp:
            name = line.rstrip()
            cacheify_Name(dName(0, name))

def dumb_Stamp(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# For each record in dnSense.names
# Resolve name and grab the expiration
## Sort name into chain based on expiration time
#
# Loop at first ('shortest') record in chain
# Sleep until that time
# Resolve name and grab the expiration
## Sort name into chain based on expiration time


create_List('dnSense.names')
for item in dNames:
    print('{} expires at {} ({})'.format(item.name, item.expiry, dumb_Stamp(item.expiry)))

while True:
    print(dNames)
    if len(dNames) == 0:
        print('Error! List of names is empty!')
        sys.exit(1)
    now = time.time()
    if now > dNames[0].expiry:
        print('{} has expired at {}, re-cacheifying'.format(dNames[0].name, dumb_Stamp(time.time())))
        cacheify_Name(dNames[0])
        dNames = dNames[1:]        
    else:
        #time.sleep(dNames[0].expiry - now)
        diff = dNames[0].expiry - now
        print('Sleeping from now until {} ({}, roughly {} seconds)'.format(dNames[0].expiry, dumb_Stamp(dNames[0].expiry), diff))
        time.sleep(diff)
