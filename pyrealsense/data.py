import pandas as pd
import numpy as np
import os
from statistics import mean

s = 0
e = 479
def aver(filename, s, e):
    global dpath
    a = pd.read_csv('./test/%s/%s'%(dpath,filename), sep = ',', header = None)
    check = a.values[s:e+1]
    nz = check != 0
    a = np.average(check[nz])
    return a

dpath = raw_input("project name: ")
flist = os.listdir('./test/%s/'%dpath)
csvlist= []
for i in flist:
    if i.find('csv')!=-1:
        csvlist.append(i)


ans = []
for i in csvlist:
    ans.append(aver(i,s,e))
print ans
print mean(ans)
