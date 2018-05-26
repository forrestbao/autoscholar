# Extract text information of a paper from the publisher's website 
# Copyleft 2018 Forrest Sheng Bao, Iowa State University
# AGPL 3.0 
import bs4

def file2text(filename):
    """open a file and extract sentences from a paper. 
    """
    with open(filename, 'r') as f:
        html = f.read()

    publisher = determine_publisher(html)

    if publisher == "elsevier":
        text = html2text_elsevier(html)
    elif publisher == "nature":
        text = html2text_nature(html)
    elif publisher == "springer":
        text = html2text_springer(html)

    return text

def children2string(BS4Tag):
    """Given a BS4 tag, concatenate all its children to into a string 
    """
    return "".join(map(str, list(BS4Tag.children)))

def decompose_list(List):
    """remove elements of List from parsing tree
    """
    for element in List:
        element.decompose()

def taglist2stringlist(taglist):
    """Given a list BS4 tag, one string for all children of each of them. 
    """

    return list(map(children2string, taglist))

def determine_publisher(html):
    """Determine the publisher based on the meta info in HTML

    Args:
        html (str): a string in HTML syntax

    Returns:
        str: a string \in {nature, springer, elsevier, bmc, wiley}

    """
    soup = bs4.BeautifulSoup(html, 'html.parser')

    publisher_url_tag = soup.find("meta", {"name":"citation_pdf_url"})
    citation_pdf_url = publisher_url_tag["content"]

    if "sciencedirect.com" in citation_pdf_url:
        return "elsevier"
    elif "asm.org" in citation_pdf_url:
        return "asm"
    elif "nature.com" in citation_pdf_url:
        return "nature"
    elif "biomedcentral.com" in citation_pdf_url:
        return "bmc"
    elif "springer.com" in citation_pdf_url:
        return "springer"
    elif "embopress.org" in citation_pdf_url:
        return "embo"
    else:
        return "WARNING"
 
def html2text_nature(html):
    """Extract text from an Elsevier HTML page 

    Args:
        html (str): a string in HTML syntax 

    Returns:
        (bs4.element.ResultSet, bs4.element.ResultSet): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <p> and <td> tags are preserved
    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    
    article = soup.find('article') # get article node
#    body = article.find('div', {'class':'article-body clear'}) # the part without title, abstract, 
    body = article.find('div', {"data-track-component":"article body"}) # the part without title, abstract, 

# Under body, a paper is segmented into <section>s, each of which contain many <p> nodes
    sections  = body.find_all("section")
    true_body = [section for section in sections if section["aria-labelledby"] in ["abstract", "main", "results", "discussion", "methods"]]

    paragraphs, table_cells = [], []
    for section in true_body:
        paragraphs += section.find_all('p') # includes plain paragraphs and detailed captions under figures
        table_cells += section.find_all('td')
#    figure_captions = 

    for cell in table_cells:
        cell.attrs = []  # strip attributes of all table cells 

    return paragraphs, table_cells

def html2text_springer(html):
    """

    Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <p> and <td> tags are preserved

    """

    paragraphs = []

    soup = bs4.BeautifulSoup(html, 'html.parser')

    main = soup.find("main")
    article = main.find("article")

    # 1. Abstract 
    Abs_section = article.find("section", {"class":"Abstract"})
    paragraphs += taglist2stringlist(Abs_section.find_all("p"))  # A list of strings

    # 2. Regular text paragraphs, except those right before figures/tables
    body = article.find("div", {"id":"body"})  # only regular sections
    p_para = body.find_all("p", {"class":"Para"})
    paragraphs += taglist2stringlist(p_para)

    # 3. Get Table captions and table footnote
    Captions = body.find_all("div", {"class":"CaptionContent"})
    Footers = body.find_all("div", {"class":"TableFooter"})
    # Get both <span> for table/figure number, and the caption/footnote in <p class="SimplePara"> 

    paragraphs += taglist2stringlist(Captions)
    paragraphs += taglist2stringlist(Footers)

    # Table contents 
    table_tds = taglist2stringlist(body.find_all("td"))

    # 4. Paragraph right before a table/figure, and captions, and footnote 
    # Delete all figure and table nodes since they are extracted in Step 3.
    decompose_list(body.find_all("div",{"class":"Table"}))
    decompose_list(body.find_all("figure"))

    # Then we have only "pure" paragraphs left 
    div_para = body.find_all("div", {"class":"Para"})
    paragraphs += taglist2stringlist(div_para)

    # 5. convert to string from bs4.element
    paragraphs = list(map(str, paragraphs))
    table_tds = list(map(str, table_tds))

    return paragraphs, table_tds

def html2text_bmc():
    pass

def html2text_wiley():
    pass

def html2text_embo():
    pass


def html2text_elsevier(html):
    """Extract text from an Elsevier HTML page 

    Args:
        html (str): a string in HTML format

    Returns:
        (list of bs4.element, list of bs4.element): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <p> and <td> tags are preserved 
    """

    def remove_unwanted(text):
        """remove text that can be noise to our NLP downstream task 
        Args:
            text (str): a string, likely a node on HTML parsing tree 
                        and its child(ren)

        Notes:
            We cannot remove them at this stage. Otherwise, alignment to 
            highlighted text from PDF may be problematic. Remove in 
            training preprocessing
        """
        cross_refs = text.find_all("a", {"class":"workspace-trigger"})
        table_figure_numbers = text.find_all("span", {"class":"label"})
        

    soup = bs4.BeautifulSoup(html, 'html.parser')
    body = soup.find('div', {'class':'Body'}) # the part without title, abstract, 
    true_body = body.find('div')
    
    paragraphs = true_body.find_all('p')
    table_cells = true_body.find_all('td')

    for cell in table_cells:
        cell.attrs = []  # strip attributes of all table cells 


    return paragraphs, table_cells

if __name__ == "__main__" :
    import sys

    text = file2text(sys.argv[1])
