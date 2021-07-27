#!/usr/bin/python3


import re, collections, math
import stanfordcorenlp
# from preprocessing.gen_data import calculate_special_feature_vector
import csv
import numpy as np
from tqdm import tqdm

def lemma_func(nlp_handler, sentence):
    r_dict = nlp_handler._request('lemma', sentence)
    words = []
    tags = []
    for s in r_dict['sentences']:
        for token in s['tokens']:
            words.append(token['originalText'])
            tags.append(token['lemma'])
    return list(zip(words, tags))

def build_features(texts, nlp, stopwords, units, **kwargs):
    """
    nlp = stanfordcorenlp.StanfordCoreNLP(stanfordcorenlp_jar_location)
    stopwords = set(open(stopword_path, 'r').read().split())
    units = open(unit_file, 'r').read().split()
    """

    Features = []
    
    for i in tqdm(range(len(texts))):
        Features.append(feature_per_line(texts[i], nlp, stopwords, units, **kwargs)) 

    # nlp.close()

    v, DF = voc_df_from_unigram_counts([Feature[1] for Feature in Features])

    # finalize features using length and total vocablary, e.g., tf-idf
    DF = dict(DF) # from collection.defaultdict to regular dict
    Doc_count = len(Features)
    # from direct document number to logarithmic IDF
    IDF = {term:math.log(Doc_count/df) for term, df in DF.items() }
    Features = feature_finalize(Features, IDF) 

    return Features, IDF

def convert_features(texts, nlp, stopwords, units, IDF, **kwargs):
    Features = []
    for text in texts:
        Features.append(feature_per_line(text, nlp, stopwords, units, **kwargs))
    Features = feature_finalize(Features, IDF)
    return Features

def feature_per_line(Text, nlp_handler, stopwords, units, model, tokenizer, **kwargs):
    """Turn a string/sentence into a feature vector
    """
    # Sentence Embedding Feature
    embedding = np.zeros((1, 768), dtype=float)
    try:
        # Can't deal with excetionally long sentences
        inputs = tokenizer(Text, return_tensors="pt")
        outputs = model(**inputs)
        embedding = outputs.pooler_output.detach().numpy()
    except Exception as e:
        print(e)
        
    embedding = embedding.flatten()

    Plain, tag_features = strip_special(Text) # <i>, <sup>, <sub> in a line 
    # print(Plain)
    tokens = text_normalize(nlp_handler, Plain)
    tokens = remove_stopwords(tokens, stopwords)

    manual_features, tokens = feature_engineering(tokens, units) # collapse numbers and units 
    line_length = len(tokens)

    unigram_counts = collections.Counter(tokens) # Counter type

    return (tag_features, unigram_counts, line_length, manual_features, embedding)

def feature_finalize(Features, IDF):
    """From raw per line feature to final features

    Args: 
        Features: tuple, return from feature_per_line
                  1st is tag_features converted from <i>, <sub> and <sup>
                  2nd is unigram counts, collections.Couner
                  3rd is length of the text 
                  4th is manual features, dict 

        IDF: inverse document frequency
    """

    New_features = [] 

    for tag_feature, unigram_counts, length, manual_feature, embedding in Features:
        TFIDF = [idf * unigram_counts[term] for term, idf in IDF.items()]
        feature_per_line = TFIDF + \
                           list(manual_feature.values()) + \
                           list(tag_feature.values())

        # normalize feature vector by sentence/doc length
        if length == 0:
            # FIXME why zero
            length = 1
        length = 1 # Why normalize by length
        feature_per_line = np.array([x/length for x in feature_per_line], dtype=float)
        feature_per_line = np.concatenate([feature_per_line, embedding])
        New_features.append(feature_per_line)
    return New_features
 
def voc_df_from_unigram_counts(Dicts, low_freq_cutoff=5):
    """Get the frequencies of words and raw document frequencies in all documents from a list of word freq dict/Counters

    Args:
        Dicts: list of collections.Counter objects 
               Each element is a unigram dict built of a text, sentence or paragraph
        low_freq_coutoff: int
                          Drop a term if its frequency is below this 

     Returns: 
        v: collections.Counter objects, the frequencies of words in all documents 
        DF: collections.defaultdict, the raw document frequencies of all terms

    Examples:
        >>> voc_df_from_unigram_counts([collections.Counter({"car":2, "mouse":3}), collections.Counter({"mouse":3, "wine":4})], 0)
        (Counter({'car': 2, 'mouse': 6, 'wine': 4}),
         defaultdict(int, {'car': 1, 'mouse': 2, 'wine': 1}))

    """
    v = collections.Counter()
    DF = collections.defaultdict(int)  # the size of set {d\in D : t \in d}

    # 1. Get all words and their freqs. 
    for Dict in Dicts: 
           v += Dict # append and add up the term frequencies
           for t in Dict:
               DF[t] += 1

    # 2. Drop words of very low freqs in all docs 
    for t in list(v):
        if v[t] < low_freq_cutoff: 
            print (t)
            del v[t] 
            del DF[t]

    return v, DF 

def feature_engineering(Tokens, Units):
    """Collapse certain tokens to common dimensions, e.g., numbers and units

    Example:

    >>> feature_engineering(["I", "3.0","-5-5", "mg"], ["mg", "l"])
    ({'number': 2, 'unit': 1}, ['I'])
    >>> feature_engineering(["ab1-cd23-gf76", "ABC123", "CamelCaseWord", "Noncamel"], [])
    ({'number': 0, 'unit': 0, 'A1-A1': 1, 'UPPER': 1, 'CamelCase': 1}, ['Noncamel'])
    >>> feature_engineering(["plasmids", "p416-Cyc-CAD", "and", "p416-Tef-CAD"], [])
    
    """
    Collapse_dim= {"number":0, "unit":0, "A1-A1": 0, "UPPER": 0, "CamelCase": 0}
    Remain_tokens=[]
    # FIXME do we remove all these tokens?
    for t in Tokens:
        if re.match(r'[\d.-]+', t):
            Collapse_dim["number"] += 1
        elif t in Units:
            Collapse_dim["unit"] += 1
        elif re.fullmatch('(\w+-)+(\w+)', t):
            # \w+\d+-\w+\d+-... like A1-A1, or ab1-cd23-gf76
            Collapse_dim["A1-A1"] += 1
        elif re.fullmatch('[A-Z]+\d*', t):
            # frequencies of all upper case words
            Collapse_dim["UPPER"] += 1
        elif re.fullmatch('([A-Z][a-z]+){2,}', t):
            # camel style, like aNb
            Collapse_dim["CamelCase"] += 1
        else:
            Remain_tokens.append(t)

    return Collapse_dim, Remain_tokens

def load_stopwords(Path):
    stopwords = set(open(Path, 'r').read().split())
    return stopwords

def remove_stopwords(tokens, stopwords):
    """Given a list of strings (tokens), remove that are stopwords

    Args:
        tokens: list of str, tokens
        stopwords: list/set of str
    """
    return [token for token in tokens if token not in stopwords]

def manual_tune_pre(Text):
    """Certain manual adjustment on the text for easier downstream operations
    """
    Text = Text.lower() 
#    Text = Text.strip()
    To_be_whitespaced = ["et al.", "/", "et al"]
    for t in To_be_whitespaced:
        Text = Text.replace(t, " ")

    To_separate = ["Δ", "δ"]
    for t in To_separate:
        Text = Text.replace(t, t+" ")

    To_sub = {"°C":"CELSIUS"}
    Text="".join([To_sub.get(t, t) for t in Text])

    # To do: 
    # for an equal sign in form xxx=ddd.dd

    return Text


def manual_tune_post(Tokens):
    """Post-tokenization manual tune 

    Args:
        Tokens: list of str

    """
#    unit_conversion={"Δ":"DELTA", "δ":"DELTA", "=":"EQUAL", "l":"LITER", "g":"GRAM", "mg":"MILLIGRAM", "μg":"MICROGRAM", "ml":"MILLILITER", "μg":"MICROLITER", "c":"CELSIUS"}
    unit_conversion = {}
    return [unit_conversion.get(t, t) for t in Tokens]

def text_normalize(nlp_handler, Text):
    """Normalize the text, e.g., lemmatization 

    Args:
        nlp_handler: an instance of stanfordcorenlp type 

    Return type:
        tuple of str, each element is a token
    """
    punctuations =set("`'?")
    Text = manual_tune_pre(Text)
    # lemmatization_result = nlp_handler.lemma(Text) # tokenization and lemmatization 
    lemmatization_result = lemma_func(nlp_handler, Text)
    # print(lemmatization_result)
    _, Tokens = zip(*lemmatization_result)
    Tokens = manual_tune_post(Tokens)

    Tokens = [x for x in Tokens if x not in punctuations]

    return Tokens

def strip_special(Text):
    """Strip away special annotatiosn at the end of each paragraph
    Returns a normal string and feature values related to those annotations


    Examples:
    >>> strip_special("x y z iiii  iiii 2222  2222  PPPP")
    "x y z", {"iiii":2, "2222":2, "PPPP":1}
    
    """
    def findAll(str1, str2):
        """return all occurences of str1 in str2

        """
        return [m.start() for m in re.finditer(str1, str2)]
   
    special_list = ["iiii", "PPPP"]
    special_at = {special:findAll(special, Text) for special in special_list}

    first_special = min([min(special_at[special] + [1000000])  for special in special_list ] ) 
    special_counter = {special:len(special_at[special]) for special in special_list}

    return Text[:first_special], special_counter
