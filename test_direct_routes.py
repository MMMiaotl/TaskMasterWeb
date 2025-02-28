import requests

print("\n" + "="*50)
print("测试主应用中直接定义的路由")
print("="*50)

# 测试直接调试路由
print("\n" + "-"*30)
print("测试直接调试路由 /direct_debug")
print("-"*30)
try:
    response = requests.get('http://127.0.0.1:5000/direct_debug')
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

# 测试直接服务路由
print("\n" + "-"*30)
print("测试直接服务路由 /direct_service/daily/moving")
print("-"*30)
try:
    response = requests.get('http://127.0.0.1:5000/direct_service/daily/moving')
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

# 测试原始服务路由
print("\n" + "-"*30)
print("测试原始服务路由 /service/daily/moving")
print("-"*30)
try:
    response = requests.get('http://127.0.0.1:5000/service/daily/moving')
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

print("\n" + "="*50)
print("测试结束")
print("="*50) 