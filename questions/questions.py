import nltk
import sys
import os
import string
import numpy as np

FILE_MATCHES = 1
SENTENCE_MATCHES = 1
STOPWORDS = nltk.corpus.stopwords.words("english")
PUNCTUATION = set(string.punctuation)


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    loaded_files = dict()
    for filename in os.listdir(directory):
        with open(os.path.join(directory,filename), "r", encoding="utf8") as f:
            loaded_files[filename] = f.read()
            f.close()
    return loaded_files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    
    list_of_words = nltk.word_tokenize(document)
    list_of_words_lower = [word.lower() for word in list_of_words if not word in STOPWORDS]
    list_of_words_filtered =  [word for word in list_of_words_lower if word not in PUNCTUATION]
    return list_of_words_filtered

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    word_count = dict()
    for document_name, document_words in documents.items():
        words_added = []
        for word in document_words:
            if word not in word_count and word not in words_added:
                word_count[word] = 1
                words_added.append(word)
            elif word not in words_added:
                word_count[word] += 1
                words_added.append(word)
                
    idf = dict()
    for word, count in word_count.items():
        idf[word] = np.log(len(documents)/count)
    return idf

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidf = dict()
    query_words = [word.lower() for word in query if not word in STOPWORDS if word not in PUNCTUATION]
    for file_name, file_content in files.items():
        for word in query_words:
            if word not in idfs:
                continue
            if file_name not in tfidf:
                tfidf[file_name] = word_frequency(word, file_content) * idfs[word]
            else:
                tfidf[file_name] += word_frequency(word, file_content) * idfs[word]
                
    sorted_tfidf = sorted(tfidf.items(), key=lambda x:x[1], reverse = True)
    sorted_tfidf = [x[0] for x in sorted_tfidf]
    return sorted_tfidf[:(n)]
        

def word_frequency(word, file_content):
    word_count = 0
    for each_word in file_content:
        if word == each_word:
            word_count += 1
    return word_count


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    query_words = [word.lower() for word in query if not word in STOPWORDS if word not in PUNCTUATION]
    sentence_idf = dict()
    for sentence, token_sentence in sentences.items():
        for word in query_words:
            if word in token_sentence:
                if sentence not in sentence_idf.keys():
                    sentence_idf[sentence] = idfs[word]
                else:
                    sentence_idf[sentence] += idfs[word]

    if len(sentence_idf) == 0:
        return []
    else:
        sorted_idf = sorted(sentence_idf.items(), key=lambda x:x[1], reverse = True)
        top_value = sentence_idf[sorted_idf[0][0]]
        top_sentences = [x[0] for x in sorted_idf if x[1] == top_value]
    sentence_density = dict()
    for sentence in top_sentences:
        sentence_density[sentence] = 0
        for word in sentences[sentence]:
            if word in query_words:
                sentence_density[sentence] += 1
        sentence_density[sentence] = sentence_density[sentence]/len(sentence)
    sorted_sentence_density = sorted(sentence_density.items(), key=lambda x:x[1], reverse = True)         
    sorted_sentence_density = [x[0] for x in sorted_sentence_density]
    return sorted_sentence_density[:n]    


if __name__ == "__main__":
    main()
