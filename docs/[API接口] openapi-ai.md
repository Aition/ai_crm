# 📑 接口文档导航

> 本文档包含 **140+ API接口**，涵盖云手机全生命周期管理

## 🚀 快速开始

- [API域名](#api域名) - 选择正确的服务区域
- [接口限流规则](#接口限流规则) - 了解调用频率限制
- [分页查询说明](#分页查询说明) - 分页参数使用规范
- [枚举值参考文档](#枚举值参考文档) - 查询接口参数的所有枚举值定义

## 📦 接口分类总览

| 分类 | 说明 | 主要功能 |
|------|------|----------|
| 🔐 [SDK Token签发](#sdk-token签发) | 临时Token获取与管理 | 获取临时Token、清除Token |
| 💾 [板卡管理](#板卡管理) | 板卡资源的查询与操作 | 板卡列表、算力查询、重启重置 |
| 📱 [实例管理](#实例管理) | 云手机实例全生命周期管理 | 实例操作、属性设置、ADB调试、屏幕交互、数据注入 |
| 🔔 [回调管理](#回调管理) | 异步任务回调配置 | 回调地址配置、各类任务回调通知 |
| 📁 [文件管理](#文件管理) | 文件上传下载与管理 | 云盘上传、实例文件操作 |
| 📦 [应用管理](#应用管理-1) | 应用安装、启停与黑白名单 | 应用安装卸载、黑白名单管理 |
| 🌐 [网存2.0](#网存20) | 新一代网络存储方案 | 存储实例管理、备份还原 |
| 💿 [网存1.0](#网存10) | 经典网络存储管理 | 存储创建、开关机、备份删除 |
| 🛡️ [应用安全策略V2.0](#应用安全策略v20) | 应用安全管控 | 应用安全策略配置 |
| 💽 [镜像管理](#镜像管理) | 系统镜像查询 | 获取镜像列表 |
| 👥 [账户管理](#账户管理) | 子账户与权限管理 | 子账户管理、板卡授权 |

---|------|----------|
| 国内 | `https://api.xiaosuanyun.com` | 中国大陆地区用户 |
| 海外 | `https://openapi-hk.armcloud.net` | 海外及港澳台地区用户 |

### 接口限流规则

**warning 限流提醒**
所有OpenAPI接口都受到访问频率限制，请合理控制调用频率。详细限流规则请参考 [使用指南 - 接口限流说明](./UsageGuide.md#接口限流说明)

**主要限流规则：**

| 用户类型 | QPS限制（每秒） | 每分钟限制 | 计算方式 |
|---------|----------------|------------|----------|
| **测试用户** | 200次/秒 | 5,000次/分钟 | 滑动窗口，Access Key级别 |
| **付费用户** | 2,000次/秒 | 30,000次/分钟 | 滑动窗口，Access Key级别 |

**info 重要说明**
- 每个Access Key独立计算限流，不同Key之间不共享额度
- 单个Access Key下所有接口调用共享同一个限流额度
- 必须同时满足QPS和每分钟两个维度的限制

**限流响应**：当触发限流时返回HTTP 429状态码和错误信息

```json
{
  "msg": "Too many requests. Please try again later..",
  "code": 429,
  "data": null
}
```

**响应头说明**：

| 响应头 | 说明 | 示例 |
|--------|------|------|
| `X-RateLimit-Limit` | 当前限流周期的请求上限，根据限流类型而定 | 200 |
| `X-RateLimit-Remaining` | 当前限流周期剩余可用请求数 | 150 |
| `X-RateLimit-Reset` | 当前限流周期重置时间戳（Unix时间戳） | 1618900361 |
| `X-RateLimit-Type` | 触发的限流类型 | qps |

### 分页查询说明

**danger 分页参数重要约定**
所有分页查询类接口的 `rows`（或 `pageSize`）参数，**推荐默认值为 100**。请勿使用过大的值（如 1000），以避免单次查询数据量过大导致接口超时或性能下降。

本平台的分页查询接口有两种分页方式：

**方式一：传统分页（page + rows）**

| 参数 | 类型 | 说明 | 推荐默认值 |
|------|------|------|-----------|
| page | Integer | 页码，从1开始 | 1 |
| rows | Integer | 每页数量，取值范围1-1000 | **100** |

**方式二：游标分页（lastId + rows）**  — 推荐用于大数据量场景

| 参数 | 类型 | 说明 | 推荐默认值 |
|------|------|------|-----------|
| lastId | Long | 上次查询返回的最后一条记录ID，首次查询传null或0 | null |
| rows | Integer | 每页数量，取值范围1-1000 | **100** |

**tip 分页最佳实践**
- **默认每页数量使用 100**，在确有需要时可适当调大，但不建议超过 500
- 如需获取全部数据，请循环翻页直到 `hasNext` 为 false 或返回数据量小于 rows
- 游标分页（lastId方式）性能优于传统分页，大数据量场景建议优先使用

### 枚举值参考文档

**tip 枚举值查询指南**
本文档中所有接口参数的枚举值定义都已聚合到专门的枚举参考文档中，方便快速查询。

**枚举参考文档：** [EnumReference.md - 接口参数枚举值聚合文档](./EnumReference.md)

**包含内容：**

| 分类 | 参数数量 | 说明 |
|------|---------|------|
| **Status状态类** | 15个 | 实例状态、任务状态、设备状态等 |
| **Type类型类** | 17个 | 实例类型、策略类型、镜像类型等 |
| **Flag标记类** | 7个 | 网存标记、删除标记等 |
| **Boolean布尔类** | 5个 | 启用状态、在线状态等 |
| **其他** | 3个 | 国家编码、查询范围等 |

**使用方式：**
- 文档中枚举参数都带有跳转链接，点击即可查看完整枚举值
- 例如：`padStatus`参数显示为"实例状态。[查看所有26个状态码↗](./EnumReference.md#11-padstatus---实例状态)"

### 同步与异步接口判断

**：如何判断接口是同步还是异步**
如果接口响应数据中包含 `taskId` 字段，则该接口为**异步接口**。`code=200` 仅代表任务提交成功，**不代表操作已完成**。实际执行结果需通过**回调通知**获取。请务必在代码中正确处理异步逻辑，不要在调用后直接当作操作已完成。

### 回调机制说明（重要）

**：回调驱动，而非轮询**
本平台提供完善的**回调（Webhook）通知机制**，是获取异步操作结果和实例状态变化的**推荐方式**。在设计和实现时，应优先采用回调方式，而不是轮询查询。

**回调能力概述：**

- **异步任务结果通知**：所有异步接口（实例开关机、重启、重置、应用安装/卸载、文件上传等）执行完成后，平台会主动将结果通过回调推送到您配置的地址，包含 `taskId`、`taskStatus`、`taskResult` 等信息
- **实例状态变更通知**：实例状态发生变化时（如启动完成、关机、异常等），平台会主动推送实例状态回调，包含实例当前状态 `padStatus` 和连接状态 `padConnectStatus`，**无需轮询查询实例状态**
- **订阅事件通知**：支持订阅应用启动/停止等事件，事件触发时主动推送通知

**接入步骤：**

1. 调用 [查询支持的回调类型](#查询支持的回调类型) 获取可配置的回调类型列表
2. 调用 [新增回调地址配置](#新增回调地址配置) 为所需的回调类型配置接收地址（HTTP/HTTPS 接口）
3. 在您的服务端实现回调接收接口，处理平台推送的 JSON 数据

**回调数据通用格式示例：**

```json
{
  "taskBusinessType": 1000,
  "padCode": "AC22030010001",
  "taskId": 10111,
  "taskStatus": 3,
  "taskResult": "Success",
  "endTime": 1756021166163
}
```

其中 `taskStatus`：-1 全失败、-3 取消、-4 超时、1 待执行、2 执行中、3 完成。

详细的回调类型和字段说明请参考 [回调管理](#回调管理) 章节。

---

### SDK Token签发

签发临时 STS Token，用于对接入云手机服务的用户进行鉴权。

#### **获取SDK临时Token**

**接口类型**: 同步接口

**接口地址**

**接口概要**

作用：查询获取SDK临时Token。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

> /openapi/open/token/stsToken

**请求方式**

> GET

**请求数据类型**

> application/json

**请求示例**

```java
package com.xiaosuan.api.utils;

import com.alibaba.fastjson.TypeReference;
import com.xiaosuan.armcloud.sdk.configure.ArmCloudConfig;
import com.xiaosuan.armcloud.sdk.constant.ArmCloudApiEnum;
import com.xiaosuan.armcloud.sdk.http.DefaultHttpExecutor;
import com.xiaosuan.armcloud.sdk.model.Result;
import com.xiaosuan.armcloud.sdk.service.ArmCloudApiService;
import com.xiaosuan.armcloud.sdk.service.impl.ArmCloudApiServiceImpl;

import java.util.HashMap;

public class test {
    /**
     * 获取sts_token
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {

        ArmCloudConfig armCloudConfig = new ArmCloudConfig();
        armCloudConfig.setOpenUrl("https://xxx");
        armCloudConfig.setService("armcloud-paas");
        armCloudConfig.setHost("xxx");
        armCloudConfig.setAk("xxxxxx");
        armCloudConfig.setSk("xxxxxx");
        ArmCloudApiService armcloudApiService = new ArmCloudApiServiceImpl(armCloudConfig, new DefaultHttpExecutor());
        Result result = armcloudApiService.execute(ArmCloudApiEnum.STS_TOKEN,new HashMap<>(), new TypeReference>() {});
        System.out.println(result);

    }
}

```

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述|
|--- | --- | --- | ---|
|code | 200 | Integer | 状态码|
|msg | success | String | 响应消息|
|ts | 1756021167163 | Long | 时间戳|
|data |  | Object |  |
|├─token | xxxx-xxxx-xxxxx-xxxx | String | sdk通信token|

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
 "data": {
  "token": "xxxx-xxxx-xxxxx-xxxx"
 }
}
```

#### **获取SDK临时Token(根据padCode)**

**接口类型**: 同步接口

签发临时 STS Token，用于对接入云手机服务的用户进行鉴权(该token只能用于请求的padCode)。

**接口概要**

作用：查询获取SDK临时Token(根据padCode)。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/token/stsTokenByPadCode

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值 | 参数类型   | 是否必填 | 参数描述   |
|--- |-----|--------| --- |--------|
|padCode | ACXXXXX | String | 是 | 实例code |

**请求示例**

```javascript
{"padCode":"AC32010230001"}
```

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述|
|--- | --- | --- | ---|
|code | 200 | Integer | 状态码|
|msg | success | String | 响应消息|
|ts | 1756021167163 | Long | 时间戳|
|data |  | Object |  |
|├─token | xxxx-xxxx-xxxx-xxxx | String | sdk通信token|

**响应示例**

```javascript
{"code":200,"msg":"success","ts":1735209109185,"data":{"token":"xxx-xxx-xxx-xxxx"}}
```

#### **清除SDK授权Token**

**接口类型**: 同步接口

**接口地址**

**接口概要**

作用：修改清除SDK授权Token。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

> /openapi/open/token/clearStsToken

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值 | 参数类型   | 是否必填 | 参数描述|
|--- |-----|--------| --- | --- |
|token | 123 | String | 是 | |

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述|
|--- | --- | --- | ---|
|code | 200 | Integer | 状态码|
|msg | success | String | 响应消息|
|ts | 1756021167163 | Long | 时间戳|
|data |  | Object |  |

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
 "data": null
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
120008 | token不属于当前用户| 参考接口说明，检查请求参数和传值

#### **清除SDK临时Token(根据padCode)**

**接口类型**: 同步接口

**接口地址**

**接口概要**

作用：修改清除SDK临时Token(根据padCode)。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

> /openapi/open/token/clearStsTokenByPadCode

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值 | 参数类型   | 是否必填 | 参数描述   |
|--- |-----|--------| --- |--------|
|padCode | ACXXXXX | String | 是 | 实例code |

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1757656454505 | Long | 时间戳
data | null | Object | 响应数据（本接口清除token无返回值）
traceId | extrgsyx962o | String | 链路追踪ID

**响应示例**

```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1757656454505,
  "data": null,
  "traceId": "extrgsyx962o"
}
```

### 板卡管理

#### **板卡列表**

**接口类型**: 同步接口

根据查询条件分页获取板卡列表。

**接口概要**

作用：查询板卡列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/device/list

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值          | 参数类型 | 是否必填 | 参数描述
--- |--------------| --- |--| ---
page | 1            | Integer | 是 | 页码
rows | 10           | Integer | 是 | 条数
padAllocationStatus | 2           | Integer |否 | 实例分配状态。[详见枚举↗](./EnumReference.md#15-padallocationstatus---实例分配状态)
deviceStatus | 1           | Integer | 否 | 物理机状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#14-devicestatus---物理机状态)
armServerCode | XS-MARS3500SA-0019           | String | 否 | 服务器code
deviceCode | 192.168.230.100           | String | 否 | 板卡code
deviceIp | 172.31.3.3           | String | 否 | deviceIp
armServerStatus | 1           | Integer | 否 | 服务器状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#16-armserverstatus---服务器状态)
idc | 1           | String | 否 |  机房Id
deviceIpList |  | String[] | 否    |
├─ | 172.31.3.3 | String | 否    | 板卡IP

**响应参数**

| 参数名               | 示例值 | 参数类型 | 参数描述                                            |
|-------------------| -- | --- |-------------------------------------------------|
| code              | 200 | Integer |                                                 |
| msg               | success | String ||
| ts                | 1713773577581 | Long ||
| data              |  | Object ||
| ├─page            | 1 | Integer | 当前页                                             |
| ├─rows            | 10 | Integer | 每页的数量                                           |
| ├─size            | 1 | Integer | 当前页的数量                                          |
| ├─total           | 1 | Integer | 总记录数                                            |
| ├─totalPage       | 1 | Integer | 总页数                                             |
| ├─pageData        |  | object[] | 列表                                              |
| ├─├─id            | 11236 | Integer | 板卡id                                            |
| ├─├─deviceLevel      | m2-3 | String | 云机实例级别                              |
| ├─├─deviceCode     | AC32010250020 | String | 物理机编号 |
| ├─├─deviceOutCode   | 03-58614134b4357321 | String | 外部物理机编码                                            |
| ├─├─deviceStatus       | 172.31.3.0/24 | Integer | 物理机状态 0-离线；1-在线                                            |
| ├─├─deviceIp      | 172.31.3.3 | Integer | 物理机IP                                            |
| ├─├─idc         | 1 | Integer | 外部机房编码                                           |
| ├─├─armServerCode | ACS32010260000 | String | ARM服务器编码                                           |
| ├─├─createBy    | admin | String | 创建者                                            |
| ├─├─createTime          | 2025-01-02 10:56:13 | String | 创建时间                                         |
| ├─├─padAllocationStatus          | 2 | Integer | 实例分配状态。[详见枚举↗](./EnumReference.md#15-padallocationstatus---实例分配状态) |
| ├─├─clusterCode          | 001 | String | 集群code    |
| ├─├─macAddress          | 52:74:01:b8:58:40 | String | MAC地址    |
| ├─├─initStatus          | 1 | String | 初始化状态。可选值：`0`初始化失败/`1`初始化成功/`2`初始化中。[详见枚举↗](./EnumReference.md#17-initstatus---初始化状态) |
| ├─├─cbsInfo          | 2.0.8 | String | 板卡CBS信息    |
| ├─├─nodeId          | 1 | String | 刀片ID    |
| ├─├─position          | 3 | String | 卡槽位置    |
| ├─├─gateway          | 192.168.3.1 | String | 板卡网关    |

**请求示例**

```javascript
{
    "padAllocationStatus": 2,
        "deviceStatus": 1,
        "armServerCode": "ACS32010260000",
        "deviceCode": "AC32010250020",
        "deviceIpList": [
        "172.31.3.3"
    ],
        "deviceIp": "172.31.3.3",
        "armServerStatus": 1
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1737626655161,
        "data": {
        "page": 1,
            "rows": 10,
            "size": 1,
            "total": 1,
            "totalPage": 1,
            "pageData": [
            {
                "page": 1,
                "rows": 10,
                "id": 11236,
                "deviceLevel": "m2-3",
                "deviceCode": "AC32010250020",
                "deviceOutCode": "03-58614134b4357321",
                "deviceStatus": true,
                "deviceIp": "172.31.3.3",
                "idc": "1",
                "armServerCode": "ACS32010260000",
                "createBy": "admin",
                "createTime": "2025-01-02 10:56:13",
                "padAllocationStatus": 2,
                "deleteFlag": false,
                "clusterCode": "001",
                "macAddress": "52:74:01:b8:58:40",
                "initStatus": 1,
                "cbsInfo": "2.0.8",
                "nodeId": "1",
                "position": "3",
                "gateway": null
            }
        ]
    }
}
```

#### **查询算力使用情况**

**接口类型**: 同步接口

汇总算力单元的使用情况。

**接口概要**

作用：查询查询算力使用情况。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

> 校验说明：子账号只能查询自身；指定查询时子账号列表必须属于当前主账号的下属账号集合。

**接口地址**

> /openapi/open/device/computeUsage

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | --- | --- | --- |
| queryRange | 0 | Integer | 否 | 查询范围。可选值：`0`主账号及全部子账号/`1`仅自身(默认)/`2`指定子账号列表 |
| subCustomerIds | [862, 863] | Long[] | 否 | 子账号ID列表，`queryRange=2` 时必填 |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | --- | --- |
| code | 200 | Integer | 状态码 |
| msg | success | String | 响应消息 |
| ts | 1756021167163 | Long | 时间戳 |
| data |  | Object[] | 账户算力使用列表 |
| ├─customerId | 10001 | Long | 客户ID |
| ├─customerAccount | test001 | String | 客户账号 |
| ├─usedCompute | 2 | Long | 已使用算力数量 |
| ├─totalCompute | 8 | Long | 总算力数量 |

**请求示例**

```javascript
{
  "queryRange": 0
}
```

**响应示例**

```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1737626655161,
  "data": [
    {
      "customerId": 10001,
      "customerAccount": "master001",
      "usedCompute": 4,
      "totalCompute": 12
    },
    {
      "customerId": 10002,
      "customerAccount": "sub001",
      "usedCompute": 1,
      "totalCompute": 4
    }
  ]
}
```

#### **板卡重启**

**接口类型**: 异步接口
**关联回调**: [实例重启任务回调](#实例重启任务回调) (taskBusinessType: `1002`)

断电重启板卡, 将影响板卡上创建的所有实例

**接口概要**

作用：操作板卡重启。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

该接口一般用在重启实例也无法恢复的情况

**接口地址**

> /openapi/open/device/powerReset

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名  | 示例值        | 参数类型 | 是否必填 | 参数描述              |
| ------- | ------------- | -------- | -------- |-------------------|
|deviceIps |  | String[] | 是 |                   |
|├─ | 172.31.4.124 | String | 是 | 物理设备IP            |
|type | 2 | String[] | 是 | 重启类型 1：硬重启 2：断电重启 |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述|
| --- | --- | --- | ---|
| code | 200 | Integer |  状态码|
| msg | success | String |  响应消息|
| ts | 1756021167163 | Long |  时间戳|
| data |  | Object[] |  |
| ├─taskId | 1|Integer |  任务ID|
| ├─deviceIp |172.31.4.124 |String |  物理设备IP|
| ├─errorMsg |“” |String |  失败的原因|
| ├─deviceOutCode |AC22030010000 |String |  云机编号|

**请求示例**

```javascript
{
 "deviceIps": [
  "172.31.4.124"
 ],
 "type":2
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1713773577581,
    "data": [
        {
            "taskId": 1,
            "deviceIp": "172.31.4.124",
            "errorMsg": null,
            "deviceOutCode": "AC22030010000"
        }
    ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110030 | 执行断电重启命令失败,参数请求不合规 | 参数请求不合规
110032 | 物理IP不存在 | 请检查物理设备IP是否正确
110033 | 执行断电重启命令失败 | 联系相关人员

#### **重置板卡**

**接口类型**: 异步接口
**关联回调**: [实例重置任务回调](#实例重置任务回调) (taskBusinessType: `-`)

重置板卡,清除对应实例并重启板卡

**接口概要**

作用：操作重置板卡。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/device/resetDevice

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值          | 参数类型 | 是否必填 | 参数描述
--- |--------------| --- |--| ---
remark | 确认删除           | String | 是 |  重置备注信息
deviceIps |  | String[] | 是    |物理机Ip列表(最少1个，最大128个)
├─ | 172.31.3.3 | String | 是    | 板卡IP

**响应参数**

| 参数名               | 示例值 | 参数类型 | 参数描述                                            |
|-------------------| -- | --- |-------------------------------------------------|
| code              | 200 | Integer |           响应码                                      |
| msg               | success | String ||
| ts                | 1713773577581 | Long ||
| data                | 1个板卡删除实例！ | String |消息内容|

**请求示例**

```javascript
{
    "deviceIps": [
        "172.31.3.3"
    ],
        "remark": "1"
}
```

**响应示例**

```javascript
{
    "msg": "success",
        "code": 200,
        "data": "1个板卡删除实例！",
        "ts": 1739954448827
}

```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110060 | 板卡不存在| 确认下板卡IP是否正确

#### **查询最新预热成功镜像**

**接口类型**: 同步接口

获取最近预热成功的镜像ID列表，最多返回3个记录。

**接口概要**

作用：查询查询最新预热成功镜像。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/device/getLatestWarmupSuccessImages

**请求方式**

> GET

**请求数据类型**

> 无

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | --- | --- | --- |
| customerId | 178 | Long | 否 | 客户ID（管理员可传此参数查询指定客户的镜像，普通用户忽略此参数） |

**说明**:
- 普通用户：无需传参数，自动查询当前用户的预热成功镜像
- 管理员用户：可传 `customerId` 参数查询指定客户的预热成功镜像

**响应参数**

| 参数名                | 示例值             | 参数类型 | 参数描述              |
|--------------------|-----------------| --- |-------------------|
| code               | 200             | Integer | 状态码               |
| msg                | success         | String | 响应消息              |
| ts                 | 1713773577581   | Long | 时间戳               |
| traceId            | ewab8qjqbaio    | String | 链路追踪ID            |
| data               |                 | WarmupSuccessImageVO[] | 最新预热成功镜像信息列表，最多3个 |
| ├─ customerId      | 178             | Long | 客户ID              |
| ├─ customerAccount | testa           | String | 客户账号              |
| ├─ customerName    | 张三              | String | 客户名称              |
| ├─ imageId         | IMG-20250305001 | String | 镜像ID              |
| ├─ imageVersion    | 20251027_1      | String | 镜像版本              |
| ├─ imageDesc       | 测试              | String | 镜像描述              |
| ├─ supportF2fs     | 1               | Integer | 是否支持f2fs(1:支持 0:不支持) |
| ├─ fileTag         | 0               | Integer | 文件标签(1:可删除 0:不能删除)   |
| ├─ androidVersion  | 13              | Integer | 安卓版本              |

**请求示例**

```javascript
/openapi/open/device/getLatestWarmupSuccessImages
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1713773577581,
    "traceId": "ewab8qjqbaio",
    "data": [
        {
            "customerId": 178,
            "customerAccount": "testa",
            "customerName": "张三",
            "imageDesc": "测试",
            "imageVersion": "20251027_1",
            "imageId": "IMG-20250305001",
            "fileTag": 1,
            "supportF2fs": 1,
            "androidVersion": 13
        },
        {
            "customerId": 178,
            "customerAccount": "testa",
            "customerName": "张三",
            "imageDesc": "测试",
            "imageVersion": "20251027_1",
            "imageId": "IMG-20250304002",
            "fileTag": 1,
            "supportF2fs": 1,
            "androidVersion": 13
        },
        {
            "customerId": 178,
            "customerAccount": "testa",
            "customerName": "张三",
            "imageDesc": "测试",
            "imageVersion": "20251027_1",
            "imageId": "IMG-20250303005",
            "fileTag": 1,
            "supportF2fs": 1,
            "androidVersion": 12
        }
    ]
}
```

### 网存2.0

#### 一、网存2.0对比网存1.0

![NetPadV2FlowDoc.png](netPadV2FlowDoc.png)

- 大幅优化了 API 接口，降低开机/关机任务失败率。
- 网存2.0将实例与存储二合一，无需再进行复杂的存储块与实例关系管理，删除实例即删除实例与对应存储。
---

#### 二、快速入门

![netPadV2UseDoc.png](netPadV2UseDoc.png)

1. 购买板卡获得算力
2. 查询板卡信息
3. 设置板卡规格（多开数）
4. 创建网存实例
5. 使用刚创建好的实例或之前关机的实例进行开机
6. 完成业务关机
7. 将单个实例克隆成多个后使用（克隆出的实例是单独的实体，可以修改实例的机型属性、镜像版本等）
---

#### 三、API 接口

##### **创建网存实例**

**接口类型**: 同步接口

用于创建网存2.0实例接口，支持批量创建,最多创建100个实例。

**接口地址**

> `/openapi/open/pad/v2/net/storage/res/create`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名                 | 示例值        | 参数类型    | 是否必填 | 参数描述                                    |
|---------------------|------------|---------|------|-----------------------------------------|
| clusterCode         | 001        | String  | 是    | 集群编码，标识实例所属集群                           |
| specificationCode   | SPEC_001   | String  | 是    | 规格代码，定义实例的硬件规格                          |
| imageId             | IMG_123456 | String  | 是    | 镜像ID，用于创建实例的系统镜像                        |
| number              | 5          | Integer | 是    | 实例数量，必须在1-100之间                         |
| storageSize         | 32         | Integer | 是    | 存储大小(GB)，必须大于0，支持：4,8,16,32,64,128,256  |
| screenLayoutCode    | LAYOUT_001 | String  | 否    | 屏幕布局编码，非随机ADI模板且未传入ADI模板参数时必填           |
| randomADITemplates  | false      | Boolean | 否    | 是否随机选择ADI模板。`true`随机选择/`false`不随机选择，默认`false` |
| excludeRealPhoneTemplateIds | [101,102] | List&lt;Long&gt; | 否    | 随机ADI模板时需排除的模板ID列表，randomADITemplates为true时生效 |
| realPhoneTemplateId | 12345      | Long    | 否    | ADI模板ID，指定使用的ADI模板                      |
| countryCode         | SG         | String  | 否    | 国家编码，默认值`SG`。仅首次开机生效，为空时使用创建时传入的国家编码。[查看所有国家编码↗](./EnumReference.md#51-countrycode---国家编码) |
| groupId             | 0          | Integer | 否    | 分组ID，默认为公共池。                            |

**响应参数**

| 参数名         | 示例值              | 参数类型     | 参数描述          |
| ----------- | ---------------- | -------- | ------------- |
| code        | 200              | Integer  | 状态码（200表示成功）  |
| msg         | success          | String   | 接口请求状态信息      |
| ts          | 1742536327373    | Long     | 时间戳           |
| data        | [ {...} ]        | Object[] | 创建结果列表        |
| ├─ padCode  | ACN1234567890123 | String   | 实例编码          |
| ├─ padName  | 网存实例001         | String   | 实例名称          |
| ├─ status   | 0                | Integer  | 实例状态          |

**请求示例**

```json
{
  "clusterCode": "001",
  "specificationCode": "SPEC_001",
  "imageId": "IMG_123456",
  "number": 5,
  "storageSize": 32,
  "screenLayoutCode": "LAYOUT_001",
  "randomADITemplates": true,
  "excludeRealPhoneTemplateIds": [101, 102],
  "countryCode": "SG"
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": [
    {
      "padCode": "ACN1234567890123",
      "clusterCode": "001",
      "storageSize": 32
    },
    {
      "padCode": "ACN1234567890124",
      "clusterCode": "001",
      "storageSize": 32
    }
  ],
  "ts": 1742536327373
}
```

**错误码**

| 错误码    | 错误说明               | 操作建议                             |
| ------ | ------------------ |----------------------------------|
| 100000 | 集群编码不能为空           | 提供有效的集群编码                        |
| 100000 | 规格代码不能为空           | 提供有效的规格代码                        |
| 100000 | 镜像ID不能为空           | 提供有效的镜像ID                        |
| 100000 | 实例数量必须在1-100之间     | 调整实例数量到有效范围内                     |
| 100000 | 存储大小必须大于0          | 提供有效的存储大小                        |
| 100000 | 屏幕布局编码不能为空         | 在非随机ADI模板并且未指定ADI模板时下提供屏幕布局编码    |
| 100000 | DNS格式错误            | 确认DNS格式是否正确                      |
| 110044 | 实例规格不存在            | 确认规格代码是否正确，联系管理员确认规格配置           |
| 110041 | 镜像不存在              | 确认镜像ID是否正确，检查镜像是否可用              |
| 110045 | 屏幕布局不存在            | 确认屏幕布局编码是否正确                     |
| 110099 | ADI模板不存在,请检查参数     | 确认ADI模板ID是否正确                    |
| 220003 | 暂不支持当前存储规格,请参考文档设置 | 使用支持的存储规格：4,8,16,32,64,128,256GB |
| 220009 | 当前集群存储容量不足,请联系管理员  | 联系管理员增加存储容量或删除清理实例               |
| 110077 | 获取实例MAC失败，请重试      | 稍后重试或联系管理员                       |

##### **网存实例批量开机**

**接口类型**: 异步接口
**关联回调**: [网存2.0开机回调](#网存20开机回调) (taskBusinessType: `1000`)

用于对多个网存实例进行批量开机操作

**接口地址**

> `/openapi/open/pad/v2/net/storage/batch/boot/on`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名         | 示例值                                                 | 参数类型    | 是否必填 | 参数描述                                                                                                                                                                      |
| ----------- |-----------------------------------------------------|---------| ---- |---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| padCodes    | ["ACN250321HRKNE3F", "ACN250321HRKNE3G"]            | String[] | 是    | 需要开机的实例编码列表，数量范围1-200个                                                                                                                                                    |
| dns         | 8.8.8.8                                             | String  | 否    | DNS配置                                                                                                                                                                     |
| countryCode | SG                                                  | String  | 否    | 国家编码，默认值`SG`。 仅实例首次开机时生效，未传入时使用创建实例时传入的国家编码（为空则默认为SG）。[查看所有国家编码↗](./EnumReference.md#51-countrycode---国家编码) |
| androidProp | {"persist.sys.cloud.wifi.mac": "D2:48:83:70:66:0B"} | Object  | 否    | 安卓属性配置，参考 [安卓改机属性列表](https://docs.armcloud.net/cn/server/InstanceAndroidPropList.html)（注意： 时区、语言、国家三个属性目前不生效 ）                                   |
| timeout     | 1800                                                | Integer | 否    | 超时时间（秒），范围300-7200秒（5分钟-120分钟）                                                                                                                                            |
| imageId     | img-25081965158                                      | String  | 否    | 镜像ID，支持开机时更换镜像ID，每次开机传入时均可生效。注意仅支持同版本镜像                                                                                                          |

**响应参数**

| 参数名                       | 示例值                | 参数类型    | 参数描述                                        |
| ------------------------- | ------------------ | ------- | ------------------------------------------- |
| code                      | 200                | Integer | 状态码（200不代表实例操作成功，实例是否操作成功需要自行判断successList） |
| msg                       | success            | String  | 接口请求状态信息                                    |
| ts                        | 1742536327373      | Long    | 时间戳                                         |
| data                      | {...}              | Object  | 操作结果数据                                      |
| ├─ successList            | [{...}]            | Array   | 操作成功的列表（异步回调，代表当前异步执行成功，业务结果需等待回调）          |
| ├─ successList[].taskId   | 13023              | Integer | 任务ID                                        |
| ├─ successList[].padCode  | ACN280512603291648 | String  | 实例编码                                        |
| ├─ successList[].vmStatus | 0                  | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
| ├─ failList               | [{...}]            | Array   | 操作失败的列表，由于业务校验不通过或是其他异常导致的无法操作              |
| ├─ failList[].padCode     | ACN279133733257216 | String  | 实例编码                                        |
| ├─ failList[].errCode     | 110028             | String  | 错误码                                         |
| ├─ failList[].errMsg      | 实例不存在              | String  | 失败原因                                        |
**请求示例**

``` json
{
  "padCodes": ["ACN250321HRKNE3F", "ACN250321HRKNE3G"],
  "dns": "8.8.8.8",
  "countryCode": "US",
  "androidProp": {"persist.sys.cloud.wifi.mac": "D2:48:83:70:66:0B"},
  "timeout": 1800
}
```

**响应示例**

``` json
{
    "code": 200,
    "msg": "success",
    "ts": 1752480095637,
    "data": {
        "successList": [
            {
                "taskId": 10111,
                "padCode": "ACN281696605700096",
                "vmStatus": 0
            }
        ],
        "failList": [
            {
                "errCode": 110028,
                "padCode": "ACN281696605700095",
                "errMsg": "实例不存在"
            },
            {
                "errCode": 110028,
                "padCode": "ACN281696605700094",
                "errMsg": "实例不存在"
            },
            {
                "errCode": 110028,
                "padCode": "ACN281696605700093",
                "errMsg": "实例不存在"
            }
        ]
    }
}
```

**错误码**

| 错误码     | 错误说明                           | 操作建议                     |
| ------- | ------------------------------ | ------------------------ |
| 100000  | 实例编码列表不能为空                     | 确保padCodes参数不为空          |
| 100000  | 实例数量范围1-200                    | 确保padCodes数量在1-200范围内    |
| 100000  | 超时时间必须在5分钟-120分钟之间             | 确保timeout参数在300-7200秒范围内 |
| 100000  | DNS格式错误                        | 确认DNS格式是否正确              |
| 110042  | 存在不属于当前用户的实例                   | 检查实例是否属于当前用户             |
| 110071  | 存在非网存实例                        | 确认实例类型为网存实例              |
| 110079  | 存在未释放算力的实例                     | 等待算力释放后重试                |
| 111070  | 请勿重复操作，当前实例正在开机中               | 等待当前开机操作完成后重试            |
| 111076  | 请勿重复操作，当前实例正在关机中               | 等待关机操作完成后重试              |
| 111071  | 存在非关机且非开机失败状态的实例，不允许操作开机       | 确认实例状态为关机或开机失败状态         |
| 111074  | 网存实例批量开机失败（系统异常）               | 系统异常，请稍后重试或联系技术支持        |
| 110074  | 获取算力单元失败，请重试                   | 稍后重试或联系管理员               |
| 110075  | 获取实例IP失败，请重试                   | 稍后重试                     |
| 110076  | ARM服务器网段不存在                    | 联系管理员检查网段配置              |
| 2200014 | 当前集群下没有可用的算力资源，算力资源不足，请联系管理员处理 | 等待算力资源释放或联系管理员           |
| 111079 | 当前实例所属板卡已离线      | 稍后重试或联系管理员                    |
| 111081 | 不支持网存1.0实例      | 使用网存2.0实例调用接口                 |

##### 网存实例批量关机

**接口类型**: 异步接口
**关联回调**: [网存2.0关机回调](#网存20关机回调) (taskBusinessType: `1001`)

用于对网存2.0实例进行批量关机操作。支持同时关机多个实例，只有运行中或关机失败状态的实例才能进行关机操作。

**接口地址**

> `/openapi/open/pad/v2/net/storage/batch/off`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名      | 示例值                                      | 参数类型 | 是否必填 | 参数描述                                                                                                                    |
|----------|------------------------------------------|---------|------|-------------------------------------------------------------------------------------------------------------------------|
| padCodes | ["ACN250321HRKNE3F", "ACN250321HRKNE3G"] | String[] | 是    | 需要关机的实例编码列表，最多允许同时关机200个实例                                                                                              |
| timeout  | 1800                                     | Integer | 否    | 超时时间（秒），范围：300-7200秒（5分钟-120分钟）                                                                                         |
| forceDel | false                                    | Boolean  | 否    | **请谨慎使用** 是否强制删除。`true`强制删除（直接关机并删除实例，不保留数据）/`false`不强制删除，默认`false`（CBS版本2.3.5以上支持）|

**响应参数**

| 参数名                       | 示例值                | 参数类型    | 参数描述                                        |
| ------------------------- | ------------------ | ------- | ------------------------------------------- |
| code                      | 200                | Integer | 状态码（200不代表实例操作成功，实例是否操作成功需要自行判断successList） |
| msg                       | success            | String  | 接口请求状态信息                                    |
| ts                        | 1742536327373      | Long    | 时间戳                                         |
| data                      | {...}              | Object  | 操作结果数据                                      |
| ├─ successList            | [{...}]            | Array   | 操作成功的列表（异步回调，代表当前异步执行成功，业务结果需等待回调）          |
| ├─ successList[].taskId   | 13023              | Integer | 任务ID                                        |
| ├─ successList[].padCode  | ACN280512603291648 | String  | 实例编码                                        |
| ├─ successList[].vmStatus | 0                  | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
| ├─ failList               | [{...}]            | Array   | 操作失败的列表，由于业务校验不通过或是其他异常导致的无法操作              |
| ├─ failList[].padCode     | ACN279133733257216 | String  | 实例编码                                        |
| ├─ failList[].errCode     | 110028             | String  | 错误码                                         |
| ├─ failList[].errMsg      | 实例不存在              | String  | 失败原因                                        |

**请求示例**

``` json
{
  "padCodes": ["ACN250321HRKNE3F", "ACN250321HRKNE3G"],
  "timeout": 1800
}
```

**响应示例**

``` json
{
    "code": 200,
    "msg": "success",
    "ts": 1752480095637,
    "data": {
        "successList": [
            {
                "taskId": 10111,
                "padCode": "ACN281696605700096",
                "vmStatus": 0
            }
        ],
        "failList": [
            {
                "errCode": 110028,
                "padCode": "ACN281696605700095",
                "errMsg": "实例不存在"
            },
            {
                "errCode": 110028,
                "padCode": "ACN281696605700094",
                "errMsg": "实例不存在"
            },
            {
                "errCode": 110028,
                "padCode": "ACN281696605700093",
                "errMsg": "实例不存在"
            }
        ]
    }
}
```

**错误码**

| 错误码    | 错误说明                        | 操作建议                 |
|--------|-----------------------------| -------------------- |
| 100000 | 实例编码列表不能为空                  | 确保padCodes参数不为空      |
| 100000 | 实例数量范围1-200                 | 确保实例数量在1-200范围内      |
| 100000 | 超时时间必须在5分钟-120分钟之间          | 设置合理的超时时间（300-7200秒） |
| 110028 | 实例不存在                       | 检查实例编码是否正确           |
| 110071 | 存在非网存实例                     | 确保操作的都是网存实例          |
| 110042 | 存在不属于当前用户的实例                | 检查实例归属权限             |
| 111072 | 实例未绑定算力，无法关机                | 确保实例已绑定算力资源          |
| 111073 | 网存实例连续关机失败                  | 检查实例状态，联系管理员处理       |
| 111070 | 请勿重复操作，当前实例正在开机中            | 等待当前开机操作完成后重试        |
| 111076 | 请勿重复操作，当前实例正在关机中            | 等待关机操作完成后重试          |
| 111078 | 存在非运行中且非关机失败状态的实例，不允许操作关机   | 确认实例状态为运行中或关机失败      |
| 111079 | 当前实例所属板卡已离线                 | 稍后重试或联系管理员                    |
| 111080 | CBS版本不支持强制删除                | 有需要请联系管理员升级CBS版本   |
| 111081 | 不支持网存1.0实例                  | 使用网存2.0实例调用接口                 |

##### 网存实例批量删除

**接口类型**: 异步接口
**关联回调**: [网存2.0实例删除回调](#网存20实例删除回调) (taskBusinessType: `-`)

用于批量删除网存实例，支持传入多个实例进行批量删除操作。

**接口地址**

> `/openapi/open/pad/v2/net/storage/batch/delete`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名      | 示例值                                      | 参数类型     | 是否必填 | 参数描述                           |
| -------- | ---------------------------------------- | -------- | ---- | ------------------------------ |
| padCodes | ["ACN250321HRKNE3F", "ACN250321HRKNE3G"] | String[] | 是    | 需要删除的实例编码列表，数量范围1-200个         |
| timeout  | 1800                                     | Integer  | 否    | 超时时间（秒），范围300-7200秒（5分钟-120分钟） |

**响应参数**

| 参数名                       | 示例值                | 参数类型    | 参数描述                                          |
| ------------------------- | ------------------ | ------- | --------------------------------------------- |
| code                      | 200                | Integer | 状态码（200不代表全部实例操作成功，实例是否操作成功需要自行判断successList） |
| msg                       | success            | String  | 接口请求状态信息                                      |
| ts                        | 1742536327373      | Long    | 时间戳                                           |
| data                      | {...}              | Object  | 操作结果数据                                        |
| ├─ successList            | [{...}]            | Array   | 操作成功的列表（异步回调，代表当前异步执行成功，业务结果需等待回调）            |
| ├─ successList[].taskId   | 13023              | Integer | 任务ID                                          |
| ├─ successList[].padCode  | ACN280512603291648 | String  | 实例编码                                          |
| ├─ successList[].vmStatus | 0                  | Integer | 实例状态                                          |
| ├─ failList               | [{...}]            | Array   | 操作失败的列表，由于业务校验不通过或是其他异常导致的无法操作                |
| ├─ failList[].padCode     | ACN279133733257216 | String  | 实例编码                                          |
| ├─ failList[].errCode     | 110028             | String  | 错误码                                           |
| ├─ failList[].errMsg      | 实例不存在              | String  | 失败原因                                          |
| ├─ completeList           | [{...}]            | Array   | 操作完成的列表，不需要进行异步操作的实例                          |
| ├─ completeList[].padCode | ACN279133733257231 | String  | 实例编码                                          |

**请求示例**

``` json
{
  "padCodes": ["ACN250321HRKNE3F", "ACN250321HRKNE3G"],
  "timeout": 1800
}
```

**响应示例**

``` json
{
    "code": 200,
    "msg": "success",
    "ts": 1752480095637,
    "data": {
        "successList": [
            {
                "taskId": 10111,
                "padCode": "ACN281696605700096",
                "vmStatus": 0
            }
        ],
        "failList": [
            {
                "errCode": 110028,
                "padCode": "ACN281696605700095",
                "errMsg": "实例不存在"
            },
            {
                "errCode": 110028,
                "padCode": "ACN281696605700094",
                "errMsg": "实例不存在"
            },
            {
                "errCode": 110028,
                "padCode": "ACN281696605700093",
                "errMsg": "实例不存在"
            }
        ],
        "completeList": [
            {
                "padCode": "ACN281696605700096"
            }
        ]
    }
}
```

**错误码**

| 错误码    | 错误说明               | 操作建议                       |
| ------ | ------------------ | -------------------------- |
| 100000 | 实例编码列表不能为空         | 检查padCodes参数是否传递           |
| 100000 | 实例数量范围1-200        | 检查padCodes数组长度是否在有效范围内     |
| 100000 | 超时时间必须在5分钟-120分钟之间 | 检查timeout参数是否在300-7200秒范围内 |
| 110028 | 实例不存在              | 检查传入的实例编码是否正确              |
| 110042 | 存在不属于当前用户的实例       | 检查实例是否属于当前登录用户             |
| 110071 | 存在非网存实例            | 确认传入的实例都是网存实例              |
| 111070 | 请勿重复操作，当前实例正在开机中   | 等待开机操作完成后再进行删除             |
| 111073 | 当前实例非关机状态实例不允许删除   | 确保所有实例都处于关机状态再进行删除         |
| 111077 | 请勿重复操作，当前实例正在删除中   | 等待当前删除操作完成                 |
| 111079 | 当前实例所属板卡已离线      | 稍后重试或联系管理员                    |
| 111081 | 不支持网存1.0实例      | 使用网存2.0实例调用接口                 |

##### **网存实例克隆**

**接口类型**: 异步接口
**关联回调**: 通过返回的 `taskId` 轮询[实例操作任务详情](#实例操作任务详情)接口查询任务状态，建议查询间隔至少30秒

用于对单个网存实例进行克隆操作，支持指定克隆数量和备注信息。该接口只支持关机状态且已开机过的网存2.0实例。另外需要特别注意：**一定要接入回调处理，克隆成功后创建的实例会在回调信息中返回。**

**接口地址**

> /openapi/open/pad/v2/net/storage/clone

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名     | 示例值              | 参数类型    | 是否必填 | 参数描述          |
| ------- | ---------------- | ------- | ---- | ------------- |
| padCode | ACN250321HRKNE3F | String  | 是    | 需要克隆的原始实例编码   |
| number  | 2                | Integer | 是    | 克隆数量，范围1-100个 |

**响应参数**

| 参数名                       | 示例值                | 参数类型    | 参数描述                               |
| ------------------------- | ------------------ | ------- | ---------------------------------- |
| code                      | 200                | Integer | 状态码，200表示成功                        |
| msg                       | success            | String  | 接口请求状态信息                           |
| ts                        | 1742536327373      | Long    | 时间戳                                |
| data                      | {...}              | Object  | 克隆结果信息                             |
| ├─ successList            | [{...}]            | Array   | 操作成功的列表（异步回调，代表当前异步执行成功，业务结果需等待回调） |
| ├─ successList[].taskId   | 13023              | Integer | 任务ID                               |
| ├─ successList[].padCode  | ACN280512603291648 | String  | 实例编码                               |
| ├─ successList[].vmStatus | 0                  | Integer | 实例状态                               |
| ├─ failList               | [{...}]            | Array   | 操作失败的列表，由于业务校验不通过或是其他异常导致的无法操作     |
| ├─ failList[].padCode     | ACN279133733257216 | String  | 实例编码                               |
| ├─ failList[].errCode     | 110028             | String  | 错误码                                |
| ├─ failList[].errMsg      | 实例不存在              | String  | 失败原因                               |

**请求示例**

``` json
{
    "padCode": "ACN250321HRKNE3F",
    "number": 2,
    "remark": "测试克隆"
}
```

**响应示例**

```  json
{
    "msg": "success",
    "code": 200,
    "data": {
        "successList": [
            {
                "taskId": 13023,
                "padCode": "ACN250321HRKNE3F",
                "vmStatus": 0
            }
        ],
        "failList": []
    },
    "ts": 1742536327373
}
```

**回调示例**
``` json
{
  "endTime": 1754724268268,
  "padCode": "ACN319190980034587",
  "taskBusinessType": 1304,
  "taskContent": "[\"ACN319348753039360\",\"ACN319348753039363\",\"ACN319348753039366\",\"ACN319348753039369\",\"ACN319348753039372\",\"ACN319348753039375\",\"ACN319348753039378\",\"ACN319348753039381\",\"ACN319348753039384\",\"ACN319348753039387\"]",
  "taskId": 10682,
  "taskResult": "Success",
  "taskStatus": 3
}
```
**错误码**

| 错误码    | 错误说明             | 操作建议              |
| ------ | ---------------- |-------------------|
| 100000 | 请求参数不正确          | 检查请求参数是否完整        |
| 100000 | 实例编号不能为空         | 确保padCode参数不为空    |
| 100000 | 克隆数量不能为空且必须大于0   | 确保number参数大于0且不为空 |
| 100000 | 克隆数量不能超过100      | 确保number参数不超过100  |
| 111081 | 不支持网存1.0实例       | 确保实例类型为网存V2实例     |
| 110028 | 实例不存在            | 检查实例编码是否正确        |
| 111083 | 非关机状态的实例不允许克隆    | 确保实例状态为关机状态       |
| 111085 | 实例不存在开机行为，不允许克隆  | 确保实例至少开机过一次       |
| 111082 | 网存存储单元不存在        | 检查实例存储配置是否正常      |
| 111086 | 实例开机后未产生数据，不允许克隆 | 确保实例有有效的存储数据      |
| 111087 | CBS版本不支持克隆，请升级CBS版本后重试 | 请联系升级CBS版本        |
| 111084 | 请勿重复操作，当前实例正在克隆中 | 最好不要并发调用          |
| 111070 | 请勿重复操作，当前实例正在开机中 | 最好不要并发调用          |
| 111076 | 请勿重复操作，当前实例正在关机中 | 最好不要并发调用          |
| 111077 | 请勿重复操作，当前实例正在删除中 | 最好不要并发调用          |
| 500    | 系统异常             | 系统异常，请稍后重试或联系技术支持 |

### 应用安全策略V2.0

#### 一、API 接口

**接口类型**: 同步接口

##### **分页查询应用安全策略组列表**

**接口类型**: 同步接口

用于分页查询应用安全策略组列表，支持按策略组名称和类型进行筛选，使用lastId+rows方式分页查询。

**接口地址**

> `/openapi/open/appSecurityPolicyGroup/pageList`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| policyName | 测试策略组 | String | 否 | 策略组名称（模糊查询） |
| policyType | 0 | Integer | 否 | 策略组类型。可选值：`0`黑名单/`1`白名单。[详见枚举↗](./EnumReference.md#23-policytype---策略组类型) |
| lastId | 0 | Long | 否 | 上次查询的最后一条记录ID，首次查询传null或0 |
| rows | 10 | Integer | 是 | 查询数量，范围1-1000，默认10 |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
|--------|--------|----------|----------|
| code | 200 | Integer | 状态码（200表示成功） |
| msg | success | String | 接口请求状态信息 |
| ts | 1742536327373 | Long | 时间戳 |
| data | {...} | Object | 分页结果数据 |
| ├─ pageData | [{...}] | Array | 策略组列表 |
| ├─ pageData[].id | 123 | Long | 策略组ID |
| ├─ pageData[].policyName | 测试策略组 | String | 策略组名称 |
| ├─ pageData[].policyType | 0 | Integer | 策略组类型。可选值：`0`黑名单/`1`白名单。[详见枚举↗](./EnumReference.md#23-policytype---策略组类型) |
| ├─ pageData[].appCount | 5 | Integer | 应用数量 |
| ├─ pageData[].padCount | 10 | Integer | 实例数量 |
| ├─ pageData[].remark | 备注信息 | String | 备注 |
| ├─ pageData[].createTime | 2025-01-29 10:00:00 | String | 创建时间 |
| ├─ pageData[].updateTime | 2025-01-29 10:00:00 | String | 更新时间 |
| ├─ lastId | 123 | Long | 最后一条记录ID，用于下次分页查询 |
| ├─ rows | 10 | Integer | 查询数量 |
| ├─ size | 10 | Integer | 当前页的数量 |
| ├─ hasNext | true | Boolean | 是否还有下一页 |

**请求示例**

```json
{
  "policyName": "测试",
  "policyType": 0,
  "lastId": 0,
  "rows": 10
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": {
    "pageData": [
      {
        "id": 123,
        "policyName": "测试策略组",
        "policyType": 0,
        "appCount": 5,
        "padCount": 10,
        "remark": "备注信息",
        "createTime": "2025-01-29 10:00:00",
        "updateTime": "2025-01-29 10:00:00"
      }
    ],
    "lastId": 123,
    "rows": 10,
    "size": 10,
    "hasNext": true
  },
  "ts": 1742536327373
}
```

##### **查询应用安全策略组详情**

**接口类型**: 同步接口

用于根据策略组ID查询应用安全策略组的详细信息，包括关联的应用和实例信息。

**接口地址**

> `/openapi/open/appSecurityPolicyGroup/detail`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| id | 123 | Long | 是 | 策略组ID |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
|--------|--------|----------|----------|
| code | 200 | Integer | 状态码（200表示成功） |
| msg | success | String | 接口请求状态信息 |
| ts | 1742536327373 | Long | 时间戳 |
| data | {...} | Object | 策略组详情数据 |
| ├─ id | 123 | Long | 策略组ID |
| ├─ policyName | 测试策略组 | String | 策略组名称 |
| ├─ policyType | 0 | Integer | 策略组类型。可选值：`0`黑名单/`1`白名单。[详见枚举↗](./EnumReference.md#23-policytype---策略组类型) |
| ├─ appNum | 5 | Integer | 应用数量 |
| ├─ padNum | 10 | Integer | 实例数量 |
| ├─ remark | 备注信息 | String | 备注 |
| ├─ appInfos | [{...}] | Array | 应用信息列表 |
| ├─ appInfos[].fileId | 456 | Long | 文件ID |
| ├─ appInfos[].appId | 789 | Long | 应用ID |
| ├─ appInfos[].appName | 测试应用 | String | 应用名称 |
| ├─ appInfos[].packageName | com.test.app | String | 包名 |
| ├─ appInfos[].appVersionNo | 1 | Integer | 应用版本号 |
| ├─ appInfos[].appVersionName | 1.0.0 | String | 应用版本名称 |
| ├─ padInfos | [{...}] | Array | 实例信息列表 |
| ├─ padInfos[].padcode | ACN1234567890123 | String | 实例code |
| ├─ padInfos[].padType | real | String | 实例类型。可选值：`real`云真机/`virtual`虚拟机。[详见枚举↗](./EnumReference.md#22-padtype---实例类型) |
| ├─ padInfos[].padImageId | img_123456 | String | 实例镜像ID |
| ├─ padInfos[].padImageAosp | 10 | String | 实例镜像AOSP版本 |
| ├─ padInfos[].padImageVersion | 20251023_2 | String | 实例镜像版本 |
| ├─ padInfos[].padIp | 192.168.1.100 | String | 实例IP |

**请求示例**

```
POST /openapi/open/appSecurityPolicyGroup/detail?id=123
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": {
    "id": 123,
    "policyName": "测试策略组",
    "policyType": 0,
    "appNum": 5,
    "padNum": 10,
    "remark": "备注信息",
    "appInfos": [
      {
        "fileId": 456,
        "appId": 789,
        "appName": "测试应用",
        "packageName": "com.test.app",
        "appVersionNo": 1,
        "appVersionName": "1.0.0"
      }
    ],
    "padInfos": [
      {
        "padcode": "ACN1234567890123",
        "padType": "real",
        "padImageId": "img_123456",
        "padImageAosp": "10",
        "padImageVersion": "20251023_2",
        "padIp": "192.168.1.100"
      }
    ]
  },
  "ts": 1742536327373
}
```

##### **新增/更新应用安全策略组**

**接口类型**: 同步接口

用于新增或更新应用安全策略组。当传入id时更新，不传id时新增。

**接口地址**

> `/openapi/open/appSecurityPolicyGroup/save`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| id | 123 | Long | 否 | 策略组ID（更新时必填，新增时可为空） |
| policyName | 测试策略组 | String | 是 | 策略组名称（不可重复） |
| policyType | 0 | Integer | 是 | 策略组类型。可选值：`0`黑名单/`1`白名单。[详见枚举↗](./EnumReference.md#23-policytype---策略组类型) |
| remark | 备注信息 | String | 否 | 备注 |
| appInfos | [{...}] | Array | 否 | 应用信息列表（传null不做更新，传空数组[]清空） |
| ├─ appInfos[].appId | 789 | Long | 否 | 应用ID（appId和packageName二选一）通过应用上传可获取到appId |
| ├─ appInfos[].packageName | com.test.app | String | 否 | 包名（appId和packageName二选一）appId有效时该字段不生效 |
| padCodes | ["ACN1234567890123"] | String[] | 否 | 实例code列表（传null不做更新，传空数组[]清空）  |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
|--------|--------|----------|----------|
| code | 200 | Integer | 状态码（200表示成功） |
| msg | success | String | 接口请求状态信息 |
| ts | 1742536327373 | Long | 时间戳 |
| data | 123 | Long | 策略组ID |

**请求示例**

```json
{
  "policyName": "测试策略组",
  "policyType": 0,
  "remark": "备注信息",
  "appInfos": [
    {
      "appId": 789
    },
    {
      "packageName": "com.test.app"
    }
  ],
  "padCodes": ["ACN1234567890123"]
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": 123,
  "ts": 1742536327373
}
```

##### **删除应用安全策略组**

**接口类型**: 同步接口

用于根据策略组ID删除应用安全策略组。

**接口地址**

> `/openapi/open/appSecurityPolicyGroup/delete`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| id | 123 | Long | 是 | 策略组ID |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
|--------|--------|----------|----------|
| code | 200 | Integer | 状态码（200表示成功） |
| msg | success | String | 接口请求状态信息 |
| ts | 1742536327373 | Long | 时间戳 |
| data | null | Object | 无数据返回 |

**请求示例**

```
POST /openapi/open/appSecurityPolicyGroup/delete?id=123
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": null,
  "ts": 1742536327373
}
```

##### **实例更换策略组**

**接口类型**: 同步接口

用于将实例更换为指定的策略组集合，入参为实例编号 + 策略组id集合。

**接口地址**

> `/openapi/open/appSecurityPolicyGroup/changePadPolicyGroups`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| padCode | ACN1234567890123 | String | 是 | 实例编号 |
| policyGroupIds | [123, 456] | Long[] | 是 | 策略组ID集合（最多100个） |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
|--------|--------|----------|----------|
| code | 200 | Integer | 状态码（200表示成功） |
| msg | success | String | 接口请求状态信息 |
| ts | 1742536327373 | Long | 时间戳 |
| data | null | Object | 无数据返回 |

**请求示例**

```json
{
  "padCode": "ACN1234567890123",
  "policyGroupIds": [123, 456]
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": null,
  "ts": 1742536327373
}
```

##### **查询实例关联策略组**

**接口类型**: 同步接口

用于根据实例编号集合查询每个实例关联的全部策略组。

**接口地址**

> `/openapi/open/appSecurityPolicyGroup/queryPadPolicyGroups`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| padCodes | ["ACN1234567890123", "ACN1234567890124"] | String[] | 是 | 实例编号集合 |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
|--------|--------|----------|----------|
| code | 200 | Integer | 状态码（200表示成功） |
| msg | success | String | 接口请求状态信息 |
| ts | 1742536327373 | Long | 时间戳 |
| data | [{...}] | Array | 实例关联策略组列表 |
| ├─ padCode | ACN1234567890123 | String | 实例编号 |
| ├─ policyGroups | [{...}] | Array | 关联的策略组列表 |
| ├─ policyGroups[].id | 123 | Long | 策略组ID |
| ├─ policyGroups[].policyName | 测试策略组 | String | 策略组名称 |
| ├─ policyGroups[].policyType | 0 | Integer | 策略组类型。可选值：`0`黑名单/`1`白名单。[详见枚举↗](./EnumReference.md#23-policytype---策略组类型) |
| ├─ policyGroups[].appCount | 5 | Integer | 应用数量 |
| ├─ policyGroups[].remark | 备注信息 | String | 备注 |

**请求示例**

```json
{
  "padCodes": ["ACN1234567890123", "ACN1234567890124"]
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": [
    {
      "padCode": "ACN1234567890123",
      "policyGroups": [
        {
          "id": 123,
          "policyName": "测试策略组",
          "policyType": 0,
          "appCount": 5,
          "remark": "备注信息"
        }
      ]
    }
  ],
  "ts": 1742536327373
}
```

##### **策略组追加更新**

**接口类型**: 同步接口

用于策略组追加更新，可追加应用或实例。入参为策略组id + 应用集合 + 实例编号集合。

**接口地址**

> `/openapi/open/appSecurityPolicyGroup/appendRelations`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| policyGroupId | 123 | Long | 是 | 策略组ID |
| appInfos | [{...}] | Array | 否 | 应用信息列表（最多100个），每个应用信息appId和packageName二选一 |
| ├─ appInfos[].appId | 789 | Long | 否 | 应用ID（appId和packageName二选一） |
| ├─ appInfos[].packageName | com.test.app | String | 否 | 包名（appId和packageName二选一）同时存在时以有效appId为准 |
| padCodes | ["ACN1234567890123"] | String[] | 否 | 实例编号集合（最多100个） |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
|--------|--------|----------|----------|
| code | 200 | Integer | 状态码（200表示成功） |
| msg | success | String | 接口请求状态信息 |
| ts | 1742536327373 | Long | 时间戳 |
| data | null | Object | 无数据返回 |

**请求示例**

```json
{
  "policyGroupId": 123,
  "appInfos": [
    {
      "appId": 789
    },
    {
      "packageName": "com.test.app"
    }
  ],
  "padCodes": ["ACN1234567890123"]
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": null,
  "ts": 1742536327373
}
```

##### **策略组删除应用/实例**

**接口类型**: 同步接口

用于策略组删除应用/实例，应用列表与实例列表不能同时为空。

**接口地址**

> `/openapi/open/appSecurityPolicyGroup/removeRelations`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| policyGroupId | 123 | Long | 是 | 策略组ID |
| appInfos | [{...}] | Array | 否 | 应用信息列表（最多100个），每个应用信息appId和packageName二选一 |
| ├─ appInfos[].appId | 789 | Long | 否 | 应用ID（appId和packageName二选一） |
| ├─ appInfos[].packageName | com.test.app | String | 否 | 包名（appId和packageName二选一）同时存在时以有效appId为准 |
| padCodes | ["ACN1234567890123"] | String[] | 否 | 实例编号集合（最多100个） |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
|--------|--------|----------|----------|
| code | 200 | Integer | 状态码（200表示成功） |
| msg | success | String | 接口请求状态信息 |
| ts | 1742536327373 | Long | 时间戳 |
| data | null | Object | 无数据返回 |

**请求示例**

```json
{
  "policyGroupId": 123,
  "appInfos": [
    {
      "appId": 789
    },
    {
      "packageName": "com.test.app"
    }
  ],
  "padCodes": ["ACN1234567890123"]
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": null,
  "ts": 1742536327373
}
```

### 网存1.0

#### **创建网存实例**

**接口类型**: 同步接口

用于在指定集群中创建网存实例（默认类型为虚拟机）

**接口概要**

作用：创建创建网存实例。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/pad/net/storage/res/create

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值                      | 参数类型    | 是否必填 | 参数描述
--- |--------------------------|---------|------| ---
clusterCode | 001                      | String  | 是    | 集群代码，标识实例所属集群
specificationCode | m2-3                     | String  | 是    | 规格代码，定义实例的性能配置
imageId | img-25021828327          | String  | 是    | 镜像ID，指定系统镜像
screenLayoutCode | realdevice_1440x3120x560 | String  | 是    | 屏幕布局代码
number | 2                        | Integer | 是    | 需要创建的实例数量
dns | 8.8.8.8                  | String  | 否    | DNS服务器地址
storageSize | 16                       | Integer | 是    | 存储大小（GB）
randomADITemplates | true                     | boolean | 否    | 随机ADI模板（该值为true为真机,并随机填充一个adi模板）
excludeRealPhoneTemplateIds | [36,37]                 | Long[] | 否    | 随机ADI模板时需排除的模板ID列表，randomADITemplates为true时生效
realPhoneTemplateId | 36                       | Integer | 否    | 真实设备模板ID
groupId             | 0          | Integer | 否    | 分组ID，默认为公共池。

**响应参数**

参数名 | 示例值                                 | 参数类型 | 参数描述
--- |-------------------------------------| --- |--------------
code | 200                                 | Integer | 状态码（200表示成功）
msg | success                             | String | 接口请求状态信息
ts | 1742536074329                       | Long | 时间戳
data | 实例创建成功                              | String | 业务返回信息
| ├─padCode | ACN250424UPHQOTG                    |Integer | 实例编号         |
| ├─screenLayoutCode | realdevice_1440x3120x560            |String | 屏幕布局编号       |
| ├─netStorageResId | “ZSC250424G4S6RH1-ACN250424UPHQOTG” |String | 网存code       |
| ├─deviceLevel | “m2-4”                              |String | 实例规格         |
| ├─clusterCode | “006”                               |String | 集群编号         |

**请求示例**

```json
{
  "clusterCode": "001",
  "specificationCode": "m2-3",
  "imageId": "img-25021828327",
  "screenLayoutCode": "realdevice_1440x3120x560",
  "isolateCpu": true,
  "isolateMemory": true,
  "number": 2,
  "isolateStorage": true,
  "dns": "8.8.8.8",
  "storageSize": 16,
  "randomADITemplates": true,
  "excludeRealPhoneTemplateIds": [36, 37],
  "realPhoneTemplateId": 36
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": [
    {
      "padCode": "ACN250424UPHQOTG",
      "cloudVendorType": 3,
      "memory": 8192,
      "groupId": 0,
      "storage": 45,
      "padIp": null,
      "streamType": 1,
      "padSn": 1,
      "armServerCode": null,
      "screenLayoutCode": "realdevice_1440x3120x560",
      "netStorageResSize": 16,
      "imageId": "img-25041475147",
      "dns": "8.8.8.8",
      "dataSize": 17179869184,
      "dataSizeAvailable": null,
      "cpu": -1,
      "clusterCode": "006",
      "netStorageResId": "ZSC250424G4S6RH1-ACN250424UPHQOTG",
      "realPhoneTemplateId": null,
      "dataSizeUsed": null,
      "netStorageResFlag": 1,
      "deviceLevel": "m2-4",
      "online": 0,
      "socModel": "MACS2080",
      "streamStatus": 0,
      "status": 1
    }
  ],
  "ts": 1745465574610
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | -- | ---
220003 | 暂不支持当前存储规格,请参考文档设置| 当前支持固定存储值(4, 16, 32, 64, 128, 256)
110099 | ADI模板不存在,请检查参数| 确认ADI模板的值存在且未被禁用
110044 | 实例规格不存在 | 目前支持m2-1~10
220009 | 当前网存容量不足,请联系管理员 | 联系管理员增加网存容量或者删除掉一些不用的实例释放空间
110041 | 镜像不存在 | 确认镜像ID是否正确
110045 | 屏幕布局不存在 | 确认屏幕布局代码是否正确

#### **网存实例开机**

**接口类型**: 异步接口
**关联回调**: [网存实例开机回调](#网存实例开机回调) (taskBusinessType: `1000`)

用于在指定集群中对网存实例进行开机操作。如果传入国家code无法匹配,将使用默认code:SG

**接口概要**

作用：处理网存实例开机。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/net/storage/on

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- |------| ---
clusterCode | 001 | String | 否    | 集群代码，标识实例所属集群
androidProp | {"persist.sys.cloud.wifi.mac": "D2:48:83:70:66:0B"} | Object  | 否    | 参考 [安卓改机属性列表](./InstanceAndroidPropList.html)（注意： 时区、语言、国家三个属性目前不生效 ）
countryCode | SG                                                  | String  | 否    | 国家编码，默认值`SG`。[查看所有国家编码↗](./EnumReference.md#51-countrycode---国家编码)
padCodes | ["ACN250321HRKNE3F"] | String[] | 是    | 需要开机的实例编码列表,最多允许同时开机200个实例
imageId     | img-25081965158                                      | String  | 否    | 镜像ID，支持开机时更换镜像ID，每次开机传入时均可生效。注意仅支持同版本镜像

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码（200表示成功）
msg | success | String | 接口请求状态信息
ts | 1742536327373 | Long | 时间戳
data | [ {...} ] | Object[] | 实例状态信息列表
├─ padCode | ACN250321HRKNE3F | String | 实例编码
├─ vmStatus | 0 | Integer | 实例状态（0 表示已启动）。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─ taskId | 13023 | Integer | 后台任务ID

**请求示例**

```json
{
  "clusterCode": "001",
  "padCodes": ["ACN250321HRKNE3F"],
   "countryCode":"US",
   "androidProp": "{\"persist.sys.cloud.wifi.mac\": \"D2:48:83:70:66:0B\"}"
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": [
    {
      "padCode": "ACN250321HRKNE3F",
      "vmStatus": 0,
      "taskId": 13023
    }
  ],
  "ts": 1742536327373
}

```

**错误码**

错误码 | 错误说明|操作建议
--- | -- | ---
110095 | 没有可以开机的实例,请检查实例状态 | 确认实例状态是否为关机状态
220011 | 频繁操作网存实例,请稍后再试 | 稍后再试
110101 | 未找到与实例规格匹配的板卡，请前往板卡列表设置规格。 | 确认实例的规格跟板卡规格一致,并且板卡有算力未被占用

#### **网存实例关机**

**接口类型**: 异步接口
**关联回调**: [网存实例关机回调](#网存实例关机回调) (taskBusinessType: `1001`)

用于在指定集群中对网存实例执行关机操作。

**接口概要**

作用：处理网存实例关机。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/net/storage/off

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- |------|------------------------------------------------------------------------------------------------------------------------
clusterCode | 001 | String | 否    | 集群代码，标识实例所属集群
padCodes | ["ACN250321HRKNE3F"] | String[] | 是    | 需要关机的实例编码列表
forceDel | false              | Boolean  | 否    | **请谨慎使用** 是否强制删除。`true`强制删除（直接关机并删除实例，不保留数据）/`false`不强制删除，默认`false`。CBS版本2.3.5以上支持 |

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码（200表示成功）
msg | success | String | 接口请求状态信息
ts | 1742536327373 | Long | 时间戳
data | [ {...} ] | Object[] | 关机结果信息列表
├─ padCode | ACN250321HRKNE3F | String | 实例编码
├─ vmStatus | 0 | Integer | 实例状态（0 表示已关机）
├─ taskId | 13023 | Integer | 后台任务ID

**请求示例**

```json
{
  "clusterCode": "001",
  "padCodes": ["ACN250321HRKNE3F"]
}
```

**响应示例**

```json
{
"msg": "success",
"code": 200,
"data": [
{
"padCode": "ACN250321HRKNE3F",
"vmStatus": 0,
"taskId": 13023
}
],
"ts": 1742536327373
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | -- | ---
110094 | 没有可以关机的实例,请检查实例状态 | 确认实例状态(关机状态跟开机中状态无法关机)

#### **删除网存实例**

**接口类型**: 异步接口
**关联回调**: [网存实例删除回调](#网存实例删除回调) (taskBusinessType: `-`)

用于在指定集群中删除指定的网存实例。

**接口概要**

作用：修改删除网存实例。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/net/storage/delete

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
clusterCode | "" | String | 否 | 集群代码，标识实例所属集群（可为空）
padCodes | ["ACN250321GYWUP8J"] | String[] | 是 | 需要删除的实例编码列表

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码（200表示成功）
msg | success | String | 接口请求状态信息
ts | 1742536423100 | Long | 时间戳
data | [ {...} ] | Object[] | 删除结果信息列表
├─ padCode | ACN250321GYWUP8J | String | 实例编码
├─ vmStatus | 0 | Integer | 实例状态（0 表示已删除或已关机）
├─ taskId | 13025 | Integer | 后台任务ID

**请求示例**

```json
{
  "clusterCode": "",
  "padCodes": ["ACN250321GYWUP8J"]
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": [
    {
      "padCode": "ACN250321GYWUP8J",
      "vmStatus": 0,
      "taskId": 13025
    }
  ],
  "ts": 1742536423100
}

```

**错误码**

错误码 | 错误说明|操作建议
--- | -- | ---
110096 | 当前实例状态无法删除,请检查实例状态 | 确认实例状态(只有关机状态的实例可以允许被删除)

#### **查询网存集群详情**

**接口类型**: 同步接口

用于查询指定集群的存储资源信息，包括已使用存储容量、总存储容量以及剩余可用存储容量等。

**接口概要**

作用：查询查询网存集群详情。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/pad/net/detail/storageCapacity/available

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
clusterCode | "002" | String | 是 | 集群编号，用于查询指定集群的存储资源信息

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码（200表示成功）
msg | success | String | 接口请求状态信息
ts | 1742476224830 | Long | 时间戳
data | {} | Object | 返回的数据对象
data.netStorageResList | null | Object | 网存资源列表
data.storageCapacityUsedTotal | 0 | Integer | 已使用存储容量
data.storageCapacityTotal | 0 | Integer | 总存储容量
data.storageCapacityAvailable | 0 | Integer | 剩余可用存储容量

**请求示例**

```json
{
  "clusterCode": "002"
}
```

**响应示例**

```json
{
  "code": 200,
  "data": [
    {
      "clusterCode": "001",
      "netStorageResList": [
        {
          "clusterCode": "001",
          "createTime": "2025-04-11 11:51:00",
          "dcCode": "001",
          "netStorageResId": 5,
          "storageCapacity": 800,
          "storageCapacityUsed": 0,
          "updateBy": "0",
          "updateTime": "2025-04-23 19:10:00"
        }
      ],
      "storageCapacityAvailable": 800,
      "storageCapacityTotal": 800,
      "storageCapacityUsedTotal": 0
    }
  ],
  "msg": "success",
  "ts": 1745406673542
}
```

#### **设置网存集群板卡规格**

**接口类型**: 同步接口

用于设置指定设备的板卡规格等级。

**接口概要**

作用：修改设置网存集群板卡规格。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/device/net/setDeviceLevel

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
deviceCodes | `["ACD250320R4I7OLM", "ACD250320UEH4OV3"]` | Array | 是 | 设备编码列表，包含需要设置规格的板卡的编码
deviceLevel | `"m2-8"` | String | 是 | 设置的设备规格等级

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码（200表示成功）
msg | success | String | 接口请求状态信息
ts | 1742526263389 | Long | 时间戳
data | "" | String | 业务返回信息

**请求示例**

```json
{
  "deviceCodes": ["ACD250320R4I7OLM", "ACD250320UEH4OV3"],
  "deviceLevel": "m2-8"
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": "",
  "ts": 1742526263389
}
```

错误码 | 错误说明|操作建议
--- | -- | ---
220002 | 当前规格不存在，请检查参数 | 确认规格代码是否正确
220007 | 操作的板卡不存在，请检查参数 | 确认板卡编码是否正确
220008 | 当前板卡存在运行中的算力单元，无法修改 | 板卡上有运行的实例,无法修改规格,需要先将板卡上的实例关机

#### **网存存储备份**

**接口类型**: 异步接口
**关联回调**: [网存存储备份回调](#网存存储备份回调) (taskBusinessType: `-`)

用于发起网存存储备份任务，系统将为每个传入的网存资源编号生成一个对应的备份任务。

**接口概要**

作用：修改网存存储备份。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/net/storage/pad/backup

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | -- | --- | --- | ---
remark | 谷歌验证已经登录 | String | 是 | 备份标记信息
padCodes | `["ACN250403SFPIB1N"]` | List&lt;String&gt; | 是 | 实例padCode，最少 1 个，最多 200 个

**响应参数**

网存存储资源编号列表

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码（200表示成功）
msg | success | String | 接口请求状态信息
ts | 1743664828338 | Long | 时间戳
data | `[ { "padCode": "ZSC2504034L6B26X-ACN250403SFPIB1N", "vmStatus": 0, "taskId": 10350 } ]` | List&lt;GeneratePadTaskVO&gt;  | 备份存储code列表

**请求示例**

```json
{
  "padCodes": [
    "ACN250403SFPIB1N"
  ],
  "remark": "谷歌验证已经登录"
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": [
    {
      "padCode": "ZSC2504034L6B26X-ACN250403SFPIB1N",
      "vmStatus": 0,
      "taskId": 10350
    }
  ],
  "ts": 1743664828338
}
```

错误码 | 错误说明|操作建议
--- | -- | ---
220009 | 无法操作不属于自己的存储单元,请检查参数 | 确认存储code填写正确
220010 | 处于开机中的网存无法备份,请检查数据 | 存储只有关机状态才允许备份
220001 | 当前批次实例中存在未关机的实例，请检查实例状态 |

#### **指定网存ID的网存实例开机(还原)**

**接口类型**: 异步接口
**关联回调**: [网存实例开机回调](#网存实例开机回调) (taskBusinessType: `1000`)

用于为指定网存资源编号（netStorageResUnitCode）绑定的实例开机。如果传入国家code无法匹配,将使用默认code:SG
在进行指定存储开机时，以下情形需要进行拦截：

**接口概要**

作用：修改指定网存ID的网存实例开机(还原)。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

1. **跨设备类型**：
    - 虚拟机 —— 云真机
    - 云真机 —— 虚拟机

2. **跨真机品牌、型号(实例未开机除外)**：
    - A品牌云真机 —— B品牌云真机（例如：Samsung —— Xiaomi）
    - A品牌1型号云真机 —— A品牌2型号云真机（例如：Samsung Galaxy A53 —— Samsung Galaxy A71）

3. **跨镜像版本**：
    - 安卓13 —— 安卓14
    - 安卓13 —— 安卓10
    - 安卓14 —— 安卓13
    - 安卓14 —— 安卓10
    - 安卓10 —— 安卓13
    - 安卓10 —— 安卓14

**接口地址**

> /openapi/open/pad/net/storage/specifiedCode/on

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
clusterCode | "001" | String | 否 | 集群编码
padCode | "ACN250403FKAX2HX" | String | 是 | 实例编号
netStorageResUnitCode | "ZSC250403MMGUFGN-ACN250403ZIMD9KJ" | String | 否 | 网络存储资源编号（可选）
androidProp | {"persist.sys.cloud.wifi.mac": "D2:48:83:70:66:0B"} | Object  | 否    | 参考 [安卓改机属性列表](./InstanceAndroidPropList.html)
countryCode | SG                                                  | String  | 否    | 国家编码，默认值`SG`。[查看所有国家编码↗](./EnumReference.md#51-countrycode---国家编码)

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码（200表示成功）
msg | success | String | 接口请求状态信息
ts | 1743664443188 | Long | 时间戳
data | `{ "padCode": "ACN250403FKAX2HX", "vmStatus": 0, "taskId": 10341 }` | GeneratePadTaskVO | 任务详情

**请求示例**

```json
{
  "clusterCode": "001",
  "padCode": "ACN250403FKAX2HX",
  "netStorageResUnitCode": "ZSC250403MMGUFGN-ACN250403ZIMD9KJ",
   "countryCode":"US",
   "androidProp": "{\"persist.sys.cloud.wifi.mac\": \"D2:48:83:70:66:0B\"}"
}
```

**响应示例**

```json
{
  "clusterCode": "001",
  "padCode": "ACN250403FKAX2HX",
  "netStorageResUnitCode": "ZSC250403MMGUFGN-ACN250403ZIMD9KJ"
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | -- | ---
110095 | 没有可以开机的实例,请检查实例状态 | 确认实例状态是否为关机状态
220011 | 频繁操作网存实例,请稍后再试 | 稍后再试
110101 | 未找到与实例规格匹配的板卡，请前往板卡列表设置规格。 | 确认实例的规格跟板卡规格一致,并且板卡有算力未被占用

#### **网存存储删除**

**接口类型**: 异步接口
**关联回调**: [网存存储删除回调](#网存存储删除回调) (taskBusinessType: `-`)

用于删除指定网存存储资源。

**接口概要**

作用：修改网存存储删除。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

---

**接口地址**

> POST /openapi/open/pad/net/storage/pad/delete

---

**请求数据类型**

> application/json

---

**请求参数**

| 参数名                   | 示例值                                          | 参数类型     | 是否必填 | 参数描述                     |
|------------------------|----------------------------------------------|------------|---------|----------------------------|
| netStorageResUnitCodes | `["ZSC250407XLYILP4-ACN250407XRY4CW9"]`       | List&lt;String&gt; | 是      | 需要删除的网存存储资源编号列表，最多支持 200 个 |

---

**响应参数**

| 参数名    | 示例值   | 参数类型  | 参数描述                   |
|---------|--------|----------|----------------------------|
| code    | 200    | Integer  | 状态码（200表示成功）        |
| msg     | success| String   | 接口请求状态信息            |
| ts      | 1744026334273 | Long | 时间戳                     |
| data    | `[{"padCode": "ZSC250407XLYILP4-ACN250407XRY4CW9", "vmStatus": 0, "taskId": 10159}]` | List&lt;GeneratePadTaskVO&gt; | 每个存储资源对应的删除任务结果列表 |

---

**请求示例**

```json
{
  "netStorageResUnitCodes": [
    "ZSC250407XLYILP4-ACN250407XRY4CW9"
  ]
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": [
    {
      "padCode": "ZSC250407XLYILP4-ACN250407XRY4CW9",
      "vmStatus": 0,
      "taskId": 10159
    }
  ],
  "ts": 1744026334273
}

```

**错误码**
[错误码说明](./ErrorMsgCode.md#系统错误码说明)

#### **获取网存实例使用详情**

**接口类型**: 同步接口

用于查询网存实例使用详情，按设备等级分组。

**接口概要**

作用：查询获取网存实例使用详情。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

---

**接口地址**

> POST /openapi/open/pad/netPad/group/deviceLevel

---

**请求数据类型**

> application/json

---

**请求参数**

| 参数名        | 示例值   | 参数类型 | 是否必填 | 参数描述                     |
|-------------|--------|--------|---------|----------------------------|
| clusterCode | "001"  | String | 是      | 集群编码                    |

---

**响应参数**

| 参数名        | 示例值   | 参数类型  | 参数描述                   |
|-------------|--------|----------|----------------------------|
| totalNumber | 16     | Long     | 总算力数量                 |
| onNumber    | 2      | Long     | 已开机数量                 |
| deviceLevel | "m2-8" | String   | 规格                       |

---

**请求示例**

```json
{
  "clusterCode": "001"
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": [
    {
      "totalNumber": 16,
      "onNumber": 2,
      "deviceLevel": "m2-8"
    },
    {
      "totalNumber": 9,
      "onNumber": 1,
      "deviceLevel": "m2-3"
    }
  ],
  "ts": 1744024331175
}

```

#### **网存存储详情查询**

**接口类型**: 同步接口

用于查询网存存储资源的详细信息，支持分页查询。

**接口概要**

作用：查询网存存储详情查询。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

---

**接口地址**

> POST /openapi/open/netStorage/resUnit/net/storage/pad/resUnit

---

**请求数据类型**

> application/json

---

**请求参数**

| 参数名    | 示例值  | 参数类型 | 是否必填 | 参数描述                 |
|---------|--------|--------|---------|------------------------|
| page    | 3      | Integer | 是      | 当前页码                |
| rows    | 10     | Integer | 是      | 每页显示条数            |

---

**响应参数**

| 参数名         | 示例值  | 参数类型         | 参数描述                   |
|--------------|--------|------------------|----------------------------|
| total        | 27     | Integer          | 总记录数                   |
| size         | 7      | Integer          | 当前页记录数               |
| totalPage    | 3      | Integer          | 总页数                     |
| page         | 3      | Integer          | 当前页码                   |
| pageData     | `[...]`| List&lt;NetStorageResUnitVO&gt; | 当前页的数据列表          |

**NetStorageResUnitVO字段说明**

| 字段名                   | 示例值                    | 参数类型 | 参数描述                           |
|------------------------|--------------------------|----------|-----------------------------------|
| netStorageResUnitId     | 87                       | Long     | 网络存储详情 ID                     |
| shutdownFlag            | 0                        | Integer  | 是否有实例开关机（0: 关机，1: 开机） |
| netStorageResUnitCode   | "ZSC25040761D2GP8-ACN250407XRY4CW9" | String   | 网络存储详情 Code                  |
| clusterCode             | "001"                    | String   | 集群 Code                          |
| padCode                 | "ACN250407XRY4CW9"       | String   | 实例 Code                          |
| netStorageResUnitSize   | 16                       | Long     | 网络存储大小 (单位:GB)             |

---

**请求示例**

```json
{
  "page": 3,
  "rows": 10
}
```

**响应示例**

```json
{
  "msg": "success",
  "code": 200,
  "data": {
    "total": 27,
    "size": 7,
    "totalPage": 3,
    "page": 3,
    "pageData": [
      {
        "shutdownFlag": 0,
        "padCode": "ACN250407XRY4CW9",
        "netStorageResUnitCode": "ZSC25040761D2GP8-ACN250407XRY4CW9",
        "clusterCode": "001",
        "netStorageResUnitId": 87,
        "netStorageResUnitSize": 16
      }
      // ... 更多网存实例对象
    ],
    "rows": 10
  },
  "ts": 1744023373581
}
```

### 实例管理

#### **修改实例WIFI属性**

**接口类型**: 同步接口

修改指定实例的WIFI列表属性（此接口与一建新机设置WIFI二选一，否则会出现覆盖问题）

**接口概要**

作用：为指定实例批量设置 Wi-Fi 列表属性，替代一键新机中的 Wi-Fi 设置。
关键参数：`padCodes` 指定实例；`wifiJsonList` 中包含 SSID/BSSID/MAC/IP/gateway/DNS 等字段。
结果：创建任务并返回 `taskId` 与实例状态，设置会覆盖已有 Wi-Fi 配置（与一键新机互斥）。

**接口地址**

> /openapi/open/pad/setWifiList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | -- | ---
padCodes |  | String[] | 是 | 实例编号
wifiJsonList |  | String[] | 是 | wifi属性列表
├─SSID | 110101 | String | 是 | wifi名称  (不支持中文)
├─BSSID | 02:31:00:00:00:01 | String | 是 | 接入点mac地址
├─MAC | 02:00:10:00:00:00 | String | 是 | wifi网卡mac地址
├─IP | 02:00:10:00:00:00 | String | 是 | wifi网络IP
├─MAC | 02:00:10:00:00:00 | String | 是 | wifi网卡mac地址
├─gateway | 192.168.120.1 | String | 是 | wifi网关
├─DNS1 | 1.1.1.1 | String | 是 | DNS1
├─DNS2 | 8.8.8.8 | String | 是 | DNS2
├─hessid | 0 | Integer | 否 | 网络标识符
├─anqpDomainId | 0 | Integer | 否 | ANQP（Access Network Query Protocol）域ID
├─capabilities | "" | String | 否 | WPA/WPA2等信息
├─level | 0 | Integer | 否 | 信号强度（RSSI）
├─linkSpeed | 500 | Integer | 否 | 当前Wi-Fi连接速率
├─txLinkSpeed | 600 | Integer | 否 | 上传链路速度
├─rxLinkSpeed | 700 | Integer | 否 | 下载链路速度
├─frequency | 2134 | Integer | 否 | Wi-Fi信道频率
├─distance | -1 | Integer | 否 | 估算的AP距离
├─distanceSd | -1 | Integer | 否 | 估算距离的标准差
├─channelWidth | 0 | Integer | 否 | 信道带宽
├─centerFreq0 | 0 | Integer | 否 | 中心频率0
├─centerFreq1 | -1 | Integer | 否 | 中心频率1
├─is80211McRTTResponder | false | Boolean | 否 | 是否支持 802.11mc（Wi-Fi RTT，测距技术

**响应参数**

参数名 | 示例值 | 参数类型    | 参数描述
--- | -- |---------| ---
code | 200 | Integer | 状态码
msg | success | String  | 响应消息
ts | 1756021167163 | Long    | 时间戳
data |  | Object  |
├─ taskId | 1 | Integer | 任务ID
├─ padCode | AC2025030770R | String | 实例编号
├─ vmStatus | 1 | Integer  | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)

**请求示例**

```javascript
{
    "padCodes":["AC2025030770R92X"],
        "wifiJsonList":[
        {
            "SSID": "110101",
            "BSSID": "02:31:00:00:00:01",
            "MAC": "02:00:10:00:00:00",
            "IP": "192.168.120.15",
            "gateway": "192.168.120.1",
            "DNS1": "1.1.1.1",
            "DNS2": "8.8.8.8",
            "hessid": 0,
            "anqpDomainId": 0,
            "capabilities": "",
            "level": 0,
            "linkSpeed": 500,
            "txLinkSpeed": 600,
            "rxLinkSpeed": 700,
            "frequency": 2413,
            "distance": -1,
            "distanceSd": -1,
            "channelWidth": 0,
            "centerFreq0": -1,
            "centerFreq1": -1,
            "is80211McRTTResponder": true
        }
    ]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1741676855566,
        "data": [
        {
            "taskId": 14904,
            "padCode": "AC2025030770R92X",
            "vmStatus": 0
        }
    ]
}

```

#### **实例详情**

**接口类型**: 同步接口

查询指定实例的属性信息，包括系统属性信息和设置信息。

**接口概要**

作用：按条件分页查询实例详情（系统属性、设置、状态、机房等）。
关键参数：`padCodes`/`padIps`/`vmStatus`/`groupId` 等筛选条件。
结果：返回实例列表与详细字段（状态、规格、网络、存储等）。

**接口地址**

> /openapi/open/pad/padDetails

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | -- | ---
page | 1 | Integer | 否 | 页码
rows | 10 | Integer | 否 | 每页记录数
padCodes |  | String[] | 否 |
├─ | AC21020010391 | String | 否 | 实例编号
padIps |  | String[] | 否 |
├─ | 192.168.1.1 | String | 否 | 实例ip
vmStatus | 1 | String | 否 | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
controlStatus | 1 | String | 否 | 受控状态（推流状态）。可选值：`1`非受控/`2`受控。[详见枚举↗](./EnumReference.md#18-controlstatus---受控状态推流状态)
faultStatus | 14 | String | 否 | 实例运行状态。可选值：`14`异常/其他正常。[详见枚举↗](./EnumReference.md#19-faultstatus---实例运行状态)
deviceStatus | 0 | String | 否 | 物理机在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#14-devicestatus---物理机状态)
groupId | 2 | Integer | 否 | 分组ID
idcCode | HNCS-C-01 | String | 否 | 机房编号

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756360093771 | Long | 时间戳
traceId | ewc83bwudvr4 | String | 链路追踪ID
data |  | Object | 响应数据
├─ page | 1 | Integer | 当前页
├─ rows | 10 | Integer | 每页记录数
├─ size | 10 | Integer | 当前页的数量
├─ total | 13398 | Integer | 总记录数
├─ totalPage | 1340 | Integer | 总页数
├─ pageData |  | object[] | 列表
├─ ├─ padId | 552 | Long | 实例ID
├─ ├─ padCode | ACP250331GLMP7YX | String | 云机编号
├─ ├─ customerId | null | Long | 客户ID
├─ ├─ imageId | img-25032628136 | String | 镜像ID
├─ ├─ deviceLevel | m2-6 | String | 实例规格
├─ ├─ dcInfo |  | Object | 机房信息
├─ ├─ ├─ id | 1 | Long | 机房ID
├─ ├─ ├─ dcName | 小算测试-机房 | String | 机房名称
├─ ├─ ├─ dcCode | 001 | String | 机房编码
├─ ├─ ├─ area | changsha | String | 地区
├─ ├─ ├─ ossEndpoint | null | String | OSS公网接口地址
├─ ├─ ├─ ossEndpointInternal | null | String | OSS内网接口地址
├─ ├─ ├─ ossFileEndpoint | null | String | 文件访问地址
├─ ├─ ├─ ossScreenshotEndpoint | null | String | 截图访问地址
├─ ├─ padStatus | 15 | Integer | 实例状态（10-运行中，11-重启中，12-重置中，13-升级中，14-异常，15-未就绪，16-备份中，17-恢复数据中，18-关机，19-关机中，20-开机中，21-关机失败，22-开机失败，23-删除中，24-删除失败，25-已删除，26-克隆中）
├─ ├─ deviceStatus | 1 | Integer | 物理机状态（0-离线，1-在线）
├─ ├─ online | 0 | Integer | 实例在线状态（0-离线，1-在线）
├─ ├─ streamStatus | 0 | Integer | 实例推流状态。可选值：`0`空闲/`1`推流中。[详见枚举↗](./EnumReference.md#110-streamstatus---实例推流状态)
├─ ├─ dataSize | null | Long | 存储总容量(字节)
├─ ├─ dataSizeUsed | null | Long | 存储已使用容量(字节)
├─ ├─ adbOpenStatus | null | String | ADB开关状态。可选值：`0`或空关闭/`1`开启。[详见枚举↗](./EnumReference.md#111-adbopenstatus---adb开关状态)
├─ ├─ deviceIp | 172.31.1.4 | String | 板卡 IP
├─ ├─ screenLayoutCode | multiple-portrait-basic | String | 屏幕布局编码
├─ ├─ mac | "" | String | MAC 地址
├─ ├─ netStorageResId | null | String | 网存ID
├─ ├─ dns | 192.168.50.15 | String | 实例 DNS
├─ ├─ memory | null | Integer | 内存大小
├─ ├─ cpu | -1 | Integer | CPU 大小
├─ ├─ socModel | MACS2080 | String | SoC 型号
├─ ├─ netStorageResFlag | 0 | Integer | 网存标记（1 网存实例；0 本地实例）
├─ ├─ netStorageResSize | null | Long | 网存实例大小（GB）
├─ ├─ realPhoneTemplateId | 389 | Long | 真实机型模板ID
├─ ├─ clusterCode | ZEG3650947 | String | 集群编码
├─ ├─ padIp | null | String | 实例 IP
├─ ├─ updateNetStorageResFlag | false | Boolean | 是否指定网存ID开机
├─ ├─ targetStorageResId | null | String | 指定的网存ID
├─ ├─ armIp | 192.168.200.50 | String | ARM 服务器 IP
├─ ├─ countryCode | null | String | 国家代码
├─ ├─ type | virtual | String | 实例类型（virtual-虚拟机 / real-云真机）
├─ ├─ armServerId | 179 | Long | 服务器ID
├─ ├─ lastComputeUnitCode | null | String | 最后开机使用的算力编号
├─ ├─ lastDeviceCode | null | String | 最后开机使用的板卡编号
├─ ├─ lastDeviceIp | null | String | 最后开机使用的板卡IP
├─ ├─ cloneFlag | null | String | 克隆标志（0-否，1-是）
├─ ├─ baseResUnitCode | null | String | 克隆实例的基础存储code
├─ ├─ cbsInfo | 2.0.14 | String | CBS 信息
├─ ├─ firstBoot | true | Boolean | 是否首次开机

**请求示例**

```javascript
{
 "page": 1,
 "rows": 10,
 "padCodes": ["AC21020010391"],
 "padIps":["192.168.1.1"],
 "vmStatus":"1",
 "controlStatus":"1",
 "faultStatus":"14",
 "deviceStatus":"0"
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756360093771,
        "data": {
        "page": 1,
            "rows": 10,
            "size": 10,
            "total": 13398,
            "totalPage": 1340,
            "pageData": [
            {
                "padId": 552,
                "padCode": "ACP250331GLMP7YX",
                "customerId": null,
                "imageId": "img-25032628136",
                "deviceLevel": "m2-6",
                "dcInfo": {
                    "id": 1,
                    "dcName": "小算测试-机房",
                    "dcCode": "001",
                    "area": "changsha",
                    "ossEndpoint": null,
                    "ossEndpointInternal": null,
                    "ossFileEndpoint": null,
                    "ossScreenshotEndpoint": null
                },
                "padStatus": 15,
                "deviceStatus": 1,
                "online": 0,
                "streamStatus": 0,
                "dataSize": null,
                "dataSizeUsed": null,
                "adbOpenStatus": null,
                "deviceIp": "172.31.1.4",
                "screenLayoutCode": "multiple-portrait-basic",
                "mac": "",
                "netStorageResId": null,
                "dns": "192.168.50.15",
                "memory": null,
                "cpu": -1,
                "socModel": "MACS2080",
                "netStorageResFlag": 0,
                "netStorageResSize": null,
                "realPhoneTemplateId": 389,
                "clusterCode": "ZEG3650947",
                "padIp": null,
                "updateNetStorageResFlag": false,
                "targetStorageResId": null,
                "armIp": "192.168.200.50",
                "countryCode": null,
                "type": "virtual",
                "armServerId": 179,
                "lastComputeUnitCode": null,
                "lastDeviceCode": null,
                "lastDeviceIp": null,
                "cloneFlag": null,
                "baseResUnitCode": null,
                "cbsInfo": "2.0.14",
                "firstBoot": true
            }
        ]
    },
    "traceId": "ewc83bwudvr4"
}

```

**代码示例**

```java
// java 调用示例
PadDetailsRequest requestParam = new PadDetailsRequest();
List padCodes = new ArrayList<>();
padCodes.add("AC22010041147");
requestParam.setPadCodes(padCodes);
Result> result = armCloudApiService.execute(ArmCloudApiEnum.PAD_DETAILS, requestParam,new TypeReference>>() {});
```

#### **实例详情-精简版**

**接口类型**: 同步接口

查询实例的基础属性信息。

**接口概要**

作用：查询实例基础信息的精简列表，用于轻量分页与状态检查。
关键参数：`lastId` + `rows` 做游标分页；`padCodes`/`padIps`/`online` 等过滤条件。
结果：返回精简字段（在线/运行状态、网存标记等）。

**接口地址**

> /openapi/open/pad/padBaseInfoList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值           | 参数类型     | 是否必填 | 参数描述
--- |---------------|----------| -- | ---
lastId | 1234          | Long     | 否 | 上一次查询返回的lastId，首次查询可不传或者传null
rows | 10            | Integer  | 否 | 每页记录数，最大支持单页 1000条
padCodes |               | String[] | 否 |
├─ | ACP250331GLXXXXX | String   | 否 | 实例编号
padIps |               | String[] | 否 |
├─ | 192.168.1.1   | String   | 否 | 实例ip
online | 1             | Integer  | 否 | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#52-online---在线状态)
padStatus | 14            | Integer  | 否 | 实例运行状态。[查看所有26个状态码↗](./EnumReference.md#11-padstatus---实例状态)
computeOccupied | true          | Boolean        | 否 | 筛选算力占用情况。`true`占用算力/`false`未占用算力
netStorageResFlag | 1             | Integer        | 否 | 网存标记。可选值：`0`本地实例/`1`网存实例/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记)

**响应参数**

参数名 | 示例值              | 参数类型     | 参数描述
--- |------------------|----------| ---
code | 200              | Integer  | 状态码
msg | success          | String   | 响应消息
ts | 1756360093771    | Long     | 时间戳
traceId | ewc83bwudvr4     | String   | 链路追踪ID
data |                  | Object   | 响应数据
├─ rows | 10               | Integer  | 每页记录数
├─ size | 10               | Integer  | 当前页的数量
├─ lastId | 1234             | Long     | 最后一条记录ID，用于下次分页查询
├─ hasNext | true             | Boolean  | 是否还有下一页
├─ pageData |                  | object[] | 列表
├─ ├─ padCode | ACP250331GLXXXXX | String   | 实例编号
├─ ├─ padIp | null             | String   | 实例 IP
├─ ├─ padStatus | 15               | Integer  | 实例运行状态（10-运行中，11-重启中，12-重置中，13-升级中，14-异常，15-未就绪，16-备份中，17-恢复数据中，18-关机，19-关机中，20-开机中，21-关机失败，22-开机失败，23-删除中，24-删除失败，25-已删除，26-克隆中）
├─ ├─ online | 0                | Integer  | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#52-online---在线状态)
├─ ├─ computeOccupied | true             | Boolean  | 算力占用情况。`true`占用算力/`false`未占用算力
├─ ├─ netStorageResFlag | 1                | Integer        | 网存标记。可选值：`0`本地实例/`1`网存实例/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记)

**请求示例**

```javascript
{
 "lastId": null,
 "rows": 10,
 "padCodes": ["ACP250331GLXXXXX"],
 "padIps":["192.168.1.1"],
 "online":1,
 "padStatus":10,
 "computeOccupied":true,
 "netStorageResFlag":1
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1756360093771,
    "data": {
        "rows": 10,
        "size": 10,
        "lastId": 552,
        "hasNext": true,
        "pageData": [{
            "padCode": "ACP250331GLXXXXX",
            "padIp": null,
            "padStatus": 15,
            "online": 0,
            "computeOccupied": true,
            "netStorageResFlag":1
        }]
    },
    "traceId": "f9lvinjx337k"
}

```

#### **实例重启**

**接口类型**: 异步接口
**关联回调**: [实例重启任务回调](#实例重启任务回调) (taskBusinessType: `1002`)

对指定实例执行重启操作，用以解决系统无响应、卡死等问题。

**接口概要**

作用：对实例发起重启任务，处理卡死/无响应等问题。
关键参数：`padCodes`（或 `groupIds`）选择目标实例。
结果：返回任务 `taskId`，可通过回调或任务状态查询获取结果。

**接口地址**

> /openapi/open/pad/restart

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名  | 示例值        | 参数类型    | 是否必填 | 参数描述      |
| ------- | ------------- |---------|------|-----------|
|padCodes |  | String[] | 是    |           |
|├─ | AC21020010001 | String  | 是    | 实例编号      |
|groupIds |  | Integer[] | 否    |           |
|├─ | 1 | Integer | 否    | 实例组ID     |

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述|
|--- | --- | --- | ---|
|code | 200 | Integer | 状态码|
|msg | success | String | 响应消息|
|ts | 1756021167163 | Long | 时间戳|
|data | | Object[] | |
|├─taskId | 1 | Integer | 任务ID|
|├─padCode | AC21020010001 | String | 实例编号|
|├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)|
|├─ taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）|

**请求示例**

```javascript
{
 "padCodes": [
  "AC22030022693"
 ],
 "groupIds": [1]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756313806284,
        "data": [
        {
            "taskId": 4844869,
            "padCode": "ATP250818261XVMO",
            "vmStatus": 0,
            "taskStatus": 1
        }
    ],
        "traceId": "ewab9x88fkzk"
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
10001 | 重启失败| 联系管理员
110004 | 执行重启命令失败| 稍后再次重启
110028 | 实例不存在| 请检查实例是否存在

**代码示例**

```java
// java 调用示例
public class SDKExample {
    private final ArmCloudApiService armCloudApiService;

    public SDKExample() {
        ArmCloudConfig armCloudConfig = new ArmCloudConfig();
        armCloudConfig.setOpenUrl("https://openapi-hk.armcloud.net");
        armCloudConfig.setService("armcloud-paas");
        armCloudConfig.setHost("openapi.armcloud.net");
        armCloudConfig.setAk("your access_key_id");
        armCloudConfig.setSk("your secret_access_key");
        armCloudApiService = new ArmCloudApiServiceImpl(armCloudConfig, new DefaultHttpExecutor());
    }

    @Test
    public void test() throws Exception {
        RestartRequest requestParam = new RestartRequest();
        List padCodes = new ArrayList<>();
        padCodes.add("AC22010041147");
        requestParam.setPadCodes(padCodes);
        Result result = armCloudApiService.execute(ArmCloudApiEnum.PAD_RESTART, requestParam, new TypeReference>() {});
    }
}
```

#### **实例重置**

**接口类型**: 异步接口
**关联回调**: [实例重置任务回调](#实例重置任务回调) (taskBusinessType: `-`)
>
> 注意：实例重置清除系统所有数据。请谨慎使用,每次重置之后会将公网IP恢复到默认值

对实例执行重置操作，将会清理云机所有数据

**接口概要**

作用：对实例执行重置并清空所有数据（公网 IP 恢复默认）。
关键参数：`padCodes`（或 `groupIds`）指定实例。
结果：返回重置任务 `taskId`，通过回调或状态查询确认完成。

**接口地址**

> /openapi/open/pad/reset

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值         | 参数类型  | 是否必填 | 参数描述   |
| -------- | -------------- | --------- | -------- | ---------- |
| padCodes |                | String[]  | 是       |            |
| ├─       | AC21020010001  | String    | 是       | 实例编号   |
| groupIds |                | Integer[] | 否       |            |
| ├─       | 1              | Integer   | 否       | 实例组ID   |

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述|
|--- | --- | --- | --- |
|code | 200 | Integer | 状态码 |
|msg | success | String | 响应消息 |
|ts | 1756021167163 | Long | 时间戳 |
|data |  | Object[] | |
|├─taskId | 1 | Integer |  任务ID|
|├─padCode | AC21020010001 | String | 实例编号 |
|├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
|├─ taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）|

**请求示例**

```javascript
{
 "padCodes": [
  "AC21020010001"
 ],
 "groupIds": [1]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756313781715,
        "data": [
        {
            "taskId": 760459892,
            "padCode": "ATP250817PIJLWRP",
            "vmStatus": 0,
            "taskStatus": 1
        }
    ],
        "traceId": "ewab8lv65yio"
}
```

**错误码**

|错误码 | 错误说明 | 操作建议|
|--- | --- | --- |
|10002 | 重置失败 | 联系管理员|
|110005 | 执行重置命令失败 | 稍后再次重置|

**代码示例**

```java
// java 调用示例
 ResetRequest requestParam = new ResetRequest();
List padCodes = new ArrayList<>();
padCodes.add("AC22010041147");
requestParam.setPadCodes(padCodes);
Result result = armCloudApiService.execute(ArmCloudApiEnum.PAD_RESET, requestParam, new TypeReference>() {});
```

#### **查询实例属性**

**接口类型**: 同步接口

查询指定实例的属性信息，包括系统属性信息和设置信息。

**接口概要**

作用：获取单个实例的属性列表（系统/设置/Modem/OAID）。
关键参数：`padCode` 指定实例。
结果：返回属性名与属性值集合，供诊断或后续改机设置参考。

**接口地址**

> /openapi/open/pad/padProperties

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--- | --- | --- | --- | --- |
|padCode | AC21020010001 | String | 是 | 实例编号 |

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述 |
|--- | --- | --- | --- |
|code | 200 | Integer | 状态码 |
|msg | success | String| 响应消息 |
|ts | 1756021167163 | Long |  时间戳 |
|data |  | Object |  |
|├─padCode | AC21020010001 | String | 实例编号 |
|├─modemPropertiesList |  | Object[] | Modem-属性列表 |
|├─├─propertiesName | IMEI | String | 属性名称 |
|├─├─propertiesValue | 412327621057784 | String | 属性值 |
|├─systemPropertiesList|  | Object[] | 系统-属性列表 |
|├─├─propertiesName | ro.build.id | String | 属性名称 |
|├─├─propertiesValue | QQ3A.200805.001 | String | 属性值 |
|├─settingPropertiesList |  | Object[] | setting-属性列表 |
|├─├─propertiesName | ro.build.tags | String | 属性名称 |
|├─├─propertiesValue | release-keys | String | 属性值 |
|├─oaidPropertiesList |  | Object[] | oaid-属性列表 |
|├─├─propertiesName | oaid | String | 属性名称 |
|├─├─propertiesValue | 001 | String | 属性值 |

**请求示例**

```javascript
{
 "padCode": "AC21020010001"
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
 "data": {
  "padCode": "AC21020010001",
  "modemPropertiesList": [
   {
    "propertiesName": "IMEI",
    "propertiesValue": "412327621057784"
   }
  ],
  "systemPropertiesList": [
   {
    "propertiesName": "ro.build.id",
    "propertiesValue": "QQ3A.200805.001"
   }
  ],
  "settingPropertiesList": [
   {
    "propertiesName": "ro.build.tags",
    "propertiesValue": "release-keys"
   }
  ],
  "oaidPropertiesList": [
   {
    "propertiesName": "oaid",
    "propertiesValue": "001"
   }
  ]
 }
}
```

**错误码**

|错误码 | 错误说明 | 操作建议 |
| ----- | -------- | ------ |
|110028 | 实例不存在 | 请检查实例是否正确 |

**代码示例**

```java
// java 调用示例
PadPropertiesRequest requestParam = new PadPropertiesRequest();
requestParam.setPadCode("AC22010041147");
Result result = armCloudApiService.execute(ArmCloudApiEnum.PAD_GET_PROPERTIES, requestParam,new TypeReference>() {});
```

#### **批量查询实例属性**

**接口类型**: 同步接口

批量查询指定实例的属性信息，包括系统属性信息和设置信息。

**接口概要**

作用：批量获取多实例属性列表，适用于批量核对/对比。
关键参数：`padCodes`（最多 200 个）。
结果：返回每个实例的属性名与属性值集合。

**接口地址**

> /openapi/open/pad/batchPadProperties

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值           | 参数类型 | 是否必填 | 参数描述 |
|--- |---------------| --- | --- | --- |
|padCodes |               | String[] | 是 |实例数量不多余200个 |
|├─ | AC21020010001 | String | 是 | 实例编号|
|├─ | AC21020010002 | String | 是 | 实例编号|

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述 |
|--- | --- | --- | --- |
|code | 200 | Integer | 状态码 |
|msg | success | String| 响应消息 |
|ts | 1756021167163 | Long |  时间戳 |
|data |  | Object[] | |
|├─padCode | AC21020010001 | String | 实例编号 |
|├─modemPropertiesList |  | Object[] | Modem-属性列表 |
|├─├─propertiesName | IMEI | String | 属性名称 |
|├─├─propertiesValue | 412327621057784 | String | 属性值 |
|├─systemPropertiesList|  | Object[] | 系统-属性列表 |
|├─├─propertiesName | ro.build.id | String | 属性名称 |
|├─├─propertiesValue | QQ3A.200805.001 | String | 属性值 |
|├─settingPropertiesList |  | Object[] | setting-属性列表 |
|├─├─propertiesName | ro.build.tags | String | 属性名称 |
|├─├─propertiesValue | release-keys | String | 属性值 |
|├─oaidPropertiesList |  | Object[] | oaid-属性列表 |
|├─├─propertiesName | oaid | String | 属性名称 |
|├─├─propertiesValue | 001 | String | 属性值 |

**请求示例**

```javascript
{
    "padCodes": [
        "AC21020010001",
        "AC21020010002"
    ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
 "data": [
        {
            "padCode": "AC21020010001",
            "modemPropertiesList": [
                {
                    "propertiesName": "IMEI",
                    "propertiesValue": "412327621057784"
                }
            ],
            "systemPropertiesList": [
                {
                    "propertiesName": "ro.build.id",
                    "propertiesValue": "QQ3A.200805.001"
                }
            ],
            "settingPropertiesList": [
                {
                    "propertiesName": "ro.build.tags",
                    "propertiesValue": "release-keys"
                }
            ],
            "oaidPropertiesList": [
                {
                    "propertiesName": "oaid",
                    "propertiesValue": "001"
                }
            ]
        },
        {
            "padCode": "AC21020010002",
            "modemPropertiesList": [
                {
                    "propertiesName": "IMEI",
                    "propertiesValue": "412327621057784"
                }
            ],
            "systemPropertiesList": [
                {
                    "propertiesName": "ro.build.id",
                    "propertiesValue": "QQ3A.200805.001"
                }
            ],
            "settingPropertiesList": [
                {
                    "propertiesName": "ro.build.tags",
                    "propertiesValue": "release-keys"
                }
            ],
            "oaidPropertiesList": [
                {
                    "propertiesName": "oaid",
                    "propertiesValue": "001"
                }
            ]
        }
    ]
}
```

**错误码**

|错误码 | 错误说明 | 操作建议 |
| ----- | -------- | ------ |
|110028 | 实例不存在 | 请检查实例是否正确 |

**代码示例**

```java
// java 调用示例
PadPropertiesRequest requestParam = new PadPropertiesRequest();
List padCodes = new ArrayList<>();
padCodes.add("AC21020010001");
padCodes.add("AC21020010002");
requestParam.setPadCodes(padCodes);
Result> result = armCloudApiService.execute(ArmCloudApiEnum.PAD_POST_PROPERTIES, requestParam,new TypeReference>() {});
```

#### **修改实例属性**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

动态修改实例的属性信息，包括系统属性和设置

实例需要处于开机状态，该接口为即时生效

参考 [实例属性列表](./InstanceList.html#modem-properties-属性列表)

**接口概要**

作用：动态修改实例属性（系统/设置/Modem/OAID/WebKit），开机状态即时生效。
关键参数：`padCodes` 指定实例；各 `*PropertiesList` 使用 `propertiesName/propertiesValue` 赋值。
结果：返回任务 `taskId`；可用于修改如分辨率等属性（需在实例属性列表中找到对应属性名）。

**接口地址**

> /openapi/open/pad/updatePadProperties

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述|
|--- | --- | --- | --- | ---|
|padCodes |  | String[] | 是 | |
|├─ | AC21020010001 | String | 是 | 实例编号|
|modemPersistPropertiesList |  | Object[] | 否 | Modem-持久化-属性列表|
|├─propertiesName | IMEI | String | 否 | 属性名称|
|├─propertiesValue | 412327621057784 | String | 否 | 属性值|
|modemPropertiesList |  | Object[] | 否 | Modem-非持久化-属性列表|
|├─propertiesName | IMEI | String | 否 | 属性名称|
|├─propertiesValue | 412327621057784 | String | 否 | 属性值|
|systemPersistPropertiesList |  | Object[] | 否 | 系统-持久化-属性列表|
|├─propertiesName | ro.build.id | String | 否 | 属性名称|
|├─propertiesValue | QQ3A.200805.001 | String | 否 | 属性值|
|systemPropertiesList |  | Object[] | 否 | 系统-非持久化-属性列表|
|├─propertiesName | ro.build.id | String | 否 | 属性名称|
|├─propertiesValue | QQ3A.200805.001 | String | 否 | 属性值|
|settingPropertiesList |  | Object[] | 否 | setting-属性列表|
|├─propertiesName | ro.build.tags | String | 否 | 属性名称|
|├─propertiesValue | release-keys | String | 否 | 属性值|
|oaidPropertiesList |  | Object[] | 否 | oaid-属性列表|
|├─propertiesName | oaid | String | 否 | 属性名称|
|├─propertiesValue | 001 | String | 否 | 属性值|
|webkitPropertiesList |  | Object[] | 否 | webkit-属性列表|
|├─propertiesName | oaid | String | 否 | 属性名称|
|├─propertiesValue | 001 | String | 否 | 属性值|

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述|
|--- | --- | --- | --- |
|code | 200 | Integer | 状态码 |
|msg | success | String | 响应消息 |
|ts | 1756021167163 | Long | 时间戳 |
|data |  | Object[] | |
|├─taskId | 1 | Integer |  任务ID|
|├─padCode | AC21020010001 | String | 实例编号 |
|├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |

**请求示例**

```javascript
{
 "padCodes": [
  "AC21020010001"
 ],
 "modemPersistPropertiesList": [
   {
    "propertiesName": "IMEI",
    "propertiesValue": "412327621057784"
   }
  ],
 "modemPropertiesList": [
   {
    "propertiesName": "IMEI",
    "propertiesValue": "412327621057784"
   }
  ],
  "systemPersistPropertiesList": [
   {
    "propertiesName": "ro.build.id",
    "propertiesValue": "QQ3A.200805.001"
   }
  ],
  "systemPropertiesList": [
   {
    "propertiesName": "ro.build.id",
    "propertiesValue": "QQ3A.200805.001"
   }
  ],
  "settingPropertiesList": [
   {
    "propertiesName": "ro.build.tags",
    "propertiesValue": "release-keys"
   }
  ],
  "oaidPropertiesList": [
   {
    "propertiesName": "oaid",
    "propertiesValue": "001"
   }
  ],
   "webkitPropertiesList": [
     {
      "propertiesName": "oaid",
      "propertiesValue": "001"
     }
    ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1717570916196,
 "data": [
  {
   "taskId": 36,
   "padCode": "AC22030010001",
   "vmStatus": 1
  }
 ]
}
```

**错误码**

|错误码 | 错误说明 | 操作建议 |
| --- | --- | --- |
|110011 | 执行修改属性命令失败 | 请稍后重试 |
|110028 | 实例不存在 | 请检查实例是否正确 |
|110027 | 实例编号集合存在重复项 | 请检查实例是否存在重复的 |

**代码示例**

```java
// java 调用示例
UpdatePadPropertiesRequest requestParam = new UpdatePadPropertiesRequest();
List padCodes = new ArrayList<>();
padCodes.add("AC22010041147");
requestParam.setPadCodes(padCodes);

List subs = new ArrayList<>();
PadPropertiesSub sub = new PadPropertiesSub();
sub.setPropertiesName("oaid");
sub.setPropertiesValue("123456789");
subs.add(sub);
requestParam.setSystemPropertiesList(subs);
Result> result = armCloudApiService.execute(ArmCloudApiEnum.PAD_UPDATE_PROPERTIES, requestParam,new TypeReference>>() {});
```

#### **修改实例安卓改机属性**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

静态设置安卓改机属性，需要重启实例才能够生效，一般用于修改设备信息

该接口与[修改实例属性](./OpenAPI.md#修改实例属性)接口的区别在于生效时机，该接口生效时间为每次开机初始化

设置实例属性后，属性数据会持久化存储，重启或重置实例无需再调用该接口

参考 [安卓改机属性列表](./InstanceAndroidPropList.html)

**接口概要**

作用：设置安卓改机属性（持久化），需重启后生效。
关键参数：`padCode` 指定实例；`props` 为 key-value 属性集；`restart` 控制是否自动重启。
结果：返回任务 `taskId`，属性会持久化到后续开机。

**使用该接口需要对安卓系统有一定的理解**，部分属性可能会影响实例正常启动，如果改机后，导致实例异常，可以通过调用实例重置接口恢复正常

**接口地址**

> /openapi/open/pad/updatePadAndroidProp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名                   | 示例值        | 参数类型 | 是否必填 | 参数描述                        |
| ------------------------ | ------------- | -------- | -------- | ------------------------------- |
| padCode                  | AC32010210001 | String   | 否       | 实例id                          |
| restart                  | false         | Boolean  | 否       | 设置完成后是否自动重启。`true`自动重启/`false`不自动重启，默认`false` |
| props                    | {}            | Object   | 是       | 系统属性（此字段为key-value定义） |
| ├─ro.product.vendor.name | OP52D1L1      | String   | 是       | 属性设置                        |

**响应参数**

| 参数名          | 示例值        | 参数类型 | 参数描述 |
|--------------| ------------- | -------- | -------- |
| code         | 200           | Integer  | 状态码   |
| msg          | success       | String   | 响应消息 |
| ts           | 1756021167163 | Long     | 时间戳   |
| data         |               | Object   |          |
| ├─taskId     | 24            | Long     | 任务id   |
| ├─padCode    | AC32010210001 | String   | 实例id   |
| ├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "padCode": "AC32010210001",
 "props": {
  "ro.product.vendor.name": "OP52D1L1"
 },
 "restart": false
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756313781338,
        "data": {
        "taskId": 760459884,
            "padCode": "AC32010160134",
            "vmStatus": 0,
            "taskStatus": 1
    },
    "traceId": "ewab8l4lqu4g"
}
```

#### **根据国家Code修改SIM卡信息**

**接口类型**: 同步接口

静态设置安卓改机属性，需要重启实例才能够生效，一般用于修改设备信息

该接口与[修改实例安卓改机属性](./OpenAPI.md#修改实例安卓改机属性)接口具有相同功能.区别在于该接口会随机生成SIM卡信息,并且每次都会重启

设置实例属性后，属性数据会持久化存储，重启或重置实例无需再调用该接口

**接口概要**

作用：按国家编码随机生成并设置 SIM 卡信息，同时写入改机属性并重启。
关键参数：`padCode` 指定实例；`countryCode` 选择国家；`props` 可额外指定属性。
结果：返回任务 `taskId` 与状态，每次调用都会重启并生成新的 SIM 信息。

**接口地址**

> /openapi/open/pad/replacePadAndroidPropByCountry

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名                      | 示例值        | 参数类型 | 是否必填 | 参数描述                  |
|--------------------------| ------------- | -------- |------|-----------------------|
| padCode                  | AC32010210001 | String   | 是    | 实例id                  |
| countryCode              | US | String   | 否    | 国家编码，默认值`SG`。[查看所有国家编码↗](./EnumReference.md#51-countrycode---国家编码) |
| props                    | {}            | Object   | 否    | 系统属性（此字段为key-value定义） |
| ├─ro.product.vendor.name | OP52D1L1      | String   | 否    | 属性设置                  |

**响应参数**

| 参数名          | 示例值               | 参数类型 | 参数描述 |
|----------------|--------------------|---------|---------|
| code           | 200                | Integer | 状态码   |
| msg            | success            | String  | 响应消息 |
| ts             | 1756360113813      | Long    | 时间戳   |
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| data           |                    | Object  | 响应数据 |
| ├─taskId       | 10002486           | Long    | 任务ID  |
| ├─padCode      | ACN342712020172800 | String  | 实例编号 |
| ├─vmStatus     | 0                  | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
| ├─taskStatus   | 1                  | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加） |

**请求示例**

```javascript
{
    "padCode": "AC32010250001",
        "props": {
        "persist.sys.cloud.phonenum": "1234578998"
    },
    "countryCode": "US"
}
```

**响应示例1**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756360113813,
        "data": {
        "taskId": 10002486,
            "padCode": "ACN342712020172800",
            "vmStatus": 0,
            "taskStatus": 1
    },
    "traceId": "ewc84g8si0oy"
}
```

**响应示例2**
```javascript
{
   "code": 500,
   "msg": "目前不支持国家编码: XX",
   "ts": 1753521350163,
   "data": null
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ----
110065 | 参数请求不合规,请参考接口文档 | 检查参数,参考接口文档
110028 | 实例不存在 | 请检查实例编号是否正确

#### **停止推流**

**接口类型**: 同步接口

停止指定实例推流，断开实例连接。

**接口概要**

作用：操作停止推流。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /rtc/open/room/dissolveRoom

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名  | 示例值        | 参数类型 | 是否必填 | 参数描述 |
| ------- | ------------- | -------- | -------- | -------- |
|padCodes |  | String[] | 是 |  |
|├─ | AC11010000031 | String | 是 | 实例编号 |
|├─ | AC22020020700 | String | 是 | 实例编号 |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述|
| --- | --- | --- | ---|
| code | 200 | Integer |  状态码|
| msg | success | String |  响应消息||
| ts | 1756021167163 | Long |  时间戳|
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| data |  | Object[] |  |
| ├─successList |  | Object[] |  成功集合|
| ├─├─padCode | AC11010000031 | String |  实例编号|
| ├─failList |  | Object[] |  失败集合|
| ├─├─padCode | AC22020020700|String |  实例编号|
| ├─├─errorCode |120005 |Integer |  错误码|
| ├─├─errorMsg |实例不存在 |String |  失败的原因|

**请求示例**

```javascript
{
    "padCodes": ["AC11010000031","AC22020020700"]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
     "data": {
     "successList": [
              {
                  "padCode": "AC11010000031"
              }
          ],
          "failList": [
      {
                  "padCode": "AC22020020700",
      "errorCode": 120005,
      "errorMsg": "实例不存在"
              }
    ]
     },
    "traceId": "ewab9njt3gn4"

}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ----
120005 | 实例不存在 | 请检查实例编号是否正确
120004 | 中止推流错误，指令服务异常 | 请稍后重试

#### **批量申请RTC连接Token**

**接口类型**: 同步接口

批量申请当前账号下多个实例的RTC Token连接信息，连接信息根据Pad进行分组返回。

**接口概要**

作用：创建批量申请RTC连接Token。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

> 当Pad无法连接时不会返回RTC Toekn信息，`msg`字段会显示无法连接原因。
>
> 目前此接口仅支持生产 ArmcloudRTC Token。如出现`此接口暂不支持此功能`等异常消息时请联系相关人员重新配置推流信息
>
> 生成的token暂不支持刷新延长有效期。当过期后需重新申请新token
>
> 加密数据需使用AES GCM模式解密，密钥为padCode

**接口地址**

> /rtc/open/room/batchApplyToken

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名         | 示例值        | 参数类型 | 是否必填 | 参数描述                                                     |
| -------------- | ------------- | -------- | -------- | ------------------------------------------------------------ |
| userId         | 202           | String   | 是       | 业务方自定义用户ID，此字段用来生成房间信息。实现一个用户跟GameServer处于一个房间。调用方需做用户级唯一性，如使用同一个userId生成不同的Toekn连接同一个GamerServer会导致上一个已建立的连接断开 |
| expire         | 3600          | Integer  | 否       | token有效期（单位：秒。默认86400）                           |
| pads           |               | Object[] | 是       | 实例列表                                                     |
| ├─padCode      | AC11010000031 | String   | 是       | 实例编号                                                     |
| ├─videoStream  |               | Object   | 否       | 推流配置                                                     |
| ├─├─resolution | 07            | String   | 否       | 分辨率                                                       |
| ├─├─frameRate  | 30            | String   | 否       | 帧率                                                         |
| ├─├─bitrate    | 2000          | String   | 否       | 码率                                                         |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述|
| --- | --- | --- | ---|
| code | 200 | Integer |  状态码|
| msg | success | String |  响应消息|
| ts | 1756021167163 | Long |  时间戳|
| data |  | Object[] |  |
| ├─roomToken | 001j7Tb2jAyAzR6UtLv3cgclCFhw6Q== | String | token |
| ├─roomCode | AC22030010181202 | String | 房间号 |
| ├─appId | j7Tb2GcE9rN5oF6xP3A4qwer | String | 应用ID |
| ├─padCode | AC22030010181 | String | 实例ID |
| ├─signalServer | LnBbVX4AD1CA4uyoN1kXp:P8H01PaGZDHEFD | String | 信令地址(需使用AES GCM模式解密) |
| ├─stuns | pL25iYgaA12RNmdCYR/:SUJD21Bz4S6HE88GzVN | String | stuns地址(需使用AES GCM模式解密) |
| ├─turns | doF22kA7Z6OiVP1br29:rA1R4d6Vyk9e | String | turns地址(需使用AES GCM模式解密) |
| ├─msg | connect pad fail | String | 错误信息 |

**请求示例**

```javascript
{
 "userId": "202",
 "expire": 3600,
 "pads": [
  {
   "padCode": "AC22010010842",
   "videoStream ": {
    "resolution": "1",
    "frameRate": "30",
    "bitrate": "2000"
   }
  },
  {
   "padCode": "AC22030010181",
   "videoStream ": {
    "resolution": "1",
    "frameRate": "30",
    "bitrate": "2000"
   }
  }
 ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1721305008916,
 "data": [
  {
   "roomToken": null,
   "roomCode": "AC22010010842202",
   "appId": "j7Tb2GcE9rN5oF6xP3A4qwer",
   "streamType": 2,
   "videoCodec": "",
   "reportSdkLog": false,
   "padCode": "AC22010010842",
   "msg": "connect pad fail",
   "signalServer": null,
   "stuns": null,
   "turns": null
  },
  {
   "roomToken": "001j7Tb2GcE9rN15oF6xP3A4qwerNwDyCHIRtQrGxZABAAC1ZuzKkAEAABAAQUMyMjAzMDAxMDE4MA12D1TIwMgMAMjAyAQAEALVm7MqQAQAAIABpLvj5zX3dnyN/8UvRsLJnHWA4zR6UtLv3cgclCFhw6Q==",
   "roomCode": "AC22030010181202",
   "appId": "j7Tb2GcE9rN5oF6xP3A4qwer",
   "streamType": 2,
   "videoCodec": "",
   "reportSdkLog": false,
   "padCode": "AC22030010181",
   "msg": null,
   "signalServer": "LnBbVX4AD1CA4uyoN1kXp:P8H01PaGZDHEFDsnU6nRCbOFzvL2smbG9HxKh+XP5WHC",
   "stuns": "pL25iYgaA12RNmdCYR/:SUJD21Bz4S6HE88GzVN8rANlfL9925iaHW+ilJAaWldPpoBKqwoEq0Ggon0HhDc4a6v0pg=",
   "turns": "doF22kA7Z6OiVP1br29:rA1R4d6Vyk9efIFX6qPPMyKs7OhmxFA7xBr65P8NA/Rxb31Js6VOaO3Zrtd3h9uM/mNYUy5mJOQ4j8TJ8DjfBFaEHVNOAcF5tzgbg8iksGhNONfv8hHw=="
  }
 ]
}
```

**错误码**

| 错误码 | 错误说明             | 操作建议                 |
| ------ | -------------------- | ------------------------ |
| 120005 | 实例不存在           | 请检查实例编号是否正确   |
| 120007 | 此接口暂不支持此功能 | 联系相关人员更改推流配置 |

#### **申请RTC共享房间Token**

用于实现多个实例在一个房间中，实例接收房间广播消息进行处理与实现获取公共流

> 房间号生成规则：terimer + userId + paas用户标识
> 例如：terimer = pc，userId=123，paas用户标识=qwer
>
> 房间号为：pc123qwer

**接口地址**

> /rtc/open/room/share/applyToken

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名            | 示例值        | 参数类型 | 是否必填 | 参数描述                      |
| ----------------- | ------------- | -------- | -------- | ----------------------------- |
| userId            | 202           | String   | 是       | 调用方业务用户ID              |
| terminal          | pc            | String   | 是       | 终端                          |
| expire            | 3600          | Integer  | 否       | token有效期 单位秒。默认1小时 |
| pushPublicStream  | true          | Boolean  | 否       | 是否推送公共流。`true`推送/`false`不推送，默认`false` |
| pads              |               | Array    | 是       | 需要加入共享房间的实例列表    |
| ├─padCode         | AC22010010842 | String   | 是       | 实例id                        |
| ├─├─videoStream   |               | Object   | 否       | 推流配置                      |
| ├─├─├─videoStream | 1             | String   | 否       |                               |
| ├─├─├─frameRate   | 30            | String   | 否       |                               |
| ├─├─├─bitrate     | 2000          | String   | 否       |                               |

**响应参数**

| 参数名      | 示例值                                 | 参数类型 | 参数描述  |
| ----------- | -------------------------------------- | -------- | --------- |
| code        | 200                                    | Integer  | 状态码    |
| msg         | success                                | String   | 响应消息  |
| ts          | 1756021167163                          | Long     | 时间戳    |
| data        |                                        | Object   |           |
| ├─roomToken | 00165b7AS149e52467a4016f050b8cQQBDjDJKuTAb | String   | 房间Token |
| ├─roomCode  | android_12345                          | String   | 房间号    |
| ├─appId     | 65b749e52467a4016f050b8c               | String   | 应用id    |

**请求示例**

```javascript
{
 "userId": "202",
 "terminal": "pc",
 "expire": 3600,
 "pushPublicStream": true,
 "pads": [
  {
   "padCode": "AC22010010842",
   "videoStream": {
    "resolution": "1",
    "frameRate": "30",
    "bitrate": "2000"
   }
  },
  {
   "padCode": "AC22030010181",
   "videoStream": {
    "resolution": "1",
    "frameRate": "30",
    "bitrate": "2000"
   }
  }
 ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": null,
 "data": {
  "roomToken": "00165b7AS149e52467a4016f050b8cQQBDjDJKuTAbnZVwU52UOAENSTTExMDEwMDAwMDExAwAxMjMFAAAAXBTnZQEAXBTnZQIAXBTnZQMAXBTnZQQAAAAAACAADCbuyT9crLX9MNUCWyFhsFXwb4nuFPxfgE7MqHjv4yQ=",
  "roomCode": "android_12345",
  "appId": "65b749e52467a4016f050b8c"
 }
}
```

**接口概要**

作用：创建申请RTC共享房间Token。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

#### **修改实例时区**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

**接口地址**

**接口概要**

作用：修改修改实例时区。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

> /openapi/open/pad/updateTimeZone

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值        | 参数类型 | 是否必填 | 参数描述    |
| -------- | ------------- | -------- | -------- | ----------- |
| timeZone | Asia/Shanghai | String   | 是       | UTC标准时间 |
| padCodes |               | Array    | 是       | 实例列表    |

**响应参数**

| 参数名          | 示例值        | 参数类型 | 参数描述                         |
|--------------| ------------- | -------- | -------------------------------- |
| code         | 200           | Integer  | 状态码                           |
| msg          | success       | String   | 响应消息                         |
| ts           | 1756021167163 | Long     | 时间戳                           |
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| data         |               | Object   |                                  |
| ├─taskId     | 24            | Long     | 任务ID                           |
| ├─padCode    | AC22030010001 | String   | 房间号                           |
| ├─vmStatus   | 实例状态      | Integer  | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
| ├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "padCodes": [
  "AC32010140003"
 ],
 "timeZone": "Asia/Shanghai"
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756313802157,
        "data": [
        {
            "taskId": 760460229,
            "padCode": "ACP250417QAGGQ3S",
            "vmStatus": 0,
            "taskStatus": 1
        }
    ],
        "traceId": "ewab9p712ww0"
}
```

#### **修改实例语言**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

**接口地址**

**接口概要**

作用：修改修改实例语言。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

> /openapi/open/pad/updateLanguage

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| -------- | ------ | -------- | -------- | -------- |
| language | zh     | String   | 是       | 语言     |
| country  | CN     | String   | 否       | 国家     |
| padCodes |        | Array    | 是       | 实例列表 |

**响应参数**

| 参数名           | 示例值        | 参数类型 | 参数描述                         |
|---------------| ------------- | -------- | -------------------------------- |
| code          | 200           | Integer  | 状态码                           |
| msg           | success       | String   | 响应消息                         |
| ts            | 1756021167163 | Long     | 时间戳                           |
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| data          |               | Object   |                                  |
| ├─taskId      | 24            | Long     | 任务ID                           |
| ├─padCode     | AC22030010001 | String   | 房间号                           |
| ├─vmStatus    | 实例状态      | Integer  | 实例在线状态（0：离线；1：在线） |
| ├─ taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）|

**请求示例**

```javascript
{
 "padCodes": [
  "AC32010140026"
 ],
 "language": "zh",
 "country": ""
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1717570663080,
 "traceId": "ewab9p712ww0",
 "data": [
  {
   "taskId": 24,
   "padCode": "AC32010140026",
   "vmStatus": 1,
      "taskStatus": 1

  }
 ]
}
```

#### **修改实例SIM卡信息**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

**接口地址**

**接口概要**

作用：修改修改实例SIM卡信息。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

> /openapi/open/pad/updateSIM

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名           | 示例值                  | 参数类型   | 是否必填 | 参数描述                           |
| ---------------- |----------------------|--------|------|--------------------------------|
| imei             | 868034031518269      | String | 否    | IMEI号                          |
| imeisv             | 00      | String | 否    | 版本号                            |
| operatorShortnam | CMSS                 | String | 否    | 运营商简称                          |
| operatorLongname | CHINA MOBILE                | String | 否    | 运营商全称                          |
| iccid | 89860002191807255576                | String | 否    | SIM卡的唯一标识                      |
| imsi             | 460074008004488      | String | 否    | 前缀为sim卡运营商号：MCC(3位)+MNC(2位或3位) |
| phonenum         | 18511112222          | String | 否    | 电话号码                           |
| mcc       | 502                  | String | 否    | 网络所属国家                         |
| mnc       | 146                  | String | 否    | 移动设备网络代码                       |
| padCodes         |                      | Array  | 是    | 实例列表                           |
| type         | 1                    | String | 是    | 网络类型                           |
| tac         | 871420                    | String | 是    | 追踪区域码                          |
| cellid         | 870091003                    | String | 是    | 基站 ID                          |
| narfcn         | 99240                    | String | 是    | 用于 5G 网络中标识信道的频点编号             |
| physicalcellid         | 6C                    | String | 是    | 用来标识 5G 或 LTE 网络中的特定小区         |

**响应参数**

| 参数名     | 示例值        | 参数类型 | 参数描述                         |
| ---------- | ------------- | -------- | -------------------------------- |
| code       | 200           | Integer  | 状态码                           |
| msg        | success       | String   | 响应消息                         |
| ts         | 1756021167163 | Long     | 时间戳                           |
| data       |               | Object   |                                  |
| ├─taskId   | 24            | Long     | 任务ID                           |
| ├─padCode  | AC22030010001 | String   | 房间号                           |
| ├─vmStatus | 实例状态      | Integer  | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |

**请求示例**

```javascript
{
    "padCodes": ["AC32010230011"],
        "imei": "868034031518269",
        "imeisv": "00",
        "operatorLongname": "CHINA MOBILE",
        "operatorShortnam": "CMSS",
        "iccid": "89860002191807255576",
        "imsi": "460074008004488",
        "phonenum": "861234566",
        "type": "9",
        "mcc": "502",
        "mnc": "146",
        "tac": "871420",
        "cellid": "870091003",
        "narfcn": "99240",
        "physicalcellid": "6C"
}

```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1717570663080,
 "data": [
  {
   "taskId": 24,
   "padCode": "AC32010140033",
   "vmStatus": 1
  }
 ]
}
```

#### **设置实例经纬度**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `1124`)

**接口地址**

**接口概要**

作用：修改设置实例经纬度。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

> /openapi/open/pad/gpsInjectInfo

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名                          | 示例值        | 参数类型  | 是否必填 | 参数描述                    |
|------------------------------|------------|-------|------|-------------------------|
| longitude                    | 116.397455 | Float | 是    | 经度                      |
| latitude                     | 39.909187  | Float | 是    | 纬度                      |
| altitude                     | 8          | Float | 否    | 海拔 (需要更新到最新镜像)          |
| speed                        | 8          | Float | 否    | 速度，m/s (20251024之后的镜像)  |
| bearing                      | 0          | Float | 否    | 速度方向，°  (20251024之后的镜像) |
| horizontalAccuracyMeters     | 0.1        | Float | 否    | 水平精度 (20251024之后的镜像)    |
| padCodes                     |            | Array | 是    | 实例列表                    |

**响应参数**

| 参数名     | 示例值        | 参数类型 | 参数描述                         |
| ---------- | ------------- |--------| ------------------------------- |
| code       | 200           | Integer | 状态码                           |
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| msg        | success       | String | 响应消息                         |
| ts         | 1756021167163 | Long   | 时间戳                           |
| data       |               | Boolean    |                                 |

**请求示例**

```javascript
{
 "padCodes": [
  "AC32010030001"
 ],
 "longitude": 116.397455,
 "latitude": 39.909187,
 "altitude": 8
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1717570663080,
 "traceId": "ewab9p712ww0",
 "data": true
}
```

#### **执行任务：查询代理出口IP信息**

**接口类型**: 同步接口

该接口仅创建任务并返回任务ID与执行状态等信息，结果需要通过`/task-center/open/task/padTaskDetail`查询，返回字段`taskResult`对应`pad_task.result`。

**接口概要**

作用：执行执行任务：查询代理出口IP信息。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/network/proxy/info

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| -------- | ------ | -------- | -------- | -------- |
| padCodes |        | Array    | 是       | 实例列表 |

**响应参数**

| 参数名     | 示例值        | 参数类型 | 参数描述                         |
| ---------- | ------------- | -------- | -------------------------------- |
| code       | 200           | Integer  | 状态码                           |
| msg        | success       | String   | 响应消息                         |
| ts         | 1756021167163 | Long     | 时间戳                           |
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| data       |               | Object   |                                  |
| ├─taskId   | 24            | Long     | 任务ID                           |
| ├─padCode  | AC22030010001 | String   | 房间号                           |
| ├─vmStatus | 实例状态      | Integer  | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
| ├─ taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）|

**请求示例**

```javascript
{
  "padCodes": [
    "AC32010140012"
  ]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756348835040,
        "data": [
        {
            "taskId": 14294,
            "padCode": "ACP250820SBM4NEU",
            "vmStatus": 0,
            "taskStatus": 1
        }
    ],
        "traceId": "ewbrcry0frb4"
}
```

 /openapi/open/pad/data/backup

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes | AC32010100001 | [] | 是 | 实例id列表
backupNamePrefix | test | String | 否 | 数据备份名称前缀

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1721739857317 | Long | 时间戳
data |  | Object |
├─taskId | 12818 | Long | 任务ID
├─padCode | AC22030010124 | String | 实例编号

**请求示例**

```json
{
  "padCodes": [
    "AC32010100001"
  ],
  "backupNamePrefix": "test"
}
```

**响应示例**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1733212452565,
  "data": [
    {
      "taskId": 2447,
      "padCode": "AC32010100001",
      "backupName": "test_AC32010100001_20241203155412"
    }
  ]
}
``` -->

 /openapi/open/pad/data/del

**请求方式**

> POST（删除备份数据，支持批量删除，一批最多支持200个）

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | -- | --- | ---
padCode | AC32010100001 | String | 是 | 实例编号
backupName | 12345_AC32010230011_20241218143659 | String | 是 | 数据备份名称

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1721739857317 | Long | 时间戳
data |  | Boolean |

**请求示例**

```json
{
  "dataDelDTOS": [
    {
      "backupName": "OpenApi_AC32010230012_20241220161011",
      "padCode": "AC32010230012"
    },
    {
      "backupName": "12345_AC32010230011_20241218143659",
      "padCode": "AC32010230011"
    }
  ]
}
```

**响应示例(全部成功)**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1733212452565,
  "data": true
}
```

**响应示例(部分成功)**

```json
{
  "code": 200,
  "msg": "删除成功,存在无效实例编码与数据备份名称",
  "ts": 1734934603646,
  "data": [
    {
      "padCode": "AC32010230011",
      "backupName": "OpenApi_AC32010230012_20241220161011"
    }
  ]
}
``` -->

 注意：因数据是全量替换，有可能会当前实例导致数据丢失。请谨慎使用！

把备份到云空间的数据恢复到指定实例，恢复数据的内容包括以下

- 已安装的APP
- 实例磁盘上的所有数据（图库文件、下载的文件等）
- 改机属性

**接口地址**

> /openapi/open/pad/data/restore

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes | [] | Array | 是 | 实例id列表
backupName | test_AC32010100001_20241211174508 | String | 是 | 数据备份名称

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1721739857317 | Long | 时间戳
data |  | Object |
├─taskId | 12818 | Long | 任务ID
├─padCode | AC22030010124 | String | 实例编号

**请求示例**

```json
{
  "padCodes": [
    "AC32010030001"
  ],
  "backupName": "test_AC32010100001_20241211174508"
}
```

**响应示例**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1717570615524,
  "data": [
    {
      "taskId": 23,
      "padCode": "AC22030010124"
    }
  ]
}
``` -->

#### **一键新机**

**接口类型**: 异步接口
**关联回调**: [一键新机回调](#一键新机回调) (taskBusinessType: `-`)
>
> 注意：一键新机会清除系统所有数据。请谨慎使用！

一键新机功能，将当前实例数据全部清空,并重新设置安卓属性

**接口概要**

作用：处理一键新机。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

- 虚拟机直接设置安卓属性,然后清空所有数据
- 云真机直接清空所有数据(等同于重置),并且添加SIM信息,如果有传入模板id,会替换adi模板.如果没有传入模板,并且replacementRealAdiFlag为true.会随机挑选一个模板Id
- 注意:如果不传国家信息,或者传入的国家信息服务找不到,会默认设置上新加坡的SIM信息
- 如果传入的国家不支持,会返回错误500,提示:目前不支持国家编码XX

**接口地址**

> /openapi/open/pad/replacePad

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值                                                 | 参数类型   | 是否必填 | 参数描述
--- |-----------------------------------------------------|--------|------| ---
padCodes | []                                                  | Array  | 是    | 实例id列表
countryCode | SG                                                  | String | 否    | 国家编码，默认值`SG`。[查看所有国家编码↗](./EnumReference.md#51-countrycode---国家编码)
realPhoneTemplateId | 65                                                  | Long   | 否    | 模板id(从/openapi/open/realPhone/template/list接口获取)
androidProp | {"persist.sys.cloud.wifi.mac": "D2:48:83:70:66:0B"} | Object | 否    | 参考 [安卓改机属性列表](./InstanceAndroidPropList.html)
replacementRealAdiFlag | false                                               | Boolean | 否    | 真机是否随机ADI模板。`true`随机/`false`不随机，默认`false`
excludeRealPhoneTemplateIds | [101,102]                                         | Long[]  | 否    | 随机ADI模板时需排除的模板ID列表
certificate | 参考[手机根证书](./PhoneCertificate.html)                  | String | 否    | 手机根证书
wipeData | true                                                | Boolean | 否    | 是否清除用户数据。`true`清除数据/`false`不清除，默认`true`（CBS2.4.4以上版本支持）
wipeSpecificData | ["/fonts","/media"]                                 | String[] | 否    | wipeData为false该参数生效；需要清除哪些数据
enableCpuCoreConfig | true                                                | Boolean | 否    | 是否启用CPU大小核配置。`true`启用/`false`不启用，默认`true`。本功能基于 Android cpuset 机制，为云手机物理机上的多个容器提供静态错峰的 CPU 资源分配方案。通过精细化划分大小核（Little/Big Cores）资源，显著提升单容器的性能稳定性与用户体验。

**响应参数**

参数名 | 示例值           | 参数类型    | 参数描述
--- |---------------|---------| ---
code | 200           | Integer | 状态码
msg | success       | String  | 响应消息
ts | 1721739857317 | Long    | 时间戳
 traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |               | Object  |
├─taskId | 12818         | Long    | 任务ID
├─padCode | AC22030010124 | String  | 实例编号
├─vmStatus | 实例状态      | Integer  | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```json
{
  "padCodes": ["AC32010250031"],
  "countryCode": "SG",
  "realPhoneTemplateId": 210,
  "androidProp": {
    "persist.sys.cloud.battery.level": "67",
    "persist.sys.cloud.gps.lat": "1.3657",
    "persist.sys.cloud.gps.lon": "103.6464",
    "persist.sys.cloud.imsinum": "525050095718767"
  },
  "replacementRealAdiFlag": true,
  "excludeRealPhoneTemplateIds": [101, 102],
  "certificate": "手机根证书",
  "wipeData": false,
  "wipeSpecificData": ["/fonts", "/media"]
}
```

**响应示例1**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1732270378320,
  "data": {
    "taskId": 8405,
    "padCode": "AC32010250031",
    "vmStatus": 2,
    "taskStatus": 1
  },
  "traceId": "ewab8qjqbaio"
}
```
**响应示例2**
```json
{
   "code": 500,
   "msg": "目前不支持国家编码: xx",
   "ts": 1753521350163,
   "data": null,
    "traceId": "ewab8qjqbaio"

}
```

#### **查询一键新机支持国家列表**

**接口类型**: 同步接口

**接口地址**

**接口概要**

作用：查询查询一键新机支持国家列表。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

> /openapi/open/info/country

**请求方式**

> GET

**请求数据类型**

> application/json

**响应参数**

参数名 | 示例值           | 参数类型    | 参数描述
--- |---------------|---------| ---
code | 200           | Integer | 状态码
msg | success       | String  | 响应消息
ts | 1721739857317 | Long    | 时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |               | Object[]  |
├─code | AD         | String    | 国家编码
├─name | Andorra | String  | 国家名称(英文)

**响应示例**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1730192434383,
  "traceId": "ewab8qjqbaio",
  "data": [{
    "code": "AD",
    "name": "Andorra"
  }]
}
```

#### **更新通讯录**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `1201`)

> fileUniqueId和info必填一个

**接口地址**

**接口概要**

作用：修改更新通讯录。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

> /openapi/open/pad/updateContacts

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值                             | 参数类型     | 是否必填 | 参数描述
--- |---------------------------------|----------| --- | ---
padCodes | []                              | Array    | 是 | 实例id列表
fileUniqueId | cfca25a2c62b00e065b417491b0cf07ffc | String   | 否 | 通讯录文件ID
operateType | -1                              | Interger | 否 | 操作类型。可选值：`-1`新增联系人/`0`删除联系人/`1`覆盖联系人，默认`-1`
info |                                 | Object[] | 否 | 通讯录信息
├─firstName | tom                             | String   | 否 | 姓名
├─phone | 13111111111                     | String   | 否| 手机号
├─email |                  | String   | 否| 邮箱

**响应参数**

参数名 | 示例值           | 参数类型    | 参数描述
--- |---------------|---------| ---
code | 200           | Integer | 状态码
msg | success       | String  | 响应消息
ts | 1721739857317 | Long    | 时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |               | Object  |
├─taskId | 12818         | Long    | 任务ID
├─padCode | AC22030010124 | String  | 实例编号
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|
├─vmStatus | 实例状态      | Integer  | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |

**请求示例**

```json
{
  "fileUniqueId": "cfca25a2c62b00e065b417491b0cf07ffc",
  "info": [{
    "firstName": "tom",
    "phone": "13111111111",
    "email": "xxxxx@gmail.com"
  }],
  "padCodes": [
    "AC32010180326"
  ]
}
```

**响应示例**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1756373645105,
  "data": [
    {
      "taskId": 392077,
      "padCode": "ATP250822LBOD8V7",
      "vmStatus": 0,
      "taskStatus": 1
    }
  ],
  "traceId": "ewcs8ow5u328"
}
```

#### **实例设置代理**

**接口类型**: 同步接口

**接口地址**

**接口概要**

作用：修改实例设置代理。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

> /openapi/open/network/proxy/set

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值      | 参数类型 | 是否必填 | 参数描述 |
| -------- | ----------- | -------- |------| -------- |
| account  | 2222        | String   | 否    | 账号     |
| password | 2222        | String   | 否    | 密码     |
| ip       | 47.76.241.5 | String   | 否    | IP       |
| port     | 2222        | Integer  | 否    | 端口     |
| enable   | true        | Boolean  | 是    | 启用     |
| padCodes |             | Array    | 是    | 实例列表 |
| proxyType |   vpn          | String    | 否    | 代理类型。可选值：`proxy`代理/`vpn`VPN |
| proxyName |   socks5          | String    | 否    | 代理名称。可选值：`socks5`SOCKS5代理/`http-relay`HTTP/HTTPS代理 |
| bypassPackageList       |  | Array   | 否    | 包名 设置该包名不走代理  |
| bypassIpList       |  | Array   | 否    | ip  设置该ip不走代理 |
| bypassDomainList       |  | Array   | 否    | 域名  设置该域名不走代理  |
| sUoT   | true        | Boolean  | 否    | 是否开启UDP连接。`true`开启/`false`不开启，默认`false` |

**响应参数**

| 参数名          | 示例值        | 参数类型 | 参数描述                         |
|--------------| ------------- | -------- | -------------------------------- |
| code         | 200           | Integer  | 状态码                           |
| msg          | success       | String   | 响应消息                         |
| ts           | 1756021167163 | Long     | 时间戳                           |
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| data         |               | Object   |                                  |
| ├─taskId     | 24            | Long     | 任务ID                           |
| ├─padCode    | AC22030010001 | String   | 房间号                           |
| ├─vmStatus   | 实例状态      | Integer  | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
| ├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "padCodes": [
  "AC32010140023"
 ],
 "account": "2222",
 "password": "2222",
 "ip": "47.76.241.5",
 "port": 2222,
 "enable": true,
    "bypassPackageList":[],
    "bypassIpList":[],
    "bypassDomainList":[],
    "sUoT":true
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756313787216,
        "data": [
        {
            "taskId": 22323879,
            "padCode": "ACN250828ED53YMG",
            "vmStatus": 0,
            "taskStatus": 1
        }
    ],
        "traceId": "ewab8whwonb4"
}
```

#### **实时查询已安装的应用列表**

**接口类型**: 同步接口

**接口地址**

**接口概要**

作用：查询实时查询已安装的应用列表。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

> /openapi/open/pad/listInstalledApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值      | 参数类型 | 是否必填 | 参数描述                   |
| -------- | ----------- | -------- |------|------------------------|
| padCodes |  AC32010250001     | String[]    | 是    | 实例编号                   |
| appName |             | String    | 否    | 应用名称                |

**响应参数**

| 参数名     | 示例值 | 参数类型 | 参数描述                    |
| ---------- |---|------|-------------------------|
| code       | 200 | Integer | 状态码                     |
| msg        | success | String | 响应消息                    |
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| ts         | 1756021167163 | Long | 时间戳                     |
| data       |   | Object |                         |
| ├─padCode   | AC32010250001 | String | 实例编号 |
| ├─apps |   | Object[] | 应用集合
| ├─├─appName | 测试app | String |  应用名称
| ├─├─packageName | com.xxx.xxx | String |  包名
| ├─├─versionCode | 150600 | String |  版本号
| ├─├─versionName | 15.6.0 | String |  版本名称
| ├─├─appState | 0 | Integer |  0 已完成  1安装中   2下载中

**请求示例**

```javascript
{
 "padCodes": ["AC32010250001"],
 "appName": ""
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756313784076,
        "data": [
        {
            "padCode": "ACP250417KYBOAXK",
            "apps": [
                {
                    "appName": "WeChat",
                    "packageName": "com.tencent.mm",
                    "versionCode": "2900",
                    "versionName": "8.0.62",
                    "appState": 0
                }
            ]
        }
    ],
        "traceId": "ewab8qh6vwg1"
}
```

#### **设置应用自启动**

**接口类型**: 同步接口

用于单个或多个实例配置应用开机自启动功能。本接口为覆盖修改，若需修改自启动应用以新自启动应用清单覆盖当前自启动应用清单再调用本接口即可。
- 当 `applyAllInstances=true` 时，不下发任务，配置保存到数据库，**等下次开机才生效**，应用于所有实例（包括未来新建的实例）
- 当 `applyAllInstances=false` 时，下发任务到指定实例，**任务执行后立即生效**
- `padCodes` 和 `applyAllInstances` 互斥，优先使用 `applyAllInstances`

**接口概要**

作用：修改设置应用自启动。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

目前只支持安卓13、14、15

**接口地址**

> openapi/open/pad/setKeepAliveApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值      | 参数类型     | 是否必填 | 参数描述   |
| -------- | ----------- |----------|------|--------|
| padCodes |  AC32010250001     | String[] | 否    | 实例编号（applyAllInstances=false时必填） |
| applyAllInstances |  false     | Boolean  | 是    | 是否应用所有实例模式。`true`应用所有实例（不下发任务，等下次开机才生效）/`false`不应用，默认`false`。与padCodes互斥，优先级更高 |
| appInfos |             | Object[] | 否    |        |
| ├─serverName | com.example/com.example.service.TaskService | String   | 是    | com.xxx.xxx（包名）/com.xxx.xxx.service.DomeService  (需要启动的服务完整路径) |

**响应参数**

| 参数名     | 示例值           | 参数类型   | 参数描述                    |
| ---------- |---------------|--------|-------------------------|
| code       | 200           | Integer | 状态码                     |
| msg        | success       | String | 响应消息                    |
| ts         | 1756021167163 | Long   | 时间戳                     |
| data       |               | null |                         |

**请求示例**

```javascript
{
 "padCodes": [
  "AC002",
  "AC001"
 ],
 "appInfos": [{
   "serverName": "com.example/com.example.service.TaskService"
  }
 ],
 "applyAllInstances": false
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1736326542985,
        "data": [{
        "taskId": 10074,
        "padCode": "AC32010250011",
        "errorMsg": null
    }]
}
```

#### **设置应用保活(新)**

**接口类型**: 同步接口

用于单个或多个实例配置应用保活功能，并设置保活应用名单。开启后，名单内的应用在实例内存不足时不会被系统杀死。默认对应用保活进行持久化配置（实例重启也会生效）
本接口为覆盖修改，若需修改保活应用以新保活应用清单覆盖当前保活应用清单再调用本接口即可。

**接口概要**

作用：修改设置应用保活(新)。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> openapi/open/pad/setKeepAliveApp/new

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值      | 参数类型     | 是否必填 | 参数描述   |
| -------- | ----------- |----------|------|--------|
| padCodes |  AC32010250001     | String[] | 是    | 实例编号（最多500个） |
| appInfos |             | Object[] | 是    | 保活应用列表，空数组表示清空（最多保活3个应用） |
| ├─packageName | com.tencent.mm | String   | 否    | 应用包名，留空或空数组表示清空 |

**响应参数**

| 参数名     | 示例值           | 参数类型   | 参数描述                    |
| ---------- |---------------|--------|-------------------------|
| code       | 200           | Integer | 状态码                     |
| msg        | success       | String | 响应消息                    |
| ts         | 1756021167163 | Long   | 时间戳                     |
| data       |               | null |                         |

**请求示例**

```javascript
{
 "padCodes": [
  "AC002",
  "AC001"
 ],
 "appInfos": [{
   "packageName": "com.tencent.mm"
  }]
}
```

**清空保活列表示例**

```javascript
{
 "padCodes": [
  "AC002",
  "AC001"
 ],
 "appInfos": []
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1736326542985,
    "data": null
}
```

#### **设置应用隐藏**

**接口类型**: 同步接口

下发隐藏包名列表到指定实例，允许包名列表为空（为空则清空隐藏列表并下发空列表）。需要注意：当应用未安装时，设置不会生效，需在安装后进行重启才可生效。

**接口概要**

作用：修改设置应用隐藏。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> openapi/open/pad/setHideAppList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值      | 参数类型     | 是否必填 | 参数描述                   |
| -------- | ----------- |----------|------|------------------------|
| padCodes |  AC32010250001     | String[] | 是    | 实例编号（最多200个）           |
| appInfos |             | Object[] | 是    | 隐藏应用列表，空数组表示清空（0-200个） |
| ├─packageName | com.tencent.mm | String   | 否    | 应用包名，留空或空数组表示清空        |

**响应参数**

| 参数名     | 示例值           | 参数类型   | 参数描述                    |
| ---------- |---------------|--------|-------------------------|
| code       | 200           | Integer | 状态码                     |
| msg        | success       | String | 响应消息                    |
| ts         | 1756021167163 | Long   | 时间戳                     |
| data       |               | null |                         |

**请求示例**

```javascript
{
 "padCodes": [
  "AC002",
  "AC001"
 ],
 "appInfos": [{
   "packageName": "com.tencent.mm"
  }]
}
```

**清空隐藏列表示例**

```javascript
{
 "padCodes": [
  "AC002",
  "AC001"
 ],
 "appInfos": []
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1736326542985,
    "data": null
}
```

#### **隐藏辅助服务**

下发需隐藏辅助服务权限的应用列表到指定实例，设置成功后被设置隐藏权限的应用将不会被同实例上其他应用检测到申请了辅助服务权限。
说明：
1.指定应用本身能获取到自己开了无障碍
2.三方应用获取不到指定应用开了无障碍
3.无障碍列表里面也没有这个指定应用

**接口地址**

> /openapi/open/pad/setHideAccessibilityAppList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值      | 参数类型     | 是否必填 | 参数描述                   |
| -------- | ----------- |----------|------|------------------------|
| padCodes |  ["AC32010250001"]     | String[] | 是    | 实例编号数组（最多200个）           |
| appInfos |  []           | Object[] | 是    | 隐藏应用列表对象数组，传空数组[]表示清空（0-200个） |
| ├─packageName | com.tencent.mm | String   | 是（数组非空时）    | 应用包名。特殊值：传 `*` 或 `ALL` 表示隐藏所有应用的辅助服务权限        |

**响应参数**

| 参数名     | 示例值           | 参数类型   | 参数描述                    |
| ---------- |---------------|--------|-------------------------|
| code       | 200           | Integer | 状态码                     |
| msg        | success       | String | 响应消息                    |
| ts         | 1756021167163 | Long   | 时间戳                     |
| data       |               | null |                         |

**请求示例 - 隐藏指定应用**

```javascript
{
 "padCodes": [
  "AC002",
  "AC001"
 ],
 "appInfos": [{
   "packageName": "com.tencent.mm"
  }]
}
```

**请求示例 - 清空隐藏列表**

```javascript
{
 "padCodes": [
  "AC002",
  "AC001"
 ],
 "appInfos": []
}
```

**请求示例 - 隐藏所有应用**

```javascript
{
 "padCodes": [
  "AC002",
  "AC001"
 ],
 "appInfos": [{
   "packageName": "*"
  }]
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1736326542985,
    "data": null
}
```

**接口概要**

作用：处理隐藏辅助服务。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

#### **修改真机ADI模板**

**接口类型**: 同步接口

修改实例云真机ADI模版, 传入云真机模版ID

**接口概要**

作用：修改修改真机ADI模板。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

必要条件：

1. 实例创建时，需要创建为云真机类型
2. 实例创建时的安卓版本，需要和目标的ADI安卓版本一致

**接口地址**

> /openapi/open/pad/replaceRealAdiTemplate

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名  | 示例值           | 参数类型     | 是否必填 | 参数描述    |
| ------- |---------------|----------|------|---------|
|padCodes |               | String[] | 是    |         |
|├─ | AC21020010001 | String   | 是    | 实例编号    |
|wipeData | false         | Boolean  | 是    | 是否清除数据  |
|realPhoneTemplateId | 186             | Long     | 是    | 云真机模板id |

**响应参数**

| 参数名          | 示例值 | 参数类型 | 参数描述|
|--------------| --- | --- | ---|
| code         | 200 | Integer | 状态码|
| msg          | success | String | 响应消息|
| ts           | 1756021167163 | Long | 时间戳|
| data         | | Object[] | |
| ├─taskId     | 1 | Integer | 任务ID|
| ├─padCode    | AC21020010001 | String | 实例编号|
| ├─vmStatus   | 1 | Integer | 实例在线状态（0：离线；1：在线）|
| ├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```json
{
 "padCodes": ["AC32010250011"],
 "wipeData": true,
 "realPhoneTemplateId": 186
}
```

**响应示例**

```json
{
 "code": 200,
 "msg": "success",
 "ts": 1736326542985,
 "data": [{
  "taskId": 10074,
  "padCode": "AC32010250011",
  "errorMsg": null,
   "taskStatus": 1
 }]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110028 | 实例不存在| 联系管理员
110064 | 当前实例中有不满足升级真机条件,请检查实例| 检查实例是否是真机
110099 | ADI模板不存在,请检查参数| 检查ADI模板信息

#### **异步执行ADB命令**

**接口类型**: 异步接口
**关联回调**: [异步执行ADB任务回调](#异步执行adb任务回调) (taskBusinessType: `-`)

在一个或多个云手机实例中异步执行命令

**接口概要**

作用：执行异步执行ADB命令。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/asyncCmd

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述|
|--- | --- | --- | --- | ---|
|padCodes |  | String[] | 是 |
|├─ | AC22020020793 | String | 是 | 实例编号|
|scriptContent | cd /root;ls | String | 是 | ADB命令，多条命令使用分号隔开|

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String |  响应消息
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
ts | 1756021167163 | Long  | 时间戳
data |  | Object[] |
├─taskId | 1 | Integer |  任务ID
├─padCode | AC22020020793 | String |  实例编号
├─vmStatus | 1 | Integer |  实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)

**请求示例**

```json
{
    "padCodes": [
        "AC22020020793"
    ],
    "scriptContent": "cd /root;ls"
}
```

**响应示例**

```json
{
 "code": 200,
 "msg": "success",
 "ts": 1717570297639,
  "traceId": "ewab8whwonb4",
  "data": [
  {
   "taskId": 14,
   "padCode": "AC22030010001",
   "vmStatus": 1
  },
  {
   "taskId": 15,
   "padCode": "AC22030010002",
   "vmStatus": 0
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110003 | 执行ADB命令失败| 联系管理员
110012 | 命令执行超时 | 请稍后重试

#### **开关Root权限**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

在一个或多个云手机实例中开关root权限。
开个单个应用root,需要指定包名,否则会抛出异常.(云真机产品，在调用此接口时，不建议设置全局root权限，会有被风控检测到的可能。)

**接口概要**

作用：操作开关Root权限。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/switchRoot

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值           | 参数类型     | 是否必填 | 参数描述                     |
|--- |---------------|----------|------|--------------------------|
|padCodes |               | String[] | 是    |
|├─ | AC22020020793 | String   | 是    | 实例编号                     |
|globalRoot | false         | Boolean  | 否    | 是否开启全局root权限。`true`开启全局root/`false`不开启，默认`false` |
|packageName | com.example        | String   | 否    | 应用包名(非全局root必传)多个包名通过,连接 |
|rootStatus | root开启状态         | Integer  | 是    | root状态。可选值：`0`关闭/`1`开启。[详见枚举↗](./EnumReference.md#113-rootstatus---root状态) |

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long  | 时间戳
data |  | Object[] |
├─taskId | 1 | Integer |  任务ID
├─padCode | AC22020020793 | String |  实例编号
├─vmStatus | 1 | Integer |  实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)

**请求示例**

```json
{
  "padCodes": [
    "AC32010250002"
  ],
  "globalRoot": false,
  "packageName": "com.android.ftpeasys",
  "rootStatus": 0
}

```

**响应示例**

```json
{
 "code": 200,
 "msg": "success",
 "ts": 1717570297639,
 "data": [
  {
   "taskId": 14,
   "padCode": "AC32010250002",
   "vmStatus": 1
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110003 | 执行ADB命令失败| 联系管理员
110089 | 开启单个root包名不能为空 | 开启单个应用root时，包名不能为空

#### **本地截图**

实例截图。

**接口URL**

> openapi/open/pad/screenshot

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名    | 示例值   | 参数类型 | 是否必填 | 参数描述                                                                     |
| ---- | ---- | ---- | ---- |--------------------------------------------------------------------------|
|padCodes |  | String[] | 是 |                                                                          |
|├─ | AC21020010231 | String | 是 | 实例编号                                                                     |
| rotation  | 0 | Integer  | 是 | 截图画面横竖屏旋：0：截图方向不做处理，默认；1：截图画面旋转为竖屏时：a：手机竖屏的截图，不做处理。b：手机横屏的截图，截图顺时针旋转90度。 |
| broadcast | false    | Boolean  | 否 | 事件是否广播。`true`广播/`false`不广播，默认`false` |
| definition | false    | Integer  | 否 | 清晰度 取值范围0-100                                                            |
| resolutionHeight | false    | Integer  | 否 | 分辨率 - 高 大于1                                                              |
| resolutionWidth | false    | Integer  | 否 | 分辨率 - 宽 大于1                                                              |

**响应参数**

参数名 | 示例值 | 参数类型 |是否必填| 参数描述
--- | --- | --- | --- | ---
code | 200 | Integer | 是 | 状态码
msg | success | String | 是 | 响应消息
ts | 1756021167163 | Long | 是 | 时间戳
data |  | Object[] |  |
├─taskId | 1 | Integer | 否 | 任务ID
├─padCode | AC21020010231 | String | 否 | 实例编号
├─vmStatus | 1 | Integer | 是 | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)

**请求示例**

```json
{
 "padCodes": [
  "AC21020010231"
 ],
 "rotation": 0,
 "broadcast": false,
    "definition": 50,
    "resolutionHeight": 1920,
    "resolutionWidth": 1080
}
```

**响应示例**

```json
{
 "code": 200,
 "msg": "success",
 "ts": 1717570337023,
 "data": [
  {
   "taskId": 16,
   "padCode": "AC22030010001",
   "vmStatus": 1
  },
  {
   "taskId": 17,
   "padCode": "AC22030010002",
   "vmStatus": 0
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110001 | 截图失败| 请重试
110004 | 执行重启命令失败| 稍后再次重启
110028 | 实例不存在| 请检查实例是否存在

**接口概要**

作用：执行本地截图。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **获取实例实时预览图片**

**接口类型**: 同步接口

获取指定的实例，当前时间下的屏幕截图。 调用此接口，会给实例返回一个url和到期时间，在有效期内，通过访问这个url，可以获取实时的云机屏幕截图。
可以批量传多个实例编号，批量获取预览图url。

**接口概要**

作用：查询获取实例实时预览图片。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/pad/getLongGenerateUrl

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名    | 示例值           | 参数类型 | 是否必填 | 参数描述                                        |
| --------- |---------------| -------- | -------- |---------------------------------------------|
|padCodes |               | String[] | 是 |                                             |
|├─ | AC11010000031 | String | 是 | 实例编号（最多支持100个实例）                            |
| format  | png           | String  | 否       | 图片格式，枚举值：png、jpg、webp(CBS2.3.7以上版本支持)，默认jpg |
| height | 50 | String | 否 | 缩放高度（像素，不传或超出设备当前高度则使用设备当前高度）               |
| width | 50 | String | 否 | 缩放宽度（像素，不传或超出设备当前宽度则使用设备当前宽度）               |
| quality | 60 | String | 否 | 图片质量（百分比：0~100，不传或不在参数范围内则默认为60%）           |

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
data |  | Object[] |
├─padCode | AC11010000031 | String | 实例编号
├─url |  | String | 访问地址
├─expireAt | 1756024767163 | Long | URL到期时间（毫秒时间戳）
├─success | true| Boolean | 是否成功生成URL
├─reason | 实例状态异常 | String | 失败原因（成功时为空）

**请求示例**

```javascript
{
    "padCodes": [
        "AC11010000031",
        "AC11010000032"
    ],
    "format": "png"
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756021167163,
        "data": [
        {
            "padCode": "AC11010000031",
            "url": "http://xxx.armcloud.png",
            "expireAt": 1756024767163,
            "success": true,
            "reason": ""
        },
        {
            "padCode": "AC11010000032",
            "url": "",
            "expireAt": null,
            "success": false,
            "reason": "实例状态异常"
        }
    ]
}
```

#### **获取实例实时预览图片(高性能)**

**接口类型**: 同步接口
注意：新接口默认不接收尺寸、清晰度、格式等转换参数，输出图像保持云端原始分辨率与格式。若客户有特殊需求，请自行后处理。
获取指定的实例，当前时间下的屏幕截图。 调用此接口，会给实例返回一个url和到期时间，在有效期内，通过访问这个url，可以获取实时的云机屏幕截图。
可以批量传多个实例编号，批量获取预览图url。
接口说明：
高性能模式：CBS不再对截图进行任何编解码和转码处理，仅作数据透传通道，减少中间环节开销
原始输出：直接输出Rom生成的原始截图数据，保持云端原始分辨率与格式
参数简化：不接收尺寸、清晰度、格式等转换参数
对比旧接口性能优化后效果：
内存占用减少：避免原始图像完整加载至内存进行软编解码，减少双倍内存占用
响应速度提升：恢复流式传输优势，降低系统资源消耗。

**接口概要**

作用：查询获取实例实时预览图片(高性能)。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/pad/getLongGenerateUrlRaw

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名    | 示例值           | 参数类型 | 是否必填 | 参数描述                                        |
| --------- |---------------| -------- | -------- |---------------------------------------------|
|padCodes |               | String[] | 是 |                                             |
|├─ | AC11010000031 | String | 是 | 实例编号（最多支持100个实例）                            |

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
data |  | Object[] |
├─padCode | AC11010000031 | String | 实例编号
├─url |  | String | 访问地址
├─expireAt | 1756024767163 | Long | URL到期时间（毫秒时间戳）
├─success | true| Boolean | 是否成功生成URL
├─reason | 实例状态异常 | String | 失败原因（成功时为空）

**请求示例**

```javascript
{
    "padCodes": [
        "AC11010000031",
        "AC11010000032"
    ]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756021167163,
        "data": [
        {
            "padCode": "AC11010000031",
            "url": "http://xxx.armcloud.png",
            "expireAt": 1756024767163,
            "success": true,
            "reason": ""
        },
        {
            "padCode": "AC11010000032",
            "url": "",
            "expireAt": null,
            "success": false,
            "reason": "实例状态异常"
        }
    ]
}
```

#### **升级镜像**

**接口类型**: 异步接口
**关联回调**: [实例升级镜像任务回调](#实例升级镜像任务回调) (taskBusinessType: `-`)

批量实例镜像升级

**接口概要**

作用：操作升级镜像。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/upgradeImage

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes |  | String[] | 是 |
├─ | AC22030010182 | String | 是 | 实例编号
imageId | mg-24061124017 | String | 是 | 镜像ID
wipeData | false | Boolean | 是 | 是否清除实例数据（data分区）。`true`清除数据/`false`不清除数据
enableCpuCoreConfig | true                                                | Boolean | 否    | 是否启用CPU大小核配置。`true`启用/`false`不启用，默认`true`。本功能基于 Android cpuset 机制，为云手机物理机上的多个容器提供静态错峰的 CPU 资源分配方案。通过精细化划分大小核（Little/Big Cores）资源，显著提升单容器的性能稳定性与用户体验。

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |  | Object[] |
├─padCode | AC22030010182 | String | 实例编号
├─taskId | 1 | Integer | 任务ID
├─errorMsg | “” | String | 错误信息

**请求示例**

```javascript
{
    "padCodes": [
        "AC22030010182"
    ],
    "wipeData": false,
    "imageId": "mg-24061124017"
}
```

**响应示例**

```javascript
{
 "code": 200,
  "traceId": "ewab8whwonb4",
  "msg": "success",
 "ts": 1718594881432,
 "data": [
  {
   "taskId": 63,
   "padCode": "AC22030010182",
   "errorMsg": null
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110041 | 镜像不存在| 镜像id传参有误
110037 | 执行升级镜像指令失败| 实例状态有误，联系管理员
110038 | 执行升级镜像命令失败| 实例状态有误，联系管理员

#### **升级真机镜像**

**接口类型**: 异步接口
**关联回调**: [实例升级镜像任务回调](#实例升级镜像任务回调) (taskBusinessType: `-`)

批量实例真机镜像升级

**接口概要**

作用：操作升级真机镜像。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/virtualRealSwitch

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

 参数名                     | 示例值            | 参数类型 | 是否必填 | 参数描述
-------------------------|----------------|----|------|-------------------------------------------
 padCodes                |                | String[] | 是    |
 ├─                      | AC22030010182  | String | 是    | 实例编号
 imageId                 | mg-24061124017 | String | 是    | 镜像ID
 wipeData                | false          | Boolean | 是    | 是否清除实例数据(data分区)。`true`清除/`false`不清除
 realPhoneTemplateId     | 178            | Integer | 否    | 真机模板ID upgradeImageConvertType=real时必填
 upgradeImageConvertType | virtual        | String | 是    | 转换镜像类型。可选值：`virtual`虚拟机/`real`云真机
 screenLayoutId          | 14             | Integer | 否    | 屏幕布局ID upgradeImageConvertType=virtual时必填
 certificate             | 参考[手机根证书](./PhoneCertificate.html) | String | 否    | 自定义手机根证书
 deviceAndroidProps      | {"persist.sys.cloud.wifi.mac": "D2:48:83:70:66:0B"} | Object  | 否    | 安卓属性配置，参考 [安卓改机属性列表](https://docs.armcloud.net/cn/server/InstanceAndroidPropList.html)（注意：CBS版本2.4.4以下不支持 ）
enableCpuCoreConfig | true                                                | Boolean | 否    | 是否启用CPU大小核配置。`true`启用/`false`不启用，默认`true`。本功能基于 Android cpuset 机制，为云手机物理机上的多个容器提供静态错峰的 CPU 资源分配方案。通过精细化划分大小核（Little/Big Cores）资源，显著提升单容器的性能稳定性与用户体验。

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |  | Object[] |
├─padCode | AC22030010182 | String | 实例编号
├─taskId | 1 | Integer | 任务ID
├─errorMsg | “” | String | 错误信息

**请求示例**

```javascript
{
    "padCodes": [
        "AC32010210023"
    ],
        "imageId": "img-24112653977",
        "wipeData": true,
        "realPhoneTemplateId": 178,
        "upgradeImageConvertType": "virtual",
        "screenLayoutId": 14
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1718594881432,
 "traceId": "ewab8whwonb4",
    "data": [
  {
   "taskId": 63,
   "padCode": "AC22030010182",
   "errorMsg": null
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110041 | 镜像不存在| 镜像id传参有误
110037 | 执行升级镜像指令失败| 实例状态有误，联系管理员
110038 | 执行升级镜像命令失败| 实例状态有误，联系管理员
110064 | 当前实例中有不满足升级真机条件,请检查实例| 当前实例中有不满足升级真机条件,请检查实例

#### **分页获取真机模板**

**接口类型**: 同步接口

分页获取真机模板

**接口概要**

作用：查询分页获取真机模板。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/realPhone/template/list

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | -- | --- | --- | ---
pageIndex | 1 | Integer | 否 | 页码 默认1
pageSize | 10 | Integer | 否 | 每页显示数量 默认10 取值范围为1-100
androidImageVersion | 14 | String | 否 | 安卓镜像版本

**响应参数**

| 参数名          | 示例值 | 参数类型 | 参数描述 |
|----------------|--------|---------|---------|
| code           | 200    | Integer | 状态码 |
| msg            | success | String  | 响应消息 |
| ts             | 1756021167163 | Long | 时间戳 |
| traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
| data           |        | Object[] | 响应数据列表 |
| ├─id           | 178    | Long    | 账号ID |
| ├─brand        | google | String  | 品牌 |
| ├─model        | Pixel 7 Pro(12G) | String | 型号 |
| ├─fingerprintMd5 | f5da7b97678ac19309f0cf0203e072d7 | String | 安卓md5(ro.build.fingerprint) |
| ├─fingerprint  | google/cheetah/cheetah:13/TQ3A.230901.001/10750268:user/release-keys | String | 安卓ro.build.fingerprint |
| ├─resourceSpecificationCode | m2-3 | String | 规格编号 |
| ├─screenLayoutCode | realdevice_1440x3120x560 | String | 屏幕布局编码 |
| ├─adiTemplateDownloadUrl | https://example.com/file.zip | String | adi模板文件下载路径 |
| ├─adiTemplatePwd | 123456 | String | adi模板文件密码 |
| ├─propertyJson | {"test": "testa"} | JSON | 实例属性 |
| ├─androidImageVersion | 13 | Integer | 安卓镜像版本 |
| ├─deleteFlag  | 0 | Integer | 是否删除（1：已删除；0：未删除） |
| ├─createBy    | admin | String | 创建人 |
| ├─createTime  | 2024-08-28 12:00:00 | Timestamp | 创建时间 |
| ├─updateBy    | admin | String | 修改人 |
| ├─updateTime  | 2024-08-28 12:30:00 | Timestamp | 修改时间 |
| ├─deviceName  | Pixel Pro | String | 机型名称(别名/展示用) |
| ├─isOfficial  | 1 | Integer | 是否正式版（0:测试版 1:正式版） |
| ├─status      | 1 | Integer | 是否启用（0:禁用 1:启用） |
| ├─adiTemplateVersion | v1.0.2 | String | adi模板版本号 |
| ├─modelCode   | cheetah | String | 机型标识 |
| ├─isPublic    | 1 | Integer | 模板使用类型(1=公共 0=私有) |
| ├─aospVersion | 13.0.1 | String | aosp版本 |
| ├─testCasesDownloadUrl | https://example.com/cases.zip | String | 测试用例文件下载路径 |

**请求示例**

```javascript
{
    "pageIndex": 1,
    "pageSize": 10
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756313820061,
        "data": [
        {
            "id": 202,
            "createTime": "2025-03-12T02:29:43.000+00:00",
            "createBy": "",
            "updateTime": "2025-04-29T09:44:28.000+00:00",
            "updateBy": "",
            "brand": "HONOR(FIX)",
            "model": "ELZ-AN10(8G)",
            "fingerprint": "HONOR/ELZ-AN10/HNELZ:14/HONORELZ-AN10/8.0.0.185CHNC00E185R4P6:user/release-keys",
            "fingerprintMd5": "9bf2de4b6aa70466a6f76f66539c4613",
            "resourceSpecificationCode": "m2-4",
            "screenLayoutCode": "realdevice_1344x2772x476",
            "adiTemplateDownloadUrl": "https://oss-hk.armcloud.net/adi/35fdc068d6fdc32a691554989008160b_fix2.zip",
            "adiTemplatePwd": "XMDoxJgoKIZKoWbWlnmY",
            "propertyJSON": "{}",
            "androidImageVersion": 14,
            "deleteFlag": false,
            "deviceName": "ELZ-AN10(8G)",
            "isOfficial": 1,
            "status": 1,
            "adiTemplateVersion": null,
            "modelCode": null,
            "isPublic": 1,
            "testCasesDownloadUrl": null,
            "aospVersion": "android14"
        }
    ],
        "traceId": "ewabantnnwn4"
}
```

#### **获取公共屏幕布局列表**

**接口类型**: 同步接口

获取公共屏幕布局列表

**接口概要**

作用：查询获取公共屏幕布局列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/screenLayout/publicList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756349808017 | Long | 时间戳
traceId | ewbssur1jbwg | String | 链路追踪ID
data |  | Object[] | 响应数据列表
├─id | 12 | Long | 账号ID
├─code | single-portrait-basic | String | 屏幕布局编码
├─screenWidth | 1080 | String | 屏幕宽度
├─screenHigh | 1920 | String | 屏幕高度
├─pixelDensity | 320 | String | 像素密度
├─screenRefreshRate | 60 | String | 屏幕刷新率
├─status | 1 | Integer | 状态（0：停用；1：启用）
├─deleteFlag | 0 | Integer | 是否删除（1：已删除；0：未删除）

**请求示例**

```javascript

```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756349808017,
        "data": [
        {
            "id": 12,
            "code": "single-portrait-basic",
            "screenWidth": "1080",
            "screenHigh": "1920",
            "pixelDensity": "320",
            "screenRefreshRate": "60",
            "status": 1,
            "deleteFlag": 0
        }
    ],
        "traceId": "ewbssur1jbwg"
}

```

#### **批量获取实例机型信息**

**接口类型**: 同步接口

根据实例编号批量获取对应的实例的机型信息。

**接口概要**

作用：查询批量获取实例机型信息。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/pad/modelInfo

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes |  | String[] | 是 |
├─ | AC22030010182 | String | 是 | 实例编号

**响应参数**

参数名 | 示例值 | 参数类型     | 参数描述
--- | -- |----------| ---
code | 200 | Integer  | 状态码
msg | success | String   | 响应消息
traceId | ewbssur1jbwg | String | 链路追踪ID
ts | 1756021167163 | Long     | 时间戳
data |  | Object[] |
├─padCode | AC22030010182 | String   | 实例编号
├─imei | 524803173613682 | String   | IMEI
├─serialno | 01NM5ON34M4O | String   | 序列号
├─wifimac | 04:3a:6c:e5:e9:8d:62:d6:4a | String   | Wi-Fi的mac地址
├─androidid | aa6bcedf1426546c | String   | Android实例唯一标识
├─model | Mi 10 Pro | String   | 型号
├─brand | Xiaomi | String   | 品牌
├─manufacturer | Xiaomi | String   | 厂商
├─isRoot | 1 | String   | 是否是ROOT权限
├─width | 720 | Integer  | 云手机的宽 最大不超过1080
├─height | 1280 | Integer  | 云手机的高 最大不超过1920
├─memoryLimit | 1024 | Integer  | 内存限额
├─bluetoothaddr | 3A:1F:4B:9C:2D:8E | String   | 蓝牙地址
├─phonenum | 1112341234 | String  | 手机号码
├─romVersion | android13 |  String | 安卓版本
├─dataSize | 2367381504 | Integer  | 内存大小(b)
├─dataSizeAvailable | 365830144 | Integer  | 剩余可用(b)
├─dataSizeUsed | 1024 | 2001551360  | 已使用(b)
├─romVersion | android14 | String  | rom版本

**请求示例**

```javascript
{
    "padCodes": [
        "AC22030010182"
    ]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1752845766596,
        "data": [
        {
            "padCode": "ACN250718J6ZLUYS",
            "imei": "237150320344334",
            "serialno": null,
            "wifimac": "44:5a:56:fb:6a:ec",
            "androidid": "ecb978a3cafff13",
            "model": "SM-A057F",
            "brand": "samsung",
            "manufacturer": "samsung",
            "isRoot": null,
            "width": 1080,
            "height": 2400,
            "memoryLimit": null,
            "bluetoothaddr": null,
            "phonenum": null,
            "dataSize": null,
            "dataSizeAvailable": null,
            "dataSizeUsed": null,
            "romVersion": "android14"
        }
    ],
        "traceId": "esb357am18n4"
}
```

#### **添加应用黑名单列表**

**接口类型**: 同步接口

根据实例规格添加应用黑名单。

**接口概要**

作用：修改添加应用黑名单列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/appBlack/setUpBlackList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padGrade | q2-1 | String | 是 | 实例规格
blackApps |  | Object[] | 是 | 黑名单列表
├─appPkg | cn.v8box.app | String | 是 | 应用包名
├─appName | x8沙箱 | String | 是 | 应用名称

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1721647657112 | Long | 时间戳
data | “” | String |

**请求示例**

```javascript
{
 "padGrade": "q2-1",
 "blackApps": [
  {
   "appPkg": "cn.v8box.app",
   "appName": "x8沙箱"
  }
 ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1721647657112,
 "data": null
}
```

#### **设置实例黑名单**

**接口类型**: 异步接口
**关联回调**: [实例黑名单任务回调](#实例黑名单任务回调) (taskBusinessType: `-`)

根据实例规格设置实例黑名单。

**接口概要**

作用：修改设置实例黑名单。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/triggeringBlacklist

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padGrade | q2-1 | String | 是 | 实例规格
padCodes |  | String[] | 否 |
├─ | AC22030010124 | String | 否 | 实例编号

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1721739857317 | Long | 时间戳
data |  | Object[] |
├─taskId | 12818 | Integer | 任务ID
├─padCode | AC22030010124 | String | 实例编号
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)

**请求示例**

```javascript
{
 "padGrade": "q2-4",
 "padCodes": [
  "AC22030010124"
 ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1721739857317,
 "data": [
  {
   "taskId": 12818,
   "padCode": "AC22030010124",
   "vmStatus": 1
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110051 | 该规格不存在应用黑名单配置| 需添加规格应用黑名单列表
110028 | 实例不存在| 传参有误
110052 | 执行设置应用黑名单指令失败| 请重试

#### **设置实例带宽**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

根据实例编号设置实例带宽。

**接口概要**

作用：修改设置实例带宽。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/setSpeed

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes |  | String[] | 是 |
├─ | AC22030010124 | String | 是 | 实例编号
upBandwidth | 10.00 | float | 是 | 上行带宽 Mbps (0：不限制；-1：限制上网)
downBandwidth | 10.00 | float | 是 | 下行带宽 Mbps (0：不限制；-1：限制上网)

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1721739857317 | Long | 时间戳
traceId | ewbssur1jbwg | String | 链路追踪ID
data |  | Object[] |
├─taskId | 679 | Integer | 任务ID
├─padCode | AC32010140011 | String | 实例编号
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "padCodes": [
  "AC32010140011"
 ],
 "upBandwidth": 10.00,
 "downBandwidth": 10.00
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "traceId": "ewab8qjqbaio",
 "ts": 1721640654237,
 "data": [
  {
   "taskId": 679,
   "padCode": "AC32010140011",
   "vmStatus": 1,
   "taskStatus": 1
  }
 ]
}
```

#### **开启关闭ADB**

**接口类型**: 同步接口

根据实例编号打开或关闭实例adb

**接口概要**

作用：操作开启关闭ADB。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/openOnlineAdb

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | -- | ---
padCodes |  | String[] | 是 | 实例列表(传入实例数量1-200个) |
├─ | AC32010250032 | String | 是 | 实例编号|
openStatus | 1 | Integer | 是 | 开启关闭ADB状态。可选值：`0`或不传关闭(默认)/`1`开启。[详见枚举↗](./EnumReference.md#112-openstatus---开启关闭adb状态)

**响应参数**

参数名 | 示例值           | 参数类型 | 参数描述
--- |---------------| --- | ---
code | 200           | Integer | 状态码
msg | success       | String | 响应消息
ts | 1721739857317 | Long | 时间戳
data |               | Object[] |
├─taskId | 16147 | Integer | 任务id
├─padCode | AC32010250032 | String | 实例编号
├─taskStatus | 3             | Integer | 任务状态（-1全失败，-2部分失败，-3取消，-4超时，-5异常，1，等待执行，2执行中，3完成）
├─taskResult | success       | String | 任务结果

**请求示例**

```javascript
{
    "padCodes":[
        "AC32010250032"
    ],
    "openStatus": 1
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1736920929306,
    "data": [
        {
        "taskId": 16147,
        "padCode": "AC32010250032",
        "taskStatus": 3,
        "taskResult": "success"
        }
    ]
}
```

#### **获取ADB连接信息**

**接口类型**: 同步接口

根据实例编号获取adb连接信息
响应数据(key,adb)不全情况时，请调用[开启关闭ADB](#pad_openOnlineAdb)开启adb。

**接口概要**

作用：查询获取ADB连接信息。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/pad/adb

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | -- | ---
padCode | AC32010250032 | String | 是 | 实例编号 |
enable | true | Boolean | 是 | ADB状态。`true`开启/`false`关闭 |

**响应参数**

参数名 | 示例值           | 参数类型 | 参数描述
--- |---------------| --- | --
code | 200           | Integer | 状态码
msg | success       | String | 响应消息
traceId | ewbssur1jbwg | String | 链路追踪ID
ts | 1736922808949 | Long | 时间戳
data |               | Object[] |
├─padCode | AC32010250032 | String | 实例编号
├─command | ssh -oHostKeyAlgorithms=+ssh-rsa 10.255.3.2_001_1736922765389@156.59.80.166 -p 1824 -L 8572:adb-proxy:53728 -Nf | String | SSH 连接指令
├─expireTime | 2025-01-16 14:32:00 | String | adb 链接有效期
├─enable | true | Boolean  | ADB状态。`true`开启/`false`关闭
├─key | 3CXr3FJZ6gbnGuJctDOpP9M6X6Rl786xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx== | String | 连接密钥
├─adb | adb connect localhost:8577            | String | adb连接信息

**请求示例**

```javascript
{
    "padCode": "AC32010250032",
    "enable": true
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "traceId": "ewab8qjqbaio",
    "ts": 1736922808949,
    "data": {
        "padCode": "AC32010250032",
        "command": "ssh -oHostKeyAlgorithms=+ssh-rsa 10.255.3.2_001_1736922765389@156.59.80.166 -p 1824 -L 8572:adb-proxy:53728 -Nf",
        "expireTime": "2025-01-16 14:32:00",
        "enable": true,
        "key": "3CXr3FJZ6gbnGuJctDOpP9M6X6Rl786xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==",
        "adb": "adb connect localhost:8577"
    }
}
```

#### **批量获取ADB连接信息**

**接口类型**: 同步接口

根据实例编号列表批量获取或关闭adb连接信息。执行开启操作时若成功返回的连接信息不全，请先调用[开启关闭ADB](#pad_openOnlineAdb)接口重新开启ADB后再重试。本接口单次最多支持10个实例。

**接口概要**

作用：查询批量获取ADB连接信息。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/pad/batch/adb

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | -- | ---
padCodes | ["AC32010250032","AC32010250033"] | String[] | 是 | 实例编号列表，数量上限10个
enable | true | Boolean | 是 | 是否开启ADB。可选值：`true`开启并返回连接信息/`false`关闭ADB。[详见枚举↗](./EnumReference.md#41-enable---启用状态)

**响应参数**

参数名 | 示例值           | 参数类型 | 参数描述
--- |---------------| --- | --
code | 200           | Integer | 状态码
msg | success       | String | 响应消息
traceId | ewbssur1jbwg | String | 链路追踪ID
ts | 1736922808949 | Long | 时间戳
data |               | Object |
├─successList |               | Object[] | 批量执行成功的结果列表
│ ├─padCode | AC32010250032 | String | 实例编号
│ ├─command | ssh -oHostKeyAlgorithms=+ssh-rsa 10.255.3.2_001_1736922765389@156.59.80.166 -p 1824 -L 8572:adb-proxy:53728 -Nf | String | SSH连接指令
│ ├─expireTime | 2025-01-16 14:32:00 | String | adb链接有效期
│ ├─enable | true | Boolean | ADB状态 true:开启 false:关闭
│ ├─key | 3CXr3FJZ6gbnGuJctDOpP9M6X6Rl786xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx== | String | 连接密钥
│ ├─adb | adb connect localhost:8577 | String | adb连接信息
├─failedList |               | Object[] | 批量执行失败的结果列表
│ ├─padCode | AC32010250034 | String | 实例编号
│ ├─errorMsg | 实例未运行 | String | 失败原因
│ ├─errorCode | PAD_NOT_RUNNING | String | 错误码

**请求示例**

```javascript
{
    "padCodes": [
        "AC32010250032",
        "AC32010250033"
    ],
    "enable": true
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "traceId": "ewbssur1jbwg",
    "ts": 1736922808949,
    "data": {
        "successList": [
            {
                "padCode": "AC32010250032",
                "command": "ssh -oHostKeyAlgorithms=+ssh-rsa 10.255.3.2_001_1736922765389@156.59.80.166 -p 1824 -L 8572:adb-proxy:53728 -Nf",
                "expireTime": "2025-01-16 14:32:00",
                "enable": true,
                "key": "3CXr3FJZ6gbnGuJctDOpP9M6X6Rl786xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==",
                "adb": "adb connect localhost:8577"
            }
        ],
        "failedList": [
            {
                "padCode": "AC32010250034",
                "errorMsg": "实例未运行",
                "errorCode": "PAD_NOT_RUNNING"
            }
        ]
    }
}
```

#### **模拟触控**

**接口类型**: 异步接口
**关联回调**: 通过返回的 `taskId` 轮询[实例操作任务详情](#实例操作任务详情)接口查询任务状态，建议查询间隔至少30秒

通过传入xy坐标，模拟在实例中的触控事件（按下、抬起、触摸中）

**接口概要**

作用：执行模拟触控。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

> 异常检查：如果2s内有重复请求，报错提示内容：请勿频繁操作

**接口地址**

> /openapi/open/pad/simulateTouch

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名        | 示例值                                                          | 参数类型     | 参数描述                                                  |
|-----------|--------------------------------------------------------------|----------|-------------------------------------------------------|
| padCodes  | 2200                                                         | String[] | 需要触发点击的实例编码                                           |
| width     | 120                                                          | Integer  | 容器宽度                                                  |
| height    | 120                                                          | Integer  | 容器高度                                                  |
| pointCount    | 1                                                            | Integer  | 多点触控(多个手指点击云机屏幕效果)，默认1，范围1-10，传其他数字均使用默认值                         |
| positions | [{"actionType":0,"x":100,"y":100,"nextPositionWaitTime":20}] | Object[] | 点击坐标组                                                 |
| ├─ actionType | 1                                                            | Integer  | 操作类型。可选值：`0`按下/`1`抬起/`2`触摸中 |
| ├─ x         | 100                                                          | float    | 点击的x坐标                                                |
| ├─ y         | 100                                                          | float    | 点击的y坐标                                                |
| ├─ nextPositionWaitTime          | 100                                                          | Integer  | 多组坐标时，触发下一组点击坐标的等待间隔时间ms毫秒值                           |
| ├─ swipe          | -1                                                           | float    | 滚动距离  -1 下划  1 上划                                     |
| ├─ touchType          | gestureSwipe                                                 | String   | 触控类型。可选值：`gestureSwipe`划动事件/`gesture`触控事件/`keystroke`按键事件(默认是按下抬起) |
| ├─ keyCode          | 1                                                            | Integer  | 用于标识用户按下或释放的具体按键                        |
| ├─ pressure          | 0.5                                                          | float   | 触点压力
| ├─ size          | 0.5                                                          | float  | 触点占屏幕面积比例            |

**响应参数**

参数名 | 示例值     | 参数类型 | 参数描述
--- |---------| --- | --
code | 200     | Integer | 状态码
msg | success | String | 响应消息
ts | 1736922808949 | Long | 时间戳
traceId | ewbssur1jbwg | String | 链路追踪ID
data |         | Object[] |
├─padCode | AC32032 | String | 实例编号
├─taskId | 10004759 | Long |任务id
├─vmStatus | 0       | String | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
  "padCodes": [
    "实例编号"
  ],
  "width": 1080,
  "height": 1920,
  "pointCount":1,
  "positions": [
    {
      "actionType": 0,
      "x": 100,
      "y": 100,
      "nextPositionWaitTime": 20,
      "swipe":-1,
      "touchType":"gestureSwipe",
      "keyCode":1,
        "pressure":0.5,
        "size":0.5
    },
    {
      "actionType": 2,
      "x": 110,
      "y": 110,
      "nextPositionWaitTime": 22
    },
    {
      "actionType": 2,
      "x": 120,
      "y": 120,
      "nextPositionWaitTime": 23
    },
    {
      "actionType": 1,
      "x": 120,
      "y": 120
    }
  ]
}
```

**响应示例**

```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1743676563784,
  "traceId": "ewab8qjqbaio",
    "data": [
    {
      "taskId": 100059,
      "padCode": "ACP00001",
      "vmStatus": 0,
      "taskStatus": 1

    },
    {
      "taskId": 100060,
      "padCode": "ACP00001",
      "vmStatus": 0,
      "taskStatus": 1

    }
  ]
}
```

#### **实例操作任务详情**

**接口类型**: 同步接口

查询指定实例操作任务的执行结果详细信息。

**接口概要**

作用：查询实例操作任务详情。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /task-center/open/task/padTaskDetail

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Query参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
taskIds |  | Integer[] | 是 |
├─taskId | 1 | Integer | 是 |任务ID

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
traceId | ewbssur1jbwg | String | 链路追踪ID
data |  | Object [] | 子任务列表详情
├─ taskId | 1 | Integer | 子任务ID
├─ padCode | VP22020020793 | String | 实例标识
├─ taskStatus | 2 | String TODO类型使用错误  | 任务状态（-1：全失败；-2：部分失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成；9：排队中）
├─ endTime | 1713429401000 | Long | 子任务结束时间戳
├─ taskContent | “” | String | 任务内容
├─ taskResult | “” | String | 任务结果
├─ errorMsg | “” | String | 错误信息

**请求示例**

```javascript
{
 "taskIds":[1,2]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756313781081,
        "data": [
        {
            "taskId": 22323794,
            "padCode": "ACN250828DYJE95Z",
            "taskStatus": 2,
            "endTime": null,
            "taskContent": null,
            "taskResult": null,
            "errorMsg": null
        }
    ],
        "traceId": "ewab8kpxb7k0"
}
```

#### **获取实例执行脚本结果**

**接口类型**: 同步接口

通过执行脚本任务ID来获取实例执行脚本结果。

**接口概要**

作用：执行获取实例执行脚本结果。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /task-center/open/task/executeScriptInfo

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
taskIds |  | Integer [] | 是 | 数组长度为1-100
├─ | 1 | Integer | 否 | 任务ID

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
ts | 1756021167163 | Long |  时间戳
data |  | Object[] |
├─taskId | 1 | Integer |  任务ID
├─padCode | AC22020020793 | String |  实例编号
├─taskStatus | 3| Integer |  任务状态（-1：全失败；-2：部分失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）
├─endTime | 1756021166163 | Long |  任务执行结束时间
├─taskContent | Success | String |  任务内容
├─taskResult | Success | String |  任务结果
├─errorMsg |实例不存在 |String |  失败的原因|

**请求示例**

```javascript
{
 "taskIds": [1]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1752214432301,
        "data": [
        {
            "taskId": 49884,
            "padCode": "ATP250707FNSVRMC",
            "taskStatus": 3,
            "endTime": 1752214271000,
            "taskContent": null,
            "taskResult": null,
            "errorMsg": "调用Adb命令成功"
        }
    ],
        "traceId": "erl0i57h6v40"
}
```

#### **获取实例截图结果**

**接口类型**: 同步接口

通过截图任务 ID 来获取实例的截图结果。

**接口概要**

作用：执行获取实例截图结果。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口URL**

> /task-center/open/task/screenshotInfo

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
taskIds |  | Integer [] | 是 |
├─ | 1 | Integer | 否 | 任务ID

**响应参数**

| 参数名     | 示例值              | 参数类型  | 参数描述                                                                 |
|---------| ------------------- | --------- | ------------------------------------------------------------------------ |
| code    | 200                 | Integer   | 状态码                                                                  |
| msg     | success             | String    | 响应消息                                                                |
| traceId | ewbssur1jbwg | String | 链路追踪ID
| ts      | 1756021167163       | Long      | 时间戳
| data    | -                   | Object[]  | 任务列表详情                                                                |
|├─ taskId | 1 | Integer | 任务ID |
|├─ taskStatus | 3 | Integer | 任务状态（-1：全失败；-2：部分失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）|
|├─ padCode | AC22020020793 | String |  实例编号 |
|├─ taskContent | Success   | String |  任务内容 |
|├─ taskResult | Success   | String |  任务结果 |
|├─ endTime | 1756121167163 | String |  任务执行结束时间 |

**请求示例**

```json
{
 "taskIds": [1]
}
```

**响应示例**

```json
{
 "code": 200,
 "msg": "success",
  "traceId": "ewab8qjqbaio",
  "ts":1713773577581,
 "data":[
    {
    "taskId": 1,
    "taskStatus": 3,
    "padCode": "AC22020020793",
    "taskContent": "Success",
    "taskResult": "Success",
    "endTime": 1756121167163
    }
   ]
}
```

#### **实例重启重置执行结果**

**接口类型**: 同步接口

通过任务ID来获取实例重启重置执行结果。

**接口概要**

作用：执行实例重启重置执行结果。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /task-center/open/task/padExecuteTaskInfo

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

|参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述|
|--- | --- | --- | --- | --- |
|taskIds |  | Integer [] | 是 | |
|├─ | 1 | Integer | 是 | 任务ID |

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述|
|--- | --- | --- | --- |
|code | 200 | Integer |  状态码 |
|msg | success | String |  响应消息 |
| traceId | ewbssur1jbwg | String | 链路追踪ID
|ts | 1756021167163 | Long |  时间戳 |
|data |  | Object[] |  |
|├─taskId | 1 | Integer |  任务ID |
|├─padCode | AC21020010001 | String | 实例编号 |
|├─taskStatus | 3| Integer |  任务状态：（-1：全失败；-2：部分失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
|├─ endTime | 1756021166163 | Long |  任务执行结束时间 |
|├─ taskContent | “” | String |  任务内容 |
|├─ taskResult | Success | String |  任务结果 |

**请求示例**

```javascript
{
    "taskIds": [1]
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "traceId": "ewab8qjqbaio",
    "ts": 1756021167163
    "data":[
        {
            "taskId": 1,
            "padCode": "AC22030022911",
            "taskStatus": 3,
            "endTime": 1756021166163,
            "taskContent": null,
            "taskResult": "Success"
        }
    ]
}
```

#### **实例列表信息**

**接口类型**: 同步接口

根据查询条件分页获取实例列表信息。

**接口概要**

作用：查询实例列表信息。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/pad/infos

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值       | 参数类型      | 是否必填 | 参数描述
--- |-----------|-----------|------| ---
page | 1         | Integer   | 是    | 页码
rows | 10        | Integer   | 是    | 条数
filterSubCustomerFlag | 1         | Integer   | 否    | 子账户筛选标记。可选值：`-1`仅查询子账号/`0`同时查询主/子账户(默认)/`1`仅查询主账号。[详见枚举↗](./EnumReference.md#35-filtersubcustomerflag---子账户筛选标记)
armServerCode | ACS32010260000 | Integer   | 否    | 服务器编号
deviceCode | AC32010250020 | String    | 否    | 板卡编号
netStorageResFlag | 1         | Integer   | 否    | 网存标记。可选值：`0`本地实例/`1`网存实例/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记)
padStatus | 10        | Integer   | 否    | 实例状态。[查看所有26个状态码↗](./EnumReference.md#11-padstatus---实例状态)
padType | real      | String    | 否    | 实例类型。可选值：`virtual`虚拟机/`real`云真机。[详见枚举↗](./EnumReference.md#22-padtype---实例类型)
idc | 1         | String    | 否    | 机房Id
padCodes |           | String[]  | 否    |
├─ | AC22010020062 | String    | 否    | 实例编号
groupIds |           | Integer[] | 否    |
├─ | 1         | Integer   | 否    | 实例分组ID
orderBy | CreateTime_DESC | String    | 否    | 排序字段, 列举情况：CreateTime_DESC: 创建时间倒序；其他任何值: 创建时间正序

**响应参数**

| 参数名             | 示例值                 | 参数类型 | 参数描述                                          |
|-----------------|---------------------| --- |-----------------------------------------------|
| code            | 200                 | Integer |                                               |
| msg             | success             | String |                                             |
| ts              | 1713773577581       | Long |                                               |
| data            |                     | Object |                                               |
| ├─page          | 1                   | Integer | 当前页                                           |
| ├─rows          | 10                  | Integer | 每页的数量                                         |
| ├─size          | 1                   | Integer | 当前页的数量                                        |
| ├─total         | 1                   | Integer | 总记录数                                          |
| ├─totalPage     | 1                   | Integer | 总页数                                           |
| ├─pageData      |                     | object[] | 列表                                            |
| ├─├─padCode     | VP21020010391       | String | 实例编号                                          |
| ├─├─padGrade    | q1-2                | String | 实例开数（q1-6六开，q1-2二开）                           |
| ├─├─padStatus   | 10                  | String | 实例状态 （10-运行中 11-重启中 12-重置中 13-升级中 14-异常 15-未就绪） |
| ├─├─groupId     | 0                   | Integer | 分组ID                                          |
| ├─├─idc         | 1                   | String | 机房id                                          ||
| ├─├─deviceIp    | 192.168.0.0         | String | 云机ip                                          |
| ├─├─padIp       | 192.168.0.0         | String | 实例ip                                          |
| ├─├─customerAccount    | star@test      | String | 该实例所属账户                                          |
| ├─├─armServerCode | ACS32010160000      | String | 服务器编号                                         |
| ├─├─padType | real                | String | 实例类型。可选值：`virtual`虚拟机/`real`云真机。[详见枚举↗](./EnumReference.md#22-padtype---实例类型) |
| ├─├─deviceCode  | AC32010150070       | String | 板卡编号                                          |
| ├─├─createTime  | 2025-09-15 14:11:21 | String | 实例创建时间                                        |
| ├─├─imageVersion  | android14           | String | 安卓版本                                          |
| ├─├─apps        |                     | String[] | 安装的应用列表                                       |
| ├─├─├─          | armcloud001         | String | 安装的应用                                         |

**请求示例**

```javascript
{
        "page": 1,
        "rows": 10,
        "filterSubCustomerFlag": 0,
        "padCodes": [
        "AC21020010391"
    ],
        "armServerCode": "ACS32010260000",
        "deviceCode": "AC32010250020",
        "groupIds": [
        1
    ]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1737625119669,
        "data": {
        "page": 1,
            "rows": 10,
            "size": 3,
            "total": 3,
            "totalPage": 1,
            "pageData": [
            {
                "padCode": "AC32010250021",
                "padGrade": "m2-3",
                "padStatus": 12,
                "groupId": 3,
                "idcCode": "1",
                "deviceIp": "172.31.3.3",
                "padIp": "10.255.3.5",
                "customerAccount": "star@test",
                "padType": "real",
                "adbOpenStatus": "0",
                "armServerCode": "ACS32010260000",
                "deviceCode": "AC32010250020",
                "apps": null,
                "imageId": "img-25012330968",
                "createTime": "2025-09-15 14:11:21",
                "imageVersion": "android14"
            }
            // ... 更多实例对象
        ]
    }
}
```

#### **实例列表信息（优化分页版本）**

**接口类型**: 同步接口

根据查询条件获取实例列表信息，使用 lastId + rows 方式进行分页。

**接口概要**

作用：查询实例列表信息（优化分页版本）。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/pad/infos/new

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes |  | String[] | 否 | 实例编号
├─ | AC22010020062 | String | 否 | 实例编号
deviceSubnet | 192.168.0.0/24 | String | 否 | 物理机子网
armServerCode | ACS32010260000 | String | 否 | 服务器编号
clusterCode | cluster-001 | String | 否 | 集群编号
idc | 1 | String | 否 | 机房Id
padType | real | String | 否 | 实例类型（virtual：虚拟机；real：真机）
deviceCode | AC32010250020 | String | 否 | 板卡编号
groupIds |  | Integer[] | 否 | 实例分组ID
├─ | 1 | Integer | 否 | 实例分组ID
lastId | 0 | Long | 否 | 上次查询的最后一条记录ID，首次查询传null或0
rows | 10 | Integer | 是 | 查询数量，范围1-1000，默认10
netStorageResFlag | 1 | Integer | 否 | 网存集群标记。可选值：`0`本地集群/`1`网存集群/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记)

**响应参数**

| 参数名             | 示例值                 | 参数类型 | 参数描述                                          |
|-----------------|---------------------| --- |-----------------------------------------------|
| code            | 200                 | Integer |                                               |
| msg             | success             | String |                                             |
| ts              | 1713773577581       | Long |                                               |
| data            |                     | Object |                                               |
| ├─rows          | 10                  | Integer | 每页的数量                                         |
| ├─size          | 3                   | Integer | 当前页的数量                                        |
| ├─lastId        | 123                 | Long | 最后一条记录ID，用于下次分页查询                            |
| ├─hasNext       | true                | Boolean | 是否还有下一页                                       |
| ├─pageData      |                     | object[] | 列表                                            |
| ├─├─padCode     | VP21020010391       | String | 实例编号                                          |
| ├─├─padGrade    | q1-2                | String | 实例开数（q1-6六开，q1-2二开）                           |
| ├─├─padStatus   | 10                  | String | 实例状态 （10-运行中 11-重启中 12-重置中 13-升级中 14-异常 15-未就绪） |
| ├─├─groupId     | 0                   | Integer | 分组ID                                          |
| ├─├─idc         | 1                   | String | 机房id                                          ||
| ├─├─deviceIp    | 192.168.0.0         | String | 云机ip                                          |
| ├─├─padIp       | 192.168.0.0         | String | 实例ip                                          |
| ├─├─customerAccount    | star@test      | String | 该实例所属账户                                          |
| ├─├─armServerCode | ACS32010160000      | String | 服务器编号                                         |
| ├─├─padType | real                | String | 实例类型。可选值：`virtual`虚拟机/`real`云真机。[详见枚举↗](./EnumReference.md#22-padtype---实例类型) |
| ├─├─deviceCode  | AC32010150070       | String | 板卡编号                                          |
| ├─├─createTime  | 2025-09-15 14:11:21 | String | 实例创建时间                                        |
| ├─├─imageVersion  | android14           | String | 安卓版本                                          |
| ├─├─apps        |                     | String[] | 安装的应用列表                                       |
| ├─├─├─          | armcloud001         | String | 安装的应用                                         |

**请求示例**

```javascript
{
    "lastId": 0,
    "rows": 10,
    "padCodes": [
        "AC21020010391"
    ],
    "armServerCode": "ACS32010260000",
    "deviceCode": "AC32010250020",
    "groupIds": [
        1
    ],
    "netStorageResFlag": 1
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1737625119669,
    "data": {
        "rows": 10,
        "size": 3,
        "lastId": 123,
        "hasNext": true,
        "pageData": [
            {
                "padCode": "AC32010250021",
                "padGrade": "m2-3",
                "padStatus": 12,
                "groupId": 3,
                "idcCode": "1",
                "deviceIp": "172.31.3.3",
                "padIp": "10.255.3.5",
                "customerAccount": "star@test",
                "padType": "real",
                "adbOpenStatus": "0",
                "armServerCode": "ACS32010260000",
                "deviceCode": "AC32010250020",
                "apps": null,
                "imageId": "img-25012330968",
                "createTime": "2025-09-15 14:11:21",
                "imageVersion": "android14"
            }
            // ... 更多实例对象
        ]
    }
}
```

#### **实例分组列表**

**接口类型**: 同步接口

获取用户当前所有实例分组列表信息（包括：分组 ID,分组名称，分组下实例数量）。
**接口地址**

**接口概要**

作用：查询实例分组列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

> /openapi/open/group/infos

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCode | AC21020010391 | String | 否 | 实例编号
groupIds |  | Integer[] | 否 |
├─ | 1 | Integer | 否 | 分组ID

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
data |  | Object[] |
├─groupId | 1 | Integer | 分组ID
├─groupName | 分组一 | String | 分组名称
├─padCount | 1 | Integer | 分组下的实例数

**请求示例**

```javascript
{
 "padCode": "AC21020010391",
 "groupIds": [1]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
 "data": [
   {
    "groupId": 1,
    "groupName": "分组一",
    "padCount": 1
   }
 ]
}
```

#### **导入通话记录**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `1205`)

此接口允许将通话记录数据导入至云手机中。接口在导入过程中，会自动检测云手机通讯录中已保存的联系人，并将这些联系人对应的名称显示在通话记录中，便于用户快速识别联系人。

**接口概要**

作用：创建导入通话记录。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/addPhoneRecord

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名           | 示例值                                                                                       | 参数类型     | 是否必填 | 参数描述                 |
|---------------|-------------------------------------------------------------------------------------------|----------|------|----------------------|
| padCodes      | ACP2505060777                                                                             | String[] | 是    | 需要编辑通话记录的实例编码        |
| callRecords   | [{"number":"18009781201","inputType":1,"duration":30,"timeString":"2025-05-06 14:00:09"}] | Object[] | 是    | 通话记录                 |
| ├─ number     | 13900000000                                                                               | String   | 是    | 电话号码                 |
| ├─ inputType  | 1                                                                                         | int      | 是    | 通话类型。可选值：`1`拨出/`2`接听/`3`未接 |
| ├─ duration   | 60                                                                                        | int      | 是    | 通话时长;单位是秒,未接电话是0秒    |
| ├─ timeString | 2025-05-08 12:30:00                                                                       | String   | 否    | 通话时长                 |

**响应参数**

参数名 | 示例值     | 参数类型 | 参数描述
--- |---------| --- | --
code | 200     | Integer | 状态码
msg | success | String | 响应消息
ts | 1736922808949 | Long | 时间戳
data |         | Object[] |
├─padCode | AC32032 | String | 实例编号
├─taskId | 10004759 | Long |任务id
├─vmStatus | 0       | String | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)

**请求示例**

```javascript
{
  "padCodes": [
     "实例编号"
  ],
  "callRecords": [
    {
      "number": "18009781201",
      "inputType": 1,
      "duration": 30,
      "timeString": "2025-05-06 14:00:09"
    },
    {
      "number": "18009781202",
      "inputType": 2,
      "duration": 60,
      "timeString": "2025-05-07 14:00:09"
    },
    {
      "number": "18009781203",
      "inputType": 3,
      "duration": 0
    }
  ]
}
```

**响应示例**

```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1743676563784,
  "data": [
    {
      "taskId": 100059,
      "padCode": "ACP00001",
      "vmStatus": 0
    },
    {
      "taskId": 100060,
      "padCode": "ACP00001",
      "vmStatus": 0
    }
  ]
}
```

#### **云机文本信息输入**

在云机中预先聚焦好输入框，调用该接口传入指定的文本信息内容后，文本展示在云机指定位置。

**接口地址**

> /openapi/open/pad/inputText

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名           | 示例值           | 参数类型     | 是否必填 | 参数描述          |
|---------------|---------------|----------|------|---------------|
| padCodes      | ACP2505060777 | String[] | 是    | 实例编码 |
| text   | hello123      | String | 是    | 输入文本          |
**响应参数**

参数名 | 示例值           | 参数类型 | 参数描述
--- |---------------| --- | --
code | 200           | Integer | 状态码
msg | success       | String | 响应消息
ts | 1736922808949 | Long | 时间戳
data |               | Object[] |
├─padCode | AC32032       | String | 实例编号
├─taskId | 10004759      | Long |任务id
├─vmStatus | 0             | String | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1             | String | 任务当前状态

**请求示例**

```javascript
{
   "padCodes": [
      "ACP250509FECQN33",
      "ACP250509T1VME44",
      "ACP25050917AYX11"
   ],
   "text": "12345678"
}
```

**响应示例**

```javascript
{
     "msg": "success",
     "code": 200,
     "data": [
      {
         "padCode": "ACP250509FECQN33",
         "vmStatus": 0,
         "taskId": 10013014,
         "taskStatus": 1
      },
      {
         "padCode": "ACP250509T1VME44",
         "vmStatus": 0,
         "taskId": 10013015,
         "taskStatus": 1
      },
      {
         "padCode": "ACP25050917AYX11",
         "vmStatus": 0,
         "taskId": 10013016,
         "taskStatus": 1
      }
   ],
   "ts": 1746797852244
}
```

**接口概要**

作用：处理云机文本信息输入。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **模拟发送短信**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `1203`)

向实例内模拟下发一条短信，支持批量实例。（暂时限定AOSP13、14）

**接口概要**

作用：执行模拟发送短信。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/pad/simulateSendSms

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名      | 示例值                          | 参数类型     | 是否必填 | 参数描述                 |
|-----------|------------------------------|----------|------|----------------------|
| padCodes  | ["ACN2505060777"]            | String[] | 是   | 实例编码列表，数量1-100个 |
| senderNumber | 13800000000                 | String   | 是   | 发送方号码，不支持大陆号码。（格式：长度限制16位，允许数字、英文、空格、+-号）|
| smsContent | 这是一条测试短信。 | String   | 是   | 短信内容（长度限制127位）                 |

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1736922808949 | Long | 时间戳
traceId | ewb123abc | String | 追踪ID
data | true | Boolean | 是否调用成功

**请求示例**

```javascript
{
  "padCodes": ["ACN2505060777"],
  "senderNumber": "13800000000",
  "smsContent": "这是一条测试短信。"
}
```

**响应示例**

```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1736922808949,
  "traceId": "ewb123abc",
  "data": true
}
```

#### **重置GAID**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

调用该接口传入指定实例编号或者实例分组，将重置云机中的 advertising ID（Reset advertising ID）

**接口概要**

作用：操作重置GAID。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/resetGAID

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名   | 示例值           | 参数类型      | 是否必填 | 参数描述             |
| -------- |---------------|-----------|------|------------------|
| padCodes |               | String[]  | 是    |                  |
| ├─       | AC21020010001 | String    | 是    | 实例编号             |
| groupIds |               | Integer[] | 否    |                  |
| ├─       | 1             | Integer   | 否    | 实例组ID            |
| resetGmsType | GAID          | String    | 是    | 重置GMS类型。可选值：`GAID`重置GAID |
| oprBy | zhangsan      | String    | 否    | 操作人              |
| taskSource | OPEN_PLATFORM      | String    | 是    | 任务来源，可选：OPEN_PLATFORM         |

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述|
|--- | --- | --- | --- |
|code | 200 | Integer | 状态码 |
|msg | success | String | 响应消息 |
|ts | 1756021167163 | Long | 时间戳 |
|data |  | Object[] | |
|├─taskId | 1 | Integer |  任务ID|
|├─padCode | AC21020010001 | String | 实例编号 |
|├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |

**请求示例**

```javascript
{
   "padCodes": [
      "ACPXXXXXXXXXXXXXXX"
   ],
  "taskSource": "OPEN_PLATFORM",
  "oprBy": "admin",
  "resetGmsType": "GAID"
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1717559681604,
    "data": [
         {
            "taskId": 88,
            "padCode": "AC22030010001",
            "vmStatus": 1
         },
         {
            "taskId": 89,
            "padCode": "AC22030010002",
            "vmStatus": 0
         }
      ]
}
```

#### **注入音频到实例麦克风**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

将一个音频文件注入到实例的麦克风，代替麦克风收音的接口
备注：目前仅支持注入pcm格式的音频文件，请处理转好格式后再进行上传

**接口概要**

作用：执行注入音频到实例麦克风。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/injectAudioToMic

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名           | 示例值                              | 参数类型     | 是否必填 | 参数描述                    |
|---------------|----------------------------------|----------|------|-------------------------|
| padCodes      | ACP2505060777                    | String[] | 是    | 实例编码                    |
| url   | http://localhost/abc             | String   | 否    | 音频文件下载地址 （此字段和fileUniqueId 2选1传值）|
| fileUniqueId  | 8fc73d05371740008ea27a2707496a82 | String   | 否    | 文件id唯一标识（此字段和url 2选1传值） |
| enable        | true                             | Boolean        | 是    | 注入开关                    |
**响应参数**

参数名 | 示例值           | 参数类型 | 参数描述
--- |---------------| --- | --
code | 200           | Integer | 状态码
msg | success       | String | 响应消息
ts | 1736922808949 | Long | 时间戳
data |               | Object[] |
├─padCode | AC32032       | String | 实例编号
├─taskId | 10004759      | Long |任务id
├─vmStatus | 0             | String | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1             | String | 任务当前状态

**请求示例**

```javascript
{
  "padCodes": [
    "ACP250509FECQN33","ACP250509T1VME44","ACP25050917AYX11
  ],
  "url":"http://localhost/abc ",
  "fileUniqueId":"8a6d0df189ef4b0e83858fd9eeb7620c",
  "enable":true
}
```

**响应示例**

```javascript
{
     "msg": "success",
     "code": 200,
     "data": [
      {
         "padCode": "ACP250509FECQN33",
         "vmStatus": 0,
         "taskId": 10013014,
         "taskStatus": 1
      },
      {
         "padCode": "ACP250509T1VME44",
         "vmStatus": 0,
         "taskId": 10013015,
         "taskStatus": 1
      },
      {
         "padCode": "ACP25050917AYX11",
         "vmStatus": 0,
         "taskId": 10013016,
         "taskStatus": 1
      }
   ],
   "ts": 1746797852244
}
```

#### **创建本地实例备份**

**接口类型**: 异步接口
**关联回调**: 通过返回的 `taskId` 轮询[本地实例备份结果查询](#本地实例备份结果查询)接口查询任务状态，建议查询间隔至少30秒

用于创建本地实例备份接口。

**接口概要**

作用：修改创建本地实例备份。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> `/openapi/open/pad/local/pod/backup`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名      | 示例值                          | 参数类型 | 是否必填                | 参数描述                                            |
|----------|------------------------------|------|---------------------|-------------------------------------------------|
| padCode  | PAD_001                      | String | 是                   | 实例编号，不能为空，最大64字符                                |
| backupName | backnameinfo                 | String | 否                   | 备份名称，最大128字符                                    |
| backupPath | backup/db                    | String | 否                   | 不要/开头，备份数据保存路径，不传则默认保存在根目录 `/{备份ID}/` 下，最大256字符 |
| ossConfig | {...}                        | Object | 否                   | 对象存储配置，需要支持 S3 协议，不能为空且永久授权                     |
| ├─ endpoint | oss-cn-shanghai.aliyuncs.com | String | ossConfig != null-是 | 对象存储 endpoint，最大128字符                           |
| ├─ bucket | pad-backup                   | String | ossConfig != null-是 | 对象存储 bucket 名称，最大128字符                          |
| ├─ accessKey| AKIA123456                   | String | ossConfig != null-是 | 对象存储 accessKey，最大128字符                          |
| ├─ secretKey| xxxxxxx                      | String | ossConfig != null-是 | 对象存储 secretKey，最大128字符                          |
| ├─ protocol | https                        | String | ossConfig != null-是 | 对象存储访问协议：http 或 https，最大16字符                    |
| ├─ region | cn-shanghai                  | String | ossConfig != null-是 | OSS 地域，最大32字符                                   |
| ├─ securityToken | xxxxxxxxx                    | String | credentialType=2-是  | 临时凭证token                                       |
| ├─ expiration | 2025-12-01T21:38:49z         | String | credentialType=2-是  | 过期时间                                            |
| credentialType   | 1                            | Integer | 否                   | 凭证类型。可选值：`1`永久凭证/`2`临时凭证。[详见枚举↗](./EnumReference.md#216-credentialtype---凭证类型) |

**响应参数**

| 参数名        | 示例值                                 | 参数类型  | 参数描述                      |
|-------------|-------------------------------------|-------|---------------------------|
| code        | 200                                 | Integer | 状态码（200表示成功）              |
| msg         | success                             | String  | 接口请求状态信息                  |
| ts          | 1758271736814                       | Long    | 时间戳                         |
| data        | {...}                               | Object  | 返回的任务信息对象                  |
| ├─ taskId   | 59                                  | Long    | 任务ID                        |
| ├─ padCode  | ACP250919HTTMIBQ                    | String  | 实例编号                        |
| ├─ vmStatus | 0                                   | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
| ├─ taskStatus | 1                                 | Integer | 任务状态：-1=任务已存在(请勿重复提交)，1=任务已添加 |
| ├─ errMsg   | null                                | String  | 描述或错误信息                     |
| ├─ backupName | backupName                        | String  | 备份名称                        |
| ├─ backupId | bkp-ACP250919HTTMIBQ-1758271735910  | String  | 备份ID                        |
| traceId     | eyj68nk6dnuo                        | String  | 请求链路追踪ID，用于问题排查             |
|

**请求示例**

```json
{
  "padCode": "ACP25091XXXXXX15",
  "backupName": "backnameinfo",
  "backupPath": "backup/data/",
  "credentialType": 1,
  "ossConfig": {
    "endpoint": "oss-cn-xxxxx.xxxxx.com",
    "bucket": "armcloud-cn",
    "accessKey": "LTAI5txxxxxxxYC",
    "secretKey": "kjgvYxxxxxxxxxxx8URWU",
    "protocol": "httpxxxx",
    "region": "cn-xxxxx"
  }
}
```

**响应示例**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1758271736814,
  "data": {
    "taskId": 59,
    "padCode": "ACP25091XXXXXX15",
    "vmStatus": 0,
    "taskStatus": 1,
    "errMsg": null,
    "backupName": "backnameinfo",
    "backupId": "bkp-ACP25091XXXXXX15-1758271735910"
  },
  "traceId": "eyj68nk6dnuo"
}
```

**错误码**

| 错误码   | 错误说明                                           | 操作建议           |
| ------ | ------------------------------------------------ |----------------|
| 220025 | 当前本地实例存在其他正在执行或待执行的任务，请等待任务执行完毕后再试！ | 等待任务执行完成后再尝试   |
| 220026 | 仅支持本地实例备份！                                  | 确认操作实例为本地实例    |
| 220029 | 当前实例状态不在运行中                                 | 确认实例处于运行中      |
| 220033 | 当前实例CBS版本过低，不支持备份或者还原                        | 联系客户经理升级板卡系统到最新版本后再尝试 |

#### **创建本地实例还原**

**接口类型**: 异步接口
**关联回调**: 通过返回的 `taskId` 轮询[本地实例备份结果查询](#本地实例备份结果查询)接口查询任务状态，建议查询间隔至少30秒

用于创建本地实例备份文件还原接口。

**接口概要**

作用：修改创建本地实例还原。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> `/openapi/open/pad/local/pod/restore`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名       | 示例值                                         | 参数类型 | 是否必填                | 参数描述                       |
|------------|--------------------------------------------|--------|---------------------|------------------------------|
| backupId   | bkp-ACP250917XSYESH3-1758097064458        | String | 是                   | 备份Id 最大128字符                  |
| padCode    | ACP250917CLAQJ15                           | String | 是                   | 实例编号，不能为空，最大64字符     |
| ossConfig   | {...}                       | Object | 否                   | 对象存储配置，需要支持 S3 协议，不能为空且永久授权                     |
| ├─ endpoint | oss-cn-shanghai.aliyuncs.com | String | ossConfig != null-是 | 对象存储 endpoint，最大128字符                           |
| ├─ bucket   | pad-backup                  | String | ossConfig != null-是 | 对象存储 bucket 名称，最大128字符                          |
| ├─ accessKey| AKIA123456                  | String | ossConfig != null-是 | 对象存储 accessKey，最大128字符                          |
| ├─ secretKey| xxxxxxx                     | String | ossConfig != null-是 | 对象存储 secretKey，最大128字符                          |
| ├─ protocol | https                       | String | ossConfig != null-是 | 对象存储访问协议：http 或 https，最大16字符                    |
| ├─ region   | cn-shanghai                 | String | ossConfig != null-是 | OSS 地域，最大32字符                                   |
| ├─ securityToken | xxxxxxxxx                    | String | credentialType=2-是  | 临时凭证token                                       |
| ├─ expiration | 2025-12-01T21:38:49z         | String | credentialType=2-是  | 过期时间                                            |
| credentialType   | 1                            | Integer | 否                   | 凭证类型。可选值：`1`永久凭证/`2`临时凭证。[详见枚举↗](./EnumReference.md#216-credentialtype---凭证类型) |

**响应参数**

| 参数名        | 示例值                                 | 参数类型  | 参数描述                      |
|-------------|-------------------------------------|-------|---------------------------|
| code        | 200                                 | Integer | 状态码（200表示成功）              |
| msg         | success                             | String  | 接口请求状态信息                  |
| ts          | 1758271736814                       | Long    | 时间戳                         |
| data        | {...}                               | Object  | 返回的任务信息对象                  |
| ├─ taskId   | 59                                  | Long    | 任务ID                        |
| ├─ padCode  | ACP250919HTTMIBQ                    | String  | 实例编号                        |
| ├─ vmStatus | 0                                   | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态) |
| ├─ taskStatus | 1                                 | Integer | 任务状态：-1=任务已存在(请勿重复提交)，1=任务已添加 |
| ├─ errMsg   | null                                | String  | 描述或错误信息                     |
| traceId     | eyj68nk6dnuo                        | String  | 请求链路追踪ID，用于问题排查             |

**请求示例**

```json
{
  "padCode": "ACP25091XXXXXJ15",
  "backupId": "bkp-ACP25091XXXXXJ15-1758097064458",
  "credentialType": 1
}

```

**响应示例**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1758271736814,
  "data": {
    "taskId": 59,
    "padCode": "ACP25091XXXXXX15",
    "vmStatus": 0,
    "taskStatus": 1,
    "errMsg": null
  },
  "traceId": "eyj68nk6dnuo"
}
```

**错误码**

| 错误码   | 错误说明                              | 操作建议                   |
| ------ |-----------------------------------| ---------------------- |
| 220025 | 当前本地实例存在其他正在执行或待执行的任务，请等待任务执行完毕后再试！ | 等待任务执行完成后再尝试       |
| 220027 | 当前本地实例备份文件不存在，请检查文件后再试！           | 检查备份文件是否存在          |
| 220030 | 当前实例状态不在运行中或者异常中                  | 确认实例处于运行或异常状态      |
| 220031 | 备份的文件不属于当前用户                      | 确认备份实例归属权限          |
| 220032 | 当前备份ID实例信息不存在，无法辨别当前备份文件是否属于当前用户  | 检查备份ID是否正确           |
| 220033 | 当前实例CBS版本过低，不支持备份或者还原             | 升级实例CBS版本后再尝试       |

#### **本地实例备份结果查询**

**接口类型**: 同步接口

根据实例编号获取本地实例可用备份。

**接口概要**

作用：修改本地实例备份结果查询。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> `/openapi/open/pad/local/pod/backupSelectPage`

**请求方式**

> `POST`

**请求数据类型**

> `application/json`

**请求Body参数**

| 参数名     | 示例值              | 参数类型   | 是否必填 | 参数描述              |
|---------|------------------|--------|-----|-------------------|
| page    | 1                | Integer | 否   | 当前页               |
| rows    | 10               | Integer | 否   | 每页的数量             |
| padCodes |                  | String[] | 是   |                   |
| ├─padCode | ACP5C24S9G6xxxxx | String | 是   | 实例编号，最大支持传入100条实例 |

**响应参数**

| 参数名        | 示例值                                  | 参数类型   | 参数描述                                             |
|---------------|------------------------------------------|----------|------------------------------------------------------|
| code          | 200                                      | Integer  | 状态码                                               |
| msg           | success                                  | String   | 响应消息                                             |
| ts            | 1756021167163                            | Long     | 时间戳                                               |
| data          |                                          | Object   | 返回的数据对象                                       |
| ├─ page       | 1                                        | Integer  | 当前页                                               |
| ├─ rows       | 10                                       | Integer  | 每页的数量                                           |
| ├─ size       | 1                                        | Integer  | 当前页的数量                                         |
| ├─ total      | 1                                        | Integer  | 总记录数                                             |
| ├─ totalPage  | 1                                        | Integer  | 总页数                                               |
| ├─ pageData   |                                          | Object[] | 列表                                                 |
| ├─├─ padCode      | ACP5C24S9G6xxxxx                           | String   | 实例编号                                             |
| ├─├─ backupId     | bkp-xxxxxS4QBMGEW1ZX-1764728535556     | String   | 备份ID                                               |
| ├─├─ backupName   | backupName                              | String   | 备份名称                                             |
| ├─├─ backupPath   | backup/db                               | String   | 备份数据保存路径                                     |
| ├─├─ endpoint     | backupName                              | String   | 备份名称（endpoint）                                 |
| ├─├─ bucket       | pad-backup                              | String   | 对象存储 bucket 名称，最大128字符                   |
| ├─├─ protocol     | https                                   | String   | 对象存储访问协议：http 或 https，最大16字符         |
| ├─├─ region       | cn-shanghai                             | String   | OSS 地域，最大32字符                                 |
| traceId     | eyj68nk6dnuo                        | String  | 请求链路追踪ID，用于问题排查

**请求示例**

```json
{
  "padCodes":["ACP5C24S9G6xxxxx"],
  "page":1,
  "rows":10
}

```

**响应示例**

```json
{
  "code": 200,
  "msg": "success",
  "ts": 1764819200220,
  "data": {
    "page": 1,
    "rows": 10,
    "size": 1,
    "total": 1,
    "totalPage": 1,
    "pageData": [
      {
        "padCode": "ACP5C24S9G6xxxxx",
        "backupId": "bkp-xxxxxS4QBMGEW1ZX-1764728535556",
        "backupName": "android13-xxxx-虚拟机-img-25112665572-王者荣耀+抖音",
        "backupPath": "backup/data/",
        "endpoint": "oss-cn-xxxxxx.xxxxxxx.com",
        "bucket": "armcloud-xx",
        "protocol": "https",
        "region": "cn-hongkong"
      }
    ]
  },
  "traceId": "f61kq5vu5ts0"
}
```

#### **清除进程并返回桌面**

**接口类型**: 同步接口

清除手机系统进程以外的所有进程，并返回桌面

**接口概要**

作用：修改清除进程并返回桌面。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/cleanAppHome

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名           | 示例值                              | 参数类型     | 是否必填 | 参数描述                    |
|---------------|----------------------------------|----------|------|-------------------------|
| padCodes      | ATP250814USYXXXX                    | String[] | 是    | 实例编码                    |

**响应参数**

参数名 | 示例值           | 参数类型     | 参数描述
--- |---------------|----------| --
code | 200           | Integer  | 状态码
msg | success       | String   | 响应消息
ts | 1736922808949 | Long     | 时间戳
traceId | euz60azzc7i8 | String   | 追踪ID
data |               | Object[] |
├─padCode | AC32032       | String   | 实例编号
├─taskId | 10004759      | Long     |任务id
├─vmStatus | 0             | String   | 实例在线状态
├─taskStatus | 1             | String   | 任务当前状态

**请求示例**

```javascript
{
    "padCodes": [
        "ATP250814USYXXXX"
    ]
}
```

**响应示例**

```javascript
{
    "msg": "success",
        "traceId": "euz60azzc7i8",
        "code": 200,
        "data": [
        {
            "padCode": "ATP250814USYXXXX",
            "vmStatus": 0,
            "taskId": 68951,
            "taskStatus": 1
        }
    ],
        "ts": 1755172215886
}
```

#### **无人直播**

**接口类型**: 异步接口
**关联回调**: [无人直播任务回调](#无人直播任务回调) (taskBusinessType: `1303`)

实例注入视频接口( 注意：目前只有img-25092692759 这个镜像版本可以使用，后续会更新其他哪些版本可以使用 )。支持通过单个视频地址`injectUrl`或地址列表`injectUrls`注入，二者至少传入一项且不能同时传入，`injectUrls`最多支持传入5个地址。

**接口概要**

作用：处理无人直播。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/unmanned/live

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名           | 示例值                                                                      | 参数类型     | 是否必填 | 参数描述                                 |
|---------------|--------------------------------------------------------------------------|----------|-----|--------------------------------------|
| padCodes      | ACN384345141346304                                                       | String[] | 是   | 实例编码(1-100个)                         |
| injectSwitch      | true                                                                     | Boolean | 否   | 是否开启注入视频。`true`开启/`false`取消，默认`false` |
| injectLoop     | false                                                                    | Boolean | 否    | 是否循环播放。`true`循环播放/`false`不循环，默认`false` |
| injectUrl      | https://file.vmoscloud.com/userFile/1eea385b2a6ba3942ebf642badf39aa0.mp4 | String   | 否   | 单个视频注入地址，支持 http/https/rtmp:// 以及本地路径，与injectUrls至少传一项 |
| injectUrls      | ["https://file.vmoscloud.com/userFile/1eea385b2a6ba3942ebf642badf39aa0.mp4","rtmp://example.com/live"] | String[]   | 否   | 视频注入地址列表(最多5个)，支持 http/https/rtmp:// 以及本地路径，与injectUrl至少传一项 |

**响应参数**

参数名 | 示例值                | 参数类型     | 参数描述
--- |--------------------|----------| --
code | 200                | Integer  | 状态码
msg | success            | String   | 响应消息
ts | 1759134336311      | Long     | 时间戳
traceId | ezispr1m30n4       | String   | 追踪ID
data |                    | Object[] |
├─padCode | ACN384345141346304 | String   | 实例编号
├─taskId | 20503              | Long     |任务id
├─vmStatus | 0                  | String   | 实例在线状态
├─taskStatus | 1                  | String   | 任务当前状态
├─errMsg | null               | String   | 错误提示

**请求示例**

```javascript
{
        "padCodes": ["ACN384345141346304"],
        "injectSwitch": true,
        "injectLoop": false,
        "injectUrl": "https://file.vmoscloud.com/userFile/1eea385b2a6ba3942ebf642badf39aa0.mp4",
        "injectUrls": [
          "https://file.vmoscloud.com/userFile/1eea385b2a6ba3942ebf642badf39aa0.mp4",
          "rtmp://example.com/live/unmanned01"
        ]
}
```
**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1759134336311,
        "data": [
        {
            "taskId": 20503,
            "padCode": "ACN384345141346304",
            "vmStatus": 0,
            "taskStatus": 1,
            "errMsg": null
        }
    ],
        "traceId": "ezispr1m30n4"
}
```

#### **图片注入**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `1303`)

实例注入图片接口

**接口概要**

作用：执行图片注入。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/inject/picture

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名           | 示例值                                                                      | 参数类型     | 是否必填 | 参数描述                                 |
|---------------|--------------------------------------------------------------------------|----------|-----|--------------------------------------|
| padCodes      | ACN2510166WZUPCJ                                                       | String[] | 是   | 实例编码(1-100个)                         |
| injectSwitch      | true                                                                     | Boolean | 否   | 是否开启注入图片(true:开启  false:取消) 默认是false |
| injectLoop     | false                                                                    | Boolean | 否    | 是否循环播放。`true`循环播放/`false`不循环，默认`false` |
| injectUrl      | https://file.vmoscloud.com/userFile/ac4e112d72f9ed724101f510e774001f.JPG | String   | 是   | 图片注入地址,支持 http https rtmp://         |

**响应参数**

参数名 | 示例值                | 参数类型     | 参数描述
--- |--------------------|----------| --
code | 200                | Integer  | 状态码
msg | success            | String   | 响应消息
ts | 1759134336311      | Long     | 时间戳
traceId | ezispr1m30n4       | String   | 追踪ID
data |                    | Object[] |
├─padCode | ACN384345141346304 | String   | 实例编号
├─taskId | 20503              | Long     |任务id
├─vmStatus | 0                  | String   | 实例在线状态
├─taskStatus | 1                  | String   | 任务当前状态
├─errMsg | null               | String   | 错误提示

**请求示例**

```javascript
{
        "padCodes": ["ACN2510166WZUPCJ"],
        "injectSwitch": true,
        "injectLoop": false,
        "injectUrl": "https://file.vmoscloud.com/userFile/ac4e112d72f9ed724101f510e774001f.JPG"
}
```
**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1759134336311,
        "data": [
        {
            "taskId": 28247,
            "padCode": "ACN2510166WZUPCJ",
            "vmStatus": 0,
            "taskStatus": 1,
            "errMsg": null
        }
    ],
        "traceId": "ezispr1m30n4"
}
```

#### **运动数据注入（步数）**

**接口类型**: 异步接口
**关联回调**: [实例状态回调](#实例状态回调) (taskBusinessType: `999`)

注入运动数据接口，支持向指定实例注入运动数据，因不同的第三方应用有不同运动数据获取规则，因此第三方应用准确性有一定偏差。

**接口概要**

作用：执行运动数据注入（步数）。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/stepData

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值                    | 参数类型     | 是否必填 | 参数描述
--- |------------------------|----------|-----| ---
padCodes | ["ACN519141428559881"] | String[] | 是   | 实例编号，需要注入运动数据的实例编号，单次最多500个实例，多个实例编号之间用英文逗号隔开
stepCount | 60                     | Integer  | 是   |步数 仅支持大于0的正整数，有效值大于0小于45000
motorPattern | 0                      | Integer    | 否   | 运动模式选择 0-慢，步频60 步 / 分钟 ,1-中，步频120 步 / 分钟,2-快，步频180 步 / 分钟 默认值为0
addNoise | true                   | Boolean   | 否   | 是否添加噪音。`true`添加噪音/`false`不添加，默认`false`。添加噪音可使数据更真实，但可能会增加相应任务时间

**响应参数**

参数名 | 示例值                | 参数类型     | 参数描述
--- |--------------------|----------| --
code | 200                | Integer  | 状态码
msg | success            | String   | 响应消息
ts | 1759134336311      | Long     | 时间戳
traceId | ezispr1m30n4       | String   | 追踪ID
data |                    | Object[] |
├─padCode | ACN384345141346304 | String   | 实例编号
├─taskId | 20503              | Long     |任务id
├─vmStatus | 0                  | String   | 实例在线状态
├─taskStatus | 1                  | String   | 任务当前状态
├─errMsg | null               | String   | 错误提示

**请求示例**

```javascript
{
    "padCodes": [
        "ACN519141428559881"
    ],
    "stepCount": 60,
    "motorPattern": 1,
    "addNoise": false
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1759134336311,
        "data": [
        {
            "taskId": 20503,
            "padCode": "ACN384345141346304",
            "vmStatus": 0,
            "taskStatus": 1,
            "errMsg": null
        }
    ],
        "traceId": "ezispr1m30n4"
}
```

### 回调管理

配置说明:需要客户在客户开放平台配置回调地址，配置地址成功则默认开启接收回调信息

#### **查询支持的回调类型**

**接口地址**

> /openapi/open/config/selectList

**请求方式**

> GET

**请求数据类型**

> 无参数

**响应参数**

|参数名 | 示例值           | 参数类型    | 参数描述                   |
|--- |---------------|---------|------------------------|
|code | 200           | Integer |                        |
|msg | success       | String  ||
|ts | 1713773577581 | Long    ||
|data |               | Object  ||
|├─callbackName | "文件上传任务"        | String  | 回调类型名称                 |
|├─callbackType | "4"          | String  | 回调类型                   |
|├─id | 14         | Long    | 回调类型的ID(后续新增修改需要传入该参数) |

**请求示例**

```javascript
/openapi/open/config/selectList
```

**响应示例**

```javascript
{
    "code": 200,
        "data": [
        {
            "callbackName": "文件上传任务",
            "callbackType": "4",
            "id": 14
        },
        {
            "callbackName": "文件上传实例任务",
            "callbackType": "5",
            "id": 15
        },
        {
            "callbackName": "应用同步任务",
            "callbackType": "6",
            "id": 16
        }
    ],
    "msg": "success",
    "ts": 1734500966127
}
```

**接口概要**

作用：查询查询支持的回调类型。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

#### **查询配置的回调地址**

**接口地址**

> /openapi/open/config/selectCallback

**请求方式**

> GET

**请求数据类型**

> 无参数

**响应参数**

|参数名 | 示例值           | 参数类型    | 参数描述     |
|--- |---------------|---------|----------|
|code | 200           | Integer |          |
|msg | success       | String  ||
|ts | 1713773577581 | Long    ||
|data |               | String  | 配置的回调地址 |

**请求示例**

```javascript
/openapi/open/config/selectCallback
```

**响应示例**

```javascript
{
 "code" : 200,
 "data" : "http://www.baidu.com",
 "msg" : "success",
 "ts" : 1734501602763
}
```

**接口概要**

作用：查询查询配置的回调地址。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

#### **新增回调地址配置**

**接口地址**

> /openapi/open/config/insertCallback

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | --- | --- | --- |
| callbackIdList | [1,2,3] | Long[] | 是 | 回调类型ID集合(从查询支持的回调类型接口获取) |
| callbackUrl | http://192.168.1.1/callback | String | 是 | 接收任务回调配置URL |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | --- | --- |
| code | 200 | Integer | 状态码 |
| msg | success | String | 响应消息 |
| ts | 1713773577581 | Long | 时间戳 |
| data | 2 | Integer | 配置成功type数量 |

**请求示例**

```javascript
{
  "callbackIdList": [21, 14],
  "callbackUrl": "http://localhost:8080/callback"
}
```

**响应示例**

```javascript
{"code":200,"data":2,"msg":"success","ts":1734502541732}
```

**接口概要**

作用：创建新增回调地址配置。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

#### **修改回调地址配置**

**接口地址**

> /openapi/open/config/updateCallback

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | --- | --- | --- |
| callbackIdList | [1,2,3] | Long[] | 是 | 回调类型ID集合(从查询支持的回调类型接口获取) |
| callbackUrl | http://192.168.1.1/callback | String | 是 | 接收任务回调配置URL |

**响应参数**

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | --- | --- |
| code | 200 | Integer | 状态码 |
| msg | success | String | 响应消息 |
| ts | 1713773577581 | Long | 时间戳 |
| data | 2 | Integer | 更新成功type数量 |

**请求示例**

```javascript
{
  "callbackIdList": [21, 14],
  "callbackUrl": "http://localhost:8080/callback"
}
```

**响应示例**

```javascript
{
 "code" : 200,
 "data" : 2,
 "msg" : "success",
 "ts" : 1734502541732
}
```

**接口概要**

作用：修改修改回调地址配置。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

#### **删除配置的回调地址**

**接口地址**

> /openapi/open/config/deleteCallback

**请求方式**

> POST

**请求数据类型**

> 无参数

**响应参数**

|参数名 | 示例值           | 参数类型    | 参数描述     |
|--- |---------------|---------|----------|
|code | 200           | Integer |          |
|msg | success       | String  ||
|ts | 1713773577581 | Long    ||
|data | 4             | Long    | |

**请求示例**

```javascript
{}
```

**响应示例**

```javascript
{
 "code" : 200,
 "data" : 22,
 "msg" : "success",
 "ts" : 1734503029282
}
```

**接口概要**

作用：修改删除配置的回调地址。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

#### **实例状态回调**

**使用场景**

实例状态变更的情况会通过该回调接口通知给客户。

| 字段               | 类型      | 示例     | 说明                                                                                                              |
|------------------|---------|--------|-----------------------------------------------------------------------------------------------------------------|
| taskBusinessType | Integer | 999    | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| padCode          | String  | 212254 | 实例标识                                                                                                            |
| padStatus        | Integer | 1      | 实例状态： 实例状态： -1 已删除 10-运行中 11-重启中 12-重置中 13-升级中 14-异常 15-未就绪 16-备份中 17-还原中 18-关机  19-关机中  20-开机中 21-关机失败 22-开机失败 |
| padConnectStatus | Integer | 1      | 实例连接状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#114-padconnectstatus---实例连接状态) |

**接口概要**

作用：处理实例状态回调。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

#### **实例重启任务回调**

**使用场景**

实例重启任务的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- |---------------| ---------- |
| taskBusinessType | Integer | 1000          |  任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型)|
| padCode| String  | 212254        | 实例编号   |
| taskStatus | Integer | 3             | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|
| taskId | Integer  | 1             | 任务ID      |
| taskContent | String  |               | 任务内容   |
| endTime | Long| 1756021166163 | 结束时间 |
| taskResult| String  | Success       | 任务结果   |

**接口概要**

作用：操作实例重启任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **实例重置任务回调**

**使用场景**

实例重置任务的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- |---------------| ---------- |
| taskBusinessType | Integer | 1001          |  任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型)|
| padCode| String  | 212254        | 实例编号   |
| taskStatus | Integer | 3             | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|
| taskId | Integer  | 1             | 任务ID      |
| taskContent | String  |               | 任务内容   |
| endTime | Long| 1756021166163 | 结束时间 |
| taskResult| String  | Success       | 任务结果   |

**接口概要**

作用：操作实例重置任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **异步执行ADB任务回调**

**使用场景**

客户调用异步执行ADB命令，会通过该回调接口通知给客户。

| 字段               | 类型    | 示例            | 说明                                                |
|------------------| ------- |---------------|---------------------------------------------------|
| taskBusinessType | Integer| 1002          | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| padCode          | String  | AC22030022001 | 实例标识                                              |
| taskId           | Integer| 1             | 任务id                                              |
| taskStatus       | Integer| 3             | 任务状态（-1：全失败；-2：部分失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态) |
| endTime          | Long| 1756021166163 | 任务执行结束时间                                          |
| taskResult       | String  | Success       | 任务结果                                              |
| taskContent      | String  |               | 任务内容                                              |
| cmd              | String  | cd /root;ls   | 执行的命令                                             |
| cmdResult        | String  | /ws           | 执行的命令返回                                           |

**接口概要**

作用：执行异步执行ADB任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **应用安装任务回调**

**使用场景**

客户调用应用安装，应用的安装情况会通过该回调接口通知给客户。

| 字段               | 类型    | 示例             | 说明       |
|------------------| ------- |----------------| ---------- |
| taskBusinessType | Integer| 1003           | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| taskId           | Integer | 1              | 任务ID |
| padCode       | String | AC22030022001  | 实例编号 |
| taskBusinessType | Integer| 1004          | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| endTime | Long| 1756021166163 | 结束时间 |
| apps             | Object[] |                | 应用信息   |
| ├─ appId         | Integer | 10001          |应用ID|
| ├─ appName       | String  | demo           | 应用名称   |
| ├─ pkgName       | String | com.xxx.demo   | 包名 |
| ├─ padCode       | String | AC22030022001  | 实例编号 |
| ├─ result        | boolean | true           | 安装结果的标识。true：成功，false：失败 |
| ├─ failMsg       | String | 此应用已加入黑名单，禁止安装 | 失败信息 |
| ├─ versionCode   | 150600 | String |  版本号
| ├─ versionName   | 15.6.0 | String |  版本名称

**接口概要**

作用：处理应用安装任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **应用卸载任务回调**

**使用场景**

客户调用应用卸载，应用卸载的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- |---------------| ---------- |
| taskBusinessType | Integer| 1004          | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| taskId | Integer | 1             | 任务ID |
| apps   | Object |               | 应用信息   |
| ├─ appId | Integer | 10001         |应用ID|
| ├─ appName | String  | demo          | 应用名称   |
| ├─ pkgName | String | com.xxx.demo  | 包名 |
| ├─ padCode | String | AC22030022001 | 实例编号 |
| ├─ result | boolean | true          | 安装结果的标识。true：成功，false：失败 |

**接口概要**

作用：处理应用卸载任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **应用停止任务回调**

**使用场景**

客户调用应用停止，应用停止的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- |---------------| ---------- |
| taskBusinessType | Integer| 1005           | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| padCode | String  | AC22030022001 | 实例标识   |
| taskId  | Integer | 1             | 任务ID     |
| taskStatus | Integer | 3             | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| packageName | String | xxx.test.com  | 包名 |

**接口概要**

作用：操作应用停止任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **应用启动任务回调**

**使用场景**

客户调用应用启动，应用启动的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例        | 说明       |
| ------- | ------- | ----------- | ---------- |
| taskBusinessType | Integer| 1007          | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| padCode | String  | AC22030022001      | 实例标识   |
| taskId  | Integer | 1           | 任务ID     |
| taskStatus | Integer | 3 | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| packageName | String | xxx.test.com | 包名 |

**接口概要**

作用：处理应用启动任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **文件上传实例任务回调**

**使用场景**

客户调用实例文件上传api，会通过该回调接口通知客户。

| 字段    | 类型    | 示例        | 说明       |
| ------- | ------- | ----------- | ---------- |
| taskBusinessType | Integer| 1009           | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| padCode | String  | AC22030022001      | 实例编号   |
| taskId   | Integer | 1           | 任务ID   |
| result  | boolean  |   true     | 执行结果：true-成功，false-失败   |
| errorCode  | String  |        |  错误码 |
| fileId | String   |  cf08f7b685ab3a7b6a793b30de1b33ae34         | 文件id |

**接口概要**

作用：创建文件上传实例任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **查询实例应用列表回调**

**使用场景**

客户调用实例已安装应用列表，实例已安装应用列表的情况会通过该回调接口通知给客户。

| 字段           | 类型    | 示例        | 说明       |
|--------------| ------- | ----------- | ---------- |
| taskBusinessType | Integer| 1011            | 任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型) |
| padCode      | String | AC22030022001 |pod标识|
| taskId       | Integer | 1           | 任务ID   |
| taskStatus   | Integer | 1 |任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）|
| apps         | Object[] |  | |
| ├─appName    | String  | test   | 应用名称 |
| ├─appState | 0 | Integer |  0 已完成  1安装中   2下载中
| ├─pkgName      | String | text.xx.com | 包名 |
| ├─versionCode  | 150600 | String |  版本号
| ├─versionName  | 15.6.0 | String |  版本名称

**接口概要**

作用：查询查询实例应用列表回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **实例升级镜像任务回调**

**使用场景**

实例升级镜像任务状态变更的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- |---------------| ---------- |
| taskBusinessType | Integer | 1012          |  任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型)|
| padCode| String  | 212254        | 实例编号   |
| taskStatus | Integer | 3             | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|
| taskId | Integer  | 1             | 任务ID      |
| taskContent | String  |               | 任务内容   |
| endTime | Long| 1756021166163 | 结束时间 |
| taskResult| String  | Success       | 任务结果   |

**接口概要**

作用：操作实例升级镜像任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **实例黑名单任务回调**

**使用场景**

实例设置应用黑名单任务状态变更的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例        | 说明       |
| ------- | ------- | ----------- | ---------- |
| taskBusinessType | Integer | 1015          |  任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型)|
| padCode| String  | 212254      | 实例编号   |
| taskId | Integer  | 1         | 任务ID     |
| taskStatus | Integer | 3 | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）|

[//]: # (#### **备份实例回调**)

[//]: #
[//]: # (**使用场景**)

[//]: #
[//]: # (实例备份实例的情况会通过该回调接口通知给客户。)

[//]: #
[//]: # (| 字段    | 类型    | 示例            | 说明       |)

[//]: # (| ------- | ------- |---------------| ---------- |)

[//]: # (| taskBusinessType | Integer | 1024          |  任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型)|)

[//]: # (| padCode| String  | 212254        | 实例编号   |)

[//]: # (| taskStatus | Integer | 3             | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|)

[//]: # (| taskId | Integer  | 1             | 任务ID      |)

[//]: # (| taskContent | String  |               | 任务内容   |)

[//]: # (| endTime | Long| 1756021166163 | 结束时间 |)

[//]: # (| taskResult| String  | Success       | 任务结果   |)

[//]: #
[//]: # (#### **还原备份数据回调**)

[//]: #
[//]: # (**使用场景**)

[//]: #
[//]: # (还原备份数据的情况会通过该回调接口通知给客户。)

[//]: #
[//]: # (| 字段    | 类型    | 示例            | 说明       |)

[//]: # (| ------- | ------- |---------------| ---------- |)

[//]: # (| taskBusinessType | Integer | 1025          |  任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型)|)

[//]: # (| padCode| String  | 212254        | 实例编号   |)

[//]: # (| taskStatus | Integer | 3             | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|)

[//]: # (| taskId | Integer  | 1             | 任务ID      |)

[//]: # (| taskContent | String  |               | 任务内容   |)

[//]: # (| endTime | Long| 1756021166163 | 结束时间 |)

[//]: # (| taskResult| String  | Success       | 任务结果   |)

**接口概要**

作用：处理实例黑名单任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **一键新机回调**

**使用场景**

一键新机的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- |---------------| ---------- |
| taskBusinessType | Integer | 1124            |  任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型)|
| padCode| String  | 212254        | 实例编号   |
| taskStatus | Integer | 3             | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|
| taskId | Integer  | 1             | 任务ID      |
| taskContent | String  |               | 任务内容   |
| endTime | Long| 1756021166163 | 结束时间 |
| taskResult| String  | Success       | 任务结果   |

**接口概要**

作用：处理一键新机回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存实例开机回调**

**使用场景**
网存实例开机的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- | --------------- | ---------- |
| taskBusinessType | Integer | 1201 | 任务业务类型 |
| padCode | String  | ACN250427352B7WU | 实例编号   |
| taskStatus | Integer | 3 | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001661 | 任务ID      |
| taskContent | String | （空字符串） | 任务内容 |
| endTime | Long | null | 结束时间（时间戳，单位毫秒） |
| taskResult | String | （空字符串） | 任务结果 |

**示例内容**

```json
{
  "endTime": null,
  "padCode": "ACN250427352B7WU",
  "taskBusinessType": 1201,
  "taskContent": "",
  "taskId": 10001661,
  "taskResult": "",
  "taskStatus": 3
}
```

---

**接口概要**

作用：处理网存实例开机回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存实例关机回调**

**使用场景**
网存实例关机的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- | --------------- | ---------- |
| taskBusinessType | Integer | 1202 | 任务业务类型 |
| padCode | String  | ACN250427352B7WU | 实例编号   |
| taskStatus | Integer | 3 | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001662 | 任务ID      |
| taskContent | String | （空字符串） | 任务内容 |
| endTime | Long | null | 结束时间（时间戳，单位毫秒） |
| taskResult | String | （空字符串） | 任务结果 |

**示例内容**

```json
{
  "endTime": null,
  "padCode": "ACN250427352B7WU",
  "taskBusinessType": 1202,
  "taskContent": "",
  "taskId": 10001662,
  "taskResult": "",
  "taskStatus": 3
}
```

---

**接口概要**

作用：处理网存实例关机回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存实例删除回调**

**使用场景**
网存实例删除的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- | --------------- | ---------- |
| taskBusinessType | Integer | 1203 | 任务业务类型 |
| padCode | String  | ACN250427352B7WU | 实例编号   |
| taskStatus | Integer | 3 | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001662 | 任务ID      |
| taskContent | String | （空字符串） | 任务内容 |
| endTime | Long | null | 结束时间（时间戳，单位毫秒，null 表示尚未结束） |
| taskResult | String | （空字符串） | 任务结果 |

**示例内容**

```json
{
  "endTime": null,
  "padCode": "ACN250427352B7WU",
  "taskBusinessType": 1203,
  "taskContent": "",
  "taskId": 10001672,
  "taskResult": "",
  "taskStatus": 3
}
```

---

---

**接口概要**

作用：修改网存实例删除回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存存储备份回调**

**使用场景**
网存存储备份的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- | --------------- | ---------- |
| taskBusinessType | Integer | 1204 | 任务业务类型 |
| padCode | String  | ACN250427352B7WU | 实例编号   |
| taskStatus | Integer | 3 | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001664 | 任务ID      |
| taskContent | String | （空字符串） | 任务内容 |
| endTime | Long | null | 结束时间（时间戳，单位毫秒，null 表示尚未结束） |
| taskResult | String | （空字符串） | 任务结果 |

**示例内容**

```json
{
  "endTime": null,
  "padCode": "ACN250427352B7WU",
  "taskBusinessType": 1204,
  "taskContent": "",
  "taskId": 10001664,
  "taskResult": "",
  "taskStatus": 3
}
```

---

---

**接口概要**

作用：修改网存存储备份回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存存储删除回调**

**使用场景**
网存存储删除的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例            | 说明       |
| ------- | ------- | --------------- | ---------- |
| taskBusinessType | Integer | 1205 | 任务业务类型 |
| padCode | String  | ACN250427352B7WU | 实例编号   |
| taskStatus | Integer | 3 | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001665 | 任务ID      |
| taskContent | String | （空字符串） | 任务内容 |
| endTime | Long | null | 结束时间（时间戳，单位毫秒，null 表示尚未结束） |
| taskResult | String | （空字符串） | 任务结果 |

**示例内容**

```json
{
  "endTime": null,
  "padCode": "ACN250427352B7WU",
  "taskBusinessType": 1205,
  "taskContent": "",
  "taskId": 10001665,
  "taskResult": "",
  "taskStatus": 3
}
```

---

**接口概要**

作用：修改网存存储删除回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **文件上传任务回调**

**使用场景**

客户调用上传文件，上传文件的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例        | 说明       |
| ------- | ------- | ----------- | ---------- |
| taskBusinessType | Integer | 2000          |  任务业务类型。[查看所有业务类型↗](./EnumReference.md#21-taskbusinesstype---任务业务类型)|
| taskId   | Integer | 1           | 任务ID   |
| taskStatus | Integer | 3 |任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）|
| originFileUrl | String |  |原文件下载地址|
| fileUniqueId | String | test001      | 文件id |

**接口概要**

作用：创建文件上传任务回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存2.0开机回调**

**使用场景**
网存实例开机的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例                 | 说明       |
| ------- | ------- |--------------------| ---------- |
| taskBusinessType | Integer | 1301               | 任务业务类型 |
| padCode | String  | ACN317629292153649 | 实例编号   |
| taskStatus | Integer | 3                  | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001085           | 任务ID      |
| taskContent | String | （空字符串）             | 任务内容 |
| endTime | Long | null               | 结束时间（时间戳，单位毫秒） |
| taskResult | String | （空字符串）             | 任务结果 |

**示例内容**

```json
{
  "endTime": null,
  "padCode": "ACN317629292153649",
  "taskBusinessType": 1301,
  "taskContent": "",
  "taskId": 10001085,
  "taskResult": "Success",
  "taskStatus": 3
}
```

---

**接口概要**

作用：处理网存2.0开机回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存2.0关机回调**

**使用场景**
网存实例关机的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例                 | 说明       |
| ------- | ------- |--------------------| ---------- |
| taskBusinessType | Integer | 1302               | 任务业务类型 |
| padCode | String  | ACN317629292153649 | 实例编号   |
| taskStatus | Integer | 3                  | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001086           | 任务ID      |
| taskContent | String | （空字符串）             | 任务内容 |
| endTime | Long | null               | 结束时间（时间戳，单位毫秒） |
| taskResult | String | （空字符串）             | 任务结果 |

**示例内容**

```json
{
  "endTime": 1755141290862,
  "padCode": "ACN317629292153649",
  "taskBusinessType": 1302,
  "taskContent": "",
  "taskId": 10001086,
  "taskResult": "Success",
  "taskStatus": 3
}
```

---

**接口概要**

作用：处理网存2.0关机回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存2.0实例删除回调**

**使用场景**
网存实例删除的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例                 | 说明       |
| ------- | ------- |--------------------| ---------- |
| taskBusinessType | Integer | 1303               | 任务业务类型 |
| padCode | String  | ACN317629292153649 | 实例编号   |
| taskStatus | Integer | 3                  | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001087           | 任务ID      |
| taskContent | String | （空字符串）             | 任务内容 |
| endTime | Long | null               | 结束时间（时间戳，单位毫秒，null 表示尚未结束） |
| taskResult | String | （空字符串）             | 任务结果 |

**示例内容**

```json
{
  "endTime": 1755141290862,
  "padCode": "ACN317629292153649",
  "taskBusinessType": 1303,
  "taskContent": "",
  "taskId": 10001087,
  "taskResult": "",
  "taskStatus": 3
}
```

---

---

**接口概要**

作用：修改网存2.0实例删除回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **网存2.0存储备份回调**

**使用场景**
网存存储备份的情况会通过该回调接口通知给客户。

| 字段    | 类型    | 示例                         | 说明       |
| ------- | ------- |----------------------------| ---------- |
| taskBusinessType | Integer | 1304                       | 任务业务类型 |
| padCode | String  | ACN317629292153649         | 实例编号   |
| taskStatus | Integer | 3                          | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001088                   | 任务ID      |
| taskContent | String | json字符串，内容为克隆出的新实例集合（需要解析） | 任务内容 |
| endTime | Long | null                       | 结束时间（时间戳，单位毫秒，null 表示尚未结束） |
| taskResult | String | （空字符串）                     | 任务结果 |

**示例内容**

```json
{
  "endTime": 1755001588956,
  "padCode": "ACN317629292153649",
  "taskBusinessType": 1304,
  "taskContent": "[\"ACN317629292153650\"]",
  "taskId": 10001088,
  "taskResult": "Success",
  "taskStatus": 3
}
```

**接口概要**

作用：修改网存2.0存储备份回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

#### **订阅事件回调**

**使用场景**
客户订阅事件后，当所订阅事件触发则平台通过该回调接口通知给客户。( 注意：img-25111133267镜像版本开始生效 )

| 字段    | 类型      | 示例                         | 说明                                        |
| ------- |---------|----------------------------|-------------------------------------------|
| eventType | Integer |  50              | 订阅事件类型。可选值：`50`应用启动/`51`应用停止 |
| timestamp | Long    | 1762221316                 | 回调时间戳                                      |
| eventDetail | Object  |                            | 事件详情，以下内容为JSON |
| ├─padCode | String | ACN000000                  | 实例编号                                      |
| ├─packageName | String  | COM.BAIDU | 应用包名                                      |
| ├─eventTime | Long  | 1762221362                    | 事件时间戳                                     |

**示例内容**

```json
{
  "eventType": 50,
  "timestamp": "1762221316",
  "eventDetail": {
    "padCode": "ACN000000",
    "packageName": "COM.BAIDU",
    "eventTime": "1762221362"
  }
}

```

#### 无人直播任务回调

**使用场景**
云机执行无人直播任务时，任务执行完成（成功 / 失败 / 取消 / 超时等）会通过该回调接口通知给客户。

| 字段    | 类型    | 示例                         | 说明       |
| ------- | ------- |----------------------------| ---------- |
| taskBusinessType | Integer | 1052                        | 任务业务类型 |
| padCode | String  | ACN3176292921xxxxxxx       | 实例编号   |
| taskStatus | Integer | 3                          | 任务状态（-1：全失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
| taskId | Integer | 10001088                   | 任务ID      |
| taskContent | String | json字符串，内容为克隆出的新实例集合（需要解析） | 任务内容 |
| endTime | Long | null                       | 结束时间（时间戳，单位毫秒，null 表示尚未结束） |
| taskResult | String | （空字符串）                     | 任务结果 |

**示例内容**

```json
{
  "endTime": 1755001588956,
  "padCode": "ACN3176292921xxxxxxx",
  "taskBusinessType": 1052,
  "taskContent": "[\"ACN3176292921xxxxxxx\"]",
  "taskId": 10001088,
  "taskResult": "Success",
  "taskStatus": 3
}
```

**接口概要**

作用：处理订阅事件回调。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

### 文件管理

#### **文件上传到云盘**

**接口类型**: 异步接口
**关联回调**: [文件上传任务回调](#文件上传任务回调) (taskBusinessType: `2000`)

进行文件上传操作，上传到云盘

**接口概要**

作用：创建文件上传到云盘。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**查询实例状态

> /file-center/open/file/cache

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
fileUrl |  | String | 是 | 文件下载地址
fileName | 桃源深处有人家游戏官方版.apk | String | 是 | 文件名称
fileMd5 | 32e1f345f209a7dc1cc704913ea436d3 | String | 是 | ⽂件预期md5，⽤作下载⽂件校验最⼤⻓度32

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
data |  | Object[] |
├─taskId | 1 | Integer | 任务ID
├─fileUniqueId | 6865b417b7257d782afd5ac8bee4d311 | String | 文件唯一标识

**请求示例**

```javascript

{
    "fileUrl": "http://down.s.qq.com/download/11120898722/apk/10043132_com.tencent.fiftyone.yc.apk",
    "fileName": "桃源深处有人家游戏官方版.apk",
    "fileMd5": "c52585e13a67e13128d9963b2f20f69678a86ee8b5551ca593327d329719a5"
}

```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1713773577581,
 "data": {
  "taskId":1,
  "fileUniqueId": "6865b417b7257d782afd5ac8bee4d311"
 }
}
```

#### **实例文件删除**

**接口类型**: 同步接口

实例文件删除

**接口概要**

作用：修改实例文件删除。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /file-center/open/file/batch/del

**请求方式**

> POST (支持批量删除，一次最多只能删除200个)

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
fileUniqueIds | cfc280111c435823c5409ddb9a4186420d | String[] | 是 | unique_id→文件id标识

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
data | true | Boolean |

**请求示例**

```javascript

{
 "fileUniqueIds": [
  "cfc280111c435823c5409ddb9a4186420d",
  "cf77f930acbbe1707fffc661f2c4380a71"
 ]
}

```

**响应示例(全部成功)**

```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1734677342300,
  "data": true
}

```

**响应示例(部分成功)**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1734935677246,
        "data": [
        "cfc280111c435823c5409ddb9a4186420d"
    ]
}

```

#### **文件上传实例V3版本**

**接口类型**: 异步接口
**关联回调**: [文件上传实例任务回调](#文件上传实例任务回调) (taskBusinessType: `2000`)

从文件管理中心推送文件到一个或多个云手机实例（异步任务）

**接口概要**

作用：创建文件上传实例V3版本。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/v3/uploadFile

- 如果能通过md5值或者文件ID找到对应的文件,会直接通过OSS的路径下发给实例下载
- 如果OSS没有对应的文件,会直接将URL下发给实例下载,并且将该URL内容上传到OSS
- 如果选择安装应用,会检验包名是否有值,如果没值,会抛出异常.(安装应用默认会授权所有权限,通过isAuthorization字段可以选择不授权)
  **请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值                                                                           | 参数类型     | 是否必填 | 参数描述
--- |-------------------------------------------------------------------------------|----------|------| ---
padCodes |                                                                               | String[] | 是    |
├─ | AC22030023061                                                                 | String   | 是    | 实例编号
autoInstall | 1                                                                             | Integer  | 否    | 是否需要⾃动安装 1需要、0不需要。不填默认不需要。仅对apk类型的⽂件⽣效
fileUniqueId | 1e5d3bf00576ee8f3d094908c0456722                                              | String   | 否    | 文件id唯一标识。
customizeFilePath | /Documents/                                                                   | String   | 否    | ⾃定义路径。非必传，支持的文件路径包括以下目录：/DCIM/, /Documents/, /Download/, /Movies/, /Music/, /Pictures/。
fileName | threads                                                                       | String   | 否    | 文件名称
packageName | com.zhiliaoapp.musically                                                      | String   | 否    | 文件包名
url |  | String   | 否    | 文件安装路径
md5 | d41d8cd98f00b204e980xxxxxxxxxxx                                               | String   | 否    | 文件MD5值（用于校验文件完整性，可通过MD5查找已上传的文件）
isAuthorization | false                                                                         | Boolean  | 否    | 是否授权应用。`true`授权/`false`不授权，默认`true`(全授权)
iconPath |  | string   | 否    | 安装时的图标展示

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
data |  | Object[] |
├─padCode | AC22010020062 | String | 实例编号
├─taskId | 1 | Integer | 任务ID
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
    "padCodes":["AC32010250022"],
        "customizeFilePath":"/DCIM/",
        "md5":"d97fb05b3a07d8werw2341f10212sdfs3sdfs24",
        "url":"https://oss.domain.com/appMarket/2/apk/fe1f75df23e6fe3fd3b31c0f7f60c0af.apk ",
        "autoInstall":1,
        "packageName":"com.zhiliaoapp.musically",
        "fileName":"market",
        "isAuthorization":false
}

```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1737431505379,
        "data": [
        {
            "taskId": 13469,
            "padCode": "AC32010250022",
            "vmStatus": 0,
            "taskStatus": 1
        }
    ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- |---
140006 | 文件存储路径不正确| ⾃定义路径需以/开头
140005 | 文件不可用| 文件路径为空
110006 | 下载失败| 文件路径不能下载

#### **文件上传到实例**

**接口类型**: 异步接口
**关联回调**: [文件上传实例任务回调](#文件上传实例任务回调) (taskBusinessType: `2000`)

从文件管理中心推送文件到一个或多个云手机实例（异步任务）

**接口概要**

作用：创建文件上传到实例。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/v2/uploadFile

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值                              | 参数类型     | 是否必填 | 参数描述
--- |----------------------------------|----------| --- | ---
padCodes |                                  | String[] | 是 |
├─ | AC22030023061                    | String   | 是 | 实例编号
autoInstall | 0                                | Integer  | 否 | 是否需要⾃动安装 1需要、0不需要。仅对apk类型的⽂件⽣效。不需要请不要填或填0
fileUniqueId | 1e5d3bf00576ee8f3d094908c0456722 | String   | 是 | 文件id唯一标识。
customizeFilePath | /Documents/                      | String   | 否 | ⾃定义路径。非必传，支持的文件路径包括以下目录：/DCIM/, /Documents/, /Download/, /Movies/, /Music/, /Pictures/。
isAuthorization | false                            | Boolean      | 否 | 是否授权应用。`true`授权/`false`不授权，默认`true`(全授权)

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |  | Object[] |
├─padCode | AC22010020062 | String | 实例编号
├─taskId | 1 | Integer | 任务ID
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "padCodes": [
  "AC22030023061"
 ],
 "isAuthorization":false,
 "autoInstall": 0,
 "fileUniqueId": "1e5d3bf00576ee8f3d094908c0456722",
 "customizeFilePath": "/Documents/"
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",

 "ts": 1717571059834,
 "data": [
  {
   "taskId": 39,
   "padCode": "AC22030010001",
   "vmStatus": 1,
      "taskStatus": 1

  },
  "traceId": "ewab8qjqbaio"

]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- |---
140006 | 文件存储路径不正确| ⾃定义路径需以/开头
140005 | 文件不可用| 文件路径为空
110006 | 下载失败| 文件路径不能下载

#### **文件列表**

**接口类型**: 同步接口

查询已上传的文件列表信息

**接口概要**

作用：查询文件列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /file-center/open/file/list

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值     | 参数类型    | 是否必填 | 参数描述
--- |---------|---------|------| ---
page | 1       | Integer | 是    | 起始页,默认1
rows | 10      | Integer | 是    | 查询数量,默认10
fileName | "33"   | String  | 否    | 根据文件名查询

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- |-------------
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |  | Object |
├─page | 1 | Integer | 当前页
├─rows | 10 | Integer | 每页的数量
├─size | 2 | Integer | 当前页的数量
├─total | 2 | Integer | 总记录数
├─totalPage | 1 | Integer | 总页数
├─pageData |  | object[] | 列表
├─├─fileUniqueId | c417cdf30cd13437a60a494f2fcee616 | String | 文件id标识
├─├─fileName | 15b18072b01049dfa30da046aaf5b213.apk | String | 文件名
├─├─fileMd5 | 49f526ec07f261ef6c22081fd61fb6b2836b84214ab6f4620e89d2f2d454253 | String | 文件内容值
├─├─fileSize | 165936779 | Integer | 文件大小（单位：字节）
├─├─originUrl |  | String | 文件原地址
├─├─createTime | 1713884498000 | Long | 创建时间
├─├─Id | 134 | Long | 文件id        |

**请求示例**

```javascript

{
    "page": 1,
    "rows": 10,
    "fileName":"33"
}

```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1750616581943,
        "data": {
        "page": 1,
            "rows": 10,
            "size": 10,
            "total": 466,
            "totalPage": 47,
            "pageData": [
            {
                "fileName": "wa-vmos-debug.apk",
                "fileSize": 12957234,
                "fileUniqueId": "f3b9afb69c8e4953b171950766ebbb9a",
                "originUrl": null,
                "createdTime": 1750162347000,
                "id": 487451,
                "fileMd5": "9fe3cfc677baaff554eb4c2506234d0f"
            }
            // ... 更多文件对象
        ]
    },
    "traceId": "epr0w079xc00"
}
```

#### **文件任务详情**

**接口类型**: 同步接口

查询指定文件任务的执行结果详细信息。

**接口概要**

作用：查询文件任务详情。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /task-center/open/task/fileTaskDetail

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Query参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
taskIds |  | Integer[] | 是 |
├─taskId | 1 | Integer | 是 |任务ID

**响应参数**

|参数名 | 示例值 | 参数类型 | 参数描述 |
|--- | --- | --- | --- |
|code | 200 | Integer | 状态码 |
|msg | success | String | 响应消息 |
|ts | 1756021167163 | Long | 时间戳 |
|data |  | Object[] | 任务列表详情 |
|├─ taskId | 1 | Integer | 子任务ID |
|├─ appId | 134 | Long | 应用id |
|├─ fileUniqueId | e2c07491309858c5cade4bfc44c03724 | String | ⽂件唯⼀标识 |
|├─ fileName | xx.apk | String | 文件名称 |
|├─ taskStatus | 2 | Integer | 任务状态（-1：全失败；-2：部分失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成） |
|├─ endTime | 1713429401000 | Long | 子任务结束时间戳 |

**请求示例**

```javascript
{
 "taskIds":[
  1,2
 ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1716283460673,
 "data": [
  {
   "taskId": 1,
   "appId": 134,
   "fileUniqueId": "e2c07491309858c5cade4bfc44c03724",
   "fileName": "xx.apk",
   "taskStatus": 2,
   "endTime": 1713429401000
  },
  {
   "taskId": 2,
   "appId": 135,
   "fileUniqueId": "e2c07491309858c5cade4bfc43c03725",
   "fileName": "xx.apk",
   "taskStatus": 2,
   "endTime": 1713429401001
  }
 ]
}
```

### 应用管理

#### **应用上传**

**接口类型**: 同步接口

上传应用安装文件到指定业务的应用管理中心（异步任务）。

**接口概要**

作用：创建应用上传。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /file-center/open/app/cache

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
parse | true | Boolean | 是 | 是否缓存并解析（解析并缓存） 如解析则无需填包信息
apps |  | Object[]  | 是 | 应用列表
├─ appId | 1243 | Integer | 否 | 自定义应用ID
├─ url |  | String | 是 | 源文件下载地址
├─ appName | kuaishou | String | 否 | 应用名称
├─ pkgName | com.smile.gifmaker | String | 否 | 包名
├─ signMd5 | 0F938C4F0995A83C9BF31F0C64322589 | String | 否 | 应用签名MD5
├─ versionNo | 36000 | Integer | 否 | 版本号
├─ versionName | 12.3.20.36000 | String | 否 | 版本名
├─ description | kuai | String | 否 | 描述
├─ md5sum | e673a204b8f18a0f6482da9998 | String | 否 | 应用唯一标识

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |  | Object[] |
├─ taskId | 12 | Integer |  任务ID
├─ appId | 1243 | Integer |  应用ID
├─ url |  | String | 是 | 源文件下载地址
**请求示例**

```javascript
{
 "parse": true,
 "apps": [
  {
   "appId": 1243,
   "appName": "kuaishou",
   "url": "https://xxx.armcloud.apk",
   "pkgName": "com.smile.gifmaker",
   "signMd5": "0F938C4F0995A83C9BF31F0C64322589",
   "versionNo": 36000,
   "versionName": "12.3.20.36000",
   "description": "kuai",
   "md5sum": "e673a204b8f18a0f6482da9998"
  }
 ]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1755603598157,
        "data": [
        {
            "appId": 996875143,
            "url": "https://xxx.abc.com/app/b66bbdb93f404cfdac955bc35ace809a.apk",
            "taskId": 197136930
        }
    ],
    "traceId": "evgzda3b7f9c"
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
100001 | 没有访问权限| 是否没有订购机房

#### **应用列表**

**接口类型**: 同步接口

可根据应用ID查询应用信息列表。

**接口概要**

作用：查询应用列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /file-center/open/app/list

**请求方式**

> POST

**请求数据类型**
> application/json

**请求Query参数**

参数名 | 示例值                      | 参数类型      | 是否必填 | 参数描述
--- |--------------------------|-----------| --- | ---
page | 1                        | Integer   | 是 | 起始页,默认1
rows | 10                       | Integer   | 是 | 查询数量,默认10
appIds | 1,2                      | Integer[] | 否 | 应用id
packageName | com.ss.android.ugc.aweme | String    | 否 | 应用包名

**响应参数**

参数名 | 示例值 | 参数类型     | 参数描述
--- | -- |----------| ---
code | 200 | Integer  | 状态码
msg | success | String   | 响应消息
ts | 1756021167163 | Long     | 时间戳
packageName | com.ss.android.ugc.aweme | String     | 包名
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
pageData |  | Object   |
├─page | 1 | Integer  | 当前页
├─rows | 10 | Integer  | 每页显示数量
├─size | 10 | Integer  | 当前页的数量
├─total | 2 | Integer  | 总数量
├─totalPage | 1 | Integer  | 总页数
├─pageData |  | Object[] |
├─├─originUrl | downloadUrl_tr0bi | String   | 文件原下载地址
├─├─appId | dwadawdf | Integer  | 自定义应用ID
├─├─description | description_1cq3m | String   | 描述
├─├─packageName | packageName_e6lw8 | String   | 包名
├─├─appName | appName_o4mhn | String   | 应用名称
├─├─versionName | versionName_s4o2i | String   | 版本名
├─├─versionNo | 1 | Integer  | 版本号
├─├─signMd5 | 0F938C4F0995A83C9BF31F0C64322589 | String   | MD5
├─├─available | true | Boolean  | 当前文件是否可用
├─├─createTime | 1709895492000 | Integer  | 创建时间
├─├─fileId | 文件id | Integer  | 文件id
├─├─iconPath |  | String   | 应用图标
├─├─newAppClassifyList | 应用分类 | Object[] | 应用分类
├─├─├─classifyName | test | String | 应用分类名称
├─├─├─classifyId | 1 | Long | 应用分类id
├─├─├─description | 这个应用质量很高 | String | 应用描述 备注
├─├─├─sortNum | 1 | Integer | 排序-输入框-仅支持整数输入，最大限制10000，列表按照数值从小到大排序展示

**请求示例**

```javascript

{
    "rows": 10,
    "page": 1,
    "appIds": [
        1,2
    ],
    "packageName":"com.ss.android.ugc.aweme"
}

```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
 "traceId": "ewab8qjqbaio",
 "data": {
  "page": 1,
  "rows": 10,
  "size": 10,
  "total": 30,
  "totalPage": 3,
  "pageData": [
   {
    "originUrl": "downloadUrl_tr0bi",
    "appId": 1,
    "description": "description_1cq3m",
    "packageName": "packageName_e6lw8",
    "appName": "appName_o4mhn",
    "versionName": "versionName_s4o2i",
    "versionNo": 1,
    "signMd5": "0F938C4F0995A83C9BF31F0C64322589",
    "available": true,
    "createTime": 1709895492000,
                "iconPath": "http://192.168.230.80:18100/icon/110_6ca4d3e6e5111ec38e8eca6c1998ce89..png",
                "fileId": 1,
                "newAppClassifyList": [
                    {
                        "classifyName": "f1",
                        "classifyId": 3
                    }
                ]
   }
   // ... 更多应用对象
  ]
 }
}
```

#### **应用详情**

**接口类型**: 同步接口

查询指定实例上的应用安装情况

**接口概要**

作用：查询应用详情。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /file-center/open/app/detail

**请求方式**

> POST

**请求数据类型**
> application/json

**请求Query参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
appId | 1 | Integer | 是 | 应用id

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756076880250 | Long | 时间戳
traceId | ew0j0vipc3y8 | String | 链路追踪ID
data |  | Object | 应用详情
├─appId | 1178436326 | Long | APP ID
├─originalUrl | https://file.vsphone.com/appMarket/null/apk/2d12187c91cf0f2024b3015777175.apk | String | 原文件下载地址
├─description | null | String | 文件备注/应用描述
├─packageName | com.truedevelopersstudio.automatictap.autoclicker | String | Android 包名
├─appName | Auto Clicker | String | 应用名称
├─versionName | 2.1.4 | String | 版本名
├─versionNo | 81 | Integer | 版本号
├─signMd5 | f282d5b8aa801ab13517ad1fe9dbc2b1 | String | 签名 MD5
├─createTime | 1751009986000 | Long | 文件创建时间
├─minSdkVersion | 24 | Integer | 最低 SDK 版本
├─targetSdkVersion | 31 | Integer | 目标 SDK 版本

**请求示例**

```javascript
{
 "appId":1
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756076880250,
        "data": {
        "minSdkVersion": 24,
            "createTime": 1751009986000,
            "appName": "Auto Clicker",
            "appId": 1178436326,
            "versionNo": 81,
            "description": null,
            "signMd5": "f282d5b8aa801ab13517ad1fe9dbc2b1",
            "originalUrl": "https://file.vsphone.com/appMarket/null/apk/2d12187c91cf0f2024b3015777175.apk",
            "packageName": "com.truedevelopersstudio.automatictap.autoclicker",
            "targetSdkVersion": 31,
            "versionName": "2.1.4"
    },
    "traceId": "ew0j0vipc3y8"
}
```

#### **查询实例应用列表**

**接口类型**: 同步接口

查询已上传的文件列表信息

**接口概要**

作用：查询查询实例应用列表。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/listApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes |  | String[] | 否 |
├─ | AC22010020062 | String | 是 | 实例编号

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |  | Object[] |
├─taskId | 1 | Integer | 任务ID
├─padCode | AC22010020062 | String | 实例编号
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
    "padCodes": [
        "AC22010020062"
    ]
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1756077327794,
        "data": [
        {
            "taskId": 13462859,
            "padCode": "ACN250823P61EWV1",
            "vmStatus": 0,
            "taskStatus": 1
        }
    ],
        "traceId": "ew0jotsvw83k"
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
100010 | 处理失败| 请重新安装

#### **应用安装**

**接口类型**: 异步接口
**关联回调**: [应用安装任务回调](#应用安装任务回调) (taskBusinessType: `1011`)

为单台或多台实例同时安装单个或多个APP。此接口为异步操作。
增加黑白名单逻辑。

**接口概要**

作用：处理应用安装。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/installApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值                   | 参数类型 | 是否必填 | 参数描述
--- |-----------------------| --- |------| ---
apps |                       | Object[] | 是    | 应用列表
├─appId | 124                   | Integer | 是    | 应用ID
├─appName | 葫芦侠                   | String | 否    | 应用名称
├─pkgName | com.huluxia.gametools | String | 否    | 应用包名
├─isGrantAllPerm | false                 | Boolean | 否    | 是否授予全部权限。`true`授予全部权限/`false`不授予，默认`true`
├─padCodes |                       | String[] | 是    |
├─├─ | AC22010020062         | String | 是    | 实例编号

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
msg | success | String | 响应消息
ts | 1756021167163 | Long |  时间戳
data |  | Object[] |
├─taskId | 1 | Integer |  任务ID
├─padCode | AC22010020062 | String |实例编号
├─vmStatus | 1 | Integer |实例在线状态（0：离线；1：在线）
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "apps":[
  {
   "appId":124,
   "appName":"葫芦侠",
   "pkgName":"com.huluxia.gametools",
   "isGrantAllPerm":false,
   "padCodes":["AC22010020062"]
  }
 ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1717570991004,
 "data": [
  {
   "taskId": 37,
   "padCode": "AC22030010001",
   "vmStatus": 1,
      "taskStatus": 1

  },
  {
   "taskId": 38,
   "padCode": "AC22030010002",
   "vmStatus": 1,
   "taskStatus": 1
  }
 ],
 "traceId": "ewab8qjqbaio"

}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
140005 | 文件不可用 | 查看文件是否存在

#### **应用卸载**

**接口类型**: 异步接口
**关联回调**: [应用卸载任务回调](#应用卸载任务回调) (taskBusinessType: `1009`)

为单台或多台实例同时卸载单个或多个APP。此接口为异步操作。

**接口概要**

作用：处理应用卸载。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/uninstallApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- |------| ---
apps |  | Object[] | 是    | 应用列表
├─appId | 124 | Integer | 否    | 应用ID
├─appName | 葫芦侠 | String | 否    | 应用名称
├─pkgName | com.huluxia.gametools | String | 是    | 应用包名
├─padCodes |  | String[] | 是    |
├─├─ | AC22010020062 | String | 是    | 实例编号

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data | | Object[] |
├─taskId | 2 | Integer |  任务ID
├─padCode | AC22010020062 | String | 实例编号
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "apps":[
  {
   "appId":124,
   "appName":"demo",
   "pkgName":"com.demo",
   "padCodes":["AC22010020062"]
  }
 ]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1717570615524,
  "traceId": "ewab8qjqbaio",
  "data": [
  {
   "taskId": 22,
   "padCode": "AC22030010001",
   "vmStatus": 1,
   "taskStatus": 1
  },
  {
   "taskId": 23,
   "padCode": "AC22030010002",
   "vmStatus": 0,
   "taskStatus": 1
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110007 | 卸载应用失败| 稍后请重试

#### **应用启动**

**接口类型**: 异步接口
**关联回调**: [应用启动任务回调](#应用启动任务回调) (taskBusinessType: `1005`)

根据实例编号和应用包名对实例进行应用启动的操作。

**接口概要**

作用：处理应用启动。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/startApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名      | 示例值       | 参数类型 | 是否必填 | 参数描述 |
| ----------- | ------------ | -------- | -------- | -------- |
|padCodes |  | String[] | 是 | |
|├─ | AC22010020062 | String | 是 | 实例编号|
| pkgName | xxx.test.com | String   | 是       | 包名     |

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
data |  | Object[] |
├─taskId | 1 | Integer | 任务ID
├─padCode | AC22020020793 | String |  实例编号
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "padCodes": [
  "AC22030022693"
 ],
 "pkgName": xxx.test.com
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "traceId": "ewab8qjqbaio",
 "ts": 1717570663080,
 "data": [
  {
   "taskId": 24,
   "padCode": "AC22030010001",
   "vmStatus": 1,
   "taskStatus": 1
  },
  {
   "taskId": 25,
   "padCode": "AC22030010002",
   "vmStatus": 0,
      "taskStatus": 1
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110008 | 启动应用失败 | 重启云机后再启动应用

#### **应用停止**

**接口类型**: 异步接口
**关联回调**: [应用停止任务回调](#应用停止任务回调) (taskBusinessType: `1007`)

根据实例编号和应用包名对实例进行应用停止的操作。

**接口概要**

作用：操作应用停止。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/stopApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes |  | String[] | 是 |
├─ | AC22010020062 | String | 是 | 实例编号
pkgName | xxx.test.com | String   | 是       | 包名

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
ts | 1756021167163 | Long |时间戳
data |  | Object[] |
├─taskId | 1 | Integer |  任务ID
├─padCode | AC22010020062 | String | 实例编号
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "padCodes": [
  "AC22010020062"
 ],
 "pkgName": xxx.test.com
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "traceId": "ewab8qjqbaio",
 "ts": 1717570700415,
 "data": [
  {
   "taskId": 26,
   "padCode": "AC22030010001",
   "vmStatus": 1,
   "taskStatus": 1
  },
  {
   "taskId": 27,
   "padCode": "AC22030010002",
   "vmStatus": 0,
   "taskStatus": 1
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110010 | 停止应用失败 | 重启云机关闭应用

#### **应用重启**

**接口类型**: 异步接口
**关联回调**: 两个回调：[应用停止任务回调](#应用停止任务回调) (taskBusinessType: `1007`) 和 [应用启动任务回调](#应用启动任务回调) (taskBusinessType: `1005`)

根据实例编号和应用包名对实例进行应用重启的操作。

**接口概要**

作用：操作应用重启。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /openapi/open/pad/restartApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
padCodes |  | String[] | 是 |
├─ | AC22010020062 | String | 是 | 实例编号
pkgName | xxx.test.com | String   | 是       | 包名

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
ts | 1756021167163 | Long |  时间戳
data |  | Object[] |
├─taskId | 1 | Integer |  任务ID
├─padCode | AC22010020062 | String | 实例编号
├─vmStatus | 1 | Integer | 实例在线状态。可选值：`0`离线/`1`在线。[详见枚举↗](./EnumReference.md#12-vmstatus---实例在线状态)
├─taskStatus | 1 | Integer | 任务状态（-1：任务已存在，请勿重复提交；1：任务已添加）。[查看所有状态↗](./EnumReference.md#13-taskstatus---任务状态)|

**请求示例**

```javascript
{
 "padCodes": [
  "AC22030022693"
 ],
 "pkgName": xxx.test.com
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "traceId": "ewab8qjqbaio",
 "ts": 1717570855874,
 "data": [
  {
   "taskId": 33,
   "padCode": "AC22030010001",
   "vmStatus": 1,
   "taskStatus": 1
  },
  {
   "taskId": 34,
   "padCode": "AC22030010002",
   "vmStatus": 0,
   "taskStatus": 1
  }
 ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110009 | 重启应用失败 | 重启云机后再启动应用

#### **黑白名单列表**

**接口类型**: 同步接口

分页查询黑白名单列表

**接口概要**

作用：查询黑白名单列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/appClassify/pageList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
classifyName | test | String | 否 | 黑白名单名称(模糊查询)
classifyType | 1 | Integer | 否 | 黑白名单类型。可选值：`1`白名单/`2`黑名单。[详见枚举↗](./EnumReference.md#24-classifytype---黑白名单类型)
page | 1 | Integer | 否 | 页码 默认1
rows | 10 | Integer | 否 | 每页数量 默认10 最大值100

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data |  | Object[] |
├─id | 8 | Integer |  黑白名单id
├─classifyName | 白名单A组1 | String | 黑白名单名称
├─classifyType | 1 | Integer | 黑白名单类型。可选值：`1`白名单/`2`黑名单。[详见枚举↗](./EnumReference.md#24-classifytype---黑白名单类型)
├─appNum | 3 | Integer | 已关联的应用数量
├─remark | 白名单A组测试1 | String | 描述
├─applyAllInstances | false | Boolean | 是否应用所有实例模式。`true`应用所有实例/`false`不应用

**请求示例**

```javascript
{
    "classifyName": "",
    "classifyType": 1,
    "page": 1,
    "rows": 10
}
```

**响应示例**

```javascript
{
     "code": 200,
     "msg": "success",
     "ts": 1735019791977,
     "data": [
          {
               "id": 8,
               "classifyName": "白名单A组1",
               "classifyType": 1,
               "appNum": 3,
               "remark": "白名单A组测试1",
               "applyAllInstances": false
          }
     ]
}
```

#### **黑白名单保存**

保存黑白名单和关联应用，参数id不为null，则表示更新，此操作会覆盖该分类下所有的关联应用

**接口地址**

> /openapi/open/appClassify/save

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
id | 123 | Long | 否 | 黑白名单id(不为空则为修改，为空则新增)
classifyName | 白名单A组 | String | 是 | 黑白名单名称
classifyType | 1 | Integer | 是 | 黑白名单类型。可选值：`1`白名单/`2`黑名单。[详见枚举↗](./EnumReference.md#24-classifytype---黑白名单类型)
applyAllInstances | false | Boolean | 否 | 是否应用所有实例。`true`应用所有实例/`false`不应用，默认`false`
remark | 10 | String | 否 | 黑白名单描述
appInfos |  | Object[] | 否 | 关联应用集合 范围0-500个
├─fileId | 1 | Integer | 否 | 文件id
├─appId | 1 | Integer | 否 |  应用id
├─appName | 测试app | String | 否 |  应用名称
├─packageName | com.xxx.xxx | String | 是 |  包名
├─appVersionNo | 123 | Integer | 否 |  版本号
├─appVersionName | 1.2.3 | String | 否 |  版本名称

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data | 1 | Long | 黑白名单id

**请求示例**

```javascript
{
 "id": null,
 "classifyName": "白名单A组1",
 "classifyType": 1,
    "applyAllInstances": false,
 "remark": "白名单A组测试1",
 "appInfos": [
  {
   "fileId": 1,
   "appId": 1,
   "appName": "测试app",
   "packageName": "com.xxx.xxx",
   "appVersionNo": 123,
   "appVersionName": "1.2.3"
  }
 ]
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": 1
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110080 | 黑白名单不存在 | 黑白名单不存在
110085 | 黑白名单名称重复 | 黑白名单名称重复

**接口概要**

作用：处理黑白名单保存。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

#### **黑白名单详情**

**接口类型**: 同步接口

查询黑白名单详情和关联应用

**接口概要**

作用：查询黑白名单详情。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/appClassify/detail

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Query参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
id | 1 | Integer | 是 | 黑白名单id

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data |  | Object[] |
├─id | 8 | Integer |  黑白名单id
├─classifyName | 白名单A组1 | String | 黑白名单名称
├─classifyType | 1 | Integer | 黑白名单类型。可选值：`1`白名单/`2`黑名单。[详见枚举↗](./EnumReference.md#24-classifytype---黑白名单类型)
├─applyAllInstances | false | Boolean | 是否应用所有实例模式。`true`应用所有实例/`false`不应用
├─appNum | 3 | Integer | 已关联的应用数量
├─remark | 白名单A组测试1 | String | 描述
├─appInfos |  | Object[] | 关联应用集合
├─├─fileId | 1 | Integer | 文件id
├─├─appId | 1 | Integer |  应用id
├─├─appName | 测试app | String |  应用名称
├─├─packageName | com.xxx.xxx | String |  包名
├─├─appVersionNo | 123 | Integer |  版本号
├─├─appVersionName | 1.2.3 | String |  版本名称

**请求示例**

```javascript
{"id":153858}
```

**响应示例**

```javascript
{
     "code": 200,
     "msg": "success",
     "ts": 1735020014142,
     "data": {
          "id": 8,
          "classifyName": "白名单A组1",
          "classifyType": 1,
          "applyAllInstances": false,
          "appNum": 3,
          "remark": "白名单A组测试1",
          "appInfos": [
               {
                    "fileId": 1,
                    "appId": 1,
                    "appName": "测试app",
                    "packageName": "com.xxx.xxx",
                    "appVersionNo": 123,
                    "appVersionName": "1.2.3"
               }
          ]
     }
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110080 | 黑白名单不存在 | 黑白名单不存在

#### **黑白名单实例关联保存**

保存关联实例，此操作会删除该分类下原所有的关联实例

**接口地址**

> /openapi/open/appClassify/padSave

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
id | 123 | Long | 是 | 黑白名单id（从pageList接口获取）
appPadInfos |  | Object[] | 否 | 关联实例集合 范围0-500个
├─padCode | AC32010230001 | String | 是 | 实例编号
├─deviceLevel | m2-4 | String | 否 |  规格
├─padIp | 10.255.3.1 | String | 否 |  实例ip

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data | null |  |

**请求示例**

```javascript
{
 "id": 1,
 "appPadInfos": [
  {
   "padCode": "AC32010230001",
   "deviceLevel": "m2-4",
   "padIp": "10.255.3.1"
  }
 ]
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": null
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110080 | 黑白名单不存在 | 黑白名单不存在

**接口概要**

作用：处理黑白名单实例关联保存。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

#### **黑白名单实例关联详情**

**接口类型**: 同步接口

查询黑白名单详情和关联实例

**接口概要**

作用：查询黑白名单实例关联详情。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/appClassify/padDetail

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Query参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
id | 1 | Integer | 是 | 黑白名单id

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
traceId        | ewc84g8si0oy       | String  | 链路追踪ID |
ts | 1756021167163 | Long |  时间戳
data |  | Object[] |
├─id | 8 | Integer |  黑白名单id
├─classifyName | 白名单A组1 | String | 黑白名单名称
├─classifyType | 1 | Integer | 黑白名单类型。可选值：`1`白名单/`2`黑名单。[详见枚举↗](./EnumReference.md#24-classifytype---黑白名单类型)
├─appNum | 3 | Integer | 已关联的应用数量
├─applyAllInstances |  false     | Boolean  | 是    | 是否应用所有实例模式。`true`应用所有实例/`false`不应用 |
├─appPadInfos |  | Object[] | 关联实例集合
├─├─padCode | AC111 | String | 实例编号
├─├─deviceLevel | m2-3 | String |  规格
├─├─padIp | 127.0.0.1 | String |  实例ip

**请求示例**

```javascript
{"id":153858}
```

**响应示例**

```javascript
{
     "code": 200,
     "msg": "success",
     "ts": 1735020251631,
     "data": {
          "id": 8,
          "classifyName": "白名单A组1",
          "classifyType": 1,
          "appNum": 3,
          "applyAllInstances": false,
          "appPadInfos": [
               {
                    "padCode": "AC111",
                    "deviceLevel": "m2-3",
                    "padIp": "127.0.0.1"
               }
          ]
     },
    "traceId": "ewab8qjqbaio"
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110080 | 黑白名单不存在 | 黑白名单不存在

#### **删除黑白名单**

**接口类型**: 同步接口

删除黑白名单 所关联的应用和实例都会清除

**接口概要**

作用：修改删除黑白名单。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/appClassify/del

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Query参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
id | 1 | Integer | 是 | 黑白名单id

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data | null |  |

**请求示例**

```javascript
{"id":153858}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735020371601,
    "data": null
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110084 | 该黑白名单不存在或已删除 | 该黑白名单不存在或已删除

#### **添加黑白名单App**

添加关联应用，此操作不会覆盖该分类下所有的关联应用，直接添加到分类下

**接口地址**

> /openapi/open/appClassify/addApp

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
id | 123 | Long | 是 | 黑白名单id（从pageList接口获取）
appInfos |  | Object[] | 是 | 关联应用集合 范围1-500个
├─fileId | 1 | Integer | 否 | 文件id
├─appId | 1 | Integer | 否 |  应用id
├─appName | 测试app | String | 否 |  应用名称
├─packageName | com.xxx.xxx | String | 是 |  包名
├─appVersionNo | 123 | Integer | 否 |  版本号
├─appVersionName | 1.2.3 | String | 否 |  版本名称

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data | null |  |

**请求示例**

```javascript
{
 "id": 1,
 "appInfos": [
  {
   "fileId": 1,
   "appId": 1,
   "appName": "测试app",
   "packageName": "com.xxx.xxx",
   "appVersionNo": 123,
   "appVersionName": "1.2.3"
  }
 ]
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": null
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110080 | 黑白名单不存在 | 黑白名单不存在

**接口概要**

作用：修改添加黑白名单App。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

#### **添加黑白名单实例关联**

添加关联实例，此操作不会覆盖该分类下所有的关联实例，直接添加到分类下

**接口地址**

> /openapi/open/appClassify/addPad

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
id | 123 | Long | 是 | 黑白名单id（从pageList接口获取）
appPadInfos |  | Object[] | 是 | 关联实例集合 范围1-500个
├─padCode | AC32010230001 | String | 是  | 实例编号
├─deviceLevel | m2-4 | String | 否  |  规格
├─padIp | 10.255.3.1 | String | 否   |  实例ip

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data | null |  |

**请求示例**

```javascript
{
 "id": 1,
 "appPadInfos": [
  {
   "padCode": "AC32010230001",
   "deviceLevel": "m2-4",
   "padIp": "10.255.3.1"
  }
 ]
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": null
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110080 | 黑白名单不存在 | 黑白名单不存在

**接口概要**

作用：修改添加黑白名单实例关联。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

#### **删除黑白名单关联的实例**

**接口类型**: 同步接口

删除黑白名单关联的实例,即指定实例解绑黑白名单

**接口概要**

作用：修改删除黑白名单关联的实例。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/appClassify/delPad

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
id | 123 | Long | 是 | 黑白名单id（从pageList接口获取）
padCodes |  | String[] | 是 | 关联实例集合 范围1-200个

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer |  状态码
msg | success | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data | null |  |

**请求示例**

```javascript
{
 "id": 100,
 "padCodes": ["AC32010250003"]
}
```

**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": null
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110080 | 黑白名单不存在 | 黑白名单不存在

#### **按实例查询关联的黑白名单**

**接口类型**: 同步接口

按实例查询该实例关联的黑白名单策略组列表

**接口概要**

作用：查询按实例查询关联的黑白名单。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/appClassify/padClassifyList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- |----| ---
padCodes | ["AC32010230001","AC32010230002"] | String[] | 是  | 实例编号集合，数量范围0-100个

**响应参数**

参数名 | 示例值 | 参数类型 | 参数描述
--- | --- | --- | ---
code | 200 | Integer | 状态码
msg | success | String | 响应消息
ts | 1756021167163 | Long | 时间戳
data |  | Object[] | 实例关联黑白名单列表
├─padCode | AC32010230001 | String | 实例编号
├─classifyCount | 2 | Integer | 关联策略组数量
├─classifyList |  | Object[] | 关联策略组明细
├─├─id | 8 | Long | 策略组id
├─├─classifyName | 白名单A组1 | String | 策略组名称
├─├─classifyType | 1 | Integer | 策略组类型 1白名单 2黑名单
├─├─appNum | 3 | Integer | 已关联的应用数量
├─├─padNum | 5 | Integer | 已关联的实例数量
├─├─remark | 白名单A组测试1 | String | 描述
├─├─applyAllInstances | false | Boolean | 是否应用所有实例

**请求示例**

```javascript
{
  "padCodes": [
    "AC32010230001",
    "AC32010230002"
  ]
}
```

**响应示例**

```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1735883927104,
  "data": [
    {
      "padCode": "AC32010230001",
      "classifyCount": 2,
      "classifyList": [
        {
          "id": 8,
          "classifyName": "白名单A组1",
          "classifyType": 1,
          "appNum": 3,
          "padNum": 5,
          "remark": "白名单A组测试1",
          "applyAllInstances": false
        },
        {
          "id": 9,
          "classifyName": "黑名单B组1",
          "classifyType": 2,
          "appNum": 6,
          "padNum": 5,
          "remark": "黑名单B组测试1",
          "applyAllInstances": true
        }
      ]
    },
    {
      "padCode": "AC32010230002",
      "classifyCount": 1,
      "classifyList": [
        {
          "id": 8,
          "classifyName": "白名单A组1",
          "classifyType": 1,
          "appNum": 3,
          "padNum": 5,
          "remark": "白名单A组测试1",
          "applyAllInstances": false
        }
      ]
    }
  ]
}
```

**错误码**

错误码 | 错误说明|操作建议
--- | --- | ---
110028 | 实例不存在 | 检查实例编号是否正确
110042 | 存在不属于当前用户的实例 | 确认实例归属后再重试

#### **应用分类列表**

**接口类型**: 同步接口

分页查询应用分类

**接口概要**

作用：查询应用分类列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/newAppClassify/pageList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值        | 参数类型    | 是否必填 | 参数描述
--- | --- |---------| --- | ---
enable | true       | Boolean | 否 | 是否启用。`true`启用/`false`禁用
page | 1       | Integer | 否 |  页码 默认1
rows | 10 | Integer | 否 |  每页数量 默认10 最大100

**响应参数**

参数名 | 示例值         | 参数类型     | 参数描述
--- |-------------|----------| ---
code | 200         | Integer  |  状态码
msg | success     | String   |  响应消息
ts | 1756021167163 | Long     |  时间戳
data |             | Object[] |
├─id | 3           | Integer  |  应用分类id
├─classifyName | f1          | String   |  应用分类名称
├─appNum | 4           | Integer  |  应用数量
├─enable | true        | Boolean  |  是否启用
├─remark | test        | String   |  描述
├─createBy | admin            | String   |  创建人
├─createTime | 2024-12-27 17:16:20            | String   |  创建时间

**请求示例**

```javascript
{
    "enable":true,
    "page":1,
    "rows":10
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1735883927104,
        "data": [
        {
            "id": 3,
            "classifyName": "f1",
            "appNum": 4,
            "enable": true,
            "remark": "你好",
            "createBy": "admin",
            "createTime": "2024-12-27 17:16:20"
        }
    ]
}
```

#### **应用启停执行结果**

**接口类型**: 同步接口

通过应用启停任务ID来获取实例的应用启停的结果

**接口概要**

作用：执行应用启停执行结果。
关键参数：见请求参数表。
结果：返回任务ID，可用于查询执行结果。

**接口地址**

> /task-center/open/task/appOperateInfo

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
taskIds |  | Integer [] | 是 |
├─ | 1 | Integer | 是 | 任务ID

**响应参数**

参数名 | 示例值           | 参数类型 | 参数描述
--- |---------------| --- | ---
code | 200           | Integer |  状态码
msg | success       | String |  响应消息
ts | 1756021167163 | Long |  时间戳
data |               | Object[] |
├─taskId | 1             | Integer | 任务ID
├─padCode | AC22020020793 | String | 实例编号
├─taskStatus | 3             | Integer |  任务状态（-1：全失败；-2：部分失败；-3：取消；-4：超时；1：待执行；2：执行中；3：完成）
├─endTime | 1756021166163 | Long |  任务执行结束时间
├─taskContent | Success       | String |  任务内容
├─taskResult | Success       | String |  任务结果
├─errorMsg | 实例不存在         |String |  失败的原因|

**请求示例**

```javascript
{
 "taskIds": [1]
}
```

**响应示例**

```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
 "data":[
    {
    "taskId": 1,
    "taskStatus": 3,
    "padCode": "AC22020020793",
    "taskContent": "Success",
    "taskResult": "Success",
    "endTime": 1756121167163,
    "errorMsg": null
    }
   ]
}
```

### 镜像管理

#### **获取镜像列表**

**接口类型**: 同步接口

获取可用镜像列表。

**接口概要**

作用：查询获取镜像列表。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/image/queryImageList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Query参数**

参数名 | 示例值                 | 参数类型    | 是否必填 | 参数描述
--- |---------------------|---------|------| ---
imageType | 1                   | Integer | 否    |镜像类型。可选值：`1`公共镜像/`2`自定义镜像。[详见枚举↗](./EnumReference.md#26-imagetype---镜像类型)
releaseType | 1                   | Integer | 否    |镜像版本。可选值：`1`测试版/`2`正式版。[详见枚举↗](./EnumReference.md#27-releasetype---镜像版本发版版本)
romVersion | android13           | String  | 否    |AOSP版本(android13，android14)
createTimeStart | 2025-03-11 00:00:00 | String  | 否    |创建开始时间(格式为：yyyy-MM-dd HH:mm:ss)
createTimeEnd | 2025-03-11 00:00:00 | String  | 否    |创建结束时间(格式为：yyyy-MM-dd HH:mm:ss)
page | 1                   | Integer | 否    |页码,默认1
rows | 10                  | Integer | 否    |每页条数,默认10,最大100

**响应参数**

| 参数名             | 示例值             | 参数类型 | 参数描述                 |
|-----------------|-----------------| --- |----------------------|
| code            | 200             | Integer | 状态码                  |
| msg             | success         | String | 响应消息                 | | |
| ts              | 1717643679112   | Long | 时间戳                  | |
| data            |                 | Object |                      | |
| ├─records       |                 | Object[] | 记录列表                 | |
| ├─├─imageId     | img-25030796215 | String | 镜像ID                 |
| ├─├─imageName   | 20250307_4      | String | 镜像名称                 |
| ├─├─imageTag    | 20250307_4      | String | 镜像Tag                |
| ├─├─serverType  | Cruise10        | String | SOC类型                |
| ├─├─romVersion  | android13       | String | Rom版本                |
| ├─├─imageDesc   | WIFI自定义版        | String | 描述                   |
| ├─├─releaseType | 1               | Integer | 发版版本 1测试版 2正式版       |
| ├─├─supportF2fs | 1               | Integer | 是否支持f2fs(1:支持 0:不支持) |
| ├─├─fileTag     | 0               | Integer | 文件标签(1:可删除 0:不能删除)   |
| ├─total         |                 | Integer | 总记录条数                | |
| ├─size          |                 | Integer | 每页大小                 | |
| ├─current       |                 | Integer | 当前页码                 | |
| ├─pages         |                 | Integer | 总页数                  | |

**请求示例**

```javascript
{
    "imageType":1,
        "releaseType":1,
        "romVersion":"android13",
        "createTimeStart":"2025-02-11 00:00:00",
        "createTimeEnd":"2025-03-11 00:00:00",
        "page":1,
        "rows":10
}
```

**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1741688704152,
        "data": {
        "records": [
            {
                "imageId": "img-25030796215",
                "imageName": "20250307_4",
                "imageTag": "20250307_4",
                "serverType": "Cruise10",
                "romVersion": "android13",
                "imageDesc": "",
                "releaseType": 1,
                "fileTag": 1,
                "supportF2fs": 1
            }
        ],
            "total": 4,
            "size": 10,
            "current": 1,
            "pages": 1
    }
}
```

### 账户管理

#### **批量新增子账户**

**接口类型**: 同步接口
客户账户用来创建子账户。

**接口概要**

作用：创建批量新增子账户。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/subCustomer/batchAdd

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值           | 参数类型 | 是否必填 | 参数描述
--- |---------------| --- |------| ---
addDTOList |               | Object[]  | 是    | 子账号参数列表(单次新增范围1-30个)
├─ customerAccount | 测试账号1         | String | 是    | 账号
├─ customerName | 测试名称1         | String | 是    | 名称
├─ customerTel | 15580887450 | String | 是    | 联系电话

**响应参数**

| 参数名               | 示例值                              | 参数类型     | 参数描述    |
|-------------------|----------------------------------|----------|---------|
| code              | 200                              | Integer  | 状态码     |
| msg               | success                          | String   | 响应消息    | | |
| ts                | 1760097337371                    | Long     | 时间戳     | |
| data              |                                  | Object[] | 子账户信息   | |
| ├─id              | 972                               | Long     | 子账户主键ID |
| ├─customerAccount | 测试账号1@zeng                       | String   | 子账户登录账号 |
| ├─password        | o32kqvn152nj                     | String   | 子账户登录密码 | |
| ├─accessKeyId     | jxurdk0uptvm2ztt3urs57jx2o2p4824 | String   | 子账户AK   | |
| ├─secretAccessKey | n927izl0bkonsw7znh6c5vns         | String   | 子账户SK   | |
| ├─errorMsg        | 系统异常                             | String   | 错误信息    | |

**请求示例**

```javascript
{
    "addDTOList": [
        {
            "customerName": "子账号名称1",
            "customerAccount": "测试账号1",
            "customerTel": "15580887450"
        },
        {
            "customerName": "子账号名称2",
            "customerAccount": "测试账号2",
            "customerTel": "15580887459"
        }
    ]
}
```
**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1760097337371,
        "data": [
        {
            "id": 972,
            "customerAccount": "测试账号1@zeng",
            "password": "o32kqvn152nj",
            "accessKeyId": "jxurdk0uptvm2ztt3urs57jx2o2p4824",
            "secretAccessKey": "n927izl0bkonsw7znh6c5vns",
            "errorMsg": null
        },
        {
            "id": 973,
            "customerAccount": "测试账号2@zeng",
            "password": "l63g1dtoujbs",
            "accessKeyId": "gia3tj3lvtdfiiw6m5i2pmmqkzuejstt",
            "secretAccessKey": "1pwk6pxvm59fjaefvrjy8b6i",
            "errorMsg": null
        }
    ]
}
```

#### **子账户列表分页查询**

**接口类型**: 同步接口
分页查询客户账户下面的子账户。

**接口概要**

作用：查询子账户列表分页查询。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/subCustomer/pageList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值                | 参数类型 | 是否必填 | 参数描述
--- |--------------------| --- |--| ---
page | 1                  | Integer | 是 | 页码
rows | 10                 | Integer | 是 | 条数
status | 1                  | Integer |否 | 启用状态：0-禁用；1-启用
customerAccount | 测试账号1    | String | 否 | 客户账号
customerTel | 15580887450         | String | 否 | 客户电话

**响应参数**

| 参数名               | 示例值                              | 参数类型     | 参数描述    |
|-------------------|----------------------------------|----------|---------|
| code              | 200                              | Integer  |         |
| msg               | success                          | String   |         |
| ts                | 1713773577581                    | Long     |         |
| data              |                                  | Object   |         |
| ├─page            | 1                                | Integer  | 当前页     |
| ├─rows            | 10                               | Integer  | 每页的数量   |
| ├─size            | 1                                | Integer  | 当前页的数量  |
| ├─total           | 1                                | Integer  | 总记录数    |
| ├─totalPage       | 1                                | Integer  | 总页数     |
| ├─pageData        |                                  | object[] | 列表      |
| ├─├─id            | 972                              | Integer  | 主键id    |
| ├─├─customerAccount     | 测试账号1@zeng                       | String   | 子账户登录账号 |
| ├─├─subCustomerPassword     | o32kqvn152nj                     | String   | 子账户登录密码 |
| ├─├─customerName   | 子账号名称1                           | String   | 子账户名称   |
| ├─├─customerTel       | 15580887450                      | String   | 子账户电话   |
| ├─├─accessKeyId      | jxurdk0uptvm2ztt3urs57jx2o2p4824 | String   | 子账户AK   |
| ├─├─secretAccessKey         | n927izl0bkonsw7znh6c5vns         | String   | 子账户SK   |
| ├─├─status         | 1                                | Interge  | 启用状态：0-禁用；1-启用   |

**请求示例**

```javascript
{
    "page": 1,
    "rows": 10,
    "status": 1,
    "customerAccount": "测试账号1",
    "customerTel": "15580887450"
}
```
**响应示例**

```javascript
{
    "code": 200,
        "msg": "success",
        "ts": 1760152734156,
        "data": {
        "page": 1,
            "rows": 10,
            "size": 1,
            "total": 1,
            "totalPage": 1,
            "pageData": [
            {
                "id": 972,
                "customerAccount": "测试账号1@zeng",
                "subCustomerPassword": "o32kqvn152nj",
                "customerName": "子账号名称1",
                "customerTel": 15580887450,
                "status": 1,
                "accessKeyId": "jxurdk0uptvm2ztt3urs57jx2o2p4824",
                "secretAccessKey": "n927izl0bkonsw7znh6c5vns"
            }
        ]
    }
}
```

#### **子账户批量删除**

**接口类型**: 同步接口
批量删除客户账户下面的子账户。

**接口概要**

作用：修改子账户批量删除。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/subCustomer/batchDelete

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

| 参数名      | 示例值   | 参数类型    | 是否必填 | 参数描述                          |
| -------- |-------|---------| ---- |-------------------------------|
| ids | [972] | Long[]  | 是    | 需要删除的子账户主键ID        |

**响应参数**

| 参数名               | 示例值                              | 参数类型     | 参数描述    |
|-------------------|----------------------------------|----------|---------|
| code              | 200                              | Integer  | 状态码     |
| msg               | success                          | String   | 响应消息    | | |
| ts                | 1760154208875                    | Long     | 时间戳     | |

**请求示例**

```javascript
{
    "ids": [972]
}
```
**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1760154208875
}
```

#### **主账号板卡列表分页查询**

**接口类型**: 同步接口
分页查询客户账号下拥有的板卡列表。

**接口概要**

作用：查询主账号板卡列表分页查询。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/subCustomer/resource/masterCustomer/pageList

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值             | 参数类型 | 是否必填 | 参数描述
--- |-----------------| --- |--| ---
page | 1               | Integer | 是 | 页码
rows | 10              | Integer | 是 | 条数
netStorageResFlag | 1               | Integer |否 | 网存板卡标记。可选值：`0`本地板卡/`1`网存板卡/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记)
deviceCode | ACD250411WU3CF2U | String | 否 | 板卡编号
deviceCreatePadStatus | 1       | Integer | 否 | 板卡实例状态。可选值：`-1`未创建实例/`0`所有板卡(默认)/`1`已创建实例。[详见枚举↗](./EnumReference.md#115-devicecreatepadstatus---板卡实例状态)

**响应参数**

| 参数名             | 示例值              | 参数类型     | 参数描述                   |
|-----------------|------------------|----------|------------------------|
| code            | 200              | Integer  | 状态码                    |
| msg             | success          | String   | 响应消息                   | | |
| ts              | 1760097337371    | Long     | 时间戳                    | |
| data            |                  | Object[] | 板卡信息                   | |
| ├─deviceId              | 12376            | Long     | 板卡主键ID                 |
| ├─deviceCode | ACD250411WU3CF2U | String   | 板卡编号                   |
| ├─netStorageResFlag      | 1                | Integer  | 网存板卡标记。可选值：`0`本地板卡/`1`网存板卡/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记)   | |
| ├─deviceCreatePadStatus      | 1         | Integer  | 板卡实例状态 -1未创建实例 1 已创建实例 | |

**请求示例**

```javascript
{
     "page": 1,
     "rows": 10,
     "netStorageResFlag":1,
     "deviceCode":"ACD250411WU3CF2U",
     "deviceCreatePadStatus":1
}
```
**响应示例**

```javascript
{
        "code": 200,
        "msg": "success",
        "ts": 1760163320924,
        "data": [
        {
            "deviceCreatePadStatus":1,
            "deviceCode": "ACD250411WU3CF2U",
            "deviceId": 12376,
            "netStorageResFlag": 1
        }
    ]
}
```

#### **子账号板卡列表查询**

**接口类型**: 同步接口
客户账户查询其子账户下被分配的板卡列表。

**接口概要**

作用：查询子账号板卡列表查询。
关键参数：见请求参数表。
结果：返回结果列表/分页数据。

**接口地址**

> /openapi/open/subCustomer/resource/list

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值            | 参数类型    | 是否必填 | 参数描述
--- |----------------|---------|------| ---
subCustomerId | 862            | Long    | 是    | 子账户主键ID
netStorageResFlag | 1              | Integer | 否    | 网存板卡标记。可选值：`0`本地板卡/`1`网存板卡/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记)
deviceCode | ACD250411WU3CF2U | String  | 否    | 板卡编号

**响应参数**

| 参数名             | 示例值              | 参数类型     | 参数描述    |
|-----------------|------------------|----------|---------|
| code            | 200              | Integer  | 状态码     |
| msg             | success          | String   | 响应消息    | | |
| ts              | 1760097337371    | Long     | 时间戳     | |
| data            |                  | Object[] | 板卡信息    | |
| ├─deviceId              | 12376            | Long     | 板卡主键ID  |
| ├─deviceCode | ACD250411WU3CF2U | String   | 板卡编号 |
| ├─netStorageResFlag      | 1                | Integer  | 网存板卡标记。可选值：`0`本地板卡/`1`网存板卡/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记) | |

**请求示例**

```javascript
{
     "subCustomerId":862,
     "netStorageResFlag":1,
     "deviceCode":"ACD250411WU3CF2U"
}
```
**响应示例**

```javascript
{
        "code": 200,
        "msg": "success",
        "ts": 1760163320924,
        "data": [
        {
            "deviceCode": "ACD250411WU3CF2U",
            "deviceId": 12376,
            "netStorageResFlag": 1
        }
    ]
}
```

#### **子账号板卡授权**

**接口类型**: 同步接口
客户账户对其下某个子账户授权板卡。

**接口概要**

作用：处理子账号板卡授权。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。

**接口地址**

> /openapi/open/subCustomer/resource/allocate

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值     | 参数类型   | 是否必填 | 参数描述
--- |---------|--------|------| ---
subCustomerId | 862     | Long   | 是    | 需要授权板卡的子账户主键ID
allocateDeviceIds | [12376] | Long[] | 是    | 需要授权的板卡ID集合

**响应参数**

| 参数名               | 示例值                              | 参数类型     | 参数描述    |
|-------------------|----------------------------------|----------|---------|
| code              | 200                              | Integer  | 状态码     |
| msg               | success                          | String   | 响应消息    | | |
| ts                | 1760154208875                    | Long     | 时间戳     | |

**请求示例**

```javascript
{
    "subCustomerId": 862,
     "allocateDeviceIds": [
        12376
    ]
}
```
**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1760168978928
}
```

#### **子账号板卡解绑**

客户账户对其下某个子账户授权的板卡进行解绑。解绑成功后板卡重新归属到客户账户。

**接口地址**

> /openapi/open/subCustomer/resource/unbind

**请求方式**

> POST

**请求数据类型**

> application/json

**请求Body参数**

参数名 | 示例值     | 参数类型   | 是否必填 | 参数描述
--- |---------|--------|------| ---
subCustomerId | 862     | Long   | 是    | 需要解绑板卡的子账户主键ID
unbindDeviceIds | [12376] | Long[] | 是    | 需要解绑的板卡ID集合

**响应参数**

| 参数名               | 示例值                              | 参数类型     | 参数描述    |
|-------------------|----------------------------------|----------|---------|
| code              | 200                              | Integer  | 状态码     |
| msg               | success                          | String   | 响应消息    | | |
| ts                | 1760154208875                    | Long     | 时间戳     | |

**请求示例**

```javascript
{
     "subCustomerId": 862,
     "unbindDeviceIds": [
        12376
    ]
}
```
**响应示例**

```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1760168978928
}
```

**接口概要**

作用：处理子账号板卡解绑。
关键参数：见请求参数表。
结果：返回处理结果与状态信息。
