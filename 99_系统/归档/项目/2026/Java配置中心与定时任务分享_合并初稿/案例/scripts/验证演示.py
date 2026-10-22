"""对真实 Docker 服务做端到端验证；执行前会重置本案例的数据和配置。"""
import json
import os
import time
import urllib.parse
import urllib.request

A = os.environ.get("APP_A_URL", "http://localhost:8081")
B = os.environ.get("APP_B_URL", "http://localhost:8082")
T = os.environ.get("APP_TEST_URL", "http://localhost:8083")
NACOS = os.environ.get("NACOS_URL", "http://localhost:8848")


def api(base, path, data=None):
    body = None if data is None else json.dumps(data).encode()
    request = urllib.request.Request(base + "/api/" + path, body,
                                     {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.load(response)


def wait(label, probe, timeout=120):
    deadline = time.monotonic() + timeout
    error = None
    while time.monotonic() < deadline:
        try:
            result = probe()
            if result:
                print("通过：" + label, flush=True)
                return result
        except Exception as exception:
            error = exception
        time.sleep(1)
    raise AssertionError(label + "超时；最近错误：" + str(error))


def config_is(base, enabled, batch):
    state = api(base, "runtime")["config"]
    snapshot = state["snapshot"]
    return snapshot["enabled"] == enabled and snapshot["batchSize"] == batch and not state["lastError"]


def publish(target, enabled, batch):
    return api(A, "config/" + target, {"enabled": enabled, "batchSize": batch})


def trigger():
    before = api(A, "summary")["runCount"]
    api(A, "jobs/trigger", {})
    wait("三个分片本轮执行完成", lambda: (lambda state: state["runCount"] >= before + 3 and state["running"] == 0)(api(A, "summary")))


for base in [A, B, T]:
    wait("实例就绪 " + base, lambda base=base: api(base, "runtime"))
boots = {base: api(base, "runtime")["bootId"] for base in [A, B, T]}
publish("dev", False, 100)
publish("test", False, 7)
wait("开发实例初始配置一致", lambda: config_is(A, False, 100) and config_is(B, False, 100))
wait("测试环境初始值独立", lambda: config_is(T, False, 7))
api(A, "demo/reset", {})
trigger()
assert api(A, "summary")["effects"] == 0, "关闭开关后不应写入业务流水"

publish("dev", True, 20)
wait("两个开发实例动态刷新", lambda: config_is(A, True, 20) and config_is(B, True, 20))
assert config_is(T, False, 7), "开发环境发布影响了测试环境"
trigger()
state = api(A, "summary")
assert (state["success"], state["pending"], state["effects"]) == (11, 1, 11), state
assert len({item["instance_id"] for item in api(A, "runs")}) == 2, "未观察到两个实例参与分片"
assert {item["item"] for item in api(A, "shards")} == {0, 1, 2}
print("通过：两个实例参与三个分片；首轮 11 成功、1 失败。", flush=True)

api(A, "demo/failure", {"enabled": False})
trigger()
state = api(A, "summary")
assert (state["success"], state["pending"], state["effects"]) == (12, 0, 12), state
orders = api(A, "orders")
assert next(item for item in orders if item["order_id"] == 1005)["attempts"] == 2
assert all(item["attempts"] == 1 for item in orders if item["order_id"] != 1005)
trigger()
assert api(A, "orders") == orders, "额外重跑改变了已完成订单"
assert api(A, "summary")["effects"] == 12
assert api(T, "summary")["effects"] == 0, "测试数据库被开发任务写入"
print("通过：失败补偿、额外重跑幂等、测试数据库隔离。", flush=True)

valid_versions = {base: api(base, "runtime")["config"]["snapshot"]["version"] for base in [A, B]}
body = urllib.parse.urlencode({"tenant":"share-dev","group":"ORDER_SERVICE","dataId":"order-service.yaml",
                              "type":"yaml","content":"order:\n  compensation:\n    enabled: false\n    batch-size: 0\n"}).encode()
with urllib.request.urlopen(NACOS + "/nacos/v1/cs/configs", body, timeout=8) as response:
    assert response.read().decode().strip() == "true"
wait("非法配置被两个实例拒绝", lambda: all(api(base, "runtime")["config"]["lastError"] for base in [A, B]))
for base in [A, B]:
    assert api(base, "runtime")["config"]["snapshot"]["version"] == valid_versions[base]
publish("dev", True, 20)
wait("恢复有效配置", lambda: config_is(A, True, 20) and config_is(B, True, 20))
publish("test", True, 9)
wait("测试环境可独立刷新", lambda: config_is(T, True, 9))
assert config_is(A, True, 20) and config_is(B, True, 20)
assert all(api(base, "runtime")["bootId"] == boot for base, boot in boots.items()), "发生了应用重启"
print("通过：非法值保留旧快照；环境隔离；全过程未重启。", flush=True)

api(A, "demo/reset", {})
api(A, "demo/failure", {"enabled": False})
publish("dev", True, 2)
wait("批量大小刷新为 2", lambda: config_is(A, True, 2) and config_is(B, True, 2))
trigger()
assert api(A, "summary")["effects"] == 6, "每分片批量 2 应共处理 6 笔"
trigger()
assert api(A, "summary")["effects"] == 12
print("通过：每分片批量限制确实影响业务处理数量。", flush=True)

publish("dev", False, 100)
publish("test", False, 7)
wait("恢复分享起始配置", lambda: config_is(A, False, 100) and config_is(B, False, 100) and config_is(T, False, 7))
api(A, "demo/reset", {})
print("全部端到端验证通过，已恢复演示起始状态。", flush=True)
