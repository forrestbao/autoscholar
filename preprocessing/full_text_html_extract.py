# Extract text information of a paper from the publisher's website 
# Copyleft 2018 Forrest Sheng Bao, Iowa State University
# AGPL 3.0 
import bs4, re, itertools
import os

def html2text(filename):
    """open an HTML file and extract sentences from a paper. 
    """
    with open(filename, 'r') as f:
        html = f.read()

    def exit_cleanup(a_str):
        """Clean up each block of text from the paper
        """
        a_str = re.sub(' +',' ', a_str) # get rid of multiple white spaces
        a_str = re.sub('-+','-', a_str) # get rid of multiple dashes
        a_str = a_str.replace("\n", '') # get rid of line breaks
        return a_str

    publisher = determine_publisher(html)
    print ("This paper is by {}".format(publisher))

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

    text = [list(map(exit_cleanup, t)) for t in text]

    return text

def children2string(BS4Tag):
    """Given a BS4 tag, concatenate all its children into a string 
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

    Returns: (bs4.element.ResultSet, bs4.element.ResultSet): text from
        paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <td> tags are preserved

    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    
    article = soup.find('article')  # get article node
    # the part without title, abstract
    body = article.find('div', {"data-track-component":"article body"})


    # 0. Clean up HTML
    decompose_list(body.findAll(lambda x: x.name == 'sup' and x.a)) # get rid of bibiographical links first 
    decompose_list(body.findAll('a')) # all remaining links, e.g. figures. 

    # Under body, a paper is segmented into <section>s, each of which
    # contain many <p> nodes
    sections = body.find_all("section")
    true_body = [section for section in sections
                 if section["aria-labelledby"]
                 in ["abstract", "main", "results", "discussion", "methods"]]

    paragraphs, captions, table_cells = [], [], []
    # get captions of figures (FIXME no tables found in these papers)
    for section in true_body:
        bs4_list = section.select('figure p')
        captions += taglist2stringlist(bs4_list)
        # remove figure element
        decompose_list(bs4_list)
    # find paragraphs and table cells
    for section in true_body:
        # includes plain paragraphs and detailed captions under figures
        paragraphs += taglist2stringlist(section.find_all('p'))
        cells = section.find_all('td')
        # strip attributes of all table cells 
        for cell in cells:
            cell.attrs = []
        table_cells += taglist2stringlist(cells)

    return (paragraphs, captions, table_cells)

def html2text_springer(html):
    """Extract text from a Springer-style HTML page

    Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <td> tags are preserved

    """

    paragraphs = []
    captions = []

    soup = bs4.BeautifulSoup(html, 'html.parser')

    main = soup.find("main")
    article = main.find("article")
 
    # 0. Clean up the HTML.
    decompose_list(main.find_all("span"))

    for e in main.select("em"):
        e.attrs={}
        e.name= "i" 

    for strong in soup.select('strong'):
#        new_tag=soup.new_tag("b")
#        new_tag.string=strong.string
#        strong.replace_with(new_tag) 
        strong.unwrap()

    # 1. Abstract 
    Abs_section = article.find("section", {"class":"Abstract"})
    # A list of strings
    paragraphs += taglist2stringlist(Abs_section.find_all("p"))

    # 2. Regular text paragraphs, except those right before figures/tables
    body = article.find("div", {"id":"body"})  # only regular sections
    p_para = body.find_all("p", {"class":"Para"})
    paragraphs += taglist2stringlist(p_para)

    # 3. Tables 
    caption_paras = body.find_all("p", {"class":"SimplePara"})
    caption_paras = [p for p in caption_paras if p.parent.name=="div" and "CaptionContent" in p.parent.get("class", [])]
#    caption_elements = body.find_all("div", {"class":"CaptionContent"})
#    caption_paras = [ e.findAll("p", {"class":"SimplePara"}) for e in caption_elements]


    Footers = body.find_all("div", {"class":"TableFooter"})
    # Get both <span> for table/figure number, and the
    # caption/footnote in <p class="SimplePara">
    captions += taglist2stringlist(caption_paras)
    captions += taglist2stringlist(Footers)

    # 4. Table contents
    table_tds = taglist2stringlist(body.find_all("td"))

    # 5. Paragraph right before a table/figure, and captions, and
    # footnote Delete all figure and table nodes since they are
    # extracted in Step 3.
    decompose_list(body.find_all("div",{"class":"Table"}))
    decompose_list(body.find_all("figure"))

    # Then we have only "pure" paragraphs left 
    div_para = body.find_all("div", {"class":"Para"})
    paragraphs += taglist2stringlist(div_para)

    return paragraphs, captions, table_tds

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

    # 0. Clean up HTML
    decompose_list(body.select('a[class="xref-bibr"]'))
    decompose_list(body.select('a[class="xref-fig"]'))
    decompose_list(body.select('a[class="xref-table"]'))
    decompose_list(body.select('a[class="rev-xref"]'))

    for i in body.select('span[class="inine-l2-header"]'):
        i.unwrap()
    for i in body.select('span[class="fn-label"]'):
        i.unwrap()

    sections = body.findAll("div", {"class":"section"})

    # Find all main sections 
    main_sections = [s for s in sections
                     if re.match(r'sec-[\d]+', s["id"])]

    # find all .fig elemnets, extract paragraphs, and remove
    caption_elements = []
    captions = []
    for section in main_sections:
        caption_elements += section.select(".fig p")
        caption_elements += section.select('.table p')
    captions = taglist2stringlist(caption_elements)
    decompose_list(caption_elements)

    # Find the maximum ID of regular paragraphs 
    main_paras = []
    for section in main_sections:
         main_paras += section.findAll("p")
    pids = [p["id"] for p in main_paras]
    pids = [int(re.search(r'p-([\d]+)', ID).group(1)) for ID in pids] 
    max_pid = max(pids)
    
    # Extract all regular paragraphs, including abstract 
    paragraphs = [] 
    for ID in range(1, max_pid+1):
         the_p = body.find("p", {"id":"p-"+str(ID)})
         if the_p: # if it's non-empty
             paragraphs.append(the_p)
    paragraphs = taglist2stringlist(paragraphs)

    return paragraphs, captions, ['']

def html2text_bmc(html):
    """Extract text from a Springer-style HTML page

    Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <td> tags are preserved

    """

    paragraphs = []
    captions = []

    soup = bs4.BeautifulSoup(html, 'html.parser')

    main = soup.find("main")

    # 0. Clean up the HTML.
    decompose_list(main.find_all("span"))

    for e in main.select("em"):
        e.attrs={}
        e.name="i"

    for e in main.select("sub"):
        e.attrs={}

    for strong in soup.select('strong'):
#        new_tag=soup.new_tag("b")
#        new_tag.string=strong.string
#        strong.replace_with(new_tag) 
        strong.unwrap()

    # 1. Paragraphs not right bbefore figures/tables
    # All paragraphs not before figures/tables 
    AllParas = main.findAll("p", {"class":"Para"})
    GoodParaID= r'(Sec|ASec)\d+'
    Paras = []  # only those good ones 
    for p in AllParas:
        # for paras under a subsection <section> node
        if p.parent.has_attr("id"):
            if re.match(GoodParaID, p.parent["id"]):
                Paras.append(p)
        if p.parent.parent.has_attr("id"):
            # for paras under a section <section> node
            if re.match(GoodParaID, p.parent.parent["id"]):
                Paras.append(p)

    paragraphs += taglist2stringlist(Paras)

    # 2. Captions and footers of figures/tables 
    captions_elements = main.select('  div[class="CaptionContent"] > p[class="SimplePara"] ')
    footers  = main.find_all("div", {"class":"TableFooter"})

    captions += taglist2stringlist(captions_elements)
    captions += taglist2stringlist(footers)

    # 3. Table contents
    table_tds = taglist2stringlist(main.find_all("td"))

    # 4. Paragraph right before a table/figure, and captions, and footnote 
    # Delete all figure and table nodes since they are extracted in Step 2.
    decompose_list(main.find_all("figure"))

    # Then we have only "pure" paragraphs left 
    div_para = main.find_all("div", {"class":"Para"})
    paragraphs += taglist2stringlist(div_para)

    return paragraphs, captions, table_tds

def html2text_wiley(html):
    """Extract text from Wiley format HTML pages 

    Args:
        html (str): a string in HTML format

    Returns:
        list of lists of str: text from paragraphs, captions, and table cells

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <td> tags are preserved

    """

    def true_fig_cap(tag):
        if tag.name == "div" and tag.get("class", []) == [] and tag.parent.name == "figcaption":
            return True

    soup = bs4.BeautifulSoup(html, 'html.parser')
    article_body = soup.find("div", {"class":"article__body"})
    article = article_body.find("article")

    captions = []
    paragraphs = []
 
    # 0. Clean up the HTML
    decompose_list(article.findAll('span', {})) # Safe to do so for span with no attributes 
    decompose_list(article.findAll('a')) # Safe to do so for all a's 

#    decompose_list(article.findAll(lambda x: "bibLink" in x.get("class", [])))
#    decompose_list(article.findAll(lambda x: "tableLink" in x.get("class", [])))
   
    # Get abstract 
    abstract_section = article.find("section",
                                    {"class":"article-section__abstract"})
    abstract_paras = abstract_section.findAll("p")
    abstract_paras = taglist2stringlist(abstract_paras)
    abstract_paras[-1] = " ".join((abstract_paras[-1])
                                  .split("\n")[:-2]).strip()
    # -2 because the copyright info has one empty line.
    paragraphs += abstract_paras

    full_section = article.find("section", {"class":"article-section__full"})

    # Get table captions
    table_captions = full_section.select('header.article-table-caption')
#    for c in table_captions:
#        c.span.decompose() # drop the part: <span>Table I</span>

    table_footnotes = full_section.select("div.article-section__table-footnotes > ul > li")
#    for f in table_footnotes:
#        if f.span: 
#            f.span.decompose() # drop the <span> that is for footnote numbering 

    captions += taglist2stringlist(table_captions)
    captions += taglist2stringlist(table_footnotes)

    # Get figure captions 
#    fig_cap_text = full_section.select("figcaption.figure__caption div")
    fig_cap_text = full_section.findAll(true_fig_cap)
    fig_cap_text = [div.p if div.p else div for div in fig_cap_text]
    captions += taglist2stringlist(fig_cap_text)

    # remove fig cap because so that normal paragraph will not get <p>
    # inside it
    figure_captions = full_section.findAll("figcaption")
    decompose_list(figure_captions)

    # Get <td> s
    table_tds = taglist2stringlist(full_section.findAll("td"))

    # Get normal paragrahs 
    normal_divs = full_section.findAll("div", {"class":"article-section__content"})
    normal_paras = []
    for div in normal_divs:
        normal_paras += div.findAll("p")
        
    paragraphs += taglist2stringlist(normal_paras)

    return paragraphs, captions, table_tds

def html2text_embo(html):
    """Extract text from pubmed format HTML pages 

    Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        1. Subscripts, superscripts, and italic tags are preserved 
        2. Unknown how tables are represented because example paper has no tables. 

        Example paper: http://msb.embopress.org/content/3/1/149

    """

    soup = bs4.BeautifulSoup(html, 'html.parser')
    article = soup.find('div', {"class":"article"})

    # 0. Clean up HTML
    decompose_list(article.findAll("a"))
    for i in article.select('span[class="sc"]'):
        i.unwrap()


    paras = article.findAll("p")
    main_paras = [p for p in paras
                  if re.match(r'sec-\d+', p.parent.get("id", ""))]
    # only main paragraphs have parent <div> of id in the form of sec-\d+

    abs_paras = [p for p in paras
                 if "abstract" in p.parent.get("class", "")]

    fig_captions = [p for p in paras
                    if "fig-caption" in p.parent.get("class", "")]

    paragraphs = taglist2stringlist(abs_paras + main_paras)
    captions = taglist2stringlist(fig_captions)

    return paragraphs, captions, []

def html2text_pubmed(html):
    """Extract text from pubmed format HTML pages 

    Args:
        html (str): a string in HTML format

    Returns:
        (list of str, list of str): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <p> and <td> tags are preserved

    Example paper: http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=123913&tool=pmcentrez&rendertype=abstract 

    """

    captions = []
    paragraphs = []

    soup = bs4.BeautifulSoup(html, 'html.parser')
    article = soup.find("div", {"class":"article"})

    # 0. Clean up HTML
    decompose_list(article.findAll(lambda x : x.name=='a' and 'bibr' in x.get("class", []))) # get rid of bibliography
    decompose_list(article.findAll(lambda x : x.name=='a' and 'figpopup' in x.get("class", []))) # get rid of fig/table links

    # 1. get main paraphraphs, including Abstract
    paras = article.findAll("p")
    main_paras = [p for p in paras if (p.parent.name == "div" and re.match(r'__sec\d+', p.parent.get("id", "")) ) ]
    # only main paragraphs have parent <div> of id in the form of
    # __sec-\d+, including paras under a Section

    # headless_paras = [p for p in paras if (p.parent.name is "div"
    # and "headless" in p.parent.get("class", ""))]

    # some paragraphs are under a <div> node corresponding to a
    # section without head
    pids = [p.get("id", "__p0") for p in main_paras]
    pids = [int(re.search(r'__p([\d]+)', ID).group(1)) for ID in pids] 
    last_main_pid = max(pids)

    main_paras = [p for p in paras
                  if int(re.search(r'__p([\d]+)', p.get("id", "__p10000")).group(1)) <= last_main_pid]
    paragraphs += taglist2stringlist(main_paras)

    # 2. Figure and table captions
    caption_divs = article.findAll("div", {"class":"caption"})
    # only one p node under a caption div
    captions += taglist2stringlist([div.p for div in caption_divs])

    # 3. Table footnotes
    footnote_divs = article.findAll("div", {"class":"tblwrap-foot"})
    # always a div node under the <div class="tblwrap-foot"> node 
    captions += taglist2stringlist([div.div for div in footnote_divs])

    # 4. table cells
    table_tds = taglist2stringlist(article.findAll("td"))

    return paragraphs, captions, table_tds

def html2text_elsevier(html):
    """Extract text from an Elsevier HTML page 

    Args:
        html (str): a string in HTML format

    Returns:
        (list of bs4.element, list of bs4.element): text from paragraphs/captions, and text from table contents

    Notes:
        Subscripts, superscripts, and italic tags are preserved 
        <p> and <td> tags are preserved

        Example paper: 

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

    paragraphs = []
    captions = []
 
    soup = bs4.BeautifulSoup(html, 'html.parser')

    # 0. Clean up the HTML
    for i in soup.findAll(lambda x: "Learn more about" in x.get('title', ' ') and x.name=='a'):
        i.unwrap()
    decompose_list(soup.select('a.workspace-trigger') ) # all bibliographies
    decompose_list(soup.findAll(lambda x: 'Download' in x.text and x.name=='a')) # e.g., "Downloda fullsize images "
    decompose_list(soup.select('span[class="label"]')) # all figure and table numberings 


    # 1.  Abstract 
    abstract = soup.find('div', {'class': 'Abstracts'})
    paragraphs += taglist2stringlist(abstract.find_all('p'))


    # True/main body, the part without title, abstract
    body = soup.find('div', {'class':'Body'})
    true_body = body.find('div')
   
    # 2. captions
    table_ps = true_body.select('.tables p')
    figure_ps = true_body.select('.figure p')
    captions += taglist2stringlist(table_ps + figure_ps)
    decompose_list(table_ps)
    decompose_list(figure_ps)
    
    # 3. regular paragraphs 
    paragraph_elements = true_body.find_all('p')
    # fix <p><p></p></p>
    paragraph_elements = list(filter(lambda x: x.parent.name != 'p',
                                     paragraph_elements))
    paragraphs += taglist2stringlist(paragraph_elements)

    # 4. tables 
    tds = true_body.find_all('td')
    # strip attributes of all table cells 
    for td in tds:
        td.attrs = []
    table_cells = taglist2stringlist(tds)

    # 5. remove <span> in *string-level*
    paragraphs = remove_span_list(paragraphs)
    captions = remove_span_list(captions)
    table_cells = remove_span_list(table_cells)

    return paragraphs, captions, table_cells


def remove_span(s):
    """Remove <span ...> and </span>
    >>> remove_span('<span class="hello"> world </span>')
    ' world '
    """
    s = re.sub(r'<span[^>]*>', '', s)
    s = re.sub(r'</span>', '', s)
    return s

def remove_span_list(lst):
    return list(map(remove_span, lst))


if __name__ == "__main__" :
    import sys

    text = html2text(sys.argv[1])


    
def test_export(dir, ids):
    for i in ids:
        filename = './html_output/' + str(i) + '.html'
        with open(os.path.join(dir, str(i) + '.txt')
                  , 'w') as f:
            l1, l2, l3 = file2text(filename)
            f.write('==============Paragraph('
                    + str(len(l1))
                    + ')================'
                    + '\n\n\n\n\n')
            for s in l1:
                f.write(s)
                f.write('\n\n\n\n')

            f.write('\n\n\n\n\n\n\n'
                    + '==============Captions('
                    + str(len(l2))
                    + ')================'
                    '\n\n\n\n\n\n\n')

            for s in l2:
                f.write(s)
                f.write('\n\n\n\n')

            f.write('\n\n\n\n\n\n\n'
                    + '==============Tables('
                    + str(len(l3))
                    + ')================'
                    '\n\n\n\n\n\n\n')
            for s in l3:
                f.write(s)
                f.write('\n\n\n\n')

                
def rewrite_a(s):
    # markup = '<a href="fdsfds" title="fkd" class="fdsfd">hell<em>world</em></a>'
    # s = bs4.BeautifulSoup(markup, 'html.parser')
    for a in s.find_all('a'):
        a.wrap(s.new_tag('a'))
        a.unwrap()
        
if __name__ == '__test__':
    files = list(map(lambda x: os.path.join('./html_output', x),
                     filter(lambda x: x.endswith('.html'),
                            os.listdir('./html_output/'))))
    for f in files:
        print('------ ' + f)
        l1, l2, l3 = file2text(f)
        print(determine_publisher(open(f).read()))
        print(len(l1))
        print(len(l2))
        print(len(l3))

    file2text('./html_output/50.html')
    determine_publisher(open('./html_output/68.html').read())

    springer_ids = [71, 53, 44, 77, 58]
    elsevier_ids = [66,50,54,68,80,76,45,
                    72,51,69,63,47,60,59,75,48]
    wiley_ids = [55,79,70,61,43,46]
    asm_ids = [57,65,49,64]
    nature_ids = [67,78,73,56,62]
    embo_ids = [89,42]
    bmc_ids = [74]
    pubmed_ids = [52]

    test_export('./test/springer', springer_ids)
    test_export('./test/elsevier', elsevier_ids)
    test_export('./test/wiley', wiley_ids)
    test_export('./test/asm', asm_ids)
    test_export('./test/nature', nature_ids)
    test_export('./test', embo_ids)
    test_export('./test', bmc_ids)
    test_export('./test', pubmed_ids)

