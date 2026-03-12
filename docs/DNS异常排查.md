### 一键排查脚本
在实例中依次执行以下命令，复制输出结果：
```bash
echo "=== 1. 网络连通性 ===" && ping -c 2 8.8.8.8
echo "=== 2. DNS解析测试 ===" && ping -c 1 www.google.com
echo "=== 3. DNS配置 ===" && getprop | grep dns
echo "=== 4. DNS状态 ===" && dumpsys dnsresolver | head -20
echo "=== 5. 代理进程 ===" && ps -ef | grep -E "clash|v2ray|xray" | grep -v grep
echo "=== 6. 代理日志 ===" && tail -20 /data/local/tmp/proxy.log 2>/dev/null || echo "无代理日志"

```
### 快速判断表
| 检查项 | 正常 | 异常 | 结论 |
| --- | --- | --- | --- |
| ping 8.8.8.8 | 有响应 | 超时/不通 | 网络问题，非DNS |
| ping 域名 | 有响应 | unknown host | DNS解析问题 |
| dumpsys dnsresolver | NOERROR多 | SERVFAIL多 | DNS服务异常 |
| ps grep clash | 无输出 | 有进程 | 有代理运行 |
| 代理日志 | 无错误 | connection refused | **代理服务器不可用** |

### 常见场景及话术

场景1：代理服务器不可用（最常见）
**判断依据**
*   有clash进程运行 
*   代理日志中出现 `connection refused` 或 `timeout`
**参考回复话术**：
> 您好，经排查发现您配置的代理服务器无法连接，导致DNS域名解析失败。请检查代理服务是否正常运行，或更换可用的代理服务器。

场景2：DNS服务器配置问题
**判断依据**：
*   无代理运行
*   `getprop | grep dns` 无输出或配置错误
**参考回复话术**：
> 您好，您的实例DNS服务器未正确配置。请在启动参数中添加DNS配置，例如设置 `ro.boot.redroid_net_dns1=8.8.8.8`。


场景3：网络不通
**判断依据**：
*   `ping 8.8.8.8` 也不通
### 临时恢复方法
如果确认是代理问题，可指导用户临时关闭代理恢复网络：
```bash
# 查找并停止代理进程
pkill -f clash
# 清理iptables规则
iptables -t nat -F OUTPUT
iptables -t nat -F CLASH 2>/dev/null
iptables -t nat -X CLASH 2>/dev/null
# 验证恢复
ping www.google.com

```

### 升级条件
以下情况需升级至研发处理：
*   无代理运行但DNS仍然失败 
*   DNS配置正确但 `dumpsys dnsresolver` 显示无DNS服务器
*   网络连通但所有DNS查询超时（可能是容器NAT问题）