# 主应用入口
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from auth import authenticate_user
from user_mgmt import add_user, delete_user, get_all_users, update_user, unlock_user
from permission_mgmt import get_modules, get_operations, assign_permission, remove_permission, get_user_permissions_detail, remove_all_user_permissions
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '请输入用户名和密码'})
        
        result = authenticate_user(username, password)
        
        if result['success']:
            session['user_id'] = result['user']['id']
            session['username'] = result['user']['username']
            session['role'] = result['user']['role']
            session['permissions'] = result['permissions']
            return jsonify(result)
        else:
            return jsonify(result)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    permissions = session.get('permissions', {})
    return render_template('dashboard.html', username=session['username'], permissions=permissions)

@app.route('/admin')
@login_required
def admin():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    return render_template('admin.html', username=session['username'])

@app.route('/api/users', methods=['GET'])
@login_required
def api_get_users():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    users = get_all_users()
    return jsonify({'success': True, 'users': users})

@app.route('/api/users', methods=['POST'])
@login_required
def api_add_user():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    result = add_user(username, password, role)
    return jsonify(result)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def api_delete_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    result = delete_user(user_id)
    return jsonify(result)

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def api_update_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    data = request.json
    new_password = data.get('password')
    role = data.get('role')
    
    result = update_user(user_id, new_password, role)
    return jsonify(result)

@app.route('/api/users/<int:user_id>/unlock', methods=['POST'])
@login_required
def api_unlock_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    result = unlock_user(user_id)
    return jsonify(result)

@app.route('/api/modules', methods=['GET'])
@login_required
def api_get_modules():
    modules = get_modules()
    return jsonify({'success': True, 'modules': modules})

@app.route('/api/operations', methods=['GET'])
@login_required
def api_get_operations():
    operations = get_operations()
    return jsonify({'success': True, 'operations': operations})

@app.route('/api/users/<int:user_id>/permissions', methods=['POST'])
@login_required
def api_assign_permission(user_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    data = request.json
    module_code = data.get('module')
    op_codes = data.get('operations', [])
    
    if not module_code:
        return jsonify({'success': False, 'message': '模块不能为空'})
    
    result = assign_permission(user_id, module_code, op_codes)
    return jsonify(result)

@app.route('/api/users/<int:user_id>/permissions', methods=['DELETE'])
@login_required
def api_remove_permission(user_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    data = request.json
    module_code = data.get('module')
    op_codes = data.get('operations', [])
    
    result = remove_permission(user_id, module_code, op_codes)
    return jsonify(result)

@app.route('/api/users/<int:user_id>/permissions', methods=['GET'])
@login_required
def api_get_user_permissions(user_id):
    permissions = get_user_permissions_detail(user_id)
    return jsonify({'success': True, 'permissions': permissions})

@app.route('/api/users/<int:user_id>/permissions/all', methods=['DELETE'])
@login_required
def api_remove_all_permissions(user_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    result = remove_all_user_permissions(user_id)
    return jsonify(result)

@app.route('/api/my-permissions')
@login_required
def api_my_permissions():
    return jsonify({'success': True, 'permissions': session.get('permissions', {})})

@app.route('/api/session')
@login_required
def api_session():
    return jsonify({
        'success': True,
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
