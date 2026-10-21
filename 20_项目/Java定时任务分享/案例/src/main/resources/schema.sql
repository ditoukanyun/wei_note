CREATE TABLE compensation_order (
    order_id BIGINT PRIMARY KEY,
    region VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error VARCHAR(500),
    completed_by VARCHAR(100)
);
-- 业务唯一键与订单状态在同一事务提交，演示数据库内副作用的幂等。
CREATE TABLE compensation_effect (
    order_id BIGINT PRIMARY KEY REFERENCES compensation_order(order_id),
    instance_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE job_run (
    execution_id VARCHAR(36) PRIMARY KEY,
    instance_id VARCHAR(100) NOT NULL,
    shard INTEGER NOT NULL,
    region VARCHAR(20) NOT NULL,
    config_version VARCHAR(64) NOT NULL,
    batch_size INTEGER NOT NULL,
    job_parameter VARCHAR(100) NOT NULL,
    success_count INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    skipped_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    error_message VARCHAR(500),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP WITH TIME ZONE
);
CREATE TABLE demo_control (
    id INTEGER PRIMARY KEY,
    failure_enabled BOOLEAN NOT NULL,
    fail_order_id BIGINT NOT NULL
);
INSERT INTO demo_control VALUES (1, TRUE, 1005);
INSERT INTO compensation_order(order_id, region) VALUES
    (1001,'华东'),(1002,'华东'),(1003,'华东'),(1004,'华东'),
    (1005,'华南'),(1006,'华南'),(1007,'华南'),(1008,'华南'),
    (1009,'华北'),(1010,'华北'),(1011,'华北'),(1012,'华北');
