#!/usr/bin/env python3

import requests
import time
import sqlite3
import os
import argparse


dxdoi = 'https://doi.org/'


def db_get_document_ids(cursor, group_name=''):
    if group_name:
        query = ('SELECT documentId FROM RemoteDocuments'
                 ' JOIN Groups ON Groups.id=RemoteDocuments.groupId'
                 ' WHERE Groups.name="' + group_name + '"')
    else:
        query = 'SELECT id from Documents'
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


def db_get_url(cursor, id):
    query = ('select url from DocumentUrls where documentId='
             + str(id))
    cursor.execute(query)
    res = cursor.fetchone()
    return res[0] if res else ''


def db_get_title(cursor, id):
    query = 'select title from Documents where id=' + str(id)
    cursor.execute(query)
    res = cursor.fetchone()
    return res[0]


def doi2link(doi):
    '''
    Make request to dx.doi.org, and follow redirects
    '''
    res = ''
    # known issue
    # known = {'10.1111/1567-1364.12028':
    #          'https://onlinelibrary.wiley.com/doi/full/10.1111/1567-1364.12028'}
    # if doi in known:
    #     return known[doi]
    try:
        r = requests.get(dxdoi + doi)
        r.close()
        res = r.url
    except Exception:
        print('Error during requesting doi link')
    return res


def full_text_url(url):
    url = url.strip()
    if type(url) == bytes:
        url = url.decode('utf8')
    if url.startswith('http://aem.asm.org') and not url.endswith('.full'):
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

            
def download_html_for_ids(cursor, ids, outdir, prefer):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for id in ids:
        print('=== processing ' + str(id) + ' ..')
        outfile = os.path.join(outdir, str(id) + '.html')
        if not os.path.exists(outfile):
            doi = db_get_doi(cursor, id)
            url = db_get_url(cursor, id)
            print('getting url ..')
            if prefer == 'url':
                url = url if url else doi2link(doi)
            else:
                doiurl = doi2link(doi)
                url = doiurl if doiurl else url
            if not url:
                print('no url available')
            else:
                download_html(url, outfile)
                print('sleeping 5 sec ..')
                time.sleep(5)

                
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--group',
                        help='group name')
    parser.add_argument('--prefer', choices=['url', 'doi'],
                        default='doi',
                        help='In case of url is provided, which one to prefer')
    parser.add_argument('-o', '--output', default='html_output',
                        help='Output folder')
    parser.add_argument('db', help='database file')
    args = parser.parse_args()
    conn = sqlite3.connect(args.db)
    cursor = conn.cursor()
    ids = db_get_document_ids(cursor, args.group)
    print('number of documents: ' + str(len(ids)))
    download_html_for_ids(cursor, ids, args.output, args.prefer)



# Testing Code
if __name__ == '__test__':
    db_file = '/home/hebi/.local/share/data/Mendeley Ltd./Mendeley Desktop/lihebi.com@gmail.com@www.mendeley_old_code_base.com.sqlite'

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    groups = db_get_groups(cursor)
    ids = db_get_document_ids(cursor, "NSF project")

    for id in ids:
        print(id)
        print(db_get_doi(cursor, id))

    download_html_for_ids(cursor, ids, 'html_output', 'doi')
    db_get_url(cursor, 67)

    doi2link('10.1111/1567-1364.12028')

    for id in ids:
        print(id)
        print(db_get_url(cursor, id))


    print(doi2link('10.1016/j.ymben.2015.03.003'))
    doi = '10.1016/j.ymben.2015.03.003'
    r = requests.get(dxdoi + doi)

    db_get_title(cursor, 67)

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
