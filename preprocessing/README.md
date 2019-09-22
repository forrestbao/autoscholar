# Preprocessing of text data in PDF/HTML

This folder contains several scripts to prepare the data before machine learning stage:
* `hl_fulltext_align.py`: Transfer user highlights to full-text HTML, by taking a full-text HTML file from the publisher ([downloaded via this Racket script](../mendeley/paper_html_download)) and an HTML file containing manually annotated highlights extracted from PDF ([generated via this Python  script](../mendeley/highlight_extract)). 
* `gen_data.py`: Generate the double-column CSV file that contains sentences and their labels for supervised ML. 

The file `full_text_html_extract.py` is only provided as a library, not for end users to run. 


## Dependencies
* Python 3
* BeautifulSoup4
* The parser lxml
* `agrep` command line utility
* `nltk` and `punkt`

To install, run the following commands in shell:

```shell
sudo apt install agrep
pip3 install lxml BeautifulSoup4 nltk  
python3 -c "import nltk; nltk.download('punkt')"
```

## Usage 

**First:**

```shell
python3 hl_fulltext_align.py\
    /path/to/publisher.html\
    /path/to/highlights.html\
    /path/to/aligned.html
```

Arguments: 
- Publisher HTML (input): an HTML page downloaded from publisher website by [this Racket script](../mendeley/paper_html_download).
- Highlights HTML (output): an HTML page generated from the PDF and the mendeley database with `<hl>` tags by [this Python script](../mendeley/highlight_extract)
- Aligned HTML (output): an HTML file with the two inputs aligned

Example contents: 
* publisher HTML: `<html>This is a happy day </html>`
* highlights HTML: `<html><hl> happy </hl> </html>`
* aligned HTML:  `<html>This is a  <hl> happy </hl> day </html>`

**Then:**

```shell
python3 gen_data.py\
    /path/to/aligned.html
    /path/to/label.csv
```

Arguments: 
* Aligned HTML (input): an HTML file with the two inputs aligned
* label CSV (output): a CSV file for supervised ML 


## Note: publisher determination
Because different publishers have different HTML structures for papers, the publisher information is important for the correct extraction of text. 

For the following publishers, we can use domain name in the value of the `content` attribute in the only `<meta name="citation_pdf_url">` tag. 
* Elsevier: ScienceDirect.com, e.g., `<meta content="https://www.sciencedirect.com/...-main.pdf" name="citation_pdf_url"/>`
* American Society for Microbiology:  ASM.org, e.g., `<meta content="http://aem.asm.org/content/73/24/7814.full.pdf"  name="citation_pdf_url" />`
* Wiley/Blackwell: wiley.com, e.g., `<meta name="citation_pdf_url" content="https://onlinelibrary.wiley.com/doi/pdf/10.1111/1567-1364.12028">`
* Nature: nature.com, e.g., `<meta name="citation_pdf_url" content="https://www.nature.com/articles/nbt.2149.pdf"/>`
* BioMedCentral (BMC): biomedcentral.com, e.g., `<meta name="citation_pdf_url" content="https://microbialcellfactories.biomedcentral.com/track/pdf/10.1186/s12934-015-0240-6"/>`
* Springer, springer.com, e.g., `<meta name="citation_pdf_url" content="https://link.springer.com/content/pdf/10.1007%2Fs00253-007-1246-8.pdf"/>`
* EMBOPress, embopress.org, e.g., `<meta name="citation_pdf_url" content="http://msb.embopress.org/content/3/1/149.full.pdf" />`




