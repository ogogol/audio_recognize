import re
with open('simple.txt', 'r') as f: 
    words = re.findall(r'\w+', f.read())
    print sorted(list(set([(w, words.count(w)) for w in words])), key=lambda x: x[1])