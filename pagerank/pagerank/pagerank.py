import os
import random
import re
import sys
import copy
import numpy as np

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    holder = {}
    total_count = 0
    
    #duplicate links on the same page are treated as a single link,
    # and links from a page to itself are ignored as well)

    # find page in corpus
    for each_link in corpus[page]:
        if each_link not in holder and each_link is not page:
            holder[each_link] = 1 #duplicate links on the same page are treated as a single link,
            total_count+=1

    answer = {}
    if total_count == 0:
        damping_factor = 0
    else:
        page_prob = (damping_factor)/total_count
        
    for each_page in corpus:
        if each_page in holder:
            answer[each_page] = page_prob*holder[each_page] + (1-damping_factor)/len(corpus.keys())
        else:
            answer[each_page] = (1-damping_factor)/len(corpus.keys())
    return answer


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #initialise tracking dict
    holder = {}
    for each_page in corpus:
        holder[each_page] = 0
        
    #  for first iteration
    init_page = random.choice(list(corpus.keys())) 
    
    for i in range(n):
        probabilities = transition_model(corpus,init_page,damping_factor)
        next_page = calculate_page(probabilities)

        holder[next_page] +=1/n

        init_page = next_page
    return holder
        
def calculate_page(trans_prob):
    
    random_prob = random.uniform(0,1)
    lower_limit = 0
    upper_limit = 0
    for link,prob in trans_prob.items():
        upper_limit += prob
        if random_prob >= lower_limit and random_prob < upper_limit:
            return link
        else:
            lower_limit += prob



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    tolerance = 0.001
    answer = {}
    
    N = len(corpus.keys())
    # get initial PR values

        
    incoming_corpus = {}
        
    # get incoming corpus
    for link, link_to_others in corpus.items():
        incoming_corpus[link] = set()
        
    for link, link_to_others in corpus.items():
        for each_link in link_to_others:
            if each_link not in incoming_corpus:
                incoming_corpus[each_link] = {link}
            else:
                incoming_corpus[each_link].add(link)
    
    for link in corpus:
        answer[link] = 1/N
        
        
    numlinks = {}
    # get numlinks, remove duplicates
    for link, link_to_others in corpus.items():
        templist = []
        for i in link_to_others:
            if i in templist:
                continue
            else:
                templist.append(i)
            numlinks[link] = len(templist)    
    # new PR values
    flag = True

    while flag:
        new_answer = {}
        for link, prob in answer.items():
            # get second term 
            second_term = 0
            new_prob = 0
            for link2, prob2 in answer.items(): 
                # iterating through incoming_corpus for link, if iterating (link2 = i) is in incoming_corpus link, sum it
                if link2 in incoming_corpus[link]:
                    second_term += damping_factor * prob2/numlinks[link2]
            new_prob = (1-damping_factor)/N + second_term
            new_answer[link] = new_prob
        new_answer = normalize(new_answer)
        if compare_answers(answer, new_answer, tolerance):
            flag = False
        else:
            flag = True
        answer = copy.copy(new_answer)
    return answer
            
def normalize(answer):
    sum_of_answer_prob = sum(answer.values())
    return {k:(v/sum_of_answer_prob) for (k,v) in answer.items()}

#Returns true when converged
def compare_answers(old, new, tolerance):

    for link in old:
        if abs(old[link] - new[link]) > tolerance:
            return False
            break
    return True



if __name__ == "__main__":
    main()

