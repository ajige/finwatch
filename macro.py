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

from crawlheader import sinaanalystheader, sinaheader, analyze_company_news_sentiment, summary_analyst, summary_macro_analyst_report, summary_strategy_analyst_report 
from crawlanalyst import crawlbody
import matplotlib.dates as mdates
# Check if file exists before opening
import os

def crawl_analyst_macro(item):
    newsdf = pd.DataFrame(columns=('headline', 'href', 'pubtime', 'sentiment', 'type', 'source'))
    newscnt = 0
    reachend = False
    currenttime = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')

    duplicated = 0
    outdatedcnt = 0
    now = datetime.datetime.now()
    destpath = '/home/invest/data/analystmacro'

    for page in range(1,10):
        usedurl = "http://stock.finance.sina.com.cn/stock/go.php/vReport_List/kind/%s/index.phtml?p=%d" % (item, page)
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
            if (now - dt_parsed).total_seconds() > 7 * 24 * 3600:
                outdatedcnt += 1
                if outdatedcnt > 20:
                    print("outdated news, outdatedcnt: %d" % outdatedcnt)
                    break

            newscnt += 1
            if newscnt % 10 == 0:
                print("crawled %d reports" % newscnt)
                time.sleep(1)
                # 保存报告到文件
            reportfile = save_report(headline, body, destpath, item)

        if reachend:
            break

    print("%s: %d new macro analyst report, reportfile %s" % (datetime.datetime.today(), newscnt,
                                                         reportfile))

    return reportfile

def save_report(headline, body, destpath, item):
    """
    保存分析师报告到文件

    参数:
        headline: 报告标题
        body: 报告正文
        destpath: 目标路径
    """
    # 确保目录存在
    if not os.path.exists(destpath):
        os.makedirs(destpath)

    # 使用当前日期作为文件名
    macro_date = '%s_' % item + datetime.datetime.today().strftime('%Y%m%d') + '.txt'
    filename = os.path.join(destpath, macro_date)

    # 追加写入文件
    with open(filename, 'a', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("标题：%s\n" % headline)
        f.write("=" * 80 + "\n")
        f.write("%s\n" % body)
        f.write("\n\n")


    return filename


# 全局文件对象，用于同时输出到屏幕和文件
_summary_file = None

def print_to_file_and_stdout(*args, **kwargs):
    """同时打印到屏幕和文件"""
    
    # 构建输出内容
    output = ' '.join(str(arg) for arg in args)
    # 打印到屏幕
    print(output, **kwargs)
    # 写入文件
    if _summary_file is not None:
        _summary_file.write(output + '\n')
        _summary_file.flush()

destpath = '/home/invest/data/analystmacro'

def get_macro():
    global _summary_file
    try:
        # 爬取报告
        reportfile = crawl_analyst_macro("macro")
        #reportfile = "/home/invest/data/analystmacro/macro_20260308.txt"

        topic = "macro"

        summary_date = 'summary_%s_' % topic + datetime.datetime.today().strftime('%Y%m%d') + '.txt'
        summary_filename = os.path.join(destpath, summary_date)
        _summary_file = open(summary_filename, 'w', encoding='utf-8')


        print_to_file_and_stdout("\n=== 分析宏观报告 ===")
        print_to_file_and_stdout("报告文件：%s" % reportfile)

        hot_topics, consensus_expectations, investment_strategy = summary_macro_analyst_report(reportfile)

        if hot_topics and consensus_expectations:
            print_to_file_and_stdout("\n=== 热门宏观话题 ===")
            for t in hot_topics:
                print_to_file_and_stdout("  - %s (热度：%d)" % (t['topic_name'], t['mention_count']))
                if 'summary' in t:
                    print_to_file_and_stdout("    摘要：%s" % t['summary'])

            print_to_file_and_stdout("\n=== 市场一致性预期 ===")
            for exp in consensus_expectations:
                direction_map = {'positive': '正面', 'negative': '负面', 'neutral': '中性'}
                consistency_map = {'high': '高', 'medium': '中', 'low': '低'}
                print_to_file_and_stdout("  - %s [%s, 一致性：%s]" % (
                    exp['expectation'],
                    direction_map.get(exp['sentiment'], exp['sentiment']),
                    consistency_map.get(exp.get('consistency', exp.get('Consistency')), '中')
                ))

            if investment_strategy:
                print_to_file_and_stdout("\n=== 推荐投资策略 ===")
                for s in investment_strategy:
                    print_to_file_and_stdout("  - %s" % s)
        else:
            print_to_file_and_stdout("分析失败")
    finally:
        # 关闭文件
        if _summary_file:
            _summary_file.close()

        # 创建软连接，指向最新日期的文件
        symlink_path = os.path.join(destpath, 'summary_%s.txt' % topic)
        # 如果软连接已存在，先删除
        if os.path.islink(symlink_path):
            os.remove(symlink_path)
        elif os.path.exists(symlink_path):
            os.remove(symlink_path)
        # 创建新的软连接
        os.symlink(summary_filename, symlink_path)

        print("摘要已保存到：%s" % summary_filename)
        print("软连接：%s -> %s" % (symlink_path, summary_filename))
        print("====================================")

def get_strategy():
    global _summary_file
    try:
        # 爬取报告
        reportfile = crawl_analyst_macro("strategy")
        #reportfile = "/home/invest/data/analystmacro/strategy_20260308.txt"

        topic = "strategy"

        summary_date = 'summary_%s_' % topic + datetime.datetime.today().strftime('%Y%m%d') + '.txt'
        summary_filename = os.path.join(destpath, summary_date)
        _summary_file = open(summary_filename, 'w', encoding='utf-8')

        print_to_file_and_stdout("\n=== 分析策略报告 ===")
        print_to_file_and_stdout("报告文件：%s" % reportfile)

        hot_topics, consensus_expectations, investment_strategy = summary_strategy_analyst_report(reportfile)

        if hot_topics and consensus_expectations:
            print_to_file_and_stdout("\n=== 热门宏观话题 ===")
            for t in hot_topics:
                print_to_file_and_stdout("  - %s (热度：%d)" % (t['topic_name'], t['mention_count']))
                if 'summary' in t:
                    print_to_file_and_stdout("    摘要：%s" % t['summary'])

            print_to_file_and_stdout("\n=== 市场一致性预期 ===")
            for exp in consensus_expectations:
                direction_map = {'positive': '正面', 'negative': '负面', 'neutral': '中性'}
                consistency_map = {'high': '高', 'medium': '中', 'low': '低'}
                print_to_file_and_stdout("  - %s [%s, 一致性：%s]" % (
                    exp['expectation'],
                    direction_map.get(exp['sentiment'], exp['sentiment']),
                    consistency_map.get(exp.get('consistency', exp.get('Consistency')), '中')
                ))

            if investment_strategy:
                print_to_file_and_stdout("\n=== 推荐投资策略 ===")
                for s in investment_strategy:
                    print_to_file_and_stdout("  - %s" % s)
        else:
            print_to_file_and_stdout("分析失败")
    finally:
        # 关闭文件
        if _summary_file:
            _summary_file.close()

        # 创建软连接，指向最新日期的文件
        symlink_path = os.path.join(destpath, 'summary_%s.txt' % topic)
        # 如果软连接已存在，先删除
        if os.path.islink(symlink_path):
            os.remove(symlink_path)
        elif os.path.exists(symlink_path):
            os.remove(symlink_path)
        # 创建新的软连接
        os.symlink(summary_filename, symlink_path)

        print("摘要已保存到：%s" % summary_filename)
        print("软连接：%s -> %s" % (symlink_path, summary_filename))

if __name__ == "__main__":
    get_macro()
    get_strategy()


