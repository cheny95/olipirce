# 更新日志

## v1.0.1

### 新增
- 全面切换为 UI 配置流程（无需 `configuration.yaml`）。
- 新增“更新周期（小时）”配置：必填数字输入，默认 `12`，范围 `1-168`。
- 新增设备控制按钮：`button.you_jia_<region_slug>_refresh`，点击后立即刷新。
- 新增亮色/深色 Lovelace 模板：`油价卡片模板.yaml`、`油价卡片模板-深色.yaml`。

### 变更
- 传感器模型从“单实体+属性”升级为“多实体状态输出”。
- 统一命名规则：`you_jie` -> `you_jia`。
- 油价字段改为独立状态实体（示例：北京）：
  - `sensor.you_jia_bei_jing_gas92`
  - `sensor.you_jia_bei_jing_gas95`
  - `sensor.you_jia_bei_jing_gas98`
  - `sensor.you_jia_bei_jing_die0`
  - `sensor.you_jia_bei_jing_time`
  - `sensor.you_jia_bei_jing_tips`
  - `sensor.you_jia_bei_jing_update_time`
  - `sensor.you_jia_bei_jing_friendly_name`

### 迁移
- 自动迁移旧命名：`you_jie` -> `you_jia`。
- 自动清理旧单实体模型，避免和新多实体并存。
- 自动规范按钮实体命名。

### 可能影响（Breaking Changes）
- 旧卡片若读取 `state_attr(sensor.xxx, 'gas92')`，需改为读取独立实体状态（如 `states('sensor.you_jia_bei_jing_gas92')`）。
- 升级后建议重启 Home Assistant 或重载一次本集成以完成迁移。

