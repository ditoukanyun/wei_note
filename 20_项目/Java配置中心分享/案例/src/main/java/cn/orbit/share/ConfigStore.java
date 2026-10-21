package cn.orbit.share;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.HexFormat;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.yaml.snakeyaml.LoaderOptions;
import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.constructor.SafeConstructor;

/** 配置先完整解析、校验，再一次替换快照；业务不会读到半新半旧的两个字段。 */
@Component
public class ConfigStore {
    private static final Logger log = LoggerFactory.getLogger(ConfigStore.class);
    public record Snapshot(boolean enabled, int pageSize, String version, Instant appliedAt) {}
    public record State(Snapshot snapshot, long refreshCount, String lastError) {}
    private final AtomicReference<State> state = new AtomicReference<>(
            new State(new Snapshot(false, 100, "默认值", Instant.now()), 0, "尚未加载配置"));

    public State state() { return state.get(); }
    public Snapshot snapshot() { return state.get().snapshot(); }

    public synchronized boolean apply(String content) {
        try {
            Snapshot next = parse(content);
            State old = state.get();
            state.set(new State(next, old.refreshCount() + 1, ""));
            log.info("配置已刷新 version={} enabled={} pageSize={}", next.version(), next.enabled(), next.pageSize());
            return true;
        } catch (Exception error) {
            State old = state.get();
            state.set(new State(old.snapshot(), old.refreshCount(), error.getMessage()));
            log.warn("拒绝配置变更，继续使用上次有效快照：{}", error.getMessage());
            return false;
        }
    }

    static Snapshot parse(String content) throws Exception {
        if (content == null || content.isBlank()) throw new IllegalArgumentException("配置不能为空或被删除");
        LoaderOptions options = new LoaderOptions();
        options.setAllowDuplicateKeys(false);
        options.setCodePointLimit(16384);
        Map<?, ?> root = map(new Yaml(new SafeConstructor(options)).load(content));
        Map<?, ?> values = map(map(root.get("order")).get("list"));
        Object enabled = values.get("enabled");
        Object batch = values.get("page-size");
        if (!(enabled instanceof Boolean)) throw new IllegalArgumentException("enabled 必须为 true 或 false");
        if (!(batch instanceof Integer || batch instanceof Long)) throw new IllegalArgumentException("page-size 必须为整数");
        long size = ((Number) batch).longValue();
        if (size < 1 || size > 1000) throw new IllegalArgumentException("page-size 范围必须为 1～1000");
        String version = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256")
                .digest(content.getBytes(StandardCharsets.UTF_8))).substring(0, 12);
        return new Snapshot((Boolean) enabled, (int) size, version, Instant.now());
    }

    private static Map<?, ?> map(Object value) {
        if (!(value instanceof Map<?, ?> result)) throw new IllegalArgumentException("需要 order.list 层级的 YAML 配置");
        return result;
    }
}
