from bs4 import BeautifulSoup
import re
import psycopg2
import urllib.request as u
import datetime
import time
import requests as r
import math
import shelve
import numpy as np

import os.path
# DB
con = psycopg2.connect(
    "host=localhost port=5432 dbname=mydb user=t2 password=password")
cur = con.cursor()


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

# モデルをロード
s = shelve.open('model/m1_b100.db')
try:
    ld = s['map']
finally:
    s.close()

r16 = range(1, 7)
kumiban_all = ['%d-%d-%d' % (i0, i1, i2) for i0 in r16 for i1 in r16 if i1 !=
               i0 for i2 in r16 if i2 not in [i0, i1]]

KAI = {'all': 0, 'race': 0, 'atari': 0, 'kau': 0, 'haitou': 0}

def rune_nnn(race_id):
    [race_ymd, jcd, race_no] = race_id.split('-')
    N_ = len(kumiban_all)
    cur.execute("SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s ORDER BY ninki1,kumiban", [race_id])
    iDat = [ { 'kumiban': kumiban, 'value': math.log(float(odds1),1000) } for [kumiban, odds1] in cur ]
    
    inSet =  [ obj['value'] for obj in iDat ]
    inSet += [ obj['value'] for obj in sorted(iDat,key=lambda x:x['kumiban'])]
    inSet += [ 1 if int(race_no)==idx0 else 0 for idx0 in range(1,13)]
    if len(iDat) != 120:
        return
    graphDat = sigmoid(np.dot(np.tanh(np.dot(inSet, ld['ww0']) + ld['bb0']), ld['ww1']) + ld['bb1'])
    [kagen, jougen] = [10.00, 12.58]
    # [kagen, jougen] = [39.79, 50.10]
    # [kagen, jougen] = [250.99, 315.95]
    [kane, haitou, kauCnt, atariCnt] = [0, 0, 0, 0]
    cur.execute("SELECT COUNT(*), MAX(atari) FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s",
                (race_id, kagen, jougen))
    [cnt, atari] = cur.fetchone()
    KAI['all'] += 1
    if 0.1301 < graphDat :
        print(race_id, graphDat)
        kauCnt += 1
        kane = kane + cnt
        KAI['race'] += 1
        KAI['kau'] += cnt
        if atari is not None and atari > 0:
            cur.execute("SELECT atari,kumiban,ninki1,odds1 FROM odds_list_koushiki WHERE race_id=%s AND atari=1 AND odds1 BETWEEN %s AND %s", (
                race_id, kagen, jougen))
            [atari, kumiban, ninki1, odds1] = cur.fetchone()
            haitou = haitou + odds1
            atariCnt += 1
            KAI['atari'] += 1
            KAI['haitou'] += odds1
        cur.execute(
            "SELECT kumiban,ninki1,odds1 FROM odds_list_koushiki WHERE race_id=%s AND atari=1 ", [race_id])
        rec00 = cur.fetchone()
        if rec00 is None:
          return
        [kumiban, ninki1, odds1] = rec00
        print(' ', 'HIT ' if atari == 1 else '    ', kumiban, ninki1, odds1, ' ', kane, haitou, (haitou / kane)
              if kane != 0 else 0, kauCnt, atariCnt)
        cur.execute("SELECT atari,kumiban,ninki1,odds1 FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN  %s AND %s ORDER BY ninki1", (
            race_id, kagen, jougen))
        for [atari, kumiban, ninki1, odds1] in cur:
            print('    ', '〇' if atari == 1 else '☓ ', kumiban, ninki1, odds1)


cur.execute(
    "SELECT race_id FROM race_list_koushiki WHERE sumi='2' AND race_id > '20180500' ORDER BY SUBSTR(race_id,1,8),shime")
for [race_id] in cur.fetchall():
    rune_nnn(race_id)
    continue

print('0', KAI)
