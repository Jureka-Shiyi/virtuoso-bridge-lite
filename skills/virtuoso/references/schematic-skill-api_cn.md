# Schematic 参考

## 编辑模式

```python
from virtuoso_bridge.virtuoso.schematic import (
    schematic_create_inst_by_master_name as inst,
    schematic_create_pin as pin,
    schematic_create_wire_between_instance_terms as wire,
    schematic_label_instance_term as label,
)

with client.schematic.edit(lib, cell) as sch:
    sch.add(inst("analogLib", "vdc", "symbol", "V0", 0, 0, "R0"))
    sch.add(inst("analogLib", "gnd", "symbol", "GND0", 0, -0.5, "R0"))
    sch.add(wire("V0", "MINUS", "GND0", "gnd!"))
    sch.add(label("V0", "PLUS", "VDD"))
    sch.add(pin("VDD", 0, 1.0, "R0", direction="inputOutput"))
    sch.add_net_label_to_transistor("M0", drain_net="OUT", gate_net="IN",
        source_net="VSS", body_net="VSS")
```

`sch.add(skill_cmd)` 排队 SKILL 命令；`schCheck` + `dbSave` 在上下文退出时运行。

## CDF 参数设置

对 PDK 器件使用 `set_instance_params`——处理 `schHiReplace` + CDF 回调：

```python
from virtuoso_bridge.virtuoso.schematic.params import set_instance_params

set_instance_params(client, "MP0", w="500n", l="30n", nf="4", m="2")
```

对 analogLib 器件，直接 CDF 访问可以工作：

```python
client.execute_skill(
    'cdfFindParamByName(cdfGetInstCDF('
    'car(setof(i geGetEditCellView()~>instances i~>name == "R0")))'
    ' "r")~>value = "1k"')
client.execute_skill('dbSave(geGetEditCellView())')
```

## 读取放置

```python
from virtuoso_bridge.virtuoso.schematic.reader import read_placement

p = read_placement(client, "myLib", "myCell")
for i in p["instances"]:
    print(i["name"], i["xy"], i["orient"])
```

## 技巧

- 对 MOS D/G/S/B 使用 `add_net_label_to_transistor`——自动检测 stub 方向
- 使用 `schematic_label_instance_term` / `schematic_create_wire_between_instance_terms` 而不是猜测坐标
- **仿真前检查并保存**：`schCheck` + `dbSave`——否则网表生成会失败并弹出一个阻塞对话框
- **原理图应在 GUI 中打开**，Maestro 才能正确引用它

## 另见

- `references/schematic-python-api.md`——Python API 参考
