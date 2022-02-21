import string

FILE = "english3.txt"

def getIndex(L):
    return ord(L)


f = open(FILE, 'r')

lines = f.readlines()

class Node(object):

    def __init__(self, letter) -> None:
        self.letter = letter 
        self.nextLetters = [None for _ in range(128)]

library = dict()
for L in string.ascii_lowercase:
    library[L] = Node(L)

for line in lines:
    word = line.strip()
    parentNode = library[word[0]]
    currNode = parentNode
    for L in word[1:]:
        nextNode = currNode.nextLetters[getIndex(L)]
        if not nextNode:
            nextNode = Node(L)
            currNode.nextLetters[getIndex(L)] = nextNode
        currNode = nextNode 

def findWord(w):
    currNode = library[w[0]]
    for L in w[1:]:
        if currNode.nextLetters[getIndex(L)]:
            currNode = currNode.nextLetters[getIndex(L)]
        else:
            return False 
    return True

def findClosest(w):
    out = w[0]
    currNode = library[w[0]]
    for L in (w[1:] + " " * 80):
        if currNode.nextLetters[getIndex(L)]:
            currNode = currNode.nextLetters[getIndex(L)]
            out += L 
        else:
            nextNode = None 
            for N in currNode.nextLetters:
                if N:
                    nextNode = N 
                    out += N.letter
                    break
                else:
                    return out
            if not nextNode:
                return out 
            currNode = nextNode
    return out

while True:
    print(">", sep=" ")
    w = input()
    print("Closest word: " + findClosest(w))





    


