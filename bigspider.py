# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 20:16:17 2016

@discription 该页面用来爬取所有页面venue的信息，目标网站为lonely planet
@author: River He
"""
import urllist
import urllib2
import time
import os
import re
import mysql
import sys
from bs4 import BeautifulSoup

class Spider:
    
    #初始化
    def __init__(self):
        self.page_num = 1
        self.total_num = None
        self.path = os.getcwd()
        self.mysql = mysql.Mysql()
        self.urllist = urllist.Urllist().urllist
        
    #获取当前时间
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))
    
    #获取当前时间
    def getCurrentDate(self):
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))
    
    #通过网页的页码数来构建网页的URL
    def getPageURLByNum(self, page_num, category):
        page_url = category + "?page=" + str(page_num)
        return page_url
    
    
    #通过传入网页页码来获取该页面的HTML
    def getPageByNum(self, page_num, category):
        header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'}
        timeout = 20
        request = urllib2.Request(self.getPageURLByNum(page_num, category),None,header)
        try:
            response = urllib2.urlopen(request,None,timeout)
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print self.getCurrentTime(),"获取list页面失败,错误代号", e.code
                self.getPageByNum(page_num, category)
            if hasattr(e, "reason"):
                print self.getCurrentTime(),"获取list页面失败,原因", e.reason
                self.getPageByNum(page_num, category)
        else:
            page =  response.read().decode("utf-8")
            return page
    
    #获取所有的页码数
    def getTotalPageNum(self, category):
        print self.getCurrentTime(),"正在获取目录页面个数,请稍候"
        url = category
        header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'}
        timeout = 20
        request = urllib2.Request(url,None,header)
        try:
            response = urllib2.urlopen(request,None,timeout)
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print self.getCurrentTime(),"获取目录页面个数失败,错误代号", e.code
                self.getTotalPageNum(category)
            if hasattr(e, "reason"):
                print self.getCurrentTime(),"获取目录页面个数失败,原因", e.reason
                self.getTotalPageNum(category)
        else:
            content = response.read().decode("utf-8")
            soup = BeautifulSoup(content)
            total_num = soup.find_all(class_="js-page-link")
            if total_num==[]:
                print "获取页面成功，页面个数为： 1"
                return "1"
            else:
                total_num = total_num[-1].get('href').split('=')[-1]
                print "获取成功，页面个数为：%s" % total_num
                return total_num
    

    #获取当前页面venue的url,返回venue的URL列表
    def getVenueURLs(self,page_num, category):
        #获取当前页面的HTML
        page = self.getPageByNum(page_num, category)
        soup = BeautifulSoup(page)
        #分析该页面
        venues = soup.find_all(class_="card__mask")
        return ["http://www.lonelyplanet.com" + venue.a["href"] for venue in venues]

    #通过该页面的URL来获取当前页面源码
    def getPageByURL(self, url):
        header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'}
        timeout = 20
        request = urllib2.Request(url,None,header)        
        try: 
            response = urllib2.urlopen(request,None,timeout)
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print self.getCurrentTime(), "获取Venue页面失败，错误代号", e.code
                return None
            if hasattr(e, "reason"):
                print self.getCurrentTime(), "获取Venue页面失败，原因", e.reason
                return None
        else:
            return response.read().decode("utf-8")
    #传入Venue页面源码，解析
    def getVenueInfo(self, venue_page):
        #初始化venue的所有信息，都为字符串类型
        venue_name = ""
        address = ""
        phone = ""
        area = ""
        metro = ""
        hours = ""
        cards = ""
        web = ""
        happy_hour = ""
        price = ""
        description = ""
        latitude = ""
        longitude = ""
        #初始化tags信息
        tags = []
        #使用bs解析网页
        soup = BeautifulSoup(venue_page)
        #venue名称
        venue_name = re.sub('\n', '', soup.find(class_="copy--h1").get_text())
        venue_name = re.sub('\'', '\'\'', venue_name)
        #获取图片链接
        img_links = []
        img_divs = soup.find_all(class_="slider__slide") or soup.find_all(id="js-tab-photos")
        if img_divs != None and img_divs != []:
            img_links = ["http" + (img_div.img.get('src') or img_div.img.get('data-src')).split('http')[-1] for img_div in img_divs]
        #Tag名称
        tags = [tag.strip() for tag in 
                soup.find(class_="card--page__breadcrumb")
                .get_text().split('/')]
        #编辑描述
        description = re.sub('\n', '', soup.find(class_="ttd__section ttd__section--description").get_text())
        description = re.sub('\'', '\'\'', description)
        #经纬度
        latitude_c = soup.find(class_="poi-map__container mv--inline js-poi-map-container")
        if latitude_c != None:
            latitude = latitude_c.get('data-latitude')
        longitude_c = soup.find(class_="poi-map__container mv--inline js-poi-map-container")
        if longitude_c != None:
            longitude = longitude_c.get('data-longitude')
        #其他信息获取
        info_list = soup.find(class_="grid-wrapper--20")
        keys = [re.sub('\n', '', dt.get_text()).strip() for dt in info_list.find_all("dt")]
        values = [re.sub('\n', '',dd.get_text()) for dd in info_list.find_all("dd")]
        for i in range(len(keys)):
            if keys[i]=="Location":
                area = values[i]
            elif keys[i]=="Address":
                address = values[i]
            elif keys[i]=="Telephone":
                phone = values[i]
            elif keys[i]=="Getting there":
                metro = re.sub('\'', '\'\'', values[i].split(':')[-1])
            elif keys[i]=="Prices":
                price = values[i]
            elif keys[i]=="Opening hours":
                hours = values[i]
            elif keys[i]=="More information":
                web = values[i]
            else:
                break
        return [venue_name, address, phone, area, metro, hours, cards, web, happy_hour, price, description, tags, img_links, latitude, longitude]
    
    #插入venue各项信息到数据库
    def insertVenue(self, venue_info):
        #定义一个字典存取venue，用来插入到数据库中
        venue_dict = {
                "venue_name": venue_info[0],
                "address": venue_info[1],
                "phone": venue_info[2],
                "area": venue_info[3],
                "metro": venue_info[4],
                "hours": venue_info[5],
                "cards": venue_info[6],
                "web": venue_info[7],
                "happy_hour": venue_info[8],
                "price": venue_info[9],
                "description": venue_info[10],
                "latitude": venue_info[13],
                "longitude": venue_info[14]
        }
        #获得插入venue的自增ID
        vinsert_id = self.mysql.insertData("venue", venue_dict)
        print self.getCurrentTime(), "保存到数据库，此venue的ID为", vinsert_id
            
        if venue_info[11] != None and len(venue_info[11]) > 0:
            for i in range(len(venue_info[11])):
                venue_tag_dict = {
                    "venue_name": venue_info[0],
                    "tag_name": venue_info[11][i]
                }
                vtinsert_id = self.mysql.insertData("venue_tag", venue_tag_dict)
                print self.getCurrentTime(), "保存到数据库，此venue_tag的ID为", vtinsert_id
                
            for j in range(len(venue_info[11])):
                tag_dict = {
                    "tag_name": venue_info[11][j]
                }
                #获得插入tag的id
                tinsert_id = self.mysql.insertData("tags", tag_dict)
                print self.getCurrentTime(), "保存到数据库，此tag的ID为", tinsert_id    
        img_links = venue_info[12]
        if img_links != None and len(img_links) != 0 :
            img_path = os.path.join(self.path, u'lonelyplanet\\' + re.sub('/', '_', venue_info[0]))
            if not os.path.isdir(img_path):
                os.mkdir(img_path)
            for link in img_links:
                try:
                    img_content = urllib2.urlopen(link).read()
                except urllib2.URLError, e:
                    if hasattr(e, "code"):
                        print self.getCurrentTime(),"获取图片信息失败,错误代号", e.code
                    if hasattr(e, "reason"):
                        print self.getCurrentTime(),"获取图片信息失败,原因", e.reason
                    continue
                else:
                    with open(img_path + '\\' + link[-11:], 'wb') as code:
                        code.write(img_content)              
    #获取所有的venue
    def getVenues(self, page_num, category):
    	venue_urls = self.getVenueURLs(page_num, category)
    	for venue_url in venue_urls:
    		print self.getCurrentTime(),"正在抓取venue，地址为", venue_url 
    		page = self.getPageByURL(venue_url)
        	venue_info = self.getVenueInfo(page)
        	try:
        		self.insertVenue(venue_info)
    		except Exception, e:
    			if hasattr(e, "reason"):
    				print self.getCurrentTime(),"抓取venue失败，原因", e.reason

    def main(self):
    	#创建文件夹
        new_path = os.path.join(self.path, u'lonelyplanet')
        if not os.path.isdir(new_path):  
            os.mkdir(new_path)  
        f_handler=open('out.log', 'w') 
        sys.stdout=f_handler
        if not os.path.exists('page.txt'):
            f = open('page.txt', 'w')
            f.write('0|1')
            f.close()
        pagereader = open('page.txt', 'r')
        content = pagereader.readline()
        website = int(content.strip().split('|')[0])
        page = int(content.strip().split('|')[1])
        print "主页", self.urllist[website], "页面", str(page)
        start_site = website
        start_page = page
        pagereader.close()     
        print self.getCurrentTime(),"开始页码",start_page
        print self.getCurrentTime(),"爬虫正在启动,开始爬取lonelyplanet"
        see_total_list = len(self.urllist)
        for url_x in range(start_site, see_total_list):
            category = self.urllist[url_x]
            self.total_num = self.getTotalPageNum(category)
            print self.getCurrentTime(),"获取到" + category + "目录页面个数",self.total_num,"个"
            #爬取单个网站
            see_total_num = int(self.total_num)
            for x in range(start_page, see_total_num+1):
                print self.getCurrentTime(),"正在抓取第",x,"个页面"
                try:
                    self.getVenues(x, category)
                except urllib2.URLError, e:
                    if hasattr(e, "reason"):
                        print self.getCurrentTime(),"某总页面内抓取或提取失败,错误原因", e.reason
                except Exception,e:
                    print self.getCurrentTime(),"某总页面内抓取或提取失败,错误原因:",e
                if x < see_total_num:
                    f=open('page.txt','w')
                    f.write(str(url_x) + '|' + str(x))
                    print self.getCurrentTime(),"写入新页码",category,x
                    f.close()
                else:
                    print self.getCurrentTime(),"最后一页",category,x
                    f = open('page.txt', 'w')
                    f.write(str(url_x) + '|' + str('1'))
                    f.close()
            if url_x >= see_total_list-1:
                print self.getCurrentDate(), self.getCurrentTime(),"爬取结束"
                return 0
spider = Spider()
spider.main()
    