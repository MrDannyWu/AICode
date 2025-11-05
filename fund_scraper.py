"""
基金数据抓取脚本 - 天天基金网(eastmoney.com)
用于抓取基金的基本信息、净值数据和历史业绩数据
"""

import requests
import json
import time
import csv
import re
from typing import List, Dict, Optional, Union
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path


class FundScraper:
    """基金数据抓取器"""

    def __init__(self, timeout: int = 10, delay: float = 0.5):
        """
        初始化爬虫
        
        Args:
            timeout: 请求超时时间（秒）
            delay: 请求之间的延迟时间（秒）
        """
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        发送HTTP请求
        
        Args:
            url: 请求URL
            params: 查询参数
            
        Returns:
            Response对象或None
        """
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None

    def get_fund_info(self, fund_code: str) -> Optional[Dict]:
        """
        获取基金基本信息
        
        Args:
            fund_code: 基金代码（6位数字）
            
        Returns:
            包含基金信息的字典，或None如果失败
        """
        time.sleep(self.delay)
        
        url = f"https://fundgz.1234567.com.cn/js/fundgz_{fund_code}.js"
        
        try:
            response = self._request(url)
            if not response:
                return None
            
            # 解析JSONP响应
            content = response.text
            # 提取JSON数据
            json_str = re.search(r'jsonpgz\((.*)\)', content)
            if not json_str:
                print(f"无法解析基金代码 {fund_code} 的数据")
                return None
            
            data = json.loads(json_str.group(1))
            
            info = {
                'fund_code': fund_code,
                'fund_name': data.get('name', ''),
                'unit_net_value': float(data.get('gsz', 0)),
                'accumulated_net_value': float(data.get('jsn', 0)),
                'daily_growth_rate': float(data.get('dwjz', 0)) if data.get('dwjz') else 0,
                'update_date': data.get('gztime', ''),
                'status': data.get('isrising', ''),
            }
            
            return info
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"解析基金信息失败: {fund_code}, 错误: {e}")
            return None

    def get_fund_info_from_page(self, fund_code: str) -> Optional[Dict]:
        """
        从基金详情页获取更详细的基金信息
        
        Args:
            fund_code: 基金代码
            
        Returns:
            包含基金详细信息的字典
        """
        time.sleep(self.delay)
        
        url = f"https://fundpage.eastmoney.com/{fund_code}.html"
        
        try:
            response = self._request(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # 提取基金类型、基金公司、基金经理信息
            info = {'fund_code': fund_code}
            
            # 获取基金名称和基本信息
            fund_name = soup.select_one('div.title h1')
            if fund_name:
                info['fund_name'] = fund_name.get_text(strip=True)
            
            # 查找基金类型
            fund_type_elem = soup.find('dt', string='基金类型')
            if fund_type_elem:
                fund_type = fund_type_elem.find_next('dd')
                if fund_type:
                    info['fund_type'] = fund_type.get_text(strip=True)
            
            # 查找基金公司
            company_elem = soup.find('dt', string='基金公司')
            if company_elem:
                company = company_elem.find_next('dd')
                if company:
                    info['fund_company'] = company.get_text(strip=True)
            
            # 查找基金经理
            manager_elem = soup.find('dt', string='基金经理')
            if manager_elem:
                manager = manager_elem.find_next('dd')
                if manager:
                    manager_name = manager.find('a')
                    if manager_name:
                        info['fund_manager'] = manager_name.get_text(strip=True)
            
            return info
        except Exception as e:
            print(f"从页面获取基金信息失败: {fund_code}, 错误: {e}")
            return None

    def get_fund_performance(self, fund_code: str) -> Optional[Dict]:
        """
        获取基金的历史业绩数据
        
        Args:
            fund_code: 基金代码
            
        Returns:
            包含基金业绩数据的字典
        """
        time.sleep(self.delay)
        
        url = f"https://fundpage.eastmoney.com/{fund_code}.html"
        
        try:
            response = self._request(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            performance = {}
            
            # 查找业绩表格或相关信息
            # 这个可能需要根据网站的实际结构调整
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        header = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        
                        # 匹配各个时期的收益率
                        if '1个月' in header or '近1月' in header:
                            performance['monthly_1_return'] = value
                        elif '3个月' in header or '近3月' in header:
                            performance['monthly_3_return'] = value
                        elif '6个月' in header or '近6月' in header:
                            performance['monthly_6_return'] = value
                        elif '1年' in header or '近1年' in header:
                            performance['yearly_1_return'] = value
                        elif '3年' in header or '近3年' in header:
                            performance['yearly_3_return'] = value
                        elif '5年' in header or '近5年' in header:
                            performance['yearly_5_return'] = value
                        elif '成立以来' in header:
                            performance['since_establishment_return'] = value
            
            return performance if performance else None
        except Exception as e:
            print(f"获取基金业绩数据失败: {fund_code}, 错误: {e}")
            return None

    def scrape_fund(self, fund_code: str, detailed: bool = False) -> Optional[Dict]:
        """
        抓取单个基金的所有数据
        
        Args:
            fund_code: 基金代码
            detailed: 是否获取详细信息
            
        Returns:
            包含基金所有信息的字典
        """
        print(f"正在抓取基金: {fund_code}")
        
        # 获取实时净值数据
        fund_data = self.get_fund_info(fund_code)
        
        if not fund_data:
            print(f"无法获取基金 {fund_code} 的数据")
            return None
        
        if detailed:
            # 获取详细信息
            page_info = self.get_fund_info_from_page(fund_code)
            if page_info:
                fund_data.update(page_info)
            
            # 获取历史业绩
            performance = self.get_fund_performance(fund_code)
            if performance:
                fund_data.update(performance)
        
        print(f"成功获取基金 {fund_code} 的数据")
        return fund_data

    def scrape_multiple_funds(self, fund_codes: List[str], detailed: bool = False) -> List[Dict]:
        """
        批量抓取多个基金的数据
        
        Args:
            fund_codes: 基金代码列表
            detailed: 是否获取详细信息
            
        Returns:
            包含所有基金数据的列表
        """
        results = []
        
        for code in fund_codes:
            data = self.scrape_fund(code, detailed=detailed)
            if data:
                results.append(data)
        
        return results

    def save_to_csv(self, data: Union[List[Dict], pd.DataFrame], filepath: str) -> bool:
        """
        保存数据到CSV文件
        
        Args:
            data: 要保存的数据
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"数据已保存到: {filepath}")
            return True
        except Exception as e:
            print(f"保存CSV文件失败: {e}")
            return False

    def save_to_json(self, data: Union[List[Dict], pd.DataFrame], filepath: str) -> bool:
        """
        保存数据到JSON文件
        
        Args:
            data: 要保存的数据
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            if isinstance(data, pd.DataFrame):
                data = data.to_dict('records')
            
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"数据已保存到: {filepath}")
            return True
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
            return False

    def to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """
        将数据转换为DataFrame
        
        Args:
            data: 基金数据列表
            
        Returns:
            DataFrame对象
        """
        return pd.DataFrame(data)


def main():
    """主函数 - 使用示例"""
    
    # 创建爬虫实例
    scraper = FundScraper(timeout=10, delay=0.5)
    
    # 示例基金代码列表
    # 可以改为从文件读取或命令行参数获取
    fund_codes = [
        '110022',  # 易方达消费行业
        '161725',  # 招商中证白酒
        '163402',  # 兴全趋势投资
    ]
    
    print("=" * 50)
    print("基金数据抓取开始")
    print("=" * 50)
    
    # 抓取数据
    results = scraper.scrape_multiple_funds(fund_codes, detailed=False)
    
    if results:
        print("\n" + "=" * 50)
        print("抓取结果")
        print("=" * 50)
        
        # 转换为DataFrame并打印
        df = scraper.to_dataframe(results)
        print(df.to_string())
        
        # 保存到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存为CSV
        csv_path = f"output/funds_{timestamp}.csv"
        scraper.save_to_csv(df, csv_path)
        
        # 保存为JSON
        json_path = f"output/funds_{timestamp}.json"
        scraper.save_to_json(results, json_path)
    else:
        print("未获取到任何数据")
    
    print("\n抓取完成")


if __name__ == "__main__":
    main()
