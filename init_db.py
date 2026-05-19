# 数据库初始化脚本
import pymysql
from config import DB_CONFIG

def init_database():
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset=DB_CONFIG['charset']
    )
    
    try:
        cursor = conn.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(32) NOT NULL,
                role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_locked BOOLEAN DEFAULT FALSE,
                failed_attempts INT DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permission_modules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                module_code VARCHAR(50) UNIQUE NOT NULL,
                module_name VARCHAR(100) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_types (
                id INT AUTO_INCREMENT PRIMARY KEY,
                op_code VARCHAR(50) UNIQUE NOT NULL,
                op_name VARCHAR(100) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                module_id INT NOT NULL,
                operation_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (module_id) REFERENCES permission_modules(id) ON DELETE CASCADE,
                FOREIGN KEY (operation_id) REFERENCES operation_types(id) ON DELETE CASCADE,
                UNIQUE KEY unique_permission (user_id, module_id, operation_id)
            )
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO permission_modules (module_code, module_name) VALUES
                ('entry', '录入模块'),
                ('query', '查询模块'),
                ('modify', '修改模块'),
                ('print', '打印模块')
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO operation_types (op_code, op_name) VALUES
                ('create', '新增'),
                ('read', '查看'),
                ('update', '修改'),
                ('delete', '删除'),
                ('print', '打印')
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO users (username, password_hash, role) VALUES
                ('admin', '0192023a7bbd73250516f069df18b500', 'admin')
        """)
        
        conn.commit()
        print("数据库初始化成功！")
        print("默认管理员账户: admin / admin123")
        
    except pymysql.Error as e:
        print(f"数据库初始化失败: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
