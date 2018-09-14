#!/usr/bin/python3

# Script to clean up the text data 
# Copyleft 2018 Forrest Sheng Bao, Iowa State University
# AGPL 3.0 

import bs4
import nltk
import csv
import re

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
    
    sub_string = " ".join([(" "+tag_sub[key]+" ")*times for key, times in tag_counter.items()])

    return str(soup) + " " + sub_string

def remove_html_tags(text):
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

    I'm using regular expression. Removing all <span...> and </span>
    """
    tags = ['a', 'p', 'span', 'dl', 'dt', 'dd', 'img', 'div',
            # not so common
            'g', 'rect', 'use', 'figure', 'li', 'ol',
            'svg', 'math', 'mrow', 'mn', 'msub', 'mi', 'script']
    for tag in tags:
        text = re.sub(r'<' + tag + '>', r'', text)
        text = re.sub(r'<' + tag + r' +[^>]*>', r'', text)
        text = re.sub(r'</' + tag + r'>', r'', text)
    return text

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

def replace_nonascii(text):
    """Replace non-ascii string
    """
    s = r' ‐'
    text = text.replace(r' ', '_')
    text = text.replace(r'‐', '-')
    text = text.replace(r'★', ' ')
    text = text.replace(r'●', ' ')
    text = text.replace(r'○', ' ')
    text = text.replace(r'■', ' ')
    text = text.replace(r'▴', ' ')
    text = text.replace(r'•', ' ')
    text = text.replace(r'▪', ' ')
    text = text.replace(r'□', ' ')
    text = text.replace(r'·', ' ')
    # text = text.replace(r'·', ' ')
    return text

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
    punctuations = ":(),;[]► " #"!#$%&\'()*+,-./:;=?@[\\]^_`{|}~"
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

def hl_label_light(text, last_label):
    """Return the label highlight/1 or not/0, based on whether <hl> or
    </hl> presents.


    - It will not use bs4, cause the sentence may be very short
    - The <h> will not be removed for now, for debugging purpose.
    - FIXME what if <hl>. hello world .</hl>
    - FIXME the sentence tokenization might be poor, due to scientific
      notations and html markups

    """
    if '<hl>' in text or '</hl>' in text:
        return 1
    else:
        return 0

    
def remove_citation(string):
    """Remove citation from string

    >>> remove_citation('In an in vitro study by Joshi et al. (2005), linking a short')
    >>> remove_citation('supplementation (Tehlivets et al., 2007). The FAS2 knockout')
    >>> remove_citation('from E. coli, and a group II PPT, Sfp phosphopantetheinyl transferase from B. subtilis (Mootz et al., 2001; Nakano et al., 1992; White et al., 2005). Previously, rat ACP expressed in')
    >>> remove_citation('closest structurally characterized enzyme to holo-ACP synthase from H. sapiens (Bunkoczi et al., 2007; Kealey et al., 1998; Lee et al., 2009). Both')
    >>> remove_citation('although betaine was helpful (Underwood et al. ).')
    >>> remove_citation('broth (Fig. 6). Minor')
    >>> remove_citation('morphology (Fig. 3B).')
    >>> remove_citation('morphology (Table. 3B).')
    >>> remove_citation('hello (Atsumi et al. ; Curran and Alper ; Keasling ; Schirmer et
al. ) world')
    >>> remove_citation('hello Özcan et al. world')
    """
    # remove_citation('hello (Atsumi et al. ; Curran and Alper ; Keasling ; Schirmer et al. ) world')
    removed = []
    year_reg = r'(?:19\d\d|20[0-1]\d)'
    year_reg_paren = '\(?' + year_reg + '\)?'
    author_reg = '[A-Z][a-z]+'
    # Tehlivets et al., 2007
    reg1 = author_reg + r' et al.,? ' + year_reg_paren
    # Tehlivets and Mootz, 2007
    reg2 = author_reg + r' and ' + author_reg + ',? ' + year_reg_paren
    # Tehlivets (2007)
    reg3 = author_reg + ' ' + year_reg_paren
    # Tehlivets et al.
    reg4 = author_reg + r' et al.'
    # (Okabe et al. ; Tate ; Tsai et al. )
    reg5 = r'\((?:[^)]*;)+[^)]*\)'
    # Özcan et al.
    reg6 = r'\w+ et al.'
    
    removed += re.findall(reg1, string)
    string = re.sub(reg1, '', string)
    removed += re.findall(reg2, string)
    string = re.sub(reg2, '', string)
    removed += re.findall(reg3, string)
    string = re.sub(reg3, '', string)
    removed += re.findall(reg4, string)
    string = re.sub(reg4, '', string)
    removed += re.findall(reg5, string)
    string = re.sub(reg5, '', string)
    removed += re.findall(reg6, string)
    string = re.sub(reg6, '', string)

    fig_reg = r'\([Ff]ig(?:ure)?\.? \w*\)'
    table_reg = r'\([Tt]ab(?:le)?\.? \w*\)'
    removed += re.findall(fig_reg, string)
    string = re.sub(fig_reg, '', string)
    removed += re.findall(table_reg, string)
    string = re.sub(table_reg, '', string)

    # print('-- removed:')
    # if removed:
    #     print(removed)
    return string

def replace_Xdot(text):
    """Replace S. cerevisiae such that there is no dot. Dot is harmful
sentence tokenization

    >>> replace_Xdot('S. cerevisiae')
    AUTOSCHOLAR_XDOT_S cerevisiae
    >>> replace_Xdot('Z. mobilis')
    AUTOSCHOLAR_XDOT_Z mobilis
    >>> replace_Xdot('E. coli')
    AUTOSCHOLAR_XDOT_E coli
    """
    return re.sub(r'\b([A-Z])\.', r'AUTOSCHOLAR_XDOT_\1', text)

def replace_Figdot(text):
    """Replace Fig. Tab.
    """
    text = re.sub(r'Fig\.', r'Figure ', text)
    text = re.sub(r'Tab\.', r'Table ', text)
    return text

def replace_short(text):
    text = text.replace('e.g.', 'for example')
    text = text.replace('i.e.', 'that is')
    text = text.replace('s.d.', 'standard derivation')
    text = text.replace('approx.', 'approximate')
    text = re.sub(r'\bNo.', 'number', text)
    return text


def replace_unitdot(text):
    """Replace dotted units.

    >>> replace_unitdot('2000 r.p.m. is good')
    >>> replace_unitdot('low pH ca. 2.5')
    """
    text = re.sub(r'\br\.p\.m\.', 'AUTOSCHOLAR_UNIT_RPM', text)
    text = re.sub(r'\bca\.', 'AUTOSCHOLAR_UNIT_CA', text)
    return text
    
# def test():
#     hl_html_to_csv('/home/hebi/github/autoscholar/data/align_html/42.html',
#                    '/home/hebi/github/autoscholar/output/test.csv')

def hl_html_to_csv(html_input, csv_output):
    """Turn one hl_html file into csv format of sentences and their labels

    This function is actually doing sentence segmentation and hl-label
    assigning to those sentences. Before doing sentence segmentation,
    we remove those words that have dot in them, because they affect
    segmentation result.

    We also do some preliminary level clean up, including 1) removing
    most html tags 2) remove citations 3) replace non-ascii non-latin
    characters 4) unify html tags for <i><b>

    Args:
        html_input: string
                    filename of an HTML file with our <hl> tags 

        csv_output: string
                    filename to the output

    """
    html = open(html_input, 'r').read()
    csv_rows = []

    # Chen et al. will affect sentence tokenization
    html = remove_citation(html)
    html = replace_nonascii(html)
    html = replace_Xdot(html)
    html = replace_Figdot(html)
    html = replace_unitdot(html)
    html = replace_short(html)
    html = remove_html_tags(html)
    
    html = unify_html_tags(html)
    html = string_replace(html)
    html = unify_html_tags(html)

    soup = bs4.BeautifulSoup(html, 'html.parser')
    body = soup.find('body')

    paras = "".join(map(str, body.children))
    paras = paras.split("<br/><br/>")

    # nltk.sent_tok
    for para in paras:
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        # text = 'Punkt knows that the periods in Mr. Smith and Johann S. Bach.'
        # print('\n-----\n'.join(sent_detector.tokenize(text.strip())))
        # sents = nltk.sent_tokenize(para)

        text = 'Ho and consequently <i>S. cerevisiae</i> has been widely evaluated'
        sent_detector.tokenize(text)
        sents = sent_detector.tokenize(para)
        in_hl = False
        for sent in sents:
            if sent.strip() == '.': continue
            if '<hl>' in sent:
                in_hl = True
            csv_rows.append([1 if in_hl else 0, sent])
            if '</hl>' in sent:
                in_hl = False

    with open(csv_output, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(csv_rows)
        # f.write("\n".join([str(label) + ", " + para for [label, para] in csv]))

    # return csv


def sentence_segmentation():
    """Segment sentences in my way
    """
    pass

def further_transform(in_csv_file, out_csv_file):
    rows = []
    with open(in_csv_file) as f:
        csv_reader = csv.reader(f)
        rows = list(csv_reader)
    result = []
    print('total: ', len(rows))
    ct=0
    for row in rows:
        ct+=1
        if ct==100:
            print('.', end='', flush=True)
            ct=0
        result.append([row[0], pattern_replacement(row[1])])
    with open(out_csv_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(result)


def pattern_replacement(text):
    """Replace patterns

    1. labels <i> <sup> <sub>
    2. CamelCase-Dash/Slash-Number123 patterns
    """
    text = pattern_i(text)
    text = pattern_sup(text)
    text = pattern_sub(text)
    text = pattern_short(text)
    
    text = pattern_place(text)
    text = pattern_units(text)
    
    text = pattern_dash(text)
    text = pattern_underline(text)
    text = pattern_slash(text)
    text = pattern_number(text)
    
    text = pattern_case(text)
    # text = pattern_equation(text)
    return text


def pattern_i(text):
    # print('-- pattern i')
    # - `<i>r</i>`
    # - `<i>α</i>`, `<i>α</i>‐santalene`
    i1 = 0
    # - `∆<i>ade3</i>`
    # - `Δ<em>idh1/2</em>`
    i7 = 0
    # - `<i>Saccharomyces cerevisiae</i>`
    # - `<i>S. cerevisiae</i>`
    # - `<i>Error bars</i>`
    ilong = 0
    for m in re.findall(r'<i>([^<]*)</i>', text):
        if len(m) == 1:
            i1 += 1
        elif len(m) < 7:
            i7 += 1
        else:
            ilong += 1
    # remove <i>
    text = re.sub(r'<i>([^<]*)</i>', r'\1', text)
    return (text + ' '
            + 'AUTOSCHOLAR_i1 ' * i1
            + 'AUTOSCHOLAR_i7 ' * i7
            + 'AUTOSCHOLAR_ilong ' * ilong)


# DEBUG remove this in production
debug_f = open('debug.txt', 'w')

def my_re_sub(pattern, replace, text):
    # print('---')
    # print(pattern)
    # print(pattern.replace('(', '(?:'))
    matches = re.findall(pattern.replace('(', '(?:').replace('?:?', '?'), text)
    for m in matches:
        debug_f.write(str(m) + '\t=>\t' + replace + '\n')
    return re.sub(pattern, replace, text)

def pattern_sup(text):
    # print('-- pattern sup')
    # - `∼10<sup>6</sup>-fold`
    text = my_re_sub(r'\d+<sup>-?\d+</sup>', r'AUTOSCHOLAR_SUP_SCINUM', text)
    # - `NADP<sup>+</sup>‐dependent`
    text = my_re_sub(r'\w+<sup>\+</sup>', r'AUTOSCHOLAR_SUP_CHEMICAL_PLUS', text)
    # units = ['l', 'L', 'mol', 'h', 'in']
    # - `(50 mg l<sup>−1</sup>)`
    text = my_re_sub(r'(\w+)<sup>-1</sup>', r'AUTOSCHOLAR_SUP_UNIT_MINUS_\1', text)
    # - `<i>MATa SUC2 MAL2</i>‐<i>8</i><sup>c</sup>`
    num = len(re.findall(r'<sup>[^<]</sup>', text))
    text = my_re_sub(r'<sup>[^<]</sup>', '', text)
    return (text + ' ' + 'AUTOSCHOLAR_SUP ' * num)
    
def pattern_sub(text):
    # print('-- pattern sub')
    # - `7H<sub>2</sub>O`
    # - `CO<sub>2</sub>`
    text = my_re_sub(r'(\w+<sub>\d+</sub>)+\w*', 'AUTOSCHOLAR_SUB_H2O', text)
    text = my_re_sub(r'\w*<sub>[^<]</sub>', 'AUTOSCHOLAR_SUB', text)
    return text

def pattern_short(text):
    return text
def pattern_case(text):
    """Replace case patterns

    >>> pattern_case('A hello world')
    """
    # print('-- pattern case')
    # - All Upper case: PCR, DNA, MLS, NADPH
    text = my_re_sub(r'\b[A-Z]{2,}\b', 'AUTOSCHOLAR_UPPER', text)
    # - strict CamelCase
    text = my_re_sub(r'\b([A-Z][a-z]+){2,}\b', 'AUTOSCHOLAR_CAMEL_STRICT', text)
    # - generalized Camel case: GeneJET, SynPgPPDS, EtOH
    text = my_re_sub(r'\b[A-Z][a-z]*[A-Z][a-z]*\b', 'AUTOSCHOLAR_CAMEL_CxC', text)
    # - start with lower: gapN
    text = my_re_sub(r'\b[a-z][a-z]*[A-Z][a-z]*\b', 'AUTOSCHOLAR_CAMEL_xCx', text)
    return text

def pattern_dash(text):
    # print('-- pattern dash')
    # - YSC-URA-LEU
    text = my_re_sub(r'\b(?:[A-Z]+-)+[A-Z]+\b', 'AUTOSCHOLAR_DASH_UPPER', text)
    # - CSM-Uracil-Leucine-Histidine
    text = my_re_sub(r'\b(?:[A-Z]\w*-)+(?:[A-Z]\w*)\b', 'AUTOSCHOLAR_DASH_CAMEL', text)
    # - p415-GPD
    # - `3-hydroxy-3-methylglutaryl`
    text = my_re_sub(r'\b(?:\w+-)+\w+\b', 'AUTOSCHOLAR_DASH', text)
    # FIXME over‐expression
    return text
def pattern_underline(text):
    # print('-- pattern underline')
    # protect AUTOSCHOLAR_
    text = re.sub(r'(\bAUTOSCHOLAR_(\w+_)*\w+\b)', r'+\1', text)
    # underline pattern
    text = my_re_sub(r'(?<!\+)\b(?:[A-Za-z]+_)+[A-Za-z]+\b', 'AUTOSCHOLAR_UNDERLINE', text)
    # restore AUTOSCHOLAR_
    text = re.sub(r'\+(AUTOSCHOLAR_(\w+_)*\w+)\b', r'\1', text)
    return text
def pattern_slash(text):
    # print('-- pattern slash')
    text = my_re_sub(r'\b(?:\w+/)+\w+\b', 'AUTOSCHOLAR_SLASH', text)
    return text
def pattern_number(text):
    # print('-- pattern number')
    # mixed alphabet and number
    text = my_re_sub(r'\b(?:[a-zA-Z]+\d+)\w*\b', 'AUTOSCHOLAR_NUMBER_MIX', text)
    # percentage number
    text = my_re_sub(r'\b\d+[ _]*%', 'AUTOSCHOLAR_NUMBER_PERCENT', text)
    text = my_re_sub(r'\b\d+\.\d+[ _]*%', 'AUTOSCHOLAR_NUMBER_PERCENT', text)
    # floating number
    text = my_re_sub(r'\b\d+\.\d+\b', 'AUTOSCHOLAR_NUMBER_FLOAT', text)
    # integers
    text = my_re_sub(r'\b\d+\b', 'AUTOSCHOLAR_NUMBER_INT', text)
    return text
    
def pattern_units(text):
    # print('-- pattern units')
    units = ['g', 'l', 'L', '°C', 'day', 'min', 'mol',
             'gDW', 'h', 'gDCW', 'rpm', 'm', 'M',
             'b', 'v', 'Da', 'liter', 'V', 'w', 'W',
             'in', 's', 'vol', 'wt']
    modifiers = ['m', 'μ', 'n', 'k']
    suffix = ['s']
    divider = ['/', ':']
    # TODO 'pH 9'
    unit_reg = '(?:' + '|'.join(units) + ')'
    modifier_reg = '(?:' + '|'.join(modifiers) + ')'
    suffix_reg = '(?:' + '|'.join(suffix) + ')'
    divider_reg = '(?:' + '|'.join(divider) + ')'
    modified_reg = (r'\b' + modifier_reg + '?' + unit_reg + suffix_reg + '?' + r'\b')
    reg = modified_reg + '(?:' + divider_reg + modified_reg + ')*'
    # retain number right before the unit
    text = my_re_sub(r'(\d+)[ _]*'+reg, r'\1 AUTOSCHOLAR_UNIT', text)
    return text
    
def pattern_place(text):
    """Replace place

    >>> pattern_place('Takara, Dalian, China')
    >>> pattern_place('kit BioRad Richmond CA using')
    >>> pattern_place('Finally isopropanol can be dehydrated to yield propylene which is currently derived from petroleum as a monomer for making polypropylene.')
    """
    # print('-- pattern place')
    US_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE',
                 'FL', 'GA', 'HI', 'ID', 'IL', 'IN',
                 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA',
                 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV',
                 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH',
                 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
                 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
    Countries = ['UK', 'Germany', 'USA', 'Sweden', 'Korea', 'China', 'Singapore']
    Other = ['Corporation', 'BioTek', 'Netherlands']
    all_places = US_states + Countries + Other
    all_places = [r'\b' + s + r'\b' for s in all_places]
    reg = '(' + '|'.join(all_places) + ')'
    text = my_re_sub(reg, 'PLACE_HOLDER', text)
    reg = r'([A-Z]\w*\s+)+PLACE_HOLDER'
    text = my_re_sub(reg, 'AUTOSCHOLAR_PLACE', text)
    # FIXME assert PLACE_HOLDER does not exist
    return text
    
def pattern_equation(text):
    # print('-- pattern equation')
    text = my_re_sub(r'=', ' equals ', text)
    text = my_re_sub(r'±', ' plusminus ', text)
    return text

def count_and_sub(pattern, text):
    # FIXME why I have to import re here?
    ct = len(re.findall(pattern, text))
    text = re.sub(pattern, '', text)
    return (text, ct)

def calculate_special_feature_vector(text):
    """features on AUTOSCHOLAR magic strings

    FIXME post-condition: 'AUTOSCHOLAR' not in text
    """
    vector = []
    magic_strings = [r'AUTOSCHOLAR_XDOT_\w', r'AUTOSCHOLAR_UNIT\w*',
                     r'AUTOSCHOLAR_i1', r'AUTOSCHOLAR_i7', r'AUTOSCHOLAR_ilong',
                     r'AUTOSCHOLAR_SUP_SCINUM', r'AUTOSCHOLAR_SUP_CHEMICAL_PLUS',
                     r'AUTOSCHOLAR_SUP_UNIT_MINUS_\w*', 'AUTOSCHOLAR_SUP',
                     'AUTOSCHOLAR_SUB_H2O', 'AUTOSCHOLAR_SUB', 'AUTOSCHOLAR_UPPER',
                     'AUTOSCHOLAR_CAMEL_STRICT', 'AUTOSCHOLAR_CAMEL_CxC',
                     'AUTOSCHOLAR_CAMEL_xCx', 'AUTOSCHOLAR_DASH_UPPER',
                     'AUTOSCHOLAR_DASH_CAMEL', 'AUTOSCHOLAR_DASH',
                     'AUTOSCHOLAR_UNDERLINE', 'AUTOSCHOLAR_SLASH', 'AUTOSCHOLAR_NUMBER_MIX',
                     'AUTOSCHOLAR_NUMBER_PERCENT', 'AUTOSCHOLAR_NUMBER_FLOAT',
                     'AUTOSCHOLAR_NUMBER_INT', 'AUTOSCHOLAR_UNIT',
                     'AUTOSCHOLAR_PLACE']
    # TODO do we remove them? Leaving them there may be good for
    # n-gram modeling.
    for s in magic_strings:
        text, ct = count_and_sub(s, text)
        vector.append(ct)
    return text, vector
    

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
