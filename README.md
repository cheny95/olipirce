# 油价 HomeAssistant集成

![yaofan](https://user-images.githubusercontent.com/6293952/196037499-17ef6aec-9fe4-4fc2-a4ac-811a12bfb380.jpg)

<a name="install"></a>
## 安装/更新

> 以下两种方法任选其一！

#### 方法1: [HACS (**点击这里安装**)](https://my.home-assistant.io/redirect/hacs_repository/?owner=cheny95&repository=olipirce&category=integration)

#### 方法2: 通过 Samba / SFTP 手动安装
> [下载](https://github.com/cheny95/olipirce/archive/main.zip)解压并复制`custom_components/oilprice`文件夹到HA配置目录下的`custom_components`文件夹

## 使用方法：
- 安装完毕后重启Home Assistant。
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
<img width="1765" alt="image" src="https://user-images.githubusercontent.com/6293952/191039960-5a75aa65-6066-41c5-a94e-03d4a2d3f546.png">

- 保存，完成编辑，查看效果。

## 交流
- QQ群：198841186

- 微信群：(添加该机器人，发送“进群”会自动发送邀请链接）
  
![xiaomi miot weixin group](https://user-images.githubusercontent.com/4549099/161735971-0540ce1c-eb49-4aff-8cb3-3bdad15e22f7.png)
