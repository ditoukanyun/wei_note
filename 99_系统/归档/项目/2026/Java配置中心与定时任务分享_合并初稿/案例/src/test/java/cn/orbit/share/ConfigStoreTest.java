package cn.orbit.share;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ConfigStoreTest {
    @Test
    void validPublicationReplacesBothValuesButOldSnapshotRemainsStable() {
        ConfigStore store = new ConfigStore();
        assertTrue(store.apply(yaml(false, "100")));
        ConfigStore.Snapshot old = store.snapshot();
        assertTrue(store.apply(yaml(true, "20")));
        assertFalse(old.enabled());
        assertEquals(100, old.batchSize());
        assertTrue(store.snapshot().enabled());
        assertEquals(20, store.snapshot().batchSize());
        assertNotEquals(old.version(), store.snapshot().version());
    }

    @Test
    void invalidPublicationAndDeletionKeepLastValidVersion() {
        ConfigStore store = new ConfigStore();
        assertTrue(store.apply(yaml(true, "20")));
        ConfigStore.Snapshot valid = store.snapshot();
        for (String invalid : new String[]{yaml(false, "0"), yaml(false, "1001"), yaml(false, "1.5"), "", null}) {
            assertFalse(store.apply(invalid));
            assertSame(valid, store.snapshot());
            assertFalse(store.state().lastError().isBlank());
        }
    }

    @Test
    void duplicatedKeysAreRejected() {
        ConfigStore store = new ConfigStore();
        assertFalse(store.apply("order:\n  compensation:\n    enabled: true\n    enabled: false\n    batch-size: 20\n"));
    }

    static String yaml(boolean enabled, String batch) {
        return "order:\n  compensation:\n    enabled: " + enabled + "\n    batch-size: " + batch + "\n";
    }
}
