import re, collections
import stanfordcorenlp

def build_samples(File):
    """Given a CSV file in our format, convert into two lists, the feature vectors and the labels. 
    """


def feature_per_line(Text):
    """Turn a string/sentence into a feature vector
    """
    
    Plain, tag_features = strip_special(Text)
    Plain = manual_tune(Plain)
    Plain = text_normalize(Plain)
    unigram_counts = collections.Counter(Plain)
    return unigram_counts

def manual_tune(Text):
    """Certain manual adjustment on the text for easier downstream operations
    """
    Text = Text.replace("/", " ")

    return Text

def text_normalize(nlp_handler, Text):
    """Normalize the text, e.g., lemmatization 

    Args:
        nlp_handler: an instance of stanfordcorenlp type 

    Return type:
        tuple of str, each element is a token

    """
    lemmatization_result = nlp_handler.lemma(Text)
    _, lemmatized = zip(*lemmatization_result)

    return lemmatized

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

    first_special = min([min(special_at[special])  for special in special_list ] ) 
    special_counter = {special:len(special_at[special]) for special in special_list}

    return Text[:first_special], special_counter


if __name__ == "__main__":
    stanforecorenlp_jar_location = "/mnt/unsecure/Apps/stanford-corenlp-full-2018-02-27/"
    nlp = stanfordcorenlp.StanfordCoreNLP('stanfordcorenlp_jar_location')


