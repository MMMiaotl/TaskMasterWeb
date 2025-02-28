import requests
import time
from bs4 import BeautifulSoup

# 等待服务器启动
print("等待服务器启动...")
time.sleep(5)

# 测试服务页面
base_url = "http://127.0.0.1:5000/service/daily/moving"
print(f"测试URL: {base_url}")
try:
    response = requests.get(base_url)
    print(f"服务页面状态码: {response.status_code}")
    assert response.status_code == 200
    
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 检查服务详情区域
    service_detail = soup.find('div', class_='service-detail')
    assert service_detail is not None, "未找到服务详情区域"
    
    # 检查flex布局
    flex_container = service_detail.find('div', class_='d-flex')
    assert flex_container is not None, "未找到flex布局容器"
    
    # 检查服务标题和描述在左侧
    content_area = flex_container.find('div', class_='flex-grow-1')
    assert content_area is not None, "未找到内容区域"
    
    # 检查服务标题
    title = content_area.find('h1')
    assert title is not None, "未找到服务标题"
    print(f"服务标题: {title.text.strip()}")
    
    # 检查发布任务按钮在右侧
    actions_area = flex_container.find('div', class_='service-actions')
    assert actions_area is not None, "未找到操作区域"
    
    # 检查发布任务按钮
    button = actions_area.find('a', class_='btn-primary')
    assert button is not None, "未找到发布任务按钮"
    assert "发布任务" in button.text, "按钮文本不正确"
    print(f"按钮文本: {button.text.strip()}")
    
    print("布局测试通过！发布任务按钮已成功移到右侧。")
except Exception as e:
    print(f"测试服务页面布局时出错: {str(e)}")
    exit(1) 