"""独立验证配置中心，既不启动也不访问定时任务组件。"""
import json
import os
import time
import urllib.parse
import urllib.request
A=os.environ.get('APP_A_URL','http://localhost:8081')
B=os.environ.get('APP_B_URL','http://localhost:8082')
T=os.environ.get('APP_TEST_URL','http://localhost:8083')
N=os.environ.get('NACOS_URL','http://localhost:8848')
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
def matches(base,enabled,size):
    c=api(base,'runtime')['config']
    return c['snapshot']['enabled']==enabled and c['snapshot']['pageSize']==size and not c['lastError']
def publish(target,enabled,size):return api(A,'config/'+target,{'enabled':enabled,'pageSize':size})
for base in [A,B,T]:wait('实例就绪 '+base,lambda base=base:api(base,'runtime'))
boots={base:api(base,'runtime')['bootId'] for base in [A,B,T]}
publish('dev',False,100);publish('test',False,7)
wait('初始配置',lambda:matches(A,False,100) and matches(B,False,100) and matches(T,False,7))
assert api(A,'orders')['returned']==0
publish('dev',True,3)
wait('开发实例动态刷新',lambda:matches(A,True,3) and matches(B,True,3))
assert api(A,'orders')['returned']==3 and api(B,'orders')['returned']==3
assert matches(T,False,7) and api(T,'orders')['returned']==0
print('通过：开关与分页改变实际业务返回；测试环境独立。',flush=True)
versions={base:api(base,'runtime')['config']['snapshot']['version'] for base in [A,B]}
body=urllib.parse.urlencode({'tenant':'share-dev','group':'ORDER_SERVICE','dataId':'order-list.yaml','type':'yaml','content':'order:\n  list:\n    enabled: true\n    page-size: 0\n'}).encode()
with urllib.request.urlopen(N+'/nacos/v1/cs/configs',body,timeout=8) as r:assert r.read().decode().strip()=='true'
wait('非法配置被拒绝',lambda:all(api(base,'runtime')['config']['lastError'] for base in [A,B]))
for base in [A,B]:assert api(base,'runtime')['config']['snapshot']['version']==versions[base]
assert api(A,'orders')['returned']==3
publish('dev',True,3);publish('test',True,5)
wait('测试环境单独刷新',lambda:matches(T,True,5) and matches(A,True,3) and matches(B,True,3))
assert api(T,'orders')['returned']==5
assert all(api(base,'runtime')['bootId']==boot for base,boot in boots.items())
print('通过：非法配置保留旧快照；全部实例未重启。',flush=True)
publish('dev',False,100);publish('test',False,7)
wait('恢复起点',lambda:matches(A,False,100) and matches(B,False,100) and matches(T,False,7))
print('配置中心独立案例全部验证通过。',flush=True)
