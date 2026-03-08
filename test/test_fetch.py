#!/usr/bin/env python3
import requests
import re

url = "https://www.csindex.com.cn/#/indices/family/detail?indexCode=H30269"

# 尝试获取页面
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"内容类型: {response.headers.get('content-type')}")
    # 打印前500个字符
    print("前500字符:", response.text[:500])

    # 搜索download、xls、xlsx、export等关键词
    text = response.text.lower()
    if 'download' in text:
        print("找到 'download' 关键词")
    if 'xls' in text:
        print("找到 'xls' 关键词")
    if 'xlsx' in text:
        print("找到 'xlsx' 关键词")
    if 'export' in text:
        print("找到 'export' 关键词")

    # 查找所有链接
    links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
    excel_links = [link for link in links if '.xls' in link.lower() or '.xlsx' in link.lower()]
    if excel_links:
        print("找到Excel链接:", excel_links)
    else:
        print("未找到Excel链接，所有链接:")
        for link in links[:20]:
            print("  ", link)

except Exception as e:
    print(f"错误: {e}")