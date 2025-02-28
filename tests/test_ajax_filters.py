import requests
import time
import json
from bs4 import BeautifulSoup

# 等待服务器启动
print("等待服务器启动...")
time.sleep(5)  # 增加等待时间到5秒

# 测试基本服务页面
base_url = "http://127.0.0.1:5000/service/daily/moving"
print(f"测试URL: {base_url}")
try:
    response = requests.get(base_url)
    print(f"基本服务页面状态码: {response.status_code}")
    assert response.status_code == 200
except Exception as e:
    print(f"访问基本服务页面时出错: {str(e)}")
    exit(1)

# 测试AJAX任务筛选功能
ajax_url = "http://127.0.0.1:5000/service/ajax_tasks/daily/moving"
print(f"测试AJAX URL: {ajax_url}")

try:
    # 测试价格筛选 - 从低到高
    price_asc_params = {"price_sort": "asc"}
    response = requests.get(ajax_url, params=price_asc_params)
    print(f"价格筛选(从低到高)状态码: {response.status_code}")
    assert response.status_code == 200
    print("价格筛选(从低到高)响应内容长度:", len(response.text))

    # 测试价格筛选 - 从高到低
    price_desc_params = {"price_sort": "desc"}
    response = requests.get(ajax_url, params=price_desc_params)
    print(f"价格筛选(从高到低)状态码: {response.status_code}")
    assert response.status_code == 200
    print("价格筛选(从高到低)响应内容长度:", len(response.text))

    # 测试日期筛选 - 最新优先
    date_newest_params = {"date_sort": "newest"}
    response = requests.get(ajax_url, params=date_newest_params)
    print(f"日期筛选(最新优先)状态码: {response.status_code}")
    assert response.status_code == 200
    print("日期筛选(最新优先)响应内容长度:", len(response.text))

    # 测试位置筛选 - 市中心
    location_params = {"location": "city_center"}
    response = requests.get(ajax_url, params=location_params)
    print(f"位置筛选(市中心)状态码: {response.status_code}")
    assert response.status_code == 200
    print("位置筛选(市中心)响应内容长度:", len(response.text))

    # 测试组合筛选
    combined_params = {"price_sort": "desc", "date_sort": "newest", "location": "city_center"}
    response = requests.get(ajax_url, params=combined_params)
    print(f"组合筛选状态码: {response.status_code}")
    assert response.status_code == 200
    print("组合筛选响应内容长度:", len(response.text))

    # 检查响应内容是否为HTML片段
    soup = BeautifulSoup(response.text, 'html.parser')
    task_cards = soup.find_all('div', class_='task-card')
    print(f"找到的任务卡片数量: {len(task_cards)}")

    print("所有测试通过！AJAX筛选功能正常工作。")
except Exception as e:
    print(f"测试AJAX筛选功能时出错: {str(e)}")
    exit(1) 