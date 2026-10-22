package cn.orbit.share;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DemoDataService {
    private final JdbcTemplate jdbc;
    public DemoDataService(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    @Transactional
    public void reset() {
        Integer running = jdbc.queryForObject("SELECT COUNT(*) FROM job_run WHERE finished_at IS NULL", Integer.class);
        if (running != null && running > 0) throw new IllegalStateException("仍有分片执行中，请结束后再重置");
        jdbc.update("DELETE FROM compensation_effect");
        jdbc.update("DELETE FROM job_run");
        jdbc.update("UPDATE compensation_order SET status='PENDING', attempts=0, last_error=NULL, completed_by=NULL");
        jdbc.update("UPDATE demo_control SET failure_enabled=TRUE, fail_order_id=1005 WHERE id=1");
    }
}
