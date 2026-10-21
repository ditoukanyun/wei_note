"""独立验证 ElasticJob，不连接 Nacos 或 Apollo。"""
import json
import os
import time
import urllib.request
A=os.environ.get('APP_A_URL','http://localhost:8091')
B=os.environ.get('APP_B_URL','http://localhost:8092')
def api(base,path,data=None):
    req=urllib.request.Request(base+'/api/'+path,None if data is None else json.dumps(data).encode(),{'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=8) as r:return json.load(r)
def wait(label,probe):
    end=time.monotonic()+150
    last=None
    while time.monotonic()<end:
        try:
            if probe():print('通过：'+label,flush=True);return
        except Exception as e:last=e
        time.sleep(1)
    raise AssertionError(label+'超时：'+str(last))
def trigger():
    before=api(A,'summary')['runCount']
    api(A,'jobs/trigger',{})
    wait('三个分片结束',lambda:(lambda s:s['runCount']>=before+3 and s['running']==0)(api(A,'summary')))
for base in [A,B]:wait('任务实例就绪 '+base,lambda base=base:api(base,'runtime'))
api(A,'demo/reset',{})
trigger()
s=api(A,'summary')
assert (s['success'],s['pending'],s['effects'])==(11,1,11),s
assert len({r['instance_id'] for r in api(A,'runs')})==2
assert {r['item'] for r in api(A,'shards')}=={0,1,2}
print('通过：两个实例承担三个分片，首轮 11 成功、1 待补偿。',flush=True)
api(A,'demo/failure',{'enabled':False})
trigger()
s=api(A,'summary')
assert (s['success'],s['pending'],s['effects'])==(12,0,12),s
orders=api(A,'orders')
assert next(o for o in orders if o['order_id']==1005)['attempts']==2
assert all(o['attempts']==1 for o in orders if o['order_id']!=1005)
trigger()
assert api(A,'orders')==orders and api(A,'summary')['effects']==12
print('通过：失败补偿与额外重跑幂等。',flush=True)
api(A,'demo/reset',{})
print('ElasticJob 独立案例全部验证通过，已恢复 12 笔待补偿订单。',flush=True)
