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
        cursor.execute('''CREATE TABLE IF NOT EXISTS db_data (
                          id varchar(8),
                          uid varchar(16),
                          name text,
                          reason text,
                          time text,
                          evidence text,
                          PRIMARY KEY(id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;''')
    except:
        print('建表发生异常')

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
                id = tempDict['id']
                uid = tempDict['uid']
                name = tempDict['uname']
                reason = tempDict['punishTitle']
                if tempDict['blockedDays'] == 0:
                    time = '永久'
                else:
                    time = tempDict['blockedDays']
                evidence = tempDict['originContentModify']
                sql = "insert into db_data(id,uid,name,reason,time,evidence) values ('{}','{}','{}','{}','{}','{}')".format(id,uid,name,reason,time,evidence)
                cursor.execute(sql)
                conn.commit()
            except:
                pass
        print('当前爬取页数：{}'.format(page))
        page += 1

def closeDB():
    global conn,cursor
    cursor.close()
    conn.close()

if __name__=="__main__":
    url = 'http://www.bilibili.com/blackroom/web/blocked_info?originType=0&pageNo='
    print('************bilibili小黑屋爬虫************')
    print('注意事项：')
    print('1.本程序采用MySQL数据库，请确认数据库已经正确安装')
    print('2.请确认已修改程序开头的数据库连接信息，包括数据库、用户名和密码')
    print('****************************************')
    input('确认无误后，按任意键开始爬取')
    getInfo(url)
    closeDB()
