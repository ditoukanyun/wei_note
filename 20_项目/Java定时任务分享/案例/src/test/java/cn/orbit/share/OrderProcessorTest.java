package cn.orbit.share;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;
import org.junit.jupiter.api.*;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;
import static org.junit.jupiter.api.Assertions.*;

class OrderProcessorTest {
    @Configuration
    @EnableTransactionManagement
    static class Transactions {}
    private AnnotationConfigApplicationContext context;
    private JdbcTemplate jdbc;
    private OrderProcessor processor;

    @BeforeEach
    void setup() {
        DataSource source = new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID()
                + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", "");
        new ResourceDatabasePopulator(new ClassPathResource("schema.sql")).execute(source);
        context = new AnnotationConfigApplicationContext();
        context.register(Transactions.class);
        context.registerBean(DataSource.class, () -> source);
        context.registerBean(JdbcTemplate.class, () -> new JdbcTemplate(source));
        context.registerBean(PlatformTransactionManager.class, () -> new DataSourceTransactionManager(source));
        context.registerBean(OrderProcessor.class);
        context.refresh();
        jdbc = context.getBean(JdbcTemplate.class);
        processor = context.getBean(OrderProcessor.class);
    }

    @AfterEach
    void close() { context.close(); }

    @Test
    void failureCanBeRecoveredAndRepeatedSuccessHasNoExtraEffect() {
        assertEquals(OrderProcessor.Result.FAILED, processor.process(1005, "实例甲"));
        assertEquals(0, countEffects());
        assertEquals("PENDING", jdbc.queryForObject("SELECT status FROM compensation_order WHERE order_id=1005", String.class));
        jdbc.update("UPDATE demo_control SET failure_enabled=FALSE WHERE id=1");
        assertEquals(OrderProcessor.Result.SUCCESS, processor.process(1005, "实例乙"));
        assertEquals(OrderProcessor.Result.SKIPPED, processor.process(1005, "实例甲"));
        assertEquals(1, countEffects());
        assertEquals(2, jdbc.queryForObject("SELECT attempts FROM compensation_order WHERE order_id=1005", Integer.class));
    }

    @Test
    void concurrentInstancesCreateOneEffect() throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        CountDownLatch start = new CountDownLatch(1);
        try {
            var first = pool.submit(() -> { start.await(); return processor.process(1001, "实例甲"); });
            var second = pool.submit(() -> { start.await(); return processor.process(1001, "实例乙"); });
            start.countDown();
            var results = List.of(first.get(10, TimeUnit.SECONDS), second.get(10, TimeUnit.SECONDS));
            assertTrue(results.contains(OrderProcessor.Result.SUCCESS));
            assertTrue(results.contains(OrderProcessor.Result.SKIPPED));
            assertEquals(1, countEffects());
            assertEquals(1, jdbc.queryForObject("SELECT attempts FROM compensation_order WHERE order_id=1001", Integer.class));
        } finally { pool.shutdownNow(); }
    }

    @Test
    void databaseFailureRollsBackAttemptAndStatusTogether() {
        jdbc.update("INSERT INTO compensation_effect(order_id, instance_id) VALUES (1001, '故障注入')");
        assertThrows(RuntimeException.class, () -> processor.process(1001, "实例甲"));
        assertEquals(0, jdbc.queryForObject("SELECT attempts FROM compensation_order WHERE order_id=1001", Integer.class));
        assertEquals("PENDING", jdbc.queryForObject("SELECT status FROM compensation_order WHERE order_id=1001", String.class));
    }

    @Test
    void batchLimitAndRegionPreventProcessingOtherShards() {
        TaskSettings store = new TaskSettings(true, 2);
        var service = new CompensationService(jdbc, processor, store, "实例甲");
        assertEquals(2, service.execute(0, "华东", "pending").success());
        assertEquals(2, countEffects());
        assertEquals(0, jdbc.queryForObject("SELECT SUM(attempts) FROM compensation_order WHERE region<>'华东'", Integer.class));
    }

    private int countEffects() { return jdbc.queryForObject("SELECT COUNT(*) FROM compensation_effect", Integer.class); }
}
