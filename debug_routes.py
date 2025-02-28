from app import create_app

app = create_app()

print("\n=== 所有注册的路由 ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    print(f"Rule: {rule}, Endpoint: {rule.endpoint}")
print("=== 路由注册结束 ===\n")

# 特别检查服务相关的路由
print("\n=== 服务相关的路由 ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    if rule.endpoint.startswith('service.'):
        print(f"Rule: {rule}, Endpoint: {rule.endpoint}")
print("=== 服务路由检查结束 ===\n") 