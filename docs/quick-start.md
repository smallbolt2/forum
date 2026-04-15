# 快速开始指南

## 前置准备

### 1. 安装开发工具

#### 必需工具
- **Python 3.8+**: [下载地址](https://www.python.org/downloads/)
- **Node.js 16+**: [下载地址](https://nodejs.org/)
- **MySQL 8.0+**: [下载地址](https://dev.mysql.com/downloads/)
- **Git**: [下载地址](https://git-scm.com/downloads)

#### IDE推荐
- **Visual Studio Code**: [下载地址](https://code.visualstudio.com/)
- **PyCharm**: [下载地址](https://www.jetbrains.com/pycharm/)

### 2. 验证安装

```bash
# 检查Python版本
python --version

# 检查Node.js版本
node -v
npm -v

# 检查MySQL版本
mysql --version

# 检查Git版本
git --version
```

## 环境配置

### 1. 数据库配置

#### 创建数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 执行初始化脚本
mysql -u root -p blog_db < database/init.sql
```

### 2. 后端环境配置

#### 创建虚拟环境

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 安装依赖

```bash
pip install -r requirements.txt

# 如果下载慢，可以使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 配置数据库连接

编辑 `backend/app/config.py`，修改数据库连接信息：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:你的密码@localhost:3306/blog_db?charset=utf8mb4'
```

### 3. 前端环境配置

#### 安装依赖

```bash
cd frontend
npm install
```

#### 配置国内镜像（可选，加速下载）

```bash
npm config set registry https://registry.npmmirror.com
```

## 启动项目

### 1. 启动后端服务

```bash
cd backend

# 激活虚拟环境（如果还没激活）
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 启动Flask服务
python run.py
```

后端服务运行在: `http://localhost:5000`

### 2. 启动前端服务

打开新的终端窗口：

```bash
cd frontend
npm run dev
```

前端服务运行在: `http://localhost:5173`

## 验证项目运行

### 1. 测试后端

打开浏览器访问：
```
http://localhost:5000/api/posts
```

应该返回JSON格式的文章列表。

### 2. 测试前端

1. 打开浏览器访问 `http://localhost:5173`
2. 应该能看到博客首页
3. 点击文章可以查看详情
4. 可以尝试写文章和评论功能

## 常见问题

### 1. 后端启动失败

**问题**: 端口被占用
**解决**: 修改 `backend/run.py` 中的端口号

**问题**: 数据库连接失败
**解决**: 
- 检查MySQL服务是否启动
- 检查数据库连接信息是否正确
- 检查数据库是否已创建

**问题**: 依赖安装失败
**解决**: 
- 检查Python版本是否符合要求（3.8+）
- 使用国内镜像源
- 升级pip：`pip install --upgrade pip`

### 2. 前端启动失败

**问题**: 端口被占用
**解决**: 修改 `frontend/vite.config.js` 中的 `server.port`

**问题**: 依赖安装失败
**解决**: 
- 清除缓存：`npm cache clean --force`
- 删除 `node_modules` 和 `package-lock.json`，重新安装
- 使用国内镜像源

**问题**: 后端API请求失败
**解决**: 
- 检查后端服务是否启动
- 检查 `frontend/src/utils/request.js` 中的 `baseURL` 配置
- 检查后端CORS配置

### 3. 数据库问题

**问题**: 字符编码问题
**解决**: 确保数据库使用 `utf8mb4` 字符集

**问题**: 表不存在
**解决**: 执行 `database/init.sql` 初始化脚本

## 下一步

1. 阅读项目文档
2. 查看代码结构
3. 开始开发功能
4. 添加用户认证功能

---

祝你开发顺利！

