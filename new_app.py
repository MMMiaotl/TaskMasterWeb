from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "新应用首页"

@app.route('/service/<category>/<service_id>')
def service_page(category, service_id):
    return f"新应用服务页面: 类别={category}, 服务ID={service_id}"

if __name__ == '__main__':
    # 打印所有注册的路由
    print("\n=== 所有注册的路由 ===")
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
        print(f"Rule: {rule}, Endpoint: {rule.endpoint}")
    print("=== 路由注册结束 ===\n")
    
    app.run(debug=True, port=5002) 