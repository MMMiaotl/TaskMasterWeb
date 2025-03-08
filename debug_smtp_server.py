import asyncio
from aiosmtpd.controller import Controller

class DebugHandler:
    async def handle_DATA(self, server, session, envelope):
        print('收到邮件:')
        print(f'发件人: {envelope.mail_from}')
        print(f'收件人: {envelope.rcpt_tos}')
        print(f'内容长度: {len(envelope.content)}')
        print(f'内容: {envelope.content.decode("utf8", errors="replace")}')
        print('=' * 50)
        return '250 OK'

async def amain():
    controller = Controller(DebugHandler(), hostname='localhost', port=1025)
    controller.start()
    print(f'调试邮件服务器运行在 localhost:1025')
    
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(amain())