# encode: UTF-8
import numpy as np
import datetime
from datetime import date, timedelta
import time
import more_itertools
from itertools import islice
import pandas as pd
import os
from os.path import splitext


def get_ensemble(file, n):
    return [x.strip() for x in islice(file, n)]


def ens_proc(ens, ncells):

    result = []
    dx = []         # пройденное расстояние по прямой distance made good
    h = []          # глубина по первому лучу - средняя для ансамбля
    vel = []        # средняя скорость по ансамблю см/с -> м/с
    topvel = []
    btvel = []
    topdir = []
    btdir = []
    avbsct = []

    print(ens)
    dxi = round(float(ens[2].split()[4]), 2)
    hi = round(float(ens[1].split()[8]), 2)
    result.append((dxi, hi))

    return result


def file_proc(path):
    savepath = path[:path.rfind("\\")+1]
    os.chdir(savepath)
    with open(path, "r") as f:
        f.readline()
        f.readline()
        head = f.readline().split()
        n = int(head[3])+6
        opr = []
        ne = get_ensemble(f, n)
        opr.append(ens_proc(ne, n))

        while ne:
            ni = ens_proc(ne, n)
            if len(opr) >= 1:
                # print(ni[0][0], opr[-1][0][0])
                if ni[0][0] != opr[-1][0][0]:
                    opr.append(ni)
            ne = get_ensemble(f, n)
        print('Finished ' + path)

        profname = path[path.rfind("\\")+1:path.rfind(".")]
        fout = profname + ".pfl"
        ff = open(fout, mode="w")
        for i in opr:
            line = profname + ", " + str(i[0][0]) + ", " + str(i[0][1])
            ff.write(line + "\n")
        ff.close()
    return




# главный модуль
if __name__ == "__main__":
    path = r'I:\Селенга2016\Доплер СТВОРЫ ВСЕ ВМЕСТЕ'
    proc_list = []
    for root, subfolders, files in os.walk(path):
        for f in files:
            if splitext(f)[1].lower() == ".txt":
                # print(root + "\\" + f)
                proc_list.append(root + "\\" + f)

    # file_proc(proc_list[0])
    for f in proc_list:
        print('Processing: ' + f)
        file_proc(f)

