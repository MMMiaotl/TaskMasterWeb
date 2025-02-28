from app import create_app
import json

app = create_app()
client = app.test_client()

print("\n" + "="*50)
print("测试开始")
print("="*50)

# 打印所有注册的路由
print("\n=== 所有注册的路由 ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    print(f"Rule: {rule}, Endpoint: {rule.endpoint}")
print("=== 路由注册结束 ===\n")

# 测试服务首页
print("\n" + "-"*30)
print("测试服务首页")
print("-"*30)
response = client.get('/service/')
print(f"状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
print(f"响应内容: {response.data.decode('utf-8')}")

# 测试服务页面
print("\n" + "-"*30)
print("测试服务页面 /service/daily/moving")
print("-"*30)
response = client.get('/service/daily/moving')
print(f"状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
print(f"响应内容: {response.data.decode('utf-8')}")

# 测试调试路由
print("\n" + "-"*30)
print("测试调试路由 /service/debug")
print("-"*30)
response = client.get('/service/debug')
print(f"状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
try:
    json_data = json.loads(response.data.decode('utf-8'))
    print(f"响应内容(JSON格式化): {json.dumps(json_data, indent=2, ensure_ascii=False)}")
except:
    print(f"响应内容: {response.data.decode('utf-8')}")

# 测试直接访问URL
print("\n" + "-"*30)
print("测试直接访问URL (不通过Flask测试客户端)")
print("-"*30)
import requests
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