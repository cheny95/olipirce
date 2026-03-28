# 油价 HomeAssistant集成

![yaofan](https://user-images.githubusercontent.com/6293952/196037499-17ef6aec-9fe4-4fc2-a4ac-811a12bfb380.jpg)

<a name="install"></a>
## 安装/更新

> 以下两种方法任选其一！

#### 方法1: [HACS (**点击这里安装**)](https://my.home-assistant.io/redirect/hacs_repository/?owner=cheny95&repository=oilprice-for-homeassistant&category=integration)

#### 方法2: 通过 Samba / SFTP 手动安装
> [下载](https://github.com/cheny95/oilprice-for-homeassistant/archive/main.zip)解压并复制`custom_components/oilprice`文件夹到HA配置目录下的`custom_components`文件夹

## 使用方法：
- 安装完毕后重启Home Assistant。
- 打开 **设置 -> 设备与服务 -> 添加集成**
- 搜索并选择 **油价 (Oil Price)**
- 在弹窗中选择地区
- 设置更新周期（小时），默认 12 小时
- 点击提交后，集成会自动创建油价实体
- 如果地区重复或网络不可用，界面会给出友好错误提示
- 会额外创建一个“立即更新”按钮实体，点击后会立刻拉取最新油价

<img width="584" height="351" alt="image" src="https://github.com/user-attachments/assets/a92967a9-0186-4b1c-9ae2-cf7474a97584" />
<img width="981" height="736" alt="image" src="https://github.com/user-attachments/assets/e45ecc58-2e77-4322-b0bd-79528a663ec7" />
<img width="625" height="597" alt="ac10fd4dc1ae4b9835304c67a00dd81e" src="https://github.com/user-attachments/assets/1449407b-7f44-4812-8297-8f7c0c543d18" />


## 升级说明（重要）

- 本次升级已从“单实体 + 多属性”模式升级为“多实体状态”模式。
- ~~旧命名 `you_jie` 已统一迁移为 `you_jia`~~。
- ~~升级后会自动执行：~~
  - ~~旧实体重命名（`you_jie -> you_jia`）~~
  - ~~旧单实体自动清理~~
  - ~~新按钮命名规范化 ~~
- ~~如升级后仍看到旧实体，请重启 Home Assistant 或重载一次本集成。~~

### 新实体模型（示例：北京）

- `sensor.you_jie_bei_jing_gas92`
- `sensor.you_jie_bei_jing_gas95`
- `sensor.you_jie_bei_jing_gas98`
- `sensor.you_jie_bei_jing_die0`
- `sensor.you_jie_bei_jing_time`
- `sensor.you_jie_bei_jing_tips`
- `sensor.you_jie_bei_jing_update_time`
- `sensor.you_jie_bei_jing_friendly_name`
- `button.you_jie_bei_jing_refresh`

### 修改更新周期

- 进入 **设置 -> 设备与服务 -> 油价 -> 配置**
- 可修改“更新周期（小时）”，保存后会自动重载并应用新周期

> 说明：新版本无需在`configuration.yaml`中配置`platform: oilprice`。

## 查看是否成功：

- 开发者工具-状态-实体-输入筛选实体
- 输入 `油价` 关键字进行筛选
- 确认已生成多个独立实体（如 `sensor.you_jie_bei_jing_gas92`）
- 点击 `button.you_jie_bei_jing_refresh` 可立即刷新油价
- 查看是否有数据，形如：
<img width="1267" height="918" alt="image" src="https://github.com/user-attachments/assets/6a9f1f20-1ee9-40f3-982b-3c2e0c7b699b" />

## 面板调用：

1. 打开概览页面，点击右上角三个点，进入「编辑仪表盘」。
2. 点击右下角「添加卡片」，选择「手动」。
3. 粘贴模板代码（任选其一）：
   - 亮色版：`油价卡片模板.yaml`
   - 深色版：`油价卡片模板-深色.yaml`
4. 把模板中的实体替换为你自己的实体（重点改这两个）：
   - `sensor.you_jie_bei_jing_gas92`（及同地区的其它 `sensor.you_jie_bei_jing_*`）
   - `button.you_jie_bei_jing_refresh`
5. 保存卡片后返回概览，即可查看油价并点击“立即更新”。

> 提示：如果你添加的是其他地区，只需要把实体中的 `bei_jing` 替换为对应地区 slug。

## 交流
- QQ群：198841186

- 微信群：(添加该机器人，发送“进群”会自动发送邀请链接）
  
![xiaomi miot weixin group](https://user-images.githubusercontent.com/4549099/161735971-0540ce1c-eb49-4aff-8cb3-3bdad15e22f7.png)
