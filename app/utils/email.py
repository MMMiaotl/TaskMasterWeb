from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread
from datetime import datetime

def send_async_email(app, msg):
    """在后台线程中发送邮件"""
    print("进入异步邮件发送函数")
    try:
        with app.app_context():
            print("尝试发送邮件...")
            mail.send(msg)
            print("邮件发送成功")
    except Exception as e:
        print(f"异步发送邮件时出错: {str(e)}")

def send_email(subject, recipients, text_body, html_body, sender=None):
    """发送邮件的通用函数"""
    print(f"===== 准备发送邮件 =====")
    print(f"主题: {subject}")
    print(f"收件人: {recipients}")
    print(f"发件人: {sender or current_app.config['MAIL_DEFAULT_SENDER']}")
    
    app = current_app._get_current_object()
    print(f"邮件服务器配置: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
    print(f"TLS: {app.config['MAIL_USE_TLS']}")
    
    try:
        msg = Message(
            subject=current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
            recipients=recipients,
            body=text_body,
            html=html_body,
            sender=sender or current_app.config['MAIL_DEFAULT_SENDER']
        )
        print(f"邮件对象创建成功")
        
        # 直接发送邮件，不使用线程
        print(f"开始直接发送邮件...")
        mail.send(msg)
        print(f"邮件直接发送成功")
        
        # 不再使用线程发送
        # Thread(target=send_async_email, args=(app, msg)).start()
        # print(f"邮件发送线程已启动")
    except Exception as e:
        print(f"===== 创建或发送邮件时出错: {str(e)} =====")
        import traceback
        traceback.print_exc()
        raise

def send_confirmation_email(user, token):
    """发送邮箱确认邮件"""
    print(f"===== 准备发送确认邮件 =====")
    print(f"用户: {user.username}, 邮箱: {user.email}")
    print(f"令牌: {token}")
    
    try:
        confirm_url = current_app.config['BASE_URL'] + '/auth/confirm/' + token
        print(f"确认URL: {confirm_url}")
        now = datetime.utcnow()
        
        # 纯文本邮件内容
        try:
            text_body = render_template(
                'email/confirm_email.txt',
                user=user,
                confirm_url=confirm_url,
                now=now
            )
            print(f"纯文本邮件模板渲染成功")
        except Exception as e:
            print(f"===== 渲染纯文本邮件模板时出错: {str(e)} =====")
            import traceback
            traceback.print_exc()
            # 使用简单的纯文本内容作为备选
            text_body = f"""
            您好，{user.username}！
            
            感谢您注册海帮账号。请点击以下链接确认您的邮箱地址：
            
            {confirm_url}
            
            此链接将在24小时后失效。
            
            如果您没有注册海帮账号，请忽略此邮件。
            """
            print(f"使用备选纯文本内容")
        
        # HTML邮件内容
        try:
            html_body = render_template(
                'email/confirm_email.html',
                user=user,
                confirm_url=confirm_url,
                now=now
            )
            print(f"HTML邮件模板渲染成功")
        except Exception as e:
            print(f"===== 渲染HTML邮件模板时出错: {str(e)} =====")
            import traceback
            traceback.print_exc()
            # 使用简单的HTML内容作为备选
            html_body = f"""
            <html>
            <body>
                <h2>您好，{user.username}！</h2>
                <p>感谢您注册海帮账号。请点击下面的链接确认您的邮箱地址：</p>
                <p><a href="{confirm_url}">{confirm_url}</a></p>
                <p>此链接将在24小时后失效。</p>
                <p>如果您没有注册海帮账号，请忽略此邮件。</p>
            </body>
            </html>
            """
            print(f"使用备选HTML内容")
        
        # 发送邮件
        print(f"调用send_email函数")
        send_email(
            subject='请确认您的邮箱',
            recipients=[user.email],
            text_body=text_body,
            html_body=html_body
        )
        print(f"send_email函数调用完成")
        
    except Exception as e:
        print(f"===== send_confirmation_email函数中发生异常: {str(e)} =====")
        import traceback
        traceback.print_exc()
        raise 