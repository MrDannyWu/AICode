# 历史数据抓取功能修复说明

## 问题描述

运行历史数据抓取时出现错误：
```
[1/1] 正在获取基金 518660 的历史数据...
无法解析基金 518660 的历史数据
未获取到基金 518660 的历史数据
未获取到任何历史数据
```

## 问题根源

东方财富基金历史数据API (`http://fund.eastmoney.com/f10/F10DataApi.aspx`) 返回的并非标准JSON格式，而是一个JavaScript变量声明：

```javascript
var apidata={ content:"<table>...HTML表格...</table>", records:1328, pages:28, curpage:1}
```

原代码使用 `response.json()` 尝试解析JSON，导致解析失败。

## 修复方案

### 1. 修改解析逻辑

在 `fund_scraper.py` 的 `get_fund_history()` 方法中：

**修改前**:
```python
try:
    data = response.json()
except json.JSONDecodeError:
    print(f"无法解析基金 {fund_code} 的历史数据")
    break

datas = data.get('Data', {}).get('LSJZList', [])
```

**修改后**:
```python
# 提取HTML内容
content_match = re.search(r'content:"(.*?)",records', response.text, re.DOTALL)
if not content_match:
    print(f"基金 {fund_code} 第{page}页: 未找到content字段")
    break

html_content = content_match.group(1)

# 使用BeautifulSoup解析表格
soup = BeautifulSoup(html_content, 'lxml')
table = soup.find('table')

# 解析表格行
rows = tbody.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    # 提取日期、净值、增长率等字段
```

### 2. 改进错误处理

添加了更详细的错误信息和调试日志：
- 显示请求URL
- 分页信息
- 数据解析进度
- 完整的异常堆栈跟踪

### 3. 增强数据验证

- 验证日期格式 (YYYY-MM-DD)
- 验证数值类型转换
- 处理空值和异常值
- 正确筛选日期范围

## 测试验证

### 测试的基金类型

✓ **110022** - 易方达消费行业（普通开放式基金）
✓ **518660** - 黄金ETF（场内基金）
✓ **000001** - 华夏成长（混合型基金）

### 测试的功能

✓ 单基金历史数据获取
✓ 批量基金历史数据获取
✓ CSV格式导出
✓ JSON格式导出
✓ 命令行工具
✓ Python API

### 测试结果

所有测试通过 (6/6):
```
✓ PASS - 单基金测试: 110022
✓ PASS - 单基金测试: 518660
✓ PASS - 单基金测试: 000001
✓ PASS - 批量获取测试: multiple
✓ PASS - CSV导出测试: export
✓ PASS - JSON导出测试: export
```

## 使用示例

### 命令行

```bash
# 获取单个基金的30天历史数据
python scrape_funds.py -c 518660 --history 30

# 批量获取并导出为CSV
python scrape_funds.py -c 110022 518660 000001 --history 30 -o history.csv

# 从文件读取基金列表
python scrape_funds.py -f funds.txt --history 90 -o history.json
```

### Python API

```python
from fund_scraper import FundScraper

scraper = FundScraper()

# 获取单个基金历史数据
history = scraper.get_fund_history('518660', days=30)
print(f"获取到 {len(history)} 条记录")

# 批量获取
history_data = scraper.get_multiple_funds_history(['110022', '518660'], days=30)

# 导出
scraper.save_history_to_csv(history_data, 'history.csv')
scraper.save_history_to_json(history_data, 'history.json')
```

## 输出示例

### CSV格式
```csv
fund_code,date,unit_net_value,accumulated_net_value,growth_rate
518660,2025-11-04,8.7654,2.2716,-0.38%
518660,2025-11-03,8.7990,2.2803,-0.16%
518660,2025-10-31,8.8133,2.2840,1.60%
```

### JSON格式
```json
{
  "518660": [
    {
      "fund_code": "518660",
      "date": "2025-11-04",
      "unit_net_value": 8.7654,
      "accumulated_net_value": 2.2716,
      "growth_rate": "-0.38%"
    }
  ]
}
```

## 相关文件

- `fund_scraper.py` - 核心修复代码
- `test_history_fix.py` - 完整的测试脚本
- `example_usage.py` - 新增示例函数 `example_11_test_different_fund_types()`
- `HISTORY_FEATURE.md` - 历史数据功能完整文档

## 注意事项

1. API返回的是HTML表格，需要使用BeautifulSoup解析
2. 表格结构：7列（净值日期、单位净值、累计净值、日增长率、申购状态、赎回状态、分红送配）
3. 我们主要提取前4列数据
4. 日期格式为 YYYY-MM-DD
5. 增长率包含百分号（如 "1.23%"）

## 验收标准完成情况

- [x] 能够成功获取110022的历史数据
- [x] 能够成功获取518660等ETF的历史数据  
- [x] 提供详细的调试日志帮助定位问题
- [x] 错误信息清晰明确
- [x] 历史数据能正确导出为CSV和JSON
- [x] 更新README说明历史数据功能的使用方法
