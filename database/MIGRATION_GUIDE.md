# 数据库迁移指南：MySQL 到 SQL Server

本文档指导您将个人博客系统的数据库从 MySQL 迁移到 SQL Server。

## 迁移概述

- **原数据库**: MySQL 8.0+
- **目标数据库**: SQL Server 2016+（支持 T-SQL）
- **迁移方式**:
  1. 使用 SQL Server 初始化脚本创建新数据库（推荐新项目）
  2. 使用 Flask-Migrate 自动生成迁移脚本（推荐已有项目）
  3. 手动数据迁移（如果已有生产数据）

## 步骤 1：准备工作

### 1.1 安装 ODBC Driver for SQL Server
- 下载并安装 Microsoft ODBC Driver 17 for SQL Server：
  - [官方下载页面](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- 或者使用其他版本（如 ODBC Driver 13、18），但需要相应修改连接字符串中的驱动名称

### 1.2 安装 Python 依赖
```bash
cd backend
pip install -r requirements.txt
```
注意：`requirements.txt` 已更新，用 `pyodbc` 替换了 `PyMySQL`。

### 1.3 配置数据库连接
编辑 `backend/app/config.py`，修改连接字符串：

```python
# 使用 SQL Server 身份验证（示例）
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'mssql+pyodbc://用户名:密码@主机名:端口/数据库名?driver=ODBC+Driver+17+for+SQL+Server'

# 或使用 Windows 身份验证
# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#     'mssql+pyodbc://主机名/数据库名?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server'
```

**参数说明：**
- `用户名`: SQL Server 登录用户名（如 `sa`）
- `密码`: 对应的密码
- `主机名`: SQL Server 实例地址（如 `localhost`、`127.0.0.1` 或远程服务器 IP）
- `端口`: SQL Server 端口（默认 1433）
- `数据库名`: 数据库名称（默认为 `blog_db`）
- `driver`: ODBC 驱动名称，根据安装的版本调整

## 步骤 2：创建 SQL Server 数据库

### 2.1 创建数据库
在 SQL Server Management Studio (SSMS) 或使用 SQL 命令：
```sql
CREATE DATABASE blog_db;
GO
```

### 2.2 设置数据库选项（可选）
```sql
ALTER DATABASE blog_db SET RECOVERY SIMPLE;  -- 简单恢复模式
GO
```

## 步骤 3：初始化数据库表结构

### 方法 A：使用 SQL 脚本（推荐新项目）
1. 使用 SSMS 或 `sqlcmd` 执行初始化脚本：
```bash
# 使用 sqlcmd（需安装 SQL Server 命令行工具）
sqlcmd -S localhost -U sa -P your_password -d blog_db -i database\init_sqlserver.sql
```

2. 或者直接在 SSMS 中打开并执行 `database\init_sqlserver.sql`

**脚本说明：**
- 创建所有表、索引、外键约束
- 添加表注释和列注释
- 创建触发器自动更新 `updated_at` 字段
- 插入示例分类和标签数据

### 方法 B：使用 Flask-Migrate（推荐已有项目）
如果希望使用代码优先的迁移方式：

1. **初始化迁移仓库**：
```bash
cd backend
set FLASK_APP=run.py
flask db init
```

2. **生成初始迁移脚本**：
```bash
flask db migrate -m "Initial migration for SQL Server"
```

3. **应用迁移**：
```bash
flask db upgrade
```

**注意**：如果已有数据表存在（从 MySQL 迁移），需要先清理或调整迁移脚本。

## 步骤 4：测试数据库连接

```bash
cd backend
python test_db_connection.py
```

如果测试成功，您将看到类似以下输出：
```
✓ 数据库连接成功！
✓ 当前数据库: blog_db
✓ 找到 X 个数据表
```

## 步骤 5：数据迁移（如果已有 MySQL 数据）

如果已有生产数据需要从 MySQL 迁移到 SQL Server：

### 5.1 导出 MySQL 数据
```bash
# 导出结构和数据
mysqldump -u root -p blog_db > blog_db_mysql_backup.sql

# 仅导出数据（无结构）
mysqldump -u root -p --no-create-info blog_db > blog_db_data_only.sql
```

### 5.2 转换 SQL 脚本
由于 MySQL 和 SQL Server 语法差异，需要手动转换或使用工具：
- 使用 [MySQL to MSSQL](https://github.com/datacharmer/mysql2mssql) 等转换工具
- 或手动调整以下差异：
  - `AUTO_INCREMENT` → `IDENTITY(1,1)`
  - `CURRENT_TIMESTAMP` → `GETDATE()`
  - `TINYINT(1)` → `BIT`
  - 反引号 `` ` `` → 方括号 `[]`
  - 注释语法

### 5.3 导入到 SQL Server
```bash
# 使用 sqlcmd
sqlcmd -S localhost -U sa -P your_password -d blog_db -i converted_data.sql
```

## 步骤 6：启动应用

### 6.1 启动后端服务
```bash
cd backend
python run.py
```

### 6.2 验证应用运行
访问 `http://localhost:5000` 查看 API 状态。

## 故障排除

### 常见问题 1：连接失败
**错误信息**：`[ODBC Driver 17 for SQL Server]TCP Provider: No connection could be made...`

**解决方案**：
1. 确保 SQL Server 服务正在运行
2. 启用 TCP/IP 协议：
   - 打开 SQL Server Configuration Manager
   - 展开 "SQL Server Network Configuration"
   - 启用 "TCP/IP" 协议
   - 重启 SQL Server 服务
3. 检查防火墙设置，确保端口 1433 开放

### 常见问题 2：身份验证失败
**错误信息**：`Login failed for user 'sa'`

**解决方案**：
1. 确保 SQL Server 身份验证模式已启用（混合模式）
2. 检查 sa 账户是否启用和密码是否正确
3. 或者改用 Windows 身份验证

### 常见问题 3：ODBC 驱动未找到
**错误信息**：`Data source name not found and no default driver specified`

**解决方案**：
1. 确认 ODBC Driver for SQL Server 已安装
2. 检查连接字符串中的驱动名称是否正确
3. 使用 ODBC 数据源管理器验证驱动

### 常见问题 4：数据类型不兼容
**错误信息**：`Incorrect syntax near 'TEXT'`

**解决方案**：
- SQL Server 中 `TEXT` 类型已弃用，但脚本中仍使用以保持兼容性
- 如果遇到问题，可将 `TEXT` 改为 `VARCHAR(MAX)`

## 后续维护

### 使用 Flask-Migrate 进行数据库变更
```bash
# 生成新的迁移脚本（修改模型后）
flask db migrate -m "描述变更内容"

# 应用迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

### 备份数据库
```sql
-- 完整备份
BACKUP DATABASE blog_db TO DISK = 'C:\backup\blog_db.bak';
```

## 参考资源

- [SQL Server 官方文档](https://docs.microsoft.com/en-us/sql/sql-server/)
- [SQLAlchemy 与 SQL Server](https://docs.sqlalchemy.org/en/14/dialects/mssql.html)
- [pyodbc 文档](https://github.com/mkleehammer/pyodbc/wiki)
- [Flask-Migrate 文档](https://flask-migrate.readthedocs.io/)

---

**完成迁移后**，您的应用已成功切换到 SQL Server 数据库。如有问题，请参考上述故障排除步骤或查阅相关文档。