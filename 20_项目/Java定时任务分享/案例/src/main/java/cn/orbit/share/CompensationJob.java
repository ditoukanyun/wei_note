package cn.orbit.share;

import org.apache.shardingsphere.elasticjob.api.ShardingContext;
import org.apache.shardingsphere.elasticjob.simple.job.SimpleJob;
import org.springframework.stereotype.Component;

/** 这就是分享时首先展开的最小 Job 入口。 */
@Component
public class CompensationJob implements SimpleJob {
    private final CompensationService service;
    public CompensationJob(CompensationService service) { this.service = service; }

    @Override
    public void execute(ShardingContext context) {
        CompensationService.RunResult result = service.execute(context.getShardingItem(),
                context.getShardingParameter(), context.getJobParameter());
        // 完成本批其他订单后汇总抛出，让框架错误处理器也能感知业务失败。
        if (result.failed() > 0) throw new IllegalStateException("分片存在失败订单，请查看业务执行记录");
    }
}
