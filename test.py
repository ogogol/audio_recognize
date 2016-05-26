#-*- coding: utf8 -*-
'''
script Python 2.7 for compiling small audio files of GIU-CD into the whole unit file and writing unit aup file
the prepared data file and mp3 files are wanted
'''
import logging
import subprocess
import threading
import codecs
import re
import time
import re
import subprocess
import threading
import sys
import json
from subprocess import Popen, PIPE

def audioFilesCompilation(unitNumber, unitFilesNames, unitOutFile, pause = 1.500):
    """
    #соединяет файлы
    :param inFile: list из str - имя 1  и 2 входного файла
    :param outFile: str - имя выходного файла
    :param pause: int   время паузы между файлами в миисекундах
    :return: list из int part_start, part_end -  1) начало первого куска и конец его, 2) начало второго и его конец в милисек
    """

    strForSox = 'sox '
    strMerge = ' -p pad 0 %f | sox - ' % pause
    tt1 = []
    t = 0


    for i, file in enumerate(unitFilesNames):
        length, err = Popen('soxi -D "./tmp/%s"' % file, shell=True, stdout=PIPE).communicate()
        if i == 0:
            t += float(length) + pause/2.0
        else:
            t += float(length) + pause
        tt1.append("%.4f" % t)
        if i < len(unitFilesNames)-1:
            strForSox = '%s-v 1.26 "./tmp/%s"%s' % (strForSox, file, strMerge)
        else:
            strForSox = '%s-v 1.26 "./tmp/%s" %s' % (strForSox, file, unitOutFile)

    subprocess.call(strForSox, shell=True)

    return tt1

def writeAupFile(unitNumber, unitTimes, unitPhrases, aupFile):
    """

    :param aupFile:
    :param part_start:
    :param part_end:
    :param frases:
    :return:
    """
    aup_f = open(aupFile, "w")
    aup_f.writelines('<labeltrack name="Дорожка пометок" numlabels="%s" height="73" minimized="0">\n' % len(unitPhrases))

    for i, phrase in enumerate(unitPhrases):
        if '"' in phrase:
            phrase.replace('"', '&quot;')
        if i == 0:
            aup_f.writelines('<label t="0.0" t1="%s" title="%s"/>\n' % (unitTimes[i], phrase))
        elif i < len(unitTimes):
            aup_f.writelines('<label t="%s" t1="%s" title="%s"/>\n' % (unitTimes[i-1], unitTimes[i], phrase))
        else:
            aup_f.writelines('<label t="" t1=" " title="%s"/>\n' % (phrase))

    aup_f.writelines("</labeltrack>")
    aup_f.close()
    return

#- старт, открываем файл считываем данные и инициализируем словари (массивы) для записи данных
f = open("./tmp/audio_frase.txt", 'r')
re_sep = re.compile(';')
lines = f.readlines()
d = re_sep.split(lines[0])
data = [re_sep.split(i) for i in lines]

phrases = {}
fileNames = {}
unitNames = {}
unit_num = 1

# наполняем массивы данными из файла
for i, dat in enumerate(data):
    unit_num = int(dat[0])
    if not fileNames.get(unit_num):
        phrases[unit_num] = []
        fileNames[unit_num] = []
        unitNames[unit_num] = []

    phrases[unit_num].append(dat[3])
    fileNames[unit_num].append(dat[2])
    unitNames[unit_num].append(dat[1])


#запускаем функции слияния аудиофайлов и записи в аупфайл данных
for u in range(1,70):
    unitOutFile = "./res/%s.mp3" % u
    aupFile = "./res/_%s.aup" % u
    print 'Run compilation unit %u' % u
    unitTimes = audioFilesCompilation(u, fileNames[u], unitOutFile)
    print 'Write aup file unit %u' % u
    writeAupFile (u, unitTimes, phrases[u], aupFile)




