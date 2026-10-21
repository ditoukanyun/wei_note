package cn.orbit.share;

import java.util.Map;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** 每笔订单一个事务。该类独立于循环调用方，保证 Spring 事务代理真正生效。 */
@Service
public class OrderProcessor {
    public enum Result { SUCCESS, FAILED, SKIPPED }
    private final JdbcTemplate jdbc;
    public OrderProcessor(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    @Transactional
    public Result process(long orderId, String instanceId) {
        // 第二个并发执行者等到事务提交后重新检查状态，不会再次写入业务结果。
        Map<String, Object> order = jdbc.queryForMap(
                "SELECT * FROM compensation_order WHERE order_id = ? FOR UPDATE", orderId);
        if ("SUCCESS".equals(order.get("status"))) return Result.SKIPPED;
        Map<String, Object> control = jdbc.queryForMap("SELECT * FROM demo_control WHERE id = 1");
        jdbc.update("UPDATE compensation_order SET attempts = attempts + 1 WHERE order_id = ?", orderId);
        if (Boolean.TRUE.equals(control.get("failure_enabled"))
                && ((Number) control.get("fail_order_id")).longValue() == orderId) {
            jdbc.update("UPDATE compensation_order SET last_error = ? WHERE order_id = ?",
                    "模拟下游超时，等待恢复后重跑", orderId);
            return Result.FAILED;
        }
        // 此处以数据库流水代替真实外部调用，order_id 主键是第二层约束。
        jdbc.update("INSERT INTO compensation_effect(order_id, instance_id) VALUES (?, ?)", orderId, instanceId);
        jdbc.update("UPDATE compensation_order SET status = 'SUCCESS', last_error = NULL, completed_by = ? WHERE order_id = ?",
                instanceId, orderId);
        return Result.SUCCESS;
    }
}
