from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

API_BASE_URL = "http://3.142.135.28:1605/api/v1"
# PLGI_API_URL = "http://alb-crawl-1821318816.us-east-2.elb.amazonaws.com:3738/api/v1/plgi/crawl"
APP_ID = "app-c"  # 固定应用ID

# 微服务访问接口更新
SEARCH_API_URL = 'http://service.netsage.click:3738/api/v1/plgi/search'
CRAWL_API_URL = 'http://service.netsage.click:3738/api/v1/plgi/crawl'
SEARCH_CRAWL_API_URL = 'http://service.netsage.clickm:3738/api/v1/plgi/search-crawl'

# 用户管理及密钥核实服务更新
USER_MANAGEMENT_URL = 'http://3.142.135.28:1605'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/api-docs')
def api_docs():
    return render_template('api_docs.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    if 'access_token' not in session or 'user_email' not in session:
        return redirect(url_for('login'))
    
    try:
        # 获取用户信息和API Keys
        params = {'email': session['user_email'], 'app_id': APP_ID}
        response = requests.get(f'{API_BASE_URL}/users/me', params=params)
        
        if response.status_code == 200:
            user_data = response.json()
            # 确保有基本的数据结构
            if 'api_keys' not in user_data:
                user_data['api_keys'] = []
            if 'email' not in user_data:
                user_data['email'] = session.get('user_email', 'unknown@example.com')
            
            return render_template('dashboard.html', user_data=user_data, app_id=APP_ID)
        else:
            # 用户不存在时，显示空的仪表盘
            user_data = {
                'email': session.get('user_email', 'unknown@example.com'),
                'api_keys': [],
                'id': None,
                'app_id': APP_ID
            }
            return render_template('dashboard.html', user_data=user_data, app_id=APP_ID)
    except Exception as e:
        print(f"Dashboard error: {e}")
        session.clear()
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/send-code', methods=['POST'])
def send_code():
    data = request.json
    # 确保使用固定的app_id
    data['app_id'] = APP_ID
    response = requests.post(f'{API_BASE_URL}/auth/send-code', json=data)
    return jsonify(response.json()), response.status_code

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    # 确保使用固定的app_id
    data['app_id'] = APP_ID
    response = requests.post(f'{API_BASE_URL}/auth/verify-code', json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        session['access_token'] = response_data['access_token']
        session['user_email'] = data['email']  # 存储用户邮箱
        
        # 检查是否有新创建的API Key
        if response_data.get('is_new_user') and response_data.get('new_api_key'):
            # 将新API Key信息也存储在session中，便于前端显示
            session['new_api_key'] = response_data['new_api_key']
            
    return jsonify(response.json()), response.status_code

@app.route('/api/create-api-key', methods=['POST'])
def create_api_key():
    if 'user_email' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    data['app_id'] = APP_ID  # 确保使用固定的app_id
    
    # 构建查询参数
    params = {'email': session['user_email']}
    
    response = requests.post(f'{API_BASE_URL}/api-keys/create', params=params, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/api/list-api-keys', methods=['GET'])
def list_api_keys():
    if 'user_email' not in session:
        return jsonify({'error': '未登录'}), 401
    
    params = {'email': session['user_email'], 'app_id': APP_ID}
    response = requests.get(f'{API_BASE_URL}/api-keys/list', params=params)
    return jsonify(response.json()), response.status_code

@app.route('/api/verify-api-key/<key>', methods=['POST'])
def verify_api_key(key):
    data = request.json or {}
    params = {'app_id': APP_ID}
    
    response = requests.post(f'{API_BASE_URL}/api-keys/verify/{key}', params=params, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/api/proxy/fetch', methods=['POST'])
def proxy_fetch():
    try:
        request_data = request.json or {}
        
        # 从请求中获取API Key
        api_key = request.headers.get('X-API-Key') or request_data.get('key')
        
        # 如果有API Key，进行验证和扣费
        if api_key:
            verify_data = {'service_type': 'fetch'}  # fetch服务消耗2次
            verify_response = requests.post(
                f'{API_BASE_URL}/api-keys/verify/{api_key}',
                params={'app_id': APP_ID},
                json=verify_data
            )
            
            if verify_response.status_code != 200 or not verify_response.json().get('is_valid'):
                return jsonify({'error': 'API Key验证失败'}), 403
        
        # 调用实际的API服务（直接转发原始请求）
        response = requests.post(CRAWL_API_URL, json=request_data)
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy/search', methods=['POST'])
def proxy_search():
    try:
        request_data = request.json or {}
        
        # 从请求中获取API Key
        api_key = request.headers.get('X-API-Key') or request_data.get('key')
        
        # 如果有API Key，进行验证和扣费
        if api_key:
            verify_data = {'service_type': 'search'}  # search服务消耗1次
            verify_response = requests.post(
                f'{API_BASE_URL}/api-keys/verify/{api_key}',
                params={'app_id': APP_ID},
                json=verify_data
            )
            
            if verify_response.status_code != 200 or not verify_response.json().get('is_valid'):
                return jsonify({'error': 'API Key验证失败'}), 403
        
        # 调用实际的API服务（直接转发原始请求）
        response = requests.post(SEARCH_API_URL, json=request_data)
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy/crawl', methods=['POST'])
def proxy_crawl():
    try:
        request_data = request.json or {}
        
        # 从请求中获取API Key
        api_key = request.headers.get('X-API-Key') or request_data.get('key')
        
        # 暂时不支持重排引擎
        service_type = 'crawl'
        
        # 如果有API Key，进行验证和扣费
        if api_key:
            verify_data = {'service_type': service_type}
            verify_response = requests.post(
                f'{API_BASE_URL}/api-keys/verify/{api_key}',
                params={'app_id': APP_ID},
                json=verify_data
            )
            
            if verify_response.status_code != 200 or not verify_response.json().get('is_valid'):
                return jsonify({'error': 'API Key验证失败'}), 403
        
        # 调用实际的API服务（直接转发原始请求）
        response = requests.post(SEARCH_CRAWL_API_URL, json=request_data)
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/self-delete', methods=['POST'])
def self_delete():
    if 'user_email' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    # 确保使用当前用户的邮箱和固定的app_id
    data['email'] = session['user_email']
    data['app_id'] = APP_ID
    
    # 向后端API发送注销请求
    response = requests.post(f'{API_BASE_URL}/users/self-delete', json=data)
    
    # 如果注销成功，清除session
    if response.status_code == 200:
        session.clear()
    
    return jsonify(response.json()), response.status_code

@app.route('/api/logout', methods=['POST'])
def logout():
    if 'user_email' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        # 调用后端简化登出API
        logout_data = {
            "email": session['user_email'],
            "app_id": APP_ID
        }
        
        logout_response = requests.post(
            f'{API_BASE_URL}/auth/logout-simple',
            json=logout_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # 无论后端API是否成功，都清除本地session
        user_email = session['user_email']
        session.clear()
        
        if logout_response.status_code == 200:
            return jsonify({
                'success': True, 
                'message': '登出成功',
                'email': user_email
            }), 200
        else:
            # 即使后端API失败，本地session已清除，仍然返回成功
            return jsonify({
                'success': True, 
                'message': '本地登出成功，远程登出可能失败',
                'email': user_email
            }), 200
            
    except Exception as e:
        # 出现异常时也清除本地session
        user_email = session.get('user_email', '')
        session.clear()
        return jsonify({
            'success': True, 
            'message': '登出成功',
            'error': str(e)
        }), 200

@app.route('/api/usage-stats', methods=['GET'])
def usage_stats():
    """获取API Key使用统计"""
    if 'user_email' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        # 获取用户API Keys
        params = {'email': session['user_email'], 'app_id': APP_ID}
        response = requests.get(f'{API_BASE_URL}/api-keys/list', params=params)
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': '获取统计失败'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=49150, debug=True)