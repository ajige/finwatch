# coding=utf-8
import sys
#sys.setdefaultencoding( "utf-8" )
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import Series
from pandas import DataFrame
from scipy.stats import pearsonr
import pdb
import time
import random
import datetime
import json

import requests
from snownlp import sentiment
from snownlp import SnowNLP
from pyquery import PyQuery as pq
from lxml import etree

from crawlheader import sinaanalystheader, sinaheader, analyze_company_news_sentiment, summary_analyst
import matplotlib.dates as mdates
# Check if file exists before opening
import os

threadcnt = 2

def get_page(url):
    """发起请求 获得源码"""
    r = requests.get(url)
    r.encoding = 'utf8'
    html = r.text
    return html


def crawlbody(url, headers=None):
    """
    爬取新闻正文内容
    Args:
        url: 新闻链接
        headers: 可选请求头，默认为None
    Returns:
        正文文本字符串，如果提取失败则返回空字符串
    """
    try:
        if headers is None:
            # 使用默认的请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        # 处理协议相对URL
        if url.startswith('//'):
            url = 'https:' + url
        elif not url.startswith('http'):
            url = 'https://' + url
        response = requests.get(url, headers=headers, timeout=10)
        # 检测编码，新浪页面可能是gbk或gb2312
        if response.encoding.lower() in ('gbk', 'gb2312', 'gb18030'):
            response.encoding = 'gbk'
        else:
            response.encoding = 'utf-8'
        html = response.text
        # 使用PyQuery解析
        doc = pq(html)
        # 常见新闻正文选择器
        selectors = [
            'div.blk_container p',
            'div.blk_container',
        ]
        content = None
        for selector in selectors:
            elements = doc(selector)
            if elements and len(elements) > 0:
                content = elements.text()
                break
        # 如果未找到，尝试通过标签和类名组合
        if content is None:
            content = ""
        #print(content)
        return content

    except Exception as e:
        print(f"爬取正文失败 {url}: {e}")
        return ""


def crawlanalystsina():
	newsdf = pd.DataFrame(columns=('headline', 'href', 'pubtime', 'sentiment', 'type', 'source'))
	newscnt = 0
	reachend = False
	currenttime = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')

	duplicated = 0
	outdatedcnt = 0
	now = datetime.datetime.now()
	for page in range(1,10):
		usedurl = "http://stock.finance.sina.com.cn/stock/go.php/vReport_List/kind/company/index.phtml?p=%d" % page
		usedheader = sinaanalystheader
		gg={}
		tokens = usedheader.split('\n')
		for token in tokens:
			kk = token.split(': ')
			if len(kk) > 1:
				gg[kk[0]] = kk[1]

		zz = requests.get(url=usedurl, headers=gg)
		ret = zz.content
		retstr = str(ret, encoding = "gbk")
		selector = etree.HTML(retstr)
		for num in range(0, 40):
			#print(num)
			composed = '//html/body/div/div[3]/table/tr[%d]/td[2]/a' % (num+2)
			data = selector.xpath(composed)
			#print(str(data[0].title).strip())
			if len(data) < 1:
				continue
			headline = str(data[0].attrib['title']).strip()
			print(headline)
			href = data[0].attrib['href'].strip()
			
			# 爬取新闻正文
			body = crawlbody(href, headers=gg)
			
			composed = '//html/body/div/div[3]/table/tr[%d]/td[4]' % (num+2)
			data = selector.xpath(composed)
			dt = data[0].text
			
			composed = '//html/body/div/div[3]/table/tr[%d]/td[3]' % (num+2)
			data = selector.xpath(composed)
			tp = data[0].text

			# Check if dt is within last 12 hours
			try:
				dt_parsed = datetime.datetime.strptime(dt, "%Y-%m-%d")
			except ValueError:
				# If parsing fails, assume it's outdated
				dt_parsed = datetime.datetime.now() - datetime.timedelta(days=365)
			if (now - dt_parsed).total_seconds() > 24 * 3600:
				outdatedcnt += 1
				if outdatedcnt > 20:
					print("outdated news, outdatedcnt: %d", outdatedcnt)
					break
				
			result = analyze_company_news_sentiment(headline, body)
			if result is not None:
				company, sentiment_score, importance = result
				print(result)
				sentiment_val = sentiment_score
				s = pd.Series({'headline': headline, 'href': href, 'pubtime': dt, 
				   'inserttime': datetime.datetime.today(), 
				   'sentiment': sentiment_val, 'company': company, 'importance': importance, 
				   'type' : tp, 'source': 'sina'})
				newsdf = pd.concat([newsdf, s.to_frame().T], ignore_index=True)
				newscnt += 1
			
		if reachend:
			break
		
	print("%s: %d new news" % (datetime.datetime.today(), newscnt))
	
	return newsdf

def generateanalysthtml(newsdf):

	currenttime = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
	filename="analystnews/analyst_%s.csv" % currenttime 
	
	tempdf = newsdf.sort_values('pubtime', ascending=False)
	tempdf.to_csv(filename)
	#print(newsdf.sort_values('inserttime', ascending=False).head())

	template = '''
                <div class="none_class news_item">
                  <div class="news_datetime"> %s   </div>
                  <div class="news_content"> <a href="%s" target="_blank"> %.2f: %s (%s)</a> </div>
				  </div>
			  '''
	divlist = []

	if not os.path.exists(filename):
		print(f"File {filename} does not exist, skipping HTML generation")
		return
	# Load CSV into DataFrame
	df = pd.read_csv(filename)
	linecnt = len(df)
	poscnt = 0
	cnt = 0
	for _, row in df.iterrows():
		sentiment = row['sentiment']
		# Use appropriate column names
		div = template % (row['pubtime'], row['href'], sentiment, row['headline'], row['company'])
		divlist.append(div)
		cnt += 1
		if sentiment > 0.01:
			poscnt += 1

	
	divstring = '\n'.join(divlist)
	#print(divstring)
	##findtarget = '''<!-- Fullfill news content-->'''
	summarytarget = "total event"
	findtarget = "Fullfill"
	templatefile = "/var/www/html/news/analysttemplate.html"
	templatefp = open(templatefile, "r")
	corporatenewsfile = "/var/www/html/news/analyst.html"
	corporatenewsfp = open(corporatenewsfile, "w")
	negative_cnt = linecnt - poscnt
	summaryline = "total event %d, positive %d, negative %d, sentiment index %.2f" % (linecnt, poscnt, negative_cnt, (poscnt - negative_cnt) / linecnt if linecnt > 0 else 0.0)
	summaryline = '''<div class="section-title"> <span class="h2 " > <p> <a href="http://www.168invest.net/news/corporatesenti.html"> %s </a> </p> </span> </div>''' % (summaryline)
	for line in templatefp.readlines():
		if line.find(findtarget) >= 0:
			line = divstring
		if line.find(summarytarget) >= 0:
			line = summaryline
		if line.find("corporatesenti.html") >= 0: ### replace summary for sentiment
			line = line.replace("corporatesenti.html", "analystsenti.html")
		line = line +"\n"
		corporatenewsfp.write(line)

	summary = "%s,%d,%d,%d,%.2f" % (currenttime, linecnt, poscnt, negative_cnt, ((poscnt) - negative_cnt)/linecnt if linecnt > 0 else 0.0)
		
	corporatenewsfp.close()
	templatefp.close()
	print(summary)
	
	summaryfp = open('analyst_summary.csv', 'a+')
	summaryfp.write(summary + '\n')
	summaryfp.close()	


def generatesummary(newsdf):
	
	df = pd.read_csv('analyst_summary.csv', header=None, names=['timestamp', 'total', 'positive', 'negative', 'sentiment'])
	
	# Convert timestamp to datetime
	df['datetime'] = pd.to_datetime(df['timestamp'], format='%Y%m%d-%H%M%S')
	df['date'] = df['datetime'].dt.date
	
	# Aggregate by date: compute mean sentiment and sum total per day
	daily = df.groupby('date').agg({'sentiment': 'mean', 'total': 'sum'}).reset_index()
	daily['date'] = pd.to_datetime(daily['date'])
	
	# Sort by date
	daily = daily.sort_values('date')
	
	# Create figure with two subplots (shared x-axis)
	fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
	
	# Top subplot: sentiment line
	ax1.plot(daily['date'][-60:], daily['sentiment'][-60:], color='blue', marker='o', linestyle='-', linewidth=1, markersize=2)
	ax1.set_ylabel('Sentiment', color='blue')
	ax1.tick_params(axis='y', labelcolor='blue')
	ax1.grid(True, alpha=0.3)
	ax1.set_title("Sentiment for %s" % (datetime.datetime.today().date()))
	
	# Bottom subplot: news count bar chart
	ax2.bar(daily['date'][-60:], daily['total'][-60:], color='green', alpha=0.6, width=0.8)
	ax2.set_ylabel('News Count', color='green')
	ax2.tick_params(axis='y', labelcolor='green')
	ax2.grid(True, alpha=0.3)
	
	# Format x-axis
	ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
	ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
	fig.autofmt_xdate()  # rotate dates

	output_path = "/var/www/html/news/analystsentiindex.png"

	print(f"Plot saved to {output_path}")
	
	plt.xlabel("Time")
	plt.ylabel("Volume")

	plt.savefig(output_path, dpi=100, bbox_inches='tight')
	plt.close()

	summaryjson = summary_analyst(newsdf['headline'].tolist())
	summarylist = []
	for item in summaryjson:
		entity = item['entity']
		view = item['view']
		senti = item['sentiment_score']
		summarylist.append( f'<p>{entity}:{view} {senti}</p>')
	summarystr = '\n'.join(summarylist)


	##generate html
	template = '''
                 				  </div>
			  '''
	
	topdf = newsdf.groupby('company').count().sort_values('sentiment', ascending=False)
	topnewssummary = []
	for company in topdf.head(10).index:
		output = (company, newsdf[newsdf.company == company].headline.tolist(),
			newsdf[newsdf.company == company].href.tolist(),
			newsdf[newsdf.company == company].sentiment.tolist())
		#print(output)
		topnewssummary.append(output)

	print(topnewssummary)

	divlist = []
	for topnewspair in topnewssummary:
		div = ''' <div class="news_item"> '''
		headline = topnewspair[0]
		div += '<p> %s </p> \n' % headline
		details = ""
		for headline, href, sent in zip(topnewspair[1], topnewspair[2], topnewspair[3]):
			details += '''<p><a href="%s"> %s: %.2f </a> </p>''' % (href, headline, sent)

		finaldiv = div + "<p> %s </p>" % (details) + "</div>"
		#print(finaldiv)
		divlist.append(finaldiv)
	
	divstring = '\n'.join(divlist)
	toptarget = 'TopCompany'
	summarytemplate = '/var/www/html/news/analyst_summarytemplate.html'
	templatefp = open(summarytemplate, "r")
	corporatenewsfile = "/var/www/html/news/analystsenti.html"
	corporatenewsfp = open(corporatenewsfile, "w")
	for line in templatefp.readlines():
		if line.find('Summary') >= 0:
			line = summarystr
		if line.find(toptarget) >= 0:
			line = divstring
		if line.find('sentiindex.png')	> 0:
			line = line.replace('sentiindex.png', 'analystsentiindex.png')

		line = line +"\n"
		corporatenewsfp.write(line)
		
	corporatenewsfp.close()
	templatefp.close()

	
if __name__ == "__main__":
	currentday = datetime.datetime.today().date()
	cumulativecnt = 0
	
	newsdf = crawlanalystsina()
	# cumulativecnt += len(newsdf)
	#newsdf = pd.read_csv("/home/invest/childe/analystnews/analyst_20260130-161827.csv", sep = ',')
	#if cumulativecnt > threadcnt:
	generateanalysthtml(newsdf)
	generatesummary(newsdf)



	

		
