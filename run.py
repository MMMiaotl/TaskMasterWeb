from app import create_app
from flask import Flask

app = create_app()

# 添加一个直接的调试路由
@app.route('/direct_debug')
def direct_debug():
    return "直接调试路由 - 绕过蓝图"

@app.route('/direct_service/<category>/<service_id>')
def direct_service(category, service_id):
    return f"直接服务路由: 类别={category}, 服务ID={service_id}"

if __name__ == '__main__':
    app.run(debug=True)