# Extract text information of a paper from the publisher's website 
# Copyleft 2018 Forrest Sheng Bao, Iowa State University
# AGPL 3.0 
import bs4, re

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
    elif publisher in ["springer"]:
        text = html2text_springer(html)
    elif publisher == "asm":
        text = html2text_asm(html)
    elif publisher == "wiley":
        text = html2text_wiley(html)
    elif publisher == "bmc":
        text = html2text_bmc(html)
    elif publisher == "embo":
        text = html2text_embo(html)
    elif publisher == "pubmed":
        text = html2text_pubmed(html)



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
    if publisher_url_tag:
        citation_pdf_url = publisher_url_tag["content"] 
    else:
        abstract_url_tag = soup.find("meta", {"name":"citation_abstract_html_url"})
        if abstract_url_tag:
            citation_pdf_url = abstract_url_tag["content"]
        else:
            return "WARNING"


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
    elif "wiley.com" in citation_pdf_url:
        return "wiley"
    elif "pmc" in citation_pdf_url:
        return "pubmed"
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

    return (taglist2stringlist(paragraphs),
            taglist2stringlist(table_cells))

def html2text_springer(html):
    """Extract text from a Springer-style HTML page

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

    # 3. Tables 
    Captions = body.find_all("div", {"class":"CaptionContent"})
    Footers = body.find_all("div", {"class":"TableFooter"})
    # Get both <span> for table/figure number, and the caption/footnote in <p class="SimplePara"> 
    paragraphs += taglist2stringlist(Captions)
    paragraphs += taglist2stringlist(Footers)

    # 4. Table contents
    table_tds = taglist2stringlist(body.find_all("td"))

    # 5. Paragraph right before a table/figure, and captions, and footnote 
    # Delete all figure and table nodes since they are extracted in Step 3.
    decompose_list(body.find_all("div",{"class":"Table"}))
    decompose_list(body.find_all("figure"))

    # Then we have only "pure" paragraphs left 
    div_para = body.find_all("div", {"class":"Para"})
    paragraphs += taglist2stringlist(div_para)

    # 6. convert to string from bs4.element
    paragraphs = list(map(str, paragraphs))
    table_tds = list(map(str, table_tds))

    return paragraphs, table_tds

def html2text_asm(html):
    """Extract text from a ASM-style HTML page

     Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        ASM does not keep tables in the same HTML page as the main body. 
        So no <td>  nodes in return. 

        ASM: American Society for Microbiology

    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    body = soup.find("div",{"class":"article"}) # only one of such tag 
    sections = body.findAll("div", {"class":"section"})

    # Find the first appendix-type paragraph's id 
    """
    appendix_paras = []
    for s in sections:
        if "abstract" not in s["class"] and s["class"] != ["section"]:
            appendix_paras += s.findAll("p")
    pids = [p["id"] for p in appendix_paras]
    pids = [int(re.search(r'p-([\d]+)', ID).group(1)) for ID in pids] 
    first_appendix_pid = min(pids)
    """

    # Find all main sections 
    main_sections = [s for s in sections if re.match(r'sec-[\d]+', s["id"])]
    main_paras = [] # include captions for tables and figures 
    for section in main_sections:
        main_paras += section.findAll("p")
    pids = [p["id"] for p in main_paras]
    pids = [int(re.search(r'p-([\d]+)', ID).group(1)) for ID in pids] 
    first_main_pid = min(pids)
    
    # Now append abstract paragraphs
    paras = main_paras
    for ID in range(1, first_main_pid):
        paras.append(body.find("p", {"id":"p-"+str(ID)}))

    # Captions = body.find_all("div", {"class": "fig-caption"})
    # paras += Captions
    paras  = taglist2stringlist(paras)

    return paras, ['']

def html2text_bmc(html):
    """Extract text from a Springer-style HTML page

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

    # 1. Paragraphs not right bbefore figures/tables 
    AllParas = main.findAll("p", {"class":"Para"})   # All paragraphs not before figures/tables 
    GoodParaID= r'(Sec|ASec)\d+'
    Paras = []  # only those good ones 
    for p in AllParas:
        if p.parent.has_attr("id"):  # for paras under a subsection <section> node
            if re.match(GoodParaID, p.parent["id"]):
                Paras.append(p)
        if p.parent.parent.has_attr("id"): 
            if re.match(GoodParaID, p.parent.parent["id"]):  # for paras under a section <section> node
                Paras.append(p)

    paragraphs += taglist2stringlist(Paras)

    # 2. Captions and footers of figures/tables 
    Captions = main.find_all("div", {"class":"CaptionContent"})
    Footers  = main.find_all("div", {"class":"TableFooter"})

    paragraphs += taglist2stringlist(Captions)
    paragraphs += taglist2stringlist(Footers)

    # 3. Table contents
    table_tds = taglist2stringlist(main.find_all("td"))

    # 4. Paragraph right before a table/figure, and captions, and footnote 
    # Delete all figure and table nodes since they are extracted in Step 2.
    decompose_list(main.find_all("figure"))

    # Then we have only "pure" paragraphs left 
    div_para = main.find_all("div", {"class":"Para"})
    paragraphs += taglist2stringlist(div_para)

    # 6. convert to string from bs4.element
    paragraphs = list(map(str, paragraphs))
    table_tds = list(map(str, table_tds))

    return paragraphs, table_tds

def html2text_wiley(html):
    """Extract text from Wiley format HTML pages 

    Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <p> and <td> tags are preserved


    Notes:
        test on 296.html 
    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    article_body = soup.find("div", {"class":"article__body"})
    article = article_body.find("article")

    # Get abstract 
    abstract_section = article.find("section",{"class":"article-section__abstract"})
    abstract_paras = abstract_section.findAll("p")
    abstract_paras = taglist2stringlist(abstract_paras)
    abstract_paras[-1] = " ".join((abstract_paras[-1]).split("\n")[:-2]).strip()
    # -2 because the copyright info has one empty line. 

    full_section = article.find("section", {"class":"article-section__full"})

    # Get table captions
    table_captions = full_section.findAll("header", {"class":"article-table-caption"})
    table_footnotes = full_section.findAll("div", {"class":"article-section__table-footnotes"})

    # Get figure captions 
    figure_captions = full_section.findAll("figcaption")
    fig_cap_text = []
    for fig_cap in figure_captions:
        fig_cap_text += fig_cap.findAll("div", {"class":"accordion__content"})
    fig_cap_str_list = taglist2stringlist(fig_cap_text)
    # remove fig cap because so that normal paragraph will not get <p>
    # inside it
    decompose_list(figure_captions)

    # Get <td> s
    table_tds = full_section.findAll("td")

    # Get normal paragrahs 
    normal_divs = full_section.findAll("div", {"class":"article-section__content"})
    normal_paras = []
    for div in normal_divs:
        normal_paras += div.findAll("p")
        
    # Final output 
    all_paras = normal_paras + table_captions + table_footnotes
    all_paras = taglist2stringlist(all_paras)
    all_paras = abstract_paras + all_paras + fig_cap_str_list

    table_tds = taglist2stringlist(table_tds)

    return all_paras, table_tds

def html2text_embo(html):
    """Extract text from pubmed format HTML pages 

    Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        1. Subscripts, superscripts, and italic tags are preserved 
        2. Unknown how tables are represented because example paper has no tables. 

    """

    soup = bs4.BeautifulSoup(html, 'html.parser')
    article = soup.find('div', {"class":"article"})

    paras = article.findAll("p")
    main_paras = [p for p in paras if re.match(r'sec-\d+', p.parent.get("id", ""))]
    # only main paragraphs have parent <div> of id in the form of sec-\d+

    abs_paras = [p for p in paras if "abstract" in p.parent.get("class", "")]

    fig_captions = [p for p in paras if "fig-caption" in p.parent.get("class", "") ]

    all_useable_paras = abs_paras + main_paras + fig_captions 
    all_useable_paras = taglist2stringlist(all_useable_paras)

    return all_useable_paras, []

def html2text_pubmed(html):
    """Extract text from pubmed format HTML pages 

    Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <p> and <td> tags are preserved


    """

    soup = bs4.BeautifulSoup(html, 'html.parser')
    article = soup.find("div", {"class":"article"})

    # 1. get main paraphraphs, including Abstract
    paras = article.findAll("p")
    main_paras = [p for p in paras if (p.parent.name == "div" and re.match(r'__sec\d+', p.parent.get("id", "")) ) ]
    # only main paragraphs have parent <div> of id in the form of __sec-\d+, including paras under a Section 
#    headless_paras = [p for p in paras if (p.parent.name is "div" and "headless" in p.parent.get("class", ""))]
    # some paragraphs are under a <div> node corresponding to a section without head
    pids = [p.get("id", "__p0") for p in main_paras]
    pids = [int(re.search(r'__p([\d]+)', ID).group(1)) for ID in pids] 
    last_main_pid = max(pids)

    main_paras = [p for p in paras if int(re.search(r'__p([\d]+)', p.get("id", "__p10000")).group(1)) <= last_main_pid]

    # 2. Figure and table captions
    caption_divs = article.findAll("div", {"class":"caption"})
    captions = [div.p for div in caption_divs] # only one p node under a caption div

    # 3. Table footnotes
    footnote_divs = article.findAll("div", {"class":"tblwrap-foot"})
    footnotes = [div.div for div in footnote_divs] # always a div node under the <div class="tblwrap-foot"> node 

    # 4. table cells
    table_tds = article.findAll("td")


    # Final output 
    ps = taglist2stringlist(main_paras + captions + footnotes)
    tds = taglist2stringlist(table_tds)

    return ps, tds

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
    # fix <p><p></p></p>
    paragraphs = list(filter(lambda x: x.parent.name != 'p', paragraphs))
    table_cells = true_body.find_all('td')

    abstract = soup.find('div', {'class': 'Abstracts'})
    paragraphs = abstract.find_all('p') + paragraphs
    
    for cell in table_cells:
        cell.attrs = []  # strip attributes of all table cells 


    return (taglist2stringlist(paragraphs),
            taglist2stringlist(table_cells))

if __name__ == "__main__" :
    import sys

    text = file2text(sys.argv[1])
