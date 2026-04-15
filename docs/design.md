# 系统设计文档

## 1. 系统架构设计

### 1.1 总体架构

本项目采用前后端分离架构，系统总体架构如下：

```
┌─────────────────┐
│   前端应用      │
│  (Vue.js + Vite)│
└────────┬────────┘
         │ HTTP/HTTPS
         │ RESTful API
┌────────▼────────┐
│   后端服务      │
│  (Flask)        │
└────────┬────────┘
         │
┌────────▼──────┐
│  MySQL        │
│  数据库       │
└───────────────┘
```

### 1.2 架构特点

- **前后端分离**: 前端和后端独立开发、部署和扩展
- **RESTful API**: 统一的API接口规范
- **分层架构**: 控制器层、服务层、数据访问层清晰分离
- **模块化设计**: 功能模块化，便于维护和扩展

### 1.3 技术架构

#### 前端架构
- **框架**: Vue.js 3.x (Composition API)
- **构建工具**: Vite
- **UI组件**: Element Plus
- **路由**: Vue Router
- **HTTP客户端**: Axios

#### 后端架构
- **框架**: Flask 2.3.x
- **ORM**: SQLAlchemy
- **数据库**: MySQL 8.0+
- **跨域**: Flask-CORS

## 2. 模块设计

### 2.1 前端模块

```
frontend/
├── src/
│   ├── views/          # 页面视图
│   │   ├── Home.vue    # 首页
│   │   └── PostDetail.vue # 文章详情页
│   ├── components/     # 公共组件
│   │   ├── ArticleItem.vue
│   │   ├── WritePostDialog.vue
│   │   ├── CommentForm.vue
│   │   └── CommentItem.vue
│   ├── router/         # 路由配置
│   └── utils/          # 工具函数
│       └── request.js  # HTTP请求封装
```

### 2.2 后端模块

```
backend/
├── app/
│   ├── __init__.py     # Flask应用初始化
│   ├── config.py       # 配置文件
│   ├── models/         # 数据模型
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   └── comment.py
│   └── routes/          # 路由
│       ├── posts.py
│       ├── categories.py
│       ├── tags.py
│       ├── comments.py
│       └── users.py
```

## 3. 数据库设计

### 3.1 数据库设计原则

- **规范化**: 遵循数据库三大范式
- **索引优化**: 为常用查询字段建立索引
- **字符集**: 使用utf8mb4支持emoji
- **字段命名**: 使用下划线命名法
- **时间字段**: 统一使用datetime类型

### 3.2 表设计

#### 用户表 (users)
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- password_hash: 密码哈希
- nickname: 昵称
- avatar: 头像URL
- bio: 个人简介
- role: 角色
- status: 状态
- created_at: 创建时间
- updated_at: 更新时间

#### 文章表 (posts)
- id: 主键
- title: 标题
- content: 内容
- summary: 摘要
- cover_image: 封面图片URL
- author_id: 作者ID（外键）
- category_id: 分类ID（外键）
- status: 状态（草稿/已发布/已删除）
- views: 浏览量
- likes: 点赞数
- is_top: 是否置顶
- created_at: 创建时间
- updated_at: 更新时间
- published_at: 发布时间

#### 分类表 (categories)
- id: 主键
- name: 分类名称（唯一）
- slug: 分类别名（唯一）
- description: 分类描述
- order: 排序
- created_at: 创建时间
- updated_at: 更新时间

#### 标签表 (tags)
- id: 主键
- name: 标签名称（唯一）
- slug: 标签别名（唯一）
- color: 标签颜色
- created_at: 创建时间
- updated_at: 更新时间

#### 评论表 (comments)
- id: 主键
- content: 评论内容
- post_id: 文章ID（外键）
- user_id: 用户ID（外键）
- parent_id: 父评论ID（外键，用于回复）
- status: 状态
- created_at: 创建时间
- updated_at: 更新时间

#### 文章-标签关联表 (post_tags)
- post_id: 文章ID（外键）
- tag_id: 标签ID（外键）
- 联合主键 (post_id, tag_id)

## 4. API设计

### 4.1 RESTful API规范

- **URL设计**: 使用名词，不使用动词
- **HTTP方法**: GET（查询）、POST（创建）、PUT（更新）、DELETE（删除）
- **状态码**: 200（成功）、400（请求错误）、401（未授权）、404（未找到）、500（服务器错误）
- **响应格式**: 统一使用JSON格式

### 4.2 API接口

#### 文章相关API
- `GET /api/posts` - 获取文章列表
- `GET /api/posts/<id>` - 获取文章详情
- `POST /api/posts` - 创建文章
- `PUT /api/posts/<id>` - 更新文章
- `DELETE /api/posts/<id>` - 删除文章
- `POST /api/posts/<id>/like` - 点赞文章

#### 分类相关API
- `GET /api/categories` - 获取分类列表
- `POST /api/categories` - 创建分类

#### 标签相关API
- `GET /api/tags` - 获取标签列表
- `POST /api/tags` - 创建标签

#### 评论相关API
- `GET /api/comments` - 获取评论列表
- `POST /api/comments` - 创建评论

### 4.3 响应格式

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

## 5. 前端设计

### 5.1 页面设计

- **首页**: 文章列表、分类导航、标签云、搜索框
- **文章详情页**: 文章内容、评论列表、评论表单

### 5.2 组件设计

- **ArticleItem**: 文章列表项组件
- **WritePostDialog**: 写文章对话框组件
- **CommentForm**: 评论表单组件
- **CommentItem**: 评论项组件

### 5.3 UI设计原则

- **一致性**: 保持界面风格一致
- **易用性**: 界面简洁易用
- **美观性**: 符合现代UI设计趋势
- **响应式**: 适配PC端和移动端

## 6. 后端设计

### 6.1 分层架构

```
Routes层 (路由)
    ↓
Models层 (数据模型)
    ↓
Database层 (数据库)
```

### 6.2 设计模式

- **MVC模式**: 模型-视图-控制器
- **工厂模式**: 应用工厂函数
- **单例模式**: 数据库连接等

### 6.3 异常处理

- 统一异常处理机制
- 返回友好的错误信息

## 7. 安全设计

### 7.1 数据安全

- 防止SQL注入：使用ORM参数化查询
- 防止XSS攻击：对用户输入进行转义
- 跨域配置：配置CORS允许的源

### 7.2 密码安全

- 使用Werkzeug加密存储密码
- 密码长度至少6位

---

**注意**: 本文档为示例设计文档，实际项目中应根据具体需求进行详细设计。

