import requests,re,traceback,json,pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='small_black_room',charset="utf8")
cursor = conn.cursor()

def getHTMLText(url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        r = requests.get(url,timeout=30,headers = headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ''

def getInfo(url):
    global conn,cursor
    page = 1
    try:
        cursor.execute("CREATE TABLE db_data(用户名 Text,封禁原因 Text,封禁时间 Text,封禁证据 Text)")
    except:
        print('新建表失败,可能表已经存在')

    while True:
        html = getHTMLText(url + str(page))
        dicts = json.loads(html)
        if(len(dicts['data']) == 0):
            print('已获取所有小黑屋信息,程序已结束')
            break;
        data = dicts['data']
        for i in data:
            i = ((str(i).replace("'",'"')).replace('True','true')).replace('False','false')
            re_h=re.compile('</?\w+[^>]*>')
            i=re_h.sub('',i)
            try:
                tempDict = json.loads(i)
                name = tempDict['uname']
                reason = tempDict['punishTitle']
                if tempDict['blockedDays'] == 0:
                    time = '永久'
                else:
                    time = tempDict['blockedDays']
                evidence = tempDict['originContentModify']
                sql = "insert into db_data(用户名,封禁原因,封禁时间,封禁证据) values ('{}','{}','{}','{}')".format(name,reason,time,evidence)
                cursor.execute(sql)
                conn.commit()
            except:
                pass
        print('当前存储页数：{}'.format(page))
        page += 1

def closeDB():
    global conn,cursor
    cursor.close()
    conn.close()

def main():
    url = 'http://www.bilibili.com/blackroom/web/blocked_info?originType=0&pageNo='
    print('欢迎使用bilibili小黑屋爬虫')
    getInfo(url)
    closeDB()
    
main()
