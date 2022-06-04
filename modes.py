import time
from tqdm import tqdm
import re
import spacy
from itertools import combinations

class FileInfo:
    nlp = spacy.load("en_core_web_sm")

def name_finder(strocka):
    nlp = FileInfo.nlp
    doc = nlp(strocka)
    pun_free_list = []
    for token in doc:
        if token.pos_ == "PROPN":
            pun_free = re.sub(r"[^\w\s]","", token.text) #убираем пунктуацию
            if len(pun_free) > 0:
                pun_free_list.append(pun_free)
    return(pun_free_list)

def mode1(filename, delimiter, min_weight, name_list):
    name_list = name_list.split(" ")
    big_list = []
    for name_name in name_list.copy():
        if "_" in name_name:
            name_list.remove(name_name)
            sup_list = name_name.split("_")
            big_list.append(sup_list)
            for name in sup_list:
                name_list.append(name)
            sup_list = []

    file = open(filename, "r", encoding = "utf-8")
    writefile = open("log.txt", "w")
    filename1 = filename.split(".")[0] + "_graph.csv"
    writecsv = open(filename1, "w")
    writefile.write(filename + "\n" + delimiter + "\n")

    dict1 = {} #словарь с номерами кусков текста и именами
    dict2 = {} #словарь для частотности
    dict3 = {} #вспомогательный словарь для сортировки char_list по частотности
    pair_dict = {} # словарь для вывода режима 2
    char_list = [] #список персонажей
    final_list = [] #char_list но по частотности
    count = 0
    check = 0
    text = file.read()
    text_list = text.split(delimiter)
    for i in tqdm(range(len(text_list))):
        count += 1 #счетчик номеров абзаца для словаря ниже
        paragraph = text_list[i].strip() #чистим текст
        res = name_finder(paragraph) #ищем через спейси все то, что похоже на имя
        for elem in res.copy(): #убираем из выдачи спейси все, что с маленькой буквы, итерируемся по копии списка во избежание
            if elem.islower() == True:
                res.remove(elem)
        dict1[count] = res # записываем в словарь под номером абзаца
        for name in res.copy():
            if name not in name_list:
                res.remove(name)
            dict1[count] = res

    for sth in dict1: # собираем словарь частотности
        for k in range (len(dict1[sth])):
            if dict1[sth][k] not in dict2:
                dict2[dict1[sth][k]] = 0
            if dict1[sth][k] in dict2:
                dict2[dict1[sth][k]] = dict2[dict1[sth][k]] + 1

    for pair in dict1.items():
        for name in pair[1].copy():
            for sup_list in big_list:
                if name in sup_list:
                    pair[1].remove(name)
                    if sup_list[0] not in pair[1]:
                        pair[1].append(sup_list[0])
        cleary = set(pair[1])
        clearly = list(cleary)
        dict1[pair[0]] = clearly


    for sth in dict1:
        for k in range (len(dict1[sth])): #записываем в char_list уникальные вхождения имен героев, потом отдадим это юзеру
            if str(dict1[sth][k]) not in char_list: #фильтр для отсечения возможных опечаток.
                char_list.append(dict1[sth][k])

    for el in char_list: #формируем список по убыванию частотности
        dict3[el] = dict2[el]
    for i in range (len(char_list)):
        for key in dict3:
            if dict3[key] >= check:
                check = dict3[key]
                mean = key
        final_list.append(mean)
        check = 0
        dict3.pop(mean)

    writefile.write(str(dict1) + "\n\n") #с номерами абзацев
    writefile.write(str(dict2) + "\n\n") # с частотностью
    writefile.write("Список частотности: " + str(final_list))

    for pair in dict1.items():
        if len(pair[1]) > 1:
            for j in combinations(pair[1],2):
                j = tuple(sorted(j))
                if j in pair_dict:
                    pair_dict[j] += 1
                if j not in pair_dict:
                    pair_dict[j] = 1
    writecsv.write("Source,Type,Target,Weight" + "\n")
    for enters in pair_dict.items():
        if int(enters[1]) >= min_weight:
            writecsv.write(enters[0][0] + "," + "Undirected" + "," + enters[0][1] + "," + str(enters[1]) + "\n")
    writecsv.close()
    return filename1

def mode2_1(filename, delimiter, frequency):

    file = open(filename, "r", encoding = "utf-8")
    writefile = open("log.txt", "w")
    writefile.write(filename + "\n" + delimiter + "\n")

    dict1 = {} #словарь с номерами кусков текста и именами
    dict2 = {} #словарь для частотности
    dict3 = {} #вспомогательный словарь для сортировки char_list по частотности
    char_list = [] #список персонажей
    final_list = [] #char_list но по частотности
    final_list_freq = []
    count = 0
    check = 0
    text = file.read()
    text_list = text.split(delimiter)
    for i in tqdm(range(len(text_list))):
        count += 1 #счетчик номеров абзаца для словаря ниже
        paragraph = text_list[i].strip() #чистим текст
        res = name_finder(paragraph) #ищем через спейси все то, что похоже на имя
        for elem in res.copy(): #убираем из выдачи спейси все, что с маленькой буквы, итерируемся по копии списка во избежание
            if elem.islower() == True:
                res.remove(elem)
        dict1[count] = res # записываем в словарь под номером абзаца
    for sth in dict1: # собираем словарь частотности
        for k in range (len(dict1[sth])):
            if dict1[sth][k] not in dict2:
                dict2[dict1[sth][k]] = 0
            if dict1[sth][k] in dict2:
                dict2[dict1[sth][k]] = dict2[dict1[sth][k]] + 1

    for things in dict1:
        for w in range (len(dict1[things])): #записываем в char_list уникальные вхождения имен героев, потом отдадим это юзеру
            if str(dict1[things][w]) not in char_list and dict2[dict1[things][w]] >= frequency: #фильтр для отсечения возможных опечаток.
                char_list.append(dict1[things][w])

    for es in char_list: #формируем список по убыванию частотности
        dict3[es] = dict2[es]
    for l in range (len(char_list)):
        for key in dict3:
            if dict3[key] >= check:
                check = dict3[key]
                mean = key
        final_list.append(mean)
        check = 0
        dict3.pop(mean)

    writefile.write(str(dict1) + "\n\n") #с номерами абзацев
    writefile.write(str(dict2) + "\n\n") # с частотностью
    writefile.write("Список частотности: " + str(final_list))
    return dict1, dict3, final_list

def mode2_2(chrtr,dict1,dict3,filename,min_weight):
    pair_dict = {} # словарь для вывода режима 2
    big_list = []
    name_list = chrtr.split(" ")
    for name_name in name_list:
        if "_" in name_name:
            name_list.remove(name_name)
            sup_list = name_name.split("_")
            big_list.append(sup_list)
            for sth in sup_list:
                name_list.append(sth)
            sup_list = []

    for key, values in dict1.items():
        clearlist = []
        for name in values:
            if name in name_list:
                clearlist.append(name)
                for sup_list in big_list:
                    if name in sup_list:
                        clearlist.remove(name)
                        clearlist.append(sup_list[0])
#    print(clearlist)
        cleary = set(clearlist)
        clearly = list(cleary)
        dict3[key] = clearly

    for pair in dict3.items():
        if len(pair[1]) > 1:
            for j in combinations(pair[1],2):
                j = tuple(sorted(j))
                if j in pair_dict:
                    pair_dict[j] += 1
                if j not in pair_dict:
                    pair_dict[j] = 1
    fnamenew = filename.split(".")[0] + "_graph.csv"
    writecsv = open(fnamenew, "w")
    writecsv.write("Source,Type,Target,Weight" + "\n")
    for enters in pair_dict.items():
        if int(enters[1]) >= min_weight:
            writecsv.write(enters[0][0] + "," + "Undirected" + "," + enters[0][1] + "," + str(enters[1]) + "\n")
    writecsv.close()
    return fnamenew


def mode3(filename, delimiter, quantity, cont):
    dict1 = {} #словарь с номерами кусков текста и именами
    dict3 = {} #вспомогательный словарь для сортировки char_list по частотности
    main_dict = {}
    char_list = [] #список персонажей
    final_list_freq = []
    final_dict = {} # то же, что final_list, но для режима 3
    chapter_list = [] # для режима 3: сюда пока идут словари с частотностью имен по главам
    count = 0
    check = 0

    file = open(filename, "r", encoding = "utf-8")
    writefile = open("log.txt", "w")
    fname = filename.split(".")[0] + "_frequency.txt"
    writetxt = open(fname, 'w')
    writefile.write(filename + "\n" + delimiter + "\n")
    writetxt.write(filename + "\n" + delimiter + "\n")
    text = file.read()
    text_list = text.split(delimiter)

    for i in tqdm(range(len(text_list))):
        count += 1 #счетчик номеров абзаца для словаря ниже
        paragraph = text_list[i].strip() #чистим текст
        res = name_finder(paragraph) #ищем через спейси все то, что похоже на имя
        for elem in res.copy(): #убираем из выдачи спейси все, что с маленькой буквы, итерируемся по копии списка во избежание
            if elem.islower() == True:
                res.remove(elem)
        dict1[count] = res # записываем в словарь под номером абзаца
        for el in res:
            if el not in dict3:
                dict3[el] = 0
            if el in dict3:
                dict3[el] += 1
        chapter_list.append(dict3)
        dict3 = {}
    for dh in range(len(chapter_list)):
        if len(chapter_list[dh]) > quantity:
            for s in range (quantity):
                for keys in chapter_list[dh]:
                    if chapter_list[dh][keys] >= check:
                        check = chapter_list[dh][keys]
                        mean = keys
                final_list_freq.append(mean)
                check = 0
                chapter_list[dh].pop(mean)
            final_dict[dh] = final_list_freq
            final_list_freq = []
        if len(chapter_list[dh]) <= quantity:
            for elems in chapter_list[dh]:
                final_list_freq.append(elems)
            final_dict[dh] = final_list_freq
            final_list_freq = []
    for numer, info in final_dict.items():
        # print(f"{delimiter} {int(numer)+1}: {info}\n")
        writefile.write(f"{delimiter} {str(int(numer)+1)}: {str(info)}\n")
        writetxt.write(f"{delimiter} {str(int(numer)+1)}: {str(info)}\n")
    if cont == True:
        for ens, lists in final_dict.items():
            for h in range (len(lists)):
                if lists[h] not in main_dict:
                    main_dict[lists[h]] = 1
                if lists[h] in main_dict:
                    main_dict[lists[h]] = main_dict[lists[h]] + 1
        check = 0
        for key1 in main_dict:
            if main_dict[key1] >= check:
                check = main_dict[key1]
                mean = key1
    return fname, mean
