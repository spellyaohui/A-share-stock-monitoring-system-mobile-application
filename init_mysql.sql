CREATE DATABASE IF NOT EXISTS stock_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stock_monitor;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    email VARCHAR(100) COMMENT '邮箱',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_login DATETIME COMMENT '最后登录时间',
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE IF NOT EXISTS stocks (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基本信息';

CREATE TABLE IF NOT EXISTS monitors (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监测配置';

CREATE TABLE IF NOT EXISTS stock_daily (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票日线数据';

CREATE TABLE IF NOT EXISTS notifications (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知记录';

CREATE TABLE IF NOT EXISTS notification_configs (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知配置';

CREATE TABLE IF NOT EXISTS system_cache (
    cache_key VARCHAR(100) PRIMARY KEY,
    cache_value JSON COMMENT '缓存值',
    expire_at DATETIME COMMENT '过期时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_expire (expire_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统缓存';

INSERT INTO users (username, password_hash, email) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', 'admin@example.com')
ON DUPLICATE KEY UPDATE username=username;
