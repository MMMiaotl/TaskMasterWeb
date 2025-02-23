import os
import click
from flask import current_app
from flask.cli import with_appcontext

@click.command()
@with_appcontext
def compile_translations():
    """编译所有翻译文件"""
    print("开始编译翻译文件...")
    os.system('pybabel compile -d app/translations')
    print("翻译文件编译完成")

@click.command()
@with_appcontext
def update_translations():
    """更新所有翻译文件"""
    print("提取翻译字符串...")
    os.system('pybabel extract -F babel.cfg -o messages.pot .')
    print("更新现有翻译...")
    os.system('pybabel update -i messages.pot -d app/translations')
    print("编译翻译文件...")
    os.system('pybabel compile -d app/translations')
    print("翻译更新完成") 