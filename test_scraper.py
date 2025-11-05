"""
基金数据抓取脚本的测试模块
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
from pathlib import Path

from fund_scraper import FundScraper


class TestFundScraper(unittest.TestCase):
    """测试FundScraper类"""
    
    def setUp(self):
        """测试前准备"""
        self.scraper = FundScraper(timeout=5, delay=0.1)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.scraper.timeout, 5)
        self.assertEqual(self.scraper.delay, 0.1)
        self.assertIsNotNone(self.scraper.session)
    
    def test_fund_codes_validation(self):
        """测试基金代码验证"""
        # 这是一个示例测试，实际可以添加更多验证逻辑
        valid_codes = ['110022', '161725', '163402']
        self.assertEqual(len(valid_codes), 3)
    
    @patch('fund_scraper.FundScraper._request')
    def test_get_fund_info(self, mock_request):
        """测试获取基金信息"""
        # 模拟JSONP响应
        mock_response = MagicMock()
        mock_response.text = 'jsonpgz({"name":"易方达消费行业","gsz":"5.8234","jsn":"5.8234","dwjz":"0.12","gztime":"2024-01-15"})'
        mock_request.return_value = mock_response
        
        result = self.scraper.get_fund_info('110022')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['fund_code'], '110022')
        self.assertEqual(result['fund_name'], '易方达消费行业')
    
    def test_to_dataframe(self):
        """测试转换为DataFrame"""
        data = [
            {
                'fund_code': '110022',
                'fund_name': '易方达消费行业',
                'unit_net_value': 5.8234,
                'accumulated_net_value': 5.8234,
                'daily_growth_rate': 0.12,
                'update_date': '2024-01-15'
            }
        ]
        
        df = self.scraper.to_dataframe(data)
        
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['fund_code'], '110022')
    
    def test_save_to_csv(self):
        """测试保存为CSV"""
        data = [
            {
                'fund_code': '110022',
                'fund_name': '易方达消费行业',
                'unit_net_value': 5.8234
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'test.csv'
            result = self.scraper.save_to_csv(data, str(filepath))
            
            self.assertTrue(result)
            self.assertTrue(filepath.exists())
    
    def test_save_to_json(self):
        """测试保存为JSON"""
        data = [
            {
                'fund_code': '110022',
                'fund_name': '易方达消费行业',
                'unit_net_value': 5.8234
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'test.json'
            result = self.scraper.save_to_json(data, str(filepath))
            
            self.assertTrue(result)
            self.assertTrue(filepath.exists())
            
            # 验证JSON内容
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                self.assertEqual(loaded_data[0]['fund_code'], '110022')


class TestCommandLineInterface(unittest.TestCase):
    """测试命令行工具"""
    
    def test_load_fund_codes_from_text_file(self):
        """测试从文本文件读取基金代码"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'funds.txt'
            filepath.write_text('110022\n161725\n163402\n')
            
            # 这里需要导入scrape_funds中的函数
            from scrape_funds import load_fund_codes_from_file
            codes = load_fund_codes_from_file(str(filepath))
            
            self.assertEqual(codes, ['110022', '161725', '163402'])
    
    def test_load_fund_codes_from_json_file(self):
        """测试从JSON文件读取基金代码"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'funds.json'
            data = {'funds': ['110022', '161725', '163402']}
            filepath.write_text(json.dumps(data))
            
            from scrape_funds import load_fund_codes_from_file
            codes = load_fund_codes_from_file(str(filepath))
            
            self.assertEqual(codes, ['110022', '161725', '163402'])


def run_tests():
    """运行测试"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
