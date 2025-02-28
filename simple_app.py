from flask import Flask, Blueprint

app = Flask(__name__)

# 创建一个简单的蓝图
service_bp = Blueprint('service', __name__)

@service_bp.route('/')
def service_index():
    return "服务首页 - 简单应用"

@service_bp.route('/<category>/<service_id>')
def service_page(category, service_id):
    return f"服务页面: 类别={category}, 服务ID={service_id} - 简单应用"

# 注册蓝图
app.register_blueprint(service_bp, url_prefix='/service')

# 添加一个根路由
@app.route('/')
def index():
    return "首页 - 简单应用"

if __name__ == '__main__':
    # 打印所有注册的路由
    print("\n=== 所有注册的路由 ===")
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
        print(f"Rule: {rule}, Endpoint: {rule.endpoint}")
    print("=== 路由注册结束 ===\n")
    
    app.run(debug=True, port=5001) 