---
created: 2025-03-02
area: "[[AI相关]]"
tags: [ai, vector-db, algorithm, ivf]
---
# IVF

## 定义

IVF（Inverted File Index，倒排文件索引）是一种基于聚类的向量近似最近邻搜索算法。通过将向量空间划分为多个聚类（Voronoi单元），先定位到最近的聚类中心，再在该聚类内进行精确搜索，从而加速检索。

## 核心思想

**空间分区策略**：

- 将高维空间划分为多个区域（聚类）
- 每个区域由一个中心点（centroid）代表
- 搜索时先找到最近的中心，再搜索该中心所属区域

**类比**：
就像图书馆的分类系统，先确定书在哪个书架（聚类），再在那个书架上找书，而不是遍历整个图书馆。

## 检索流程

```mermaid
flowchart LR
    A["查询向量"] --> B["计算与聚类中心距离"]
    B --> C["选择 nprobe 个最近聚类"]
    C --> D["扫描倒排列表"]
    D --> E["计算候选距离"]
    E --> F["返回 Top K"]
```

IVF 的核心取舍是搜索范围：`nprobe` 越大，越不容易漏掉边界附近的近邻，但延迟也越高。

## 算法结构

### 索引构建

```python
def build_ivf_index(vectors, nlist):
    """
    构建IVF索引
    nlist: 聚类数量（通常为sqrt(N)）
    """
    # 1. 使用K-means对向量进行聚类
    kmeans = KMeans(n_clusters=nlist)
    kmeans.fit(vectors)

    centroids = kmeans.cluster_centers_
    labels = kmeans.labels_

    # 2. 构建倒排列表
    inverted_lists = [[] for _ in range(nlist)]
    for idx, label in enumerate(labels):
        inverted_lists[label].append({
            "id": idx,
            "vector": vectors[idx]
        })

    return {
        "centroids": centroids,
        "inverted_lists": inverted_lists
    }
```

### 搜索过程

```python
def ivf_search(query, index, nprobe=1, k=10):
    """
    IVF搜索
    nprobe: 要搜索的聚类数量（默认只搜最近的1个）
    k: 返回的结果数量
    """
    # 1. 计算查询向量与所有中心的距离
    distances = [
        distance(query, centroid)
        for centroid in index["centroids"]
    ]

    # 2. 选择最近的nprobe个中心
    nearest_clusters = argsort(distances)[:nprobe]

    # 3. 在这些聚类中搜索
    candidates = []
    for cluster_id in nearest_clusters:
        for item in index["inverted_lists"][cluster_id]:
            dist = distance(query, item["vector"])
            candidates.append((item["id"], dist))

    # 4. 排序并返回Top K
    candidates.sort(key=lambda x: x[1])
    return candidates[:k]
```

## 关键参数

| 参数       | 描述         | 推荐值     | 影响                     |
| ---------- | ------------ | ---------- | ------------------------ |
| **nlist**  | 聚类数量     | 4\*sqrt(N) | 越大搜索越快，构建越慢   |
| **nprobe** | 搜索的聚类数 | 1-100      | 越大召回率越高，搜索越慢 |
| **metric** | 距离度量     | L2/IP      | 根据场景选择             |

## IVF变体

### IVF-PQ（Product Quantization）

**问题**：原始向量存储占用空间大

**解决方案**：

- 将向量分成m个子向量
- 每个子向量单独量化
- 用短码本代替原始向量

**效果**：

- 存储空间减少10-20倍
- 搜索时可以快速计算近似距离

```python
# PQ编码示例
def pq_encode(vector, codebooks):
    """
    向量维度: D = 128
    子向量数: m = 8
    每个子向量维度: D/m = 16
    """
    subvectors = split(vector, m)  # 分成8个子向量
    codes = []

    for i, subvec in enumerate(subvectors):
        # 在第i个码本中找到最近的码字
        code = find_nearest_codebook(subvec, codebooks[i])
        codes.append(code)

    return codes  # 8个整数，代替128个浮点数
```

### IVF-HNSW

**改进**：用HNSW加速中心点搜索

```python
def ivf_hnsw_search(query, index):
    # 1. 用HNSW快速找到最近的nprobe个中心
    nearest_centroids = hnsw_search(
        query,
        index["centroid_hnsw"],
        k=nprobe
    )

    # 2. 在这些聚类中搜索（同标准IVF）
    candidates = search_in_clusters(query, nearest_centroids)

    return candidates
```

## 优点

1. **内存效率高**：原始数据可以不全部加载到内存
2. **可扩展性好**：适合十亿级数据
3. **构建相对快**：K-means聚类比构建图结构快
4. **磁盘友好**：倒排列表可以存储在磁盘

## 缺点

1. **动态更新困难**：新数据需要重新聚类或维护复杂的增量更新
2. **边界问题**：查询向量恰好在聚类边界时可能漏检
3. **参数敏感**：nlist和nprobe需要仔细调优
4. **召回率**：相比HNSW，相同速度下召回率略低

## IVF vs HNSW

| 维度         | IVF           | HNSW           |
| ------------ | ------------- | -------------- |
| **查询速度** | 快（10-50ms） | 极快（1-10ms） |
| **内存占用** | 低            | 高             |
| **构建时间** | 中等          | 慢             |
| **动态更新** | 困难          | 相对容易       |
| **召回率**   | 中高          | 高             |
| **适用规模** | 千万级-十亿级 | 百万级-千万级  |
| **磁盘支持** | 好            | 差             |

## 适用场景

**适合使用IVF**：

- 数据规模大（千万级以上）
- 内存受限
- 可以接受稍低的实时性要求
- 数据相对稳定，不需要频繁更新

**不适合使用IVF**：

- 需要实时动态更新
- QPS要求极高
- 数据集较小（百万级以下，HNSW更合适）

## 实际应用

**Milvus中的IVF配置**：

```python
# IVF_FLAT：标准IVF
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}  # 聚类数
}

# IVF_SQ8：标量量化版（更省空间）
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_SQ8",
    "params": {"nlist": 1024}
}

# IVF_PQ：乘积量化版（最省空间）
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_PQ",
    "params": {
        "nlist": 1024,
        "m": 8,      # 子向量数
        "nbits": 8   # 每子向量编码位数
    }
}

# 搜索参数
search_params = {
    "metric_type": "L2",
    "params": {"nprobe": 16}  # 搜索的聚类数
}
```

## 调优建议

1. **nlist设置**：
   - 经验公式：nlist ≈ 4 \* sqrt(N)
   - N=1M → nlist=4096
   - N=100M → nlist=40000

2. **nprobe调优**：
   - 从1开始逐步增加，直到召回率满足要求
   - 通常1-10适合低延迟场景，10-100适合高召回场景

3. **量化选择**：
   - 内存充足：IVF_FLAT（精度最高）
   - 内存紧张：IVF_SQ8（精度换空间）
   - 极致压缩：IVF_PQ（最大压缩比）

## 实践检查清单

- 是否用业务评估集同时测召回率、延迟和成本。
- `nlist` 是否和数据量匹配，避免聚类过粗或过细。
- `nprobe` 是否按不同延迟档位配置，而不是固定一个值。
- 是否评估边界查询的漏召回问题。
- 数据频繁增删时是否考虑 [[HNSW]] 或重建索引策略。

## 相关概念

- [[向量数据库]] - 向量存储与检索系统
- [[HNSW]] - 另一种向量检索算法
- [[ANN]] - 近似最近邻搜索
- [[Milvus]] - 支持IVF的开源向量数据库
- [[PQ]] - 乘积量化技术

## 参考资料

- 论文：_Product quantization for nearest neighbor search_ (Jégou et al., 2011)
