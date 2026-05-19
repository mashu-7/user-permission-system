# 权限管理模块
from database import fetch_one, fetch_all, execute_query

def get_modules():
    return fetch_all("SELECT id, module_code, module_name FROM permission_modules ORDER BY id")

def get_operations():
    return fetch_all("SELECT id, op_code, op_name FROM operation_types ORDER BY id")

def assign_permission(user_id, module_code, op_codes):
    module = fetch_one("SELECT id FROM permission_modules WHERE module_code = %s", (module_code,))
    if not module:
        return {'success': False, 'message': '模块不存在'}
    
    module_id = module['id']
    
    for op_code in op_codes:
        operation = fetch_one("SELECT id FROM operation_types WHERE op_code = %s", (op_code,))
        if not operation:
            continue
        
        operation_id = operation['id']
        existing = fetch_one(
            "SELECT id FROM user_permissions WHERE user_id = %s AND module_id = %s AND operation_id = %s",
            (user_id, module_id, operation_id)
        )
        if not existing:
            execute_query(
                "INSERT INTO user_permissions (user_id, module_id, operation_id) VALUES (%s, %s, %s)",
                (user_id, module_id, operation_id)
            )
    
    return {'success': True, 'message': '权限分配成功'}

def remove_permission(user_id, module_code, op_codes):
    module = fetch_one("SELECT id FROM permission_modules WHERE module_code = %s", (module_code,))
    if not module:
        return {'success': False, 'message': '模块不存在'}
    
    module_id = module['id']
    for op_code in op_codes:
        operation = fetch_one("SELECT id FROM operation_types WHERE op_code = %s", (op_code,))
        if not operation:
            continue
        
        operation_id = operation['id']
        execute_query(
            "DELETE FROM user_permissions WHERE user_id = %s AND module_id = %s AND operation_id = %s",
            (user_id, module_id, operation_id)
        )
    
    return {'success': True, 'message': '权限删除成功'}

def get_user_permissions_detail(user_id):
    query = """
        SELECT pm.module_code, pm.module_name, ot.op_code, ot.op_name
        FROM user_permissions up
        JOIN permission_modules pm ON up.module_id = pm.id
        JOIN operation_types ot ON up.operation_id = ot.id
        WHERE up.user_id = %s
        ORDER BY pm.module_code, ot.op_code
    """
    return fetch_all(query, (user_id,))

def remove_all_user_permissions(user_id):
    execute_query("DELETE FROM user_permissions WHERE user_id = %s", (user_id,))
    return {'success': True, 'message': '所有权限已删除'}
