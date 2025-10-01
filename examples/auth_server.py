"""
简易认证服务器（用于测试）

这是一个最小化的 Flask 服务器，用于测试混合安全方案
生产环境应使用更完善的后端框架
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)
CORS(app)  # 允许跨域

# 配置
SECRET_KEY = "your-secret-key-change-this-in-production"
TOKEN_EXPIRY_HOURS = 1

# 模拟用户数据库
USERS_DB = {
    'admin': {
        'password_hash': hashlib.sha256('Admin123!'.encode()).hexdigest(),
        'email': 'admin@example.com',
        'permissions': ['view_charts', 'manage_users']
    },
    'testuser': {
        'password_hash': hashlib.sha256('TestPassword123!'.encode()).hexdigest(),
        'email': 'test@example.com',
        'permissions': ['view_charts']
    }
}


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        device_fingerprint = data.get('device_fingerprint')
        app_version = data.get('app_version', 'unknown')

        # 验证输入
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400

        # 验证用户
        user = USERS_DB.get(username)
        if not user:
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            }), 401

        # 验证密码
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password_hash'] != password_hash:
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            }), 401

        # 生成 JWT Token
        token = jwt.encode({
            'username': username,
            'device_fingerprint': device_fingerprint,
            'app_version': app_version,
            'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        }, SECRET_KEY, algorithm='HS256')

        # 记录登录（生产环境应写入数据库）
        print(f"[{datetime.now()}] Login: {username} from device {device_fingerprint[:16]}...")

        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'username': username,
                'email': user['email'],
                'permissions': user['permissions']
            }
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500


@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """验证 Token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'valid': False, 'error': 'Missing token'}), 401

        token = auth_header.split(' ')[1]

        # 验证 Token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return jsonify({
                'valid': True,
                'username': payload.get('username')
            })
        except jwt.ExpiredSignatureError:
            return jsonify({'valid': False, 'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'valid': False, 'error': 'Invalid token'}), 401

    except Exception as e:
        print(f"Verify error: {e}")
        return jsonify({'valid': False, 'error': 'Server error'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False}), 401

        # 生产环境应将 Token 加入黑名单
        print(f"[{datetime.now()}] Logout")

        return jsonify({'success': True})

    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({'success': False}), 500


@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取用户信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing token'}), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            username = payload.get('username')

            user = USERS_DB.get(username)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            return jsonify({
                'username': username,
                'email': user['email'],
                'permissions': user['permissions']
            })

        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    except Exception as e:
        print(f"Get user info error: {e}")
        return jsonify({'error': 'Server error'}), 500


def main():
    """启动服务器"""
    print("\n" + "=" * 60)
    print("简易认证服务器")
    print("=" * 60)
    print("\n测试账号：")
    print("  用户名: testuser")
    print("  密码: TestPassword123!")
    print("\n  用户名: admin")
    print("  密码: Admin123!")
    print("\n服务器地址: http://localhost:8000")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=8000, debug=True)


if __name__ == '__main__':
    # 需要先安装依赖：
    # pip install flask flask-cors pyjwt
    main()
