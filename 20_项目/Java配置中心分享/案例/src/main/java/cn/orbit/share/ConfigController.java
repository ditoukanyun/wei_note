package cn.orbit.share;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.stream.IntStream;
import org.springframework.core.env.Environment;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/** 配置中心独立案例：配置变化直接影响订单列表接口，没有定时任务或数据库依赖。 */
@RestController
@RequestMapping("/api")
public class ConfigController {
    private final ConfigStore store;
    private final Environment env;
    private final ObjectMapper json;
    private final String bootId = UUID.randomUUID().toString();
    private final Instant startedAt = Instant.now();
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();

    public ConfigController(ConfigStore store, Environment env, ObjectMapper json) {
        this.store = store; this.env = env; this.json = json;
    }

    @GetMapping("/runtime")
    public Map<String, Object> runtime() {
        return Map.of("instanceId", env.getRequiredProperty("demo.instance-id"),
                "environment", env.getRequiredProperty("demo.environment"),
                "namespace", env.getRequiredProperty("demo.nacos.namespace"),
                "bootId", bootId, "startedAt", startedAt, "config", store.state());
    }

    @GetMapping("/cluster")
    public List<Object> cluster() throws Exception {
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
    public Map<String, Object> orders() {
        ConfigStore.Snapshot snapshot = store.snapshot();
        List<Map<String, Object>> items = snapshot.enabled()
                ? IntStream.rangeClosed(1001, 1012).limit(snapshot.pageSize())
                    .mapToObj(id -> Map.<String, Object>of("orderId", id, "title", "演示订单 " + id)).toList()
                : List.of();
        return Map.of("enabled", snapshot.enabled(), "pageSize", snapshot.pageSize(), "total", 12,
                "returned", items.size(), "items", items, "configVersion", snapshot.version());
    }

    public record ConfigInput(boolean enabled, int pageSize) {}

    @PostMapping("/config/{target}")
    public Map<String, String> publish(@PathVariable String target, @RequestBody ConfigInput input) throws Exception {
        if (!"share-dev".equals(env.getRequiredProperty("demo.nacos.namespace")))
            throw new IllegalArgumentException("请从开发实例发布配置，测试实例只用于观察");
        String namespace = switch (target) {
            case "dev" -> "share-dev";
            case "test" -> "share-test";
            default -> throw new IllegalArgumentException("环境仅支持 dev 或 test");
        };
        String content = "order:\n  list:\n    enabled: " + input.enabled() + "\n    page-size: " + input.pageSize() + "\n";
        ConfigStore.parse(content);
        Map<String, String> params = Map.of("tenant", namespace, "group", "ORDER_SERVICE",
                "dataId", "order-list.yaml", "type", "yaml", "content", content);
        String body = params.entrySet().stream().map(entry -> encode(entry.getKey()) + "=" + encode(entry.getValue()))
                .collect(java.util.stream.Collectors.joining("&"));
        HttpRequest request = HttpRequest.newBuilder(URI.create("http://" + env.getRequiredProperty("demo.nacos.address")
                        + "/nacos/v1/cs/configs"))
                .timeout(Duration.ofSeconds(8)).header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        HttpResponse<String> response = http.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200 || !"true".equals(response.body().trim()))
            throw new IllegalStateException("Nacos 发布失败");
        return Map.of("message", "配置已发布，等待客户端刷新", "namespace", namespace);
    }

    private static String encode(String value) { return URLEncoder.encode(value, StandardCharsets.UTF_8); }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, String>> invalid(IllegalArgumentException error) {
        return ResponseEntity.badRequest().body(Map.of("message", String.valueOf(error.getMessage())));
    }
}
