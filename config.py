# 应用配置文件

import os

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'user_permission_db'),
    'charset': 'utf8mb4'
}

# Flask 配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
SESSION_TIMEOUT = 3600  # 会话超时时间（秒）

# 登录失败锁定配置
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 1800  # 锁定时间 30 分钟

# 功能模块定义
MODULES = {
    'entry': '录入模块',
    'query': '查询模块',
    'modify': '修改模块',
    'print': '打印模块'
}

# 操作类型定义
OPERATIONS = {
    'create': '新增',
    'read': '查看',
    'update': '修改',
    'delete': '删除',
    'print': '打印'
}
