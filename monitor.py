#coding:utf-8
# 登录新浪微博  监控
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

def get_nick(s,sid):
	url='https://weibo.cn/u/%s' %(sid)
	res=s.get(url)
	html=res.content
	page=etree.HTML(html)

	nick=page.xpath("//div[@class='ut']")
	print len(nick)
	nick=nick[0].xpath('string(.)').encode('GB18030').strip().split()[0]
	# print nick
	return nick

# 获取历史最新的微博
def get_the_first_content(s,sid,stype):
	url='https://weibo.cn/u/%s?filter=%s' %(sid,stype)
	res=s.get(url)
	time.sleep(1)
	html=res.content
	page=etree.HTML(html)
	latest=page.xpath("//div[@class='c' and @id]")[0]
	latest_content=latest.xpath('string(.)').encode('GB18030').strip()
	latest_id=latest.attrib['id']
	return latest_content,latest_id

def monitor_person(s,sid,stype,stop_id):

	sid_list=[]
	content_list=[]
	i=0
	while 1:
		i+=1
		url='https://weibo.cn/u/%s?filter=%s&page=%d' %(sid,stype,i)
		res=s.get(url)
		time.sleep(1)
		html=res.content
		page=etree.HTML(html)
		items=page.xpath("//div[@class='c' and @id]")
		for item in items:
			sid=item.attrib['id']
			# print sid
			content=item.xpath('string(.)').encode('GB18030').strip()
			sid_list.append(sid)
			content_list.append(content)
		if stop_id in sid_list:
			break

	index=sid_list.index(stop_id)
	content_list=content_list[:index+1]
	sid_list=sid_list[:index+1]
	return sid_list[0],content_list

def main():
	login_url='https://passport.weibo.cn/sso/login'
	username='13771902647'
	password='yinhao'

	s=login(login_url,username,password)

	sid='5822306215'

	nick=get_nick(s,sid)
	print nick
	print cchardet.detect(nick)

	_,stop_id=get_the_first_content(s,sid,0)

	while 1:
		tmp_id,content_list=monitor_person(s,sid,0,stop_id)
		if tmp_id==stop_id:
			print nick
			print u'%s:%s 没有更新微博...继续监控' %(time.ctime(),sid)
		else:
			print nick
			print u'%s:%s 更新微博如下:' %(time.ctime(),sid)
			for content in content_list[:-1]:
				print content
				print '-'*30
		print '='*30
		stop_id=tmp_id

		time.sleep(random.randint(5,10))



if __name__ == '__main__':
	main()