"""通过真实 ElasticJob 验证 750 笔订单的分批处理，结束后恢复基础数据。"""
import json
import os
import time
import urllib.request

A = os.environ.get('APP_A_URL', 'http://localhost:8091')
B = os.environ.get('APP_B_URL', 'http://localhost:8092')


def api(base, path, data=None):
    request = urllib.request.Request(base + '/api/' + path,
        None if data is None else json.dumps(data).encode(), {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def wait(label, probe):
    deadline = time.monotonic() + 150
    last = None
    while time.monotonic() < deadline:
        try:
            if probe():
                print('通过：' + label, flush=True)
                return
        except Exception as error:
            last = error
        time.sleep(1)
    raise AssertionError(label + ' 超时：' + str(last))


def trigger():
    before = api(A, 'summary')['runCount']
    api(A, 'jobs/trigger', {})
    wait('本轮三个分片结束', lambda: (lambda state:
        state['runCount'] >= before + 3 and state['running'] == 0)(api(A, 'summary')))


for base in [A, B]:
    wait('任务实例就绪 ' + base, lambda base=base: api(base, 'runtime'))
    assert api(base, 'runtime')['settings']['batchSize'] == 100, '扩展实验要求每片批量为 100'

api(A, 'demo/large', {})
assert api(A, 'summary')['pending'] == 750
for round_number, (success, pending) in enumerate([(300, 450), (600, 150), (750, 0)], start=1):
    trigger()
    state = api(A, 'summary')
    assert (state['success'], state['pending'], state['effects']) == (success, pending, success), state
    orders = api(A, 'orders')
    for region in ['华东', '华南', '华北']:
        assert sum(order['status'] == 'SUCCESS' for order in orders if order['region'] == region) == min(round_number * 100, 250)
    assert all(run['success_count'] <= 100 and run['failure_count'] == 0 for run in api(A, 'runs'))
    print(f'通过：第 {round_number} 轮，成功 {success}、待补偿 {pending}、流水 {success}', flush=True)

orders = api(A, 'orders')
assert all(order['attempts'] == 1 for order in orders)
assert len({run['instance_id'] for run in api(A, 'runs')}) == 2
trigger()
assert api(A, 'orders') == orders and api(A, 'summary')['effects'] == 750
print('通过：第四轮没有新增流水，750 笔订单均只处理一次', flush=True)
api(A, 'demo/reset', {})
state = api(A, 'summary')
assert (state['total'], state['pending'], state['effects']) == (12, 12, 0), state
print('分批处理验证完成，已恢复 12 笔基础演示订单', flush=True)
