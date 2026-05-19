# 用户管理模块
from database import fetch_one, fetch_all, execute_query
from auth import hash_password

def add_user(username, password, role='user'):
    existing = fetch_one("SELECT id FROM users WHERE username = %s", (username,))
    if existing:
        return {'success': False, 'message': '用户名已存在'}
    
    password_hash = hash_password(password)
    user_id = execute_query(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
        (username, password_hash, role)
    )
    
    return {'success': True, 'message': '用户添加成功', 'user_id': user_id}

def delete_user(user_id):
    existing = fetch_one("SELECT id FROM users WHERE id = %s", (user_id,))
    if not existing:
        return {'success': False, 'message': '用户不存在'}
    
    execute_query("DELETE FROM users WHERE id = %s", (user_id,))
    return {'success': True, 'message': '用户删除成功'}

def get_all_users():
    return fetch_all(
        "SELECT id, username, role, is_locked, failed_attempts, created_at FROM users ORDER BY id"
    )

def update_user(user_id, new_password=None, role=None):
    existing = fetch_one("SELECT id FROM users WHERE id = %s", (user_id,))
    if not existing:
        return {'success': False, 'message': '用户不存在'}
    
    if new_password:
        password_hash = hash_password(new_password)
        execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
    
    if role:
        execute_query("UPDATE users SET role = %s WHERE id = %s", (role, user_id))
    
    return {'success': True, 'message': '用户信息更新成功'}

def unlock_user(user_id):
    execute_query(
        "UPDATE users SET is_locked = FALSE, failed_attempts = 0 WHERE id = %s",
        (user_id,)
    )
    return {'success': True, 'message': '用户已解锁'}
