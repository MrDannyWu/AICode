# 基金数据抓取脚本

一个强大的Python脚本，用于从天天基金网（eastmoney.com）抓取基金数据。

## 功能特性

### 支持的数据类型

#### 1. 基金基本信息
- 基金代码
- 基金名称
- 基金类型
- 基金公司
- 基金经理

#### 2. 基金净值数据
- 单位净值（最新）
- 累计净值
- 日增长率
- 数据更新日期

#### 3. 历史业绩数据（可选）
- 近1月、3月、6月、1年收益率
- 成立以来收益率
- 3年、5年收益率

#### 4. 历史净值数据
- 历史单位净值
- 历史累计净值
- 历史日增长率
- 支持按天数筛选（如最近7天、30天、90天等）

### 输出格式
- **CSV格式** - 易于导入Excel和其他工具
- **JSON格式** - 适合程序化处理
- **DataFrame** - 可在Python中进一步分析

### 特性
- ✅ 智能反爬虫对策（自定义User-Agent、请求延迟）
- ✅ 完善的错误处理和异常捕获
- ✅ 支持单个或批量抓取
- ✅ 支持详细和简略两种模式
- ✅ 命令行工具和编程接口两种使用方式
- ✅ 详细的日志输出

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

#### 方式一：直接运行脚本

```bash
# 简单模式 - 直接运行，使用默认基金代码
python fund_scraper.py
```

#### 方式二：使用命令行工具

```bash
# 抓取单个基金
python scrape_funds.py -c 110022

# 抓取多个基金
python scrape_funds.py -c 110022 161725 163402

# 从文件读取基金代码
python scrape_funds.py -f funds_example.txt
python scrape_funds.py -f funds_example.json

# 获取详细信息
python scrape_funds.py -c 110022 -d

# 保存为CSV
python scrape_funds.py -c 110022 -o output.csv

# 保存为JSON
python scrape_funds.py -c 110022 -o output.json

# 完整示例：获取详细信息并保存为JSON
python scrape_funds.py -c 110022 161725 163402 -d -o funds_data.json

# 获取历史数据
python scrape_funds.py -c 110022 --history 30  # 最近30天
python scrape_funds.py -c 110022 --history 90  # 最近90天

# 批量抓取历史数据
python scrape_funds.py -f funds.txt --history 30 -o history.csv

# 交互模式（不提供参数）
python scrape_funds.py
```

## 详细使用说明

### 命令行参数

```
-c, --codes CODES           基金代码列表 (例: 110022 161725 163402)
-f, --file FILE             读取基金代码的文件路径 (.txt 或 .json)
-d, --detailed              获取详细信息（基金公司、经理等）
--history DAYS              获取历史净值数据，指定天数 (例: 30, 90)
-t, --timeout TIMEOUT       请求超时时间，秒（默认: 10）
-l, --delay DELAY           请求间隔时间，秒（默认: 0.5）
-o, --output OUTPUT         输出文件路径 (.csv 或 .json)
-h, --help                  显示帮助信息
```

### Python编程接口

#### 基本示例

```python
from fund_scraper import FundScraper

# 创建爬虫实例
scraper = FundScraper(timeout=10, delay=0.5)

# 抓取单个基金
fund_data = scraper.scrape_fund('110022', detailed=False)
print(fund_data)

# 抓取多个基金
fund_codes = ['110022', '161725', '163402']
results = scraper.scrape_multiple_funds(fund_codes, detailed=False)

# 转换为DataFrame
df = scraper.to_dataframe(results)
print(df)

# 保存为CSV
scraper.save_to_csv(df, 'funds.csv')

# 保存为JSON
scraper.save_to_json(results, 'funds.json')
```

#### 获取详细信息

```python
from fund_scraper import FundScraper

scraper = FundScraper()

# 抓取详细信息
fund_data = scraper.scrape_fund('110022', detailed=True)

# 输出包含的字段
print(fund_data.keys())
# dict_keys(['fund_code', 'fund_name', 'unit_net_value', 'accumulated_net_value', 
#            'daily_growth_rate', 'update_date', 'fund_type', 'fund_company', 
#            'fund_manager', ...])
```

#### 高级用法

```python
from fund_scraper import FundScraper
import pandas as pd

scraper = FundScraper(timeout=15, delay=1.0)

# 抓取基金列表
fund_codes = ['110022', '161725', '163402', '519674', '470018']
results = scraper.scrape_multiple_funds(fund_codes, detailed=True)

# 数据分析
df = scraper.to_dataframe(results)

# 按净值排序
df_sorted = df.sort_values('unit_net_value', ascending=False)

# 过滤基金
growth_funds = df[df['daily_growth_rate'] > 0]

# 保存结果
scraper.save_to_csv(df_sorted, 'sorted_funds.csv')
scraper.save_to_json(results, 'funds.json')
```

#### 历史数据抓取

```python
from fund_scraper import FundScraper

scraper = FundScraper(timeout=10, delay=0.5)

# 获取单个基金的历史数据
history = scraper.get_fund_history('110022', days=30)
print(f"获取 {len(history)} 条历史记录")

# 批量获取多个基金的历史数据
fund_codes = ['110022', '161725', '163402']
history_data = scraper.get_multiple_funds_history(fund_codes, days=30)

# 保存为CSV
scraper.save_history_to_csv(history_data, 'fund_history.csv')

# 保存为JSON
scraper.save_history_to_json(history_data, 'fund_history.json')

# 分析历史数据
for fund_code, records in history_data.items():
    df = pd.DataFrame(records)
    print(f"\n基金 {fund_code}:")
    print(df[['date', 'unit_net_value', 'daily_growth_rate']])
```

### 配置文件格式

#### JSON格式 (funds_example.json)

```json
{
  "funds": [
    "110022",
    "161725",
    "163402",
    "519674",
    "470018"
  ]
}
```

#### 文本格式 (funds_example.txt)

```
110022
161725
163402
519674
470018
```

## 输出数据示例

### CSV格式
```
fund_code,fund_name,unit_net_value,accumulated_net_value,daily_growth_rate,update_date
110022,易方达消费行业,5.8234,5.8234,0.12,2024-01-15
161725,招商中证白酒,2.1567,2.1567,-0.45,2024-01-15
```

### JSON格式
```json
[
  {
    "fund_code": "110022",
    "fund_name": "易方达消费行业",
    "unit_net_value": 5.8234,
    "accumulated_net_value": 5.8234,
    "daily_growth_rate": 0.12,
    "update_date": "2024-01-15"
  },
  {
    "fund_code": "161725",
    "fund_name": "招商中证白酒",
    "unit_net_value": 2.1567,
    "accumulated_net_value": 2.1567,
    "daily_growth_rate": -0.45,
    "update_date": "2024-01-15"
  }
]
```

### 历史数据格式

#### CSV格式
```
fund_code,date,unit_net_value,accumulated_net_value,daily_growth_rate,growth_rate
110022,2025-01-15,5.8234,5.8234,0,1.23%
110022,2025-01-14,5.7546,5.7546,0,-0.56%
161725,2025-01-15,2.1567,2.1567,0,0.45%
```

#### JSON格式
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
  ],
  "161725": [
    {
      "fund_code": "161725",
      "date": "2025-01-15",
      "unit_net_value": 2.1567,
      "accumulated_net_value": 2.1567,
      "daily_growth_rate": 0,
      "growth_rate": "0.45%"
    }
  ]
}
```

## 常见基金代码参考

| 基金名称 | 代码 | 类型 |
|---------|------|------|
| 易方达消费行业 | 110022 | 主动管理 |
| 招商中证白酒 | 161725 | 被动指数 |
| 兴全趋势投资 | 163402 | 主动管理 |
| 华夏回报混合 | 519674 | 混合基金 |
| 汇添富均衡增长 | 470018 | 混合基金 |

## 注意事项

### 反爬虫对策

本脚本已实现以下反爬虫措施：

1. **User-Agent设置** - 使用真实的浏览器User-Agent
2. **请求延迟** - 默认0.5秒的请求间隔，可自定义
3. **会话复用** - 使用requests.Session()复用连接
4. **超时控制** - 设置请求超时时间

### 最佳实践

1. **礼貌抓取** - 不要过度频繁地抓取数据
2. **合理延迟** - 建议设置至少0.5秒的请求间隔
3. **错误处理** - 脚本已处理常见错误，但建议检查输出日志
4. **批量操作** - 尽量一次性抓取所有需要的数据，而不是频繁调用

### 常见问题

**Q: 抓取失败，显示"无法解析数据"**

A: 可能原因：
- 网络连接问题
- 基金代码错误（请确保代码是6位数字）
- 网站结构变化
- 请求被限流

建议：
- 检查网络连接
- 验证基金代码正确性
- 增加请求延迟 (`-l 1.0` 或 `delay=1.0`)
- 稍后重试

**Q: 如何处理多个基金的大规模抓取？**

A: 建议方法：
- 使用文件配置 (`-f funds.json`)
- 增加请求延迟 (`-l 1.0`)
- 分多次执行，每次抓取100-200个基金
- 考虑添加重试机制

**Q: 能否自定义抓取间隔？**

A: 可以。使用 `-l` 或 `--delay` 参数：
```bash
python scrape_funds.py -c 110022 161725 -l 2.0  # 2秒延迟
```

或在代码中设置：
```python
scraper = FundScraper(delay=2.0)
```

## 技术栈

- **requests** - HTTP请求库
- **BeautifulSoup4** - HTML解析
- **lxml** - XML/HTML处理
- **pandas** - 数据处理和分析

## 项目结构

```
.
├── README.md                 # 本文档
├── requirements.txt          # 依赖包列表
├── fund_scraper.py          # 核心爬虫模块
├── scrape_funds.py          # 命令行工具
├── funds_example.json       # JSON配置示例
├── funds_example.txt        # 文本配置示例
└── output/                  # 输出文件目录（自动创建）
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request进行改进。

## 免责声明

本脚本仅用于学习和研究目的。使用本脚本抓取数据时，请遵守相关网站的`robots.txt`和用户协议。
作者不对由使用本脚本造成的任何问题负责。

## 更新日志

### v1.1.0 (2025-01-20)
- 添加历史净值数据抓取功能
- 支持按天数筛选历史数据
- 添加批量抓取历史数据的方法
- 支持命令行参数 `--history` 指定天数
- 添加交互式选择模式
- 添加历史数据的CSV/JSON导出方法
- 更新文档和使用示例

### v1.0.0 (2024-01-15)
- 初始发布
- 支持基金基本信息和净值数据抓取
- 支持CSV和JSON输出
- 提供命令行工具和编程接口
