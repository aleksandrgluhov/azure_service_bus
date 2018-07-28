#!/usr/local/bin/python
# coding: utf-8


# imports
import os
import logging
import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from HTMLParser import HTMLParser
import xml.etree.ElementTree


# constants
work_dir = '/tmp/asb'
#import sys
#work_dir = sys.path[0]

links = []

timestamp = datetime.datetime.now().strftime('%Y%m%d')
proxy_server = ''
proxy_port = ''
proxy_url = '{}:{}'.format(proxy_server, proxy_port)
http_prefix = 'http://'
https_prefix = 'https://'

ssl_settings = False
proxy_settings = {
    'http': http_prefix + proxy_url,
    'https': https_prefix + proxy_url
}

LOGFILE = os.path.join(work_dir, '{}_{}.log'.format('asb_updater', timestamp))
logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO, filename=LOGFILE)

# classes
# тупой ХТМЛ парсер на стандартной библиотеке
class asb_parser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attr = dict(attrs)
        try:
            if '.xml' in attr['href']:
                links.append(attr['href'])
        except KeyError:
            pass


# procedures and functions
def ipset_file(region):
    return os.path.join(work_dir, 'azure_sb_{}_{}.txt'.format(region, timestamp))


def cleanup():
    for root, dirs, files in os.walk(work_dir):
        for filename in files:
            if '.txt' in filename:
                logging.info('removing ip list file:\t' + os.path.join(work_dir, filename))
                os.remove(os.path.join(work_dir, filename))


# program entry point
if __name__ == '__main__':
    cleanup()
    # You need this if your company bumping ssl connections on proxy
    requests.packages.urllib3.disable_warnings()

    # Ip list download hyperlink
    url = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=41653'

    # Initialize parser
    parser = asb_parser()
    # with proxy
    #parser.feed(requests.get(url, proxies=proxy_settings, verify=ssl_settings).content)

    # without proxy
    parser.feed(requests.get(url).content)

    # obtain raw xml
    asb_xml = requests.get(links[0], proxies=proxy_settings, verify=ssl_settings).content

    # get azure regions
    azure_regions = xml.etree.ElementTree.fromstring(asb_xml)

    # save ips in txt files by region
    for region in azure_regions:
        
        region_name = region.attrib['Name']
        logging.info('writing ip list file:\t' + ipset_file(region_name))
        
        with open(ipset_file(region_name), 'w') as region_stream:
            
            # get every ip 
            for index, ip in enumerate(region):
                region_stream.write(ip.attrib['Subnet'])

                # if it's a last ip, we need to avoid of a newline at the end of a file,
                # or ipfw will crash
                if index < len(region)-1:
                    region_stream.write('\n')
