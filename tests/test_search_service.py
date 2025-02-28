import requests
import time
from bs4 import BeautifulSoup

# 等待服务器启动
print("等待服务器启动...")
time.sleep(5)

# 测试搜索建议功能
base_url = "http://127.0.0.1:5000"
print("测试搜索建议功能...")

# 测试搜索建议 - 搬家
search_term = "搬家"
suggestions_url = f"{base_url}/search/suggestions?q={search_term}"
response = requests.get(suggestions_url)
print(f"搜索建议状态码: {response.status_code}")
assert response.status_code == 200

suggestions = response.json()
print(f"找到 {len(suggestions)} 个搜索建议")
for suggestion in suggestions:
    print(f"- {suggestion['title']} ({suggestion['type']}): {suggestion['description']}")

assert len(suggestions) > 0, "应该至少有一个搜索建议"
assert any(search_term in suggestion['title'] for suggestion in suggestions), f"搜索建议中应该包含'{search_term}'"

# 测试搜索结果页面
print("\n测试搜索结果页面...")
search_url = f"{base_url}/service/?q={search_term}"
response = requests.get(search_url)
print(f"搜索结果页面状态码: {response.status_code}")
assert response.status_code == 200

# 解析HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 检查搜索结果标题
search_results_title = soup.find('h2', string=lambda text: f'搜索结果: "{search_term}"' in text if text else False)
assert search_results_title is not None, "搜索结果标题应该存在"
print(f"搜索结果标题: {search_results_title.text.strip()}")

# 检查搜索结果
search_results = soup.find_all('div', class_='service-card')
print(f"找到 {len(search_results)} 个服务卡片")
assert len(search_results) > 0, "应该至少有一个搜索结果"

# 检查服务名称
service_names = [card.find('h3').text.strip() for card in search_results if card.find('h3')]
print("服务名称:", service_names)
assert any(search_term in name for name in service_names), f"搜索结果中应该包含'{search_term}'"

print("\n所有测试通过！搜索功能正常工作。") 