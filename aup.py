# -*- coding: utf-8 -*-

# add_title
# - Date: 12.01.12
# - Time: 14:21
# - Description:
import re
from text_to_elements import tokenize_text
from text_utils import percent_diff
import cgi
import time
import subprocess

###-------------------------------------
###     Options
###-------------------------------------
TIME_FOR_SENTENCE_LENGTH_MODIFIER = 1.4
PLUS_FOR_SOLO_SENTENCE_LENGTH_MODIFIER = 0.2

#def add_title_aup(filename='08 A Tale of Two Cities 8.aup'):
#    """
#
#    """
#    count_words = 0
#    fileaup = open(filename, 'rb')
#    record = fileaup.read()
#    pattern = re.compile('<label t="(?P<t>.*?)" t1="(?P<t1>.*?)" title="(?P<title>.*?)"')
#    values = pattern.findall(record)
#
#    text = tokenize_text()
#    #сумма всего времени для последующего нахождение среднего времени слова
#    time_words = sum([float(t1)-float(t) for (t, t1, title) in values])
#
#    count_all_words = len(''.join(text).split())
#    #среднее время одного слова
#    time_word = time_words / count_all_words
#    print text
#    # изменяются t, t1 и начальные значения  tt, t1
#    for i, (t, t1, title) in enumerate(values):
#        try:
#            count_words = len(text[i].split())
#            if len(text[i].split()) == 1:
#                time_word += PLUS_FOR_SOLO_SENTENCE_LENGTH_MODIFIER
#        except IndexError:
#            pass
#
#        # время комментария
#        time_aup_comment = float(t1)-float(t)
#        # подсчет данных
#        if (count_words * time_word) * TIME_FOR_SENTENCE_LENGTH_MODIFIER <= time_aup_comment >= (count_words * time_word) / TIME_FOR_SENTENCE_LENGTH_MODIFIER:
#            if i == 0:
#                record = re.sub('title="%s"' % title, 'title="%s"' % text[i], record)
#                continue
#            print 'ERROR\n' \
#                  't-t1 = %s-%s,  %.4f <= %f => %.4f' % (t, t1, (count_words * time_word) * TIME_FOR_SENTENCE_LENGTH_MODIFIER, time_aup_comment, (count_words * time_word) / TIME_FOR_SENTENCE_LENGTH_MODIFIER)
#            break
#        else:
#            # Замена нового значения title
#            try:
#                text[i] = cgi.escape(text[i])
#                if title.replace("&apos;", "'") != text[i]:
#                    print '%.4f <= %f => %.4f' % ((count_words * time_word) * TIME_FOR_SENTENCE_LENGTH_MODIFIER, time_aup_comment, (count_words * time_word) / TIME_FOR_SENTENCE_LENGTH_MODIFIER)
#                    print '%s -> %s' % (title, text[i])
#                    #rewrite title
#                    record = re.sub(
#                        't="%s" t1="%s" title="%s"' % (t, t1, title),
#                        't="%s" t1="%s" title="%s"' % (t, t1, text[i]),
#                        record,
#                        count=1
#                    )
#            except IndexError:
#                print u"Нехватает записей в "
#                continue
#    fileaup.close()
#    fileaup = open(filename, 'wb')
#    print 'writen ok'
#    fileaup.write(record)
#    fileaup.close()


def update_title_aup(filename='08 A Tale of Two Cities 8.aup'):
    fileaup = open(filename, 'rb')
    record = fileaup.read()
    pattern = re.compile('<label t="(?P<t>.*?)" t1="(?P<t1>.*?)" title="(?P<title>.*?)"')
    values = pattern.findall(record)

    text = tokenize_text()
    print text
    for i, (t, t1, title) in enumerate(values):
        if str(title) == "___":
            print title, text[i+1].replace('\'', '&apos;')
            record = re.sub('title="%s"' % text[i+1], 'title="___"', record)
            record = re.sub('title="___"', 'title="%s"' % text[i+1], record, 1)
            print 'update ok'
    fileaup.close()
    fileaup = open(filename, 'wb')
    fileaup.write(record)
    fileaup.close()


def comment_aup(filename='3men_03.aup'):
    """
    функция убирает пустые места в комментах
    """
    fileaup = open(filename, 'rb')
    record = fileaup.read()
    pattern = re.compile('<label t="(?P<t>.*?)" t1="(?P<t1>.*?)" title="(?P<title>.*?)"')
    values = pattern.findall(record)

    # список всех отрезков и поделенные на 2
    dt = [abs((float(values[i][1]) - float(values[i+1][0])) / 2.0) for i in range(len(values)) if i + 2 <= len(values)]
    # изменяются t, t1 и начальные значения  tt, t1
    for i, (t, t1, title) in enumerate(values):
        tt, t1t1 = t, t1
        # замена значений
        t, t1 = float(t), float(t1)
        if i == 0:
            t1 += dt[i]
        # [1:-1] элементы
        elif i+1!=len(values):
            t -= dt[i-1]
            t1 += dt[i]
        else:
            t -= dt[i-1]
        # Замена новых значений t и t1
        record = re.sub('t="%s" t1="%s"' % (tt, t1t1), 't="%.4f" t1="%.4f"' % (t, t1), record)
    fileaup.close()
    fileaup = open(filename, 'wb')
    fileaup.write(record)
    fileaup.close()

def times_aup_file(filename='08 A Tale of Two Cities 8.aup'):
    times = list()

    fileaup = open(filename, 'rb')
    record = fileaup.read()
    pattern = re.compile('<label t="(?P<t>.*?)" t1="(?P<t1>.*?)"')
    values = pattern.findall(record)
    fileaup.close()
    return values


import threading
class MyThread(threading.Thread):
    def __init__(self, flow, filename):
        self.flow = flow
        self.filename = filename
        super(MyThread, self).__init__()

    def run(self):
        time_all = 0
        times_labels = times_aup_file()

        if self.flow == 1:
            start = 0
            end = len(times_labels)/2
        else:
            start = len(times_labels)/2
            end = len(times_labels)
        for i in xrange(start, end):
            t, t1 = times_labels[i]
            now = time.time()
            subprocess.call('sox "%s" ./tmp/%d.wav trim %s %s' % (self.filename, i, t, float(t1)-float(t)), shell=True)
            subprocess.call('sox ./tmp/%d.wav ./tmp/%d.flac rate 16k' % (i, i), shell=True)
            subprocess.call('rm ./tmp/%d.wav' % i, shell=True)
            subprocess.call('wget -q -U "Mozilla/5.0" --post-file ./tmp/%d.flac --header="Content-Type: audio/x-flac; rate=16000" -O - "http://www.google.com/speech-api/v1/recognize?lang=en-en&client=chromium" > ./tmp/%d.ret' % (i, i), shell=True)
            subprocess.call('rm ./tmp/%d.flac' % i, shell=True)
            subprocess.call('cat ./tmp/%d.ret | sed \'s/.*utterance":"//\' | sed \'s/","confidence.*//\' > ./tmp/%d.txt' % (i, i), shell=True)
            subprocess.call('rm ./tmp/%d.ret' % i, shell=True)
            print '%d / %d' % (i, end)
            time_all += (time.time() - now)
        print 'time - %d sekonds' % time_all

def googlevoice(filename='08 A Tale of Two Cities 8.mp3'):
    """
    Получаем список фраз - РФ
    """
    # удалим пустые места в метках
    comment_aup()

    for x in xrange(1, 3):
        thread = MyThread(x, filename)
        thread.start()




def labes_to_aup_file(filename='08 A Tale of Two Cities 8.aup'):
    """
    Записываем метки в aup файл
    """
    fileaup = open(filename, 'rb')
    record = fileaup.read()
    pattern = re.compile('<label t="(?P<t>.*?)" t1="(?P<t1>.*?)" title="(?P<title>.*?)"')
    values = pattern.findall(record)
    text = tokenize_text()
    # изменяется title
    print 'words', len(values), 'google - ', len(text)
    for i, (t, t1, title) in enumerate(values):
        filetxt = open('./tmp/%d.txt' % i, 'rb').read().replace('\n', '')
        print 'procent %d' % percent_diff(str(text[i].lower()), str(filetxt))

        # замена значений
        try:
            if percent_diff(text[i].lower(), filetxt) > 50 and len(text[i].split())>2:
                print 'TUTA YA'
                print text[i]
                print filetxt
                filetxt_last = open('./tmp/%d.txt' % int(i+1), 'rb').read().replace('\n', '')
                filetxt = '%s %s' % (filetxt, filetxt_last)
                # записываем в файл П и П+1
                tmp = open('./tmp/%d.txt' % i, 'wb')
                tmp.write(filetxt)
                tmp.close()

                #перезаписываем время, т.е. меняем t1 на t1+1
                t1t1 = float(values[i+1][1])
                record = re.sub('t="%s" t1="%s" title=".*"' % (t, t1), 't="%s" t1="%.4f" title="%s"' % (t, t1t1, filetxt), record)
                fileaup.close()
                fileaup = open(filename, 'wb')
                fileaup.write(record)
                fileaup.close()

                labes_to_aup_file()
                break

            print i, text[i].lower()
            print i, filetxt
            print
        except IndexError:
            pass
        t, t1 = float(t), float(t1)
        record = re.sub('t="%.4f" t1="%.4f" title="%s"' % (t, t1, title), 't="%.4f" t1="%.4f" title="%s"' % (t, t1, filetxt), record)
    fileaup.close()
    fileaup = open(filename, 'wb')
    fileaup.write(record)
    fileaup.close()


if __name__ == "__main__":

#    run_script(2)
#    googlevoice()
    #labes_to_aup_file()


    comment_aup()
#    add_title_aup()
#    update_title_aup()
    pass


