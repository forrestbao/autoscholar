# autoscholar
A computer program that automatically ''reads'' scientific papers for you. By ''reading,'' we mean two tasks: 
1. Detect sentences of a reader's interest -- based on sentences previously highlighted by the reader. 
2. Extract facts (such as a numerical ouput of a system under a set of numerical inputs) from such sentences.

We pick one scientific domain to start: microbial cell factory (e.g., fermenation of starch into ethanol using yeast) in the area of synthetic biology. We hope to automatically identify sentences about experimental conditions (inputs) and yields (outputs), then extract the numerical facts from them, and finally build a simulator that can predict the cell behavior. 

Step 1 is modeled as a binary classification problem in machine learning. First, a human reader highlights sentences in the PDF files of many papers (known as corpora in NLP) via the Mendeley client. Then such highlights are extracted (from PDF files and Mendeley database using [our script](mendeley/highlight_extract)), and aligned against the full text of the papers (crawled from publishers' websites using [our script](mendeley/paper_html_download)) to form the training set. Finally, we use typical NLP and ML approaches to train a model that can identify such sentences as if a human reader is highlighting. 

The folders are organized as follows: 
* [mendeley](mendeley): All scripts that involve the interaction with the Mendeley database. 
* [preprocessing](preprocessing): Preprocessing data before ML. 
* [ML](https://github.com/forrestbao/autoscholar/tree/html_extract) (under heavy development, not merged into master yet): Feature extraction and training of ML models. 

## Requirements
* Python 3 (no Python 2)
* Ubuntu Linux 18.04
* NLTK and [our fork](https://github.com/forrestbao/stanford-corenlp) of Stanford CoreNLP Python wrapper. 
* scikit-learn
* Mendeley version 1.18 or earlier. 

## Known issues
* The SQLite3 database file that holds highlights and full-text URLs has been encrypted since Mendeley v. 1.19 (circa. June 2018). We will soon drop the dependency on Mendeley by directly extracting highlights from PDF. 

## Documentation
Please refer to the README file in each folder, as well as the Wiki. 

## Acknowledgment 

![NSF logo](https://www.nsf.gov/images/logos/nsf1.jpg "NSF logo")

This project is partially supported by NSF through grant [1616216](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1616216 "NSF award page of the grant"). Technical questions shall be redirected to Dr. Forrest Sheng Bao (find my email from my Github profile) of Iowa State University. Opinions expressed in this repository do not reflect those of National Science Foundation nor Iowa State University. 
