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
# s = shelve.open('model/20.db')
# s = shelve.open('model/m80_5700_10.db')
s = shelve.open('model/m1000_1258.db')
try:
    ld = s['map']
finally:
    s.close()

r16 = range(1, 7)
kumiban_all = ['%d-%d-%d' % (i0, i1, i2) for i0 in r16 for i1 in r16 if i1 !=
               i0 for i2 in r16 if i2 not in [i0, i1]]


KAI = {'all': 0, 'race': 0, 'atari': 0, 'kau': 0, 'haitou': 0}


def rune_continue(race_id):
    N_ = len(kumiban_all)
    cur.execute(
        "SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s", [race_id])
    iDat = {kumiban: math.log(float(odds1), 999) if int(
        odds1) != 0 else 0 for [kumiban, odds1] in cur}
    odds1Ary = [{'kmbn': kumi, 'odds1': iDat[kumi]
                 if kumi in iDat else 999} for kumi in kumiban_all]
    inSet = [np.float(rec['odds1'])
             for rec in sorted(odds1Ary, key=lambda x: x['odds1'])] + [np.float(rec['odds1']) for rec in sorted(odds1Ary, key=lambda x: x['kmbn'])]
    # print(inSet)
    graphDat = sigmoid(
        np.dot(np.tanh(np.dot(inSet, ld['ww0']) + ld['bb0']), ld['ww1']) + ld['bb1'])
    rate = 30
    kane = 0
    cnt = 0
    cntKachi = 0
    kauGoukei = 0
    hensen = []
    puramai = []
    kakeme = 100
    cntMap = {idx: 0 for idx in range(rate)}
    sakaime = 15
    threashold = 0.117
    threashold = 0.105
    isKau = []
    for idx1 in range(len(graphDat)):
        if graphDat[idx1] > threashold and idx1 < sakaime:
            continue
            # break
        elif graphDat[idx1] > threashold and idx1 >= sakaime:
            isKau.append(idx1)
    if graphDat.tolist().index(max(graphDat)) >= sakaime and len(isKau) > 0:
        # if len(isKau) > 0:
        for idx1 in isKau:
            cur.execute("SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s",
                        (race_id, math.pow(1000, (idx1 - 0) / float(rate)), math.pow(1000, (idx1 + 1) / float(rate))))
            odds1Recs = [odds1Rec for odds1Rec in cur]
            cur.execute(
                "SELECT kumiban,haitou FROM race_list_koushiki WHERE race_id=%s AND haitou !=0", [race_id])
            atariObj = cur.fetchone()
            if atariObj is not None:
                isAtari = [odds1Rec[0]
                           for odds1Rec in odds1Recs].index(atariObj[0]) if atariObj[0] in [odds1Rec[0] for odds1Rec in odds1Recs] else None
                if isAtari is not None:
                    KAI['atari'] += odds1Recs[int(isAtari)][1]
                    print('0Atari =', race_id, len(odds1Recs),
                          odds1Recs[int(isAtari)][1], atariObj[0], atariObj[1])
                else:
                    print('0Hazure=', race_id, len(odds1Recs),
                          0, atariObj[0], atariObj[1])
                KAI['d'] = KAI['d'] + len(odds1Recs)
            else:
                print('0Fumei=', race_id, 'fumei', isKau, len(odds1Recs))
            for odds1Rec in odds1Recs:
                print('  ', odds1Rec[0], odds1Rec[1])
            cntMap[idx1] = cntMap[idx1] + 1
            cnt = cnt + len(odds1Recs)
        # print(race_id, len(graphDat), cnt, cntKachi, kauGoukei, kane, isKau)


def rune_break(race_id):
    N_ = len(kumiban_all)
    cur.execute(
        "SELECT kumiban,haitou FROM race_list_koushiki WHERE race_id=%s", [race_id])
    fo = cur.fetchone()
    if fo is None or fo[1] == 0:
        return
    cur.execute(
        "SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s", [race_id])
    iDat = {kumiban: math.log(float(odds1), 999) if int(
        odds1) != 0 else 0 for [kumiban, odds1] in cur}
    odds1Ary = [{'kmbn': kumi, 'odds1': iDat[kumi]
                 if kumi in iDat else 0} for kumi in kumiban_all]
    inSet = [np.float(rec['odds1'])
             for rec in sorted(odds1Ary, key=lambda x: x['odds1'])] + [np.float(rec['odds1']) for rec in sorted(odds1Ary, key=lambda x: x['kmbn'])]
    # print(inSet)
    graphDat = sigmoid(
        np.dot(np.tanh(np.dot(inSet, ld['ww0']) + ld['bb0']), ld['ww1']) + ld['bb1'])
    rate = 30
    kane = 0
    cnt = 0
    cntKachi = 0
    kauGoukei = 0
    hensen = []
    puramai = []
    kakeme = 100
    cntMap = {idx: 0 for idx in range(rate)}
    sakaime = 15
    # threashold = 0.117
    # threashold = 0.133
    threashold = 0.095
    threashAry = [threashold if idx >=
                  15 else threashold for idx in range(rate)]
    isKau = []
    for idx1 in range(len(graphDat)):
        if graphDat[idx1] > threashAry[idx1] and idx1 < sakaime:
            # continue
            break
        elif graphDat[idx1] > threashAry[idx1] and idx1 >= sakaime:
            isKau.append(idx1)
    # if graphDat.tolist().index(max(graphDat)) >= sakaime and len(isKau) > 0:
    if len(isKau) > 0:
        # for idx1 in range(min(isKau), max(isKau) + 2):
        # isKau.append(max(isKau) + 1)
        for idx1 in isKau:
            cur.execute("SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s",
                        (race_id, math.pow(1000, (idx1 - 0) / float(rate)), math.pow(1000, (idx1 + 1) / float(rate))))
            odds1Recs = [odds1Rec for odds1Rec in cur]
            # for odds1Rec in odds1Recs:
            #     print(race_id, odds1Rec[0], odds1Rec[1])
            # print(race_id)
            cur.execute(
                "SELECT kumiban,haitou FROM race_list_koushiki WHERE race_id=%s AND haitou !=0", [race_id])
            atariObj = cur.fetchone()
            if atariObj is not None:
                isAtari = [odds1Rec[0]
                           for odds1Rec in odds1Recs].index(atariObj[0]) if atariObj[0] in [odds1Rec[0] for odds1Rec in odds1Recs] else None
                if isAtari is not None:
                    KAI['atari'] += odds1Recs[int(isAtari)][1]
                    print('0Atari =', race_id, len(odds1Recs),
                          odds1Recs[int(isAtari)][1], atariObj[0], atariObj[1])
                else:
                    print('0Hazure=', race_id, len(odds1Recs),
                          0, atariObj[0], atariObj[1])
                KAI['d'] = KAI['d'] + len(odds1Recs)
            else:
                print('0Fumei=', race_id, 'fumei', isKau, len(odds1Recs))
            for odds1Rec in odds1Recs:
                print('  ', odds1Rec[0], odds1Rec[1])
            cntMap[idx1] = cntMap[idx1] + 1
            cnt = cnt + len(odds1Recs)
        # print(race_id, len(graphDat), cnt, cntKachi, kauGoukei, kane, isKau)


def rune_old(race_id):
    N_ = len(kumiban_all)
    cur.execute(
        "SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s", [race_id])
    iDat = {kumiban: math.log(float(odds1), 999) if int(
        odds1) != 0 else 0 for [kumiban, odds1] in cur}
    odds1Ary = [{'kmbn': kumi, 'odds1': iDat[kumi] if kumi in iDat else 0}
                for kumi in kumiban_all]
    inSet = [np.float(rec['odds1']) for rec in sorted(odds1Ary, key=lambda x: x['odds1'])] + \
        [np.float(rec['odds1'])
         for rec in sorted(odds1Ary, key=lambda x: x['kmbn'])]

    graphDat = sigmoid(
        np.dot(np.tanh(np.dot(inSet, ld['ww0']) + ld['bb0']), ld['ww1']) + ld['bb1'])
    kane = 0
    rate = 30
    cnt = 0
    cntKachi = 0
    kauGoukei = 0
    hensen = []
    puramai = []
    kakeme = 100
    cntMap = {idx: 0 for idx in range(rate)}
    sakaime = 15
    threashold = 0.133
    threashAry = [0.133 if idx >= 15 else 1 for idx in range(rate)]
    for idx1 in range(len(graphDat)):
        if graphDat[idx1] > threashAry[idx1] and idx1 < sakaime:
            break
        elif graphDat[idx1] > threashAry[idx1] and idx1 >= sakaime:
            cur.execute("SELECT COUNT(*),MAX(atari) FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s",
                        (race_id, math.pow(999, (idx1 - 0) / float(rate)), math.pow(999, (idx1 + 1) / float(rate))))
            [kau, atari] = cur.fetchone()
            kauGoukei = kauGoukei + kau
            kane = kane - (kakeme * kau)
            if atari is not None and atari > 0:
                cntKachi = cntKachi + 1
                cur.execute(
                    "SELECT odds1 FROM odds_list_koushiki WHERE race_id=%s AND atari=1", [race_id])
                [odds1] = cur.fetchone()
                kane = kane + (kakeme * odds1)
                puramai.append(kakeme * odds1)
            else:
                puramai.append(-kakeme * kau)
            hensen.append(kane)
            cntMap[idx1] = cntMap[idx1] + 1
            cnt = cnt + 1
            cur.execute("SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s ORDER BY ninki1",
                        (race_id, math.pow(999, (idx1 - 0) / float(rate)), math.pow(999, (idx1 + 1) / float(rate))))
            # print(race_id, kau, cnt, cntKachi, kauGoukei, kane, (kane), ((kauGoukei * kakeme)))
            print(race_id, kau)
            for rr in cur:
                print(rr[0], rr[1])


def rune_nnn(race_id):
    s = shelve.open('model/m1000_1258_119.db')
    try:
        ld = s['map']
    finally:
        s.close()
    N_ = len(kumiban_all)
    cur.execute(
        "SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s", [race_id])
    iDat = {kumiban: math.log(float(odds1), 999) if int(
        odds1) != 0 else 0 for [kumiban, odds1] in cur}
    odds1Ary = [{'kmbn': kumi, 'odds1': iDat[kumi] if kumi in iDat else 0}
                for kumi in kumiban_all]
    inSet = [np.float(rec['odds1']) for rec in sorted(odds1Ary, key=lambda x: x['odds1'])] + [np.float(rec['odds1'])
                                                                                              for rec in sorted(odds1Ary, key=lambda x: x['kmbn'])]
    graphDat = sigmoid(
        np.dot(np.tanh(np.dot(inSet, ld['ww0']) + ld['bb0']), ld['ww1']) + ld['bb1'])
    [kagen, jougen] = [10.00, 12.58]
    # [kagen, jougen] = [39.79, 50.10]
    # [kagen, jougen] = [250.99, 315.95]
    [kane, haitou, kauCnt, atariCnt] = [0, 0, 0, 0]
    cur.execute("SELECT COUNT(*), MAX(atari) FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s",
                (race_id, kagen, jougen))
    [cnt, atari] = cur.fetchone()
    KAI['all'] += 1
    if 0.1101 < graphDat[0] and graphDat[0] < 0.5:
        print(race_id, graphDat[0])
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


def rune_list(race_id):
    s = shelve.open('model/m1000_1258_119.db')
    try:
        ld = s['map']
    finally:
        s.close()
    N_ = len(kumiban_all)
    cur.execute(
        "SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s", [race_id])
    iDat = {kumiban: math.log(float(odds1), 999) if int(
        odds1) != 0 else 0 for [kumiban, odds1] in cur}
    odds1Ary = [{'kmbn': kumi, 'odds1': iDat[kumi] if kumi in iDat else 0}
                for kumi in kumiban_all]
    inSet = [np.float(rec['odds1']) for rec in sorted(odds1Ary, key=lambda x: x['odds1'])] + [np.float(rec['odds1'])
                                                                                              for rec in sorted(odds1Ary, key=lambda x: x['kmbn'])]
    graphDat = sigmoid(
        np.dot(np.tanh(np.dot(inSet, ld['ww0']) + ld['bb0']), ld['ww1']) + ld['bb1'])
    [kagen, jougen] = [10.00, 12.58]
    # [kagen, jougen] = [39.79, 50.10]
    # [kagen, jougen] = [250.99, 315.95]
    [kane, haitou, kauCnt, atariCnt] = [0, 0, 0, 0]
    cur.execute("SELECT COUNT(*), MAX(atari) FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s",
                (race_id, kagen, jougen))
    [cnt, atari] = cur.fetchone()
    cur.execute(
        "SELECT shime,haitou FROM race_list_koushiki WHERE race_id=%s", [race_id])
    [shime, haitou] = cur.fetchone()
    ymd_date = datetime.datetime.strptime(race_id[0:8], '%Y%m%d')
    kwd = race_id.split('-')
    print(race_id, kwd[0], kwd[1], kwd[2], ymd_date.weekday(),
          shime, haitou, atari, cnt, graphDat[0])


def rune_seikika(race_id):
    s = shelve.open('model/m40_b100_s0888.db')
    try:
        ld = s['map']
    finally:
        s.close()
    N_ = len(kumiban_all)
    cur.execute(
        "SELECT ninki1,min,max,log FROM odds_list_base00 ORDER BY ninki1")
    logBase00 = [{'min0': float(min0), 'max0': float(max0), 'log': float(log)} for [
        ninki1, min0, max0, log] in cur]
    cur.execute(
        "SELECT race_id,kumiban,ninki1,odds1,atari FROM odds_list_koushiki WHERE race_id=%s ORDER BY race_id,ninki1,kumiban", [race_id])
    iDat = {kumiban: min(max(math.log(float(odds1), logBase00[ninki1 - 1]['max0']), 0), 1) for [
        race_id, kumiban, ninki1, odds1, atari] in cur}
    odds1Ary = [{'kmbn': kumi, 'odds1': iDat[kumi] if kumi in iDat else 0}
                for kumi in kumiban_all]
    inSet = [np.float(rec['odds1']) for rec in sorted(odds1Ary, key=lambda x: x['odds1'])] + [np.float(rec['odds1'])
                                                                                              for rec in sorted(odds1Ary, key=lambda x: x['kmbn'])]
    graphDat = sigmoid(
        np.dot(np.tanh(np.dot(inSet, ld['ww0']) + ld['bb0']), ld['ww1']) + ld['bb1'])
    [kagen, jougen] = [10.00, 12.59]
    # [kagen, jougen] = [39.79, 50.10]
    # [kagen, jougen] = [250.99, 315.95]
    [kane, haitou, kauCnt, atariCnt] = [0, 0, 0, 0]
    cur.execute("SELECT COUNT(*), MAX(atari) FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s",
                (race_id, kagen, jougen))
    [cnt, atari] = cur.fetchone()
    KAI['all'] += 1
    if 0.878 > graphDat[0]:
        print(race_id, graphDat[0])
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
        [kumiban, ninki1, odds1] = cur.fetchone()
        print(' ', 'HIT ' if atari == 1 else '    ', kumiban, ninki1, odds1, ' ', kane, haitou, (haitou / kane)
              if kane != 0 else 0, kauCnt, atariCnt)
        cur.execute("SELECT atari,kumiban,ninki1,odds1 FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN  %s AND %s ORDER BY ninki1", (
            race_id, kagen, jougen))
        for [atari, kumiban, ninki1, odds1] in cur:
            print('    ', '〇' if atari == 1 else '☓ ', kumiban, ninki1, odds1)


# cur.execute(
#    "SELECT race_id FROM race_list_murao_view a WHERE sumi='2' AND race_id > '20170800' AND haitou>0 AND EXISTS (SELECT * FROM odds_list_3t b WHERE b.race_id=a.race_id AND atari=1) ORDER BY SUBSTR(race_id,1,8),shime")
cur.execute(
    "SELECT race_id FROM race_list_koushiki a WHERE sumi='2' AND race_id > '20171030' AND haitou>0 AND EXISTS (SELECT * FROM odds_list_koushiki b WHERE b.race_id=a.race_id AND atari=1) ORDER BY SUBSTR(race_id,1,8),shime")
for [race_id] in cur.fetchall():
    # rune_break(race_id)
    # rune_continue(race_id)
    # rune_old(race_id)
    rune_nnn(race_id)
    # rune_list(race_id)
    # rune_seikika(race_id)
    continue

print('0', KAI)

# import touhyou
# touhyou.nyukin()

# Query string::::::::
# cid	ap238
# r	2090979701531
# Form data::::::::
# dummyA
# dummyB
# betAmount	200
# betPassword	4616
# operationKbn
# token	xheyOFO0WhDLdeasBmyG5Lx88bHxkmxN
# _csrf	7e90da1d-e65e-4d81-adea-9a8b28e60b72
# screenFrom	D628
# betWay	5
# jyoCode	21
# multiJyo	false
# selectionJyoList	21
# multiRace	false
# selectionRaceNoList	06
# lastSelectionKachishiki	6
# lastSelectionBetWay	1
# lastSelectionRacer	1


# Form data
# orteusPrevForward	DEFAULT_TARGET!/TENTP017A.jsp!false
# org.apache.struts.taglib.html.TOKEN	93bef6b9636aaf04229f0b50cefdb73a
# in_KanyusyaNo	08099575
# in_AnsyoNo	1325
# in_PassWord	uS7b3Y
# in_AuthAfterUrl	/
# orteusElements	true
# com.nec.jp.orteusActionMethod.login	controlLogin
# login	Submit
