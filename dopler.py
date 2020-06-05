#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import glob
import numpy as np
import time
import datetime
from datetime import date, timedelta
import time
# import more_itertools
from itertools import islice
import pandas as pd
import re
from os.path import splitext

def get_chunk(file, n):
    return [x.strip() for x in islice(file, n)]

def head_proc(lines):
    res = {}
    # номер ансамбля
    res['ens'] = int(lines[0].split()[7])
    # дата и время ансамбля
    res['date'] = datetime.datetime(year=2000 + int(lines[0].split()[0]), month=int(lines[0].split()[1]),
                                    day=int(lines[0].split()[2]), hour=int(lines[0].split()[3]),
                                    minute=int(lines[0].split()[4]), second=int(lines[0].split()[5]))
    # глубина
    res['h'] = round(float(lines[1].split()[8]), 3)
    # расстояние от ПН
    res['b'] = round(float(lines[2].split()[4]), 2)
    # широта и долгота, если есть
    res['lat'] = float(lines[3].split()[0]) if float(lines[3].split()[0]) != 30000. else 'NA'
    res['lon'] = float(lines[3].split()[1]) if float(lines[3].split()[1]) != 30000. else 'NA'
    # вычисленное значение расхода в поверхностном слое, нарастающей суммой от начала профиля
    res['top_q'] =  round(float(lines[4].split()[1]), 3)
    # вычисленное значение расхода в придонном слое
    res['bot_q'] =  round(float(lines[4].split()[2]), 3)
    # количество ячеек в ансамбле
    res['nbins'] = int(lines[5].split()[0])

    # print(res)
    return res

def ens_proc(ens, ensnum, ensdist, ensh, enslat, enslon, topq, botq):

    res = {}
    df = pd.DataFrame([x.split() for x in ens], columns= ['hb', 'v', 'd', 'v1', 'v2', 'v3', 'v4',
                                                          'bs1', 'bs2', 'bs3', 'bs4', 'percgood', 'q'], dtype='float')
    rmcols = ['v1', 'v2', 'v3', 'v4', 'percgood', 'q'] # ненужные колонки
    df.drop(rmcols, inplace = True, axis=1) # удаляем ненужные
    df = df.replace(dict.fromkeys([-32768, 2147483647, 255], np.nan)) # замена отсутствующих данных
    df = df.dropna() # удаляем отсутствующие
    df['bs'] = df[['bs1', 'bs2', 'bs3', 'bs4']].mean(axis=1) # считаем среднее рассеяние
    df.drop(['bs1', 'bs2', 'bs3', 'bs4'], inplace = True, axis=1) # удаляем ненужные колонки рассеяния
    df['ens'] = ensnum # добавляем номер ансамбля
    df['dist'] = ensdist # добавляем расстояние от уреза
    df['h'] = ensh # общая глубина
    df['lat'] = enslat # широта
    df['lon'] = enslon # долгота
    df['v'] = df['v'].values * 0.01 # переводим скрость в метры в секунду
    to_round = [col for col in df.columns if not 'lat' in col and not 'lon' in col]
    df[to_round] = df[to_round].round(3)
    res = pd.melt(df, id_vars=['ens', 'dist', 'lon', 'lat', 'hb', 'h']) # переформатируем в длинный формат
    return res


def file_proc(path_in, path_out):
    # savepath = path[:path.rfind("\\")+1]
    # os.chdir(savepath)
    with open(path_in, "r") as f:
        f.readline()                    # пропускаем три строчки пустых
        f.readline()
        f.readline()
        # head = f.readline().split()     # читаем первую строку
        # n = int(head[3])                # берем первичное количество ячеек
        opr = {}                        # массив для хедера
        df = pd.DataFrame()                         # массив для данных
        # считываем первый кусочек служебной информации - всегда 6 строк
        head = get_chunk(f, 6)
        while head:
            opr = head_proc(head)
            # opr['ens'] = head_proc(head)['ens']
            # opr['b'] = head_proc(head)['b']
            chunk = get_chunk(f, opr['nbins'])
            ens = ens_proc(chunk, opr['ens'], opr['b'], opr['h'], opr['lat'], opr['lon'], opr['top_q'], opr['bot_q'])
            df = df.append(ens, ignore_index=True)
            head = get_chunk(f, 6)
            # print(head)
        df.to_csv(path_out, index=False, na_rep='-32768')
        bsf = df.loc[df['variable'] == 'bs', ['dist', 'hb', 'value', 'h']]
        bsf['hb'] = bsf['hb'].astype(float)
        bsf['h'] = bsf['h'].astype(float)
        bsf['value'] = bsf['value'].astype(float)

        print('Finished ' + path_in)
    return




# главный модуль
if __name__ == "__main__":
    ff = glob.glob("*.txt")
    print("Detected ASCII *.txt files: \n", "\n".join(ff))
    for f in ff:
        file_in = f
        file_out = re.sub(r'(?i)txt', 'csv', f)
        file_proc(file_in, file_out)
