# install
!pip install fsspec
!pip install requests
!pip install xlrd
!pip install pickle
!pip install json
!pip install matplotlib
!pip install 

# import
from array import array
import math
from tabnanny import verbose
import pandas as pd
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import datetime as dt
# common imports
import zipfile
import time
# import datetime, timedelta
import datetime
from datetime import datetime, timedelta
from datetime import date
from dateutil import relativedelta
from io import StringIO
import pandas as pd
import pickle
from sklearn.base import BaseEstimator
from sklearn.base import TransformerMixin
from io import StringIO
import requests
import json
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
%matplotlib inline 
import os
import math
from subprocess import check_output
from IPython.display import display
import logging
import yaml
from collections import Counter
import re
import os
import stemgraphic

# 파일 읽어와서 데이터프레임 만들기

import pandas as pd
raw = "c:/Users/phoen/Downloads/ttc2014.xlsx"
xlsf = pd.ExcelFile(raw)
df = pd.read_excel(raw, sheet_name=xlsf.sheet_names[0])

for sht_name in xlsf.sheet_names[1:]:
    data = pd.read_excel(raw, sheet_name=sht_name)
    df = df.append(data)

df.head()
df.tail()
ttc2014 = df
ttc2014.shape  # (11027, 10)




# 데이터프레임 자료형 오해 다듬기

ttc2014.dtypes
'''
Report Date    datetime64[ns]
Route                   int64
Time                   object
Day                    object
Location               object
Incident               object
Min Delay             float64
Min Gap               float64
Direction              object
Vehicle               float64
'''
# 자료형 바로잡기
ttc2014['Vehicle'] = ttc2014['Vehicle'].astype(int)
ttc2014['Min Delay'] = ttc2014['Min Delay'].astype(int)
ttc2014['Min Gap'] = ttc2014['Min Gap'].astype(int)

# 결측치 일괄 제거
def fill_missing(dataset):
    for col in collist:
        dataset[col].fillna(value="missing", inplace=True)
    for col in continuouscols:
        dataset[col].fillna(value=0.0,inplace=True)
    for col in textcols:
        dataset[col].fillna(value="missing", inplace=True)
    return(dataset)

collist = ['Route','Day','Location','Direction','Vehicle']
continuouscols = ['Min Delay','Min Gap']
textcols = ['Incident']
ttc2014_1 = ttc2014
ttc2014_1 = fill_missing(ttc2014_1)
ttc2014_1.isnull().sum(axis=0)


'''
1. Vehicle 부분은 분포상, 대부분(2개 빼고 다)의 50건 이상 지연 열차 번호가 4200번대.
그러므로 뒤 두자리를 자르고, 예상되는 노후화 정도에 따라 블록화한다. 
블록은 3개로 나뉘며, 내용은 다음과 같다.

Vehicle 천백 자리   /   노후화 정도
40,41               /   3
42                  /   2
44,45,46            /   1*

1*: 제일 노후화의 영향을 덜 받는, 2014년 도입 차량들.
    1으로 할지 0으로 할지 논의 혹은 실험이 필요.
    는 미입력이 0이 되겠군...????
'''
import math

Vehicle = ttc2014['Vehicle']
# Vehicle.dtypes
# Vehicle.head()
# Vehicle.shape

# Vehicle[Vehicle.isna()]
Vehicle = Vehicle.fillna(0)
# int(Vehicle) # 안되는 건 왜일까 -> 해당 열에 fillna를 안해줬음.
# Vehicle = math.floor(Vehicle/100) # 이것도 안됨

'''
여기서 안된 이유는 결측치들이 제거되지 않았기 떄문이었는데,
이 부분은 위에 결측치 일괄 제거 fill_missing함수를 추가해줌으로써 시정하였음.
'''
Vehicle = (Vehicle/100).astype(int)
# (Vehicle/100).round(0).astype(int)
# pd.to_numeric(Vehicle/100, downcast='integer')
# pd.to_numeric(Vehicle/100.astype(str), downcast='integer')

cnt = Vehicle.value_counts()
cnt

Vehicle[Vehicle == 40|41] = 3
Vehicle[Vehicle == 42] = 2
Vehicle[Vehicle == 44|45|46] = 1
Vehicle[Vehicle>3] = 0
Vehicle[Vehicle<1] = 0

ttc2014['Vehicle'] = Vehicle

'''
2. Direction 열은 TTC 지도를 참고하여 처리하겠음. 
타블로 히트맵을 보면 지연은 다운타운에 몰려있고, 그 외엔 해안선에 몰려있는 분포 특성을 보인다.
그렇다면 지도상 남쪽이 +1, 그리고 동쪽이 +1이다.
반대는 -1, 결측시 0.

전처리를 위해 대소문자 구분을 없애고,
/, B, bound 등을 제거한다.
'''
Direction = ttc2014['Direction']
Direction.dtypes # object
'''
'E/B', 'W/B', 'S/B', 'N/B', 'B/W', 'EB', 'WB', 'BW', 'bw', 's',
    'NB', 'wb', 'eb', 'w/b', 'ew', 'b/w', 'eastbound', 'w', 'sb',
    'southbound', 'northbound', 'Service adjusted.', 'westbound', 'nb',
    0, 'b#', 'SB', 'we', 'EW', 'E', 'Service adjusted', 'W', '14',
    's/b', '5', 'Bw', '0', 'sw', '2'
'''

Direction = Direction.str.lower() # 대소문자 구분 제거
Direction.unique()
Direction

# 인간적으로 2, 5, 14는 뭐야.. 2시 방향? 그럼 14시 방향이야..? 필체 이슈야 뭐야..??
# 서비스 조정은 대체 운영 방향이랑 무슨 상관인가...

Direction = Direction.str.replace('/','',-1) # 문자열 제거&교제 -> 토큰 일치하도록
Direction = Direction.str.replace('.','',-1)
Direction = Direction.str.replace('#','',-1)
Direction = Direction.str.replace('missing','0',-1)
Direction = Direction.str.replace('service adjusted','0',-1)
Direction = Direction.str.replace('bound','',-1)
Direction = Direction.str.replace('east','e',-1)
Direction = Direction.str.replace('west','w',-1)
Direction = Direction.str.replace('south','s',-1)
Direction = Direction.str.replace('north','n',-1)
Direction = Direction.str.replace('b','',-1)
Direction.unique()

# 유효한 토큰은 4개지만 es,en등의 조합이 가능하다. 순서는 무작위.
Direction = Direction.str.replace('ew','e',-1)
Direction = Direction.str.replace('we','e',-1)
Direction = Direction.str.replace('sn','s',-1)
Direction = Direction.str.replace('ns','s',-1) 
# 상반된 방향타가 한 번에 들어간 경우 : 유리하게 해석
Direction.unique()

Direction = Direction.str.replace('se','e',-1)
Direction = Direction.str.replace('sn','s',-1)
Direction = Direction.str.replace('ns','s',-1)


Direction = Direction.str.replace('es','e',-1)
Direction = Direction.str.replace('se','e',-1)
Direction = Direction.str.replace('sn','s',-1)
Direction = Direction.str.replace('ns','s',-1)

Dir_East = Direction.find('e')

'es'.find('e')
'es'.find('s')





'''

'''



# 케라스용 데이터셋 만들기
from keras.preprocessing.text import Tokenizer

for col in textcols:
    if verboseout:
        print("처리될 텍스트 열:", col)
         