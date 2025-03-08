import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# 邮件配置
MAIL_SERVER = 'localhost'
MAIL_PORT = 1025
SENDER = 'noreply@haibang.com'
RECIPIENT = 'test@example.com'
SUBJECT = '[海帮] 请确认您的邮箱'

# 用户信息
username = "测试用户"
token = "test_token_123456789"
confirm_url = f"http://localhost:5000/auth/confirm/{token}"
now = datetime.utcnow()

# 创建HTML内容
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>确认您的海帮账号</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 24px;
            font-weight: bold;
            color: #0066cc;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
        }}
        .button {{
            display: inline-block;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">海帮</div>
    </div>
    
    <div class="content">
        <h2>您好，{username}！</h2>
        
        <p>感谢您注册海帮账号。请点击下面的按钮确认您的邮箱地址：</p>
        
        <div style="text-align: center;">
            <a href="{confirm_url}" class="button">确认邮箱</a>
        </div>
        
        <p>或者，您可以复制以下链接到浏览器地址栏：</p>
        <p>{confirm_url}</p>
        
        <p>此链接将在24小时后失效。</p>
        
        <p>如果您没有注册海帮账号，请忽略此邮件。</p>
    </div>
    
    <div class="footer">
        <p>此邮件由系统自动发送，请勿回复。</p>
        <p>&copy; {now.year} 海帮 - 您身边的专业服务平台</p>
    </div>
</body>
</html>
"""

# 创建纯文本内容
text_content = f"""
您好，{username}！

感谢您注册海帮账号。请点击以下链接确认您的邮箱地址：

{confirm_url}

此链接将在24小时后失效。

如果您没有注册海帮账号，请忽略此邮件。

此邮件由系统自动发送，请勿回复。

© {now.year} 海帮 - 您身边的专业服务平台
"""

# 创建多部分邮件
msg = MIMEMultipart('alternative')
msg['Subject'] = SUBJECT
msg['From'] = SENDER
msg['To'] = RECIPIENT

# 添加纯文本和HTML内容
part1 = MIMEText(text_content, 'plain', 'utf-8')
part2 = MIMEText(html_content, 'html', 'utf-8')

# 先添加纯文本部分，再添加HTML部分
# 这样支持HTML的邮件客户端会显示HTML内容，不支持的会显示纯文本内容
msg.attach(part1)
msg.attach(part2)

# 发送邮件
try:
    print(f"连接到SMTP服务器 {MAIL_SERVER}:{MAIL_PORT}...")
    with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
        print("发送邮件...")
        server.send_message(msg)
        print("邮件发送成功！")
        print(f"收件人: {RECIPIENT}")
        print(f"主题: {SUBJECT}")
        print("内容包含HTML和纯文本格式")
except Exception as e:
    print(f"发送邮件时出错: {str(e)}")