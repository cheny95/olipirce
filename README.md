# 油价 HomeAssistant集成

## 使用方法：

- 下载该集成放入homeassistant安装目录`/config/custom_conponents/`中
- 然后重启Home Assistant服务。
- 启动完成后，在`/config/configuration.yaml`添加以下内容

```yaml
sensor:
  - platform: oilprice
    name: 油价
    region: anhui  # 此处为你要获取油价的省份全拼
```
- 再次重启 Home Assistant
- 启动成功后，如无报错，你的油价插件就已安装完成

## 查看是否成功：

- 开发者工具-状态-实体-输入筛选实体
- 输入刚才你定义的名字『油价』
- 查看是否有数据，形如：
<img width="1096" alt="image" src="https://user-images.githubusercontent.com/6293952/191035727-7dfe0de3-2693-48c6-9300-7364d247338a.png">


## 面板调用：

- 打开概览页面-右上角三个点-编辑仪表盘
- 右下角添加卡片-搜索「markdown」，添加markdown卡片
<img width="998" alt="image" src="https://user-images.githubusercontent.com/6293952/191036228-62cf66c5-aa2b-4f27-9c86-39bef9d57378.png">
- 标题按照喜好输入，内容直接拷贝仓库中提供的横排或竖排的代码即可。
- 保存，完成编辑，查看效果。
