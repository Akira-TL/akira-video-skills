# Akira Video Resume Blackbox Fixture 001

用于验证跨会话恢复、用户返回四视图候选、候选选择、稳定归档、清理临时返回，以及只为当前可执行镜头创建下一批视频生成包。

`source/` 为只读 tracked input；所有验收修改只能进入 `output/`。
