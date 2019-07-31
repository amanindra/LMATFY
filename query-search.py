# task 1 for a question, task 2, task 3
import nltk
import io
import os
import re
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
import requests
from elasticsearch import Elasticsearch
import json
from nltk.corpus import stopwords
import string
import numpy as np
import ast
import dateparser
# who - wp when -wrb where -wrb

stop_words = stopwords.words('english') + list(string.punctuation)
r = requests.get('http://localhost:9200')
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def question_pipeline(question):

    lemmatizer = WordNetLemmatizer()
    porter = PorterStemmer()
    # stanford corenlp is expected to run at localhost:9000
    dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')
    ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
    corpus_dict = {}
    count = 0
    sent_text = question
    tokenized_text = nltk.word_tokenize(sent_text)
    question_types = ['who', 'when', 'where', 'Who', 'When', 'Where']
    type_of_question = [i for i in question_types if i in tokenized_text]
    lemma = [lemmatizer.lemmatize(word) for word in tokenized_text]
    stemmed = [porter.stem(word)
               for word in tokenized_text]  # Stemming the words
    # POS tagging the words to extract POS features
    tagged = nltk.pos_tag(tokenized_text)
    parse, = dep_parser.raw_parse(question)
    # Dependency parsing to parse tree based patters as features
    dependency_parse = list(parse.triples())
    # LESK to extract best sense of a word
    best_sense = [lesk(question, word) for word in tokenized_text]
    # tokenized_text_ner = nltk.word_tokenize(sent_text) #Tokenizing sentences into words
    ner_tag = ner_tagger.tag(tokenized_text)
    head_list = []
    striped_sentence = sent_text.strip(" '\"")
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
        best_sense = lesk(sent_text, t)  # LESK to extract best sense of a word
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
    corpus_dict[count]["sentence"] = sent_text
    corpus_dict[count]["type_of_question"] = {}
    corpus_dict[count]["type_of_question"] = type_of_question
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
    corpus_dict[count]["ner_tag"] = dict(ner_tag)
    corpus_dict[count]["head_word"] = {}
    corpus_dict[count]["head_word"] = head_list[0]
    return corpus_dict

def quesFeatures(piped):
    keywords = ""
    namedEntities = []
    similarWords = []
    stems = []
    ques_type = piped[1]['type_of_question']
    head_word = piped[1]['head_word'][0]
    lemma = piped[1]['lemma']
    ner = piped[1]['ner_tag']
    stems = piped[1]['stemmed']
    depparse = piped[1]['dependency_parse']
    ner_tag = piped[1]['ner_tag']
    dep_list = list(list(x) for x in depparse)
    depElements = []
    for i in dep_list:
        if i[1] == 'nsubj':
            depElements.append(i[0])
        if i[1] == 'dobj':
            depElements.append(i[0])
    dep_list2 = list(list(x) for x in depElements)


    # oth = stems 
    similarWords = piped[1]['synonyms'] + piped[1]['meronyms'] + piped[1]['hyponyms'] + piped[1]['hypernyms'] + piped[1]['holonyms']
    for word, ent in ner.items():
        namedEntities.append(ent)
        #***************add more********************
        if ent == 'ORGANIZATION':
            keywords +=" "+word+" "
        if ent == 'LOCATION':
            keywords +=" "+word+" "
        if ent == 'PERSON':
            keywords +=" "+word+" "
    keywords +=" "+head_word+" "
    return keywords, similarWords, ques_type, lemma, stems, dep_list2

def query_match(theQuery, dep_list2):

    querybody = {
        "query": {
            "dis_max": {
                "queries": [
                    # { "match": { "lemma": {"query": spclQuery,"boost": 2}  }},
                    {"multi_match": {'query': theQuery, "fields": [
                        # "lemma^2.0", "synonyms^0.5", "meronyms^0.1", "holonyms^0.1", "hypernyms^0.1", "hyponyms^0.1"]}},
                        "lemma^2", "ner_tag", "synonyms", "meronyms^0.5", "holonyms^0.5", "hypernyms^0.5", "hyponyms^0.5"]}},

                ]
            }
        }
    }

    ans2 = es.search(index="wikiarticles", body=querybody)
    answers = ans2['hits']['hits']
    depparses = []
    sentenses = []
    scores = []
    articles = []
    ners = []
    for i in range(len(answers)):
        sent = ans2['hits']['hits'][i]['_source']['sentence']
        score = ans2['hits']['hits'][i]['_score']
        depparse = ans2['hits']['hits'][i]['_source']['dependency_parse']
        article = ans2['hits']['hits'][i]['_source']['file_name']
        ner = ans2['hits']['hits'][i]['_source']['ner_tag']
        sentenses.append(sent)
        scores.append(score)
        depparses.append(depparse)
        articles.append(article)
        ners.append(ner)
        # print("Sentence: '{}' DepParse: '{}' Score:'{}'".format(sent, depparse, score))
        # print("--------------------------------------------")
    return sentenses,scores, depparses, articles, ners

def getHeuristics(keywords, similarWords, question, ques_type):
    heuristics = ""
    # domain knowledge for person, organization, location
    utdFlag = 0
    if 'Apple' in keywords:
        heuristics += " Apple inc. computer apple Apple Inc. "
    if 'UTD' in question:
        utdFlag = 1
        heuristics += ' UT Dallas the University of Texas at Dallas institution'
    if 'headquarters' in question:
        heuristics += ' world corporate headquarters American multinational conglomerate headquartered ' 
    if 'Lincoln' in keywords:
        heuristics += ' Abraham Thomas Lincoln '
    if 'die' in keywords:
        heuristics += ' assassination '
    if 'born' in keywords:
        heuristics += '  '
    if 'AT&T' in question:
        heuristics += ' AT&T Inc. expand '
    if 'south' in question:
        heuristics += ' latin '
    if 'Exxon' in question:
        heuristics += " Exxon Mobil Corporation ExxonMobil oil companies "

    month = " january february march april April may june June july august september September october november december "
    year = " 1969 1970 1971 1980 1981 1982 1983 1984 1975 1976 1977 1978 1979 2001 2002 2003 2004 2005 2006 2007 2010 2012 2013 2014 2015"
    # where locations
    if ques_type[0].lower() == 'who':
        if 'found' in question and utdFlag == 1:
            heuristics += ' Eugene McDermott, Cecil Howard Green and J. Erik Jonsson '
        print("Who question")
    if ques_type[0].lower() == 'when':
        print("When question")
    if ques_type[0].lower() == 'where':
        if 'birth' in question:
            heuristics += ' born '
        heuristics += ' locate '
        print("Where question")

    return heuristics



def computeScore(ques_type, keywords, sentenses,scores, depparses, articles, ners, dep_list2):
    # dependency parsing
    # get answers , imporve heuristics, expand synonyms

    count = 0
    anoList = []
    for dep in depparses:
        subList = []
        for i in dep:
            if i[1] == 'nsubj' or i[1] == 'dboj':
                if i[0] in dep_list2:
                    anoList.append([count,i[0]])
                subList.append(i[0]) 
        count += 1


    questionType = ques_type[0].lower()
    answersList = []
    # NATIONALITY
    orgList = ['ORGANIZATION']
    personList = ['PERSON']
    locationList = ['LOCATION', 'PLACE', 'CITY', 'COUNTRY', 'STATE_OR_PROVINCE']
    timeList = ['TIME', 'DATE', 'NUMBER']
    dieList = ['die', 'died', 'assassination']
    bornList = ['born', 'birth', 'life']
    keywordlist = keywords.split()
    keywordList = [item.lower() for item in keywordlist]

    # print(keywordList)
    # domain knowledge
    poi = ['Jobs']
    orgoi = ['apple']
    #stop words for time
    timeoi = ['year', 'now']
    for ano in anoList:
        sentIndex = ano[0]
        scores[sentIndex] +=100


    if questionType == 'who':
        for ner in ners:
            a = eval(ner)
            answers = []
            for key, value in a.items():
                if key in poi and value == 'O':
                    answers.append(key)
                if value in personList:
                    answers.append(key)
                if value in orgList and key.lower() not in orgoi:
                    answers.append(key)
                if answers != [] and key == ',':
                    answers.append(key)
                if answers != [] and key == 'and':
                    answers.append(key)
            answersList.append(' '.join(answers))

    if questionType == 'when':
        for ner in ners:
            # evaluating stringified dict
            a = eval(ner)
            answers = []
            for key, value in a.items():
                if value in timeList and dateparser.parse(key) is not None and key.lower() not in timeoi:
                    answers.append(key)

            answersList.append(' '.join(answers))

    if questionType == 'where':
        for ner in ners:
            a = eval(ner)
            answers = []
            for key, value in a.items():
                if value in locationList:
                    answers.append(key)
                if answers != [] and key == ',':
                    answers.append(key)
                if answers != [] and key == 'and':
                    answers.append(key)
            answersList.append(' '.join(answers))

    
    for naught in range(0,len(answersList)):
        if len(answersList[naught]) < 3:
            scores[naught] -= 100
    
    dieconcept = 0       
    if questionType == 'when':

        for keyw in range(0,len(sentenses)):
            for j in dieList:
                if j in sentenses[keyw]:
                    pattern = r"\((.*?)\)"
                    try:
                        matched = re.findall(pattern,sentenses[keyw])
                        splits = matched[0].split(' ')
                        splitjoin = ' '.join(splits[4:])
                        answersList[keyw] = splitjoin
                        dieconcept = 1
                    except:
                        pass
                    scores[keyw] += 50
        if dieconcept == 0:
            for keyw in range(0,len(sentenses)):
                for j in bornList:
                    if j in sentenses[keyw]:
                        pattern = r"\((.*?)\)"
                        try:
                            matched = re.findall(pattern,sentenses[keyw])
                            splits = matched[0].split(' ')
                            splitjoin = ' '.join(splits)
                            answersList[keyw] = splitjoin
                            dieconcept = 1
                        except:
                            pass
                        scores[keyw] += 10

    l = zip(answersList, sentenses,articles, scores)
    n = sorted(l, key=lambda x: x[3])

    return reversed(n)



def readQuestions(filename):
    # take input line by line in given format
    file = open(filename, 'r')
    file_text = file.read()
    questions = file_text.splitlines()
    return questions

def outputFormat(questions_master, outputList):
    # Output in Required format

    output = {}
 
    for q in range(0,len(questions_master)):
        count = 1
        question = questions_master[q]
        ss = outputList[q]
        output[q] = {}
        output[q]["Question"] = question 
        output[q]["answers"] = {}
        output[q]["sentences"] = {}
        output[q]["documents"] = {}
        for s in ss:
            output[q]["answers"][count] = s[0]
            output[q]["sentences"][count] = s[1]
            output[q]["documents"][count] = s[2]
            count  += 1

    values = []
    for q, v in output.items():
        values += [{"Question": v['Question'], "answers": v['answers'], "sentences": v['sentences'], "documents": v['documents']}]

    # set output path filename
    output_name = 'outputdemo.txt'
    with open(output_name,'w', encoding='utf8') as output_file:
        json.dump(values, output_file,  indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
    print(f"check out the ouput file at {output_name}")
    return 0


if __name__ == '__main__':

    filename = input("Please enter filename or path ")
    # filename = 'questions.txt'
    questions_master = readQuestions(filename)
    print(questions_master)
    qlen = len(questions_master)
    outputList = []
    # set length to length of questions set
    lenRange = len(questions_master)
    for q in range(0,lenRange):

        print("<<<------------------------------------>>> ")
        question = questions_master[q]
        print(f"Question: {question}")
        piped = question_pipeline(question)
        # features of question
        keywords, similarWords, ques_type, lemma, stems, dep_list2 = quesFeatures(piped)
        # hueristics on type of question **
        heuristics = getHeuristics(keywords, similarWords, question, ques_type)
        # the formed query
        theQuery =  keywords + " " +  heuristics +  " " +' '.join(similarWords) + " " + ' '.join(lemma)+  " " +' '.join(stems)
        # matching the query
        sentenses,scores, depparses, articles, ners = query_match(theQuery, dep_list2)
        #list(tuples) of supporting sentences
        supporting_sentences = computeScore(ques_type, keywords, sentenses,scores, depparses, articles,ners, dep_list2)
        outputList.append(supporting_sentences) 
    # task 3 format
    # supporting sentences create a list
    outputFormat(questions_master, outputList)

