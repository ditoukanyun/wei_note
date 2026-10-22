package cn.orbit.share;

import java.util.ArrayList;
import java.util.List;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DemoDataService {
    private final JdbcTemplate jdbc;
    public DemoDataService(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    @Transactional
    public void reset() {
        replaceOrders(4, 1001, true);
    }

    @Transactional
    public void seedLarge() {
        replaceOrders(250, 100001, false);
    }

    private void replaceOrders(int perRegion, long firstId, boolean failureEnabled) {
        Integer running = jdbc.queryForObject("SELECT COUNT(*) FROM job_run WHERE finished_at IS NULL", Integer.class);
        if (running != null && running > 0) throw new IllegalStateException("仍有分片执行中，请结束后再重置");
        jdbc.update("DELETE FROM compensation_effect");
        jdbc.update("DELETE FROM job_run");
        jdbc.update("DELETE FROM compensation_order");
        List<Object[]> rows = new ArrayList<>();
        String[] regions = {"华东", "华南", "华北"};
        for (int shard = 0; shard < regions.length; shard++) {
            for (int index = 0; index < perRegion; index++) {
                rows.add(new Object[]{firstId + (long) shard * perRegion + index, regions[shard]});
            }
        }
        jdbc.batchUpdate("INSERT INTO compensation_order(order_id, region) VALUES (?, ?)", rows);
        jdbc.update("UPDATE demo_control SET failure_enabled=?, fail_order_id=1005 WHERE id=1", failureEnabled);
    }
}
