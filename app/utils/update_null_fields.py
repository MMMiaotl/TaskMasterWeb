from app import create_app, db
from app.models import Task

def update_null_values():
    """将所有任务中的 NULL view_count 更新为 0"""
    app = create_app()
    with app.app_context():
        # 查找所有 view_count 为 NULL 的任务
        tasks_with_null = Task.query.filter(Task.view_count.is_(None)).all()
        
        if not tasks_with_null:
            print("没有找到 view_count 为 NULL 的任务")
            return
        
        print(f"找到 {len(tasks_with_null)} 个 view_count 为 NULL 的任务")
        
        # 更新这些任务
        for task in tasks_with_null:
            task.view_count = 0
            print(f"更新任务 ID: {task.id}, 标题: {task.title}")
        
        # 提交更改
        db.session.commit()
        print("所有 NULL view_count 已更新为 0")

if __name__ == "__main__":
    update_null_values() 