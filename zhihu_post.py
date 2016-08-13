# -*- coding:utf-8 -*-
import requests
from lxml import etree
import time
import os
import re
import BeautifulSoup
import json


logn_url = 'http://www.zhihu.com/#signin'
session = requests.session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
}
content = session.get(logn_url,headers=headers).content

def get_xsrf():
    selector = etree.HTML(content)
    xsrf = selector.xpath('//input[@name="_xsrf"]/@value')[0]
    return xsrf

def get_yanzhenma():
    t = str(int(time.time() * 1000))
    yanzhenma_url = 'http://www.zhihu.com/captcha.gif?r=' + t + '&type=login'
    r = session.get(yanzhenma_url,headers=headers)
    with open('kanwo.jpg','wb') as f:
        f.write(r.content)

    print '快去看看看看看 kanwo.jpg 这个文件,然后输入噢' + '     ' + str(os.path.abspath('kanwo.jpg'))
    yanzhenma = raw_input('输入验证码:')
    return yanzhenma

def login(secret, account):
    # 通过输入的用户名判断是否是手机号
    if re.match(r"^1\d{10}$", account):
        print("手机号登录 \n")
        post_url = 'http://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'phone_num': account,
        }
    else:
        print("邮箱登录 \n")
        post_url = 'http://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'email': account,
        }
    try:
        # 不需要验证码直接登录成功
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = login_page.text
        print(login_page.status)
        print(login_code)
    except:
        # 需要输入验证码后才能登录成功
        postdata["captcha"] = get_yanzhenma()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = eval(login_page.text)
        print login_page.url
        print(login_code['msg']).encode('utf-8')# 自测

def getdetial(num):
    # following_url = 'https://www.zhihu.com/people/GitSmile/followees'
    followees_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
        'Referer': 'https://www.zhihu.com/people/GitSmile/followees',
        'Origin': 'https://www.zhihu.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': '* / *'

    }
    #
    # myfollowees = session.get(following_url, headers=followees_headers)
    url = 'https://www.zhihu.com/node/ProfileFolloweesListV2'

    for i in range(num/20 + 1):
        data = {
            'method':'next',
            'params':'{"offset":%d,"order_by":"created","hash_id":"d456d227f1f03aeb2a2ce746c04ec830"}'% (i*20),
            '_xsrf': str(get_xsrf())
        }

        myfollowees = session.post(url,data=data,headers=followees_headers)
        guanzhu_text = myfollowees.text
        for json_load in json.loads(guanzhu_text)['msg']:
            xinxi = re.findall('class="zg-link-gray-normal">(.*?)<', json_load, re.S)
            print u'姓名:' + re.findall('<a title="(.*?)"',json_load,re.S)[0]
            print u'简介:' + re.findall('span class="bio">(.*?)<',json_load,re.S)[0]
            # print xinxi_s

            print u'关注:' + xinxi[0]
            print u'提问:' + xinxi[1]
            print u'赞同:' + xinxi[2]
            time.sleep(1)

def patu(url,nums):
    answer_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
        'Referer': 'https://www.zhihu.com/question/37709992',
        'Origin': 'https://www.zhihu.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': '* / *'

    }
    for num in nums:
        data = {
            'method': 'next',
            'params': '{"url_token":37709992,"pagesize":10,"offset":'+ '%d' % (num*10) +'}',
            '_xsrf': str(get_xsrf())
        }

        answers = session.post('https://www.zhihu.com/node/QuestionAnswerListV2',headers=answer_headers,data=data)
        dic = json.loads(answers.text)

        for i in dic['msg']:
            count = 0

            name = re.findall('ata-author-name=\\"(.*?)\\" ',i)
            os.mkdir(name[0])
            imgs = re.findall('data-actualsrc=\\"https:(.*?)"',i,re.S)
            for img in imgs:
                count += 1
                r = session.get('https:' + img, headers=headers)
                with open(os.path.join(name[0],'%d.jpg'% count), 'wb') as f:
                    f.write(r.content)

if __name__ == '__main__':
    login('835656yy!!','18757781776')
    # 查询几个自己的关注ID
    # getdetial(168)
    #要爬取几页的妹子图(1页10个ID)
    patu('https://www.zhihu.com/question/37709992',10)