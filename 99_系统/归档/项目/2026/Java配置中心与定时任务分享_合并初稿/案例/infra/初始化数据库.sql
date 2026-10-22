-- 开发与测试使用独立数据库；两个开发实例共享 orders。
\i /opt/demo/schema.sql
CREATE DATABASE orders_test;
\connect orders_test
\i /opt/demo/schema.sql
