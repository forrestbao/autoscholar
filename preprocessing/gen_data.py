#!/usr/bin/python3

# Script to clean up the text data 
# Copyleft 2018 Forrest Sheng Bao, Iowa State University
# AGPL 3.0 

import bs4

def unify_html_tags(html):
    """Unify the HTML syntax, e.g. <strong> to <b>, &gt to > 

    Args:
        html: a string
            A piece of HTML code

    Returns:
        a string, in HTML syntax  

    Notes: 
        1. BeautifulSoup automatically adds an end tag if no 
           matching one, e.g., <em>Fig. 1</b> will become <em>Fig. 1</em>.
        2. BeautifulSoup automatically drops unmatched end tags.

    >>> unify_html_tags("<strong>Fig. 1</strong")
    '<b>Fig. 1</b>'
    >>> unify_html_tags("<strong>Fig. 1")
    '<b>Fig. 1</b>'
    >>> unify_html_tags("Fig. 1</strong>")
    'Fig. 1'
    >>> unify_html_tags(" As shown in <strong>Fig. 1</strong>, we can see")
    ' As shown in <b>Fig. 1</b>, we can see'
    >>> unify_html_tags(" As shown in <em>Fig. 1</em>, we can see")
    ' As shown in <i>Fig. 1</i>, we can see'
    >>> unify_html_tags(" As shown in <em>Fig. 1</b>, we can see")
    ' As shown in <i>Fig. 1</i>, we can see'
    >>> unify_html_tags(" As shown in <b>Fig. 1</b>, we can see")
    ' As shown in <b>Fig. 1</b>, we can see'
    """
    
    tag_map = {"strong":"b", "em":"i"}

    soup = bs4.BeautifulSoup(html, 'html.parser')
    
    for key, value in tag_map.items():
        tags_to_be_replaced = soup.findAll(key)
#        EndTags = ["</" + key + ">", "</" + value + ">"] # no attribute is easy
#        Text = Text.replace(CloseTags[0], CloseTags[1])
        for tag in tags_to_be_replaced:
            tag.name = value

    return str(soup)

def tag_subsitute(html, tag_sub={"i":"iiii", "sub":"2222", "sup":"PPPP"}):
    """Substitute certain tags with special characaters for easier n-gram modeling 

    Example:
    >>> gen_data.tag_subsitute("abc<i>def</i>")
    'abc<i> iiii def</i>'


    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    tag_counter  = {x:0 for x in tag_sub.keys()}
    for tag in soup.findAll(tag_sub.keys()):
        tag_counter[tag.name] += 1 
#        if tag.string: 
#            tag.string.insert_before(" " + tag_sub[tag.name] + " ")
        tag.unwrap()
#        else:
#            print (list(tag.children))
    
    sub_string = " ".join([key*times for key, times in tag_counter.items()])

    return str(soup) + " " + sub_string

def remove_html_nodes(Text):
    """Remove certain HTML nodes, e.g., references to bibliography

    The following nodes are cross-refs or citations to be deleted. 
        * Springer: safe to remove all <span>.
                    * Bao et al. <span class="CitationRef"><a ...>2001</a></span>
                    * Fig. <span class="InternalRef"><a ...>10</a></span>
        * Elsevier,  <a class="workspace-trigger">Bao et al. 2001</a> only, for both citation and cross-ref. <a title="Learn more about xxx"> is not.  
        * Wiley, 
                 * Bao et al. <span>2010</span> (no attribute) for citations 
                 * Only two kinds of <a> nodes in <p>, <a class="scrollablelink"> for cross-refs, and <a class="ppt-figure-link"> for links to figures
                 * <span class="smallCaps"> must be kept
        * ASM, safe to remove all <a>.  
        * PubMed, safe to remove all <a>.
        * EMBO, safe to remove all <a>.
        * Nature, safe to remove all <a>.  


    """
    pass

def learn_keywords(html, keyword_tags=["i", "em"]):
    """Learn keywords from HTML text

    Args:
        html: string in HTML syntax 
        keyword_tags: list of str, HTML tags that contain keywords 

    Return type:
        list of str, the keywords 

    1. all strings between <i></i> 
    2. all strings between <a title="Learn more about xxx"></a> in Elsevier format  

    Notes:
        Point 2 is not yet implemented 

    Examples:
    >>>learn_keywords("we are a at <em>New York</em> city")
    ['New York']

    >>>learn_keywords("we are a at <em>New York</i> city")
    ['New York']

    """
    soup = bs4.BeautifulSoup(html, 'html.parser') 
    em_node = soup.findAll(keyword_tags)
    em_text = [x.text for x in em_node]
    return em_text

def string_replace(Text):
    """Replace certain strings 

    1. All strings like \w+ et al\.?,?  -> space 
    2. anything between <i> are keywords  
    3. all unicode whitespace characeters to space 
    4. ►  into space
    5. brackets, paired or not, to spaces
    6. dot that can confuse sentence tokenization, E. coli, 
    7. quotation marks,  ’ to ' 

    Args:
        Text: str 

    Return type:
        str, a string cleaned up
    """
    import re, string

    # Remove punctuations 
    punctuations = ":(),;[]_-► " #"!#$%&\'()*+,-./:;=?@[\\]^_`{|}~"
    punctuation_translator = str.maketrans(punctuations, ' '*len(punctuations))
    Text = Text.translate(punctuation_translator)

    # Reduce all Unicode white spaces 
    Text = re.sub(r'[\s]+', " ", Text)
    return Text  

def hl_label(Text):
    """Return the label (highlighted/1 or not/0) for an HTML-highlighted text and the text with hl tags unwrapped. 

    Examples:
    >>> gen_data.get_label("abc<hl>def</hl>")
    1 abcdef
    >>> gen_data.get_label("abc<hl>def")
    1 abcdef
    >>> gen_data.get_label("abc</hl>def")
    0 abcdef

    """
    soup = bs4.BeautifulSoup(Text, 'html.parser')

    hls = soup.findAll("hl")
#    for hl in hls:
#        hl.unwrap()

    soup = soup.text

    if len(hls)>0 :
        return 1, soup
    else:
        return 0, soup

def hl_html_to_csv(html_input, csv_output):
    """Turn one hl_html file into csv format of sentences and their labels 

    Args:
        html_input: string
                    filename of an HTML file with our <hl> tags 

        csv_output: string
                    filename to the output 

    """
    html = open(html_input, 'r').read()
    csv = [] 

    html = unify_html_tags(html)
    html = string_replace(html)
    html = unify_html_tags(html)

    soup = bs4.BeautifulSoup(html, 'html.parser')
    body = soup.find('body')

    paras = "".join(map(str, body.children))
    paras = paras.split("<br/><br/>")

    for para in paras:
        para = tag_subsitute(para)
        label, para = hl_label(para)
        csv.append([label, para])

    with open(csv_output, 'w') as f:
        f.write("\n".join([str(label) + " " + para for [label, para] in csv]))

    return csv

def get_text_from_tags(Text):
    """Extract the text content from HTML tags 
    """
#    soup = bs4.BeautifulSoup(Text, 'html.parser')
#    Text = soup.text()
    pass

def text_normalization():
    """Lemmatization etc. 
    """
    pass

def sentence_segmentation():
    """Segment sentences in my way
    """
    pass





if __name__ == "__main__":
    import os
    hl_aligned_html_dir, csv_output_dir = "hl_html", "../ml/label_csv"
    keywords =set()
    for i in range(42, 81):
        html_filename = os.path.join(hl_aligned_html_dir, str(i) + ".html")
        csv_filename = os.path.join(csv_output_dir, str(i) + ".csv")
        _ = hl_html_to_csv(html_filename, csv_filename)

#        keywords |= set(learn_keywords(html))
#    print (keywords)
