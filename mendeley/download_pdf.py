from urllib.request import Request, urlopen
import json
import os, time

def download(url, path):
    try:
        print('Downloading', url, path)
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0')
        data = urlopen(req, timeout=10).read()
        with open(path, "wb") as w:
            w.write(data)
    except Exception as e:
        print(e)

def main():
    data = []
    outputpath = "./pdfs/"
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    with open("annot.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for doc in data:
        print("Downloading...", doc['doc_title'])
        id = doc['doc_id']
        url = doc['url']
        download(url, os.path.join(outputpath, id+'.pdf'))
        time.sleep(1)

if __name__ == "__main__":
    main()