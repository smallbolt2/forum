# API 使用指南

## 为什么使用 API 架构？

### 1. **前后端分离架构的优势**

- ✅ **独立开发**：前端和后端可以同时开发，互不干扰
- ✅ **技术灵活性**：前端可以用 Vue/React，后端可以用 Python/Java/Node.js
- ✅ **易于扩展**：可以开发移动端 App、小程序等，都使用同一个 API
- ✅ **更好的性能**：前端可以独立部署到 CDN，提高加载速度
- ✅ **团队协作**：前端和后端团队可以并行工作

### 2. **API 是什么？**

API（Application Programming Interface）是前后端通信的接口。

- 前端（Vue.js）通过 HTTP 请求调用后端 API
- 后端（Flask）接收请求，处理数据，返回 JSON 格式的响应
- 就像点餐：前端是"点餐员"，后端是"厨房"，API 是"菜单"

---

## 🚀 如何使用？

### 方式一：通过前端界面使用（最简单，推荐）

1. **启动服务**
   ```powershell
   # 终端1：启动后端
   cd backend
   python run.py
   
   # 终端2：启动前端
   cd frontend
   npm run dev
   ```

2. **访问前端页面**
   ```
   http://localhost:5173
   ```

3. **功能操作**
   - 📝 注册账号 → 点击"登录" → 选择"注册"
   - 🔐 登录 → 输入用户名和密码
   - ✍️ 写文章 → 登录后点击"写文章"按钮
   - 📖 查看文章 → 点击文章标题
   - 💬 发表评论 → 在文章详情页底部输入评论
   - 👤 个人中心 → 点击右上角头像 → 个人中心

**前端会自动调用后端 API，您无需关心 API 细节！**

---

### 方式二：直接测试 API（开发调试）

#### 方法1：使用浏览器

直接在浏览器地址栏输入以下 URL：

```
# 获取文章列表
http://localhost:5000/api/posts

# 获取分类列表
http://localhost:5000/api/categories

# 获取标签列表
http://localhost:5000/api/tags

# 获取文章详情（替换1为实际文章ID）
http://localhost:5000/api/posts/1
```

#### 方法2：使用 Postman 或 Apifox（推荐）

1. **下载工具**
   - Postman: https://www.postman.com/downloads/
   - Apifox: https://www.apifox.cn/

2. **测试登录 API**

   **请求方式：** POST  
   **URL：** `http://localhost:5000/api/auth/login`  
   **Headers：**
   ```
   Content-Type: application/json
   ```
   **Body（JSON）：**
   ```json
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```
   **响应示例：**
   ```json
   {
     "code": 200,
     "message": "登录成功",
     "data": {
       "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
       "user": {
         "id": 1,
         "username": "testuser",
         "nickname": "测试用户"
       }
     }
   }
   ```

3. **测试创建文章 API**

   **请求方式：** POST  
   **URL：** `http://localhost:5000/api/posts`  
   **Headers：**
   ```
   Content-Type: application/json
   Authorization: Bearer {你的token}
   ```
   **Body（JSON）：**
   ```json
   {
     "title": "我的第一篇文章",
     "content": "这是文章内容，支持 Markdown 格式",
     "summary": "文章摘要",
     "category_id": 1,
     "tags": [1, 2],
     "status": 1
   }
   ```

#### 方法3：使用 PowerShell 命令行

```powershell
# 获取文章列表
Invoke-RestMethod -Uri "http://localhost:5000/api/posts" -Method Get

# 登录（需要先创建账号）
$body = @{
    username = "testuser"
    password = "123456"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $body -ContentType "application/json"
```

---

## 📋 API 接口列表

### 认证相关

| 接口 | 方法 | 说明 | 需要认证 |
|------|------|------|---------|
| `/api/auth/register` | POST | 用户注册 | ❌ |
| `/api/auth/login` | POST | 用户登录 | ❌ |
| `/api/auth/me` | GET | 获取当前用户信息 | ✅ |

### 文章相关

| 接口 | 方法 | 说明 | 需要认证 |
|------|------|------|---------|
| `/api/posts` | GET | 获取文章列表 | ❌ |
| `/api/posts` | POST | 创建文章 | ✅ |
| `/api/posts/<id>` | GET | 获取文章详情 | ❌ |
| `/api/posts/<id>` | PUT | 更新文章 | ✅ |
| `/api/posts/<id>` | DELETE | 删除文章 | ✅ |
| `/api/posts/<id>/like` | POST | 点赞文章 | ✅ |

### 分类相关

| 接口 | 方法 | 说明 | 需要认证 |
|------|------|------|---------|
| `/api/categories` | GET | 获取分类列表 | ❌ |
| `/api/categories` | POST | 创建分类 | ✅ |

### 标签相关

| 接口 | 方法 | 说明 | 需要认证 |
|------|------|------|---------|
| `/api/tags` | GET | 获取标签列表 | ❌ |
| `/api/tags` | POST | 创建标签 | ✅ |

### 评论相关

| 接口 | 方法 | 说明 | 需要认证 |
|------|------|------|---------|
| `/api/comments` | GET | 获取评论列表 | ❌ |
| `/api/comments` | POST | 创建评论 | ✅ |

### 用户相关

| 接口 | 方法 | 说明 | 需要认证 |
|------|------|------|---------|
| `/api/users/<id>` | GET | 获取用户信息 | ❌ |
| `/api/users/<id>` | PUT | 更新用户信息 | ✅ |

---

## 🔐 认证说明

需要认证的接口需要在请求头中添加 Token：

```
Authorization: Bearer {你的token}
```

获取 Token：
1. 通过 `/api/auth/login` 登录获取
2. 通过 `/api/auth/register` 注册获取

---

## 📝 请求/响应格式

### 请求格式

**GET 请求：** 参数通过 URL 查询字符串传递
```
GET /api/posts?page=1&per_page=10&keyword=搜索关键词
```

**POST/PUT 请求：** 数据通过 JSON Body 传递
```json
{
  "title": "文章标题",
  "content": "文章内容"
}
```

### 响应格式

**成功响应：**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "错误信息"
}
```

---

## 🎯 快速测试示例

### 1. 注册新用户

```bash
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456",
  "nickname": "测试用户"
}
```

### 2. 登录获取 Token

```bash
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "123456"
}
```

### 3. 使用 Token 创建文章

```bash
POST http://localhost:5000/api/posts
Content-Type: application/json
Authorization: Bearer {你的token}

{
  "title": "我的第一篇文章",
  "content": "# 标题\n\n这是内容，支持 **Markdown** 格式",
  "summary": "文章摘要",
  "category_id": 1,
  "tags": [1, 2],
  "status": 1
}
```

### 4. 获取文章列表

```bash
GET http://localhost:5000/api/posts?page=1&per_page=10
```

---

## 💡 常见问题

### Q: 为什么前端访问 `/api/posts` 能正常工作？

**A:** 前端使用了 Vite 代理。在 `frontend/vite.config.js` 中配置了：
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true
  }
}
```

当前端访问 `/api/posts` 时，Vite 会自动转发到 `http://localhost:5000/api/posts`。

### Q: 如何查看 API 的实际请求和响应？

**A:** 
1. 打开浏览器开发者工具（F12）
2. 切换到 "Network"（网络）标签
3. 刷新页面或执行操作
4. 点击请求查看详情

### Q: 可以直接在浏览器访问后端 API 吗？

**A:** 可以！直接访问 `http://localhost:5000/api/posts` 即可。但某些操作（如 POST、PUT）需要认证，建议使用 Postman 等工具。

---

## 📚 更多信息

- 项目文档：查看 `docs/` 目录
- 后端代码：查看 `backend/app/routes/` 目录
- 前端代码：查看 `frontend/src/` 目录

