#-*- coding: utf8 -*-
import time
import re
from text_utils3 import percent_diff, clean_text, coalitions, clean_collocation
import codecs


def recognize(track, sentences_from_google, initial_text, output_filename):
    """
    Соединяем метки каким то алгоритмом
    """
    # track = labeltracks()[TRACK]

    # Регекспа получает массив массивов с двумя значениями времени и тайтлом
    pattern = re.compile('<label t="(.*?)" t1="(.*?)" title="(.*?)"/>')

    in_dir = 1
    values = pattern.findall(track)

    # Регекспа понимает нужно ли проводить дальнейшие действия с данным сентенсом,
    # или они были уже совершены в прошлом.
    pattern_for_empty = re.compile('^\d+_?\d?$')

    if values:
        labels = values
        initial_sentences = initial_text

        # перебор предложений
        if labels:
            finded_sentences = []
            for i in initial_sentences:
                finded_sentences.append(None)

            for i in range(2, 8):
                find_by_diff(finded_sentences, initial_sentences, sentences_from_google, i * 10)

                print(" ")
                print("После " + str(i * 10))
                print(finded_sentences)

                complete_series_one_missed(finded_sentences, initial_sentences, len(sentences_from_google))

                print(" ")
                print("После complete_series_one_missed")
                print(finded_sentences)

                modificate_initial_sentences(finded_sentences, initial_sentences, sentences_from_google)

                print(" ")
                print("После modificate_initial_sentences")
                print(finded_sentences)

            # initial_sentences = ["aaa", "bbb", "ccc"]
            # finded_sentences = [[0, 1], None, [2]]
            # sentences_from_google = ["aaa", "bbb", "ccc"]

            crudeMerging(finded_sentences, initial_sentences, sentences_from_google)
            
            print(" ")
            print("После crudeMerging")
            print(finded_sentences)

            cleaning(finded_sentences, initial_sentences)

            print(" ")
            print("После cleaning")
            print(finded_sentences)
            
            print("-----------------------------------------------------------\n" * 5)
            print("Итог:")
            for i in range(len(initial_sentences)):
                print("-----------------------------------------------------------")
                print(initial_sentences[i])

                if finded_sentences[i]:
                    print(finded_sentences[i])

                    for j in finded_sentences[i]:
                        print(sentences_from_google[j])

            print("Сохраняю")
            save_to_file(finded_sentences, initial_sentences, sentences_from_google, labels, output_filename)






def save_to_file(finded_sentences, initial_sentences, sentences_from_google, labels, output_filename):
    label_blank = '<label t="%s" t1="%s" title="%s"/>'
    new_text = ""

    for i, sentence in enumerate(initial_sentences):
        if finded_sentences[i]:
            start_time = labels[finded_sentences[i][0]][0]
            end_time = labels[finded_sentences[i][-1]][1]

            new_text += (label_blank % (start_time, end_time, sentence)) + "\n"
        else:
            print("Внимание ошибка! recognice.py save_to_file()")

    fileaup = codecs.open(output_filename, mode = 'r', encoding = 'utf-8')
    aup_file_text = fileaup.read()
    fileaup.close()

    regexp = re.compile("(<labeltrack.*?>).*(</labeltrack>)", re.DOTALL)
    aup_file_text = re.sub(regexp, r'\1%s\2' % new_text, aup_file_text)

    fileaup = codecs.open(output_filename, mode = 'w', encoding = 'utf-8')
    fileaup.write(aup_file_text)
    fileaup.close()






def cleaning(finded_sentences, initial_sentences):
    for i, sentence in enumerate(finded_sentences):
        if sentence == None or len(sentence) == 0:
            finded_sentences[i:i+1] = []
            initial_sentences[i:i+1] = []






def crudeMerging(finded_sentences, initial_sentences, recognized_sentences):
    """
    Объеденяем все последовательно идущие предложения которые ровны None.
    """
    sentences_for_merge = []
    last_not_none_sentence = -1

    for i in range(len(finded_sentences) + 1):
        is_out_of_range = False

        if i < len(finded_sentences):
            sentence = finded_sentences[i]
        else:
            is_out_of_range = True

        if sentence == None and is_out_of_range == False:
            sentences_for_merge.append(i)
        else:
            if len(sentences_for_merge) > 0:
                # Нашли что мержить, мержим
                new_sentence_id = sentences_for_merge[0]
                finded_sentences[new_sentence_id] = []

                if last_not_none_sentence >= 0:
                    prev_prev_sentence = finded_sentences[last_not_none_sentence]
                    start = prev_prev_sentence[-1] + 1
                else:
                    # Нулевой элемент пустой
                    start = 0

                if not is_out_of_range:
                    end = sentence[0]
                else:
                    # Последний элемент пустой
                    end = len(recognized_sentences)

                # Тут учитывать нулевой и последний нужно
                for j in range(start, end):
                    finded_sentences[new_sentence_id].append(j)

                initial_sentences[new_sentence_id] = joinSentence(sentences_for_merge, initial_sentences)

                finded_sentences[sentences_for_merge[0] + 1: sentences_for_merge[-1] + 1] = []
                initial_sentences[sentences_for_merge[0] + 1: sentences_for_merge[-1] + 1] = []

                # TODO: можно и нужно обойтись без рекурсии
                crudeMerging(finded_sentences, initial_sentences, recognized_sentences)
                break

            last_not_none_sentence = i





# Законсервированно
# def fill_missing(finded_sentences, initial_sentences, recognized_sentences):
#     """
#     Находит ситуацию когда в finded_sentences два предложения идут друг за другом но между ними нехватает фраз.
#     Тогда их помещаем либо в первое предложение либо во второе исходя из дифа.
#     """

#     # Код для тестирования
#     # sentences[1] = "ololo imba imba samba samba"
#     # sentences[2] = "velosipedium"

#     # sentences_from_google[0] = "ololo"
#     # sentences_from_google[1] = "imba imba"
#     # sentences_from_google[2] = "samba samba"
#     # sentences_from_google[3] = "velosipedium"

#     # finded_sentences[1] = [0, 1]
#     # finded_sentences[2] = [3]

#     # fill_missing(finded_sentences, sentences, sentences_from_google)

#     # print finded_sentences


#     for i in xrange(1, len(finded_sentences)):
#         sentence = finded_sentences[i]
#         prev_sentence = finded_sentences[i - 1]
        
#         if sentence and prev_sentence:
#             number_of_missed = (sentence[0] - prev_sentence[-1]) - 1

#             if number_of_missed > 0:
#                 for j in xrange(0, number_of_missed):
#                     checking_sentence = recognized_sentences[prev_sentence[-1] + 1]
#                     # print checking_sentence

#                     # print joinSentence(prev_sentence, recognized_sentences)
#                     # prev_sentence_diff = percent_diff






def modificate_initial_sentences(finded_sentences, initial_sentences, recognized_sentences):
    """
    Удаляет предложения из initial_sentences добавляя их в предыдущее или следующее.
    """
    for i in range(1, len(finded_sentences) - 2):
        prev_sentence = finded_sentences[i - 1]
        sentence = finded_sentences[i]
        next_sentence = finded_sentences[i + 1]
        
        if prev_sentence != None and sentence == None and next_sentence != None:
            if next_sentence[0] - prev_sentence[- 1] == 1:
                checked_with_next = check_for_modificate(initial_sentences[i] + " " + initial_sentences[i + 1], recognized_sentences, next_sentence, i + 1)
                checked_with_prev = check_for_modificate(initial_sentences[i - 1] + " " + initial_sentences[i], recognized_sentences, prev_sentence, i - 1)

                if checked_with_next["percent"] < checked_with_prev["percent"]:
                    sentence_with_lowest_percent = checked_with_next
                else:
                    sentence_with_lowest_percent = checked_with_prev

                # print "sentence_with_lowest_percent"
                # print sentence_with_lowest_percent


                id = sentence_with_lowest_percent["checked_sentences_id"]

                # print "*************"
                initial_sentences[id]
                current_sentence = joinSentence(finded_sentences[id], recognized_sentences)

                current_percent = percent_diff(initial_sentences[id], current_sentence)

                # print current_percent
                # print sentence_with_lowest_percent["percent"]


                if sentence_with_lowest_percent["percent"] <= current_percent:

                    if id < i:
                        initial_sentences[i - 1] = initial_sentences[i - 1] + " " + initial_sentences[i]
                    else:
                        initial_sentences[i + 1] = initial_sentences[i] + " " + initial_sentences[i + 1]

                    del initial_sentences[i]
                    del finded_sentences[i]
                    # TODO: Нужно сделать за один проход, тут можно обойтись без рекурсии.
                    modificate_initial_sentences(finded_sentences, initial_sentences, recognized_sentences)
                    break


def check_for_modificate(new_i_sentence, recognized_sentences, verified_sentences, verified_sentences_id):
    new_r_sentence = joinSentence(verified_sentences, recognized_sentences)

    percent = percent_diff(new_i_sentence, new_r_sentence)

    return {
        "percent":  percent,
        "checked_sentences_id": verified_sentences_id
    }


def joinSentence(join_list, main_list):
    string = ""
    for j in join_list:
        string += main_list[j] + " "
    string = string[:-1]
    return string






def complete_series_one_missed(finded_sentences, initial_sentences, rec_list_len):
    """
    Ищем ситуации когда между двух распознанных предложений, есть нераспознанное.
    В таком случае заполняем это предложение.
    """

    # Заполняем первый элемент
    first_element = finded_sentences[0]
    second_element = finded_sentences[1]

    if first_element == None and second_element != None:
        for i in range(second_element[0]):
            if finded_sentences[0] == None:
                finded_sentences[0] = []

            finded_sentences[0].append(i)

    # Заполняем последний
    penult_element = finded_sentences[- 2]
    last_element = finded_sentences[- 1]

    if last_element == None and penult_element != None:
        for i in range(penult_element[- 1] + 1, rec_list_len):
            if finded_sentences[- 1] == None:
                finded_sentences[- 1] = []

            finded_sentences[ - 1].append(i)

    # Заполняем промежуточные
    for i in range(1, len(finded_sentences) - 2):
        prev_sentence = finded_sentences[i - 1]
        sentence = finded_sentences[i]
        next_sentence = finded_sentences[i + 1]
        
        if prev_sentence != None and sentence == None and next_sentence != None:
            for j in range(prev_sentence[- 1] + 1, next_sentence[0]):
                if finded_sentences[i] == None:
                    finded_sentences[i] = []

                finded_sentences[i].append(j)






def find_by_diff(finded_sentences, initial_sentences, recognized_sentences, main_percent):
    """
    
    """
    google_index = 0

    for i in range(len(initial_sentences)):
        sentence = initial_sentences[i]
        # print "------------------------------------------------"
        # print sentence

        best_sentence = find_coincidence(sentence, recognized_sentences, google_index, main_percent)

        if best_sentence:
            best_sentance_indexes = best_sentence["best_sentance_indexes"]

            google_index = best_sentance_indexes[len(best_sentance_indexes) - 1] + 1
            
            if finded_sentences[i] == None:
                finded_sentences[i] = best_sentance_indexes


def find_coincidence(i_sentence, recognized_sentences, current_position_in_rec, main_percent):
    # print "---------------------------------------------------------------------------------" 
    # print "Sentence: '" + i_sentence + "':" 
    best_sentences = find_best_sentences(i_sentence, recognized_sentences, current_position_in_rec, main_percent)

    if best_sentences:
        best_sentence = best_sentences[0]

        if len(best_sentences) > 1:
            for i in range(1, len(best_sentences)):
                sentence = best_sentences[i]

                if sentence["percent"] < best_sentence["percent"]:
                    best_sentence = sentence

        # print best_sentence["best_sentence"]
        # print best_sentence["best_sentance_indexes"]
        return best_sentence


def find_best_sentences(i_sentence, recognized_sentences, current_position_in_rec, main_percent):
    i = 0
    best_sentences = []

    while current_position_in_rec < len(recognized_sentences):
        best_sentence = find_best_sentence(i_sentence, recognized_sentences, current_position_in_rec)
        best_sentance_indexes = best_sentence["best_sentance_indexes"]

        # print best_sentence["percent"]

        if best_sentence["percent"] < main_percent:
            best_sentences.append(best_sentence)
            # break

        current_position_in_rec += 1
        i += 1

        if i > 10:
            # Скорее всего предложение сверху пропущено, и бесполезно смотреть дальше
            break

    return best_sentences


def find_best_sentence(i_sentence, recognized_sentences, current_position):
    # print "-------find_best_sentence-------------"
    # print i_sentence, " "

    percent = 100
    best_sentence = None
    best_sentance_indexes = []

    r_sentence = ""

    # Цикл проверяет i_sentence на совпадение с recognized_sentences.
    # В результате получаем best_sentence.
    for j in range(current_position, len(recognized_sentences)):
        r_sentence = r_sentence + recognized_sentences[j]
        # print r_sentence, " "

        new_percent = percent_diff(i_sentence, r_sentence)
        # print new_percent

        if new_percent < percent:
            best_sentence = r_sentence
            percent = new_percent
            best_sentance_indexes.append(j)
        else:
            break

        r_sentence = r_sentence + " "

    return {
        "percent":percent,
        "best_sentence":best_sentence,
        "best_sentance_indexes":best_sentance_indexes
    }