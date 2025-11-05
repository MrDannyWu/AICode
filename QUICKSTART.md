# 快速开始指南

## 5分钟快速上手

### 1. 安装依赖（1分钟）

```bash
pip install -r requirements.txt
```

### 2. 基本使用（2分钟）

#### 最简单的方式 - 直接运行脚本

```bash
python fund_scraper.py
```

这将抓取3个示例基金并保存到 `output/` 目录。

#### 使用命令行工具

```bash
# 抓取单个基金
python scrape_funds.py -c 110022

# 抓取多个基金并保存为CSV
python scrape_funds.py -c 110022 161725 163402 -o funds.csv

# 从文件读取基金列表
python scrape_funds.py -f funds_example.txt -o funds.json
```

### 3. 在Python中使用（2分钟）

```python
from fund_scraper import FundScraper

# 创建爬虫
scraper = FundScraper()

# 抓取单个基金
fund = scraper.scrape_fund('110022')
print(fund)

# 抓取多个基金
funds = scraper.scrape_multiple_funds(['110022', '161725', '163402'])

# 转换为DataFrame
df = scraper.to_dataframe(funds)
print(df)

# 保存数据
scraper.save_to_csv(df, 'funds.csv')
scraper.save_to_json(funds, 'funds.json')
```

### 4. 获取历史数据（新功能！）

```python
from fund_scraper import FundScraper

scraper = FundScraper()

# 获取单个基金最近30天的历史数据
history = scraper.get_fund_history('110022', days=30)
print(f"获取 {len(history)} 条历史记录")

# 批量获取多个基金的历史数据
history_data = scraper.get_multiple_funds_history(['110022', '161725'], days=30)

# 保存为CSV或JSON
scraper.save_history_to_csv(history_data, 'history.csv')
scraper.save_history_to_json(history_data, 'history.json')
```

或使用命令行：

```bash
# 获取最近30天的历史数据
python scrape_funds.py -c 110022 --history 30

# 保存为CSV
python scrape_funds.py -c 110022 --history 30 -o fund_history.csv

# 批量获取并保存
python scrape_funds.py -f funds.txt --history 30 -o history.csv
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `python scrape_funds.py -h` | 显示帮助信息 |
| `python scrape_funds.py -c 110022` | 抓取代码为110022的基金 |
| `python scrape_funds.py -c 110022 -d` | 获取详细信息 |
| `python scrape_funds.py -c 110022 -o fund.csv` | 保存为CSV |
| `python scrape_funds.py -f funds.txt` | 从文件读取基金列表 |
| `python scrape_funds.py -c 110022 -l 1.0` | 设置1秒延迟 |
| `python scrape_funds.py -c 110022 --history 30` | 获取最近30天历史数据 |
| `python scrape_funds.py -f funds.txt --history 90 -o history.csv` | 批量获取历史数据 |
| `python scrape_funds.py` | 进入交互模式 |

## 常见基金代码

- **110022** - 易方达消费行业
- **161725** - 招商中证白酒
- **163402** - 兴全趋势投资
- **519674** - 华夏回报混合
- **470018** - 汇添富均衡增长

在 [天天基金网](https://www.1234567.com.cn/) 搜索基金名称可获得正确的代码。

## 数据输出示例

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
  }
]
```

## 遇到问题？

### 问题1：`ModuleNotFoundError: No module named 'requests'`

**解决方案：** 安装依赖
```bash
pip install -r requirements.txt
```

### 问题2：无法获取数据或显示错误

**解决方案：** 
1. 检查网络连接
2. 验证基金代码是否正确（应该是6位数字）
3. 增加请求延迟：`python scrape_funds.py -c 110022 -l 2.0`
4. 等待几分钟后重试

### 问题3：爬取速度太慢

**解决方案：** 这是故意的（反爬虫对策）。建议：
- 一次性抓取所有需要的基金
- 使用 `-f` 参数从文件读取基金列表
- 不要频繁运行脚本

## 更多示例

查看 `example_usage.py` 文件了解更多高级用法：

```bash
python example_usage.py
```

## 详细文档

完整文档请参考 `README.md` 文件。

---

准备好了？开始抓取基金数据吧！ 🚀
