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
from datetime import datetime, timedelta
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
            
        Raises:
            requests.exceptions.HTTPError: HTTP错误（如404）
        """
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError:
            raise
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
            
            print(f"基金 {fund_code} 使用实时估值API成功获取数据")
            return info
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"实时估值API不支持基金 {fund_code}（404错误），尝试使用备用数据源...")
                return self.get_fund_from_detail_page(fund_code)
            else:
                print(f"API请求失败: {fund_code}, 状态码: {e.response.status_code}")
                return None
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"解析基金信息失败: {fund_code}, 错误: {e}")
            return None

    def get_fund_from_detail_page(self, fund_code: str) -> Optional[Dict]:
        """
        从基金详情页获取基金数据（备用方案）
        用于当实时估值API不可用时的降级方案
        
        Args:
            fund_code: 基金代码
            
        Returns:
            包含基金信息的字典
        """
        time.sleep(self.delay)
        
        url = f"http://fund.eastmoney.com/{fund_code}.html"
        
        try:
            response = self._request(url)
            if not response:
                print(f"无法访问基金详情页: {fund_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            info = {'fund_code': fund_code}
            
            # 获取基金名称 - 尝试多个选择器
            fund_name_elem = soup.select_one('.fundDetail-tit')
            if not fund_name_elem:
                fund_name_elem = soup.select_one('h1.title')
            if not fund_name_elem:
                fund_name_elem = soup.select_one('div.title h1')
            
            if fund_name_elem:
                info['fund_name'] = fund_name_elem.get_text(strip=True)
            else:
                info['fund_name'] = ''
            
            # 获取单位净值 - 查找包含净值的数字
            unit_net_value = 0.0
            daily_growth_rate = 0.0
            update_date = ''
            
            # 尝试从数据表中获取净值信息
            data_nums = soup.select_one('.dataNums')
            if data_nums:
                # 查找所有的数字元素
                numbers = data_nums.select('.ui-font-large')
                if numbers:
                    try:
                        unit_net_value = float(numbers[0].get_text(strip=True))
                    except (ValueError, IndexError):
                        pass
                
                # 查找日增长率
                growth_elems = data_nums.select('.ui-font-large.red, .ui-font-large.green')
                if len(growth_elems) > 1:
                    try:
                        growth_text = growth_elems[1].get_text(strip=True)
                        # 移除%符号
                        growth_text = growth_text.rstrip('%')
                        daily_growth_rate = float(growth_text)
                    except (ValueError, IndexError):
                        pass
            
            # 如果未找到，尝试从其他位置获取净值信息
            if unit_net_value == 0.0:
                # 查找包含净值的所有表格
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 2:
                            header = cols[0].get_text(strip=True)
                            value = cols[1].get_text(strip=True)
                            
                            if '单位净值' in header or '最新净值' in header:
                                try:
                                    unit_net_value = float(value)
                                except ValueError:
                                    pass
                            elif '日增长率' in header or '涨幅' in header or '日增幅' in header:
                                try:
                                    value_clean = value.rstrip('%')
                                    daily_growth_rate = float(value_clean)
                                except ValueError:
                                    pass
                            elif '净值日期' in header or '更新日期' in header:
                                update_date = value
            
            # 如果仍未找到净值，尝试从页面的其他部分查找
            if unit_net_value == 0.0:
                # 查找所有包含数字的元素
                all_texts = soup.get_text()
                match = re.search(r'单位净值[：:]\s*([\d.]+)', all_texts)
                if match:
                    try:
                        unit_net_value = float(match.group(1))
                    except ValueError:
                        pass
            
            info['unit_net_value'] = unit_net_value
            info['daily_growth_rate'] = daily_growth_rate
            info['update_date'] = update_date
            info['accumulated_net_value'] = 0.0
            info['status'] = ''
            
            print(f"基金 {fund_code} 使用备用数据源（详情页）成功获取数据")
            return info
        except Exception as e:
            print(f"从备用数据源获取基金信息失败: {fund_code}, 错误: {e}")
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

    def get_fund_history(self, fund_code: str, days: int = 30) -> Optional[List[Dict]]:
        """
        获取基金历史净值数据
        
        Args:
            fund_code: 基金代码
            days: 获取最近N天的数据（默认30天）
        
        Returns:
            历史净值数据列表，或None如果失败
        """
        time.sleep(self.delay)
        
        url = "http://fund.eastmoney.com/f10/F10DataApi.aspx"
        
        history_data = []
        page = 1
        
        # 计算需要抓取的页数（每页最多49条记录）
        # 假设每年252个交易日，pages需要能覆盖days天数的交易日
        max_pages = max(1, (days // 49) + 2)
        
        try:
            while page <= max_pages:
                params = {
                    'type': 'lsjz',
                    'code': fund_code,
                    'page': page,
                    'per': 49
                }
                
                response = self._request(url, params=params)
                if not response:
                    break
                
                # 解析JSON响应
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    print(f"无法解析基金 {fund_code} 的历史数据")
                    break
                
                # 提取净值数据
                datas = data.get('Data', {}).get('LSJZList', [])
                if not datas:
                    break
                
                for record in datas:
                    try:
                        # 解析日期 - 尝试多个可能的字段名
                        date_str = record.get('FSRQ') or record.get('fbrq') or record.get('date') or ''
                        if not date_str:
                            continue
                        
                        # 将日期字符串转换为日期对象
                        try:
                            if len(date_str) == 10:  # 格式: YYYY-MM-DD
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            else:
                                continue
                        except ValueError:
                            continue
                        
                        # 检查是否在指定天数范围内
                        days_ago = (datetime.now() - date_obj).days
                        if days_ago > days:
                            # 已经超出天数范围，可以停止抓取
                            page = max_pages + 1
                            break
                        
                        # 解析净值数据 - 尝试多个可能的字段名
                        unit_net_value = 0.0
                        try:
                            unit_net_value = float(record.get('DWJZ') or record.get('dwjz') or record.get('unit_net_value') or 0)
                        except (ValueError, TypeError):
                            pass
                        
                        accumulated_net_value = 0.0
                        try:
                            accumulated_net_value = float(record.get('LJJZ') or record.get('ljjz') or record.get('accumulated_net_value') or 0)
                        except (ValueError, TypeError):
                            pass
                        
                        daily_growth_rate = 0.0
                        try:
                            daily_growth_rate = float(record.get('JZRQ') or record.get('jzrq') or record.get('daily_growth_rate') or 0)
                        except (ValueError, TypeError):
                            pass
                        
                        growth_rate = record.get('SUNRISERANGE') or record.get('sunriserange') or record.get('growth_rate') or '0%'
                        if isinstance(growth_rate, (int, float)):
                            growth_rate = f"{growth_rate}%"
                        growth_rate = str(growth_rate).strip()
                        
                        history_record = {
                            'fund_code': fund_code,
                            'date': date_str,
                            'unit_net_value': unit_net_value,
                            'accumulated_net_value': accumulated_net_value,
                            'daily_growth_rate': daily_growth_rate,
                            'growth_rate': growth_rate,
                        }
                        history_data.append(history_record)
                    except Exception as e:
                        print(f"解析历史记录时出错: {e}")
                        continue
                
                page += 1
                time.sleep(self.delay)
            
            if history_data:
                print(f"基金 {fund_code} 成功获取 {len(history_data)} 条历史数据")
                return history_data
            else:
                print(f"未获取到基金 {fund_code} 的历史数据")
                return None
                
        except Exception as e:
            print(f"获取基金历史数据失败: {fund_code}, 错误: {e}")
            return None

    def get_multiple_funds_history(self, fund_codes: List[str], days: int = 30) -> Dict[str, List[Dict]]:
        """
        批量获取多个基金的历史数据
        
        Args:
            fund_codes: 基金代码列表
            days: 获取最近N天的数据
            
        Returns:
            {fund_code: [历史数据列表]}
        """
        history_dict = {}
        
        total = len(fund_codes)
        for idx, code in enumerate(fund_codes, 1):
            print(f"[{idx}/{total}] 正在获取基金 {code} 的历史数据...")
            history = self.get_fund_history(code, days=days)
            if history:
                history_dict[code] = history
        
        return history_dict

    def save_history_to_csv(self, history_data: Union[Dict[str, List[Dict]], List[Dict]], filepath: str) -> bool:
        """
        保存历史数据到CSV文件
        
        Args:
            history_data: 历史数据字典或列表
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            # 合并数据
            if isinstance(history_data, dict):
                combined_data = []
                for fund_code, data_list in history_data.items():
                    combined_data.extend(data_list)
            else:
                combined_data = history_data
            
            if not combined_data:
                print("没有数据可保存")
                return False
            
            df = pd.DataFrame(combined_data)
            
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"历史数据已保存到: {filepath}")
            return True
        except Exception as e:
            print(f"保存CSV文件失败: {e}")
            return False

    def save_history_to_json(self, history_data: Union[Dict[str, List[Dict]], List[Dict]], filepath: str) -> bool:
        """
        保存历史数据到JSON文件
        
        Args:
            history_data: 历史数据字典或列表
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            
            print(f"历史数据已保存到: {filepath}")
            return True
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
            return False


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
