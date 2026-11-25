# SurgMark · 术标

本地运行的手术视频标注与 AI 辅助审核工具。Surg 来自 Surgery，Mark 表示标注；中文名“术标”便于记忆。

支持 Windows 和 macOS 浏览器。手动标注可直接打开 `index.html`；AI 功能需运行本机 Python 服务。

## 功能

- 视频播放、倍速、按设定帧率步进、起止时间标注。
- 内置组织分离动作、缝合动作、缝合子阶段，支持自定义标签和人工技能评分。
- CLIP 抽帧生成候选片段；医生逐段确认、拒绝、改标、调整边界。
- SlimSAM 点击分割当前帧，导出透明 PNG 掩码。
- JSON 项目保存恢复，CSV 导出模型来源、相似度、审核状态及审核人。

## 安装和启动

推荐 Python 3.11。下载并解压本仓库，进入项目目录。

```sh
python -m venv .venv
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
```

macOS 终端（创建环境时也可使用 `python3`）：

```sh
source .venv/bin/activate
```

安装依赖、首次下载模型、启动本机服务：

```sh
python -m pip install -r requirements.txt
python download_models.py
python server.py
```

打开 http://127.0.0.1:8765 。首次模型下载需要联网；权重不随源码分发。后续推理从本地读取权重，视频帧仅发送到本机服务。自动选择 CUDA、Apple MPS 或 CPU，速度取决于硬件。

## 使用

1. 选择本地视频，建议 MP4 H.264。
2. 填写病例编号与标注者，选择标签类型。
3. 手动使用 I/O 设定片段起止，Enter 保存；或生成 AI 候选。
4. 医生逐段确认、拒绝或编辑，调整抽样造成的边界偏差。
5. 下载 JSON 保存项目；导出 CSV 后筛选 `status=accepted` 使用已确认标注。
6. SAM 分割时暂停视频，点击“SAM 分割当前帧”，在预览中点击目标。

JSON 不含视频和分割掩码；视频及 PNG 需单独保留。浏览器缓存可能被清除，请定期下载项目。

## 当前能力与验证范围

这是研究原型。通用 CLIP 使用单帧与英文描述的相似度生成候选，没有手术专用的时序动作理解；相似度不是识别准确率。抽样可能遗漏短动作，边界必须审核。技能等级由人工评分。重复生成会增加候选，不会覆盖既有标注。

SlimSAM 仅分割当前帧，未实现视频目标追踪或由分割推断动作。帧步进按时间计算，不保证可变帧率视频逐编码帧精确定位。

已完成 Python 编译、前端脚本语法检查及 5 项本机接口测试；尚未完成真实手术视频模型推理、准确率评估及 Windows/macOS 双平台完整验证。没有 EXE/DMG 安装包。

运行接口测试：

```sh
python -m unittest discover -s . -p test_server.py
```

## 方法依据与模型

标注流程参考 [Nature Biomedical Engineering 论文](https://doi.org/10.1038/s41551-023-01010-8) 的 Methods：Surgical video samples and annotations。论文未披露标注软件名称；SurgMark 是独立实现，不是作者原软件。

- [CLIP](https://huggingface.co/openai/clip-vit-base-patch32)：动作候选的通用图文相似度模型。
- [SlimSAM](https://huggingface.co/Zigeng/SlimSAM-uniform-50)：SAM 架构的轻量分割模型。

模型权重的使用须遵循各自发布条款。仓库只包含工具源码和说明，不包含论文 PDF、患者视频、模型权重或个人标注数据。
