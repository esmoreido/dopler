# dopler
Программа для преобразования файлов ASCII Output формата RDInstruments WinRiver2 до отдельных значений характеристик по ячейкам. 
Если вы хотите посмотреть код, склонируйте или скачайте его. **Если вы хотите просто преобразовать свои файлы - скачайте [dopler.exe](https://bit.ly/dopler_v01) и запустите в папке с вашими `*_ASC.txt` файлами.**

## Проверено на файлах
- RioGrande WorkHorse 600 kHz
- RiverRay 600 kHz - учитывает разное количество ячеек, которое выдает этот прибор

## Выходной формат
```
ens,dist,lon,lat,hb,h,variable,value
73,3.43,106.53000833,52.17094833,2.12,4.85,v,1.813
73,3.43,106.53000833,52.17094833,2.62,4.85,v,1.705
73,3.43,106.53000833,52.17094833,3.12,4.85,v,1.662
73,3.43,106.53000833,52.17094833,1.12,4.85,d,348.79
73,3.43,106.53000833,52.17094833,1.62,4.85,d,342.31
73,3.43,106.53000833,52.17094833,2.12,4.85,d,323.71
73,3.43,106.53000833,52.17094833,2.62,4.85,d,347.24
73,3.43,106.53000833,52.17094833,3.12,4.85,d,345.64
73,3.43,106.53000833,52.17094833,1.12,4.85,bs,93.775
73,3.43,106.53000833,52.17094833,1.62,4.85,bs,94.775
73,3.43,106.53000833,52.17094833,2.12,4.85,bs,93.725
```
### Обозначения:
- ens: номер ансамбля
- dist: расстояние от начала профиля
- lon: долгота точки ансамбля в десятичных градусах (если измерение было с GPS)
- lat: широта точки ансамбля в десятичных градусах (если измерение было с GPS)
- hb: глубина ячейки
- h: общая глубина ансамбля
- variable: название измеренной в ячейке характеристики
- value: значение измеренной в ячейке характеристики

### Характеристики:
- v: скорость течения в ячейке, м/с
- d: направление течения в ячейке, °
- bs: значение обратного рассеяния, дБ

# Python tool for TRDI RioGrande ADCP ASCII files processing
Simply converts generic ASCII Output from RDInstruments WinRiver2 software to csv files. If you want to see through the code, clone or download it. **If you simply want to convert your files, donload [dopler.exe](https://bit.ly/dopler_v01) and run it in a folder with your `*_ASC.txt` ASCII files.**

## Output format
```
ens,dist,lon,lat,hb,h,variable,value
73,3.43,106.53000833,52.17094833,2.12,4.85,v,1.813
73,3.43,106.53000833,52.17094833,2.62,4.85,v,1.705
73,3.43,106.53000833,52.17094833,3.12,4.85,v,1.662
73,3.43,106.53000833,52.17094833,1.12,4.85,d,348.79
73,3.43,106.53000833,52.17094833,1.62,4.85,d,342.31
73,3.43,106.53000833,52.17094833,2.12,4.85,d,323.71
73,3.43,106.53000833,52.17094833,2.62,4.85,d,347.24
73,3.43,106.53000833,52.17094833,3.12,4.85,d,345.64
73,3.43,106.53000833,52.17094833,1.12,4.85,bs,93.775
73,3.43,106.53000833,52.17094833,1.62,4.85,bs,94.775
73,3.43,106.53000833,52.17094833,2.12,4.85,bs,93.725
```
### Where: 
- ens: ensemble number
- dist: distance from the profile start
- lon: longitude of the ensemble point in decimal degrees (if the measurement was made with GPS attached)
- lat: latitude of the ensemble point in decimal degrees (if the measurement was made with GPS attached)
- hb: cell depth
- h: total ensemble depth
- variable: name of the characteristic measured in the cell
- value: value of the characteristic measured in the cell

### Characteristics:
- v: flow velocity in the cell, m / s
- d: flow direction in the cell, °
- bs: backscatter value, dB

## Tested on
- RioGrande WorkHorse 600 kHz
- RiverRay 600 kHz - accounts for variable cell size and count

By Seva Moreido 
