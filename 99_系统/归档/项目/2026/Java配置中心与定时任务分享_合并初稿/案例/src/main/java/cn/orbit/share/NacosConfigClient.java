package cn.orbit.share;

import com.alibaba.nacos.api.NacosFactory;
import com.alibaba.nacos.api.PropertyKeyConst;
import com.alibaba.nacos.api.config.ConfigService;
import com.alibaba.nacos.api.config.listener.Listener;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.util.Properties;
import java.util.concurrent.Executor;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

/** 使用原生 SDK 展示“订阅变更 → 校验 → 替换快照”的完整链路。 */
@Component
public class NacosConfigClient {
    private final ConfigStore store;
    private final Environment environment;
    private final ExecutorService executor = Executors.newSingleThreadExecutor(task -> {
        Thread thread = new Thread(task, "配置刷新");
        thread.setDaemon(true);
        return thread;
    });
    private ConfigService service;

    public NacosConfigClient(ConfigStore store, Environment environment) {
        this.store = store;
        this.environment = environment;
    }

    @PostConstruct
    public void start() throws Exception {
        Properties properties = new Properties();
        properties.setProperty(PropertyKeyConst.SERVER_ADDR, environment.getRequiredProperty("demo.nacos.address"));
        properties.setProperty(PropertyKeyConst.NAMESPACE, environment.getRequiredProperty("demo.nacos.namespace"));
        service = NacosFactory.createConfigService(properties);
        Listener listener = new Listener() {
            public Executor getExecutor() { return executor; }
            public void receiveConfigInfo(String configInfo) { store.apply(configInfo); }
        };
        String initial = service.getConfigAndSignListener(environment.getRequiredProperty("demo.nacos.data-id"),
                environment.getRequiredProperty("demo.nacos.group"), 10000, listener);
        if (!store.apply(initial)) throw new IllegalStateException("初始配置无效，请检查 Nacos 初始化服务");
    }

    @PreDestroy
    public void close() throws Exception {
        if (service != null) service.shutDown();
        executor.shutdownNow();
    }
}
