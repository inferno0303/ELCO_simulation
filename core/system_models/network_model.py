import math


class BaseStation:
    """基站实体，标识符和位置信息"""

    def __init__(self, id: int | str):
        self.id = id  # 唯一标识符

    def __repr__(self):
        return f'BaseStation {self.id}'


class SECServer:
    """边缘服务器实体，与基站协同部署"""

    def __init__(self, id: int | str,
                 comp_resource: float,  # CR_k 计算资源 (MHz)
                 memory: float,  # M_k 内存资源 (MB)
                 backhaul_bw: float):  # bw_bh_k 回程带宽 (Mbps)
        self.id = id
        self.comp_resource = comp_resource
        self.memory = memory
        self.backhaul_bw = backhaul_bw
        self.cached_functions = set()  # C_k 缓存函数类型集合

    def __repr__(self):
        return f'SECServer {self.id}: CPU {self.comp_resource}, MEM {self.memory}, BackhaulBW {self.backhaul_bw}, CachedFunc {self.cached_functions}'


class IoTDevice:
    """物联网设备实体"""

    def __init__(self, id: int | str, comp_resource: float, tx_power: float, bandwidth: float, channel_gain: float,
                 noise_power: float):
        self.id = id
        self.comp_resource = comp_resource  # CR_uj 计算资源
        self.tx_power = tx_power  # P_d2s 发射功率，单位W
        self.bandwidth = bandwidth  # B_d2s 分配带宽，单位Hz
        self.channel_gain = channel_gain  # h 信道增益
        self.noise_power = noise_power  # σ 噪声功率，单位W
        # 香农公式
        snr = (self.tx_power * self.channel_gain) / self.noise_power
        self.uplink_rate = self.bandwidth * math.log2(1 + snr) / 1e6  # 发送速率，单位：Mbps（从bps转换为Mbps）

    def __repr__(self):
        return f'IoTDevice {self.id}: CPU {self.comp_resource}, TxPower {self.tx_power}, BW {self.bandwidth}, ChannelGain {self.channel_gain}, NoisePower {self.noise_power}, UplinkRate {self.uplink_rate}',


class FunctionType:
    """函数类型定义，对应具体容器镜像"""

    def __init__(self, id: int | str, image_size: float):  # I_Fx 镜像大小
        self.id = id
        self.image_size = image_size  # 镜像大小，单位：MB

    def __repr__(self):
        return f'FunctionType {self.id}: ImageSize {self.image_size}'


class FunctionTask:
    """函数任务实体"""

    def __init__(self, id: int | str, data_size: float, workload: float, invocations: int, func_type: FunctionType):
        self.id = id
        self.data_size = data_size  # d_i 输入数据大小 (KB)
        self.workload = workload  # c_i 计算负载 (CPU cycles)
        self.invocations = invocations  # n_i 调用次数
        self.func_type = func_type  # 函数任务类型

    def __repr__(self):
        return f'FunctionTask {self.id}: DataSize {self.data_size}, WorkLoad {self.workload}, Invocations {self.invocations}, FuncType {self.func_type.id}, ImageSize {self.func_type.image_size}'


class SECNetwork:
    """SEC服务器互联网络 (G = (S, E, w))"""

    def __init__(self):
        self.servers = {}  # 服务器集合: server_id -> SECServer
        self.edges = {}  # 网络边: (server_id1, server_id2) -> (latency, bandwidth)

    def add_server(self, server: SECServer):
        self.servers[server.id] = server

    def add_connection(self, server_id1: int, server_id2: int, latency: float, bandwidth: float):
        if server_id1 not in self.servers or server_id2 not in self.servers:
            raise ValueError("指定的服务器不存在")

        # 无向图处理 (保证元组有序)
        key = tuple(sorted((server_id1, server_id2)))
        self.edges[key] = (latency, bandwidth)

    def get_connection(self, sec_id_1: int | str, sec_id_2: int | str) -> tuple:
        """
        返回server1与server2之间的延迟和带宽。
        - 如果有直接边，直接返回（latency, bandwidth）
        - 否则通过最短路径(Dijkstra)计算：延迟为路径中延迟之和，带宽为路径瓶颈带宽
        """
        import heapq

        # 验证服务器存在
        if sec_id_1 not in self.servers or sec_id_2 not in self.servers:
            raise ValueError("指定的服务器不存在")

        # 如果直接相连，返回该边信息
        key = tuple(sorted((sec_id_1, sec_id_2)))
        if key in self.edges:
            return self.edges[key]

        # 构建邻接表: node -> list of (neighbor, latency)
        adj = {sid: [] for sid in self.servers}
        for (u, v), (lat, bw) in self.edges.items():
            adj[u].append((v, lat))
            adj[v].append((u, lat))

        # Dijkstra 初始化
        dist = {sid: float('inf') for sid in self.servers}
        prev = {sid: None for sid in self.servers}
        dist[sec_id_1] = 0
        pq = [(0, sec_id_1)]

        # 执行最短路径
        while pq:
            current_dist, u = heapq.heappop(pq)
            if current_dist > dist[u]:
                continue
            if u == sec_id_2:
                break
            for v, weight in adj[u]:
                new_dist = current_dist + weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(pq, (new_dist, v))

        # 目标不可达
        if dist[sec_id_2] == float('inf'):
            return None, None

        # 重建路径以计算瓶颈带宽
        path = []
        node = sec_id_2
        while node is not None:
            path.append(node)
            node = prev[node]
        path.reverse()

        # 计算路径总延迟
        total_latency = dist[sec_id_2]
        # 计算瓶颈带宽
        bandwidths = []
        for i in range(len(path) - 1):
            edge_key = tuple(sorted((path[i], path[i + 1])))
            _, bw = self.edges[edge_key]
            bandwidths.append(bw)
        bottleneck_bw = min(bandwidths) if bandwidths else None

        return total_latency, bottleneck_bw

    def is_connected(self, server_id1: int, server_id2: int) -> bool:
        # 利用get_connection判断是否可达
        latency, bw = self.get_connection(server_id1, server_id2)
        return latency is not None
