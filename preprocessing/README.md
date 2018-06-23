# Preprocessing of text data in PDF/HTML

This folder contains several scripts to prepare the data before machine learning stage:
* `full_text_html_extract.py`: Extract full text of a paper from the webpage version of the paper on the publisher's website.  
* `generate_labeled_data.py`: Generate the file for ML. Organize binary (highlighted or not) training samples into CSV format, by taking a full-text HTML file from the publisher ([downloaded via this script](../mendeley/paper_html_download)) and an HTML file containing manually annotated highlights extracted from PDF ([generated via this scrip](../mendeley/highlight_extract)). 

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
## Extract full text of a paper `full_text_html_extract.py`
This script is now provided as a library. Not for end users. 

## Generate the file for ML `generate_labeled_data.py`

Usage:

```shell
python3 generate_labeled_data.py\
    /path/to/publisher.html\
    /path/to/extract.html\
    /path/to/output.csv
```

Arguments: 
- Publisher html: an HTML page downloaded from publisher website by [the paper html download script from us](../mendeley/paper_html_download).
- Extract html: an HTML page generated from the PDF and the mendeley database with `<hl>` tags by [the highlight extraction script from us](../mendeley/highlight_extract)
- Output: a CSV file with two columns: label (0 for highlight and 1
  otherwise) and sentence.


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




