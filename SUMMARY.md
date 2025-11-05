# 修复摘要

## 问题
历史数据抓取功能无法工作，显示"无法解析基金的历史数据"错误。

## 根本原因
东方财富基金API返回的是JavaScript变量格式，包含HTML表格，而非纯JSON。

## 解决方案
修改 `fund_scraper.py` 中的 `get_fund_history()` 方法：
- 使用正则表达式提取HTML内容
- 使用BeautifulSoup解析HTML表格
- 增强错误处理和日志

## 测试结果
✓ 所有6个测试全部通过
✓ 支持普通基金、ETF、混合型基金
✓ CSV和JSON导出功能正常

## 快速验证

```bash
# 测试单个基金
python3 scrape_funds.py -c 518660 --history 30

# 测试多个基金并导出
python3 scrape_funds.py -c 110022 518660 000001 --history 30 -o history.csv

# 运行完整测试套件
python3 test_history_fix.py
```

## 相关文件
- `fund_scraper.py` - 核心修复代码
- `test_history_fix.py` - 验证测试脚本
- `FIX_NOTES.md` - 详细修复说明
- `HISTORY_FEATURE.md` - 功能文档（含修复说明）
