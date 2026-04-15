"""
应用启动文件
"""
from app import create_app
from app.config import config

app = create_app(config['development'])

if __name__ == '__main__':
    print("=" * 50)
    print("Flask论坛后端服务启动中...")
    print("=" * 50)
    print("服务地址: http://localhost:5000")
    print("API地址: http://localhost:5000/api")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)

