package cn.orbit.share;

import org.apache.shardingsphere.elasticjob.api.JobConfiguration;
import org.apache.shardingsphere.elasticjob.lite.api.bootstrap.impl.ScheduleJobBootstrap;
import org.apache.shardingsphere.elasticjob.lite.lifecycle.api.JobAPIFactory;
import org.apache.shardingsphere.elasticjob.lite.lifecycle.api.JobOperateAPI;
import org.apache.shardingsphere.elasticjob.lite.lifecycle.api.ShardingStatisticsAPI;
import org.apache.shardingsphere.elasticjob.reg.zookeeper.ZookeeperConfiguration;
import org.apache.shardingsphere.elasticjob.reg.zookeeper.ZookeeperRegistryCenter;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;

@Configuration
@ConditionalOnProperty(name = "demo.job.enabled", havingValue = "true", matchIfMissing = true)
public class JobInfrastructure {
    public static final String JOB_NAME = "order-compensation-job";

    @Bean(initMethod = "init", destroyMethod = "close")
    ZookeeperRegistryCenter registryCenter(Environment env) {
        ZookeeperConfiguration config = new ZookeeperConfiguration(env.getRequiredProperty("demo.zookeeper.address"),
                env.getRequiredProperty("demo.job.namespace"));
        config.setSessionTimeoutMilliseconds(30000);
        config.setConnectionTimeoutMilliseconds(15000);
        return new ZookeeperRegistryCenter(config);
    }

    @Bean(initMethod = "schedule", destroyMethod = "shutdown")
    ScheduleJobBootstrap scheduledJob(ZookeeperRegistryCenter registry, CompensationJob job, Environment env) {
        JobConfiguration config = JobConfiguration.newBuilder(JOB_NAME, 3)
                // ElasticJob 3.0.4 的显式时区参数要求 GMT 格式。
                .cron(env.getRequiredProperty("demo.job.cron")).timeZone("GMT+08:00")
                .shardingItemParameters("0=华东,1=华南,2=华北").jobParameter("pending")
                .monitorExecution(true).failover(false).misfire(false)
                .jobErrorHandlerType("LOG").overwrite(true).build();
        return new ScheduleJobBootstrap(registry, job, config);
    }

    @Bean
    JobOperateAPI jobOperateAPI(Environment env) {
        return JobAPIFactory.createJobOperateAPI(env.getRequiredProperty("demo.zookeeper.address"),
                env.getRequiredProperty("demo.job.namespace"), null);
    }

    @Bean
    ShardingStatisticsAPI shardingStatisticsAPI(Environment env) {
        return JobAPIFactory.createShardingStatisticsAPI(env.getRequiredProperty("demo.zookeeper.address"),
                env.getRequiredProperty("demo.job.namespace"), null);
    }
}
