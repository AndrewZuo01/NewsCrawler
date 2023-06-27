import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlsplit
import pymysql
import queue
import threading

#本程序一次爬取所有文章链接 然后分配给不同线程提取文章
#注意：爬取太快，可能会dns被拦下来

browser = webdriver.Firefox()
#创建数据库,记得修改用户名
db = pymysql.connect(host = "localhost", user="root", password="", database="news")
cursor = db.cursor()
#创建队列
q = queue.Queue()
categories = queue.Queue()
#放入队列
def putIntoQueue():
    #新闻中心全部链接与类别
        #注意："社会责任"是"产业新闻"子类，"微见石油"几乎全是微信公众号,"新闻专题"全是图片，2018年以前的文章都失效了
        # news_list = ["http://news.cnpc.com.cn/cnpcnews/","http://news.cnpc.com.cn/mtjj/index.shtml","http://news.cnpc.com.cn/cnpcnews/zr/index.shtml","http://news.cnpc.com.cn/shpj/index.shtml","http://news.cnpc.com.cn/hynews/index.shtml",
        # "http://news.cnpc.com.cn/zyjs/","http://news.cnpc.com.cn/zgsyb/","http://news.cnpc.com.cn/zongh/","http://news.cnpc.com.cn/gsld/","http://news.cnpc.com.cn/zhuanti/"]
        # news_category = ["产业新闻","媒体聚焦","社会责任","微见石油","行业新闻","中央精神","国资动态","集团要闻","公司领导活动","新闻专题"]
    #例子
    news_list = ["http://news.cnpc.com.cn/zhuanti/"]
    news_category = ["新闻专题"]
    for i in range(len(news_list)):
        browser.get(news_list[i])
        while(True):
            #间隔一秒否则容易网页卡顿
            time.sleep(1)
            elements = browser.find_element(By.CLASS_NAME, "nrstyle5")
            links = elements.find_elements(By.TAG_NAME, "a")
            #检查URL
            urls = []
            for link in links:
                url = link.get_attribute('href')
                parsed_url = urlparse(url)
                if(parsed_url.scheme and parsed_url.netloc):
                    urls.append(url)
            #放入队列
            q.put(urls)
            categories.put(news_category[i])
            # 如果没有下一页就退出
            nextbutton = browser.find_element(By.CLASS_NAME, "next")
            if(nextbutton.is_displayed()):

                nextbutton.click()
            else:
                break
#爬取文章内容
def fetchData(links,titleClass,titleTag,contentClass,category1,category2,browserK):
    
    for link in links:
        time.sleep(0.1)
        try: 
            browserK.get(link) 
        except:
            print("timeout error: " + link)
            continue
            
        pattern = re.compile(r'<[^>]+>',re.S)
        #检查页面是否是目标文章
        try:
            browserK.find_element(By.CLASS_NAME, titleClass)
        except:
            continue

        # 获取标题
        title_content = browserK.find_element(By.CLASS_NAME,titleClass)
        title_content = title_content.find_element(By.TAG_NAME, titleTag)
        title_content_result = pattern.sub('', title_content.get_attribute("outerHTML"))

        print(title_content_result)
        # 获取内容
        paragraph_content = browserK.find_element(By.CLASS_NAME, contentClass)
        texts = paragraph_content.find_elements(By.TAG_NAME, "p")
        final_result = ""
        for text in texts:
            final_result += pattern.sub('', text.get_attribute("outerHTML")+'\n')
        #放入MySQL
        #数据库结构CREATE TABLE crawler_news (id int auto_increment primary key,Title varchar(255), Content MEDIUMTEXT,Category1 varchar(100),Category2 varchar(100));
        sql = "INSERT INTO crawler_news (Title, Content,Category1,Category2) VALUES (%s, %s, %s,%s)"
        val = (title_content_result, final_result,category1,category2)
        cursor.execute(sql, val)
        db.commit()
    
# 一直爬取直到队列为空
def work(q,browserK):
    while True:
        if q.empty():
            return
        else:
            links = q.get()
            category = categories.get()
            #注意：中国石油文章两种格式，新闻中心跟信息公开的文章class不一样
            fetchData(links,"sj-title","h2","sj-main","新闻中心",category,browserK)
#先填满队列
putIntoQueue()
#注意：网速不够快但max_thread过多 网页会卡住
max_thread = 1
ts = []
browsers = []
#创建多个browser
for i in range(max_thread):
    browsers.append(webdriver.Firefox())
#开始并发运行
for i in range(max_thread):
    browserK = browsers[i]
    t =  threading.Thread(target=work, args=(q,browserK))
    t.start()
    ts.append(t)
for t in ts:
    t.join()
for browserK in browsers:
    browserK.quit()
browser.quit()




            
