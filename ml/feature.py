import re, collections
import stanfordcorenlp

def build_samples(File, stanfordcorenlp_jar_location="/mnt/unsecure/Apps/stanford-corenlp-full-2018-02-27/", stopword_path="sci_stopwords.txt"):
    """Given a CSV file in our format, convert into two lists, the feature vectors and the labels. 

    Args:
        nlp: Stanford CoreNLP handler
        File: str, path to a file in our CSV format 

    Return types:
        list of int, labels, 0 or 1
        list of list of floats, each of which is a feature vector 

    """

    nlp = stanfordcorenlp.StanfordCoreNLP(stanfordcorenlp_jar_location)
    stopwords = load_stopwords(stopword_path)

    line_count = 1 

    Labels, Features = [], []
    
    with open(File, 'r') as f: 
        for Line in f:
            if len(Line) > 5: 
                Labels.append(int(Line[0]))
                Features.append(feature_per_line(Line[1:], nlp, stopwords)) 
                line_count += 1
                print (line_count)

    nlp.close()

    vocabulary = build_vocabulary([unigram_counts for (_, unigram_counts) in Features])

    print (vocabulary)

    return Labels, Features

def feature_per_line(Text, nlp_handler, stopwords):
    """Turn a string/sentence into a feature vector
    """
    
    Plain, tag_features = strip_special(Text) # <i>, <sup>, <sub> in a line 
    tokens = text_normalize(nlp_handler, Plain)
    tokens = remove_stopwords(tokens, stopwords)
#    Plain, manual_features = features_engineering(Plain)
    unigram_counts = collections.Counter(tokens) # Counter type

    return (tag_features, unigram_counts)

def build_vocabulary(Dicts):
    """Build the vocabulary from a list of word freq dict/Counters
    """
    v = set([])

    # 1. Get all words and their freqs. 
    for Dict in Dicts: 
           v.update(set(Dict.keys())) 

    # 2. Drop words of very low freqs 

    return v 

def feature_engineering(Text, collapose_feature=True):
    """Use our own feature engineering to extract features, and replace some substrings 

    Args:
        Text: str
        collapose_feature: Boolean, whether we remove certain substrings that form our features. 

    """
    manual_features = {feature: 0 for feature in ["greek", "unit", "numbers"] } 
    
    

    return Text, manual_features


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
    unit_conversion={"Δ":"DELTA", "δ":"DELTA", "=":"EQUAL", "l":"LITER", "g":"GRAM", "mg":"MILLIGRAM", "μg":"MICROGRAM", "ml":"MILLILITER", "μg":"MICROLITER", "c":"CELSIUS"}
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
    stanforecorenlp_jar_location = "/mnt/unsecure/Apps/stanford-corenlp-full-2018-02-27/"


