# SQL Server 快速开始指南

本文档指导您快速启动个人博客系统在 SQL Server 数据库上。

## 当前状态检查

### 1. 测试数据库连接
```bash
cd backend
python test_db_connection.py
```

如果看到以下输出，说明连接正常但表可能为空：
```
✓ 数据库连接成功！
✓ 当前数据库: blog_db
⚠ 未找到数据表 或 找到 0 个数据表
```

### 2. 检查表结构
如果您已经通过某种方式创建了表但数据为空，请继续下一步。

## 解决方案：插入示例数据

您有以下几种方式插入示例数据：

### 方法 A：使用 Python 脚本（推荐）
```bash
cd backend

# 运行批处理文件（Windows）
insert_data.bat

# 或直接运行 Python 脚本
python insert_sample_data.py
```

### 方法 B：使用 SQL 脚本
```bash
# 使用 sqlcmd 执行插入脚本
sqlcmd -S localhost -U sa -P 893779731 -d blog_db -i database\insert_sample_data.sql

# 或重新执行完整初始化脚本（会删除并重建所有表）
sqlcmd -S localhost -U sa -P 893779731 -d blog_db -i database\init_sqlserver.sql
```

### 方法 C：手动创建数据

如果以上方法都不适用，您可以手动创建数据：

1. **打开 SQL Server Management Studio (SSMS)**
2. **连接到您的 SQL Server 实例**
3. **选择 blog_db 数据库**
4. **执行以下 SQL 语句**：

```sql
-- 插入分类
INSERT INTO categories (name, slug, description, [order]) VALUES
('技术分享', 'tech', '技术相关的文章', 1),
('生活随笔', 'life', '生活感悟和随笔', 2),
('学习笔记', 'study', '学习过程中的笔记', 3),
('项目经验', 'project', '项目开发经验分享', 4);

-- 插入标签
INSERT INTO tags (name, slug, color) VALUES
('Python', 'python', '#3776ab'),
('Vue.js', 'vuejs', '#4fc08d'),
('Flask', 'flask', '#000000'),
('MySQL', 'mysql', '#00758f'),
('前端开发', 'frontend', '#61dafb'),
('后端开发', 'backend', '#f7df1e');
```

## 验证数据插入

运行测试脚本验证数据：
```bash
cd backend
python test_db_connection.py
```

成功输出应包含：
```
✓ 找到 6 个数据表
✓ 分类表查询成功，当前有 4 条记录
```

## 启动应用

数据插入完成后，启动应用：
```bash
cd backend
python run.py
```

访问 `http://localhost:5000` 查看 API 状态。

## 故障排除

### 问题 1：表不存在
如果表不存在，您需要先创建表结构：

**选项 A：执行完整 SQL 脚本**
```bash
sqlcmd -S localhost -U sa -P 893779731 -d blog_db -i database\init_sqlserver.sql
```

**选项 B：使用 Flask-Migrate**
```bash
cd backend

# 如果 migrations 目录不存在，先初始化
python -m flask db init

# 生成迁移脚本（如果还没有）
python -m flask db migrate -m "Initial tables"

# 应用迁移
python -m flask db upgrade
```

### 问题 2：连接失败
检查 `backend/app/config.py` 中的连接字符串：
```python
SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://sa:893779731@localhost:1433/blog_db?driver=ODBC+Driver+17+for+SQL+Server'
```
请确保：
1. 用户名/密码正确
2. 主机名和端口正确
3. 数据库 `blog_db` 已存在
4. ODBC Driver 已安装

### 问题 3：编码问题（路径包含中文）
如果路径中包含中文字符，建议：
1. 将项目移动到英文路径，如 `C:\projects\blog-system\`
2. 或使用短路径格式

## 下一步

数据插入完成后，您可以：
1. **启动前端**：在 `frontend` 目录运行 `npm run dev`
2. **测试 API**：访问 `http://localhost:5000` 查看可用接口
3. **创建用户**：通过 API 注册新用户
4. **发布文章**：使用创建的用户登录并发布文章

## 快速命令总结

```bash
# 1. 测试数据库连接
cd backend && python test_db_connection.py

# 2. 插入示例数据
python insert_sample_data.py

# 3. 启动应用
python run.py

# 4. 验证 API
curl http://localhost:5000
```

如果仍有问题，请参考详细的 [迁移指南](./MIGRATION_GUIDE.md)。