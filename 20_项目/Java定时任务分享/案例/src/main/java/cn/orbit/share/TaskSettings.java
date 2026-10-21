package cn.orbit.share;

import java.time.Instant;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/** 本篇只讲任务，运行参数来自本地应用配置，不依赖配置中心。 */
@Component
public class TaskSettings {
    public record Snapshot(boolean enabled, int batchSize, String version, Instant appliedAt) {}
    private final Snapshot settings;

    public TaskSettings(@Value("${demo.enabled:true}") boolean enabled,
                        @Value("${demo.batch-size:100}") int batchSize) {
        if (batchSize < 1 || batchSize > 1000) throw new IllegalArgumentException("批量大小必须为 1～1000");
        settings = new Snapshot(enabled, batchSize, "本地配置", Instant.now());
    }

    public Snapshot snapshot() { return settings; }
}
