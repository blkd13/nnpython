from bs4 import BeautifulSoup
import re
import datetime
import time
import requests as r
import random as rand
import math
import os.path
import json

HOST = 'https://www.boatrace.jp'
IB_HOST = 'https://ib.mbrace.or.jp'

# 残高＞入金だったら買い付けを行わないフラグ。
hoshuteki_flg = True


def nazo_rand():
    return str(math.floor(rand.random() * (1e12 - 1 + 1)) + 1 + int(time.time() * 1000))


def form2Dat(inpts):
    dat = {}
    for inp in inpts:
        dat[inp['name']] = inp['value']
    return dat


def login():
    sess = r.Session()
    html = sess.get(HOST + '/owpc/pc/login?authAfterUrl=/')
    time.sleep(1)
    soup = BeautifulSoup(html.text, 'html.parser')

    # 不要タグを削除
    soup.find('input', {'name': 'chkRakuraku'}).extract()

    # Formを抽出
    form = soup.find('form', {'name': 'TENT010_TENTPC010PRForm'})

    # config.jsonからアカウント情報を取得して入力
    conf_obj = json.load(open('./config.json', 'r'))
    for kwd in ['in_KanyusyaNo', 'in_AnsyoNo', 'in_PassWord']:
        form.find('input', {'name': kwd})['value'] = conf_obj[kwd]

    # 不足タグを追加
    inpts = form.select('input')
    inpts.append(soup.new_tag('input'))
    inpts[-1]['name'] = 'com.nec.jp.orteusActionMethod.login'
    inpts[-1]['value'] = 'controlLogin'
    inpts.append(soup.new_tag('input'))
    inpts[-1]['name'] = 'login'
    inpts[-1]['value'] = 'Submit'
    dat = form2Dat(inpts)
    # ログイン
    html = sess.post(HOST + form['action'], data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    # print(soup)
    time.sleep(1)
    return sess


def logout(sess):
    sess.get('https://www.boatrace.jp/owpc/logout')
    time.sleep(1)


def zandaka():
    sess = login()
    conf_obj = json.load(open('./config.json', 'r'))

    next_url = '/owpc/VoteConfirm.jsp?param=H0JS00000stContens&kbn=1&voteActionUrl=/owpc/pc/site/index.html'

    # 投票ボタンを押した後に確認画面が出てくる
    html = sess.get(HOST + next_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)
    next_url = next_url.replace('/owpc/VoteConfirm.jsp',
                                '/owpc/VoteBridgeNew.jsp')

    # 確認ボタンを押して投票ページのトップページを開く
    html = sess.get(HOST + next_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    # 自動リダイレクト
    form = soup.find('form', {'name': 'voteform'})
    dat = form2Dat(form.select('input'))
    html = sess.post(form['action'], data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    token = soup.select('#toplogoForm [name=token]')[0]['value']
    _csrf = soup.select('#toplogoForm [name=_csrf]')[0]['value']
    zandaka = int(soup.select('#currentBetLimitAmount')
                  [0].text.replace(',', ''))

    logout(sess)
    return zandaka


def nyukin_list():
    sess = login()

    next_url = '/owpc/VoteConfirm.jsp?param=H0JS00000stContens&kbn=1&voteActionUrl=/owpc/pc/site/index.html'

    # 投票ボタンを押した後に確認画面が出てくる
    html = sess.get(HOST + next_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)
    next_url = next_url.replace('/owpc/VoteConfirm.jsp',
                                '/owpc/VoteBridgeNew.jsp')

    # 確認ボタンを押して投票ページのトップページを開く
    html = sess.get(HOST + next_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    # 自動リダイレクト
    form = soup.find('form', {'name': 'voteform'})
    dat = form2Dat(form.select('input'))
    html = sess.post(form['action'], data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    token = soup.select('#toplogoForm [name=token]')[0]['value']
    _csrf = soup.select('#toplogoForm [name=_csrf]')[0]['value']
    zandaka = int(soup.select('#currentBetLimitAmount')
                  [0].text.replace(',', ''))
    center_no = soup.find('meta', {'name': 'centerNo'})['content']

    # 入金額一覧
    rand = nazo_rand()
    next_url = 'https://ib.mbrace.or.jp/tohyo-ap-pctohyo-web/service/ref/rcptlist/charge?cid=%s&r=%s' % (
        center_no, rand)
    dat = {
        'refType': 2,
        'dispPageNo': 1,
        'screenFrom': 'B610',
        'token': token,
        '_csrf': _csrf
    }
    html = sess.post(next_url, data=dat)
    if html.status_code == 200:
        json_obj = json.loads(html.text)
        time.sleep(1)
        sum_amount = 0
        for rec in json_obj['rcptInfoList']:
            sum_amount += rec['amount']

    print(zandaka)
    if zandaka > sum_amount:
        print(sum_amount)
        print('end')

    logout(sess)


def nyukin(kingaku):
    sess = login()
    conf_obj = json.load(open('./config.json', 'r'))

    next_url = '/owpc/VoteConfirm.jsp?param=H0JS00000stContens&kbn=1&voteActionUrl=/owpc/pc/site/index.html'

    # 投票ボタンを押した後に確認画面が出てくる
    html = sess.get(HOST + next_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)
    next_url = next_url.replace('/owpc/VoteConfirm.jsp',
                                '/owpc/VoteBridgeNew.jsp')

    # 確認ボタンを押して投票ページのトップページを開く
    html = sess.get(HOST + next_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    # 自動リダイレクト
    form = soup.find('form', {'name': 'voteform'})
    dat = form2Dat(form.select('input'))
    html = sess.post(form['action'], data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    token = soup.select('#toplogoForm [name=token]')[0]['value']
    _csrf = soup.select('#toplogoForm [name=_csrf]')[0]['value']
    zandaka = int(soup.select('#currentBetLimitAmount')
                  [0].text.replace(',', ''))
    center_no = soup.find('meta', {'name': 'centerNo'})['content']
    print(zandaka)

    # 入金額取得？
    rand = nazo_rand()
    next_url = 'https://ib.mbrace.or.jp/tohyo-ap-pctohyo-web/service/amo/charge?cid=%s&r=%s' % (
        center_no, rand)
    dat = {
        'screenFrom': 'B610',
        'token': token,
        '_csrf': _csrf
    }
    html = sess.post(next_url, data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    # 入金処理
    rand = nazo_rand()
    next_url = 'https://ib.mbrace.or.jp/tohyo-ap-pctohyo-web/service/amo/chargecomp?cid=%s&r=%s' % (
        center_no, rand)
    dat = {
        'chargeInstructAmt': int(kingaku / 1000),
        'betPassword': conf_obj['betPassword'],
        'screenFrom': 'B634',
        'token': token,
        '_csrf': _csrf
    }
    html = sess.post(next_url, data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    print(soup)
    time.sleep(1)

    logout(sess)


def kaitsuke(ymd, jcd, rno, kumiban_list):
    sess = login()
    conf_obj = json.load(open('./config.json', 'r'))
    kakeme = 1

    # オッズ表のページから投票ボタンを押す
    html = sess.get(
        HOST + ('/owpc/pc/race/odds3t?rno=%d&jcd=%s&hd=%s' % (int(rno), jcd, ymd)))
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)
    # 投票ボタンのurlを取得
    a_tag = soup.find('a', {'id': 'mainVoteTag'})
    next_url = re.sub(r'\'.*', '', re.sub(r'^[^\']+\'', '', a_tag['onclick']))
    # 直前の締め時刻を確認しておく。締めを過ぎていたら何もしないで終了
    cur_shime = soup.find('div', {'class': 'table1'}).select(
        'tbody tr')[1].select('td')[int(rno) - 1].text
    now_time = datetime.datetime.now().strftime('%H:%M')
    if now_time > cur_shime:
        print('Time Over now=%s shime=%s' % (now_time, cur_shime))
        return

    # 投票ボタンを押した後に確認画面が出てくる
    html = sess.get(HOST + next_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)
    next_url = next_url.replace('/owpc/VoteConfirm.jsp',
                                '/owpc/VoteBridgeNew.jsp')

    # 確認ボタンを押して投票ページのトップページを開く
    html = sess.get(HOST + next_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    # 自動リダイレクト
    form = soup.find('form', {'name': 'voteform'})
    dat = form2Dat(form.select('input'))
    print(form['action'])
    html = sess.post(form['action'], data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)

    # 入金額＜残高だったら勝っているので買い付けしないでやめる
    token = soup.select('#toplogoForm [name=token]')[0]['value']
    _csrf = soup.select('#toplogoForm [name=_csrf]')[0]['value']
    zandaka = int(soup.select('#currentBetLimitAmount')
                  [0].text.replace(',', ''))
    center_no = soup.find('meta', {'name': 'centerNo'})['content']

    rand = nazo_rand()
    next_url = 'https://ib.mbrace.or.jp/tohyo-ap-pctohyo-web/service/ref/rcptlist/charge?cid=%s&r=%s' % (
        center_no, rand)
    dat = {
        'refType': 2,
        'dispPageNo': 1,
        'screenFrom': 'B610',
        'token': token,
        '_csrf': _csrf
    }
    html = sess.post(next_url, data=dat)
    time.sleep(1)
    if html.status_code == 200:
        json_obj = json.loads(html.text)
        time.sleep(1)
        sum_amount = 0
        for rec in json_obj['rcptInfoList']:
            sum_amount += rec['amount']
        if hoshuteki_flg and zandaka > sum_amount:
            print('won ', sum_amount, zandaka)
            return

    # 投票
    form = soup.find('form', {'id': 'todayForm'})
    form.find('input', {'name': 'betWay'})['value'] = '5'
    form.find('input', {'name': 'jyoCode'})['value'] = jcd
    form.find('input', {'name': 'multiJyo'})['value'] = False
    form.find('input', {'name': 'multiRace'})['value'] = False
    form.find('input', {'name': 'lastSelectionKachishiki'})['value'] = '6'
    form.find('input', {'name': 'lastSelectionBetWay'})['value'] = '1'
    form.find('input', {'name': 'lastSelectionRacer'})['value'] = '1'
    form.find('input', {'name': 'operationKbn'})['value'] = ''
    form.find('input', {'name': 'screenFrom'})['value'] = 'C620'
    inpts = form.select('input')
    inpts.append(soup.new_tag('input'))
    inpts[-1]['name'] = 'selectionJyoList'
    inpts[-1]['value'] = [jcd]
    inpts.append(soup.new_tag('input'))
    inpts[-1]['name'] = 'selectionRaceNoList'
    inpts[-1]['value'] = [rno]

    def bet(idx, jcd, rno, kumiban, kakeme):
        ret = {}
        dat = {
            'betJyoCode':	jcd,
            'raceNo':	rno,
            'kachishiki':	'6',
            'betWay':	'1',
            'kumiban': '',
            'numberOfSheets': '',
            'unfoldedFlg':	'1',
            'unfoldedKumiban':	kumiban,
            'unfoldedNum':	kakeme}
        for key in dat:
            # %5B%d%5D
            ret['betContentsList[%d].betList[0].%s' % (idx, key)] = dat[key]
        return ret

    for idx in range(len(kumiban_list)):
        bet_obj = bet(idx, jcd, rno, kumiban_list[idx], kakeme)
        for key in bet_obj:
            inpts.append(soup.new_tag('input'))
            inpts[-1]['name'] = key
            inpts[-1]['value'] = bet_obj[key]
            # print(key, betObj[key])

    dat = form2Dat(inpts)
    print(form['action'])
    html = sess.post(IB_HOST + form['action'], data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    time.sleep(1)
    # print(soup)
    form = soup.find('form', {'id': 'betconfForm'})
    form.find('input', {'name': 'dummyA'})['value'] = ''
    form.find('input', {'name': 'dummyB'})['value'] = ''
    form.find('input', {'name': 'betAmount'})[
        'value'] = (kakeme * 100 * len(kumiban_list))
    form.find('input', {'name': 'betPassword'})[
        'value'] = conf_obj['betPassword']
    form.find('input', {'name': 'operationKbn'})['value'] = ''
    inpts = form.select('input')
    fill_param = {'screenFrom': 'D628',
                  'betWay': '5',
                  'jyoCode': jcd,
                  'multiJyo': 'false',
                  'selectionJyoList': jcd,
                  'multiRace': 'false',
                  'selectionRaceNoList': rno,
                  'lastSelectionKachishiki': '6',
                  'lastSelectionBetWay': '1',
                  'lastSelectionRacer': '1'}
    for key in fill_param:
        inpts.append(soup.new_tag('input'))
        inpts[-1]['name'] = key
        inpts[-1]['value'] = fill_param[key]

    dat = form2Dat(inpts)
    # for key in dat:
    #    print(key, dat[key])

    # ここだけはformの設定値が使えないので直接指定
    next_url = '/tohyo-ap-pctohyo-web/service/bet/betcomp?'
    # centerNoをmetaから取得
    next_url = next_url + 'cid=' + \
        soup.find('meta', {'name': 'centerNo'})['content']
    # 謎の乱数をつける
    next_url = next_url + '&r=' + nazo_rand()
    print(next_url)
    # 買い付け確定
    html = sess.post(IB_HOST + next_url, data=dat)
    soup = BeautifulSoup(html.text, 'html.parser')
    # print(soup)
    logout(sess)

# kaitsuke('20171105', '07', '12', ['1-3-2', '3-1-2'])
