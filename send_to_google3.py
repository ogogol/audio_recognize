#-*- coding: utf8 -*-

import re
#import subprocess
import threading
#import sys
#import urllib
#import json
import os
import shutil
from pydub import AudioSegment
from test2 import splitAudioFile
from test1 import writeLabelTracks_file
import speech_recognition as sr


def readKeys(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    API_Google_KEY ='';IBM_USERNAME ='';IBM_PASSWORD ='';WIT_AI_KEY =''
    BING_KEY ='';API_AI_CLIENT_ACCESS_TOKEN =''
    for l in lines:
        key, value = l.split(',')
        if key == 'API_Google_KEY':
            API_Google_KEY = value
        if key == 'IBM_USERNAME':
            IBM_USERNAME = value
        if key == 'IBM_PASSWORD':
            IBM_PASSWORD = value
        if key == 'WIT_AI_KEY':
            WIT_AI_KEY = value
        if key == 'BING_KEY':
            BING_KEY = value
        if key == 'API_AI_CLIENT_ACCESS_TOKEN':
            API_AI_CLIENT_ACCESS_TOKEN = value

    return API_Google_KEY, IBM_USERNAME, IBM_PASSWORD, WIT_AI_KEY, BING_KEY, API_AI_CLIENT_ACCESS_TOKEN

API_Google_KEY, IBM_USERNAME, IBM_PASSWORD, WIT_AI_KEY, BING_KEY, API_AI_CLIENT_ACCESS_TOKEN = readKeys('k.txt')

def requestTranscribe(filename, service ='google'):

    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = r.record(source)
    text =''
    if service == 'google':
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            text = r.recognize_google(audio, key=API_Google_KEY)
            print("Google Speech Recognition thinks you said - %s" % text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    if service == 'sphinx':
        # recognize speech using Sphinx
        try:
            text = r.recognize_sphinx(audio)
            print("Sphinx thinks you said - %s" % text)
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

    if service == 'wit':
        # recognize speech using Wit.ai
        try:
            text = r.recognize_wit(audio, key=WIT_AI_KEY)
            print("Wit.ai thinks you said - %s" % text)
        except sr.UnknownValueError:
            print("Wit.ai could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Wit.ai service; {0}".format(e))

    if service == 'ibm':
        # recognize speech using IBM Speech to Text
        try:
            text = r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD)
            print("IBM Speech to Text thinks you said - %s" % text)
        except sr.UnknownValueError:
            print("IBM Speech to Text could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from IBM Speech to Text service; {0}".format(e))

    if service == 'bing':
        # recognize speech using Microsoft Bing Voice Recognition
        try:
            text = r.recognize_bing(audio, key=BING_KEY)
            print("Microsoft Bing Voice Recognition thinks you said - %s" % text)
        except sr.UnknownValueError:
            print("Microsoft Bing Voice Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))

    if service == 'ai':
        # recognize speech using api.ai
        try:
            text = r.recognize_api(audio, client_access_token=API_AI_CLIENT_ACCESS_TOKEN)
            print("api.ai thinks you said - %s" % text)
        except sr.UnknownValueError:
            print("api.ai could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from api.ai service; {0}".format(e))

    return text


class SendToGoogle_onAupFile():
    sentences_from_google   = []
    load_counter            = 0
    number_of_sentence      = 0


    def send(self, labeltracks, filename_mp3, service):
        """
        Нарезаем аудиофайл на куски
        На выходе на каждую аудиофразу получаем .txt файл с текстом данной фразы распознанной гуглом 
        """
        for track in labeltracks:
            time_all = 0
            in_dir = 1
            pattern = re.compile('<label t="(.*?)" t1="(.*?)" title="(.*?)"')
            values = pattern.findall(track)

            # создадим папку для распознанных файлов
            if not os.path.exists('tmp'):
                os.makedirs('tmp')
            if not os.path.exists('.\\tmp\%d' % in_dir):
                os.makedirs('.\\tmp\%d' % in_dir)

            self.number_of_sentence = len(values)

            for i in range(self.number_of_sentence):
                self.sentences_from_google.append("")

            flow_number = 4
            sentence_per_flow = int(self.number_of_sentence / flow_number)

            for i in range(flow_number):
                start = sentence_per_flow * i
                end = sentence_per_flow * (i + 1)

                if end + (self.number_of_sentence % flow_number) >= self.number_of_sentence:
                    end = self.number_of_sentence

                thread = threading.Thread(target=self.send_in_flow, args=(start, end, values, filename_mp3, in_dir, service))
                thread.daemon = True
                thread.start()

        while self.load_counter < self.number_of_sentence:
            pass
        try:
            shutil.rmtree(".\\tmp")
        except:
            print("PermissionError: [WinError 5] Отказано в доступе: '.\\tmp'")

        return self.sentences_from_google


    def send_in_flow(self, start, end, values, filename_mp3, in_dir, service):
        sound = AudioSegment.from_mp3(filename_mp3)
        for i in range(start, end):
            t, t1, title = values[i]
            t *= 1000.0
            t1 *= 1000.0
            # пропускаем через распознавание речи и получаем список распознаных фраз
            s = sound[t:t1]
            s.export(".\\tmp\%d\%s.flac" % (in_dir, i), format="flac", bitrate="16k")

            text_from_google = requestTranscribe(".\\tmp\%d\%s.flac" % (in_dir, i), service)

            if text_from_google != None:
                self.sentences_from_google[i] = text_from_google

            print(str(self.load_counter + 1) + "/" + str(self.number_of_sentence) + "   " + str(i + 1) + "/" + str(end) + " " + self.sentences_from_google[i])
            #try:
                #os.remove(".\\tmp\%d\%s.flac" % (in_dir, i))
            #except:
                #print("File is busy now")
            self.load_counter += 1

class SendToGoogle():
    sentences_from_google   = []
    load_counter            = 0
    number_of_sentence      = 0

    def send(self, filename_mp3, filename_aup, service):
        """
        Нарезаем аудиофайл на куски
        На выходе на каждую аудиофразу получаем .txt файл с текстом данной фразы распознанной гуглом
        """
        # создадим папку для распознанных файлов
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        chunks_range = splitAudioFile(filename_mp3)
        writeLabelTracks_file(filename_aup, chunks_range)
        for i, val in enumerate(chunks_range):
            self.number_of_sentence = len(chunks_range)

            for i in range(self.number_of_sentence):
                self.sentences_from_google.append("")

            flow_number = 4
            sentence_per_flow = int(self.number_of_sentence / flow_number)

            for i in range(flow_number):
                start = sentence_per_flow * i
                end = sentence_per_flow * (i + 1)

                if end + (self.number_of_sentence % flow_number) >= self.number_of_sentence:
                    end = self.number_of_sentence

                thread = threading.Thread(target=self.send_in_flow, args=(start, end, chunks_range, filename_mp3, service))
                thread.daemon = True
                thread.start()

        while self.load_counter < self.number_of_sentence:
            pass
        try:
            shutil.rmtree(".\\tmp")
        except:
            print("PermissionError: [WinError 5] Отказано в доступе: '.\\tmp'")

        return self.sentences_from_google


    def send_in_flow(self, start, end, values, filename_mp3, service):
        for i in range(start, end):
            t, t1 = values[i]
            # пропускаем через распознавание речи и получаем список распознаных фраз

            text_from_google = requestTranscribe(".\\tmp\%s.wav" % i, service)

            if text_from_google != None:
                self.sentences_from_google[i] = text_from_google

            print(str(self.load_counter + 1) + "/" + str(self.number_of_sentence) + "   " + str(i + 1) + "/" + str(end) + " " + self.sentences_from_google[i])

            self.load_counter += 1