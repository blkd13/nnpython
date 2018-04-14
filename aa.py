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
import subprocess
import touhyou

import os.path
# DB
con = psycopg2.connect(
    "host=localhost port=5432 dbname=mydb user=t2 password=password")
cur = con.cursor()

bet_flg = False


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def pageSum(fd):
    html = u.urlopen("http://odds.kyotei24.jp/index-%s.html" % fd)
    time.sleep(1)
    soup = BeautifulSoup(html, "html.parser")
    for block in soup.select(".table.table-bordered"):
        idx = 0
        recs = block.select("tr")
        if len(recs) >= 1:
            kaijou = ''
            name = ''
            for rec in recs:
                tds = rec.select('td')
                if len(tds) > 1:
                    no = 0
                    for h in rec.select('a'):
                        no += 1
                        # print((fd, kaijou, no, name, h['href']))
                        cur.execute(
                            "INSERT INTO race_list(kaisaibi,kaijou,no,name,url) VALUES(%s,%s,%s,%s,%s)",
                            (fd, kaijou, no, name,
                             h['href'] if 'href' in h else 'null')
                        )
                        # print(h['href'])
                else:
                    head = tds.pop()
                    kaijou = head.b.string
                    name = head.contents[1].string
                    print(head.b.string + head.contents[1].string)
                    con.commit()
                    # print(idx)
    con.commit()


def pageDetail(s):
    for rec in cur.execute('SELECT * FROM race_list ORDER BY serial_no'):
        html = u.urlopen("http://odds.kyotei24.jp/%s" % s)
        d = BeautifulSoup(html, "html.parser")
        for m in d.select('table.table-bordered.table-condensed'):
            m.pop()
            for r in m:
                ds = r.select('div')
                ds.pop()


def nikaime(tdate):
    html = u.urlopen('http://www.orangebuoy.net/odds/?day=%d&month=%d&year=%d&mode=99' %
                     (tdate.day, tdate.month, tdate.year))
    fd = "{0:%Y%m%d}".format(tdate)
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.select('#post-204 tr')[3].select('td')[1].select('a'):
        kaijou = a.string
        url = a['href']
        print(kaijou, url)
        cur.execute(
            "INSERT INTO race_list(kaisaibi,kaijou,url) VALUES(%s,'%s','%s')" %
            (fd, kaijou, url)
        )


def maruoSeikei(text):
    return text.replace('                                               <th', '<tr><th').replace('                                                                           <tr>', '</tr><tr>')


def murao_race(tdate):
    race_param = {"select_yearfrom": tdate.year,
                  "select_monthfrom": '%02d' % tdate.month,
                  "select_dayfrom": '%02d' % tdate.day,
                  "select_yearto": tdate.year,
                  "select_monthto": '%02d' % tdate.month,
                  "select_dayto": '%02d' % tdate.day,
                  "select_kaijo": 'all',
                  "select_grade": 'all',
                  "select_series": 'all',
                  "select_schedule": 'all',
                  "select_timezone": 'all',
                  "select_week": 'all',
                  "select_race": '01',
                  "select_racesbt": 'all',
                  "select_rank": 'all',
                  "select_fixedapproach": 'all',
                  "select_kimarite": 'all',
                  "select_kachisiki": 0,
                  "select_kaime0": 'all',
                  }
    html = r.post(
        'http://kyotei.murao111.net/searchResult#kensaku', data=race_param)
    time.sleep(1)
    soup = BeautifulSoup(maruoSeikei(html.text), "html5lib")
    trs0 = soup.select('.searchresult tr')[1:]
    for race_kaijo in trs0:
        kaijo = race_kaijo.select('td')[3].text.split('#')[0]
        race_param["select_kaijo"] = kaijo
        race_param["select_race"] = 'all'
        # race_param["select_race"] = '%02d' % race
        html = r.post(
            'http://kyotei.murao111.net/searchResult#kensaku', data=race_param)
        time.sleep(1)
        soup = BeautifulSoup(maruoSeikei(html.text), "html5lib")
        trs1 = soup.select('.searchresult tr')[1:]
        print(tdate, race_param['select_kaijo'])
        for race in trs1:
            td = race.select('td')
            print(tdate, race_param['select_kaijo'], td[8].text)
            k = td[17].text.split('-')
            cur.execute("SELECT * FROM race_list_murao WHERE kaisaibi=%s AND kaijou=%s AND race_no=%s",
                        (td[1].text, kaijo, '%02d' % int(td[8].text.split(' ')[0])))
            obj = cur.fetchone()
            # print(obj, "%s %s %s" % (
            #     td[1].text, kaijo, '%02d' % int(td[8].text.split(' ')[0])))
            if obj is None:
                cur.execute(
                    "INSERT INTO race_list_murao(kaisaibi,youbi,kaijou,nittei,saishu,jikantai,grade,race_no,series,rank,shubetsu,tenki,fuusoku,nami,kimarite,no1,no2,no3,haitou3t,haitou2t)" +
                    "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (td[1].text, td[2].text, kaijo, td[4].text, td[5].text, td[6].text, td[7].text, '%02d' % int(td[8].text.split(
                        ' ')[0]), td[9].text, td[10].text, td[11].text, td[12].text, td[13].text, td[14].text, td[15].text, int(k[0]), int(k[1]), int(k[2]), int(td[18].text), int(td[19].text))
                )
            # print('race_fine')
        # print('kaijou_fine')
        con.commit()


def mura_odd_d(rec, odds_param):
    # print(odds_param)
    html = r.post(
        'http://kyotei.murao111.net/searchodds#kensaku', data=odds_param)
    soup = BeautifulSoup(maruoSeikei(html.text), "html5lib")
    time.sleep(1)
    # print(soup)
    trs1 = soup.select('.searchresult tr')[1:]
    race_id = "%s-%s-%s" % (rec[1], rec[2], '%02d' % rec[3])
    for line in trs1:
        tds = line.select('td')
        kumiban = tds[15].text
        atari = 1 if tds[15].text == tds[21].text else 0
        cur.execute(
            "INSERT INTO odds_list_murao (race_serial,race_id,kachisiki,kumiban,atari,odds5,ninki5,odds1,ninki1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (rec[0], race_id, odds_param['select_kachisiki'], kumiban, atari, float(tds[16].text), int(tds[17].text), float(tds[18].text), int(tds[19].text)))


def murao_odds():
    odds_param = {"select_kachisiki": 0,
                  "select_kaime0": 'all',
                  "select_kaime1": 'all',
                  "select_kaime2": 'all',
                  "select_kaime3": 'all',
                  "select_yearfrom": '2017',
                  "select_monthfrom": '01',
                  "select_dayfrom": '31',
                  "select_yearto": '2017',
                  "select_monthto": '01',
                  "select_dayto": '31',
                  "select_oddsmin": 'bf5min',
                  "select_odds_rule": 0,
                  "input_odds_from_popular": 0,
                  "input_odds_to_popular": 100,
                  "input_odds_from_value": 0,
                  "input_odds_to_value": 999.9,
                  "select_kaijo": 'all',
                  "select_grade": 'all',
                  "select_series": 'all',
                  "select_schedule": 'all',
                  "select_timezone": 'all',
                  "select_week": 'all',
                  "select_race": '01',
                  "select_racesbt": 'all',
                  "select_rank": 'all',
                  "select_fixedapproach": 'all'
                  }
    cur_sel = con.cursor()
    while True:
        cur_sel.execute(
            'SELECT serial_no,kaisaibi,kaijou,race_no FROM race_list_murao WHERE status=0 ORDER BY serial_no DESC LIMIT 1')
        rec = cur_sel.fetchone()
        if rec == None:
            break
        odds_param['select_yearfrom'] = rec[1][0:4]
        odds_param['select_monthfrom'] = rec[1][4:6]
        odds_param['select_dayfrom'] = rec[1][6:8]
        odds_param['select_yearto'] = rec[1][0:4]
        odds_param['select_monthto'] = rec[1][4:6]
        odds_param['select_dayto'] = rec[1][6:8]
        odds_param['select_kaijo'] = rec[2]
        odds_param['select_race'] = '%02d' % rec[3]
        print(rec)

        # 3連単 1～100
        odds_param['select_kachisiki'] = '0'
        odds_param['input_odds_from_popular'] = 0
        odds_param['input_odds_to_popular'] = 100
        mura_odd_d(rec, odds_param)

        # 3連単 101～120
        odds_param['input_odds_from_popular'] = 101
        odds_param['input_odds_to_popular'] = 120
        mura_odd_d(rec, odds_param)

        # 3連複
        odds_param['select_kachisiki'] = '1'
        odds_param['input_odds_from_popular'] = 0
        odds_param['input_odds_to_popular'] = 100
        mura_odd_d(rec, odds_param)

        # 2連単
        odds_param['select_kachisiki'] = '2'
        mura_odd_d(rec, odds_param)

        # 2連複
        odds_param['select_kachisiki'] = '3'
        mura_odd_d(rec, odds_param)

        cur_sel.execute(
            'update race_list_murao SET status=1 WHERE serial_No=%s', [rec[0]])
        con.commit()


def koushiki(tdate):
    fd = "{0:%Y%m%d}".format(tdate)
    path = 'data/k' + fd[2:8] + '.txt_utf8'
    if not os.path.exists(path):
        print(fd, 'Not Found')
        return
    print(path)
    f = open(path, 'r')
    kaijou = '00'
    race_no = '1'
    list_flg = False
    for row in f:
        if not list_flg:
            if row[2:6] == 'KBGN':
                kaijou = row[0:2]
                # print(row[0:2])
            if row[4:6] == 'R ':
                race_no = row[2:4]
                # print(row[2:4])
            if row[0:1] == '-':
                list_flg = True
        else:
            key = fd + '-' + kaijou + '-' + ('%02d' % int(race_no))
            line = re.sub(r'  *', ' ', row).strip()
            if len(line) == 0:
                list_flg = False
            else:
                tds = line.split(' ')
                cur.execute(
                    "SELECT * FROM race_result_koushiki WHERE race_id=%s AND tei=%s", (key, int(tds[1])))
                if cur.fetchone() is None:
                    if tds[0][0:1] in ['K', 'L']:
                        # 欠場
                        cur.execute(
                            "insert into race_result_koushiki(race_id,chakujun,tei,touban,moter,boat)"
                            + " VALUES (%s,%s,%s,%s,%s,%s)", (key, tds[0], int(tds[1]), int(tds[2]), int(tds[4]), int(tds[5])))
                    else:
                        cur.execute(
                            "insert into race_result_koushiki(race_id,chakujun,tei,touban,moter,boat,tenji,shinnyu,starttime,racetime)"
                            + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (key, tds[0], int(tds[1]), int(tds[2]), int(tds[4]), int(tds[5]), float(tds[6]), tds[7], tds[8], tds[9]))
    con.commit()
    f.close()


def main_old():
    today = datetime.datetime.today()
    tstr = '2017-10-29'
    tdatetime = datetime.datetime.strptime(tstr, '%Y-%m-%d')
    tdate = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day)
    # koushiki(tdate)

    # print(tdate)
    R = 14
    # R = 204
    # R = 1
    for idx in range(R):
        # print(tdate)
        # koushiki(tdate)
        # print(tdate.year, tdate.month, tdate.day)
        # nikaime(tdate)
        # pageSum(tdate)
        # murao_race(tdate)
        # con.commit()
        tdate = tdate + datetime.timedelta(days=1)
    # murao_odds()


def period(dt, fmt_0, fmt_1='%Y-%m-%d %H:%M:S'):
    return datetime.datetime.strptime(dt.strftime(fmt_0), fmt_1)


def main():
    now = datetime.datetime.now()
    koushiki_asaichi(now.strftime('%Y%m%d'), now.strftime('%H%M'))
    koushiki_exec()
    fill_result()
    # # 1分後の分の20秒時点
    # next_point = period(
    #     now + datetime.timedelta(minutes=1), '%Y-%m-%d %H:%M:20')
    # # 当日の21:30時点
    # day_end = period(now, '%Y-%m-%d 21:30:00')
    # # 当日の08:30時点
    # day_start = period(now, '%Y-%m-%d 08:30:00')


def koushiki_asaichi(ymd, hm):
    if hm < '0830':
        # 8時半より前の場合は時刻表が変更される可能性があるので何もしないでおしまい
        return
    cur.execute(
        "SELECT COUNT(*) FROM race_list_koushiki WHERE SUBSTR(race_id,1,8)=%s", [ymd])
    if cur.fetchone()[0] > 0:
        return
    print('Init', ymd)
    html = r.get('https://www.boatrace.jp/owpc/pc/race/index')
    soup = BeautifulSoup(html.text, "html5lib")
    time.sleep(1)
    for rec0 in soup.select('.table1 tbody a > img[height=16]'):
        jcd = rec0['src'].split('_')[3].split('.')[0]
        html = r.get(
            'https://www.boatrace.jp/owpc/pc/race/raceindex?jcd=%s&hd=%s' % (jcd, ymd))
        soup = BeautifulSoup(html.text, "html5lib")
        time.sleep(1)
        race_no = 1
        for rec1 in soup.select('.table1 tbody'):
            shime = rec1.select('td')[1].text
            race_id = ("%s-%s-%02d" % (ymd, jcd, race_no))
            race_no += 1
            cur.execute(
                "SELECT * FROM race_list_koushiki WHERE race_id=%s", [race_id])
            if cur.fetchone() is None:
                print(race_id, shime)
                cur.execute(
                    "INSERT INTO race_list_koushiki(race_id,race_ymd,shime,sumi) VALUES(%s,%s,%s,%s)", (race_id, ymd, shime, '0'))
            con.commit()
    print('Furikae', ymd)
    if bet_flg and touhyou.zandaka() < 1000:
        touhyou.nyukin(10000)


def fill_result():
    t1 = (datetime.datetime.now() +
          datetime.timedelta(minutes=-30)).strftime('%H:%M')
    # t1 = '23:59'
    cur.execute(
        "SELECT race_id FROM race_list_koushiki WHERE sumi='1' AND shime<=%s ORDER BY serial_no", [t1])
    race_id_list = [rec for rec in cur]
    for [race_id] in race_id_list:
        [ymd, jcd, rno] = race_id.split('-')
        html = r.get(
            'https://www.boatrace.jp/owpc/pc/race/raceresult?rno=%d&jcd=%s&hd=%s' % (int(rno), jcd, ymd))
        soup = BeautifulSoup(html.text, "html5lib")
        time.sleep(1)
        if len(soup.select('.is-w495')) < 3:
            cur.execute(
                "UPDATE race_list_koushiki SET sumi='2', kumiban='', haitou=0 , fill_rslt_ts=now() WHERE race_id=%s", [race_id])
            print(race_id, '中止')
        else:
            tmpStrAry = [ban.text for ban in soup.select(
                '.is-w495')[2].select('tbody tr')[0].select('span')]
            haitou = int(tmpStrAry.pop()[1:].replace(',', '')) / 100
            kumiban = ''.join(tmpStrAry)
            cur.execute(
                "UPDATE race_list_koushiki SET sumi='2', kumiban=%s, haitou=%s , fill_rslt_ts=now() WHERE race_id=%s", (kumiban, haitou, race_id))
            cur.execute(
                "UPDATE odds_list_koushiki SET atari='1' WHERE race_id=%s AND kumiban=%s", (race_id, kumiban))
            con.commit()
            print(race_id, kumiban, haitou)


def koushiki_exec():
    t1 = (datetime.datetime.now() +
          datetime.timedelta(minutes=1)).strftime('%H:%M')
    # print(t1)
    # t1 = '23:59'
    # 本番のときはshime=t1にする
    cur.execute(
        "SELECT race_id,shime FROM race_list_koushiki WHERE sumi='0' AND shime<=%s", [t1])
    recs = [rec for rec in cur]
    # 3連単の2番目用のリスト
    renAry = [[idx1 + 1 for idx1 in range(6) if idx1 != idx0]
              for idx0 in range(6)]
    for [race_id, shime] in recs:
        print(race_id)
        [ymd, jcd, race_no] = race_id.split('-')
        race_no = int(race_no)
        html = r.get(
            'https://www.boatrace.jp/owpc/pc/race/odds3t?rno=%s&jcd=%s&hd=%s' % (race_no, jcd, ymd))
        soup = BeautifulSoup(html.text, "html5lib")
        time.sleep(1)

        # 直前の締め時刻を確認する（時間が変更されている可能性があるので直前ので確認する）
        cur_shime = soup.find('div', {'class': 'table1'}).select(
            'tbody tr')[1].select('td')[race_no - 1].text
        if cur_shime > t1:
            # 締め時刻が変更されていたらDBに反映してループをスキップ
            cur.execute(
                "UPDATE race_list_koushiki SET shime=%s, insert_ts=now() WHERE race_id=%s", (cur_shime, race_id))
            con.commit()
            continue

        # オッズの取得
        trs = soup.select('.is-p3-0 tr')
        odds1Map = {}
        for idx0 in range(len(trs)):
            ren1 = 1
            trDelta = 3 if idx0 % 4 == 0 else 2
            for idx1 in range(len(trs[idx0].select('td'))):
                if idx1 % trDelta == trDelta - 1:
                    # 組番用のリスト
                    kAry = [ren1, renAry[int(idx1 / trDelta) % 6][int(idx0 / 4)],
                            [iRec for iRec in range(1, 7) if (
                                ren1 != iRec and renAry[int(idx1 / trDelta) % 6][int(idx0 / 4)] != iRec)][idx0 % 4]]
                    kumiban = ('%d-%d-%d' % (kAry[0], kAry[1], kAry[2]))
                    odds1 = float(trs[idx0].select('td')[
                                  idx1].text.replace('欠場', '999'))
                    # print(race_id, trDelta, '-:', kumiban, odds1)
                    odds1Map[kumiban] = odds1
                    ren1 += 1
        odds1Ary = [{'kmbn': kmbn, 'odds1': odds1Map[kmbn]
                     if odds1Map[kmbn] != 0 else 999} for kmbn in odds1Map]
        odds1Ary = sorted(odds1Ary, key=lambda x: x['odds1'])
        for idx in range(len(odds1Ary)):
            cur.execute(
                "SELECT * FROM odds_list_koushiki WHERE race_id=%s AND kumiban=%s", (race_id, odds1Ary[idx]['kmbn']))
            if cur.fetchone() is None:
                # print(race_id, odds1Ary[idx]['kmbn'])
                cur.execute("INSERT INTO odds_list_koushiki(race_id,kumiban,odds1,ninki1,odds1e) VALUES(%s,%s,%s,%s,%s)", (
                    race_id, odds1Ary[idx]['kmbn'], min(odds1Ary[idx]['odds1'], 999), (idx + 1), odds1Ary[idx]['odds1']))
        cur.execute(
            "UPDATE race_list_koushiki SET sumi='1' , fill_odds_ts=now() WHERE race_id=%s", [race_id])
        con.commit()
        if bet_flg:
            rune_nnn(race_id)
            # rune3(race_id)


r16 = range(1, 7)
kumiban_all = ['%d-%d-%d' % (i0, i1, i2) for i0 in r16 for i1 in r16 if i1 !=
               i0 for i2 in r16 if i2 not in [i0, i1]]

KAI = {'d': 0, 'atari': 0}


def rune(race_id):
    N_ = len(kumiban_all)
    cur.execute(
        "SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s", [race_id])
    iDat = {kumiban: math.log(float(odds1), 999) for [kumiban, odds1] in cur}
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
    # threashold = 0.095
    isKau = []
    for idx1 in range(len(graphDat)):
        if graphDat[idx1] > threashold and idx1 < sakaime:
            continue
            # break
        elif graphDat[idx1] > threashold and idx1 >= sakaime:
            isKau.append(idx1)
    if graphDat.tolist().index(max(graphDat)) >= sakaime and len(isKau) > 0:
        # if len(isKau) > 0:
        # for idx1 in range(min(isKau), max(isKau) + 2):
        # isKau.append(max(isKau) + 1)
        for idx1 in isKau:
            cur.execute("SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s",
                        (race_id, math.pow(1000, (idx1 + 0) / float(rate)), math.pow(1000, (idx1 + 2) / float(rate))))
            odds1Recs = [odds1Rec for odds1Rec in cur]
            # for odds1Rec in odds1Recs:
            #     print(race_id, odds1Rec[0], odds1Rec[1])
            # print(race_id)
            cur.execute(
                "SELECT kumiban FROM race_list_atari_kumiban WHERE race_id=%s", [race_id])
            atariObj = cur.fetchone()
            if atariObj is not None:
                isAtari = [odds1Rec[0]
                           for odds1Rec in odds1Recs].index(atariObj[0]) if atariObj[0] in [odds1Rec[0] for odds1Rec in odds1Recs] else None
                if isAtari is not None:
                    KAI['atari'] += odds1Recs[int(isAtari)][1]
                    print('Atari=', race_id, len(odds1Recs),
                          odds1Recs[int(isAtari)][1])
                else:
                    print('Atari=', race_id, len(odds1Recs), 0)
                KAI['d'] = KAI['d'] + len(odds1Recs)
            else:
                print('Atari=', race_id, 'fumei', isKau, len(odds1Recs))
            for odds1Rec in odds1Recs:
                print('  ', odds1Rec[0], odds1Rec[1])
            cntMap[idx1] = cntMap[idx1] + 1
            cnt = cnt + len(odds1Recs)
        # print(race_id, len(graphDat), cnt, cntKachi, kauGoukei, kane, isKau)


# モデルをロード
s = shelve.open('model/20.db')
# s = shelve.open('model/m80_5700_10.db')
try:
    ld = s['map']
finally:
    s.close()


KAI = {'all': 0, 'race': 0, 'atari': 0, 'kau': 0, 'haitou': 0}


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
    if 0.1201 < graphDat[0] and graphDat[0] < 0.2:
        print(race_id, graphDat[0])
        kauCnt += 1
        kane = kane + cnt
        KAI['race'] += 1
        KAI['kau'] += cnt
        if atari is not None and atari > 0:
            cur.execute("SELECT odds1,kumiban,atari FROM odds_list_koushiki WHERE race_id=%s AND atari=1 AND odds1 BETWEEN %s AND %s", (
                race_id, kagen, jougen))
            [odds1, kumiban, atari] = cur.fetchone()
            print('  kekka', atari, kumiban,  odds1)
            haitou = haitou + odds1
            atariCnt += 1
            KAI['atari'] += 1
            KAI['haitou'] += odds1
        print('   ', kane, haitou, (haitou / kane)
              if kane != 0 else 0, kauCnt, atariCnt)
        cur.execute("SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN  %s AND %s ORDER BY ninki1", (
            race_id, kagen, jougen))
        kumibanList = []
        for [kumiban, odds1] in cur:
            kumibanList.append(kumiban)
            print('    BIT::', kumiban, odds1)
        if len(kumibanList) > 0:
            [ymd, jcd, rno] = race_id.split('-')
            touhyou.kaitsuke(ymd, jcd, rno, kumibanList)
            #       kaitsuke(ymd, jcd, rno, kumibanList):
        # try:
        #    cmd = "mplayer /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"
        #    # subprocess.call(cmd, shell=True)
        # finally:
        #    print('kacth')


def rune3(race_id):
    rate = 30
    s = shelve.open('./model/m80_5700_10.db')
    try:
        ld = s['map']
    finally:
        s.close()

    test_input_ary = [0] * len(kumiban_all)
    cur.execute(
        "SELECT race_id,kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s ORDER BY race_id,kumiban ", [race_id])
    for [race_id, kumiban, odds1] in cur:
        test_input_ary[kumiban_all.index(kumiban)] = math.log(
            float(odds1), 999) if float(odds1) != 0 else 0
    test_input_ary = sorted(test_input_ary) + test_input_ary

    graphDat = sigmoid(np.dot(
        np.tanh(np.dot(test_input_ary, ld['ww0']) + ld['bb0']), ld['ww1']) + ld['bb1'])
    [kane, cnt, cntKachi, kauGoukei] = [0, 0, 0, 0]
    sakaime = 15
    [l_r, h_r] = [1, 1]
    # threashold=0.9
    threashold = 0.5
    threashAry = [threashold if idx >=
                  15 else threashold for idx in range(rate)]
    threashAry[20] = 0.08
    for idx1 in range(len(graphDat)):
        if graphDat[idx1] > threashAry[idx1] and idx1 < sakaime:
            break
        elif graphDat[idx1] > threashAry[idx1] and idx1 >= sakaime:
            cur.execute("SELECT kumiban,odds1 FROM odds_list_koushiki WHERE race_id=%s AND odds1 BETWEEN %s AND %s ORDER BY ninki1",
                        (race_id, math.pow(1000, (idx1 - l_r) / float(rate)), math.pow(1000, (idx1 + h_r) / float(rate))))
            kumibanList = []
            for [kumiban, odds1] in cur:
                kumibanList.append(kumiban)
                print('    BIG::', kumiban, odds1)
            if len(kumibanList) > 0:
                print('    BIG::SUM=', len(kumibanList))
                kau = len(kumibanList)
                kauGoukei = kauGoukei + kau
                KAI['race'] += 1
                KAI['kau'] += cnt
                [ymd, jcd, rno] = race_id.split('-')
                touhyou.kaitsuke(ymd, jcd, rno, kumibanList)


# rune3('20171107-11-02')
main()
# cur.execute("SELECT race_id FROM race_list_koushiki ORDER BY race_id")
# for [race_id] in cur.fetchall():
#    rune(race_id)

# https://www.'boatrace.jp/owpc/pc/race/odds3t?rno=12&jcd=03&hd=20171029
# for year in range(2009, 2018):
#     for month in range(1, 13):
#         print(year, month)
#     # html = u.urlopen('http://www.orangebuoy.net/odds/?year=%d&mode=1' % year)
# print(KAI)
