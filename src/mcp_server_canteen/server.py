"""
MCP Server implementation for Canteen Data
"""

import os
import logging
from typing import Any, Dict, Tuple
from datetime import datetime, timedelta
import httpx
from mcp.server.fastmcp import FastMCP

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 检查必要的环境变量
required_env_vars = {
    'CANTEEN_API_TOKEN': 'API认证令牌',
    'CANTEEN_API_BASE': 'API基础URL'
}

# 验证环境变量
missing_vars = [var for var, desc in required_env_vars.items() if not os.getenv(var)]
if missing_vars:
    error_msg = "缺少必要的环境变量配置:\n" + "\n".join(
        f"- {var} ({required_env_vars[var]})" for var in missing_vars
    )
    logger.error(error_msg)
    raise EnvironmentError(error_msg)

# 从环境变量获取配置
API_BASE = os.getenv('CANTEEN_API_BASE')
AUTH_TOKEN = f"Bearer {os.getenv('CANTEEN_API_TOKEN')}"
TIMEOUT = 30.0  # 请求超时时间（秒）

class CanteenAPIError(Exception):
    """自定义API错误异常类"""
    pass

def get_relative_dates(period: str) -> Tuple[str, str]:
    """获取相对时间范围的开始和结束日期"""
    today = datetime.now()
    
    if period == 'today':
        return (today.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        return (yesterday.strftime('%Y%m%d'), yesterday.strftime('%Y%m%d'))
    elif period == 'day_before_yesterday':
        day_before_yesterday = today - timedelta(days=2)
        return (day_before_yesterday.strftime('%Y%m%d'), day_before_yesterday.strftime('%Y%m%d'))
    elif period == 'this_week':
        monday = today - timedelta(days=today.weekday())
        return (monday.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
    elif period == 'last_week':
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        return (last_monday.strftime('%Y%m%d'), last_sunday.strftime('%Y%m%d'))
    elif period == 'this_month':
        first_day = today.replace(day=1)
        return (first_day.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
    elif period == 'last_month':
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        return (first_day_last_month.strftime('%Y%m%d'), last_day_last_month.strftime('%Y%m%d'))
    else:
        logger.warning(f"不支持的时间范围: {period}，将使用今天的数据")
        return (today.strftime('%Y%m%d'), today.strftime('%Y%m%d'))

async def make_api_request(url: str) -> Dict[str, Any]:
    """向API发送请求并处理错误"""
    headers = {
        "Authorization": AUTH_TOKEN,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"HTTP请求错误: {str(e)}")
        raise CanteenAPIError(f"HTTP请求失败: {str(e)}")
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        raise CanteenAPIError(f"请求失败: {str(e)}")

def validate_date(date_str: str) -> bool:
    """验证日期格式是否正确"""
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False

def convert_date_format(date_str: str) -> str:
    """将各种日期格式转换为YYYYMMDD格式"""
    if not date_str:
        return None
        
    # 如果已经是YYYYMMDD格式，直接返回
    if len(date_str) == 8 and date_str.isdigit():
        return date_str
        
    # 处理相对日期
    today = datetime.now()
    if date_str.lower() == 'today':
        return today.strftime('%Y%m%d')
    elif date_str.lower() == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday.strftime('%Y%m%d')
    elif date_str.lower() == 'day_before_yesterday':
        day_before_yesterday = today - timedelta(days=2)
        return day_before_yesterday.strftime('%Y%m%d')
    elif date_str.lower() == 'this_week':
        monday = today - timedelta(days=today.weekday())
        return monday.strftime('%Y%m%d')
    elif date_str.lower() == 'last_week':
        last_monday = today - timedelta(days=today.weekday() + 7)
        return last_monday.strftime('%Y%m%d')
    elif date_str.lower() == 'this_month':
        first_day = today.replace(day=1)
        return first_day.strftime('%Y%m%d')
    elif date_str.lower() == 'last_month':
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        return first_day_last_month.strftime('%Y%m%d')
        
    # 尝试不同的日期格式
    date_formats = [
        "%Y-%m-%d",  # 2024-04-01
        "%Y/%m/%d",  # 2024/04/01
        "%Y.%m.%d",  # 2024.04.01
        "%Y年%m月%d日",  # 2024年04月01日
        "%Y年%m月%d号",  # 2024年04月01号
        "%m月%d日",  # 04月01日
        "%m月%d号",  # 04月01号
        "%m-%d",  # 04-01
        "%m/%d",  # 04/01
        "%m.%d",  # 04.01
        "%Y-%m",  # 2024-04
        "%Y/%m",  # 2024/04
        "%Y年%m月",  # 2024年04月
    ]
    
    # 清理输入字符串
    date_str = date_str.strip()
    
    # 处理"号"的情况
    if "号" in date_str:
        date_str = date_str.replace("号", "日")
    
    # 处理没有年份的情况
    if "年" not in date_str and "-" not in date_str and "/" not in date_str and "." not in date_str:
        current_year = datetime.now().year
        if "月" in date_str:
            date_str = f"{current_year}年{date_str}"
        elif "-" in date_str:
            date_str = f"{current_year}-{date_str}"
        elif "/" in date_str:
            date_str = f"{current_year}/{date_str}"
        elif "." in date_str:
            date_str = f"{current_year}.{date_str}"
    
    # 处理只有年月的情况
    if "日" not in date_str and "号" not in date_str:
        if "月" in date_str:
            date_str = f"{date_str}01日"
        elif "-" in date_str:
            date_str = f"{date_str}-01"
        elif "/" in date_str:
            date_str = f"{date_str}/01"
        elif "." in date_str:
            date_str = f"{date_str}.01"
    
    for fmt in date_formats:
        try:
            date = datetime.strptime(date_str, fmt)
            return date.strftime("%Y%m%d")
        except ValueError:
            continue
            
    raise ValueError(f"无法识别的日期格式: {date_str}")

# 初始化FastMCP服务器
mcp = FastMCP("canteen", log_level="INFO")

@mcp.tool()
async def get_canteen_data(start_date: str = None, end_date: str = None, period: str = None) -> str:
    """获取餐厅就餐人数数据"""
    valid_periods = ['today', 'yesterday', 'day_before_yesterday', 'this_week', 'last_week', 'this_month', 'last_month']
    
    if period and period in valid_periods:
        start_date, end_date = get_relative_dates(period)
    elif period:
        logger.warning(f"不支持的时间范围: {period}，将使用指定的日期范围")
        if not start_date or not end_date:
            # 如果没有指定日期范围，则使用今天
            start_date, end_date = get_relative_dates('today')
    elif not start_date or not end_date:
        # 如果没有提供日期参数，默认查询今天的数据
        start_date, end_date = get_relative_dates('today')
    
    # 转换日期格式
    try:
        start_date = convert_date_format(start_date)
        end_date = convert_date_format(end_date)
    except ValueError as e:
        raise ValueError(f"日期格式转换失败: {str(e)}")
    
    # 验证转换后的日期格式
    if not all(validate_date(date) for date in [start_date, end_date]):
        raise ValueError("日期格式不正确，请使用YYYYMMDD格式")
    
    url = f"{API_BASE}/rsdata/totalnumberofconsumers?startTime={start_date}&endTime={end_date}"
    
    try:
        data = await make_api_request(url)
        
        if not data or "success" not in data or not data["success"]:
            error_msg = data.get("error", "未知错误") if isinstance(data, dict) else "请求失败"
            raise CanteenAPIError(f"API返回错误: {error_msg}")
        
        morning_count = data["data"]["morningCount"]
        afternoon_count = data["data"]["afternoonCount"]
        total_count = morning_count + afternoon_count
        
        period_titles = {
            'today': '今日',
            'yesterday': '昨日',
            'day_before_yesterday': '前天',
            'this_week': '本周',
            'last_week': '上周',
            'this_month': '本月',
            'last_month': '上月'
        }
        
        title = period_titles.get(period, f"{start_date} 至 {end_date}")
        
        return f"""
餐厅就餐人数统计 ({title}):
日期范围: {start_date} 至 {end_date}
早餐人数: {morning_count} 人
午餐人数: {afternoon_count} 人
总计: {total_count} 人
"""
    except CanteenAPIError as e:
        logger.error(f"获取餐厅数据失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"处理餐厅数据时发生错误: {str(e)}")
        raise CanteenAPIError(f"处理数据失败: {str(e)}")

def run_server():
    """运行MCP服务器"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    run_server()