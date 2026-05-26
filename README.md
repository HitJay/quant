# Quant

量化交易研究与实盘系统。

## 项目结构

```
quant/
├── src/quant/       # 核心代码
├── tests/           # 单元测试
├── notebooks/       # Jupyter 回测/分析
└── data/            # 数据文件（gitignore 管理）
```

## 开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 功能

- 数据获取与清洗
- 策略回测框架
- 实盘交易接口
