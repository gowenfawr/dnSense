#!/usr/bin/python3

import argparse
import bisect
import collections
import datetime
import dns.resolver as dr   # From 'dnspython'
import IPy
import sys
import threading
import time

parser = argparse.ArgumentParser(description='Preventative treatment for DNS Cache Snooping')
parser.add_argument('-r', metavar='RESOLVERS', help='comma separated list of resolver IPs')
args = parser.parse_args()

dName = collections.namedtuple('dName', ['expiry', 'name'])
dNames = []

def log(tag, message):
    print('dnSense={} {}'.format(tag, message))

# create a list of tuples (name, expiry) based on input file
def create_List(file):
    global dNames
    with open(file, 'r') as fp:
        for line in fp:
            name = line.rstrip()
            dNames.append(dName(0, name))

def dumb_Stamp(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')

def cache_Filler(ip, names):
    ns = dr.Resolver(configure=False)
    ns.nameservers = [ip]
    while True:
        now = time.time()
        if now > names[0].expiry:
            log('cache', 'nameserver={} name={} expired={} now={}'.format(ip, names[0].name, dumb_Stamp(names[0].expiry), dumb_Stamp(now)))
            answers = dr.query(names[0].name)
            # Default to this, but tweak later
            ttl = time.time()+1
            for answer in answers.response.answer:
                # Note, answers.expiration is the /least/ TTL of all answers
                # Many providers have name TTL of 60s and CNAME -> IP of 1s!
                if str(answer.name) == names[0].name+'.':
                    ttl += answer.ttl
                    break
            bisect.insort(names, dName(ttl, names[0].name))
            names = names[1:]
        else:
            diff = names[0].expiry - now
            log('sleep', 'nameserver={} until={} seconds={:.1f}'.format(ip, dumb_Stamp(names[0].expiry), diff))
            time.sleep(diff)


#
# Determine which nameservers to keep filled.
#
nameservers = []
if args.r:
    rlist = args.r.split(',')
    for ip in rlist:
        try:
            IPy.IP(ip)
            nameservers.append(ip)
        except:
            print('Resolver {} is not a valid IP address... Exiting.'.format(ip))
            sys.exit(1)
    log('conf', 'nameservers_from=command_line')
else:
    nameservers = dr.get_default_resolver().nameservers
    log('conf', 'servers_from=default_resolver')
log('conf', 'nameservers={}'.format(','.join(nameservers)))

#
# Determine which names to keep filled in.
#
create_List('dnSense.names')
for item in dNames:
    log('conf', 'name={} expiry={} stamp={}'.format(item.name, item.expiry, dumb_Stamp(item.expiry)))


#
# Spawn a thread per nameserver
#
threads = []
for item in nameservers:
    t = threading.Thread(target=cache_Filler, args=(item, dNames,))
    threads.append(t)
    t.start()

