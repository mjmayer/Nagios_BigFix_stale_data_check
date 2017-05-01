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
parser.add_argument('-C', '--computers',
                    help='Number of computers to look for in the past timeframe')
parser.add_argument('-M', '--minutes', help='Number of minutes to look for last checkin',
                    default='60')
args = parser.parse_args()

BIGFIX_API_URL = 'https://bigfix.ucdavis.edu:52311/api/'

#open bigfix session
bigfix_session = BigFix(BIGFIX_API_URL, args.bigfixlogin, args.bigfixpass)
bigfix_session.authenticate()

#changes the timeframe to look at
params = {
    'relevance' : 'number of elements of set of ((values whose (it as time > '
                  '(now - ' + args.minutes + '*minute)) of it) '
                  'of results of bes properties whose (Name of it = "Last Report Time"))'
    }
#query bigfix
xml_result = bigfix_session.get('query', params)
xml_result = xml_result.encode('utf-8')
root = etree.fromstring(xml_result)
result = [ x.text for x in root[0][0].findall('Answer')][0]
result = int(result)
if result > 100:
    print("OK - %s BES Computers reported" % result)
    sys.exit(0)
elif result < 100 and result > 50:
    print("WARNING - %s BES Computers reported." % result)
    sys.exit(1)
elif result < 50:
    print("CRITICAL - %s BES Computers reported." % result)
    sys.exit(2)
else:
    print("UKNOWN - %s of disk space used." % result)
    sys.exit(3)
