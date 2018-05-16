#!/usr/bin/env python3

import requests
import time
import urllib3


dxdoi = 'http://dx.doi.org/'

def doi2link(doi):
    '''
    Make request to dx.doi.org, and follow redirects
    '''
    r = requests.get(dxdoi + doi)
    r.close()
    return r.url

def download_html(name, url):
    r = requests.get(url)
    with open(name + '.html') as f:
        f.write(r.content)

if __name__ == '__hebi__':
    print(doi2link('10.1016/j.ymben.2015.03.003'))
    doi = '10.1016/j.ymben.2015.03.003'
    r = requests.get(dxdoi + doi)

    print(doi2link('10.1111/1567-1364.12028'))

    r = requests.get('http://aem.asm.org/content/78/5/1611.full')
    r = requests.get('https://onlinelibrary.wiley.com/doi/full/10.1002/bit.25683')
    with open('test.html', 'wb') as f:
        f.write(r.content)
    r.close()

    token = 'D20E58439E3F7E0DA93AC68109F3114DE934C22FD44F6BF8B881601CB7EEED6D4311AF0E1F1CB0D0'
    
    id='S1096717606001042'
    url = 'https://www.sciencedirect.com/sdfe/arp/pii/' + id + '/body'
    payload = {'entitledToken': token}

    url='https://www.sciencedirect.com/sdfe/arp/pii/S1096717606001042/body?entitledToken=E1257F057819F6FDD10004536A3BB09EA5E69BB57D07A218D3133668D30CC6F4692A645410721384'
    r = requests.get(url)

    full_url = url + '?entitledToken=' +token
    res = urllib.request.urlopen(full_url)
    
    r = requests.get(url, params=payload)

    id='S1096717606001042'
    token='1C689D45D57E8979D321EEAA16E5F8B2C42AABA7ABF5F3B3B0844F8A58A6EC8F4B8BB0742FC554CA'
    orig_url = 'https://linkinghub.elsevier.com/retrieve/pii/' + id
    json_url = 'https://www.sciencedirect.com/sdfe/arp/pii/' + id + '/body?entitledToken=' + token
    r = requests.get(orig_url)
    jar = r.cookies
    r = requests.get(json_url, cookies=jar)

    # read dois.txt
    # for each doi, get real urls, write to urls.txt

    for line in open('dois.txt'):
        try:
            print(line, end='')
            link = doi2link(line)
            print(link)
            time.sleep(5)
        except Exception as e:
            print('ConnectionError')
