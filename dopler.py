#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import datetime
from datetime import date, timedelta
import time
# import more_itertools
from itertools import islice
import pandas as pd
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
# from mayavi import mlab
import os
import glob
from os.path import splitext

# дописать графику
def graph_plot(data):
    # пересчет на сетку
    # x = np.linspace(bsf['dist'].min(), bsf['dist'].max(), len(bsf['dist'].unique()))
    # y = np.linspace(bsf['hb'].min(), bsf['hb'].max(), len(bsf['hb'].unique()))
    x = np.linspace(bsf['dist'].min(), bsf['dist'].max(), 100)
    y = np.linspace(bsf['hb'].min(), bsf['hb'].max(), 100)
    X, Y = np.meshgrid(x, y)
    Z = griddata((bsf['dist'], bsf['hb']), bsf['value'], (X, Y), method='linear')

    fig = plt.figure(figsize=[16, 8])

    # 2D рисунок
    ax = fig.add_subplot(111)
    ff = ax.contourf(X, Y, Z, 8, cmap=cm.coolwarm)
    ax.plot(bsf['dist'], bsf['h'], color='Black', linestyle='-', linewidth=2)
    contour_labels = plt.contour(X, Y, Z, 8, colors='black', linewidth=.5)
    ax.clabel(contour_labels, inline=1, fontsize=10)
    cbar = fig.colorbar(ff, shrink=0.5, aspect=5)
    ax.set_xlabel('Расстояние')
    ax.set_ylabel('Глубина')
    cbar.set_label('Интенсивность рассеяния, дБ')
    ax.invert_yaxis()
    plt.savefig(file_out + '.png', dpi=150, facecolor='w', edgecolor='w',
                orientation='landscape', )
    plt.show()

    # переделать графику через Tricontour Smooth Delaunay
    # https://matplotlib.org/3.1.1/gallery/images_contours_and_fields/tricontour_smooth_delaunay.html#sphx-glr-gallery-images-contours-and-fields-tricontour-smooth-delaunay-py

    # 3D рисунок
    # fig = plt.figure()
    # ax = fig.gca(projection='3d')
    # surf = ax.plot_surface(X, Y, Z, rstride = 10, cstride = 1, cmap=cm.coolwarm,
    #                        linewidth=1, antialiased=False)
    # fig.colorbar(surf, shrink=0.5, aspect=5)
    # ax.invert_zaxis()
    # plt.savefig(file_out + '_3d.png', dpi=150, facecolor='w', edgecolor='w',
    #             orientation='landscape', )
    # plt.show()

    # триангуляция
    # fig = plt.figure()
    # ax = Axes3D(fig)
    # # surf = ax.plot_trisurf(bsf.iloc[:,0], bsf.iloc[:,1], bsf.iloc[:,2], cmap=cm.jet, linewidth=0.1)
    # surf = ax.plot_trisurf(X,Y,Z, cmap=cm.jet, linewidth=0.1)
    # fig.colorbar(surf, shrink=0.5, aspect=5)
    # ax.set_xlabel('Расстояние')
    # ax.set_ylabel('Глубина')
    # ax.set_zlabel('Скорость')
    # ax.invert_zaxis()
    # # ax.view_init(azim=200, elev=30)
    # ax.text2D(0.05, 0.95, 'Az {}, Z-elev {}'.format(ax.azim, ax.elev), transform=ax.transAxes)
    # plt.show()


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
    res['top_q'] =  round(float(lines[4].split()[1]), 3)
    res['bot_q'] =  round(float(lines[4].split()[2]), 3)
    res['nbins'] = int(lines[5].split()[0])

    # print(res)
    return res

def ens_proc(ens, ensnum, ensdist, ensh, enslat, enslon, topq, botq):

    res = {}
    df = pd.DataFrame([x.split() for x in ens], columns= ['hb', 'v', 'd', 'v1', 'v2', 'v3', 'v4',
                                                          'bs1', 'bs2', 'bs3', 'bs4', 'percgood', 'q'])
    rmcols = ['v1', 'v2', 'v3', 'v4', 'percgood'] # ненужные колонки
    df.drop(rmcols, inplace = True, axis=1) # удаляем ненужные
    df = df.replace(dict.fromkeys(['-32768', '2147483647', '255'], np.nan)) # замена отсутствующих данных
    df = df.dropna() # удаляем отсутствующие
    df['bs'] = df[['bs1', 'bs2', 'bs3', 'bs4']].mean(axis=1) # считаем среднее рассеяние
    df.drop(['bs1', 'bs2', 'bs3', 'bs4'], inplace = True, axis=1) # удаляем ненужные колонки рассеяния
    df['ens'] = ensnum # добавляем номер ансамбля
    df['dist'] = ensdist # добавляем расстояние от уреза
    df['h'] = ensh
    df['lat'] = enslat
    df['lon'] = enslon
    df['top_q'] = topq
    df['bot_q'] = botq
    df['v'] = df['v'].values * 0.01 # переводим скрость в метры в секунду
    df = df.round(3)
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
    # path = r'I:\Селенга2016\Доплер СТВОРЫ ВСЕ ВМЕСТЕ'
    # proc_list = []
    # for root, subfolders, files in os.walk(path):
    #     for f in files:
    #         if splitext(f)[1].lower() == ".txt":
    #             # print(root + "\\" + f)
    #             proc_list.append(root + "\\" + f)

    # file_proc(proc_list[0])
    # for f in proc_list:
    #     print('Processing: ' + f)
    # os.chdir(r"c:\temp\ob")
    # ff = glob.glob("*.txt")
    # for f in ff:
    #     file_in = f
    #     file_out = f.replace("txt", "out")
    #     file_proc(file_in, file_out)
    file_proc(r'c:\temp\doppler\2019-06-08\1_0\1_0_000_ASC.TXT', r'c:\temp\doppler\2019-06-08\1_0\1_0_000_ASC.out')
