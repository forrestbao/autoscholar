# Extract text information of a paper from the publisher's website 
# Copyleft 2018 Forrest Sheng Bao, Iowa State University
# AGPL 3.0 
import bs4

def file2text(filename, publisher="elsevier"):
    """open a file and extract sentences from a paper. 
    """
    with open(filename, 'r') as f:
        html = f.read()

    if publisher == "elsevier":
        text = html2text_elsevier(html)

    return text

def html2text_elsevier(html):
    """Extract text from an Elsevier HTML page 

    Args:
        html (str): a string in HTML format

    Returns:
        (bs4.element.ResultSet, bs4.element.ResultSet): text from paragraphs/captions, and text from table contents

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
            We cannot remove them at this stage. Remove in training preprocessing
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
