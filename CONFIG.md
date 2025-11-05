# 配置说明

本文档介绍如何配置基金数据抓取脚本的各种参数。

## 命令行参数配置

### 基本参数

#### `-c, --codes` - 基金代码列表
指定要抓取的基金代码。

```bash
# 单个基金
python scrape_funds.py -c 110022

# 多个基金
python scrape_funds.py -c 110022 161725 163402
```

#### `-f, --file` - 从文件读取基金代码
从文本文件或JSON文件读取基金代码列表。

```bash
# 文本文件（每行一个代码）
python scrape_funds.py -f funds.txt

# JSON文件
python scrape_funds.py -f funds.json
```

### 功能参数

#### `-d, --detailed` - 获取详细信息
获取基金的详细信息，包括基金公司、经理等。注意：这会增加抓取时间。

```bash
python scrape_funds.py -c 110022 -d
```

#### `-o, --output` - 输出文件
指定输出文件路径。支持 `.csv` 和 `.json` 格式。

```bash
# 输出为CSV
python scrape_funds.py -c 110022 -o output.csv

# 输出为JSON
python scrape_funds.py -c 110022 -o output.json
```

### 性能参数

#### `-t, --timeout` - 请求超时时间
设置HTTP请求的超时时间（秒）。默认为10秒。

```bash
# 增加超时时间
python scrape_funds.py -c 110022 -t 15

# 减少超时时间（网络良好时）
python scrape_funds.py -c 110022 -t 5
```

#### `-l, --delay` - 请求间隔
设置请求之间的延迟时间（秒）。默认为0.5秒。增加此值可以避免被限流。

```bash
# 增加延迟（避免限流）
python scrape_funds.py -c 110022 161725 163402 -l 2.0

# 减少延迟（网络良好时）
python scrape_funds.py -c 110022 -l 0.2
```

## 编程接口配置

### FundScraper 类参数

创建爬虫实例时可配置的参数：

```python
from fund_scraper import FundScraper

scraper = FundScraper(
    timeout=10,      # HTTP请求超时时间（秒）
    delay=0.5        # 请求间隔时间（秒）
)
```

### 配置示例

#### 示例1：快速模式（良好网络环境）

```python
scraper = FundScraper(timeout=5, delay=0.2)
```

#### 示例2：稳定模式（一般网络环境）

```python
scraper = FundScraper(timeout=10, delay=0.5)
```

#### 示例3：保守模式（网络较差或避免限流）

```python
scraper = FundScraper(timeout=15, delay=2.0)
```

## 配置文件格式

### 文本文件格式 (funds.txt)

每行一个基金代码，可以添加注释：

```
# 消费行业基金
110022
# 白酒基金
161725
# 趋势投资基金
163402
```

### JSON文件格式 (funds.json)

标准JSON格式，需要包含 `funds` 数组：

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

或者直接是数组：

```json
[
  "110022",
  "161725",
  "163402"
]
```

## 高级配置

### 大规模抓取建议

当需要抓取大量基金时：

```bash
# 分组抓取，避免过于频繁的请求
# 第1组：50个基金
python scrape_funds.py -f funds_group1.json -l 1.0 -o funds_1.csv

# 第2组：50个基金
python scrape_funds.py -f funds_group2.json -l 1.0 -o funds_2.csv
```

在Python中：

```python
from fund_scraper import FundScraper
import time

scraper = FundScraper(delay=1.0)

# 分批抓取
for i in range(0, len(all_codes), 50):
    batch = all_codes[i:i+50]
    results = scraper.scrape_multiple_funds(batch)
    scraper.save_to_csv(results, f'funds_{i//50}.csv')
    time.sleep(5)  # 批次之间等待5秒
```

### 自定义HTTP头

如果需要修改HTTP请求头（高级用途）：

```python
from fund_scraper import FundScraper

scraper = FundScraper()

# 修改User-Agent
scraper.session.headers.update({
    'User-Agent': 'Your Custom User-Agent'
})
```

### 代理设置

如果需要通过代理访问：

```python
from fund_scraper import FundScraper

scraper = FundScraper()

# 设置代理
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}

# 在请求中使用代理（需要修改源代码的_request方法）
# 或者在创建session时设置
```

## 性能优化建议

| 场景 | 推荐配置 |
|------|---------|
| 测试单个基金 | `-t 5 -l 0.2` |
| 抓取10-50个基金 | `-t 10 -l 0.5` |
| 抓取50-200个基金 | `-t 10 -l 1.0` |
| 大规模抓取(>200个) | `-t 15 -l 2.0` 并分批 |
| 网络不稳定 | `-t 15 -l 2.0` |

## 环境变量配置（可选扩展）

虽然当前版本不直接支持环境变量，但可以通过修改代码来实现：

```python
import os

timeout = int(os.getenv('FUND_SCRAPER_TIMEOUT', '10'))
delay = float(os.getenv('FUND_SCRAPER_DELAY', '0.5'))

scraper = FundScraper(timeout=timeout, delay=delay)
```

使用：

```bash
export FUND_SCRAPER_TIMEOUT=15
export FUND_SCRAPER_DELAY=1.0
python scrape_funds.py -c 110022
```

## 常见配置问题

### Q: 频繁收到"请求失败"的错误

**A:** 增加延迟和超时时间：
```bash
python scrape_funds.py -c codes.json -t 15 -l 2.0
```

### Q: 抓取速度太慢

**A:** 减少延迟（但要谨慎避免被限流）：
```bash
python scrape_funds.py -c single_code.txt -l 0.2
```

### Q: 需要在特定时间运行抓取任务

**A:** 使用系统任务调度器：

Linux/Mac:
```bash
# 每天10:00运行
0 10 * * * cd /path/to/project && python scrape_funds.py -f funds.json -o funds_daily.csv
```

Windows: 使用任务计划程序

### Q: 需要定期更新基金数据

**A:** 创建定时脚本：

```python
import schedule
import time
from scrape_funds import load_fund_codes_from_file
from fund_scraper import FundScraper

def job():
    scraper = FundScraper()
    codes = load_fund_codes_from_file('funds.json')
    results = scraper.scrape_multiple_funds(codes)
    scraper.save_to_csv(results, f'funds_{time.strftime("%Y%m%d_%H%M%S")}.csv')

schedule.every().day.at("10:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 总结

- **基本使用**：`python scrape_funds.py -c 110022`
- **文件输入**：`python scrape_funds.py -f funds.json`
- **自定义输出**：添加 `-o filename.csv` 或 `-o filename.json`
- **性能调整**：使用 `-t` 和 `-l` 参数
- **详细信息**：添加 `-d` 参数

更多信息见 README.md 和 QUICKSTART.md。
