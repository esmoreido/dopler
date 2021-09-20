#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
import glob
import re
from pandas import DataFrame, melt
import numpy as np
from numpy import nan
from scipy.optimize import curve_fit
from scipy.stats import linregress
from itertools import islice
import matplotlib.pyplot as plt
import math
import warnings


def get_chunk(file, n):
    return [x.strip() for x in islice(file, n)]

def head_proc(lines):
    res = {}
    # номер ансамбля
    res['ens'] = int(lines[0].split()[7])
    # дата и время ансамбля
    res['date'] = dt.strftime(dt(year=2000 + int(lines[0].split()[0]), month=int(lines[0].split()[1]),
                                    day=int(lines[0].split()[2]), hour=int(lines[0].split()[3]),
                                    minute=int(lines[0].split()[4]), second=int(lines[0].split()[5])),
                              format('%d.%m.%Y %H:%M:%S'))
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

    return res

def ens_proc(ens, date, ensnum, ensdist, ensh, enslat, enslon, topq, botq):

    res = {}
    df = DataFrame([x.split() for x in ens], columns= ['hb', 'v', 'd', 'v1', 'v2', 'v3', 'v4',
                                                          'bs1', 'bs2', 'bs3', 'bs4', 'percgood', 'q'], dtype='float')
    rmcols = ['v1', 'v2', 'v3', 'v4', 'percgood'] # ненужные колонки
    df.drop(rmcols, inplace = True, axis=1) # удаляем ненужные
    df = df.replace(dict.fromkeys([-32768, 2147483647, 255], nan)) # замена отсутствующих данных
    df = df.dropna() # удаляем отсутствующие
    df['bs'] = df[['bs1', 'bs2', 'bs3', 'bs4']].mean(axis=1) # считаем среднее рассеяние
    df.drop(['bs1', 'bs2', 'bs3', 'bs4'], inplace = True, axis=1) # удаляем ненужные колонки рассеяния
    df['date'] = date
    df['ens'] = ensnum # добавляем номер ансамбля
    df['dist'] = ensdist # добавляем расстояние от уреза
    df['h'] = ensh # общая глубина
    df['lat'] = enslat # широта
    df['lon'] = enslon # долгота
    df['top_q'] = topq # верхний расход (вычисленный)
    df['bot_q'] = botq # придонный расход (вычисленный)
    df["v"] = df["v"] * 0.01 # переводим скрость в метры в секунду
    to_round = [col for col in df.columns if not 'lat' in col and not 'lon' in col and 'bs' not in col]
    df[to_round] = df[to_round].round(3)
    res = df[['date', 'ens', 'dist', 'lat', 'lon', 'h', 'top_q', 'bot_q', 'hb', 'v', 'd', 'bs', 'q']]
    # res = melt(df, id_vars=['ens', 'dist', 'lon', 'lat', 'hb', 'h']) # переформатируем в длинный формат
    # print(len(res))
    bserr = DataFrame()
    if not res.empty:
        topbs, botbs, bserr = bs_approx(ensnum, res['h'], res['hb'], res['bs'])
        res['top_bs'] = topbs[0]
        res['bot_bs'] = botbs[0]
        # print(bsa)

    return res, bserr


def file_proc(path_in, path_out):
    with open(path_in, "r") as f:
        f.readline()                    # пропускаем три строчки пустых
        f.readline()
        f.readline()
        opr = {}                        # массив для хедера
        df = DataFrame()             # массив для данных
        # считываем первый кусочек служебной информации - всегда 6 строк
        head = get_chunk(f, 6)
        err = DataFrame(columns=['ens', 'a', 'b', 'c', 'err'])
        while head:
            opr = head_proc(head)
            chunk = get_chunk(f, opr['nbins'])
            ens, bserr = ens_proc(chunk, opr['date'], opr['ens'], opr['b'], opr['h'], opr['lat'], opr['lon'],
                           opr['top_q'], opr['bot_q'])
            df = df.append(ens, ignore_index=True)
            err = err.append(bserr, ignore_index=True)
            head = get_chunk(f, 6)
        # реальные величины верхнего и нижнего расхода, не накопленной суммой
        df['top_q'] = df['top_q'] - df['top_q'].shift(1)
        df['bot_q'] = df['bot_q'] - df['bot_q'].shift(1)
        df = df.dropna()
        # df.to_csv(path_out, index=False, na_rep='-32768')
        df.to_excel(path_out, index=False, na_rep='-32768')
        # err.to_csv(path_out + "_err.txt", index=False, na_rep='-32768')
        err.to_excel(path_out + "_err.xlsx", index=False, na_rep='-32768')
        # err.plot(kind='line', subplots=True, figsize=(10, 16))
        # plt.show()

        r_df = df.groupby(['ens']).mean()
        r_df['ssc'] = 10 ** (0.914 + 0.014 * r_df['bs'])
        r_df['ssc_top'] = 10 ** (0.914 + 0.014 * r_df['top_bs'])
        r_df['ssc_bot'] = 10 ** (0.914 + 0.014 * r_df['bot_bs'])
        r_df.loc[r_df['q'] >= 0, 'mid_r'] = r_df['q'] * r_df['ssc']
        r_df.loc[r_df['top_q'] >= 0, 'top_r'] = r_df['top_q'] * r_df['ssc_top']
        r_df.loc[r_df['bot_q'] >= 0, 'bot_r'] = r_df['bot_q'] * r_df['ssc_bot']
        r_df['R'] = r_df.loc[:, ['mid_r', 'top_r', 'bot_r']].sum(axis=1)
        print(r_df['R'].sum(axis=0))
        print('Finished ' + path_in)
    return


def lm(x, a, b):
    return a * x + b

def pow(x, a, b, c):
    return a * np.exp(b * x) + c

def bs_approx(ens, h, hb, bs):
    warnings.filterwarnings('ignore')
    df = DataFrame({'h': h, 'hb': hb, 'bs': bs})
    df['ha'] = df.hb / df.h
    print(ens)
    plt.plot(bs, df.ha, 'k.', label='Data points')
    plt.ylabel('h отн')
    plt.xlabel('bs')
    plt.ylim([0, 1])
    plt.xlim([0, 120])
    plt.legend()


    # if len(h) > 3:
    #     errdf = DataFrame(columns=['ens', 'a', 'b', 'c', 'err'])
    #     popt, pcov = curve_fit(pow, df.ha, df.bs, maxfev=10000)
    #     # print(*popt)
    #     train = pow(df.ha, *popt)
    #     new_x = np.linspace(0, 1, 10)
    #     pred = pow(new_x, *popt)
    #     err = np.sqrt(np.mean((train-df.bs)**2))
    #     top_bs = pow(np.array([0.05]), *popt)
    #     bot_bs = pow(np.array([0.95]), *popt)
    #     errdf = errdf.append(DataFrame({'ens': ens, 'a': popt[0], 'b': popt[1], 'c': popt[2], 'err': err}, index=[0]),
    #                      ignore_index=True)
    #     # plt.plot(pred, new_x,  'g--', label="Fitted Curve")
    #     # plt.plot(pow(np.array([0.05, 0.95]), *popt),np.array([0.05, 0.95]),  'r.', label="Fitted Points")
    # else:
    errdf = DataFrame(columns=['ens', 'a', 'b', 'r', 'err'])
    slope, intercept, r_value, p_value, std_err = linregress(df.ha, df.bs)
    train = slope * df.ha + intercept
    err = np.sqrt(np.mean((train - df.bs) ** 2))
    corr = np.corrcoef(train, df.bs)
    top_bs = slope * np.array([0.05]) + intercept
    bot_bs = slope * np.array([0.95]) + intercept
    errdf = errdf.append(DataFrame({'ens': ens, 'slope': slope, 'intercept': intercept, 'r': corr[0, 1],
                                    'err': err}, index=[0]),
                         ignore_index=True)
    # plt.plot(slope * np.linspace(0, 1, 10) + intercept, np.linspace(0, 1, 10),  'b--', label="Linear fit")
    # plt.plot(slope * np.array([0.05, 0.95]) + intercept, np.array([0.05, 0.95]), 'r.', label="Linear points")
    #
    # plt.title(ens)
    # plt.gca().invert_yaxis()
    # # plt.show()
    # plt.draw()
    # plt.pause(0.0001)
    # plt.clf()

    return top_bs, bot_bs, errdf

if __name__ == "__main__":
    os.chdir(r'd:\YandexDisk\ИВПРАН\черский\Kolyma\10_0')
    # os.chdir(r'd:\YandexDisk\ИВПРАН\селенга\поле2019\doppler\Selenga2019\10_0')
    ff = glob.glob("*_ASC.txt")
    if not ff:
        print('No files to convert.')
        exit()
    else:
        print("Detected ASCII *_ASC.txt files: \n", "\n".join(ff))
        for f in ff:
            file_in = f
            file_out = re.sub(r'(?i)txt', 'xlsx', f)
            file_proc(file_in, file_out)
