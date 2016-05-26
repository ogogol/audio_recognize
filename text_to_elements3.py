# -*- coding: utf-8 -*-

# text_to_elements
# - User: rnd_d - st00nsa@gmail.com
# - Date: 11.01.12
# - Time: 10:02
# - Description: nltk text cutter, токенезирует английский текст на нужные нам элементы
import codecs

import nltk.data
import logging
import re


def tokenize_text(TXT_FILENAME):
    f = codecs.open(TXT_FILENAME, encoding = 'utf-8', mode = 'r')
    text = f.read()
    text = text.replace('\n', "")
    text = text.split('\r')
    logging.debug("Читаю файл " + TXT_FILENAME + ". Создаю массив с предложениями разбив текст по переносом строк.")
    logging.debug("Получилось предложений: " + str(len(text)))
    f.close()
    return text



"""
def tokenize_text(text = None, filename = None):

    Токенезирует английский текст на нужные нам элементы, обычно на предложения.
    Умеет токенезировать текст как из файла так и просто тот который передает в функцию.

    @type text: string
    @param text: text to tokenize
    @type filename: string
    @param filename: path to file

    @rtype: list
    @return: list of tokenized elements


    if not text:
        f = open(filename or
                 raw_input("Input file text path(or None for default): ") or
                 "text.txt", "r")
        f = open('3men01.txt', 'rb')
        text = f.read()
        f.close()

    elements = nltk.data.load('tokenizers/punkt/english.pickle').tokenize(text)
    pattern_first = re.compile('[!?\']$')
    pattern_last = re.compile('^[\t\']+ *[a-z]+')

    for i, element in enumerate(elements):
        if ';' in element:
            elements[i] = element.split(';')[0]
            elements.insert(i+1, element.split(';')[-1])


    for i in xrange(len(elements)):
        if i+1 >= len(elements):
            break
        value1 = pattern_first.findall(elements[i])
        value2 = pattern_last.findall(elements[i+1])
        if value1 and value2:
            elements[i] += elements[i+1]
            del elements[i+1]

    n = 10
    logging.debug(str(elements))

    f = open("output.txt", "wb")
    f.write(str(elements))
    f.close()



    return elements
"""
if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    elements = tokenize_text()
    print (len(elements))

#spanish
#spanish_tokenizer = nltk.data.load('tokenizers/punkt/spanish.pickle')
#spanish_tokenizer.tokenize('Hola amigo. Estoy bien.')
