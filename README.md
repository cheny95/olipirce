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
- 打开 **设置 -> 设备与服务 -> 添加集成**
- 搜索并选择 **油价 (Oil Price)**
- 在弹窗中选择地区
- 设置更新周期（小时），默认 12 小时
- 点击提交后，集成会自动创建油价实体
- 如果地区重复或网络不可用，界面会给出友好错误提示
- 会额外创建一个“立即更新”按钮实体，点击后会立刻拉取最新油价

### 修改更新周期

- 进入 **设置 -> 设备与服务 -> 油价 -> 配置**
- 可修改“更新周期（小时）”，保存后会自动重载并应用新周期

> 说明：新版本无需在`configuration.yaml`中配置`platform: oilprice`。

## 查看是否成功：

- 开发者工具-状态-实体-输入筛选实体
- 输入实体名（默认是「油价-地区」）
- 点击实体可查看属性：`gas92`、`gas95`、`gas98`、`die0`、`time`、`tips`、`update_time`、`region`、`region_name`
- 查看是否有数据，形如：
<img width="1096" alt="image" src="https://user-images.githubusercontent.com/6293952/191035727-7dfe0de3-2693-48c6-9300-7364d247338a.png">


## 面板调用：

1. 打开概览页面，点击右上角三个点，进入「编辑仪表盘」。
2. 点击右下角「添加卡片」，选择「手动」。
3. 粘贴模板代码（任选其一）：
   - 亮色版：`油价卡片模板.yaml`
   - 深色版：`油价卡片模板-深色.yaml`
4. 把模板中的实体替换为你自己的实体（重点改这两个）：
   - `sensor.you_jia_beijing`
   - `button.you_jia_refresh_beijing`
5. 保存卡片后返回概览，即可查看油价并点击“立即更新”。

> 提示：如果你添加的是其他地区，只需要把 `beijing` 改成对应地区代码即可。

## 交流
- QQ群：198841186

- 微信群：(添加该机器人，发送“进群”会自动发送邀请链接）
  
![xiaomi miot weixin group](https://user-images.githubusercontent.com/4549099/161735971-0540ce1c-eb49-4aff-8cb3-3bdad15e22f7.png)
