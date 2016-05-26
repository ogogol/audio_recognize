import subprocess
import threading
import time
from text_to_elements3 import tokenize_text
import codecs
from text_utils3 import percent_diff, clean_text, coalitions, clean_collocation
from recognize3 import recognize
from send_to_google3 import SendToGoogle
import re
import shutil
from multiprocessing import Pool
import multiprocessing as mp


__author__ = 'tarasov'
##############################
filename_suff = "text/NYStories4"
recognition_method = 'sphinx'#'google' or 'sphinx' or 'wit' or 'ibm'

filename = "%s.aup" % filename_suff
output_filename = filename.replace(".aup", ".res.aup")
google_log_file_name = "%s_google_log.txt" % filename_suff
filename_mp3 = "%s.mp3" % filename_suff
TRACK = 0
TXT_FILENAME = "%s.txt" % filename_suff

##############################


print ("COPY \%s \%s" % (filename, output_filename))
#копируем исходны файл с именем аутпут файл, в него потом положим результат
shutil.copyfile(".\%s" % filename, ".\%s" % output_filename)
#subprocess.call(["COPY", "\%s \%s" % (filename, output_filename)], shell=True)


initial_text = tokenize_text(TXT_FILENAME)

def get_labeltracks():
    """
    Возвращает все дорожки меток ауп проекта
    """

    fileaup = open(filename, 'r')
    data = fileaup.read()
    pattern = re.compile('(<labeltrack.*?</labeltrack>)', re.S)
    values = pattern.findall(data)
    fileaup.close()
    return values

def changefloat():
    """
    Меняет формат времени на 0.1f
    """

    fileaup = open(filename, 'r')
    record = fileaup.read()
    fileaup.close()
    pattern = re.compile('<label t="(?P<t>.*?)" t1="(?P<t1>.*?)"')
    values = pattern.findall(record)
    for t, t1 in values:
        record = re.sub('t="%s" t1="%s"' % (t, t1), 't="%.1f" t1="%.1f"' % (float(t), float(t1)), record)
    record = re.sub('\t', '    ', record)
    # замена пробелов на пробел
    #    record = re.sub(r'\b[,\']* {2,}[,\']*\b', ' ', record)
    fileaup = open(filename, 'w')
    fileaup.write(record)
    fileaup.close()
    return values


if __name__ == '__main__':
    changefloat()
    labeltracks = get_labeltracks()

    try:
        file_google = open(google_log_file_name, 'r')
        print ("Файл с распознанными предложениями присутствует, считываю из него данные.")
        text_from_google = file_google.read()
        file_google.close()

        sentences_from_google = text_from_google.split('\n\n')

    except(IOError):
        print ("Файл с распознанными предложениями отсутствует, запускаю распознование.")
        send_to_google = SendToGoogle()
        sentences_from_google = send_to_google.send(labeltracks, filename_mp3, recognition_method)
        print ("Распознование гуглом завершено.")

        file_google = open(google_log_file_name, 'w')
        #subprocess.call("ECHO > " + google_log_file_name, shell=True)
        sentenses = ""
        for i, sentence in enumerate(sentences_from_google):
            sentenses += sentence + "\r\n"
        sentenses = sentenses[:-2]
        file_google.write(sentenses)
        file_google.close()

        fileaup = open(google_log_file_name, 'w')
        fileaup.write(sentenses)
        fileaup.close()
        
    print ("Полученные предложения:")
    print (sentences_from_google)
    recognize(labeltracks[TRACK], sentences_from_google, initial_text, output_filename)