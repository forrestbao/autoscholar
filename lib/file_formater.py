import sqlite3
import convert_local_url
from sqlite3 import Error
import get_highlighted_text

import csv


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)

        print("connecting to database success")

        return conn
    except Error as e:
        print(e)

    return None

def select(conn, ourdir):
    cur = conn.cursor()

    cur.execute('''SELECT Files.localUrl, FileHighlightRects.page,
                    FileHighlightRects.x1, FileHighlightRects.y1,
                    FileHighlightRects.x2, FileHighlightRects.y2,
                    FileHighlights.documentId,
                    Documents.title
            FROM Files
            LEFT JOIN FileHighlights
                ON FileHighlights.fileHash=Files.hash
            LEFT JOIN FileHighlightRects
                ON FileHighlightRects.highlightId=FileHighlights.id
            LEFT JOIN DocumentFolders
                ON DocumentFolders.documentId=FileHighlights.documentId
			LEFT JOIN Folders
                ON Folders.id=DocumentFolders.folderid
			LEFT JOIN Documents
				ON Documents.id = FileHighlights.documentId
            WHERE ((FileHighlightRects.page IS NOT NULL) AND (DocumentFolders.folderid IS NULL)  AND (FileHighlights.documentId<43))
			order by FileHighlights.documentId;
''')
    rows = cur.fetchall()
    each_line=[]
    count=1
    for r in rows:
        #annotations={}
        #file_name,highlight_text_list=get_highlighted_text.get_highlight(conn,ourdir,annotations,[r[6]])
        each_line.append([count,r[6],r[7],convert_local_url.converturl2abspath(r[0]),r[1],r[2],r[3],r[4],r[5],])
        count=count+1
    return each_line

def main():

    '''
    Change the values to the two variables below ("database_file" and "output_filename") to your file directories

    For example:

    Absolute path for the database file:
        database_file = "C:\Users\Todd Li\AppData\Local\Mendeley Ltd\Mendeley Desktop\junteng@iastate.edu@www.mendeley.com.sqlite"

    Or relative path for the output file:
        output_filename="output.csv"    

    '''

    database_file = "/home/todd/.local/share/data/Mendeley Ltd./Mendeley Desktop/junteng@iastate.edu@www.mendeley.com.sqlite"
    output_filename="/home/todd/RA/output/1234/output1.csv"
    #outdir = "/home/todd/RA/output/1234"
    

    conn = create_connection(database_file)
    data=select(conn,outdir)

    print("writting to file...")

    with open(output_filename, 'wb+') as mf:
        wr = csv.writer(mf)  
        for d in data:
            wr.writerow(d)

    print("Done!")


if __name__ == '__main__':
    main()