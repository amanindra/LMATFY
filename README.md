
## Let Me Answer That For You
*Let Me Answer That For You* is a limited domain question answering system that was developed for CS6320 Natural Language Processing - spring 2019 by Prof. Mithun Balakrishna.  

The problem statement was to implement a Question Answering (QA) system using NLP features and techniques for the following Question Types:

1. WHO questions
  * Who founded Apple Inc.?
  * Who supported Apple in creating a new computing platform?

2. WHEN questions:
 * When was Apple Inc. founded? 
 * When did Apple go public?

3. WHERE questions:
 * Where is Apple’s headquarters?
 * Where did Apple open its first retail store?

The system would need parsed web articles in a text format.

*Expected Input*: Natural language question

*Expected Output*: 

* Exact answer phrase(s)
* Supporting sentence(s) in Wikipedia document
* Supporting Wikipedia document name(s)

More details in the [project-description.pdf](https://github.com/gsk12/LMATFY/blob/master/project-description.pdf) file.

## Contributors:

[<img src="https://avatars0.githubusercontent.com/u/13969654?s=400&v=4" width="100px;" alt="Manindra Anantaneni"/><br /><sub><b>Manindra Anantaneni </b></sub>](https://github.com/amanindra)<br />

## Technologies

* Python 3.7
* [Stanford CoreNLP 3.9.2](https://stanfordnlp.github.io/CoreNLP/)
* [Elastricsearch 6.6.0](https://www.elastic.co/downloads/elasticsearch)
	
## Setup
Stanford Core NLP is expected to run at localhost:9000
Elastricsearch is expected to run at localhost:9020 

``` 
pip install requests nltk CoreNLPParser CoreNLPDependencyParser PorterStemmer Elasticsearch
```

## Usage
1) Run `nlp-pipeline.py` in commandline to parse the files - they are expected to be in the same directory in a folder Wikipedia articles. The parsed files are saved into a pipeline folder.
2) Run `elastic-insert.py` to dump json parses from step 1 and index them to elastic search.
3) Run `query-seach.py` - expects a file name  (questions seperated by lines in a single file) 
Example: questions.txt, ouput is generated in a output.txt file formatted as a json structure.

Sample I/O:


    {
        "Question": "Who founded Apple Inc.?",
        "answers": {
            "1": "Jobs , Wozniak and Ronald Wayne Computer Inc.",
            "2": "NeXT , Jobs Inc.",
 			...
			...
        },
        "documents": {
            "1": "SteveJobs.txt",
            "2": "SteveJobs.txt",
			...
			...
        },
        "sentences": {
            "1": "Jobs, Wozniak, and Ronald Wayne founded Apple Computer (now called Apple Inc.) in the garage of Jobs's Los Altos home on Crist Drive.",
            "2": "1985–1997\nNeXT computer\nFollowing his resignation from Apple in 1985, Jobs founded NeXT Inc. with $7 million.",
			...
			...
        }
    }
