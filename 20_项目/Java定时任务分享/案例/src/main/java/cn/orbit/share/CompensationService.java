package cn.orbit.share;

import java.util.List;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class CompensationService {
    private static final Logger log = LoggerFactory.getLogger(CompensationService.class);
    public record RunResult(int success, int failed, int skipped) {}
    private final JdbcTemplate jdbc;
    private final OrderProcessor processor;
    private final TaskSettings config;
    private final String instanceId;

    public CompensationService(JdbcTemplate jdbc, OrderProcessor processor, TaskSettings config,
                               @Value("${demo.instance-id}") String instanceId) {
        this.jdbc = jdbc;
        this.processor = processor;
        this.config = config;
        this.instanceId = instanceId;
    }

    public RunResult execute(int shard, String region, String jobParameter) {
        // 一次分片调用只取一份不可变快照，批次执行中不混用不同版本配置。
        TaskSettings.Snapshot snapshot = config.snapshot();
        String executionId = UUID.randomUUID().toString();
        jdbc.update("INSERT INTO job_run(execution_id, instance_id, shard, region, config_version, batch_size, job_parameter, status) "
                        + "VALUES (?, ?, ?, ?, ?, ?, ?, 'RUNNING')",
                executionId, instanceId, shard, region, snapshot.version(), snapshot.batchSize(), jobParameter);
        int success = 0, failed = 0, skipped = 0;
        String error = "";
        try {
            if (!snapshot.enabled()) return new RunResult(0, 0, 0);
            if (!"pending".equals(jobParameter)) throw new IllegalArgumentException("本案例只支持公共参数 pending");
            // 框架只分配逻辑分片，筛选本分片的数据必须由业务代码完成。
            List<Long> ids = jdbc.queryForList("SELECT order_id FROM compensation_order "
                    + "WHERE region = ? AND status = 'PENDING' ORDER BY order_id LIMIT ?", Long.class, region, snapshot.batchSize());
            for (long orderId : ids) {
                OrderProcessor.Result result = processor.process(orderId, instanceId);
                switch (result) {
                    case SUCCESS -> success++;
                    case FAILED -> failed++;
                    case SKIPPED -> skipped++;
                }
                log.info("订单补偿 instance={} execution={} shard={} region={} orderId={} result={}",
                        instanceId, executionId, shard, region, orderId, result);
            }
            if (failed > 0) error = "存在失败订单，恢复模拟依赖后再次触发";
            return new RunResult(success, failed, skipped);
        } catch (RuntimeException exception) {
            failed++;
            error = String.valueOf(exception.getMessage());
            throw exception;
        } finally {
            String status = !snapshot.enabled() ? "SKIPPED" : (failed > 0 ? "FAILED" : "SUCCESS");
            jdbc.update("UPDATE job_run SET success_count=?, failure_count=?, skipped_count=?, status=?, error_message=?, "
                            + "finished_at=CURRENT_TIMESTAMP WHERE execution_id=?",
                    success, failed, skipped, status, error.substring(0, Math.min(error.length(), 500)), executionId);
            log.info("分片结束 instance={} shard={} enabled={} configVersion={} batchSize={} success={} failed={} skipped={}",
                    instanceId, shard, snapshot.enabled(), snapshot.version(), snapshot.batchSize(), success, failed, skipped);
        }
    }
}
