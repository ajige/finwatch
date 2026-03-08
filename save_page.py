#!/usr/bin/env python3
import requests
import re

url = "https://www.csindex.com.cn/#/indices/family/detail?indexCode=H30269"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

resp = requests.get(url, headers=headers, timeout=10)
with open('page.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)
print(f"页面已保存，长度: {len(resp.text)}")

# 搜索所有可能的URL（包括JavaScript变量）
# 查找包含 .xls 或 .xlsx 的字符串
pattern = r'["\'](https?://[^"\']*?\.xlsx?)["\']'
matches = re.findall(pattern, resp.text, re.I)
if matches:
    print("找到Excel URL:")
    for m in matches:
        print(" ", m)
else:
    print("未找到Excel URL，搜索其他模式")
    # 搜索包含 download 的路径
    pattern2 = r'["\'](/[^"\']*?download[^"\']*?)["\']'
    matches2 = re.findall(pattern2, resp.text, re.I)
    if matches2:
        print("找到download路径:")
        for m in matches2:
            print(" ", m)
    # 搜索包含 export 的路径
    pattern3 = r'["\'](/[^"\']*?export[^"\']*?)["\']'
    matches3 = re.findall(pattern3, resp.text, re.I)
    if matches3:
        print("找到export路径:")
        for m in matches3:
            print(" ", m)