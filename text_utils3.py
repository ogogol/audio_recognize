# -*- coding: utf-8 -*-

# text_utils.py
# - User: rnd_d - st00nsa@gmail.com
# - Date: 07.12.11
# - Time: 21:51
# - Description:
import re
import time
from diff_match_patch import diff_match_patch
import nltk

def percent_diff(text1, text2):
    """
    Подсчитывает процентную разность текста1 и текста2
    """
    diff = diff_match_patch()
    diffs = diff.diff_main(text1, text2)

    diff.diff_cleanupEfficiency(diffs)
    diffs_lev = diff.diff_levenshtein(diffs)

    #if len(text1) >= len(text2): text_len = len(text1)
    #else: text_len = len(text2)
    text_len = len(text1)
    if text_len == 0:
        text_len = 1
    
    return int( (diffs_lev / float(text_len) ) * 100 )


#regexp for function clean text
re_clean_without_punctuation = re.compile(r"[^\w\d']", re.U)
re_clean_with_punctuation = re.compile(r"[^\w\d'\,\.!\?]", re.U)
def clean_text(text, clean_punctuation = True, clean_numbers = False, clean_skobki = True, lower_case = True, apos = False):
    """
    clean text from non letters, delete "&apos" and more then one space
    return text
    """
    text = re.sub(r"'", u'&apos;', text)
    text = re.sub(r'"', u'&quot;', text)

    if lower_case:
        text = text.lower().strip()
    else:
        text = text.strip()

    if clean_skobki:
        #[^] cut
        text = re.sub("(\[\^.*?\])", u'', text)
    else:
        #заменяем скобки на их содержимое
        in_skobki = re.findall("\[\^(.*?)\]", text, re.DOTALL)
        if in_skobki:
            text = re.sub(r'\[\^(.*?)\]', in_skobki[0], text)

    #apos(') cutter
    if apos:
        space = '\''
    else:
        space = ' '

    symbols = {
        '^&quot;': space, '&quot;$': space, '&quot;\.$': space, ' &quot;': space,
        '&quot; ': space, '^&apos;': space,'&apos;$': space, '&apos;\.$': space,
        ' &apos;': space, '(?<!s)&apos; ': space, '&apos;': '\''
    }
    for symbol, space in symbols.items():
        text = re.sub(symbol, space, text)

    #delet all non letters and not ' and in symbols
    if clean_punctuation:
        text = re_clean_without_punctuation.sub(u" ", text)
    else:
        text = re_clean_with_punctuation.sub(u" ", text)


    if clean_numbers:
        text = re.sub(r"[\d]", u' ', text)

    text = re.sub(r'( +)', u' ', text)
    text = text.strip()
    return text

#a = clean_text('we got the maps')
#b = clean_text('we pulled out the maps')
#print percent_diff(a, b)

#we got the maps
#[80, 'we pulled out']

#we got the maps
#[80, 'we pulled out the']

#we got the maps
#[82, 'we pulled out the maps']

#we got the maps
#[40, 'we pulled out the maps and']

import pickle
now = time.time()
#f = open("tags_punkt.pickle", "r")
#tagger = pickle.loads(f.read())
tagger = nltk.data.load('tokenizers/punkt/english.pickle')
print (time.time()-now)
#f.close()


def coalitions(text):
#    print text
    tokens = test(text)
#    print tokens
    tagged = tagger.tag(tokens)
    characters = []
    for tag in tagged:
        # '-', ';', ',', ':'
        if 'CC' == tag[1] or 'IN' == tag[1] or ',' == tag[1] or ':' == tag[1]:
            characters.append(tag)
    # генерирование регулярного выражения
    if not characters:
        return 0
    rep = ''
    next = False
#    print characters
    for i, char in enumerate(characters):
        # пропускаем символ, потому что он уже дабавлен в регулярное выражение
#        print char
        if next:
            next = False
            continue
        if char[1] == 'CC' or char[1] == 'IN':
            # СОЮЗЫ И ПРЕДЛОГИ
            if not i:
                # при первом союзе, надо выделить слова, которые стоят до него
                # но если он стоит в начале, то не надо
                if not re.match(char[0], text):
                    rep += '(.*)'
            # проверяем на следующий символ, если символ является не знаком препинания, то
            if i+1 != len(characters) and characters[i+1][1] == 'CC' or i+1 != len(characters) and characters[i+1][1] == 'IN':
                # добавляем союз и предлог в регулярное выражение (союз и все после)
                if i+1 == len(characters):
#                    print 'tut 0'
                    rep += '(.* %s .*)'

                    # проверяем, если второй элемент пустой, то не надо добавлять (.*) в начало
                    if not re.search(' *', pat.findall(text)[0][1]):
                        rep += '(.* %s .*)'
                else:
                    if characters[-1][1] == ":" or characters[-1][1] == "," or characters[-1][1] == "-":
#                        print 'tut -3'
                        pass

#                    print 'tut 3'
                    rep += '(.* %s .*)'

            else:
                # получается союз/предлог и знак препинания, что бы разделить нормально
                # делаем .*CC/IN.*ЗнакПрепинания, как бы за 2 действия
#                print 'tut -1'
                # последний элемент, значит добаваляем все после знака препинания
                if i == len(characters)-1:
#                    последний элемент
#                    print 'tut 0'
                    rep += '(.*%s.*)'
                elif i == len(characters)-2:
                    # тут предпоследний
                    # TODO тут всех наказать
#                    print 'предпоследний'
                    # тут если дальше есть символы
                    # если знак препинания, то делаем вместе с CC/IN
                    if characters[i+1][1] == ':' or characters[i+1][1] == ',' or characters[i+1][1] == '-':
                        rep += '(.*%s.*\%s)(.*)'
                    else:
                        # если нет, то значит дальше союз и надо делать раздельно
                        rep += '(.*%s.*)(.*\%s)'
                    # этот выберим, если последний элеменит предложения
#                    rep += '(%s.*\%s)'
                else:
                    # тут все до предпоследнего
#                    if i+2 > len(characters):
#                        print 'ERROR'

                    # если 2 следующих знака препинания, то делаем делаем регулярку без (.*)
                    if characters[i+1][1] == ',' and characters[i+2][1] == ',' or characters[i+1][1] == ':' and characters[i+2][1] == ':':
                        # сюда попадаем, если после предлога или союза идут 2 знака препинания
                        # и делаем такой вид
                        rep += '(.*%s.*%s)'
                    else:
                        # а тут все остальные случаи
#                        print 'other '
                        rep += '(.*%s.*%s)'
                # говорим пропустить следующий символ, потому что он уже добавлен в регулярное выражение
                next = True
        # ЗНАКИ ПРЕПИНАНИЯ
        else:
            # добавляем знак препинания в регулярное выражение (все до знака препинания)
            rep += '(.*\%s)'
            # проверка на последний символ
#            print i, len(characters)-1
            if i == len(characters)-1 and i >= 1:
                # +
#                print 'tut 1'
                rep += '(.*)'
            # проверка на первый символ и он один
            if i == len(characters)-1 and not i:
                # если одна запятая
                # +
#                print 'tut 2'
                rep += '(.*)'
    # приминяем наши 'разделители' к собранному регулярному выражению
    print (text)
#    print characters
#    print rep
    cor = ()
    for char in characters:
        if not re.search('[()]', char[0]):
            cor += (char[0], )
        else:
            cor += ('\\'.join(char[0]), )
#    print '-----'
#    print cor
#    print rep
#    print rep % cor

    pattern = re.compile(rep % cor)
    words = pattern.findall(text)
    if len(words) == 1:
        words = words[0]
#        print words
    elif len(words) > 1:
#        print words
        words = list(words[0])
    return words


def test(text):
    from nltk.tokenize import WordPunctTokenizer
    tokenizer = WordPunctTokenizer()
    tokens = tokenizer.tokenize(text)
    return tokens

def clean_collocation(text):
    """
    Убирает символы новой строки и лишние пробелы со словосочетания, которе записывается в aup файл
    """
    new_string = re.compile('\n+')
    other_spaces = re.compile(' +')
    return other_spaces.sub(' ', new_string.sub('', text))

if __name__ == '__main__':
    a = "'How beautiful,' we said, 'in the country, by the river, with the birds, the flowers and the trees all around us!"

    b = 'the byrds lalas'
    c = 'with the birds,  the flowers and the trees all around us!'
    d = 'with the birds,'
#    print percent_diff(b, c)
    coalitions(a)
#    test(a)


# Sometimes we stop for a moment or two and we listen to the water as it plays gently against the boat.
# You pull your side of the tent hard - and pull out all the ropes on his side.