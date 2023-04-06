import fitz

def pdf2txt(fname):
    with fitz.open(fname) as doc: # open document
        text_list = [page.get_text() for page in doc]
    return "\n\n".join(text_list)

if __name__ == '__main__':
    print(pdf2txt("C:/Users/NKWBTB/Desktop/2022.naacl-main.175.pdf").encode("utf-8"))