#!/usr/bin/env python3

import requests
import time
import sqlite3
import os
import argparse


dxdoi = 'http://dx.doi.org/'

def db_get_document_ids(cursor, group_name):
    query = ('SELECT documentId FROM RemoteDocuments'
             ' JOIN Groups ON Groups.id=RemoteDocuments.groupId'
             ' WHERE Groups.name="' + group_name + '"')
    cursor.execute(query)
    res = cursor.fetchall()
    return list(map(lambda x: x[0], res))

def db_get_groups(cursor):
    query = "SELECT name FROM Groups"
    cursor.execute(query)
    res = cursor.fetchall()
    return list(filter(lambda x: x, list(map(lambda x: x[0], res))))

def db_get_doi(cursor, id):
    query = "SELECT doi FROM Documents where id=" + str(id)
    cursor.execute(query)
    res = cursor.fetchone()
    return res[0]


def doi2link(doi):
    '''
    Make request to dx.doi.org, and follow redirects
    '''
    res = ''
    # known issue
    known = {'10.1111/1567-1364.12028':
             'https://onlinelibrary.wiley.com/doi/full/10.1111/1567-1364.12028'}
    if doi in known:
        return known[doi]
    try:
        r = requests.get(dxdoi + doi)
        r.close()
        res = r.url
    except Exception:
        print('Error during requesting doi link')
    return res

def full_text_url(url):
    if url.startswith('http://aem.asm.org'):
        return url + '.full'
    elif url.startswith('https://onlinelibrary.wiley.com'):
        return url.replace('abs', 'full')
    else:
        return url

def download_html(url, filename):
    url = full_text_url(url)
    print('downloading ' + url + ' into ' + filename + ' ...')
    if url.startswith('https://linkinghub.elsevier.com'):
        print('using save_page_as to download ..')
        os.system('save_page_as "' + url
                  + '" --browser "firefox" --destination '
                  + filename)
    else:
        r = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)

def download_html_for_group(db_file, group_name):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    ids = db_get_document_ids(cursor, group_name)
    print('number of documents: ' + str(len(ids)))
    for id in ids:
        print('=== processing document ID: ' + str(id))
        doi = db_get_doi(cursor, id)
        print('querying url ..')
        url = doi2link(doi)
        if url:
            filename = str(id) + '.html'
            download_html(url, filename)
            print('sleeping 5 sec ..')
            time.sleep(5)
            
if __name__ == '__hebi__':
    db_file = '/home/hebi/.local/share/data/Mendeley Ltd./Mendeley Desktop/lihebi.com@gmail.com@www.mendeley.com.sqlite'

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    groups = db_get_groups(cursor)
    ids = db_get_document_ids(cursor, "NSF project")

    download_html_for_group(db_file, "NSF project")
    

    print(doi2link('10.1016/j.ymben.2015.03.003'))
    doi = '10.1016/j.ymben.2015.03.003'
    r = requests.get(dxdoi + doi)

    print(doi2link('10.1111/1567-1364.12028'))
    with open('test.html', 'wb') as f:
        f.write(r.content)
    r.close()

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--group',
                        help='group name', required=True)
    parser.add_argument('db', help='database file')
    args = parser.parse_args()
    download_html_for_group(args.db, args.group)
