"""
基金数据抓取命令行工具
支持通过命令行参数或配置文件批量抓取基金数据
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List
import pandas as pd

from fund_scraper import FundScraper


def load_fund_codes_from_file(filepath: str) -> List[str]:
    """
    从文件加载基金代码列表
    
    支持格式：
    - 纯文本文件，每行一个基金代码
    - JSON文件，包含funds列表
    
    Args:
        filepath: 文件路径
        
    Returns:
        基金代码列表
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"文件不存在: {filepath}")
        return []
    
    try:
        if filepath.suffix.lower() == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'funds' in data:
                    return data['funds']
                elif isinstance(data, list):
                    return data
        else:
            # 纯文本文件
            with open(filepath, 'r', encoding='utf-8') as f:
                codes = [line.strip() for line in f if line.strip()]
                return codes
    except Exception as e:
        print(f"读取文件失败: {e}")
        return []
    
    return []


def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 60)
    print("基金数据抓取工具 - 交互模式")
    print("=" * 60)
    
    # 获取基金代码
    codes_input = input("\n请输入基金代码（多个用逗号分隔，如 110022,518600,000001）：")
    fund_codes = [code.strip() for code in codes_input.split(',') if code.strip()]
    
    if not fund_codes:
        print("未输入任何基金代码，退出")
        return
    
    # 询问是否获取详细信息
    detailed_input = input("是否获取详细信息（基金公司、经理等）？(y/n，默认: n)：").lower().strip()
    detailed = detailed_input == 'y'
    
    # 询问是否获取历史数据
    history_input = input("是否获取历史数据？(y/n，默认: n)：").lower().strip()
    history_days = None
    if history_input == 'y':
        try:
            days_input = input("请输入天数（如30、90，默认: 30）：").strip()
            history_days = int(days_input) if days_input else 30
        except ValueError:
            print("无效的天数，将使用默认值30天")
            history_days = 30
    
    # 询问输出格式
    print("\n输出格式选项: csv, json, console（默认: console）")
    output_input = input("请选择输出格式：").lower().strip()
    
    output_file = None
    if output_input == 'csv':
        output_file = input("请输入输出文件路径（默认: fund_data.csv）：").strip() or "fund_data.csv"
    elif output_input == 'json':
        output_file = input("请输入输出文件路径（默认: fund_data.json）：").strip() or "fund_data.json"
    
    # 执行抓取
    scraper = FundScraper(timeout=10, delay=0.5)
    
    # 如果需要历史数据
    if history_days:
        history_data = scraper.get_multiple_funds_history(fund_codes, days=history_days)
        
        if not history_data:
            print("未获取到任何历史数据")
            return
        
        print("\n" + "=" * 60)
        print("历史数据抓取完成")
        print("=" * 60)
        
        # 输出统计信息
        for fund_code, data_list in history_data.items():
            print(f"基金 {fund_code}: {len(data_list)} 条历史记录")
        
        # 保存输出
        if output_file:
            if output_file.endswith('.csv'):
                scraper.save_history_to_csv(history_data, output_file)
            else:
                scraper.save_history_to_json(history_data, output_file)
        else:
            print("\n历史数据样本（每个基金显示前5条）：")
            for fund_code, data_list in history_data.items():
                print(f"\n基金 {fund_code}:")
                for record in data_list[:5]:
                    print(f"  日期: {record['date']}, 净值: {record['unit_net_value']}, 增长率: {record['growth_rate']}")
                if len(data_list) > 5:
                    print(f"  ... 共 {len(data_list)} 条记录")
    else:
        # 抓取实时数据
        results = scraper.scrape_multiple_funds(fund_codes, detailed=detailed)
        
        if not results:
            print("未获取到任何数据")
            return
        
        print("\n" + "=" * 60)
        print("抓取结果")
        print("=" * 60)
        
        df = scraper.to_dataframe(results)
        
        # 选择显示的列
        display_columns = [
            'fund_code', 'fund_name', 'unit_net_value', 
            'accumulated_net_value', 'daily_growth_rate', 'update_date'
        ]
        
        # 过滤存在的列
        display_columns = [col for col in display_columns if col in df.columns]
        
        print(df[display_columns].to_string(index=False))
        
        # 保存输出
        if output_file:
            if output_file.endswith('.csv'):
                scraper.save_to_csv(df, output_file)
            else:
                scraper.save_to_json(results, output_file)


def main():
    """主函数"""
    
    parser = argparse.ArgumentParser(
        description='基金数据抓取工具 - 天天基金网(eastmoney.com)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 抓取单个基金
  python scrape_funds.py -c 110022
  
  # 抓取多个基金
  python scrape_funds.py -c 110022 161725 163402
  
  # 从文件读取基金列表
  python scrape_funds.py -f funds.txt
  python scrape_funds.py -f funds.json
  
  # 获取详细信息并保存为JSON
  python scrape_funds.py -c 110022 -d -o funds.json
  
  # 抓取历史数据
  python scrape_funds.py -c 110022 --history 30
  python scrape_funds.py -f funds.txt --history 90 -o history.csv
  
  # 交互模式
  python scrape_funds.py
        """
    )
    
    parser.add_argument(
        '-c', '--codes',
        nargs='+',
        help='基金代码列表 (例: 110022 161725 163402)'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='读取基金代码的文件路径 (支持 .txt 和 .json 格式)'
    )
    
    parser.add_argument(
        '-d', '--detailed',
        action='store_true',
        help='获取详细信息（包括基金公司、经理等）'
    )
    
    parser.add_argument(
        '--history',
        type=int,
        help='获取历史净值数据，指定天数 (例: 30, 90)'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=10,
        help='请求超时时间（秒，默认: 10）'
    )
    
    parser.add_argument(
        '-l', '--delay',
        type=float,
        default=0.5,
        help='请求间隔时间（秒，默认: 0.5）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='输出文件路径 (.csv 或 .json，默认: 输出到控制台)'
    )
    
    args = parser.parse_args()
    
    # 如果没有任何参数，进入交互模式
    if not args.codes and not args.file:
        interactive_mode()
        return
    
    # 收集基金代码
    fund_codes = []
    
    if args.codes:
        fund_codes.extend(args.codes)
    
    if args.file:
        file_codes = load_fund_codes_from_file(args.file)
        fund_codes.extend(file_codes)
    
    if not fund_codes:
        print("错误: 未指定基金代码")
        print("使用 -h 或 --help 查看帮助信息")
        sys.exit(1)
    
    # 去重
    fund_codes = list(set(fund_codes))
    
    print("=" * 60)
    print(f"基金数据抓取工具")
    print("=" * 60)
    print(f"待抓取基金数量: {len(fund_codes)}")
    print(f"基金代码: {', '.join(fund_codes)}")
    print(f"详细信息: {'是' if args.detailed else '否'}")
    if args.history:
        print(f"历史数据天数: {args.history} 天")
    print("=" * 60)
    
    # 创建爬虫
    scraper = FundScraper(timeout=args.timeout, delay=args.delay)
    
    # 根据是否指定history参数选择不同的抓取方式
    if args.history:
        # 抓取历史数据
        history_data = scraper.get_multiple_funds_history(fund_codes, days=args.history)
        
        if not history_data:
            print("未获取到任何历史数据")
            sys.exit(1)
        
        # 输出结果
        print("\n" + "=" * 60)
        print("历史数据抓取结果")
        print("=" * 60)
        
        # 输出统计信息
        total_records = 0
        for fund_code, data_list in history_data.items():
            print(f"基金 {fund_code}: {len(data_list)} 条历史记录")
            total_records += len(data_list)
        print(f"总计: {total_records} 条记录")
        
        # 保存到文件
        if args.output:
            if args.output.endswith('.csv'):
                scraper.save_history_to_csv(history_data, args.output)
            elif args.output.endswith('.json'):
                scraper.save_history_to_json(history_data, args.output)
            else:
                print("错误: 不支持的文件格式，请使用 .csv 或 .json")
                sys.exit(1)
        else:
            # 显示样本数据
            print("\n历史数据样本（每个基金显示前3条）：")
            for fund_code, data_list in history_data.items():
                print(f"\n基金 {fund_code}:")
                for record in data_list[:3]:
                    print(f"  日期: {record['date']}, 净值: {record['unit_net_value']}, 增长率: {record['growth_rate']}")
    else:
        # 抓取实时数据
        results = scraper.scrape_multiple_funds(fund_codes, detailed=args.detailed)
        
        if not results:
            print("未获取到任何数据")
            sys.exit(1)
        
        # 输出结果
        print("\n" + "=" * 60)
        print("抓取结果")
        print("=" * 60)
        
        df = scraper.to_dataframe(results)
        
        # 选择显示的列
        display_columns = [
            'fund_code', 'fund_name', 'unit_net_value', 
            'accumulated_net_value', 'daily_growth_rate', 'update_date'
        ]
        
        # 过滤存在的列
        display_columns = [col for col in display_columns if col in df.columns]
        
        print(df[display_columns].to_string(index=False))
        
        # 保存到文件
        if args.output:
            if args.output.endswith('.csv'):
                scraper.save_to_csv(df, args.output)
            elif args.output.endswith('.json'):
                scraper.save_to_json(results, args.output)
            else:
                print("错误: 不支持的文件格式，请使用 .csv 或 .json")
                sys.exit(1)
    
    print("\n抓取完成")


if __name__ == "__main__":
    main()
