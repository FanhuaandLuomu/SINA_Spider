#coding:utf-8
# 登录新浪微博
import os
import re
import time
import random
import cchardet
import requests
from lxml import etree

# 登录
def login(url,username,password):
	headers = {
		"Origin": "https://passport.weibo.cn", 
		"Content-Length": "169", 
		"Accept-Language": "zh-CN,zh;q=0.8", 
		"Accept-Encoding": "gzip, deflate", 
		"Host": "passport.weibo.cn", 
		"Accept": "*/*", 
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36", 
		"Connection": "keep-alive", 
		"Referer": "https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt=", 
		"Content-Type": "application/x-www-form-urlencoded"
	}
	data = {
		"username": username, 
		"qq": "", 
		"savestate": "1", 
		"client_id": "", 
		"wentry": "", 
		"code": "", 
		"ec": "0", 
		"r": "http://weibo.cn/", 
		"loginfrom": "", 
		"hfp": "", 
		"pagerefer": "", 
		"entry": "mweibo", 
		"password": password, 
		"mainpageflag": "1", 
		"hff": ""
	}

	s=requests.Session()
	res=s.post(url,headers=headers,data=data)
	print 'login state:',res
	return s

# 获取粉丝列表 和 关注者 列表
def get_fans(s,url):
	res=s.get(url)
	html=res.content
	page=etree.HTML(html)

	if 'fans' in url:
		my_xpath="//div[@class='c']/table/tr/td[2]/a[1]"
	if 'follow' in url:
		my_xpath="//table/tr/td[2]/a[1]"

	fans_table=page.xpath(my_xpath)
	# print len(fans_table)

	for fan_item in fans_table:
		print fan_item.xpath('text()')[0].encode('utf-8')

	pageNum=page.xpath('//*[@id="pagelist"]/form/div/text()[2]')[0].encode('utf-8')
	# print pageNum
	pageNum=int(re.findall('/(.*?)页',pageNum)[0])
	print pageNum

	for i in range(1,int(pageNum)):
		print 'page:%d' %(i+1)
		res=s.get(url+'?page=%d' %(i+1))
		html=res.content
		page=etree.HTML(html)
		fans_table=page.xpath(my_xpath)
		# print len(fans_table)

		for fan_item in fans_table:
			print fan_item.xpath('text()')[0].encode('utf-8','ignore')

def get_hot_pageNum(page):
	try:
		count=page.xpath("//div[@class='c']/span[@class='cmt']/text()")[0].encode('utf-8')
		count=int(re.findall('共(.*?)条',count)[0])

		pageNum=page.xpath('//*[@id="pagelist"]/form/div/text()[2]')[0].encode('utf-8')
		pageNum=int(re.findall('/(.*?)页',pageNum)[0])
		return pageNum,count
	except Exception,e:
		return 0,0

def crawl_hot_content_by_page(keyword,starttime,endtime,nick,page):
	div_list=page.xpath("//div[@class='c' and @id]")
	print 'len(div_list):',len(div_list)
	f=open('data/%s_%s_%s_%s.txt' %(keyword,nick,starttime,endtime),'a')
	
	for item in div_list:
		print item.xpath('string(.)').encode('GB18030')
		f.write(item.xpath('string(.)').encode('GB18030')+'\n')
	f.flush()

def search_hot(s,keyword,endtime,nick='',starttime='',sort='time'):
	url='https://weibo.cn/search/'
	data = {
		"sort": sort, 
		"smblog": u"搜索", 
		"keyword": keyword, 
		"advancedfilter": "1", 
		"nick": nick, 
		"starttime": starttime, 
		"endtime": endtime
	}
	res=s.post(url,data=data)
	time.sleep(random.random())

	html=res.content
	# print cchardet.detect(html)
	page=etree.HTML(html)

	pageNum,count=get_hot_pageNum(page)
	print '%s has page:%d [%d]' %(keyword,pageNum,count)

	# f=open('data/%s_%s_%s_%s.txt' %(keyword,nick,starttime,endtime),'a')
	# f.write('%s has page:%d [%d]\n' %(keyword,pageNum,count))
	# f.flush()

	crawl_hot_content_by_page(keyword,starttime,endtime,nick,page)

	for i in range(2,pageNum+1):
		url='https://weibo.cn/search/mblog?hideSearchFrame=&keyword=%s\
			&advancedfilter=1&nick=%s&starttime=%s&endtime=%s&sort=%s&page=%s' \
			%(keyword,nick,starttime,endtime,sort,i)
		res=s.get(url)
		time.sleep(random.random())
		html=res.content
		page=etree.HTML(html)

		crawl_hot_content_by_page(keyword,starttime,endtime,nick,page)

		print '='*30
		print 'keyword:%s starttime:%s endtime:%s cpage:%s' \
				%(keyword,starttime,endtime,i)
		print '='*30


def main():
	# 保存数据
	if not os.path.exists('data'):
		os.mkdir('data')

	login_url='https://passport.weibo.cn/sso/login'
	username='13771902647'
	password='yinhao'

	s=login(login_url,username,password)

	# fans_url='https://weibo.cn/5822306215/fans'
	# fans_url='https://weibo.cn/5822306215/follow'
	# get_fans(s,fans_url)

	keyword=u'selu'
	# nick=u'Lim王'
	nick=u''
	starttime='20170608'
	endtime='20170612'
	# 只能爬取相关内容最新100页  （100*10条）
	search_hot(s,keyword=keyword,nick=nick,starttime=starttime,endtime=endtime)

	
if __name__ == '__main__':
	main()