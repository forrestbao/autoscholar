import csv
import sqlite3
from sqlite3 import Error
import sys,os
import lib.menotexport as menotexport

def create_connection(db):
    try:
        conn = sqlite3.connect(db)

        print("success")

        return conn
    except Error as e:
        print(e)

    return None


def get_docid(conn):
    cur = conn.cursor()
    cur.execute('''SELECT Documents.id
       FROM Documents
       LEFT JOIN DocumentFolders
           ON DocumentFolders.documentId=Documents.id
	   LEFT JOIN FileHighlights
           ON DocumentFolders.documentId=FileHighlights.documentId
	   LEFT JOIN Files
		   ON FileHighlights.fileHash=Files.hash
       WHERE (DocumentFolders.folderId IS NULL)


	   order by Documents.id''')

    rows = cur.fetchall()
    docid=[]
    for r in rows:
        docid.append(r[0])
    return docid


def main(data_base_file,abspath_filename):     

    outdir,output_filename=os.path.split(abspath_filename)

    conn = create_connection(data_base_file)

    annotations = {}

    action = ['m']

    canonical_doc_ids = get_docid(conn)

    allfolders=True

    separate= True

    iszotero= False

    verbose= True

    f1,f2,f3,f4,ret,highlight_text_list2=menotexport.processCanonicals(conn,outdir,annotations,canonical_doc_ids,allfolders,action,separate,iszotero,verbose)

    counter=1
    with open(abspath_filename, 'wb+') as mf:
        wr= csv.writer(mf)
        for reti in ret:
            for retii in reti:
                wr.writerow(retii)
		    
