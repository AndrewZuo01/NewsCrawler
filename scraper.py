import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlsplit
import pymysql

#本程序一次爬取一面文章（20+文章）然后自动点击下一页

#创建数据库
db = pymysql.connect(host = "localhost", user="root", password="", database="news")
cursor = db.cursor()
browser2 = webdriver.Firefox()
# 获取数据
#links 是所有链接，titleClass是标题的class标签，titleTag是标题的tag, contentClass是内容的class标签,category是分类
def fetchData(links,titleClass,titleTag,contentClass,category1,category2):
    for link in links:
        #检查URL
        url=link.get_attribute('href')
        parsed_url = urlparse(url)
        if(not (parsed_url.scheme and parsed_url.netloc)):
            continue
        try: 
            browser2.get(url) 
        except:
            print("timeout error: " + url)
            continue

        pattern = re.compile(r'<[^>]+>',re.S)
        #检查页面是否是目标文章
        try:
            browser2.find_element(By.CLASS_NAME, titleClass)
        except:
            continue

        # 获取标题
        title_content = browser2.find_element(By.CLASS_NAME,titleClass)
        title_content = title_content.find_element(By.TAG_NAME, titleTag)
        title_content_result = pattern.sub('', title_content.get_attribute("outerHTML"))

        print(title_content_result)
        # 获取内容
        paragraph_content = browser2.find_element(By.CLASS_NAME, contentClass)
        texts = paragraph_content.find_elements(By.TAG_NAME, "p")
        final_result = ""
        for text in texts:
            final_result += pattern.sub('', text.get_attribute("outerHTML")+'\n')
            
        # print(final_result)
        #放入MySQL
        #数据库结构CREATE TABLE crawler_news (id int auto_increment primary key,Title varchar(255), Content MEDIUMTEXT,Category1 varchar(100),Category2 varchar(100));
        sql = "INSERT INTO crawler_news (Title, Content,Category1,Category2) VALUES (%s, %s, %s,%s)"
        val = (title_content_result, final_result,category1,category2)
        cursor.execute(sql, val)
        db.commit()

    
# 加载网页
browser = webdriver.Firefox()
browser.implicitly_wait(10)
# 加载信息公开
browser.get('http://xxgk.cnpc.com.cn/')  

# 定位信息公开-最新动态
elements = browser.find_element(By.CLASS_NAME, "zxdt")
links = elements.find_elements(By.TAG_NAME, "a")
fetchData(links,"content-l1","h1","content-l2","信息公开","最新动态")
# 定位信息公开-招标信息
elements = browser.find_element(By.CLASS_NAME, "zxdt_List")
links = elements.find_elements(By.TAG_NAME, "a")
fetchData(links,"content-l1","h1","content-l2","信息公开","招标信息")

# #加载新闻-底部方格
# browser.get('http://news.cnpc.com.cn/')  
# elements = browser.find_element(By.ID, "newsmain")
# links = elements.find_elements(By.TAG_NAME, "a")
# fetchData(links,"sj-title","h2","sj-main",False)

#新闻中心全部链接与类别
    #注意："社会责任"是"产业新闻"子类，"微见石油"几乎全是微信公众号,"新闻专题"全是图片，2018年以前的文章都失效了
    # news_list = ["http://news.cnpc.com.cn/cnpcnews/","http://news.cnpc.com.cn/mtjj/index.shtml","http://news.cnpc.com.cn/cnpcnews/zr/index.shtml","http://news.cnpc.com.cn/shpj/index.shtml","http://news.cnpc.com.cn/hynews/index.shtml",
    # "http://news.cnpc.com.cn/zyjs/","http://news.cnpc.com.cn/zgsyb/","http://news.cnpc.com.cn/zongh/","http://news.cnpc.com.cn/gsld/","http://news.cnpc.com.cn/zhuanti/"]
    # news_category = ["产业新闻","媒体聚焦","社会责任","微见石油","行业新闻","中央精神","国资动态","集团要闻","公司领导活动","新闻专题"]
#爬取新闻中心
# news_list = ["http://news.cnpc.com.cn/cnpcnews/","http://news.cnpc.com.cn/mtjj/index.shtml","http://news.cnpc.com.cn/cnpcnews/zr/index.shtml","http://news.cnpc.com.cn/shpj/index.shtml","http://news.cnpc.com.cn/hynews/index.shtml",
    # "http://news.cnpc.com.cn/zyjs/","http://news.cnpc.com.cn/zgsyb/","http://news.cnpc.com.cn/zongh/","http://news.cnpc.com.cn/gsld/","http://news.cnpc.com.cn/zhuanti/"]
# news_category = ["产业新闻","媒体聚焦","社会责任","微见石油","行业新闻","中央精神","国资动态","集团要闻","公司领导活动","新闻专题"]
# for i in range(len(news_list)):
#     browser.get(news_list[i])
#     while(True):
#         elements = browser.find_element(By.CLASS_NAME, "nrstyle5")
#         links = elements.find_elements(By.TAG_NAME, "a")
#         fetchData(links,"sj-title","h2","sj-main",True,"新闻中心",news_category[i])
#         # 如果没有下一页就退出
#         nextbutton = browser.find_element(By.CLASS_NAME, "next")
#         if(nextbutton.is_displayed()):
#             nextbutton.click()
#         else:
#             break
# 退出
browser.quit()
browser2.quit()

