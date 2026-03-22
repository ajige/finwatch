emoneyurl = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
# 必须带上 Referer，否则接口可能报错
emoneyheaders = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://finance.eastmoney.com/",
        "Accept": "*/*", # 接受任何类型，因为是 JS/JSONP
        "Sec-Fetch-Site": "same-site",
}

sinaheader = '''
:authority:feed.mix.sina.com.cn
:method:GET
:path:/api/roll/get?pageid=164&lid=1694&num=10&page=3&callback=feedCardJsonpCallback&_=1646920187197
:scheme:https
accept:*/*
accept-encoding:gzip, deflate, br
accept-language:en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6
cookie:SCF=AocSh_YxlIDVlhFrFynV-mC0I_67KZ42lRLJBDkC_fQu9id01A7pshTkBmsJTLNbDSgMwnreH0qMhZeRiYVYPDU.; SINAGLOBAL=60.194.192.1_1469873154.201600; vjuids=d142611c.1563b446536.0.33b3dfa9; U_TRS1=00000001.8c531830.579c7c08.9c6ffd9d; vjlast=1549707324; gr_user_id=ed112ff7-f0a0-49dc-813b-3091b137d2d1; grwng_uid=850cb4d3-6d5e-4f9b-9dc5-8ea53f71192c; channel=pc; _ga=GA1.3.1782909136.1591145517; SGUID=1628229583250_58606769; UOR=,,; SUB=_2AkMWxqXRf8NxqwJRmPkdyWrma4R0zQvEieKgmlQKJRMyHRl-yD9jqmIMtRB6PUaLPhK7RA9FvGphjjfQG5e0BIvPREI1; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFQVFaARbS.67p5n328Qxyo; Apache=111.197.252.47_1646919227.624262; ULV=1646919285744:258:1:1:111.197.252.47_1646919227.624262:1637584652201; hqEtagMode=0; rotatecount=3; U_TRS2=0000002f.8e57c21d.6229fe6a.102a9f2b; directAd_wcp=true; FEED-MIX-SINA-COM-CN=
referer:http://finance.sina.com.cn/chanjing/
user-agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36
'''

sinaanalystheader = '''
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate
Accept-Language:en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6
Connection:keep-alive
Cookie:SCF=AocSh_YxlIDVlhFrFynV-mC0I_67KZ42lRLJBDkC_fQu9id01A7pshTkBmsJTLNbDSgMwnreH0qMhZeRiYVYPDU.; SINAGLOBAL=60.194.192.1_1469873154.201600; vjuids=d142611c.1563b446536.0.33b3dfa9; U_TRS1=00000001.8c531830.579c7c08.9c6ffd9d; vjlast=1549707324; gr_user_id=ed112ff7-f0a0-49dc-813b-3091b137d2d1; grwng_uid=850cb4d3-6d5e-4f9b-9dc5-8ea53f71192c; channel=pc; _ga=GA1.3.1782909136.1591145517; visited_funds=; SGUID=1628229583250_58606769; UOR=,,; visited_uss=gb_fds%7Cgb_.inx%7Cgb_tctzf%7Cgb_tcehy%7Cgb_mpngy%7Cgb_pdd%7Cgb_jd%7Cgb_ibkr%7Cgb_ms%7Cgb_aapl; SUB=_2AkMWxqXRf8NxqwJRmPkdyWrma4R0zQvEieKgmlQKJRMyHRl-yD9jqmIMtRB6PUaLPhK7RA9FvGphjjfQG5e0BIvPREI1; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFQVFaARbS.67p5n328Qxyo; SR_SEL=1_511; UM_distinctid=17f7b1c9f2592-01e75077474a23-454f032b-144000-17f7b1c9f268a; __gads=ID=d1cbe23ff61b2c64-223c772df1d000cb:T=1647047569:RT=1647047569:S=ALNI_MZ5zEQJxkhMlkP6XK25ibSQqivSoA; Apache=111.197.252.47_1647215968.78222; SFA_version=2021-08-02%2009%3A00; hqEtagMode=1; ULV=1647216011696:262:5:2:111.197.252.47_1647215968.78222:1647215995542; rotatecount=2; U_TRS2=0000002f.dab6c99d.622e858c.503138c5; STOCK7-FINANCE-SINA-COM-CN=
Host:stock.finance.sina.com.cn
Referer:http://stock.finance.sina.com.cn/stock/go.php/vReport_List/kind/lastest/index.phtml?p=1
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36
'''

import requests
import json
import datetime
import time
import re
import os

# API 配置 - 从环境变量读取
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/chat/completions")
DEEPSEEK_AUTH_TOKEN = os.getenv("DEEPSEEK_AUTH_TOKEN", "sk-4f7491fa7e8240bc92896e50d4597ca2")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

def get_page(url):
    """发起请求 获得源码"""
    r = requests.get(url)
    r.encoding = 'utf8'
    html = r.text
    return html


def analyze_company_news_sentiment(news_headline, news_content=""):
    """
    使用 Anthropic API 分析公司新闻情感

    参数:
        news_headline: 新闻标题
        news_content: 新闻内容（可选）

    返回：sentiment_result['company_name'], sentiment_result['sentiment_score'], sentiment_result['importance']

    """

    # API 配置
    # DashScope 应用 API 端点
    api_url = DEEPSEEK_BASE_URL
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    # 构建提示词
    prompt = f"""请分析以下公司新闻的情感倾向，并给出情感评分（-1 到 1 之间）, 重要性评分（0 到 1 之间）：
    情感评分：
    - -1.0: 非常负面
    - -0.5: 负面
    - 0.0: 中性
    - 0.5: 正面
    - 1.0: 非常正面
    重要性评分：0：微不足道；1：对于公司发展或股票市场非常重要
    新闻标题：{news_headline}

    {"新闻内容：" + news_content if news_content else ""}

    请以 JSON 格式返回结果，包含以下字段：
    1. 公司名称，公司名称要正式，如果是上市公司，要和上市公司名称一致，用简称，比如寒武纪科技股份有限公司就用寒武纪。
    如果这个新闻是关于某个行业的，就给出行业名称；如果是关于整个股票市场的，就给出股票市场；
    2. sentiment_score: 情感评分（-1 到 1 之间的浮点数）
    3. sentiment_label: 情感标签（positive/negative/neutral）
    json example:
	{{
	"company_name": "腾讯控股",
	"sentiment_score": 1.0,
	"sentiment_label": "非常正面",
    "importance": 0.9
	}}
    只返回 JSON 格式的结果，不要有其他内容。"""

    # 请求数据
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的金融新闻分析专家。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }

    try:
        # 发送请求
        response = requests.post(api_url, headers=headers, json=data, timeout=30)

        # 打印调试信息
        if response.status_code != 200:
            print(f"Error Response: {response.text[:500]}")

        response.raise_for_status()

        # 解析响应
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # 解析 JSON 结果 - 处理可能的 markdown 代码块
        try:
            # 移除可能的 markdown 代码块标记
            json_content = content.strip()
            if json_content.startswith('```json'):
                json_content = json_content[7:]  # 移除 ```json
            if json_content.startswith('```'):
                json_content = json_content[3:]  # 移除 ```
            if json_content.endswith('```'):
                json_content = json_content[:-3]  # 移除结尾的 ```

            json_content = json_content.strip()

            sentiment_result = json.loads(json_content)
            return sentiment_result['company_name'], sentiment_result['sentiment_score'], sentiment_result['importance']
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败：{e}")
            print(f"处理后的内容：{json_content[:200]}...")
            return None

    except requests.exceptions.RequestException as e:
        print(f"API 请求失败：{e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败：{e}")
        print(f"原始响应：{content[:200]}...")
        return None
    except Exception as e:
        print(f"发生错误：{e}")
        return None


def summary_analyst(headerlist):
    """
    使用 DeepSeek API 分析公司新闻情感

    参数:
        api_key: DeepSeek API 密钥
        news_headline: 新闻标题
        news_content: 新闻内容（可选）

    返回：sentiment_result['company_name'], sentiment_result['sentiment_score'], sentiment_result['importance']
    """

    # API 配置
    api_url = DEEPSEEK_BASE_URL
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    news_headline = '|'.join(headerlist)

    # 构建提示词
    prompt = f"""请根据以下分析师新闻的标题，总结给出 10 点今天最重要的观点。观点包括宏观经济的，股票市场整体的，某个行业整体，或者单个公司的观点。
    分析师观点：{news_headline}
    分析师观点之间用'|'分隔。
    请以 JSON 格式返回结果，包含以下字段：
    1. entity: 如果是关于宏观经济的，就写宏观经济；如果这个新闻是关于某个行业的，就给出行业名称；如果是关于整个股票市场的，就写股票市场；
    如果是关于大宗商品的，就写大宗商品的名称；
    如果是公司的，给出公司名称，公司名称要正式，如果是上市公司，要和上市公司名称一致，用简称，比如寒武纪科技股份有限公司就用寒武纪。
    2. sentiment_score: 情感评分（-1 到 1 之间的浮点数）
    3. view: 分析师的观点综述；观点综述尽可能写的有道理。
    json example:
	{[{
	"entity": "股票市场",
	"sentiment_score": 1.0,
	"view": "bullish market in recent"
	}, {
	"entity": "股票市场",
	"sentiment_score": 2.0,
	"view": "bullish market in recent"
	}, ]}
    只返回 JSON 格式的结果，不要有其他内容。"""

    # 请求数据
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的金融新闻分析专家。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 3000
    }

    try:
        # 发送请求
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        # 解析响应
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # 解析 JSON 结果 - 处理可能的 markdown 代码块
        try:
            # 移除可能的 markdown 代码块标记
            json_content = content.strip()
            if json_content.startswith('```json'):
                json_content = json_content[7:]  # 移除 ```json
            if json_content.startswith('```'):
                json_content = json_content[3:]  # 移除 ```
            if json_content.endswith('```'):
                json_content = json_content[:-3]  # 移除结尾的 ```

            json_content = json_content.strip()

            sentiment_result = json.loads(json_content)
            return sentiment_result
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败：{e}")
            print(f"处理后的内容：{json_content[:200]}...")
            return None

    except requests.exceptions.RequestException as e:
        print(f"API 请求失败：{e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败：{e}")
        print(f"原始响应：{content[:200]}...")
        return None
    except Exception as e:
        print(f"发生错误：{e}")
        return None


def summary_macro_analyst_report(reportpath):
    """
    使用 DeepSeek API 分析宏观分析师报告，给出热门宏观话题和一致性预期

    参数:
        reportpath: 宏观报告文件路径

    返回：
        hot_topics: 热门宏观话题列表
        consensus_expectations: 一致性预期列表
        investment_strategy: 推荐投资策略列表
    """

    # 读取报告文件
    try:
        with open(reportpath, 'r', encoding='utf-8') as f:
            report_content = f.read()
    except FileNotFoundError:
        print(f"报告文件不存在：{reportpath}")
        return None, None, None
    except Exception as e:
        print(f"读取报告文件失败：{e}")
        return None, None, None

    # API 配置
    api_url = DEEPSEEK_BASE_URL
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    # 构建提示词
    prompt = f"""请根据以下的近期宏观分析师报告内容，分析并总结：(注意，要给出关键的数字)
    1. 目前热门的宏观话题（5到8个）
    热门宏观话题：当前市场讨论多的宏观经济话题，如 房地产, GDP、通胀、货币政策、财政政策、股市，债市，黄金，进出口等
    2. 市场一致性预期（尽量全面的）
    一致性预期：市场主流观点对未来经济走势的判断， 包括房地产, 经济增长预期、利率走势、通胀预期，股市，债市，黄金，房地产的预期. 要给出每一项的预期。
    要是有很不一致的观点，也请给出，说明当前很有分歧。
    3. 推荐的投资方向和策略（1-3个）
    
    宏观分析师报告内容：
    {report_content[:15000]}

    请以 JSON 格式返回结果，包含以下字段：
    1. hot_topics: 热门宏观话题数组，每个话题包含 topic_name（话题名称）和 mention_count（提及的报告数）
    2. consensus_expectations: 一致性预期数组，每个预期包含 expectation（预期内容）、sentiment（方向：positive/negative/neutral）和 一致性（一致性：high/medium/low）
    一致性为low，说明分歧很大。
    3. investment strategy: 例如，推荐投资红利和科技

    json example:
    {{
        "hot_topics": [
            {{"topic_name": "GDP 增长", "mention_count": 5, "summary": "GDP 稳健增长5%"}},
            {{"topic_name": "货币政策宽松", "mention_count": 3, "summary": "货币政策维持宽松，原因是" }}
        ],
        "consensus_expectations": [
            {{"expectation": "预计 2026 年 GDP 增长 5% 左右", "sentiment": "positive", "consistency": "high"}},
            {{"expectation": "CPI 将温和回升至 2%-3% 区间", "sentiment": "neutral", "consistency": "medium"}}
        ],
        "investment_strategy": [
            "红利", 
            "黄金"
        ]
    }}

    只返回 JSON 格式的结果，不要有其他内容。"""

    # 请求数据
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的宏观经济分析师，擅长从大量报告中提取关键话题,市场一致性预期,和宏观投资策略"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }

    try:
        # 发送请求
        response = requests.post(api_url, headers=headers, json=data, timeout=60)

        # 打印调试信息
        if response.status_code != 200:
            print(f"Error Response: {response.text[:500]}")

        response.raise_for_status()

        # 解析响应
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # 解析 JSON 结果 - 处理可能的 markdown 代码块
        try:
            # 移除可能的 markdown 代码块标记
            json_content = content.strip()
            if json_content.startswith('```json'):
                json_content = json_content[7:]  # 移除 ```json
            if json_content.startswith('```'):
                json_content = json_content[3:]  # 移除 ```
            if json_content.endswith('```'):
                json_content = json_content[:-3]  # 移除结尾的 ```

            json_content = json_content.strip()

            analysis_result = json.loads(json_content)
            hot_topics = analysis_result.get('hot_topics', [])
            consensus_expectations = analysis_result.get('consensus_expectations', [])
            investment_strategy = analysis_result.get('investment_strategy', [])
            return hot_topics, consensus_expectations, investment_strategy
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败：{e}")
            print(f"处理后的内容：{json_content[:200]}...")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"API 请求失败：{e}")
        return None, None, None
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败：{e}")
        print(f"原始响应：{content[:200]}...")
        return None, None, None
    except Exception as e:
        print(f"发生错误：{e}")
        return None, None, None


def summary_strategy_analyst_report(reportpath):
    """
    使用 DeepSeek API 分析策略分析师报告，提取投资策略和建议

    参数:
        reportpath: 策略报告文件路径

    返回：
        hot_topics: 热门策略话题列表
        consensus_expectations: 一致性预期列表
        investment_strategy: 推荐投资策略列表
    """

    # 读取报告文件
    try:
        with open(reportpath, 'r', encoding='utf-8') as f:
            report_content = f.read()
    except FileNotFoundError:
        print(f"报告文件不存在：{reportpath}")
        return None, None, None
    except Exception as e:
        print(f"读取报告文件失败：{e}")
        return None, None, None

    # API 配置
    api_url = DEEPSEEK_BASE_URL
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    # 构建提示词 - 侧重于投资策略
    prompt = f"""请根据以下的近期策略分析师报告内容，分析并总结：(注意，要给出关键的数字)
    1. 目前热门的投资策略话题（5-8个）
    热门策略话题：当前市场讨论最多的投资策略，如行业配置、风格偏好、主题投资、选股策略等
    2. 市场一致性预期（尽量全面的）
    一致性预期：市场主流观点对未来股票，债券，房地产等市场走势、行业表现、风格切换的判断
    要是有很不一致的观点，也请给出，说明当前很有分歧。
    3. 推荐的投资方向和策略（3-5 个）
    投资策略：具体的投资建议，包括行业推荐、主题推荐、个股推荐等

    策略分析师报告内容：
    {report_content[:15000]}

    请以 JSON 格式返回结果，包含以下字段：
    1. hot_topics: 热门策略话题数组，每个话题包含 topic_name（话题名称）和 mention_count（提及的报告数）和 summary（摘要）
    2. consensus_expectations: 一致性预期数组，每个预期包含 expectation（预期内容）、sentiment（方向：positive/negative/neutral）和 一致性（一致性：high/medium/low）
    一致性为low，说明分歧很大。
    3. investment_strategy: 投资策略数组，每个策略是一个字符串

    json example:
    {{
        "hot_topics": [
            {{"topic_name": "科技成长", "mention_count": 5, "summary": "科技成长股受追捧"}},
            {{"topic_name": "高股息策略", "mention_count": 3, "summary": "高股息股票配置价值凸显"}}
        ],
        "consensus_expectations": [
            {{"expectation": "预计成长股将继续跑赢价值股", "sentiment": "positive", "consistency": "high"}},
            {{"expectation": "市场震荡向上", "sentiment": "positive", "consistency": "medium"}}
        ],
        "investment_strategy": [
            "科技：AI、半导体、消费电子",
            "医药：创新药、医疗器械",
            "高股息：银行、电力"
        ]
    }}

    只返回 JSON 格式的结果，不要有其他内容。"""

    # 请求数据
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的策略分析师，擅长从大量策略报告中提取关键话题、市场一致性预期和投资策略建议。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }

    try:
        # 发送请求
        response = requests.post(api_url, headers=headers, json=data, timeout=60)

        # 打印调试信息
        if response.status_code != 200:
            print(f"Error Response: {response.text[:500]}")

        response.raise_for_status()

        # 解析响应
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # 解析 JSON 结果 - 处理可能的 markdown 代码块
        try:
            # 移除可能的 markdown 代码块标记
            json_content = content.strip()
            if json_content.startswith('```json'):
                json_content = json_content[7:]  # 移除 ```json
            if json_content.startswith('```'):
                json_content = json_content[3:]  # 移除 ```
            if json_content.endswith('```'):
                json_content = json_content[:-3]  # 移除结尾的 ```

            json_content = json_content.strip()

            analysis_result = json.loads(json_content)
            hot_topics = analysis_result.get('hot_topics', [])
            consensus_expectations = analysis_result.get('consensus_expectations', [])
            investment_strategy = analysis_result.get('investment_strategy', [])
            return hot_topics, consensus_expectations, investment_strategy
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败：{e}")
            print(f"处理后的内容：{json_content[:200]}...")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"API 请求失败：{e}")
        return None, None, None
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败：{e}")
        print(f"原始响应：{content[:200]}...")
        return None, None, None
    except Exception as e:
        print(f"发生错误：{e}")
        return None, None, None


def crawl_sina_page(page):
	pageitems = []
	usedurl = "https://feed.mix.sina.com.cn/api/roll/get?pageid=164&lid=1694&num=20&page=%d&callback=feedCardJsonpCallback&_=1646920187197" % page
	usedheader = sinaheader
	gg={}
	tokens = usedheader.split('\n')
	for token in tokens:
		kk = token.split(': ')
		if len(kk) > 1:
			gg[kk[0]] = kk[1]

	zz = requests.get(url=usedurl, headers=gg)
	ret = zz.content
	retstr = ret.decode()
	pos = retstr.find('feedCardJsonpCallback(')
	if pos == -1:
		# Try alternative pattern
		pos = retstr.find('{')
		if pos == -1:
			print("No JSON data found in Sina response")
			return
		result = retstr[pos:]
	else:
		rpos = retstr.rfind(');}catch(e)')
		if rpos == -1:
			rpos = retstr.rfind(');')
		if rpos == -1:
			print("No end marker found in Sina response")
			return
		result = retstr[pos + len('feedCardJsonpCallback('): rpos]

	# Clean the result string
	result = result.strip()
	if result.endswith(');'):
		result = result[:-2]
	if result.endswith(')'):
		result = result[:-1]

	# Remove extra backslashes
	result = result.replace("\\\\", "\\")

	try:
		ff = json.loads(result)
	except json.JSONDecodeError as e:
		print(f"JSON decode error: {e}")
		print(f"Result preview: {result[:200]}...")
		return

	for item in ff['result']['data']:
		headline = item['title'].strip()
		href = item['urls']
		href = href.replace('[', '').replace(']', '').replace('\\', '').replace('"', '')
		dt = datetime.datetime.fromtimestamp(int(item['mtime']))
		pageitems.append((headline, href, dt))

	return pageitems

def crawl_eastmoney_page(page):
    pageitems = []
    # 2. 请求参数 (根据你提供的链接分析)
    params = {
        "client": "web",
        "biz": "web_news_col",
        "column": "354",           # 354 通常对应 "公司" 资讯板块
        "order": "1",              # 1 通常代表按时间倒序
        "needInteractData": "0",   # 不需要交互数据
        "page_index": "%d" % page,         # 页码
        "page_size": "20",         # 每页数量
        # "req_trace": "1767710763435", # 这个是时间戳，建议动态生成
        "fields": "code,showTime,title,mediaName,summary,image,url,uniqueUrl,Np_dst",
        "types": "1,20",           # 资讯类型
        # "callback": "jquery18302546284174109681_1767710763363", # JSONP 回调函数名，不需要传给服务器
        # "_": "1767710763436"     # 防缓存时间戳
    }

    # 动态生成时间戳 (模拟浏览器行为)
    params["req_trace"] = str(int(time.time() * 1000))
    params["_"] = str(int(time.time() * 1000))

    try:
        # 4. 发送 GET 请求
        response = requests.get(emoneyurl, headers=emoneyheaders, params=params, timeout=10)
        if response.status_code == 200:
            text = response.text
            # 方法 A：使用正则表达式去除包裹
            # 匹配最外层的括号内容
            # match = re.search(r'\(({.*})\)', text)
            # if match:
            #     json_str = match.group(1)
            #     data = json.loads(json_str)
            # else:
            data = response.json()

            news_list = data['data']['list']

            # 7. 遍历并筛选
            for item in news_list:
                # 提取字段 (注意字段名根据你提供的接口参数)
                title = item.get("title", "")
                summary = item.get("summary", "")
                pub_time_str = item.get("showTime", "")  # 时间戳或格式化时间
                news_url = item.get("url", "")
                print(title, summary, news_url)
                # Convert pub_time to datetime object
                if pub_time_str:
                    try:
                        # Try parsing as "YYYY-MM-DD HH:MM:SS"
                        pub_time = datetime.datetime.strptime(pub_time_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pub_time = datetime.datetime.now()
                pageitems.append((title, news_url, pub_time))
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print(response.text[:200])  # 打印前 200 字符错误信息

    except Exception as e:
        print("发生错误：", e)

    return pageitems
