"""只创建缺失的配置，重启容器时保留现场修改。"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("NACOS_URL", "http://nacos:8848")


def request(path, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    with urllib.request.urlopen(BASE + path, body, timeout=10) as response:
        return response.read().decode()


namespaces = json.loads(request("/nacos/v1/console/namespaces"))["data"]
existing = {item["namespace"] for item in namespaces}
for namespace, name, batch_size in [("share-dev", "开发环境", 100), ("share-test", "测试环境", 7)]:
    if namespace not in existing:
        result = json.loads(request("/nacos/v1/console/namespaces", {
            "customNamespaceId": namespace, "namespaceName": name, "namespaceDesc": "Java 分享演示"
        }))
        if result is not True and (not isinstance(result, dict) or result.get("code") != 200):
            raise RuntimeError("创建命名空间失败：" + str(result))
    params = {"tenant": namespace, "group": "ORDER_SERVICE", "dataId": "order-service.yaml"}
    try:
        request("/nacos/v1/cs/configs?" + urllib.parse.urlencode(params))
        print(name + "配置已存在，保留原值。")
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        result = request("/nacos/v1/cs/configs", {
            **params, "type": "yaml",
            "content": "order:\n  compensation:\n    enabled: false\n    batch-size: " + str(batch_size) + "\n"
        })
        if result.strip() != "true":
            raise RuntimeError("发布初始配置失败：" + result)
        print(name + "配置初始化成功。")
