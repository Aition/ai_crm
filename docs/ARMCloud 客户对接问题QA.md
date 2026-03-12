## 主题：ARMCloud 客户对接问题QA

### QA 1
问：虚拟机和云真机的区别在哪？
答：虚拟机和云真机的区别在于云真机具有较强的抗风险能力，因为云真机的每一个ADI模板都是通过真机采集而来。

### QA 2
问：云机属性，各种id、主板名称，设备名称等等，赋值的时候有什么格式要求或者规则？
答：可通过openapi的[**分页获取真机模板**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E5%88%86%E9%A1%B5%E8%8E%B7%E5%8F%96%E7%9C%9F%E6%9C%BA%E6%A8%A1%E6%9D%BF)查询对应的云机模板属性信息，按需传入。

### QA 3
问：云真机产品为什么会变成虚拟机？
答：所有的设备，到期后或者用户降配都会刷成虚拟机镜像。虚拟机要变为云真机，要调用openapi的[**升级真机镜像**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E5%8D%87%E7%BA%A7%E7%9C%9F%E6%9C%BA%E9%95%9C%E5%83%8F)接口一个 镜像ID + 云真机模板ID，才可以变为云真机。

### QA 4
问：虚拟机每次一键新机都是新的模板吗？
答：虚拟机没有云机模板，是随机的设备参数，可以在tools拓展工具里变更。云真机有模板，可以在[**一键新机**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E4%B8%80%E9%94%AE%E6%96%B0%E6%9C%BA)的接口里传入变更模板，可以随机，也可以指定一个id。

### QA 5
问：一键新机是否有次数限制？
答：暂时没有。

### QA 6
问：用户用云手机需要一天注册很多个某应用的账号或者批量发布内容，应该怎么避免被风控？
答：针对该使用场景，我们建议您可以 用一键新机 + 代理设置 切换实现，一键新机可以根据选择代理的国家地区来自动生成改机参数属性，也可以支持自定义传，具体看您这边的业务场景适合使用哪一种。

### QA 7
问：toolbox工具改机以后是否需要重启才能生效？
答：虚拟机可以通过toolbox修改，不需要重启，云真机可以通过[**修改实例安卓改机属性**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E4%BF%AE%E6%94%B9%E5%AE%9E%E4%BE%8B%E5%AE%89%E5%8D%93%E6%94%B9%E6%9C%BA%E5%B1%9E%E6%80%A7)修改，需要重启才能生效。

### QA 8
问：云机界面左上角有一个ID，这个ID是什么？是否可以隐藏？
答：是运营商信息：国家码与区域码，系统数据库里面没有匹配的，显示的就是数字，有就是显示字符串，这个不影响使用，用来增加模拟真实度的。
# 显示运营商名称
settings put secure show\_operator\_name 1
# 隐藏运营商名称
settings put secure show\_operator\_name 0
# 查看当前设置
settings get secure show\_operator\_name

### QA 9
问：APP应用每次都要手动点权限吗？还是有api可以授予权限？
答：可以通过调用[**文件上传实例V3版本**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E5%AE%9E%E4%BE%8Bv3%E7%89%88%E6%9C%AC)接口实现，isAuthorization 默认全授权。安装应用时接口入参fileUniqueld 和 url 二选一就好，其他非必传，其中 fileUniqueld 在[**文件上传到云盘**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E5%88%B0%E4%BA%91%E7%9B%98)这个接口会返回。

### QA 10
问：Token有效期？
答：Token有效期**24小时**，需要定期刷新。

### QA 11
问：云机中设置里看到的云机存储已用和总存储空间是否为真实的？
答：是模拟的，是设置在云机模板里的数据，但是剩余空间是真实的，比如256GB总空间-225已用空间=26GB剩余空间，这个26GB是真实空间。

### QA 12
问：云机有没有模拟GPS定位？
答：如果没有开启代理和主动触发虚拟定位，云机默认的定位是新加坡。（拓展工具APP里面有虚拟定位的功能）

### QA 13
问：云机是否支持视频注入/推流？
答：除了拓展工具APP里面的视频注入功能以外，OpenAPI和Web H5 SDK 、Android SDK 都有相关接口支持

### QA 14
问：云手机可以支持esim卡吗？
答：暂时还不支持，这个需要硬件支撑。

### QA 15
问：可以跨安卓版本升级镜像吗？比如Android13升级Android14的镜像，或者Android14升级Android13的镜像？
答：可以，虚拟机在paas平台直接选择清空数据升级就好了，云真机需要调用OpenAPI接口[**升级真机镜像**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E5%8D%87%E7%BA%A7%E7%9C%9F%E6%9C%BA%E9%95%9C%E5%83%8F)来实现，需要传入Android对应版本的真机模版ID。

### QA 16
问：怎么获取真机模版信息？
答：可以通过 [**分页获取真机模板**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E5%88%86%E9%A1%B5%E8%8E%B7%E5%8F%96%E7%9C%9F%E6%9C%BA%E6%A8%A1%E6%9D%BF) 接口获取。

### QA 17
问：修改实例时区、修改实例语言、设置实例经纬度、查询实例代理信息等等是否可以通过一个接口实现？
答：可以，直接调用[**网存实例批量开机**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E7%BD%91%E5%AD%98%E5%AE%9E%E4%BE%8B%E6%89%B9%E9%87%8F%E5%BC%80%E6%9C%BA) 接口，传入 androidProp 安卓属性配置即可。

### QA 18
问：请问你们有提供配置谷歌证书相关插件的支持吗，比如定制化的magrisk或者是kernelSU这种
答：我们有自己的方案，[**一键新机**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E4%B8%80%E9%94%AE%E6%96%B0%E6%9C%BA) 可以传入手机根证书（谷歌证书）。

### QA 19
问：H5SDK提示token无效
答：检测接口请求域名是否正确，检测是否是通过 [**获取SDK临时Token(根据padCode)**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E8%8E%B7%E5%8F%96sdk%E4%B8%B4%E6%97%B6token-%E6%A0%B9%E6%8D%AEpadcode) 接口获取的token。

### QA 20
问：注入音频PCM需要多少采样率？
答：44100采样率。

### QA 21
问：[**设置实例经纬度**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E8%AE%BE%E7%BD%AE%E5%AE%9E%E4%BE%8B%E7%BB%8F%E7%BA%AC%E5%BA%A6) 海拔、速度、速度方向、水平精度 这几个参数有没有设置值的范围，是否有最大值最小值的限制？
答：
persist.sys.cloud.gps.lat（纬度）: 最小 -90，最大 90（代码未强制校验；按地理物理范围）
persist.sys.cloud.gps.lon（经度）: 最小 -180，最大 180（代码未强制校验；按地理物理范围）
persist.sys.cloud.gps.speed（速度，m/s）: 最小 0，最大未限制（代码只要求非负）
persist.sys.cloud.gps.altitude（海拔，m）: 最小未限制，最大未限制（可为负值；代码未做范围校验）
persist.sys.cloud.gps.bearing（方向，°）: 最小 0，最大小于 360（0 ≤ value < 360）
persist.sys.cloud.gps.en（使能开关）: 整型，范围未限制（语义上应为 0/1，默认 1）
persist.sys.cloud.gps.accuracy（水平精度，m）: 最小 0.1，最大 1000.0（代码明确限制）

### QA 22
问：给一台实例设置上代理之后 怎么取消这个机器的代理设置？
答：再调用一次[**实例设置代理**](https://docs.armcloud.net/cn/server/OpenAPI.html#%E5%AE%9E%E4%BE%8B%E8%AE%BE%E7%BD%AE%E4%BB%A3%E7%90%86)的接口，启用传 false

### QA 23
问：文件上传接口可以上传到Download文件夹之外的路径的吗？
答："/DCIM/", "/Documents/", "/Download/", "/Movies/", "/Music/", "/Pictures/" 目前只支持这些路径下

### QA 24
问：如何通过命令行获取实例编号
答：getprop ro.boot.pad\_code

### QA 25
问：我如果 想把我的证书加到系统证书 目录 这个怎么操作
答：mkdir -p /data/local/tmp/cacerts
cp -a /apex/com.android.conscrypt/cacerts/. /data/local/tmp/cacerts
mount --bind /data/local/tmp/cacerts /apex/com.android.conscrypt/cacerts
每次重启都要执行

### QA 26
问：在实例上通过谷歌浏览器访问UA-CH（whatismyuseragent.com）网址没有显示真实的安卓版本和机型；而真机在其他浏览器访问UA-CH（whatismyuseragent.com）网址会显示真实的镜像版本和机型
答：从 Android 10（API 29）开始，Chrome 为了保护用户隐私，在 UA-CH（User-Agent Client Hints）机制中不再返回真实的 Android 系统版本。它会采用一套固定的隐私保护策略：如果您的设备首次发布时的系统版本（first\_api\_level）≥ Android 10，Chrome 会统一将版本号映射为 Android 10。这是为了防止网站通过精确的系统版本识别您的设备，从而保护您的隐私安全，同时也能减少版本碎片化带来的兼容性问题。所以，您看到的 “显示为 Android 10” 是 Chrome 的正常隐私保护行为，不会影响设备或浏览器的实际功能