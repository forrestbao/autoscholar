#!/usr/bin/python3


import re, collections, math
import stanfordcorenlp

def build_samples(File, stanfordcorenlp_jar_location="/mnt/unsecure/Apps/stanford-corenlp-full-2018-02-27/", stopword_path="sci_stopwords.txt", unit_file="units.txt"):
    """Given a CSV file in our format, convert into two lists, the feature vectors and the labels. 

    Args:
        nlp: Stanford CoreNLP handler
        File: str, path to a file in our CSV format 

    Return types:
        list of int, labels, 0 or 1
        list of list of floats, each of which is a feature vector 

    """

    nlp = stanfordcorenlp.StanfordCoreNLP(stanfordcorenlp_jar_location)
    stopwords = set(open(stopword_path, 'r').read().split())
    units = open(unit_file, 'r').read().split()

    line_count = 1 

    Labels, Features = [], []
    
    with open(File, 'r') as f: 
        for Line in f:
            if len(Line) > 5: 
                Labels.append(int(Line[0]))
                Features.append(feature_per_line(Line[1:], nlp, stopwords, units)) 
                line_count += 1
                print (line_count)

    nlp.close()

    v, DF = voc_df_from_unigram_counts([Feature[1] for Feature in Features])

    # finalize features using length and total vocablary, e.g., tf-idf
    Features = feature_finalize(Features, v, DF) 

    return Labels, Features

def feature_per_line(Text, nlp_handler, stopwords, units):
    """Turn a string/sentence into a feature vector
    """
    
    Plain, tag_features = strip_special(Text) # <i>, <sup>, <sub> in a line 
    tokens = text_normalize(nlp_handler, Plain)
    tokens = remove_stopwords(tokens, stopwords)

    manual_features, tokens = feature_engineering(tokens, units) # collapse numbers and units 
    line_length = len(tokens)

    unigram_counts = collections.Counter(tokens) # Counter type

    return (tag_features, unigram_counts, line_length, manual_features)

def feature_finalize(Features, v, DF):
    """From raw per line feature to final features

    Args: 
        Features: tuple, return from feature_per_line
                  1st is tag_features converted from <i>, <sub> and <sup>
                  2nd is unigram counts, collections.Couner
                  3rd is length of the text 
                  4th is manual features, dict 

        v: dict, the frequencies of words in the corpus
        DF: dict, the raw DF of all words in the corpus  
    """

    New_features = [] 

    Doc_count = len(Features)
    DF = dict(DF) # from collection.defaultdict to regular dict

    # from direct document number to logarithmic IDF
    IDF = {term:math.log(Doc_count/df) for term, df in DF.items() }
    
    for tag_feature, unigram_counts, length, manual_feature in Features:
        TFIDF = [idf * unigram_counts[term] for term, idf in IDF.items()]
        feature_per_line = TFIDF + \
                           list(manual_feature.values()) + \
                           list(tag_feature.values())

        # normalize feature vector by sentence/doc length
        feature_per_line = [x/length for x in feature_per_line ]

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
    """
    Collapse_dim= {"number":0, "unit":0}
    Remain_tokens=[]
    for t in Tokens:
        if re.match(r'[\d.-]+', t):
            Collapse_dim["number"] += 1
        elif t in Units:
            Collapse_dim["unit"] += 1
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
    lemmatization_result = nlp_handler.lemma(Text) # tokenization and lemmatization 
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
   
    special_list = ["2222", "iiii", "PPPP"]
    special_at = {special:findAll(special, Text) for special in special_list}

    first_special = min([min(special_at[special] + [1000000])  for special in special_list ] ) 
    special_counter = {special:len(special_at[special]) for special in special_list}

    return Text[:first_special], special_counter


if __name__ == "__main__":
    import sys
    stanfordcorenlp_jar_location = "/mnt/unsecure/Apps/stanford-corenlp-full-2018-02-27/"
    stopword_path="sci_stopwords.txt"
    unit_file="units.txt"

    Labels, Features = build_samples(sys.argv[1], stanfordcorenlp_jar_location, stopword_path, unit_file)
    
    import pickle
    pickle.dump( (Labels, Features), open(sys.argv[2], 'wb'))





