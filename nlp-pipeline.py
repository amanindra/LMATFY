# Task 1 for domain
import nltk
import io
import os
import requests
import json
from pprint import pprint
from nltk.parse import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk.wsd import lesk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import requests
import json
import string

stop_words = stopwords.words('english') + list(string.punctuation)

i = 1
file_loc = 'WikipediaArticles/'
file_names = []

for r, d, f in os.walk(file_loc):
    for file in f:
        if '.txt' in file:
            file_names.append(os.path.join(r, file))

# File read
for file in file_names:
    print(file)
    file_read = open(file, 'r')
    file_text = file_read.read()
    lemmatizer = WordNetLemmatizer()
    porter = PorterStemmer()
    # stanford corenlp is expected to run at localhost:9000
    dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')
    ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
    corpus_dict = {}
    count = 0
    sent_text = nltk.sent_tokenize(file_text)  # Tokenizing text to sentences
    for sentence in sent_text:
        tokenized_text = [i for i in nltk.word_tokenize(
            sentence.lower()) if i not in stop_words]  # Tokenizing sentences into words
        # Lemmatizing the words to extract lemmas as features
        lemma = [lemmatizer.lemmatize(word) for word in tokenized_text]
        stemmed = [porter.stem(word)
                   for word in tokenized_text]  # Stemming the words
        # POS tagging the words to extract POS features
        tagged = nltk.pos_tag(tokenized_text)
        parse, = dep_parser.raw_parse(sentence)
        # Dependency parsing to parse tree based patters as features
        dependency_parse = list(parse.triples())
        # best_sense = [lesk(sentence, word) for word in tokenized_text] #LESK to extract best sense of a word
        tokenized_text_ner = nltk.word_tokenize(
            sentence)  # Tokenizing sentences into words
        try:
            ner_tag = ner_tagger.tag(tokenized_text_ner)
        except:
            ner_tag = ner_tagger.tag(tokenized_text)
        head_list = []
        striped_sentence = sentence.strip(" '\"")
        if striped_sentence != "":
            dependency_parser = dep_parser.raw_parse(striped_sentence)
            parsetree = list(dependency_parser)[0]
            head_word = ""
            head_word = [k["word"]
                         for k in parsetree.nodes.values() if k["head"] == 0][0]
            if head_word != "":
                head_list.append([head_word])
            else:
                for i, pp in enumerate(tagged):
                    if pp.startswith("VB"):
                        head_list.append([tokenized_text[i]])
                        break
                if head_word == "":
                    for i, pp in enumerate(tagged):
                        if pp.startswith("NN"):
                            head_list.append([tokenized_text[i]])
                            break
        else:
            head_list.append([""])
        synonym_list = []
        hypernym_list = []
        hyponym_list = []
        meronym_list = []
        holonym_list = []
        for t in tokenized_text:
            # LESK to extract best sense of a word
            best_sense = lesk(sentence, t)
            if best_sense is not None:
                this_synonym = t
                if best_sense.lemmas()[0].name() != t:
                    this_synonym = best_sense.lemmas()[0].name()
                synonym_list.append(this_synonym)
                if best_sense.hypernyms() != []:
                    hypernym_list.append(best_sense.hypernyms()[
                                         0].lemmas()[0].name())
                if best_sense.hyponyms() != []:
                    hyponym_list.append(best_sense.hyponyms()[
                                        0].lemmas()[0].name())
                if best_sense.part_meronyms() != []:
                    meronym_list.append(best_sense.part_meronyms()[
                                        0].lemmas()[0].name())
                if best_sense.part_holonyms() != []:
                    holonym_list.append(best_sense.part_holonyms()[
                                        0].lemmas()[0].name())
            else:
                synonym_list.append(t)

        count = count + 1
        corpus_dict[count] = {}
        corpus_dict[count]["sentence"] = {}
        corpus_dict[count]["sentence"] = sentence
        corpus_dict[count]["tokenized_text"] = {}
        corpus_dict[count]["tokenized_text"] = tokenized_text
        corpus_dict[count]["lemma"] = {}
        corpus_dict[count]["lemma"] = lemma
        corpus_dict[count]["stemmed"] = {}
        corpus_dict[count]["stemmed"] = stemmed
        corpus_dict[count]["tagged"] = {}
        corpus_dict[count]["tagged"] = tagged
        corpus_dict[count]["dependency_parse"] = {}
        corpus_dict[count]["dependency_parse"] = dependency_parse
        corpus_dict[count]["synonyms"] = {}
        corpus_dict[count]["synonyms"] = synonym_list
        corpus_dict[count]["hypernyms"] = {}
        corpus_dict[count]["hypernyms"] = hypernym_list
        corpus_dict[count]["hyponyms"] = {}
        corpus_dict[count]["hyponyms"] = hyponym_list
        corpus_dict[count]["meronyms"] = {}
        corpus_dict[count]["meronyms"] = meronym_list
        corpus_dict[count]["holonyms"] = {}
        corpus_dict[count]["holonyms"] = holonym_list
        corpus_dict[count]["ner_tag"] = {}
        corpus_dict[count]["ner_tag"] = str(dict(ner_tag))
        corpus_dict[count]["head_word"] = {}
        corpus_dict[count]["head_word"] = head_list[0]
        corpus_dict[count]["file_name"] = {}
        corpus_dict[count]["file_name"] = file[len(file_loc):]

    output_name = 'pipeline/parsed-' + file[len(file_loc):]
    with open(output_name, 'w', encoding='utf8') as output_file:
        
        json.dump(corpus_dict, output_file,  indent=4, sort_keys=True,
                  separators=(',', ': '), ensure_ascii=False)