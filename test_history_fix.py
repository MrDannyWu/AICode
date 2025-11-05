"""
测试历史数据抓取修复
验证不同类型基金的历史数据能够正常获取
"""

from fund_scraper import FundScraper
import sys


def test_single_fund(scraper, fund_code, description):
    """测试单个基金"""
    print(f"\n{'='*60}")
    print(f"测试: {fund_code} - {description}")
    print('='*60)
    
    history = scraper.get_fund_history(fund_code, days=30)
    
    if history:
        print(f"✓ 成功获取 {len(history)} 条记录")
        print(f"  最新日期: {history[0]['date']}")
        print(f"  最新净值: {history[0]['unit_net_value']}")
        print(f"  增长率: {history[0]['growth_rate']}")
        print("\n  前5条记录:")
        for i, record in enumerate(history[:5], 1):
            print(f"    {i}. 日期: {record['date']}, 净值: {record['unit_net_value']}, 增长率: {record['growth_rate']}")
        return True
    else:
        print(f"✗ 获取失败")
        return False


def test_multiple_funds(scraper, fund_codes):
    """测试批量获取"""
    print(f"\n{'='*60}")
    print(f"测试批量获取: {', '.join(fund_codes)}")
    print('='*60)
    
    history_data = scraper.get_multiple_funds_history(fund_codes, days=7)
    
    if history_data:
        print(f"✓ 成功获取 {len(history_data)} 个基金的历史数据")
        for fund_code, records in history_data.items():
            print(f"  基金 {fund_code}: {len(records)} 条记录")
        return True
    else:
        print(f"✗ 批量获取失败")
        return False


def test_csv_export(scraper, fund_codes, filepath):
    """测试CSV导出"""
    print(f"\n{'='*60}")
    print(f"测试CSV导出")
    print('='*60)
    
    history_data = scraper.get_multiple_funds_history(fund_codes, days=30)
    
    if history_data:
        success = scraper.save_history_to_csv(history_data, filepath)
        if success:
            print(f"✓ 成功导出到 {filepath}")
            # 读取前几行
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                print("\n文件前5行:")
                for i, line in enumerate(f):
                    if i >= 5:
                        break
                    print(f"  {line.strip()}")
            return True
        else:
            print(f"✗ 导出失败")
            return False
    else:
        print(f"✗ 获取历史数据失败")
        return False


def test_json_export(scraper, fund_codes, filepath):
    """测试JSON导出"""
    print(f"\n{'='*60}")
    print(f"测试JSON导出")
    print('='*60)
    
    history_data = scraper.get_multiple_funds_history(fund_codes, days=30)
    
    if history_data:
        success = scraper.save_history_to_json(history_data, filepath)
        if success:
            print(f"✓ 成功导出到 {filepath}")
            # 读取并显示结构
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"\n基金数量: {len(data)}")
                for fund_code, records in data.items():
                    print(f"  基金 {fund_code}: {len(records)} 条记录")
                    if records:
                        print(f"    最新: {records[0]['date']} - {records[0]['unit_net_value']}")
            return True
        else:
            print(f"✗ 导出失败")
            return False
    else:
        print(f"✗ 获取历史数据失败")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("历史数据抓取修复验证测试")
    print("="*60)
    
    scraper = FundScraper(timeout=10, delay=0.5)
    
    test_cases = [
        ('110022', '易方达消费行业（普通开放式基金）'),
        ('518660', '黄金ETF（场内基金）'),
        ('000001', '华夏成长（混合型基金）'),
    ]
    
    results = []
    
    # 测试1-3: 单个基金测试
    for fund_code, description in test_cases:
        result = test_single_fund(scraper, fund_code, description)
        results.append(('单基金测试', fund_code, result))
    
    # 测试4: 批量获取
    fund_codes = [code for code, _ in test_cases]
    result = test_multiple_funds(scraper, fund_codes)
    results.append(('批量获取测试', 'multiple', result))
    
    # 测试5: CSV导出
    result = test_csv_export(scraper, ['110022', '518660'], 'test_export.csv')
    results.append(('CSV导出测试', 'export', result))
    
    # 测试6: JSON导出
    result = test_json_export(scraper, ['110022', '518660'], 'test_export.json')
    results.append(('JSON导出测试', 'export', result))
    
    # 输出测试结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_type, test_id, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_type}: {test_id}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("="*60)
    
    # 返回状态码
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
