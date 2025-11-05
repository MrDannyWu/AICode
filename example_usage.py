"""
基金数据抓取脚本 - 使用示例
演示各种不同的使用方式和场景
"""

from fund_scraper import FundScraper
import pandas as pd


def example_1_basic_single_fund():
    """示例1：抓取单个基金的基本信息"""
    print("\n" + "=" * 60)
    print("示例1：抓取单个基金的基本信息")
    print("=" * 60)
    
    scraper = FundScraper(timeout=10, delay=0.5)
    
    # 抓取单个基金
    fund_data = scraper.scrape_fund('110022', detailed=False)
    
    if fund_data:
        print("\n基金数据:")
        for key, value in fund_data.items():
            print(f"  {key}: {value}")
    else:
        print("未能获取基金数据")


def example_2_multiple_funds():
    """示例2：批量抓取多个基金"""
    print("\n" + "=" * 60)
    print("示例2：批量抓取多个基金")
    print("=" * 60)
    
    scraper = FundScraper(timeout=10, delay=0.5)
    
    # 基金代码列表
    fund_codes = ['110022', '161725', '163402']
    
    # 批量抓取
    results = scraper.scrape_multiple_funds(fund_codes, detailed=False)
    
    if results:
        print(f"\n成功获取 {len(results)} 个基金的数据:")
        
        # 转换为DataFrame显示
        df = scraper.to_dataframe(results)
        print(df[['fund_code', 'fund_name', 'unit_net_value', 'daily_growth_rate']].to_string())
    else:
        print("未能获取任何数据")


def example_3_save_to_files():
    """示例3：保存数据到文件"""
    print("\n" + "=" * 60)
    print("示例3：保存数据到CSV和JSON文件")
    print("=" * 60)
    
    scraper = FundScraper(timeout=10, delay=0.5)
    
    fund_codes = ['110022', '161725', '163402']
    results = scraper.scrape_multiple_funds(fund_codes, detailed=False)
    
    if results:
        df = scraper.to_dataframe(results)
        
        # 保存为CSV
        csv_file = 'funds_data.csv'
        scraper.save_to_csv(df, csv_file)
        
        # 保存为JSON
        json_file = 'funds_data.json'
        scraper.save_to_json(results, json_file)
        
        print(f"\n数据已保存:")
        print(f"  CSV文件: {csv_file}")
        print(f"  JSON文件: {json_file}")
    else:
        print("未能获取数据")


def example_4_data_analysis():
    """示例4：数据分析和处理"""
    print("\n" + "=" * 60)
    print("示例4：数据分析和处理")
    print("=" * 60)
    
    scraper = FundScraper(timeout=10, delay=0.5)
    
    fund_codes = ['110022', '161725', '163402', '519674', '470018']
    results = scraper.scrape_multiple_funds(fund_codes, detailed=False)
    
    if results:
        df = scraper.to_dataframe(results)
        
        print("\n全部基金信息:")
        print(df[['fund_code', 'fund_name', 'unit_net_value', 'daily_growth_rate']].to_string())
        
        # 按单位净值排序
        print("\n按单位净值排序（从高到低）:")
        df_sorted = df.sort_values('unit_net_value', ascending=False)
        print(df_sorted[['fund_code', 'fund_name', 'unit_net_value']].to_string())
        
        # 统计基金收益情况
        positive = len(df[df['daily_growth_rate'] > 0])
        negative = len(df[df['daily_growth_rate'] < 0])
        neutral = len(df[df['daily_growth_rate'] == 0])
        
        print(f"\n今日基金涨跌统计:")
        print(f"  上涨: {positive} 只")
        print(f"  下跌: {negative} 只")
        print(f"  平盘: {neutral} 只")
        
        # 平均收益率
        avg_growth = df['daily_growth_rate'].mean()
        print(f"  平均涨幅: {avg_growth:.2f}%")
    else:
        print("未能获取数据")


def example_5_custom_settings():
    """示例5：自定义设置"""
    print("\n" + "=" * 60)
    print("示例5：自定义超时和延迟设置")
    print("=" * 60)
    
    # 自定义超时和延迟
    scraper = FundScraper(timeout=15, delay=1.0)
    
    print("爬虫配置:")
    print(f"  超时时间: {scraper.timeout} 秒")
    print(f"  请求延迟: {scraper.delay} 秒")
    
    fund_data = scraper.scrape_fund('110022', detailed=False)
    
    if fund_data:
        print(f"\n基金代码: {fund_data['fund_code']}")
        print(f"基金名称: {fund_data['fund_name']}")
        print(f"单位净值: {fund_data['unit_net_value']}")
    else:
        print("未能获取基金数据")


def example_6_detailed_info():
    """示例6：获取详细信息（可选）"""
    print("\n" + "=" * 60)
    print("示例6：获取基金详细信息")
    print("=" * 60)
    
    scraper = FundScraper(timeout=10, delay=1.0)
    
    # 获取详细信息
    print("正在获取详细信息（可能需要更长时间）...")
    fund_data = scraper.scrape_fund('110022', detailed=True)
    
    if fund_data:
        print("\n基金详细信息:")
        for key, value in fund_data.items():
            if value:  # 只显示非空值
                print(f"  {key}: {value}")
    else:
        print("未能获取基金详细数据")


def example_7_error_handling():
    """示例7：错误处理"""
    print("\n" + "=" * 60)
    print("示例7：错误处理示例")
    print("=" * 60)
    
    scraper = FundScraper(timeout=10, delay=0.5)
    
    # 测试无效的基金代码
    print("\n尝试获取无效基金代码的数据...")
    invalid_fund = scraper.scrape_fund('999999', detailed=False)
    
    if invalid_fund:
        print(f"获取数据成功: {invalid_fund['fund_name']}")
    else:
        print("未能获取数据（这是预期的行为）")
    
    # 获取多个基金，其中包含无效代码
    print("\n批量抓取多个基金（包含无效代码）...")
    fund_codes = ['110022', '999999', '161725']
    results = scraper.scrape_multiple_funds(fund_codes, detailed=False)
    
    print(f"成功获取 {len(results)} 个有效基金的数据")


def example_8_etf_funds():
    """示例8：ETF基金抓取测试（包含404自动降级）"""
    print("\n" + "=" * 60)
    print("示例8：ETF基金抓取测试（包含404自动降级）")
    print("=" * 60)
    
    scraper = FundScraper(timeout=10, delay=0.5)
    
    # 基金代码列表：包含普通基金和ETF
    fund_codes = ['110022', '518600', '000001']
    
    print(f"\n正在批量抓取基金：{', '.join(fund_codes)}")
    print("说明：518600是ETF基金，实时估值API返回404，会自动使用备用数据源")
    
    results = scraper.scrape_multiple_funds(fund_codes, detailed=False)
    
    if results:
        print(f"\n成功获取 {len(results)} 个基金的数据:")
        
        df = scraper.to_dataframe(results)
        print("\n基金数据汇总：")
        print(df[['fund_code', 'fund_name', 'unit_net_value', 'daily_growth_rate', 'update_date']].to_string())
        
        print("\n各基金的详细信息：")
        for result in results:
            print(f"\n  基金代码: {result['fund_code']}")
            print(f"  基金名称: {result['fund_name']}")
            print(f"  单位净值: {result['unit_net_value']}")
            print(f"  日增长率: {result['daily_growth_rate']}%")
            print(f"  更新日期: {result['update_date']}")
    else:
        print("未能获取任何数据")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("基金数据抓取脚本 - 使用示例")
    print("=" * 60)
    print("\n注意：由于网络原因或网站限制，某些示例可能无法正常执行")
    print("请确保已安装所有依赖包: pip install -r requirements.txt")
    
    try:
        # 运行基本示例
        example_1_basic_single_fund()
        example_2_multiple_funds()
        example_3_save_to_files()
        example_4_data_analysis()
        example_5_custom_settings()
        
        # 以下示例可选（更耗时或需要更多网络请求）
        # example_6_detailed_info()
        # example_7_error_handling()
        example_8_etf_funds()
        
    except Exception as e:
        print(f"\n执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("所有示例执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
