#!/usr/bin/env python3
import requests
import json
import re

BASE_URL = "https://www.csindex.com.cn"
INDEX_CODE = "H30269"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.csindex.com.cn/'
}

def try_url(url):
    try:
        print(f"尝试: {url}")
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            content_type = resp.headers.get('content-type', '')
            if 'application/json' in content_type:
                data = resp.json()
                print(f"  成功 JSON 数据，键: {list(data.keys()) if isinstance(data, dict) else '列表'}")
                # 检查是否有下载链接
                if isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, str) and ('.xls' in v.lower() or '.xlsx' in v.lower()):
                            print(f"  找到Excel链接: {v}")
                return True, resp
            elif 'text/html' in content_type:
                # 搜索Excel链接
                excel_links = re.findall(r'href=[\'"]?([^\'" >]+\.xlsx?)', resp.text, re.I)
                if excel_links:
                    print(f"  找到Excel链接: {excel_links}")
                    return True, resp
                else:
                    print(f"  HTML 页面，长度: {len(resp.text)}")
            else:
                print(f"  内容类型: {content_type}")
        else:
            print(f"  状态码: {resp.status_code}")
    except Exception as e:
        print(f"  错误: {e}")
    return False, None

# 尝试一些可能的API端点
candidates = [
    f"{BASE_URL}/api/indices/{INDEX_CODE}",
    f"{BASE_URL}/api/indices/{INDEX_CODE}/download",
    f"{BASE_URL}/api/indices/{INDEX_CODE}/export",
    f"{BASE_URL}/api/indices/{INDEX_CODE}/data",
    f"{BASE_URL}/api/indices/{INDEX_CODE}/excel",
    f"{BASE_URL}/api/indices/{INDEX_CODE}/file",
    f"{BASE_URL}/api/indices/{INDEX_CODE}/valuation",
    f"{BASE_URL}/api/indices/{INDEX_CODE}/valuation/download",
    f"{BASE_URL}/api/indices/{INDEX_CODE}/valuation/export",
    f"{BASE_URL}/api/indices/family/detail/{INDEX_CODE}",
    f"{BASE_URL}/api/indices/family/detail/{INDEX_CODE}/download",
]

for candidate in candidates:
    success, resp = try_url(candidate)
    if success:
        # 进一步检查
        pass

# 也尝试POST请求
print("\n尝试POST请求...")
post_candidates = [
    f"{BASE_URL}/api/indices/{INDEX_CODE}/export",
]
for candidate in post_candidates:
    try:
        print(f"POST {candidate}")
        resp = requests.post(candidate, headers=headers, timeout=5)
        print(f"  状态码: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  内容类型: {resp.headers.get('content-type')}")
    except Exception as e:
        print(f"  错误: {e}")