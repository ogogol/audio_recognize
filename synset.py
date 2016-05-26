import nltk
from nltk.corpus import wordnet as wn
import sys
#print all the synset element of an element
def lemmalist(str):
    syn_set = []
    for synset in wn.synsets(str):
        for item in synset.lemma_names:
            syn_set.append(item)
    return syn_set
	
#from lemma import lemmalist
print lemmalist('tree')	