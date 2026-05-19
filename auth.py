# 认证模块
import hashlib
from database import fetch_one, execute_query
from config import MAX_LOGIN_ATTEMPTS

def hash_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def verify_password(input_password, stored_hash):
    input_hash = hash_password(input_password)
    return input_hash == stored_hash

def authenticate_user(username, password):
    user = fetch_one(
        "SELECT id, username, password_hash, role, is_locked, failed_attempts FROM users WHERE username = %s",
        (username,)
    )
    
    if not user:
        return {'success': False, 'message': '用户名或密码错误', 'permissions': []}
    
    if user['is_locked']:
        return {'success': False, 'message': '账户已锁定，请联系管理员', 'permissions': []}
    
    if not verify_password(password, user['password_hash']):
        new_attempts = user['failed_attempts'] + 1
        if new_attempts >= MAX_LOGIN_ATTEMPTS:
            execute_query(
                "UPDATE users SET failed_attempts = %s, is_locked = TRUE WHERE id = %s",
                (new_attempts, user['id'])
            )
            return {'success': False, 'message': '密码错误次数过多，账户已锁定', 'permissions': []}
        else:
            execute_query(
                "UPDATE users SET failed_attempts = %s WHERE id = %s",
                (new_attempts, user['id'])
            )
            remaining = MAX_LOGIN_ATTEMPTS - new_attempts
            return {'success': False, 'message': f'密码错误，还剩 {remaining} 次机会', 'permissions': []}
    
    execute_query(
        "UPDATE users SET failed_attempts = 0 WHERE id = %s",
        (user['id'],)
    )
    
    permissions = get_user_permissions(user['id'])
    
    return {
        'success': True,
        'message': '登录成功',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        },
        'permissions': permissions
    }

def get_user_permissions(user_id):
    query = """
        SELECT pm.module_code, pm.module_name, ot.op_code, ot.op_name
        FROM user_permissions up
        JOIN permission_modules pm ON up.module_id = pm.id
        JOIN operation_types ot ON up.operation_id = ot.id
        WHERE up.user_id = %s
        ORDER BY pm.module_code, ot.op_code
    """
    rows = fetch_all(query, (user_id,))
    
    permissions = {}
    for row in rows:
        module = row['module_code']
        if module not in permissions:
            permissions[module] = {
                'module_name': row['module_name'],
                'operations': []
            }
        permissions[module]['operations'].append({
            'code': row['op_code'],
            'name': row['op_name']
        })
    
    return permissions
