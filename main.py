#!/usr/bin/python
# -*- coding: UTF-8 -*-
# code by Benl0xe 
# email:liukang02@qianxin.com
import requests
import json
import threading
import re
import time
import base64
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

requests.packages.urllib3.disable_warnings()

all = []

all_alive = []

fp_title = open('result.txt','a')

keywords = base64.b64encode(raw_input('please input keywords:'))

count = raw_input('please input result count:')

url = 'https://fofa.so/api/v1/search/all?email=&key=&qbase64='+str(keywords)+'&size='+str(count)

filename = base64.b64decode(keywords)

if '"' in filename:
	filename = filename.replace('"','#')
	if '&' in filename:
		filename = filename.replace('&','#')
	if '=' in filename:
		filename = filename.replace('=','#')
	if '://' in filename:
		filename = filename.replace('://','#')
	if '/' in filename:
		filename = filename.replace('/','#')

f=open(filename+'.txt','a')

try:
	r=requests.get(url = url)
	size = re.findall(',"size":(.*?),',r.content)[0]
	# print r.content
	r=r.text
	r=json.loads(r)['results']
	print r
	# for i in r:
	# 	for x in range(len(i)):
	# 		print i[x]
	for i in range(len(r)):
		if 'http' in r[i-1][0]:
			res1 = r[i-1][0]
			all.append(res1)
		else:
			res = r[i-1][1]+':'+r[i-1][2]
			all.append(res)
			print res
		# f.write('%s\n'%str(res))
		# f.write('%s\n'%str(r[i-1][1]))
	print '-'*50
	print 'All result total : %s'%str(size)
	print '-'*50
except Exception as e:
	print e
# print len(list(set(all)))

for i in list(set(all)):
	x = i.strip('\n')
	f.write('%s\n'%str(i))


def scan():
	def get_title():
		lock = threading.Lock()
		while (len(all)>0):
			lock.acquire()
			i = all[0]
			del all[0]
			lock.release()
			try:
				if 'https' in i:
					r_ssl = requests.get(url=i,timeout = 5 , verify = False)
					title = re.findall('<title>(.*?)</title>',r_ssl.content)
					# print i
					if len(title) != 0:
						res_title = i + ' ---- ' +title[0]+ ' ---- ' + str(r_ssl.headers)
						fp_title.write('%s\n'%str(res_title))
						all_alive.append(i)
						print i + ' ---- ' +title[0] + ' ---- ' + str(r_ssl.headers)
					else:
						res_title_no = i + ' ---- 未检测到title'+ ' ---- ' + str(r_ssl.headers)
						fp_title.write('%s\n' % str(res_title_no))
						all_alive.append(i)
						print i + ' ---- 未检测到title'+ ' ---- ' + str(r_ssl.headers)
				else:
					http_url = 'http://'+i
					r_http = requests.get(url = http_url , timeout = 5)
					title = re.findall('<title>(.*?)</title>', r_http.content)
					if len(title) != 0:
						res_http = str(http_url) + ' ---- ' + title[0] + ' ---- ' +str(r_http.headers)
						fp_title.write('%s\n'%str(res_http))
						all_alive.append(http_url)
						print str(http_url) + ' ---- ' + title[0]+ ' ---- ' +str(r_http.headers)
					else:
						res_http_no = str(http_url) + ' ---- 未检测到title'+ ' ---- ' +str(r_http.headers)
						fp_title.write('%s\n'%str(res_http_no))
						all_alive.append(http_url)
						print str(http_url) + ' ---- 未检测到title'+ ' ---- ' +str(r_http.headers)
			except Exception as e:
				pass
			# except可作调试
	th = []
	count = 20
	for i in range(count):
		t = threading.Thread(target=get_title)
		th.append(t)
	for i in range(count):
		th[i].start()
	for i in range(count):
		th[i].join()
	time.sleep(3)
	# 新的检测模块
	def check_shiro():
		data = {'cookie':'rememberMe=1'}
		shiro_dict = ['/index.action','/login','/index.jsp','/login.jsp']
		lock = threading.Lock()
		while (len(all_alive)>0):
			lock.acquire()
			url = all_alive[0]
			del all_alive[0]
			lock.release()
			for i in shiro_dict:
				url = url + str(i)
				if 'https' in url:
					try:
						r_shiro_https = requests.get(url = url , timeout = 5 ,verify = False , headers = data)
						if 'rememberMe' in r_shiro_https.headers['Set-Cookie']:
							print 'this is shiro ----> '+str(url)
							break
					except Exception as e:
						pass
				else:
					try:
						r_shiro_http = requests.get(url = url ,timeout =5 ,verify = False , headers = data)
						if 'rememberMe' in r_shiro_http.headers['Set-Cookie']:
							print 'this is shiro ----> '+str(url)
							break
					except Exception as e:
						pass
	th = []
	count = 20
	for i in range(count):
		t = threading.Thread(target=check_shiro)
		th.append(t)
	for i in range(count):
		th[i].start()
	for i in range(count):
		th[i].join()

scan()


