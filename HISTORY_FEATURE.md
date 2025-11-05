# 历史净值数据抓取功能说明

## 功能概述

本功能允许您获取基金的历史净值数据，支持按天数筛选（如最近7天、30天、90天等）。

## 最新更新 (2025-11-04)

**问题修复**: 修复了历史数据抓取功能无法正常工作的问题。

### 问题原因
东方财富基金API返回的数据格式是JavaScript变量（`var apidata={content:"...HTML表格...", records:XX}`），而不是纯JSON格式。原代码尝试使用`response.json()`直接解析导致失败。

### 解决方案
- 使用正则表达式提取HTML表格内容
- 使用BeautifulSoup解析HTML表格
- 正确提取日期、净值、增长率等字段
- 添加详细的错误日志和调试信息

### 验证测试
✓ 已验证支持多种类型基金：
- 普通开放式基金（如 110022）
- 场内ETF基金（如 518660）
- 混合型基金（如 000001）

✓ 已验证功能：
- 单基金历史数据获取
- 批量基金历史数据获取
- CSV格式导出
- JSON格式导出

## 使用方式

### 命令行使用

#### 获取单个基金的历史数据

```bash
# 获取基金 110022 最近30天的历史数据
python scrape_funds.py -c 110022 --history 30

# 获取基金 110022 最近90天的历史数据
python scrape_funds.py -c 110022 --history 90

# 获取基金 110022 最近7天的历史数据
python scrape_funds.py -c 110022 --history 7
```

#### 批量获取历史数据

```bash
# 获取多个基金的最近30天历史数据
python scrape_funds.py -c 110022 161725 163402 --history 30

# 从文件读取基金列表，获取最近30天的历史数据
python scrape_funds.py -f funds.txt --history 30

# 从JSON文件读取基金列表，获取最近90天的历史数据
python scrape_funds.py -f funds.json --history 90
```

#### 保存历史数据

```bash
# 保存为CSV文件
python scrape_funds.py -c 110022 --history 30 -o fund_history.csv

# 保存为JSON文件
python scrape_funds.py -c 110022 --history 30 -o fund_history.json

# 批量保存多个基金的历史数据
python scrape_funds.py -f funds.txt --history 30 -o history.csv
```

#### 交互模式

```bash
# 不提供参数，进入交互模式
python scrape_funds.py
```

在交互模式下，您可以：
1. 输入基金代码（支持多个，用逗号分隔）
2. 选择是否获取详细信息
3. 选择是否获取历史数据，并指定天数
4. 选择输出格式（CSV、JSON 或 显示在终端）

### Python API 使用

#### 获取单个基金的历史数据

```python
from fund_scraper import FundScraper

scraper = FundScraper(timeout=10, delay=0.5)

# 获取基金 110022 最近30天的历史数据
history = scraper.get_fund_history('110022', days=30)

if history:
    print(f"获取 {len(history)} 条历史记录")
    for record in history[:5]:
        print(f"日期: {record['date']}, 净值: {record['unit_net_value']}, 增长率: {record['growth_rate']}")
```

#### 批量获取多个基金的历史数据

```python
from fund_scraper import FundScraper

scraper = FundScraper(timeout=10, delay=0.5)

# 基金代码列表
fund_codes = ['110022', '161725', '163402']

# 获取最近30天的历史数据
history_data = scraper.get_multiple_funds_history(fund_codes, days=30)

# 输出统计信息
for fund_code, records in history_data.items():
    print(f"基金 {fund_code}: {len(records)} 条历史记录")
```

#### 保存历史数据

```python
from fund_scraper import FundScraper

scraper = FundScraper()

# 获取历史数据
fund_codes = ['110022', '161725']
history_data = scraper.get_multiple_funds_history(fund_codes, days=30)

# 保存为CSV
scraper.save_history_to_csv(history_data, 'fund_history.csv')

# 保存为JSON
scraper.save_history_to_json(history_data, 'fund_history.json')
```

#### 分析历史数据

```python
import pandas as pd
from fund_scraper import FundScraper

scraper = FundScraper()

# 获取历史数据
fund_codes = ['110022', '161725']
history_data = scraper.get_multiple_funds_history(fund_codes, days=30)

# 将数据转换为DataFrame进行分析
for fund_code, records in history_data.items():
    df = pd.DataFrame(records)
    
    # 按日期排序
    df = df.sort_values('date')
    
    # 计算统计信息
    print(f"\n基金 {fund_code} 统计:")
    print(f"  最高净值: {df['unit_net_value'].max()}")
    print(f"  最低净值: {df['unit_net_value'].min()}")
    print(f"  平均净值: {df['unit_net_value'].mean():.4f}")
    
    # 显示前5条记录
    print(f"\n前5条记录:")
    print(df[['date', 'unit_net_value', 'accumulated_net_value', 'growth_rate']].head())
```

## 数据格式

### CSV格式

```
fund_code,date,unit_net_value,accumulated_net_value,daily_growth_rate,growth_rate
110022,2025-01-15,5.8234,5.8234,0,1.23%
110022,2025-01-14,5.7546,5.7546,0,-0.56%
161725,2025-01-15,2.1567,2.1567,0,0.45%
```

### JSON格式

```json
{
  "110022": [
    {
      "fund_code": "110022",
      "date": "2025-01-15",
      "unit_net_value": 5.8234,
      "accumulated_net_value": 5.8234,
      "daily_growth_rate": 0,
      "growth_rate": "1.23%"
    },
    {
      "fund_code": "110022",
      "date": "2025-01-14",
      "unit_net_value": 5.7546,
      "accumulated_net_value": 5.7546,
      "daily_growth_rate": 0,
      "growth_rate": "-0.56%"
    }
  ]
}
```

## 返回数据字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| fund_code | str | 基金代码 |
| date | str | 净值日期（YYYY-MM-DD格式） |
| unit_net_value | float | 单位净值 |
| accumulated_net_value | float | 累计净值 |
| daily_growth_rate | float | 日增长率（数值） |
| growth_rate | str | 日增长率（百分比字符串，如 "1.23%"） |

## 常见问题

### Q: 如何获取更长时间的历史数据？

A: 可以通过增加 `days` 参数来获取更长时间的数据：

```bash
# 获取最近180天的历史数据
python scrape_funds.py -c 110022 --history 180

# 获取最近一年的历史数据（约365天）
python scrape_funds.py -c 110022 --history 365
```

### Q: 历史数据的获取速度很慢，如何加快？

A: 可以通过减少请求延迟来加快速度（但要注意反爬虫对策）：

```bash
# 减少延迟到0.1秒
python scrape_funds.py -c 110022 --history 30 -l 0.1
```

或在Python代码中：

```python
scraper = FundScraper(timeout=10, delay=0.1)
```

### Q: 获取历史数据时出错，如何调试？

A: 可以在Python中直接调试：

```python
from fund_scraper import FundScraper

scraper = FundScraper()

# 获取单个基金的历史数据，查看输出信息
history = scraper.get_fund_history('110022', days=7)

if history:
    print(f"成功获取 {len(history)} 条记录")
    print(history[0])  # 打印第一条记录
else:
    print("获取失败")
```

### Q: 如何将历史数据导入Excel？

A: 保存为CSV格式后，可以直接用Excel打开：

```bash
python scrape_funds.py -c 110022 161725 --history 30 -o fund_history.csv
```

然后在Excel中打开 `fund_history.csv` 文件。

### Q: 支持哪些时间范围？

A: `days` 参数没有上限，可以指定任意天数。但请注意：
- 基金历史数据从基金成立日期开始
- 如果指定的天数超过基金历史数据范围，将返回全部可用数据
- 建议每次请求不超过365天，避免过度占用服务器资源

## 性能提示

1. **批量操作**: 一次性获取多个基金的数据，而不是多次调用
   ```python
   # 推荐
   history_data = scraper.get_multiple_funds_history(['110022', '161725'], days=30)
   
   # 不推荐
   h1 = scraper.get_fund_history('110022', days=30)
   h2 = scraper.get_fund_history('161725', days=30)
   ```

2. **合理设置延迟**: 平衡速度和反爬虫对策
   ```python
   # 默认延迟
   scraper = FundScraper(delay=0.5)
   
   # 增加延迟（更安全）
   scraper = FundScraper(delay=1.0)
   ```

3. **缓存结果**: 获取数据后保存为本地文件，避免重复请求
   ```python
   history_data = scraper.get_multiple_funds_history(fund_codes, days=30)
   scraper.save_history_to_csv(history_data, 'fund_history.csv')
   ```

## 注意事项

1. 请遵守网站的 `robots.txt` 和使用协议
2. 不要过度频繁地抓取数据
3. 建议合理设置请求延迟
4. 某些基金可能没有完整的历史数据
5. 数据源来自天天基金网，如有更新延迟，属正常现象
