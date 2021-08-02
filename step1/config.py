stanfordcorenlp_jar_location = '/home/gluo/stanford-corenlp-full-2018-02-27/'
stopword_path = 'sci_stopwords.txt'
unit_file = 'units.txt'

annotation_file = "./annot.json"
pdf_download_path = "./pdfs/"
hl_pdf_folder = "./highlighted_pdfs/"
dataset_folder = "./dataset/"
input_folder = pdf_download_path
output_folder = "./output/"

train_tsv_file = 'all.tsv'
preprocessed_file = 'preprocessed.pickle'
model_file = 'model.pickle'

GENERATE_HL_PDF = True     # Generate highlighted pdf files based on mendeley annotation
GENERATE_HL_TSV = True     # Generate highlight dataset from pdfs
NEGATIVE_RATIO = 3         # Nagative Sampling Ratio