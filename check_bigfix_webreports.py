import requests
import argparse
import os, sys
from BigFix import BigFix
from lxml import etree

#argument parser
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-bigfix', '--bigfixlogin',
                    help="BigFix Login ID (Need to escape '\\' by using ''\\\\''")
parser.add_argument('-P', '--bigfixpass', help='BigFix Password/Passphrase')
parser.add_argument('-c', '--computers',
                    help='Number of computers to look for in the past timeframe', type=int)
parser.add_argument('-M', '--minutes', help='Number of minutes to look for last checkin',
                    default='60', type=int)
parser.add_argument('-U', '--url', help='BigFix API URL')
parser.add_argument('-W', '--warn', help='Threshold for warning', type=int)
parser.add_argument('-C', '--critical', help='Threshold for critical', type=int)
args = parser.parse_args()

BIGFIX_API_URL = args.url

#open bigfix session
bigfix_session = BigFix(BIGFIX_API_URL, args.bigfixlogin, args.bigfixpass)
bigfix_session.authenticate()

#changes the timeframe to look at
params = {
    'relevance' : 'number of elements of set of ((values whose (it as time > '
                  '(now - ' + str(args.minutes) + '*minute)) of it) '
                  'of results of bes properties whose (Name of it = "Last Report Time"))'
    }
#query bigfix
xml_result = bigfix_session.get('query', params)
xml_result = xml_result.encode('utf-8')
root = etree.fromstring(xml_result)
result = [ x.text for x in root[0][0].findall('Answer')][0]
result = int(result)
if result >= args.warn:
    print("OK - %s BES Computers reported" % result)
    sys.exit(0)
elif result < args.warn and result > args.critical:
    print("WARNING - %s BES Computers reported." % result)
    sys.exit(1)
elif result <= args.critical:
    print("CRITICAL - %s BES Computers reported." % result)
    sys.exit(2)
else:
    print("UKNOWN - %s of disk space used." % result)
    sys.exit(3)
