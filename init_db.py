#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import pymysql
import sys

# 数据库连接配置
DB_CONFIG = {
    'host': 'unraid.wjtjyy.top',
    'port': 3306,
    'user': 'root',
    'password': '19860515Cb!',
    'charset': 'utf8mb4'
}

# SQL语句列表（逐条执行）
SQL_STATEMENTS = [
    # 创建数据库
    "CREATE DATABASE IF NOT EXISTS stock_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",

    # 使用数据库
    "USE stock_monitor",

    # 用户表
    """CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
        password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
        email VARCHAR(100) COMMENT '邮箱',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        last_login DATETIME COMMENT '最后登录时间',
        INDEX idx_username (username)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表'""",

    # 股票基本信息表
    """CREATE TABLE IF NOT EXISTS stocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(10) UNIQUE NOT NULL COMMENT '股票代码',
        name VARCHAR(50) NOT NULL COMMENT '股票名称',
        market VARCHAR(10) COMMENT '市场: SZ/SH',
        industry VARCHAR(50) COMMENT '行业',
        full_code VARCHAR(20) COMMENT '完整代码: 000001.SZ',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_code (code),
        INDEX idx_name (name),
        INDEX idx_full_code (full_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基本信息'""",

    # 监测配置表
    """CREATE TABLE IF NOT EXISTS monitors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        stock_id INT NOT NULL,
        price_min DECIMAL(10,2) COMMENT '最低价预警',
        price_max DECIMAL(10,2) COMMENT '最高价预警',
        rise_threshold DECIMAL(5,2) COMMENT '涨幅阈值(%)',
        fall_threshold DECIMAL(5,2) COMMENT '跌幅阈值(%)',
        is_active TINYINT(1) DEFAULT 1 COMMENT '是否启用',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_user_stock (user_id, stock_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
        INDEX idx_user_active (user_id, is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监测配置'""",

    # 股票日线数据表
    """CREATE TABLE IF NOT EXISTS stock_daily (
        id INT AUTO_INCREMENT PRIMARY KEY,
        stock_id INT NOT NULL,
        trade_date DATE NOT NULL COMMENT '交易日期',
        open DECIMAL(10,2) COMMENT '开盘价',
        high DECIMAL(10,2) COMMENT '最高价',
        low DECIMAL(10,2) COMMENT '最低价',
        close DECIMAL(10,2) COMMENT '收盘价',
        volume BIGINT COMMENT '成交量',
        amount DECIMAL(20,2) COMMENT '成交额',
        turnover_rate DECIMAL(5,2) COMMENT '换手率',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_stock_date (stock_id, trade_date),
        FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
        INDEX idx_trade_date (trade_date),
        INDEX idx_stock_date (stock_id, trade_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票日线数据'""",

    # 通知记录表
    """CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        stock_id INT NOT NULL,
        monitor_id INT NOT NULL,
        type VARCHAR(20) COMMENT '类型: price_min/price_max/rise/fall',
        content TEXT COMMENT '通知内容',
        is_sent TINYINT(1) DEFAULT 0 COMMENT '是否已发送',
        sent_at DATETIME COMMENT '发送时间',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
        FOREIGN KEY (monitor_id) REFERENCES monitors(id) ON DELETE CASCADE,
        INDEX idx_user_created (user_id, created_at),
        INDEX idx_is_sent (is_sent)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知记录'""",

    # 通知配置表
    """CREATE TABLE IF NOT EXISTS notification_configs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL UNIQUE,
        api_url VARCHAR(500) COMMENT 'Webhook/API地址',
        api_headers JSON COMMENT '请求头配置',
        api_method VARCHAR(10) DEFAULT 'POST' COMMENT '请求方法',
        api_body_template TEXT COMMENT '请求体模板',
        is_enabled TINYINT(1) DEFAULT 1 COMMENT '是否启用',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知配置'""",

    # 系统缓存表
    """CREATE TABLE IF NOT EXISTS system_cache (
        cache_key VARCHAR(100) PRIMARY KEY,
        cache_value JSON COMMENT '缓存值',
        expire_at DATETIME COMMENT '过期时间',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_expire (expire_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统缓存'""",

    # 插入默认管理员账号: admin / admin
    """INSERT INTO users (username, password_hash, email) VALUES
    ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', 'admin@example.com')
    ON DUPLICATE KEY UPDATE username=username""",
]

def init_database():
    """初始化数据库"""
    print("=" * 50)
    print("股票监测系统 - 数据库初始化")
    print("=" * 50)
    print(f"\n连接信息:")
    print(f"  主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  用户: {DB_CONFIG['user']}")
    print()

    try:
        # 连接MySQL服务器
        print("正在连接MySQL服务器...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print("✓ 连接成功!\n")

        # 逐条执行SQL
        print("正在执行数据库初始化...")
        total = len(SQL_STATEMENTS)

        for i, sql in enumerate(SQL_STATEMENTS, 1):
            try:
                cursor.execute(sql)
                # 只对INSERT语句commit
                if sql.strip().upper().startswith('INSERT'):
                    connection.commit()
                print(f"  [{i}/{total}] ✓")
            except Exception as e:
                # 如果是表已存在或数据已存在，忽略错误
                if 'Duplicate' in str(e) or 'already exists' in str(e).lower():
                    print(f"  [{i}/{total}] ⊙ 已存在，跳过")
                else:
                    print(f"  [{i}/{total}] ✗ 错误: {e}")

        connection.commit()
        print("\n✓ 数据库初始化完成!\n")

        # 验证表是否创建成功
        cursor.execute("USE stock_monitor")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print("已创建的数据表:")
        for table in tables:
            print(f"  - {table[0]}")

        # 验证默认用户
        cursor.execute("SELECT username, email FROM users")
        users = cursor.fetchall()

        if users:
            print(f"\n默认账号:")
            for user in users:
                print(f"  用户名: {user[0]}")
                print(f"  邮箱: {user[1]}")
            print(f"  密码: admin")
            print(f"  ⚠️  请在首次登录后立即修改密码!")

        cursor.close()
        connection.close()

        print("\n" + "=" * 50)
        print("数据库初始化完成!")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = init_database()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(1)
