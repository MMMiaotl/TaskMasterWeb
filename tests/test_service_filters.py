import requests
import time

# 等待服务器启动
print("等待服务器启动...")
time.sleep(2)

# 测试基本服务页面
base_url = "http://127.0.0.1:5000/service/daily/moving"
print(f"测试基本URL: {base_url}")

try:
    response = requests.get(base_url)
    print(f"基本页面状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("基本服务页面访问成功!")
        
        # 测试价格排序过滤器
        price_asc_url = f"{base_url}?price_sort=asc"
        print(f"\n测试价格升序排序: {price_asc_url}")
        price_asc_response = requests.get(price_asc_url)
        print(f"状态码: {price_asc_response.status_code}")
        
        if price_asc_response.status_code == 200:
            print("价格升序排序页面访问成功!")
            if 'value="asc" selected' in price_asc_response.text:
                print("价格升序选项已正确选中")
            else:
                print("警告: 价格升序选项未正确选中")
        
        # 测试日期排序过滤器
        date_newest_url = f"{base_url}?date_sort=newest"
        print(f"\n测试最新日期排序: {date_newest_url}")
        date_newest_response = requests.get(date_newest_url)
        print(f"状态码: {date_newest_response.status_code}")
        
        if date_newest_response.status_code == 200:
            print("最新日期排序页面访问成功!")
            if 'value="newest" selected' in date_newest_response.text:
                print("最新日期选项已正确选中")
            else:
                print("警告: 最新日期选项未正确选中")
        
        # 测试位置过滤器
        location_url = f"{base_url}?location=city_center"
        print(f"\n测试位置过滤: {location_url}")
        location_response = requests.get(location_url)
        print(f"状态码: {location_response.status_code}")
        
        if location_response.status_code == 200:
            print("位置过滤页面访问成功!")
            if 'value="city_center" selected' in location_response.text:
                print("市中心位置选项已正确选中")
            else:
                print("警告: 市中心位置选项未正确选中")
        
        # 测试组合过滤器
        combined_url = f"{base_url}?price_sort=desc&date_sort=last_week&location=suburbs"
        print(f"\n测试组合过滤: {combined_url}")
        combined_response = requests.get(combined_url)
        print(f"状态码: {combined_response.status_code}")
        
        if combined_response.status_code == 200:
            print("组合过滤页面访问成功!")
            if 'value="desc" selected' in combined_response.text and 'value="last_week" selected' in combined_response.text and 'value="suburbs" selected' in combined_response.text:
                print("所有组合选项已正确选中")
            else:
                print("警告: 部分组合选项未正确选中")
    else:
        print(f"访问失败，状态码: {response.status_code}")
        print(f"错误内容: {response.text[:500]}...")
except Exception as e:
    print(f"发生错误: {str(e)}") 