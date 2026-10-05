# DesignAI-Curriculum / Study Engine

AI for Architecture 的课程内容、网站生成引擎与视频工具。

## 当前使用目录

`Prototype_Phase-01/` 是当前运行和部署目录，已合并 `Backend_10032026/` 最新版本。Vercel 继续从此目录构建。

```bash
cd Prototype_Phase-01
python3 engine/build.py --serve
```

也可双击 Mac 的 `WEBSITE.command` 或 Windows 的 `WEBSITE.bat`。视频与幻灯片分别使用 `VIDEOS-4K` 和 `SLIDES-4K`。完整说明见 [运行文档](Prototype_Phase-01/README.md)。

## 目录说明

- `Prototype_Phase-01/`：当前源码、课程、素材、测试及本地生成的视频和网站。
- `Backend_10032026/`：此次导入的原始新版文件，仅在本地保留作参考，不提交到 Git。
- `course_files_export/`：原有课程导出资料。
- `output/`、`tmp/`：原有输出与临时目录。

此次合并保留了本地修改的两处课程解锁提示文案；保留旧版运行脚本以兼容现有使用方式。新版缓存未导入，网站从合并后的源码重新生成。合并前备份及逐文件清单位于上一级 `study-engine-backups/merge-20261004-204701/`。
