import re
with open('simple.txt', 'r') as f: 
    words = re.findall(r'\w+', f.read())
    print len(list(set(words)))