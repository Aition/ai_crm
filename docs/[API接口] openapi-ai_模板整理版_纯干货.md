# 接口文档（结构化整理版）
### 接口限流规则
| 用户类型 | QPS限制（每秒） | 每分钟限制 | 计算方式 |
|---------|----------------|------------|----------|
| **测试用户** | 200次/秒 | 5,000次/分钟 | 滑动窗口，Access Key级别 |
| **付费用户** | 2,000次/秒 | 30,000次/分钟 | 滑动窗口，Access Key级别 |
- 每个Access Key独立计算限流，不同Key之间不共享额度
- 单个Access Key下所有接口调用共享同一个限流额度
- 必须同时满足QPS和每分钟两个维度的限制
```json
{
  "msg": "Too many requests. Please try again later..",
  "code": 429,
  "data": null
}
```
| 响应头 | 说明 | 示例 |
|--------|------|------|
| `X-RateLimit-Limit` | 当前限流周期的请求上限，根据限流类型而定 | 200 |
| `X-RateLimit-Remaining` | 当前限流周期剩余可用请求数 | 150 |
| `X-RateLimit-Reset` | 当前限流周期重置时间戳（Unix时间戳） | 1618900361 |
| `X-RateLimit-Type` | 触发的限流类型 | qps |
### 分页查询说明
| 参数 | 类型 | 说明 | 推荐默认值 |
|------|------|------|-----------|
| page | Integer | 页码，从1开始 | 1 |
| rows | Integer | 每页数量，取值范围1-1000 | **100** |
| 参数 | 类型 | 说明 | 推荐默认值 |
|------|------|------|-----------|
| lastId | Long | 上次查询返回的最后一条记录ID，首次查询传null或0 | null |
| rows | Integer | 每页数量，取值范围1-1000 | **100** |
- **默认每页数量使用 100**，在确有需要时可适当调大，但不建议超过 500
- 如需获取全部数据，请循环翻页直到 `hasNext` 为 false 或返回数据量小于 rows
- 游标分页（lastId方式）性能优于传统分页，大数据量场景建议优先使用
### 同步与异步接口判断
返回包含 taskId 字段为异步接口；code=200 仅代表提交成功，结果以回调为准。
### 枚举值参考文档
| 分类 | 参数数量 | 说明 |
|------|---------|------|
| **Status状态类** | 15个 | 实例状态、任务状态、设备状态等 |
| **Type类型类** | 17个 | 实例类型、策略类型、镜像类型等 |
| **Flag标记类** | 7个 | 网存标记、删除标记等 |
| **Boolean布尔类** | 5个 | 启用状态、在线状态等 |
| **其他** | 3个 | 国家编码、查询范围等 |
### 回调机制说明（重要）
- **异步任务结果通知**：所有异步接口（实例开关机、重启、重置、应用安装/卸载、文件上传等）执行完成后，平台会主动将结果通过回调推送到您配置的地址，包含 `taskId`、`taskStatus`、`taskResult` 等信息
- **实例状态变更通知**：实例状态发生变化时（如启动完成、关机、异常等），平台会主动推送实例状态回调，包含实例当前状态 `padStatus` 和连接状态 `padConnectStatus`，**无需轮询查询实例状态**
- **订阅事件通知**：支持订阅应用启动/停止等事件，事件触发时主动推送通知
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
### SDK Token签发
#### 获取SDK临时Token
方法：GET
URL：/openapi/open/token/stsToken
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 获取SDK临时Token(根据padCode)
方法：POST
URL：/openapi/open/token/stsTokenByPadCode
必填参数：padCode
请求参数：
|参数名 | 示例值 | 参数类型   | 是否必填 | 参数描述   |
|--- |-----|--------| --- |--------|
|padCode | ACXXXXX | String | 是 | 实例code |
请求示例：
```javascript
{"padCode":"AC32010230001"}
```
响应示例：
```javascript
{"code":200,"msg":"success","ts":1735209109185,"data":{"token":"xxx-xxx-xxx-xxxx"}}
```
错误码：
无
#### 清除SDK授权Token
方法：POST
URL：/openapi/open/token/clearStsToken
必填参数：token
请求参数：
|参数名 | 示例值 | 参数类型   | 是否必填 | 参数描述|
|--- |-----|--------| --- | --- |
|token | 123 | String | 是 | |
请求示例：
无
响应示例：
```javascript
{
 "code": 200,
 "msg": "success",
 "ts":1713773577581,
 "data": null
}
```
错误码：
无
#### 清除SDK临时Token(根据padCode)
方法：POST
URL：/openapi/open/token/clearStsTokenByPadCode
必填参数：padCode
请求参数：
|参数名 | 示例值 | 参数类型   | 是否必填 | 参数描述   |
|--- |-----|--------| --- |--------|
|padCode | ACXXXXX | String | 是 | 实例code |
请求示例：
无
响应示例：
```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1757656454505,
  "data": null,
  "traceId": "extrgsyx962o"
}
```
错误码：
无
### 板卡管理
#### 板卡列表
方法：POST
URL：/openapi/open/device/list
必填参数：无
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
#### 查询算力使用情况
方法：POST
URL：/openapi/open/device/computeUsage
必填参数：无
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | --- | --- | --- |
| queryRange | 0 | Integer | 否 | 查询范围。可选值：`0`主账号及全部子账号/`1`仅自身(默认)/`2`指定子账号列表 |
| subCustomerIds | [862, 863] | Long[] | 否 | 子账号ID列表，`queryRange=2` 时必填 |
请求示例：
```javascript
{
  "queryRange": 0
}
```
响应示例：
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
错误码：
无
#### 板卡重启
方法：POST
URL：/openapi/open/device/powerReset
必填参数：deviceIps、├─、type
请求参数：
| 参数名  | 示例值        | 参数类型 | 是否必填 | 参数描述              |
| ------- | ------------- | -------- | -------- |-------------------|
|deviceIps |  | String[] | 是 |                   |
|├─ | 172.31.4.124 | String | 是 | 物理设备IP            |
|type | 2 | String[] | 是 | 重启类型 1：硬重启 2：断电重启 |
请求示例：
```javascript
{
 "deviceIps": [
  "172.31.4.124"
 ],
 "type":2
}
```
响应示例：
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
错误码：
无
#### 重置板卡
方法：POST
URL：/openapi/open/device/resetDevice
必填参数：无
请求参数：
| 参数名               | 示例值 | 参数类型 | 参数描述                                            |
|-------------------| -- | --- |-------------------------------------------------|
| code              | 200 | Integer |           响应码                                      |
| msg               | success | String ||
| ts                | 1713773577581 | Long ||
| data                | 1个板卡删除实例！ | String |消息内容|
请求示例：
```javascript
{
    "deviceIps": [
        "172.31.3.3"
    ],
        "remark": "1"
}
```
响应示例：
```javascript
{
    "msg": "success",
        "code": 200,
        "data": "1个板卡删除实例！",
        "ts": 1739954448827
}

```
错误码：
无
#### 查询最新预热成功镜像
方法：GET
URL：/openapi/open/device/getLatestWarmupSuccessImages
必填参数：无
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | --- | --- | --- |
| customerId | 178 | Long | 否 | 客户ID（管理员可传此参数查询指定客户的镜像，普通用户忽略此参数） |
请求示例：
```javascript
/openapi/open/device/getLatestWarmupSuccessImages
```
响应示例：
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
错误码：
无
### 网存2.0
#### 一、网存2.0对比网存1.0
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 二、快速入门
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 三、API 接口
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 创建网存实例
方法：`POST`
URL：`/openapi/open/pad/v2/net/storage/res/create`
必填参数：clusterCode、specificationCode、imageId、number、storageSize
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
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
| 220009 | 当前集群存储容量不足,请联系管理员  | 联系管理员增加存储容量或删除清理实例               |
| 110077 | 获取实例MAC失败，请重试      | 稍后重试或联系管理员                       |
#### 网存实例批量开机
方法：`POST`
URL：`/openapi/open/pad/v2/net/storage/batch/boot/on`
必填参数：padCodes
请求参数：
| 参数名         | 示例值                                                 | 参数类型    | 是否必填 | 参数描述                                                                                                                                                                      |
| ----------- |-----------------------------------------------------|---------| ---- |---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| padCodes    | ["ACN250321HRKNE3F", "ACN250321HRKNE3G"]            | String[] | 是    | 需要开机的实例编码列表，数量范围1-200个                                                                                                                                                    |
| dns         | 8.8.8.8                                             | String  | 否    | DNS配置                                                                                                                                                                     |
| countryCode | SG                                                  | String  | 否    | 国家编码，默认值`SG`。 仅实例首次开机时生效，未传入时使用创建实例时传入的国家编码（为空则默认为SG）。[查看所有国家编码↗](./EnumReference.md#51-countrycode---国家编码) |
| androidProp | {"persist.sys.cloud.wifi.mac": "D2:48:83:70:66:0B"} | Object  | 否    | 安卓属性配置，参考 [安卓改机属性列表](https://docs.armcloud.net/cn/server/InstanceAndroidPropList.html)（注意： 时区、语言、国家三个属性目前不生效 ）                                   |
| timeout     | 1800                                                | Integer | 否    | 超时时间（秒），范围300-7200秒（5分钟-120分钟）                                                                                                                                            |
| imageId     | img-25081965158                                      | String  | 否    | 镜像ID，支持开机时更换镜像ID，每次开机传入时均可生效。注意仅支持同版本镜像                                                                                                          |
请求示例：
``` json
{
  "padCodes": ["ACN250321HRKNE3F", "ACN250321HRKNE3G"],
  "dns": "8.8.8.8",
  "countryCode": "US",
  "androidProp": {"persist.sys.cloud.wifi.mac": "D2:48:83:70:66:0B"},
  "timeout": 1800
}
```
响应示例：
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
错误码：
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
#### 网存实例批量关机
方法：`POST`
URL：`/openapi/open/pad/v2/net/storage/batch/off`
必填参数：padCodes
请求参数：
| 参数名      | 示例值                                      | 参数类型 | 是否必填 | 参数描述                                                                                                                    |
|----------|------------------------------------------|---------|------|-------------------------------------------------------------------------------------------------------------------------|
| padCodes | ["ACN250321HRKNE3F", "ACN250321HRKNE3G"] | String[] | 是    | 需要关机的实例编码列表，最多允许同时关机200个实例                                                                                              |
| timeout  | 1800                                     | Integer | 否    | 超时时间（秒），范围：300-7200秒（5分钟-120分钟）                                                                                         |
| forceDel | false                                    | Boolean  | 否    | **请谨慎使用** 是否强制删除。`true`强制删除（直接关机并删除实例，不保留数据）/`false`不强制删除，默认`false`（CBS版本2.3.5以上支持）|
请求示例：
``` json
{
  "padCodes": ["ACN250321HRKNE3F", "ACN250321HRKNE3G"],
  "timeout": 1800
}
```
响应示例：
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
错误码：
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
#### 网存实例批量删除
方法：`POST`
URL：`/openapi/open/pad/v2/net/storage/batch/delete`
必填参数：padCodes
请求参数：
| 参数名      | 示例值                                      | 参数类型     | 是否必填 | 参数描述                           |
| -------- | ---------------------------------------- | -------- | ---- | ------------------------------ |
| padCodes | ["ACN250321HRKNE3F", "ACN250321HRKNE3G"] | String[] | 是    | 需要删除的实例编码列表，数量范围1-200个         |
| timeout  | 1800                                     | Integer  | 否    | 超时时间（秒），范围300-7200秒（5分钟-120分钟） |
请求示例：
``` json
{
  "padCodes": ["ACN250321HRKNE3F", "ACN250321HRKNE3G"],
  "timeout": 1800
}
```
响应示例：
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
错误码：
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
#### 网存实例克隆
方法：POST
URL：/openapi/open/pad/v2/net/storage/clone
必填参数：padCode、number
请求参数：
| 参数名     | 示例值              | 参数类型    | 是否必填 | 参数描述          |
| ------- | ---------------- | ------- | ---- | ------------- |
| padCode | ACN250321HRKNE3F | String  | 是    | 需要克隆的原始实例编码   |
| number  | 2                | Integer | 是    | 克隆数量，范围1-100个 |
请求示例：
``` json
{
    "padCode": "ACN250321HRKNE3F",
    "number": 2,
    "remark": "测试克隆"
}
```
响应示例：
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
错误码：
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
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 分页查询应用安全策略组列表
方法：`POST`
URL：`/openapi/open/appSecurityPolicyGroup/pageList`
必填参数：rows
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| policyName | 测试策略组 | String | 否 | 策略组名称（模糊查询） |
| policyType | 0 | Integer | 否 | 策略组类型。可选值：`0`黑名单/`1`白名单。[详见枚举↗](./EnumReference.md#23-policytype---策略组类型) |
| lastId | 0 | Long | 否 | 上次查询的最后一条记录ID，首次查询传null或0 |
| rows | 10 | Integer | 是 | 查询数量，范围1-1000，默认10 |
请求示例：
```json
{
  "policyName": "测试",
  "policyType": 0,
  "lastId": 0,
  "rows": 10
}
```
响应示例：
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
错误码：
无
#### 查询应用安全策略组详情
方法：`POST`
URL：`/openapi/open/appSecurityPolicyGroup/detail`
必填参数：id
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| id | 123 | Long | 是 | 策略组ID |
请求示例：
```
POST /openapi/open/appSecurityPolicyGroup/detail?id=123
```
响应示例：
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
错误码：
无
#### 新增/更新应用安全策略组
方法：`POST`
URL：`/openapi/open/appSecurityPolicyGroup/save`
必填参数：policyName、policyType
请求参数：
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
请求示例：
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
响应示例：
```json
{
  "msg": "success",
  "code": 200,
  "data": 123,
  "ts": 1742536327373
}
```
错误码：
无
#### 删除应用安全策略组
方法：`POST`
URL：`/openapi/open/appSecurityPolicyGroup/delete`
必填参数：id
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| id | 123 | Long | 是 | 策略组ID |
请求示例：
```
POST /openapi/open/appSecurityPolicyGroup/delete?id=123
```
响应示例：
```json
{
  "msg": "success",
  "code": 200,
  "data": null,
  "ts": 1742536327373
}
```
错误码：
无
#### 实例更换策略组
方法：`POST`
URL：`/openapi/open/appSecurityPolicyGroup/changePadPolicyGroups`
必填参数：padCode、policyGroupIds
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| padCode | ACN1234567890123 | String | 是 | 实例编号 |
| policyGroupIds | [123, 456] | Long[] | 是 | 策略组ID集合（最多100个） |
请求示例：
```json
{
  "padCode": "ACN1234567890123",
  "policyGroupIds": [123, 456]
}
```
响应示例：
```json
{
  "msg": "success",
  "code": 200,
  "data": null,
  "ts": 1742536327373
}
```
错误码：
无
#### 查询实例关联策略组
方法：`POST`
URL：`/openapi/open/appSecurityPolicyGroup/queryPadPolicyGroups`
必填参数：padCodes
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| padCodes | ["ACN1234567890123", "ACN1234567890124"] | String[] | 是 | 实例编号集合 |
请求示例：
```json
{
  "padCodes": ["ACN1234567890123", "ACN1234567890124"]
}
```
响应示例：
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
错误码：
无
#### 策略组追加更新
方法：`POST`
URL：`/openapi/open/appSecurityPolicyGroup/appendRelations`
必填参数：policyGroupId
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| policyGroupId | 123 | Long | 是 | 策略组ID |
| appInfos | [{...}] | Array | 否 | 应用信息列表（最多100个），每个应用信息appId和packageName二选一 |
| ├─ appInfos[].appId | 789 | Long | 否 | 应用ID（appId和packageName二选一） |
| ├─ appInfos[].packageName | com.test.app | String | 否 | 包名（appId和packageName二选一）同时存在时以有效appId为准 |
| padCodes | ["ACN1234567890123"] | String[] | 否 | 实例编号集合（最多100个） |
请求示例：
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
响应示例：
```json
{
  "msg": "success",
  "code": 200,
  "data": null,
  "ts": 1742536327373
}
```
错误码：
无
#### 策略组删除应用/实例
方法：`POST`
URL：`/openapi/open/appSecurityPolicyGroup/removeRelations`
必填参数：policyGroupId
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--------|--------|----------|----------|----------|
| policyGroupId | 123 | Long | 是 | 策略组ID |
| appInfos | [{...}] | Array | 否 | 应用信息列表（最多100个），每个应用信息appId和packageName二选一 |
| ├─ appInfos[].appId | 789 | Long | 否 | 应用ID（appId和packageName二选一） |
| ├─ appInfos[].packageName | com.test.app | String | 否 | 包名（appId和packageName二选一）同时存在时以有效appId为准 |
| padCodes | ["ACN1234567890123"] | String[] | 否 | 实例编号集合（最多100个） |
请求示例：
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
响应示例：
```json
{
  "msg": "success",
  "code": 200,
  "data": null,
  "ts": 1742536327373
}
```
错误码：
无
### 网存1.0
#### 创建网存实例
方法：POST
URL：/openapi/open/pad/net/storage/res/create
必填参数：无
请求参数：
| ├─padCode | ACN250424UPHQOTG                    |Integer | 实例编号         |
| ├─screenLayoutCode | realdevice_1440x3120x560            |String | 屏幕布局编号       |
| ├─netStorageResId | “ZSC250424G4S6RH1-ACN250424UPHQOTG” |String | 网存code       |
| ├─deviceLevel | “m2-4”                              |String | 实例规格         |
| ├─clusterCode | “006”                               |String | 集群编号         |
请求示例：
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
响应示例：
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
错误码：
无
#### 网存实例开机
方法：POST
URL：/openapi/open/pad/net/storage/on
必填参数：无
请求参数：
无
请求示例：
```json
{
  "clusterCode": "001",
  "padCodes": ["ACN250321HRKNE3F"],
   "countryCode":"US",
   "androidProp": "{\"persist.sys.cloud.wifi.mac\": \"D2:48:83:70:66:0B\"}"
}
```
响应示例：
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
错误码：
无
#### 网存实例关机
方法：POST
URL：/openapi/open/pad/net/storage/off
必填参数：无
请求参数：
无
请求示例：
```json
{
  "clusterCode": "001",
  "padCodes": ["ACN250321HRKNE3F"]
}
```
响应示例：
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
错误码：
无
#### 删除网存实例
方法：POST
URL：/openapi/open/pad/net/storage/delete
必填参数：无
请求参数：
无
请求示例：
```json
{
  "clusterCode": "",
  "padCodes": ["ACN250321GYWUP8J"]
}
```
响应示例：
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
错误码：
无
#### 查询网存集群详情
方法：POST
URL：/openapi/open/pad/net/detail/storageCapacity/available
必填参数：无
请求参数：
无
请求示例：
```json
{
  "clusterCode": "002"
}
```
响应示例：
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
错误码：
无
#### 设置网存集群板卡规格
方法：POST
URL：/openapi/open/device/net/setDeviceLevel
必填参数：无
请求参数：
无
请求示例：
```json
{
  "deviceCodes": ["ACD250320R4I7OLM", "ACD250320UEH4OV3"],
  "deviceLevel": "m2-8"
}
```
响应示例：
```json
{
  "msg": "success",
  "code": 200,
  "data": "",
  "ts": 1742526263389
}
```
错误码：
无
#### 网存存储备份
方法：POST
URL：/openapi/open/pad/net/storage/pad/backup
必填参数：无
请求参数：
无
请求示例：
```json
{
  "padCodes": [
    "ACN250403SFPIB1N"
  ],
  "remark": "谷歌验证已经登录"
}
```
响应示例：
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
错误码：
无
#### 指定网存ID的网存实例开机(还原)
方法：POST
URL：/openapi/open/pad/net/storage/specifiedCode/on
必填参数：无
请求参数：
无
请求示例：
```json
{
  "clusterCode": "001",
  "padCode": "ACN250403FKAX2HX",
  "netStorageResUnitCode": "ZSC250403MMGUFGN-ACN250403ZIMD9KJ",
   "countryCode":"US",
   "androidProp": "{\"persist.sys.cloud.wifi.mac\": \"D2:48:83:70:66:0B\"}"
}
```
响应示例：
```json
{
  "clusterCode": "001",
  "padCode": "ACN250403FKAX2HX",
  "netStorageResUnitCode": "ZSC250403MMGUFGN-ACN250403ZIMD9KJ"
}
```
错误码：
无
#### 网存存储删除
方法：
URL：POST /openapi/open/pad/net/storage/pad/delete
必填参数：netStorageResUnitCodes
请求参数：
| 参数名                   | 示例值                                          | 参数类型     | 是否必填 | 参数描述                     |
|------------------------|----------------------------------------------|------------|---------|----------------------------|
| netStorageResUnitCodes | `["ZSC250407XLYILP4-ACN250407XRY4CW9"]`       | List&lt;String&gt; | 是      | 需要删除的网存存储资源编号列表，最多支持 200 个 |
请求示例：
```json
{
  "netStorageResUnitCodes": [
    "ZSC250407XLYILP4-ACN250407XRY4CW9"
  ]
}
```
响应示例：
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
错误码：
无
#### 获取网存实例使用详情
方法：
URL：POST /openapi/open/pad/netPad/group/deviceLevel
必填参数：clusterCode
请求参数：
| 参数名        | 示例值   | 参数类型 | 是否必填 | 参数描述                     |
|-------------|--------|--------|---------|----------------------------|
| clusterCode | "001"  | String | 是      | 集群编码                    |
请求示例：
```json
{
  "clusterCode": "001"
}
```
响应示例：
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
错误码：
无
#### 网存存储详情查询
方法：
URL：POST /openapi/open/netStorage/resUnit/net/storage/pad/resUnit
必填参数：page、rows
请求参数：
| 参数名    | 示例值  | 参数类型 | 是否必填 | 参数描述                 |
|---------|--------|--------|---------|------------------------|
| page    | 3      | Integer | 是      | 当前页码                |
| rows    | 10     | Integer | 是      | 每页显示条数            |
请求示例：
```json
{
  "page": 3,
  "rows": 10
}
```
响应示例：
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
错误码：
无
### 实例管理
#### 修改实例WIFI属性
方法：POST
URL：/openapi/open/pad/setWifiList
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 实例详情
方法：POST
URL：/openapi/open/pad/padDetails
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 实例详情-精简版
方法：POST
URL：/openapi/open/pad/padBaseInfoList
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 实例重启
方法：POST
URL：/openapi/open/pad/restart
必填参数：padCodes、├─
请求参数：
| 参数名  | 示例值        | 参数类型    | 是否必填 | 参数描述      |
| ------- | ------------- |---------|------|-----------|
|padCodes |  | String[] | 是    |           |
|├─ | AC21020010001 | String  | 是    | 实例编号      |
|groupIds |  | Integer[] | 否    |           |
|├─ | 1 | Integer | 否    | 实例组ID     |
请求示例：
```javascript
{
 "padCodes": [
  "AC22030022693"
 ],
 "groupIds": [1]
}
```
响应示例：
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
错误码：
无
#### 实例重置
方法：POST
URL：/openapi/open/pad/reset
必填参数：padCodes、├─
请求参数：
| 参数名   | 示例值         | 参数类型  | 是否必填 | 参数描述   |
| -------- | -------------- | --------- | -------- | ---------- |
| padCodes |                | String[]  | 是       |            |
| ├─       | AC21020010001  | String    | 是       | 实例编号   |
| groupIds |                | Integer[] | 否       |            |
| ├─       | 1              | Integer   | 否       | 实例组ID   |
请求示例：
```javascript
{
 "padCodes": [
  "AC21020010001"
 ],
 "groupIds": [1]
}
```
响应示例：
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
错误码：
|错误码 | 错误说明 | 操作建议|
|--- | --- | --- |
|10002 | 重置失败 | 联系管理员|
|110005 | 执行重置命令失败 | 稍后再次重置|
#### 查询实例属性
方法：POST
URL：/openapi/open/pad/padProperties
必填参数：padCode
请求参数：
|参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
|--- | --- | --- | --- | --- |
|padCode | AC21020010001 | String | 是 | 实例编号 |
请求示例：
```javascript
{
 "padCode": "AC21020010001"
}
```
响应示例：
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
错误码：
|错误码 | 错误说明 | 操作建议 |
| ----- | -------- | ------ |
|110028 | 实例不存在 | 请检查实例是否正确 |
#### 批量查询实例属性
方法：POST
URL：/openapi/open/pad/batchPadProperties
必填参数：padCodes、├─、├─
请求参数：
|参数名 | 示例值           | 参数类型 | 是否必填 | 参数描述 |
|--- |---------------| --- | --- | --- |
|padCodes |               | String[] | 是 |实例数量不多余200个 |
|├─ | AC21020010001 | String | 是 | 实例编号|
|├─ | AC21020010002 | String | 是 | 实例编号|
请求示例：
```javascript
{
    "padCodes": [
        "AC21020010001",
        "AC21020010002"
    ]
}
```
响应示例：
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
错误码：
|错误码 | 错误说明 | 操作建议 |
| ----- | -------- | ------ |
|110028 | 实例不存在 | 请检查实例是否正确 |
#### 修改实例属性
方法：POST
URL：/openapi/open/pad/updatePadProperties
必填参数：padCodes、├─
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
|错误码 | 错误说明 | 操作建议 |
| --- | --- | --- |
|110011 | 执行修改属性命令失败 | 请稍后重试 |
|110028 | 实例不存在 | 请检查实例是否正确 |
|110027 | 实例编号集合存在重复项 | 请检查实例是否存在重复的 |
#### 修改实例安卓改机属性
方法：POST
URL：/openapi/open/pad/updatePadAndroidProp
必填参数：props、├─ro.product.vendor.name
请求参数：
| 参数名                   | 示例值        | 参数类型 | 是否必填 | 参数描述                        |
| ------------------------ | ------------- | -------- | -------- | ------------------------------- |
| padCode                  | AC32010210001 | String   | 否       | 实例id                          |
| restart                  | false         | Boolean  | 否       | 设置完成后是否自动重启。`true`自动重启/`false`不自动重启，默认`false` |
| props                    | {}            | Object   | 是       | 系统属性（此字段为key-value定义） |
| ├─ro.product.vendor.name | OP52D1L1      | String   | 是       | 属性设置                        |
请求示例：
```javascript
{
 "padCode": "AC32010210001",
 "props": {
  "ro.product.vendor.name": "OP52D1L1"
 },
 "restart": false
}
```
响应示例：
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
错误码：
无
#### 根据国家Code修改SIM卡信息
方法：POST
URL：/openapi/open/pad/replacePadAndroidPropByCountry
必填参数：padCode
请求参数：
| 参数名                      | 示例值        | 参数类型 | 是否必填 | 参数描述                  |
|--------------------------| ------------- | -------- |------|-----------------------|
| padCode                  | AC32010210001 | String   | 是    | 实例id                  |
| countryCode              | US | String   | 否    | 国家编码，默认值`SG`。[查看所有国家编码↗](./EnumReference.md#51-countrycode---国家编码) |
| props                    | {}            | Object   | 否    | 系统属性（此字段为key-value定义） |
| ├─ro.product.vendor.name | OP52D1L1      | String   | 否    | 属性设置                  |
请求示例：
```javascript
{
    "padCode": "AC32010250001",
        "props": {
        "persist.sys.cloud.phonenum": "1234578998"
    },
    "countryCode": "US"
}
```
响应示例：
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
错误码：
无
#### 停止推流
方法：POST
URL：
必填参数：padCodes、├─、├─
请求参数：
| 参数名  | 示例值        | 参数类型 | 是否必填 | 参数描述 |
| ------- | ------------- | -------- | -------- | -------- |
|padCodes |  | String[] | 是 |  |
|├─ | AC11010000031 | String | 是 | 实例编号 |
|├─ | AC22020020700 | String | 是 | 实例编号 |
请求示例：
```javascript
{
    "padCodes": ["AC11010000031","AC22020020700"]
}
```
响应示例：
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
错误码：
无
#### 批量申请RTC连接Token
方法：POST
URL：
必填参数：userId、pads、├─padCode
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
| 错误码 | 错误说明             | 操作建议                 |
| ------ | -------------------- | ------------------------ |
| 120005 | 实例不存在           | 请检查实例编号是否正确   |
| 120007 | 此接口暂不支持此功能 | 联系相关人员更改推流配置 |
#### 申请RTC共享房间Token
方法：POST
URL：
必填参数：userId、terminal、pads、├─padCode
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
#### 修改实例时区
方法：POST
URL：/openapi/open/pad/updateTimeZone
必填参数：timeZone、padCodes
请求参数：
| 参数名   | 示例值        | 参数类型 | 是否必填 | 参数描述    |
| -------- | ------------- | -------- | -------- | ----------- |
| timeZone | Asia/Shanghai | String   | 是       | UTC标准时间 |
| padCodes |               | Array    | 是       | 实例列表    |
请求示例：
```javascript
{
 "padCodes": [
  "AC32010140003"
 ],
 "timeZone": "Asia/Shanghai"
}
```
响应示例：
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
错误码：
无
#### 修改实例语言
方法：POST
URL：/openapi/open/pad/updateLanguage
必填参数：language、padCodes
请求参数：
| 参数名   | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| -------- | ------ | -------- | -------- | -------- |
| language | zh     | String   | 是       | 语言     |
| country  | CN     | String   | 否       | 国家     |
| padCodes |        | Array    | 是       | 实例列表 |
请求示例：
```javascript
{
 "padCodes": [
  "AC32010140026"
 ],
 "language": "zh",
 "country": ""
}
```
响应示例：
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
错误码：
无
#### 修改实例SIM卡信息
方法：POST
URL：/openapi/open/pad/updateSIM
必填参数：padCodes、type、tac、cellid、narfcn、physicalcellid
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
#### 设置实例经纬度
方法：POST
URL：/openapi/open/pad/gpsInjectInfo
必填参数：longitude、latitude、padCodes
请求参数：
| 参数名                          | 示例值        | 参数类型  | 是否必填 | 参数描述                    |
|------------------------------|------------|-------|------|-------------------------|
| longitude                    | 116.397455 | Float | 是    | 经度                      |
| latitude                     | 39.909187  | Float | 是    | 纬度                      |
| altitude                     | 8          | Float | 否    | 海拔 (需要更新到最新镜像)          |
| speed                        | 8          | Float | 否    | 速度，m/s (20251024之后的镜像)  |
| bearing                      | 0          | Float | 否    | 速度方向，°  (20251024之后的镜像) |
| horizontalAccuracyMeters     | 0.1        | Float | 否    | 水平精度 (20251024之后的镜像)    |
| padCodes                     |            | Array | 是    | 实例列表                    |
请求示例：
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
响应示例：
```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1717570663080,
 "traceId": "ewab9p712ww0",
 "data": true
}
```
错误码：
无
#### 执行任务：查询代理出口IP信息
方法：POST
URL：/openapi/open/network/proxy/info
必填参数：padCodes
请求参数：
| 参数名   | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| -------- | ------ | -------- | -------- | -------- |
| padCodes |        | Array    | 是       | 实例列表 |
请求示例：
```javascript
{
  "padCodes": [
    "AC32010140012"
  ]
}
```
响应示例：
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
错误码：
无
#### 一键新机
方法：POST
URL：/openapi/open/pad/replacePad
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 查询一键新机支持国家列表
方法：GET
URL：/openapi/open/info/country
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
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
错误码：
无
#### 更新通讯录
方法：POST
URL：/openapi/open/pad/updateContacts
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 实例设置代理
方法：POST
URL：/openapi/open/network/proxy/set
必填参数：enable、padCodes
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
#### 实时查询已安装的应用列表
方法：POST
URL：/openapi/open/pad/listInstalledApp
必填参数：padCodes
请求参数：
| 参数名   | 示例值      | 参数类型 | 是否必填 | 参数描述                   |
| -------- | ----------- | -------- |------|------------------------|
| padCodes |  AC32010250001     | String[]    | 是    | 实例编号                   |
| appName |             | String    | 否    | 应用名称                |
请求示例：
```javascript
{
 "padCodes": ["AC32010250001"],
 "appName": ""
}
```
响应示例：
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
错误码：
无
#### 设置应用自启动
方法：POST
URL：
必填参数：applyAllInstances、├─serverName
请求参数：
| 参数名   | 示例值      | 参数类型     | 是否必填 | 参数描述   |
| -------- | ----------- |----------|------|--------|
| padCodes |  AC32010250001     | String[] | 否    | 实例编号（applyAllInstances=false时必填） |
| applyAllInstances |  false     | Boolean  | 是    | 是否应用所有实例模式。`true`应用所有实例（不下发任务，等下次开机才生效）/`false`不应用，默认`false`。与padCodes互斥，优先级更高 |
| appInfos |             | Object[] | 否    |        |
| ├─serverName | com.example/com.example.service.TaskService | String   | 是    | com.xxx.xxx（包名）/com.xxx.xxx.service.DomeService  (需要启动的服务完整路径) |
请求示例：
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
响应示例：
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
错误码：
无
#### 设置应用保活(新)
方法：POST
URL：
必填参数：padCodes、appInfos
请求参数：
| 参数名   | 示例值      | 参数类型     | 是否必填 | 参数描述   |
| -------- | ----------- |----------|------|--------|
| padCodes |  AC32010250001     | String[] | 是    | 实例编号（最多500个） |
| appInfos |             | Object[] | 是    | 保活应用列表，空数组表示清空（最多保活3个应用） |
| ├─packageName | com.tencent.mm | String   | 否    | 应用包名，留空或空数组表示清空 |
请求示例：
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
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1736326542985,
    "data": null
}
```
错误码：
无
#### 设置应用隐藏
方法：POST
URL：
必填参数：padCodes、appInfos
请求参数：
| 参数名   | 示例值      | 参数类型     | 是否必填 | 参数描述                   |
| -------- | ----------- |----------|------|------------------------|
| padCodes |  AC32010250001     | String[] | 是    | 实例编号（最多200个）           |
| appInfos |             | Object[] | 是    | 隐藏应用列表，空数组表示清空（0-200个） |
| ├─packageName | com.tencent.mm | String   | 否    | 应用包名，留空或空数组表示清空        |
请求示例：
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
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1736326542985,
    "data": null
}
```
错误码：
无
#### 隐藏辅助服务
方法：POST
URL：/openapi/open/pad/setHideAccessibilityAppList
必填参数：padCodes、appInfos、├─packageName
请求参数：
| 参数名   | 示例值      | 参数类型     | 是否必填 | 参数描述                   |
| -------- | ----------- |----------|------|------------------------|
| padCodes |  ["AC32010250001"]     | String[] | 是    | 实例编号数组（最多200个）           |
| appInfos |  []           | Object[] | 是    | 隐藏应用列表对象数组，传空数组[]表示清空（0-200个） |
| ├─packageName | com.tencent.mm | String   | 是（数组非空时）    | 应用包名。特殊值：传 `*` 或 `ALL` 表示隐藏所有应用的辅助服务权限        |
请求示例：
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
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1736326542985,
    "data": null
}
```
错误码：
无
#### 修改真机ADI模板
方法：POST
URL：/openapi/open/pad/replaceRealAdiTemplate
必填参数：padCodes、├─、wipeData、realPhoneTemplateId
请求参数：
| 参数名  | 示例值           | 参数类型     | 是否必填 | 参数描述    |
| ------- |---------------|----------|------|---------|
|padCodes |               | String[] | 是    |         |
|├─ | AC21020010001 | String   | 是    | 实例编号    |
|wipeData | false         | Boolean  | 是    | 是否清除数据  |
|realPhoneTemplateId | 186             | Long     | 是    | 云真机模板id |
请求示例：
```json
{
 "padCodes": ["AC32010250011"],
 "wipeData": true,
 "realPhoneTemplateId": 186
}
```
响应示例：
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
错误码：
无
#### 异步执行ADB命令
方法：POST
URL：/openapi/open/pad/asyncCmd
必填参数：padCodes、├─、scriptContent
请求参数：
|参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述|
|--- | --- | --- | --- | ---|
|padCodes |  | String[] | 是 |
|├─ | AC22020020793 | String | 是 | 实例编号|
|scriptContent | cd /root;ls | String | 是 | ADB命令，多条命令使用分号隔开|
请求示例：
```json
{
    "padCodes": [
        "AC22020020793"
    ],
    "scriptContent": "cd /root;ls"
}
```
响应示例：
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
错误码：
无
#### 开关Root权限
方法：POST
URL：/openapi/open/pad/switchRoot
必填参数：padCodes、├─、rootStatus
请求参数：
|参数名 | 示例值           | 参数类型     | 是否必填 | 参数描述                     |
|--- |---------------|----------|------|--------------------------|
|padCodes |               | String[] | 是    |
|├─ | AC22020020793 | String   | 是    | 实例编号                     |
|globalRoot | false         | Boolean  | 否    | 是否开启全局root权限。`true`开启全局root/`false`不开启，默认`false` |
|packageName | com.example        | String   | 否    | 应用包名(非全局root必传)多个包名通过,连接 |
|rootStatus | root开启状态         | Integer  | 是    | root状态。可选值：`0`关闭/`1`开启。[详见枚举↗](./EnumReference.md#113-rootstatus---root状态) |
请求示例：
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
响应示例：
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
错误码：
无
#### 本地截图
方法：POST
URL：
必填参数：padCodes、├─、rotation
请求参数：
| 参数名    | 示例值   | 参数类型 | 是否必填 | 参数描述                                                                     |
| ---- | ---- | ---- | ---- |--------------------------------------------------------------------------|
|padCodes |  | String[] | 是 |                                                                          |
|├─ | AC21020010231 | String | 是 | 实例编号                                                                     |
| rotation  | 0 | Integer  | 是 | 截图画面横竖屏旋：0：截图方向不做处理，默认；1：截图画面旋转为竖屏时：a：手机竖屏的截图，不做处理。b：手机横屏的截图，截图顺时针旋转90度。 |
| broadcast | false    | Boolean  | 否 | 事件是否广播。`true`广播/`false`不广播，默认`false` |
| definition | false    | Integer  | 否 | 清晰度 取值范围0-100                                                            |
| resolutionHeight | false    | Integer  | 否 | 分辨率 - 高 大于1                                                              |
| resolutionWidth | false    | Integer  | 否 | 分辨率 - 宽 大于1                                                              |
请求示例：
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
响应示例：
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
错误码：
无
#### 获取实例实时预览图片
方法：POST
URL：/openapi/open/pad/getLongGenerateUrl
必填参数：padCodes、├─
请求参数：
| 参数名    | 示例值           | 参数类型 | 是否必填 | 参数描述                                        |
| --------- |---------------| -------- | -------- |---------------------------------------------|
|padCodes |               | String[] | 是 |                                             |
|├─ | AC11010000031 | String | 是 | 实例编号（最多支持100个实例）                            |
| format  | png           | String  | 否       | 图片格式，枚举值：png、jpg、webp(CBS2.3.7以上版本支持)，默认jpg |
| height | 50 | String | 否 | 缩放高度（像素，不传或超出设备当前高度则使用设备当前高度）               |
| width | 50 | String | 否 | 缩放宽度（像素，不传或超出设备当前宽度则使用设备当前宽度）               |
| quality | 60 | String | 否 | 图片质量（百分比：0~100，不传或不在参数范围内则默认为60%）           |
请求示例：
```javascript
{
    "padCodes": [
        "AC11010000031",
        "AC11010000032"
    ],
    "format": "png"
}
```
响应示例：
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
错误码：
无
#### 获取实例实时预览图片(高性能)
方法：POST
URL：/openapi/open/pad/getLongGenerateUrlRaw
必填参数：padCodes、├─
请求参数：
| 参数名    | 示例值           | 参数类型 | 是否必填 | 参数描述                                        |
| --------- |---------------| -------- | -------- |---------------------------------------------|
|padCodes |               | String[] | 是 |                                             |
|├─ | AC11010000031 | String | 是 | 实例编号（最多支持100个实例）                            |
请求示例：
```javascript
{
    "padCodes": [
        "AC11010000031",
        "AC11010000032"
    ]
}
```
响应示例：
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
错误码：
无
#### 升级镜像
方法：POST
URL：/openapi/open/pad/upgradeImage
必填参数：无
请求参数：
无
请求示例：
```javascript
{
    "padCodes": [
        "AC22030010182"
    ],
    "wipeData": false,
    "imageId": "mg-24061124017"
}
```
响应示例：
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
错误码：
无
#### 升级真机镜像
方法：POST
URL：/openapi/open/pad/virtualRealSwitch
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 分页获取真机模板
方法：POST
URL：/openapi/open/realPhone/template/list
必填参数：无
请求参数：
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
请求示例：
```javascript
{
    "pageIndex": 1,
    "pageSize": 10
}
```
响应示例：
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
错误码：
无
#### 获取公共屏幕布局列表
方法：POST
URL：/openapi/open/screenLayout/publicList
必填参数：无
请求参数：
无
请求示例：
```javascript

```
响应示例：
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
错误码：
无
#### 批量获取实例机型信息
方法：POST
URL：/openapi/open/pad/modelInfo
必填参数：无
请求参数：
无
请求示例：
```javascript
{
    "padCodes": [
        "AC22030010182"
    ]
}
```
响应示例：
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
错误码：
无
#### 添加应用黑名单列表
方法：POST
URL：/openapi/open/appBlack/setUpBlackList
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
```javascript
{
 "code": 200,
 "msg": "success",
 "ts": 1721647657112,
 "data": null
}
```
错误码：
无
#### 设置实例黑名单
方法：POST
URL：/openapi/open/pad/triggeringBlacklist
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "padGrade": "q2-4",
 "padCodes": [
  "AC22030010124"
 ]
}
```
响应示例：
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
错误码：
无
#### 设置实例带宽
方法：POST
URL：/openapi/open/pad/setSpeed
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "padCodes": [
  "AC32010140011"
 ],
 "upBandwidth": 10.00,
 "downBandwidth": 10.00
}
```
响应示例：
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
错误码：
无
#### 开启关闭ADB
方法：POST
URL：/openapi/open/pad/openOnlineAdb
必填参数：无
请求参数：
无
请求示例：
```javascript
{
    "padCodes":[
        "AC32010250032"
    ],
    "openStatus": 1
}
```
响应示例：
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
错误码：
无
#### 获取ADB连接信息
方法：POST
URL：/openapi/open/pad/adb
必填参数：无
请求参数：
无
请求示例：
```javascript
{
    "padCode": "AC32010250032",
    "enable": true
}
```
响应示例：
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
错误码：
无
#### 批量获取ADB连接信息
方法：POST
URL：/openapi/open/pad/batch/adb
必填参数：无
请求参数：
无
请求示例：
```javascript
{
    "padCodes": [
        "AC32010250032",
        "AC32010250033"
    ],
    "enable": true
}
```
响应示例：
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
错误码：
无
#### 模拟触控
方法：POST
URL：/openapi/open/pad/simulateTouch
必填参数：无
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
#### 实例操作任务详情
方法：POST
URL：
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "taskIds":[1,2]
}
```
响应示例：
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
错误码：
无
#### 获取实例执行脚本结果
方法：POST
URL：
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "taskIds": [1]
}
```
响应示例：
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
错误码：
无
#### 获取实例截图结果
方法：POST
URL：
必填参数：无
请求参数：
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
请求示例：
```json
{
 "taskIds": [1]
}
```
响应示例：
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
错误码：
无
#### 实例重启重置执行结果
方法：POST
URL：
必填参数：taskIds、├─
请求参数：
|参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述|
|--- | --- | --- | --- | --- |
|taskIds |  | Integer [] | 是 | |
|├─ | 1 | Integer | 是 | 任务ID |
请求示例：
```javascript
{
    "taskIds": [1]
}
```
响应示例：
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
错误码：
无
#### 实例列表信息
方法：POST
URL：/openapi/open/pad/infos
必填参数：无
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
#### 实例列表信息（优化分页版本）
方法：POST
URL：/openapi/open/pad/infos/new
必填参数：无
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
#### 实例分组列表
方法：POST
URL：/openapi/open/group/infos
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "padCode": "AC21020010391",
 "groupIds": [1]
}
```
响应示例：
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
错误码：
无
#### 导入通话记录
方法：POST
URL：/openapi/open/pad/addPhoneRecord
必填参数：padCodes、callRecords、├─ number、├─ inputType、├─ duration
请求参数：
| 参数名           | 示例值                                                                                       | 参数类型     | 是否必填 | 参数描述                 |
|---------------|-------------------------------------------------------------------------------------------|----------|------|----------------------|
| padCodes      | ACP2505060777                                                                             | String[] | 是    | 需要编辑通话记录的实例编码        |
| callRecords   | [{"number":"18009781201","inputType":1,"duration":30,"timeString":"2025-05-06 14:00:09"}] | Object[] | 是    | 通话记录                 |
| ├─ number     | 13900000000                                                                               | String   | 是    | 电话号码                 |
| ├─ inputType  | 1                                                                                         | int      | 是    | 通话类型。可选值：`1`拨出/`2`接听/`3`未接 |
| ├─ duration   | 60                                                                                        | int      | 是    | 通话时长;单位是秒,未接电话是0秒    |
| ├─ timeString | 2025-05-08 12:30:00                                                                       | String   | 否    | 通话时长                 |
请求示例：
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
响应示例：
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
错误码：
无
#### 云机文本信息输入
方法：POST
URL：/openapi/open/pad/inputText
必填参数：padCodes、text
请求参数：
| 参数名           | 示例值           | 参数类型     | 是否必填 | 参数描述          |
|---------------|---------------|----------|------|---------------|
| padCodes      | ACP2505060777 | String[] | 是    | 实例编码 |
| text   | hello123      | String | 是    | 输入文本          |
请求示例：
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
响应示例：
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
错误码：
无
#### 模拟发送短信
方法：POST
URL：/openapi/open/pad/simulateSendSms
必填参数：padCodes、senderNumber、smsContent
请求参数：
| 参数名      | 示例值                          | 参数类型     | 是否必填 | 参数描述                 |
|-----------|------------------------------|----------|------|----------------------|
| padCodes  | ["ACN2505060777"]            | String[] | 是   | 实例编码列表，数量1-100个 |
| senderNumber | 13800000000                 | String   | 是   | 发送方号码，不支持大陆号码。（格式：长度限制16位，允许数字、英文、空格、+-号）|
| smsContent | 这是一条测试短信。 | String   | 是   | 短信内容（长度限制127位）                 |
请求示例：
```javascript
{
  "padCodes": ["ACN2505060777"],
  "senderNumber": "13800000000",
  "smsContent": "这是一条测试短信。"
}
```
响应示例：
```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1736922808949,
  "traceId": "ewb123abc",
  "data": true
}
```
错误码：
无
#### 重置GAID
方法：POST
URL：/openapi/open/pad/resetGAID
必填参数：padCodes、├─、resetGmsType、taskSource
请求参数：
| 参数名   | 示例值           | 参数类型      | 是否必填 | 参数描述             |
| -------- |---------------|-----------|------|------------------|
| padCodes |               | String[]  | 是    |                  |
| ├─       | AC21020010001 | String    | 是    | 实例编号             |
| groupIds |               | Integer[] | 否    |                  |
| ├─       | 1             | Integer   | 否    | 实例组ID            |
| resetGmsType | GAID          | String    | 是    | 重置GMS类型。可选值：`GAID`重置GAID |
| oprBy | zhangsan      | String    | 否    | 操作人              |
| taskSource | OPEN_PLATFORM      | String    | 是    | 任务来源，可选：OPEN_PLATFORM         |
请求示例：
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
响应示例：
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
错误码：
无
#### 注入音频到实例麦克风
方法：POST
URL：/openapi/open/pad/injectAudioToMic
必填参数：padCodes、enable
请求参数：
| 参数名           | 示例值                              | 参数类型     | 是否必填 | 参数描述                    |
|---------------|----------------------------------|----------|------|-------------------------|
| padCodes      | ACP2505060777                    | String[] | 是    | 实例编码                    |
| url   | http://localhost/abc             | String   | 否    | 音频文件下载地址 （此字段和fileUniqueId 2选1传值）|
| fileUniqueId  | 8fc73d05371740008ea27a2707496a82 | String   | 否    | 文件id唯一标识（此字段和url 2选1传值） |
| enable        | true                             | Boolean        | 是    | 注入开关                    |
请求示例：
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
响应示例：
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
错误码：
无
#### 创建本地实例备份
方法：`POST`
URL：`/openapi/open/pad/local/pod/backup`
必填参数：padCode、├─ endpoint、├─ bucket、├─ accessKey、├─ secretKey、├─ protocol、├─ region、├─ securityToken、├─ expiration
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
| 错误码   | 错误说明                                           | 操作建议           |
| ------ | ------------------------------------------------ |----------------|
| 220025 | 当前本地实例存在其他正在执行或待执行的任务，请等待任务执行完毕后再试！ | 等待任务执行完成后再尝试   |
| 220026 | 仅支持本地实例备份！                                  | 确认操作实例为本地实例    |
| 220029 | 当前实例状态不在运行中                                 | 确认实例处于运行中      |
| 220033 | 当前实例CBS版本过低，不支持备份或者还原                        | 联系客户经理升级板卡系统到最新版本后再尝试 |
#### 创建本地实例还原
方法：`POST`
URL：`/openapi/open/pad/local/pod/restore`
必填参数：backupId、padCode、├─ endpoint、├─ bucket、├─ accessKey、├─ secretKey、├─ protocol、├─ region、├─ securityToken、├─ expiration
请求参数：
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
请求示例：
```json
{
  "padCode": "ACP25091XXXXXJ15",
  "backupId": "bkp-ACP25091XXXXXJ15-1758097064458",
  "credentialType": 1
}

```
响应示例：
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
错误码：
| 错误码   | 错误说明                              | 操作建议                   |
| ------ |-----------------------------------| ---------------------- |
| 220025 | 当前本地实例存在其他正在执行或待执行的任务，请等待任务执行完毕后再试！ | 等待任务执行完成后再尝试       |
| 220027 | 当前本地实例备份文件不存在，请检查文件后再试！           | 检查备份文件是否存在          |
| 220030 | 当前实例状态不在运行中或者异常中                  | 确认实例处于运行或异常状态      |
| 220031 | 备份的文件不属于当前用户                      | 确认备份实例归属权限          |
| 220032 | 当前备份ID实例信息不存在，无法辨别当前备份文件是否属于当前用户  | 检查备份ID是否正确           |
| 220033 | 当前实例CBS版本过低，不支持备份或者还原             | 升级实例CBS版本后再尝试       |
#### 本地实例备份结果查询
方法：`POST`
URL：`/openapi/open/pad/local/pod/backupSelectPage`
必填参数：padCodes、├─padCode
请求参数：
| 参数名     | 示例值              | 参数类型   | 是否必填 | 参数描述              |
|---------|------------------|--------|-----|-------------------|
| page    | 1                | Integer | 否   | 当前页               |
| rows    | 10               | Integer | 否   | 每页的数量             |
| padCodes |                  | String[] | 是   |                   |
| ├─padCode | ACP5C24S9G6xxxxx | String | 是   | 实例编号，最大支持传入100条实例 |
请求示例：
```json
{
  "padCodes":["ACP5C24S9G6xxxxx"],
  "page":1,
  "rows":10
}

```
响应示例：
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
错误码：
无
#### 清除进程并返回桌面
方法：POST
URL：/openapi/open/pad/cleanAppHome
必填参数：padCodes
请求参数：
| 参数名           | 示例值                              | 参数类型     | 是否必填 | 参数描述                    |
|---------------|----------------------------------|----------|------|-------------------------|
| padCodes      | ATP250814USYXXXX                    | String[] | 是    | 实例编码                    |
请求示例：
```javascript
{
    "padCodes": [
        "ATP250814USYXXXX"
    ]
}
```
响应示例：
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
错误码：
无
#### 无人直播
方法：POST
URL：/openapi/open/pad/unmanned/live
必填参数：padCodes
请求参数：
| 参数名           | 示例值                                                                      | 参数类型     | 是否必填 | 参数描述                                 |
|---------------|--------------------------------------------------------------------------|----------|-----|--------------------------------------|
| padCodes      | ACN384345141346304                                                       | String[] | 是   | 实例编码(1-100个)                         |
| injectSwitch      | true                                                                     | Boolean | 否   | 是否开启注入视频。`true`开启/`false`取消，默认`false` |
| injectLoop     | false                                                                    | Boolean | 否    | 是否循环播放。`true`循环播放/`false`不循环，默认`false` |
| injectUrl      | https://file.vmoscloud.com/userFile/1eea385b2a6ba3942ebf642badf39aa0.mp4 | String   | 否   | 单个视频注入地址，支持 http/https/rtmp:// 以及本地路径，与injectUrls至少传一项 |
| injectUrls      | ["https://file.vmoscloud.com/userFile/1eea385b2a6ba3942ebf642badf39aa0.mp4","rtmp://example.com/live"] | String[]   | 否   | 视频注入地址列表(最多5个)，支持 http/https/rtmp:// 以及本地路径，与injectUrl至少传一项 |
请求示例：
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
响应示例：
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
错误码：
无
#### 图片注入
方法：POST
URL：/openapi/open/pad/inject/picture
必填参数：padCodes、injectUrl
请求参数：
| 参数名           | 示例值                                                                      | 参数类型     | 是否必填 | 参数描述                                 |
|---------------|--------------------------------------------------------------------------|----------|-----|--------------------------------------|
| padCodes      | ACN2510166WZUPCJ                                                       | String[] | 是   | 实例编码(1-100个)                         |
| injectSwitch      | true                                                                     | Boolean | 否   | 是否开启注入图片(true:开启  false:取消) 默认是false |
| injectLoop     | false                                                                    | Boolean | 否    | 是否循环播放。`true`循环播放/`false`不循环，默认`false` |
| injectUrl      | https://file.vmoscloud.com/userFile/ac4e112d72f9ed724101f510e774001f.JPG | String   | 是   | 图片注入地址,支持 http https rtmp://         |
请求示例：
```javascript
{
        "padCodes": ["ACN2510166WZUPCJ"],
        "injectSwitch": true,
        "injectLoop": false,
        "injectUrl": "https://file.vmoscloud.com/userFile/ac4e112d72f9ed724101f510e774001f.JPG"
}
```
响应示例：
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
错误码：
无
#### 运动数据注入（步数）
方法：POST
URL：/openapi/open/pad/stepData
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
### 回调管理
#### 查询支持的回调类型
方法：GET
URL：/openapi/open/config/selectList
必填参数：无
请求参数：
无
请求示例：
```javascript
/openapi/open/config/selectList
```
响应示例：
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
错误码：
无
#### 查询配置的回调地址
方法：GET
URL：/openapi/open/config/selectCallback
必填参数：无
请求参数：
无
请求示例：
```javascript
/openapi/open/config/selectCallback
```
响应示例：
```javascript
{
 "code" : 200,
 "data" : "http://www.baidu.com",
 "msg" : "success",
 "ts" : 1734501602763
}
```
错误码：
无
#### 新增回调地址配置
方法：POST
URL：/openapi/open/config/insertCallback
必填参数：callbackIdList、callbackUrl
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | --- | --- | --- |
| callbackIdList | [1,2,3] | Long[] | 是 | 回调类型ID集合(从查询支持的回调类型接口获取) |
| callbackUrl | http://192.168.1.1/callback | String | 是 | 接收任务回调配置URL |
请求示例：
```javascript
{
  "callbackIdList": [21, 14],
  "callbackUrl": "http://localhost:8080/callback"
}
```
响应示例：
```javascript
{"code":200,"data":2,"msg":"success","ts":1734502541732}
```
错误码：
无
#### 修改回调地址配置
方法：POST
URL：/openapi/open/config/updateCallback
必填参数：callbackIdList、callbackUrl
请求参数：
| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | --- | --- | --- |
| callbackIdList | [1,2,3] | Long[] | 是 | 回调类型ID集合(从查询支持的回调类型接口获取) |
| callbackUrl | http://192.168.1.1/callback | String | 是 | 接收任务回调配置URL |
请求示例：
```javascript
{
  "callbackIdList": [21, 14],
  "callbackUrl": "http://localhost:8080/callback"
}
```
响应示例：
```javascript
{
 "code" : 200,
 "data" : 2,
 "msg" : "success",
 "ts" : 1734502541732
}
```
错误码：
无
#### 删除配置的回调地址
方法：POST
URL：/openapi/open/config/deleteCallback
必填参数：无
请求参数：
无
请求示例：
```javascript
{}
```
响应示例：
```javascript
{
 "code" : 200,
 "data" : 22,
 "msg" : "success",
 "ts" : 1734503029282
}
```
错误码：
无
#### 实例状态回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 实例重启任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 实例重置任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 异步执行ADB任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 应用安装任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 应用卸载任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 应用停止任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 应用启动任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 文件上传实例任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 查询实例应用列表回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 实例升级镜像任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 实例黑名单任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 一键新机回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存实例开机回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存实例关机回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存实例删除回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存存储备份回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存存储删除回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 文件上传任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存2.0开机回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存2.0关机回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存2.0实例删除回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 网存2.0存储备份回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 订阅事件回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
#### 无人直播任务回调
方法：
URL：
必填参数：无
请求参数：
无
请求示例：
无
响应示例：
无
错误码：
无
### 文件管理
#### 文件上传到云盘
方法：POST
URL：
必填参数：无
请求参数：
无
请求示例：
```javascript

{
    "fileUrl": "http://down.s.qq.com/download/11120898722/apk/10043132_com.tencent.fiftyone.yc.apk",
    "fileName": "桃源深处有人家游戏官方版.apk",
    "fileMd5": "c52585e13a67e13128d9963b2f20f69678a86ee8b5551ca593327d329719a5"
}

```
响应示例：
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
错误码：
无
#### 实例文件删除
方法：POST (支持批量删除，一次最多只能删除200个)
URL：
必填参数：无
请求参数：
无
请求示例：
```javascript

{
 "fileUniqueIds": [
  "cfc280111c435823c5409ddb9a4186420d",
  "cf77f930acbbe1707fffc661f2c4380a71"
 ]
}

```
响应示例：
```javascript
{
  "code": 200,
  "msg": "success",
  "ts": 1734677342300,
  "data": true
}

```
错误码：
无
#### 文件上传实例V3版本
方法：POST
URL：/openapi/open/pad/v3/uploadFile
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 文件上传到实例
方法：POST
URL：/openapi/open/pad/v2/uploadFile
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 文件列表
方法：POST
URL：
必填参数：无
请求参数：
无
请求示例：
```javascript

{
    "page": 1,
    "rows": 10,
    "fileName":"33"
}

```
响应示例：
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
错误码：
无
#### 文件任务详情
方法：POST
URL：
必填参数：无
请求参数：
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
请求示例：
```javascript
{
 "taskIds":[
  1,2
 ]
}
```
响应示例：
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
错误码：
无
### 应用管理
#### 应用上传
方法：POST
URL：
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 应用列表
方法：POST
URL：
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 应用详情
方法：POST
URL：
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "appId":1
}
```
响应示例：
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
错误码：
无
#### 查询实例应用列表
方法：POST
URL：/openapi/open/pad/listApp
必填参数：无
请求参数：
无
请求示例：
```javascript
{
    "padCodes": [
        "AC22010020062"
    ]
}
```
响应示例：
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
错误码：
无
#### 应用安装
方法：POST
URL：/openapi/open/pad/installApp
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 应用卸载
方法：POST
URL：/openapi/open/pad/uninstallApp
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
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
错误码：
无
#### 应用启动
方法：POST
URL：/openapi/open/pad/startApp
必填参数：padCodes、├─、pkgName
请求参数：
| 参数名      | 示例值       | 参数类型 | 是否必填 | 参数描述 |
| ----------- | ------------ | -------- | -------- | -------- |
|padCodes |  | String[] | 是 | |
|├─ | AC22010020062 | String | 是 | 实例编号|
| pkgName | xxx.test.com | String   | 是       | 包名     |
请求示例：
```javascript
{
 "padCodes": [
  "AC22030022693"
 ],
 "pkgName": xxx.test.com
}
```
响应示例：
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
错误码：
无
#### 应用停止
方法：POST
URL：/openapi/open/pad/stopApp
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "padCodes": [
  "AC22010020062"
 ],
 "pkgName": xxx.test.com
}
```
响应示例：
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
错误码：
无
#### 应用重启
方法：POST
URL：/openapi/open/pad/restartApp
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "padCodes": [
  "AC22030022693"
 ],
 "pkgName": xxx.test.com
}
```
响应示例：
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
错误码：
无
#### 黑白名单列表
方法：POST
URL：/openapi/open/appClassify/pageList
必填参数：无
请求参数：
无
请求示例：
```javascript
{
    "classifyName": "",
    "classifyType": 1,
    "page": 1,
    "rows": 10
}
```
响应示例：
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
错误码：
无
#### 黑白名单保存
方法：POST
URL：/openapi/open/appClassify/save
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": 1
}
```
错误码：
无
#### 黑白名单详情
方法：POST
URL：/openapi/open/appClassify/detail
必填参数：无
请求参数：
无
请求示例：
```javascript
{"id":153858}
```
响应示例：
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
错误码：
无
#### 黑白名单实例关联保存
方法：POST
URL：/openapi/open/appClassify/padSave
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": null
}
```
错误码：
无
#### 黑白名单实例关联详情
方法：POST
URL：/openapi/open/appClassify/padDetail
必填参数：无
请求参数：
无
请求示例：
```javascript
{"id":153858}
```
响应示例：
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
错误码：
无
#### 删除黑白名单
方法：POST
URL：/openapi/open/appClassify/del
必填参数：无
请求参数：
无
请求示例：
```javascript
{"id":153858}
```
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735020371601,
    "data": null
}
```
错误码：
无
#### 添加黑白名单App
方法：POST
URL：/openapi/open/appClassify/addApp
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": null
}
```
错误码：
无
#### 添加黑白名单实例关联
方法：POST
URL：/openapi/open/appClassify/addPad
必填参数：无
请求参数：
无
请求示例：
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
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": null
}
```
错误码：
无
#### 删除黑白名单关联的实例
方法：POST
URL：/openapi/open/appClassify/delPad
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "id": 100,
 "padCodes": ["AC32010250003"]
}
```
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1735019933306,
    "data": null
}
```
错误码：
无
#### 按实例查询关联的黑白名单
方法：POST
URL：/openapi/open/appClassify/padClassifyList
必填参数：无
请求参数：
无
请求示例：
```javascript
{
  "padCodes": [
    "AC32010230001",
    "AC32010230002"
  ]
}
```
响应示例：
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
错误码：
无
#### 应用分类列表
方法：POST
URL：/openapi/open/newAppClassify/pageList
必填参数：无
请求参数：
无
请求示例：
```javascript
{
    "enable":true,
    "page":1,
    "rows":10
}
```
响应示例：
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
错误码：
无
#### 应用启停执行结果
方法：POST
URL：
必填参数：无
请求参数：
无
请求示例：
```javascript
{
 "taskIds": [1]
}
```
响应示例：
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
错误码：
无
### 镜像管理
#### 获取镜像列表
方法：POST
URL：/openapi/open/image/queryImageList
必填参数：无
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
### 账户管理
#### 批量新增子账户
方法：POST
URL：/openapi/open/subCustomer/batchAdd
必填参数：无
请求参数：
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
请求示例：
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
响应示例：
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
错误码：
无
#### 子账户列表分页查询
方法：POST
URL：/openapi/open/subCustomer/pageList
必填参数：无
请求参数：
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
请求示例：
```javascript
{
    "page": 1,
    "rows": 10,
    "status": 1,
    "customerAccount": "测试账号1",
    "customerTel": "15580887450"
}
```
响应示例：
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
错误码：
无
#### 子账户批量删除
方法：POST
URL：/openapi/open/subCustomer/batchDelete
必填参数：ids
请求参数：
| 参数名      | 示例值   | 参数类型    | 是否必填 | 参数描述                          |
| -------- |-------|---------| ---- |-------------------------------|
| ids | [972] | Long[]  | 是    | 需要删除的子账户主键ID        |
请求示例：
```javascript
{
    "ids": [972]
}
```
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1760154208875
}
```
错误码：
无
#### 主账号板卡列表分页查询
方法：POST
URL：/openapi/open/subCustomer/resource/masterCustomer/pageList
必填参数：无
请求参数：
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
请求示例：
```javascript
{
     "page": 1,
     "rows": 10,
     "netStorageResFlag":1,
     "deviceCode":"ACD250411WU3CF2U",
     "deviceCreatePadStatus":1
}
```
响应示例：
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
错误码：
无
#### 子账号板卡列表查询
方法：POST
URL：/openapi/open/subCustomer/resource/list
必填参数：无
请求参数：
| 参数名             | 示例值              | 参数类型     | 参数描述    |
|-----------------|------------------|----------|---------|
| code            | 200              | Integer  | 状态码     |
| msg             | success          | String   | 响应消息    | | |
| ts              | 1760097337371    | Long     | 时间戳     | |
| data            |                  | Object[] | 板卡信息    | |
| ├─deviceId              | 12376            | Long     | 板卡主键ID  |
| ├─deviceCode | ACD250411WU3CF2U | String   | 板卡编号 |
| ├─netStorageResFlag      | 1                | Integer  | 网存板卡标记。可选值：`0`本地板卡/`1`网存板卡/`2`魔盒。[详见枚举↗](./EnumReference.md#31-netstorrageresflag---网存标记网存板卡标记) | |
请求示例：
```javascript
{
     "subCustomerId":862,
     "netStorageResFlag":1,
     "deviceCode":"ACD250411WU3CF2U"
}
```
响应示例：
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
错误码：
无
#### 子账号板卡授权
方法：POST
URL：/openapi/open/subCustomer/resource/allocate
必填参数：无
请求参数：
| 参数名               | 示例值                              | 参数类型     | 参数描述    |
|-------------------|----------------------------------|----------|---------|
| code              | 200                              | Integer  | 状态码     |
| msg               | success                          | String   | 响应消息    | | |
| ts                | 1760154208875                    | Long     | 时间戳     | |
请求示例：
```javascript
{
    "subCustomerId": 862,
     "allocateDeviceIds": [
        12376
    ]
}
```
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1760168978928
}
```
错误码：
无
#### 子账号板卡解绑
方法：POST
URL：/openapi/open/subCustomer/resource/unbind
必填参数：无
请求参数：
| 参数名               | 示例值                              | 参数类型     | 参数描述    |
|-------------------|----------------------------------|----------|---------|
| code              | 200                              | Integer  | 状态码     |
| msg               | success                          | String   | 响应消息    | | |
| ts                | 1760154208875                    | Long     | 时间戳     | |
请求示例：
```javascript
{
     "subCustomerId": 862,
     "unbindDeviceIds": [
        12376
    ]
}
```
响应示例：
```javascript
{
    "code": 200,
    "msg": "success",
    "ts": 1760168978928
}
```
错误码：
无
