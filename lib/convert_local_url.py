import sys,os
import sqlite3
import argparse
import pandas as pd
from lib import extracttags
from lib import extractnt
from lib import exportpdf
from lib import exportannotation
from lib import export2bib
from lib import export2ris
from lib.tools import printHeader, printInd, printNumHeader
#from html2text import html2text
from bs4 import BeautifulSoup
from datetime import datetime
from urllib import unquote
from urlparse import urlparse

def converturl2abspath(url):
            
            if url[5:8]==u'///':   
                        url=u'file://'+url[8:]
                        path=urlparse(url)
                        path=os.path.join(path.netloc,path.path)
                        path=unquote(str(path)).decode('utf8')
                        path=os.path.abspath(path)
                        return path





def main():
	url = converturl2abspath("file:///C:/Users/Todd%20Li/AppData/Local/Mendeley%20Ltd./Mendeley%20Desktop/Downloaded/Ida%20et%20al.%20-%202015%20-%20Eliminating%20the%20isoleucine%20biosynthetic%20pathway%20to%20reduce%20competitive%20carbon%20outflow%20during%20isobutanol%20production%20by.pdf")

	print(url)

if __name__ == '__main__':
    main()











