package cn.orbit.share;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.apache.shardingsphere.elasticjob.lite.lifecycle.api.JobOperateAPI;
import org.apache.shardingsphere.elasticjob.lite.lifecycle.api.ShardingStatisticsAPI;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.core.env.Environment;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

/** 教学控制台：配置发布走 Nacos API，触发任务走 ElasticJob API。 */
@RestController
@RequestMapping("/api")
public class DemoController {
    private final ConfigStore config;
    private final JdbcTemplate jdbc;
    private final DemoDataService data;
    private final Environment env;
    private final ObjectProvider<JobOperateAPI> operations;
    private final ObjectProvider<ShardingStatisticsAPI> statistics;
    private final ObjectMapper json;
    private final String bootId = UUID.randomUUID().toString();
    private final Instant startedAt = Instant.now();
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();

    public DemoController(ConfigStore config, JdbcTemplate jdbc, DemoDataService data, Environment env,
                          ObjectProvider<JobOperateAPI> operations, ObjectProvider<ShardingStatisticsAPI> statistics,
                          ObjectMapper json) {
        this.config = config; this.jdbc = jdbc; this.data = data; this.env = env;
        this.operations = operations; this.statistics = statistics; this.json = json;
    }

    @GetMapping("/runtime")
    public Map<String, Object> runtime() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("instanceId", env.getProperty("demo.instance-id"));
        result.put("environment", env.getProperty("demo.environment"));
        result.put("namespace", env.getProperty("demo.nacos.namespace"));
        result.put("bootId", bootId);
        result.put("startedAt", startedAt);
        result.put("pid", ProcessHandle.current().pid());
        try { result.put("ip", java.net.InetAddress.getLocalHost().getHostAddress()); }
        catch (java.net.UnknownHostException ignored) { result.put("ip", "未知"); }
        result.put("jobEnabled", env.getProperty("demo.job.enabled", Boolean.class, true));
        result.put("config", config.state());
        return result;
    }

    @GetMapping("/cluster")
    public List<Object> cluster() {
        List<Object> result = new ArrayList<>();
        String peers = env.getProperty("demo.peers", "");
        if (peers.isBlank()) return List.of(runtime());
        for (String peer : peers.split(",")) {
            try {
                HttpRequest request = HttpRequest.newBuilder(URI.create(peer.trim() + "/api/runtime"))
                        .timeout(Duration.ofSeconds(3)).GET().build();
                HttpResponse<String> response = http.send(request, HttpResponse.BodyHandlers.ofString());
                if (response.statusCode() != 200) throw new IllegalStateException("实例响应异常");
                result.add(json.readValue(response.body(), Map.class));
            } catch (Exception error) {
                if (error instanceof InterruptedException) Thread.currentThread().interrupt();
                result.add(Map.of("instanceId", peer, "error", "暂时不可用"));
            }
        }
        return result;
    }

    @GetMapping("/orders")
    public List<Map<String, Object>> orders() {
        return jdbc.queryForList("SELECT * FROM compensation_order ORDER BY order_id");
    }

    @GetMapping("/summary")
    public Map<String, Object> summary() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("total", jdbc.queryForObject("SELECT COUNT(*) FROM compensation_order", Integer.class));
        result.put("success", jdbc.queryForObject("SELECT COUNT(*) FROM compensation_order WHERE status='SUCCESS'", Integer.class));
        result.put("pending", jdbc.queryForObject("SELECT COUNT(*) FROM compensation_order WHERE status='PENDING'", Integer.class));
        result.put("effects", jdbc.queryForObject("SELECT COUNT(*) FROM compensation_effect", Integer.class));
        result.put("running", jdbc.queryForObject("SELECT COUNT(*) FROM job_run WHERE finished_at IS NULL", Integer.class));
        result.put("runCount", jdbc.queryForObject("SELECT COUNT(*) FROM job_run", Integer.class));
        result.put("failureControl", jdbc.queryForMap("SELECT * FROM demo_control WHERE id=1"));
        return result;
    }

    @GetMapping("/runs")
    public List<Map<String, Object>> runs() {
        return jdbc.queryForList("SELECT * FROM job_run ORDER BY started_at DESC LIMIT 60");
    }

    @GetMapping("/shards")
    public Object shards() {
        ShardingStatisticsAPI api = statistics.getIfAvailable();
        return api == null ? List.of() : api.getShardingInfo(JobInfrastructure.JOB_NAME);
    }

    @PostMapping("/jobs/trigger")
    public Map<String, Object> trigger() {
        requireScheduler();
        if (((Number) summary().get("running")).intValue() > 0) throw new IllegalStateException("任务仍在运行，请完成后再触发");
        operations.getObject().trigger(JobInfrastructure.JOB_NAME);
        return Map.of("message", "触发请求已提交，稍后查看分片记录", "jobName", JobInfrastructure.JOB_NAME);
    }

    public record ConfigInput(boolean enabled, int batchSize) {}

    @PostMapping("/config/{target}")
    public Map<String, String> publish(@PathVariable String target, @RequestBody ConfigInput input) throws Exception {
        requireScheduler();
        String tenant = switch (target) {
            case "dev" -> "share-dev";
            case "test" -> "share-test";
            default -> throw new IllegalArgumentException("环境仅支持 dev 或 test");
        };
        String content = "order:\n  compensation:\n    enabled: " + input.enabled()
                + "\n    batch-size: " + input.batchSize() + "\n";
        ConfigStore.parse(content);
        Map<String, String> params = Map.of("tenant", tenant, "group", "ORDER_SERVICE",
                "dataId", "order-service.yaml", "type", "yaml", "content", content);
        String body = params.entrySet().stream().map(entry -> encode(entry.getKey()) + "=" + encode(entry.getValue()))
                .collect(java.util.stream.Collectors.joining("&"));
        HttpRequest request = HttpRequest.newBuilder(URI.create("http://" + env.getRequiredProperty("demo.nacos.address")
                        + "/nacos/v1/cs/configs"))
                .timeout(Duration.ofSeconds(8)).header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        HttpResponse<String> response = http.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200 || !"true".equals(response.body().trim()))
            throw new IllegalStateException("Nacos 发布失败，请查看配置服务日志");
        return Map.of("message", "配置已发布到 Nacos，等待客户端刷新", "namespace", tenant);
    }

    public record FailureInput(boolean enabled) {}

    @PostMapping("/demo/failure")
    public Map<String, Object> failure(@RequestBody FailureInput input) {
        requireScheduler();
        jdbc.update("UPDATE demo_control SET failure_enabled=? WHERE id=1", input.enabled());
        return Map.of("failureEnabled", input.enabled(), "orderId", 1005);
    }

    @PostMapping("/demo/reset")
    public Map<String, String> reset() {
        requireScheduler();
        data.reset();
        return Map.of("message", "已重置 12 笔订单和故障开关；Nacos 配置保持原值");
    }

    private void requireScheduler() {
        if (operations.getIfAvailable() == null) throw new IllegalStateException("测试实例只用于观察配置，不接受演示写操作");
    }

    private static String encode(String value) { return URLEncoder.encode(value, StandardCharsets.UTF_8); }

    @ExceptionHandler({IllegalArgumentException.class})
    public ResponseEntity<Map<String, String>> invalid(IllegalArgumentException error) {
        return ResponseEntity.badRequest().body(Map.of("message", String.valueOf(error.getMessage())));
    }

    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<Map<String, String>> conflict(IllegalStateException error) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("message", String.valueOf(error.getMessage())));
    }
}
