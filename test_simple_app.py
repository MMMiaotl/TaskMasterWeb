import requests

print("\n" + "="*50)
print("测试简单应用的路由")
print("="*50)

# 测试根路由
print("\n" + "-"*30)
print("测试根路由 /")
print("-"*30)
try:
    response = requests.get('http://127.0.0.1:5001/')
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

# 测试服务首页
print("\n" + "-"*30)
print("测试服务首页 /service/")
print("-"*30)
try:
    response = requests.get('http://127.0.0.1:5001/service/')
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

# 测试服务页面
print("\n" + "-"*30)
print("测试服务页面 /service/daily/moving")
print("-"*30)
try:
    response = requests.get('http://127.0.0.1:5001/service/daily/moving')
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

print("\n" + "="*50)
print("测试结束")
print("="*50) 