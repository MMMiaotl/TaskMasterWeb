import requests
import time

# 等待服务器启动
print("等待服务器启动...")
time.sleep(2)

# 测试服务页面
url = "http://127.0.0.1:5000/service/daily/moving"
print(f"测试URL: {url}")

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"内容类型: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        print("服务页面访问成功!")
        # 检查返回的内容是否包含预期的HTML元素
        if "<title>搬家服务 - Task Master</title>" in response.text:
            print("页面标题正确")
        else:
            print("页面标题不正确")
            
        if "搬家服务" in response.text:
            print("找到服务名称")
        else:
            print("未找到服务名称")
    else:
        print(f"访问失败，状态码: {response.status_code}")
        print(f"错误内容: {response.text[:500]}...")
except Exception as e:
    print(f"发生错误: {str(e)}") 