# -*- coding:utf-8 -*-
"""
@Author: danny
@Date: 2025-04-07
@File: canteen.py
@Description: 职工餐厅就餐人数查询MCP服务器
"""

from typing import Any, Optional, Dict, Tuple
import httpx
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
import logging
import os

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

# 初始化FastMCP服务器
mcp = FastMCP("canteen", log_level="INFO")

# 从环境变量获取配置
API_BASE = os.getenv('CANTEEN_API_BASE')
AUTH_TOKEN = f"Bearer {os.getenv('CANTEEN_API_TOKEN')}"
TIMEOUT = 30.0  # 请求超时时间（秒）


class CanteenAPIError(Exception):
    """自定义API错误异常类"""
    pass


def get_relative_dates(period: str) -> Tuple[str, str]:
    """获取相对时间范围的开始和结束日期
    
    参数:
        period: 时间范围，支持以下值：
            - 'today': 今天
            - 'yesterday': 昨天
            - 'this_week': 本周（周一到今天）
            - 'last_week': 上周（周一到周日）
            - 'this_month': 本月（1号到今天）
            - 'last_month': 上月（1号到最后一天）
        
    返回:
        Tuple[str, str]: (开始日期, 结束日期)，格式为YYYYMMDD
    """
    today = datetime.now()
    
    if period == 'today':
        return (today.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
    
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        return (yesterday.strftime('%Y%m%d'), yesterday.strftime('%Y%m%d'))
    
    elif period == 'this_week':
        # 获取本周一
        monday = today - timedelta(days=today.weekday())
        return (monday.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
    
    elif period == 'last_week':
        # 获取上周一和上周日
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        return (last_monday.strftime('%Y%m%d'), last_sunday.strftime('%Y%m%d'))
    
    elif period == 'this_month':
        # 获取本月1号
        first_day = today.replace(day=1)
        return (first_day.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
    
    elif period == 'last_month':
        # 获取上月1号和最后一天
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        return (first_day_last_month.strftime('%Y%m%d'), last_day_last_month.strftime('%Y%m%d'))
    
    else:
        raise ValueError(f"不支持的时间范围: {period}")


async def make_api_request(url: str) -> Dict[str, Any]:
    """向API发送请求并处理错误
    
    参数:
        url: API请求URL
        
    返回:
        Dict[str, Any]: API响应数据
        
    异常:
        CanteenAPIError: 当API请求失败时抛出
    """
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
    """验证日期格式是否正确
    
    参数:
        date_str: 日期字符串，格式为YYYYMMDD
        
    返回:
        bool: 日期格式是否正确
    """
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False


@mcp.tool()
async def get_canteen_data(start_date: str = None, end_date: str = None, period: str = None) -> str:
    """获取餐厅就餐人数数据
    
    参数:
        start_date: 开始日期，格式为YYYYMMDD（如20250331）
        end_date: 结束日期，格式为YYYYMMDD（如20250331）
        period: 时间范围，支持：today, yesterday, this_week, last_week, this_month, last_month
        
    返回:
        str: 格式化后的餐厅就餐人数统计信息
        
    异常:
        ValueError: 当日期格式不正确时抛出
        CanteenAPIError: 当API请求失败时抛出
    """
    # 处理相对时间
    if period:
        start_date, end_date = get_relative_dates(period)
    elif not start_date or not end_date:
        raise ValueError("必须提供开始日期和结束日期，或者指定时间范围")
    
    # 验证日期格式
    if not all(validate_date(date) for date in [start_date, end_date]):
        raise ValueError("日期格式不正确，请使用YYYYMMDD格式")
    
    url = f"{API_BASE}/rsdata/totalnumberofconsumers?startTime={start_date}&endTime={end_date}"
    
    try:
        data = await make_api_request(url)
        
        if not data or "success" not in data or not data["success"]:
            error_msg = data.get("error", "未知错误") if isinstance(data, dict) else "请求失败"
            raise CanteenAPIError(f"API返回错误: {error_msg}")
        
        morning_count = data["data"]["morningCount"]  # 早餐人数
        afternoon_count = data["data"]["afternoonCount"]  # 午餐人数
        total_count = morning_count + afternoon_count  # 总人数
        
        # 根据时间范围显示不同的标题
        period_titles = {
            'today': '今日',
            'yesterday': '昨日',
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


async def main():
    """主函数，用于本地测试"""
    try:
        # 测试不同时间范围
        for period in ['today', 'yesterday', 'this_week', 'last_week', 'this_month', 'last_month']:
            data = await get_canteen_data(period=period)
            print(data)
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        raise


if __name__ == "__main__":
    # 作为MCP服务器运行
    mcp.run(transport='stdio')
    
    # 本地测试代码（已注释）
    # import asyncio
    # asyncio.run(main())
