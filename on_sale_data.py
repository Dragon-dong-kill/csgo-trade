import requests
import json
from datetime import datetime
import pandas as pd
import time

def get_on_sale_data(item_id):
    """
    获取指定物品的在售量数据
    
    Args:
        item_id (str): 物品ID
        
    Returns:
        dict: 包含在售量数据的字典
    """
    try:
        # 构建API URL
        timestamp = int(datetime.now().timestamp() * 1000)
        url = f"https://sdt-api.ok-skins.com/user/skin/v1/current-sell?timestamp={timestamp}&itemId={item_id}"
        
        # 发送请求
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success') == True and data.get('data'):
            return parse_on_sale_data(data['data'])
        else:
            return {
                'success': False,
                'error': f"API返回错误: {data.get('errorMsg', '未知错误')}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"网络请求失败: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"数据处理失败: {str(e)}"
        }

def parse_on_sale_data(data):
    """
    解析在售量数据
    
    Args:
        data: API返回的原始数据
        
    Returns:
        dict: 解析后的在售量数据
    """
    try:
        platforms = []
        total_on_sale = 0
        
        for platform_data in data:
            platform_name = platform_data.get('platformName', '未知平台')
            on_sale_count = platform_data.get('sellCount', 0)
            min_price = platform_data.get('price', 0)
            
            platforms.append({
                'platform': platform_name,
                'on_sale_count': on_sale_count,
                'min_price': min_price
            })
            
            total_on_sale += on_sale_count
        
        return {
            'success': True,
            'total_on_sale': total_on_sale,
            'platforms': platforms,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"数据解析失败: {str(e)}"
        }

def analyze_supply_demand(on_sale_data, volume_data=None):
    """
    分析供需状况
    
    Args:
        on_sale_data (dict): 在售量数据
        volume_data (dict): 成交量数据（可选）
        
    Returns:
        dict: 供需分析结果
    """
    if not on_sale_data.get('success'):
        return {
            'success': False,
            'error': '在售量数据无效'
        }
    
    total_on_sale = on_sale_data['total_on_sale']
    
    # 基础供需分析
    if total_on_sale < 100:
        supply_level = '稀缺'
        supply_score = 90
    elif total_on_sale < 500:
        supply_level = '偏少'
        supply_score = 70
    elif total_on_sale < 1000:
        supply_level = '正常'
        supply_score = 50
    elif total_on_sale < 2000:
        supply_level = '充足'
        supply_score = 30
    else:
        supply_level = '过剩'
        supply_score = 10
    
    # 如果有成交量数据，进行更详细的分析
    demand_analysis = None
    if volume_data:
        # 这里可以添加成交量与在售量的比较分析
        pass
    
    return {
        'success': True,
        'total_on_sale': total_on_sale,
        'supply_level': supply_level,
        'supply_score': supply_score,
        'analysis': f"当前在售量为{total_on_sale}个，供应状况：{supply_level}",
        'recommendation': get_trading_recommendation(supply_score)
    }

def get_trading_recommendation(supply_score):
    """
    根据供应分数给出交易建议
    
    Args:
        supply_score (int): 供应分数 (0-100)
        
    Returns:
        str: 交易建议
    """
    if supply_score >= 80:
        return "供应稀缺，建议买入持有，价格可能上涨"
    elif supply_score >= 60:
        return "供应偏少，可考虑买入，注意价格波动"
    elif supply_score >= 40:
        return "供应正常，观望为主，等待更好时机"
    elif supply_score >= 20:
        return "供应充足，谨慎买入，可能存在价格压力"
    else:
        return "供应过剩，建议避免买入，价格可能下跌"

# 物品ID映射表（从on-sale-data.txt更新）
ITEM_ID_MAP = {
    "树篱迷宫（久经沙场）": "525873303",
    "克拉考": "1315936965627445248", 
    "怪兽在b": "1315999843394654208",
    "水栽竹": "26422",
    "tyloo": "925497374167523328",
    "出逃的萨利": "808803044176429056",
    # 保留原有的示例映射
    "Lynn Vision (Gold)": "1244761416324870144",
}

# 在售数据URL映射表（从on-sale-data.txt提取）
ON_SALE_URL_MAP = {
    "树篱迷宫（久经沙场）": "https://sdt-api.ok-skins.com/user/skin/v1/current-sell?timestamp=1749039724950&itemId=525873303",
    "克拉考": "https://sdt-api.ok-skins.com/user/skin/v1/current-sell?timestamp=1749039969883&itemId=1315936965627445248",
    "怪兽在b": "https://sdt-api.ok-skins.com/user/skin/v1/current-sell?timestamp=1749039994465&itemId=1315999843394654208",
    "水栽竹": "https://sdt-api.ok-skins.com/user/skin/v1/current-sell?timestamp=1749040017058&itemId=26422",
    "tyloo": "https://sdt-api.ok-skins.com/user/skin/v1/current-sell?timestamp=1749040047017&itemId=925497374167523328",
    "出逃的萨利": "https://sdt-api.ok-skins.com/user/skin/v1/current-sell?timestamp=1749040067008&itemId=808803044176429056"
}

def get_on_sale_data_by_url(item_name):
    """
    根据物品名称使用预设URL获取在售量数据
    
    Args:
        item_name (str): 物品名称
        
    Returns:
        dict: 在售量数据
    """
    url = ON_SALE_URL_MAP.get(item_name)
    if not url:
        return {
            'success': False,
            'error': f"未找到物品 '{item_name}' 的在售数据URL"
        }
    
    try:
        # 发送请求
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success') == True and data.get('data'):
            return parse_on_sale_data(data['data'])
        else:
            return {
                'success': False,
                'error': f"API返回错误: {data.get('errorMsg', '未知错误')}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"网络请求失败: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"数据处理失败: {str(e)}"
        }

def get_all_available_items():
    """
    获取所有可用的物品列表
    
    Returns:
        list: 可用物品名称列表
    """
    return list(ON_SALE_URL_MAP.keys())

def batch_get_on_sale_data(item_names=None):
    """
    批量获取在售量数据
    
    Args:
        item_names (list): 物品名称列表，如果为None则获取所有物品
        
    Returns:
        dict: 批量在售量数据
    """
    if item_names is None:
        item_names = get_all_available_items()
    
    results = {}
    for item_name in item_names:
        results[item_name] = get_on_sale_data_by_url(item_name)
        # 添加小延迟避免请求过于频繁
        time.sleep(0.1)
    
    return results 

def get_item_id(item_name):
    """
    根据物品名称获取物品ID（向后兼容函数）
    
    Args:
        item_name (str): 物品名称
        
    Returns:
        str: 物品ID，如果未找到返回None
    """
    return ITEM_ID_MAP.get(item_name)

def get_on_sale_data_by_name(item_name):
    """
    根据物品名称获取在售量数据（向后兼容函数）
    
    Args:
        item_name (str): 物品名称
        
    Returns:
        dict: 在售量数据
    """
    # 优先使用新的URL方法
    if item_name in ON_SALE_URL_MAP:
        return get_on_sale_data_by_url(item_name)
    
    # 回退到原有的ID方法
    item_id = get_item_id(item_name)
    if not item_id:
        return {
            'success': False,
            'error': f"未找到物品 '{item_name}' 的ID映射或URL"
        }
    
    return get_on_sale_data(item_id)

def analyze_market_behavior(historical_data):
    """
    分析主力行为和行情趋势
    
    Args:
        historical_data (list): 历史在售量和价格数据
        格式: [{'date': '2024-01-01', 'on_sale_count': 1000, 'min_price': 100}, ...]
        
    Returns:
        dict: 主力行为分析结果
    """
    if len(historical_data) < 3:
        return {
            'success': False,
            'error': '数据不足，至少需要3个时间点的数据'
        }
    
    try:
        # 计算趋势指标
        trends = calculate_trends(historical_data)
        
        # 主力行为判断
        main_force_behavior = analyze_main_force_behavior(trends)
        
        # 行情阶段判断
        market_phase = analyze_market_phase(trends)
        
        # 综合分析
        comprehensive_analysis = generate_comprehensive_analysis(main_force_behavior, market_phase, trends)
        
        return {
            'success': True,
            'main_force_behavior': main_force_behavior,
            'market_phase': market_phase,
            'trends': trends,
            'comprehensive_analysis': comprehensive_analysis,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"分析失败: {str(e)}"
        }

def calculate_trends(historical_data):
    """计算各种趋势指标"""
    # 按日期排序
    data = sorted(historical_data, key=lambda x: x['date'])
    
    # 提取数据
    dates = [item['date'] for item in data]
    on_sale_counts = [item['on_sale_count'] for item in data]
    min_prices = [item['min_price'] for item in data]
    
    # 计算变化率
    on_sale_changes = []
    price_changes = []
    
    for i in range(1, len(data)):
        # 在售量变化率
        if on_sale_counts[i-1] != 0:
            on_sale_change = (on_sale_counts[i] - on_sale_counts[i-1]) / on_sale_counts[i-1] * 100
        else:
            on_sale_change = 0
        on_sale_changes.append(on_sale_change)
        
        # 价格变化率
        if min_prices[i-1] != 0:
            price_change = (min_prices[i] - min_prices[i-1]) / min_prices[i-1] * 100
        else:
            price_change = 0
        price_changes.append(price_change)
    
    # 计算相关性
    correlation = calculate_correlation(on_sale_changes, price_changes)
    
    # 计算移动平均
    on_sale_ma = calculate_moving_average(on_sale_counts, 3)
    price_ma = calculate_moving_average(min_prices, 3)
    
    return {
        'dates': dates,
        'on_sale_counts': on_sale_counts,
        'min_prices': min_prices,
        'on_sale_changes': on_sale_changes,
        'price_changes': price_changes,
        'correlation': correlation,
        'on_sale_ma': on_sale_ma,
        'price_ma': price_ma,
        'latest_on_sale': on_sale_counts[-1],
        'latest_price': min_prices[-1],
        'on_sale_trend': 'up' if on_sale_changes[-1] > 0 else 'down' if on_sale_changes[-1] < 0 else 'stable',
        'price_trend': 'up' if price_changes[-1] > 0 else 'down' if price_changes[-1] < 0 else 'stable'
    }

def analyze_main_force_behavior(trends):
    """基于量价关系分析主力行为和下一步意图"""
    on_sale_changes = trends['on_sale_changes']
    price_changes = trends['price_changes']
    correlation = trends['correlation']
    
    # 最近的变化
    recent_on_sale_change = on_sale_changes[-1] if on_sale_changes else 0
    recent_price_change = price_changes[-1] if price_changes else 0
    
    # 计算趋势强度（最近3个周期的平均变化）
    recent_periods = min(3, len(price_changes))
    recent_price_trend = sum(price_changes[-recent_periods:]) / recent_periods if recent_periods > 0 else 0
    recent_on_sale_trend = sum(on_sale_changes[-recent_periods:]) / recent_periods if recent_periods > 0 else 0
    
    behavior_signals = []
    confidence = 0
    main_intention = "观望等待"  # 主力下一步意图
    
    # === 核心量价关系判断 ===
    
    # 1. 量减价涨 - 主力控盘阶段
    if recent_on_sale_change < -5 and recent_price_change > 1:
        if recent_price_trend > 2:  # 持续上涨趋势
            behavior_signals.append("主力强势控盘，筹码高度集中")
            main_intention = "继续拉升"
            confidence += 40
        else:
            behavior_signals.append("主力开始控盘，试探性拉升")
            main_intention = "测试抛压"
            confidence += 25
    
    # 2. 量增价涨 - 启动或出货前奏
    elif recent_on_sale_change > 8 and recent_price_change > 2:
        if recent_price_trend > 3:  # 强势上涨中
            behavior_signals.append("放量上涨，可能是启动信号")
            main_intention = "吸引跟风"
            confidence += 35
        else:
            behavior_signals.append("放量上涨，需观察后续")
            main_intention = "试探市场"
            confidence += 20
    
    # 3. 量增价跌 - 主力出货
    elif recent_on_sale_change > 10 and recent_price_change < -2:
        if recent_price_change < -5:  # 暴跌
            behavior_signals.append("放量暴跌，恐慌性抛售")
            main_intention = "快速出货"
            confidence += 50
        else:
            behavior_signals.append("放量下跌，主力开始出货")
            main_intention = "逐步减仓"
            confidence += 35
    
    # 4. 量减价跌 - 洗盘或筑底
    elif recent_on_sale_change < -8 and recent_price_change < -1:
        if recent_price_trend < -2:  # 持续下跌中
            behavior_signals.append("缩量下跌，主力可能在洗盘")
            main_intention = "清洗浮筹"
            confidence += 30
        else:
            behavior_signals.append("缩量调整，可能接近底部")
            main_intention = "准备吸筹"
            confidence += 25
    
    # 5. 量平价涨 - 无量上涨
    elif abs(recent_on_sale_change) < 5 and recent_price_change > 2:
        behavior_signals.append("无量上涨，主力高度控盘")
        main_intention = "稳步推高"
        confidence += 30
    
    # 6. 量平价跌 - 无量下跌
    elif abs(recent_on_sale_change) < 5 and recent_price_change < -2:
        behavior_signals.append("无量下跌，抛压有限")
        main_intention = "等待时机"
        confidence += 20
    
    # === 特殊量价关系判断 ===
    
    # 量价背离 - 重要转折信号
    if len(price_changes) >= 3:
        recent_prices = trends['min_prices'][-3:]
        # 价格新高但量能萎缩
        if (recent_prices[-1] > max(recent_prices[:-1]) and 
            recent_on_sale_change < -8):
            behavior_signals.append("⚠️ 量价背离，上涨乏力")
            main_intention = "准备变盘"
            confidence += 25
        
        # 价格新低但量能萎缩
        elif (recent_prices[-1] < min(recent_prices[:-1]) and 
              recent_on_sale_change < -5):
            behavior_signals.append("🟢 量价背离，下跌乏力")
            main_intention = "准备反弹"
            confidence += 25
    
    # 持续性分析
    if len(price_changes) >= 3:
        # 连续上涨且量能配合
        consecutive_rises = sum(1 for change in price_changes[-3:] if change > 0)
        if consecutive_rises >= 2 and recent_on_sale_trend < -3:
            behavior_signals.append("量价配合良好，上升趋势健康")
            main_intention = "持续推高"
            confidence += 15
        
        # 连续下跌且放量
        consecutive_falls = sum(1 for change in price_changes[-3:] if change < 0)
        if consecutive_falls >= 2 and recent_on_sale_trend > 5:
            behavior_signals.append("量价齐跌，下跌趋势确立")
            main_intention = "继续出货"
            confidence += 15
    
    # 相关性分析
    if correlation < -0.6:
        behavior_signals.append("量价负相关，走势健康")
        confidence += 10
    elif correlation > 0.6:
        behavior_signals.append("量价正相关，需要警惕")
        confidence += 15
    
    # 综合判断主力行为强度
    if confidence >= 40:
        behavior_level = "强烈"
    elif confidence >= 30:
        behavior_level = "明显"
    elif confidence >= 20:
        behavior_level = "轻微"
    else:
        behavior_level = "不明显"
    
    return {
        'signals': behavior_signals,
        'confidence': confidence,
        'level': behavior_level,
        'main_intention': main_intention,  # 主力下一步意图
        'recent_on_sale_change': recent_on_sale_change,
        'recent_price_change': recent_price_change,
        'recent_price_trend': recent_price_trend,
        'recent_on_sale_trend': recent_on_sale_trend,
        'correlation': correlation
    }

def analyze_market_phase(trends):
    """基于量价关系判断行情阶段"""
    on_sale_counts = trends['on_sale_counts']
    min_prices = trends['min_prices']
    on_sale_changes = trends['on_sale_changes']
    price_changes = trends['price_changes']
    
    # 计算趋势强度
    avg_on_sale_change = sum(on_sale_changes) / len(on_sale_changes) if on_sale_changes else 0
    avg_price_change = sum(price_changes) / len(price_changes) if price_changes else 0
    
    # 最近变化
    recent_on_sale_change = on_sale_changes[-1] if on_sale_changes else 0
    recent_price_change = price_changes[-1] if price_changes else 0
    
    phase_signals = []
    phase_score = 0
    main_phase = "观望期"
    
    # === 基于量价关系的行情阶段判断 ===
    
    # 1. 吸筹期 - 量缩价稳或微跌
    if avg_on_sale_change < -5 and abs(avg_price_change) < 2:
        phase_signals.append("主力吸筹期 - 悄然收集筹码")
        main_phase = "吸筹期"
        phase_score += 35
        
        # 深度吸筹
        if avg_on_sale_change < -10:
            phase_signals.append("深度吸筹 - 大量收集筹码")
            phase_score += 10
    
    # 2. 启动期 - 量减价涨，开始拉升
    elif avg_on_sale_change < -3 and avg_price_change > 2:
        phase_signals.append("行情启动期 - 主力开始拉升")
        main_phase = "启动期"
        phase_score += 40
        
        # 强势启动
        if avg_price_change > 5:
            phase_signals.append("强势启动 - 快速脱离成本区")
            phase_score += 15
    
    # 3. 拉升期 - 量价配合，持续上涨
    elif avg_on_sale_change > -2 and avg_price_change > 3:
        phase_signals.append("拉升期 - 量价配合上涨")
        main_phase = "拉升期"
        phase_score += 35
        
        # 加速拉升
        if avg_on_sale_change > 5 and avg_price_change > 6:
            phase_signals.append("加速拉升 - 市场情绪高涨")
            phase_score += 15
    
    # 4. 出货期 - 量增价涨或量增价平
    elif avg_on_sale_change > 8 and avg_price_change > -1:
        if avg_price_change > 2:
            phase_signals.append("出货期 - 边拉边出")
            main_phase = "出货期"
        else:
            phase_signals.append("出货期 - 高位震荡出货")
            main_phase = "出货期"
        phase_score += 45
        
        # 大量出货
        if avg_on_sale_change > 15:
            phase_signals.append("大量出货 - 主力急于离场")
            phase_score += 10
    
    # 5. 下跌期 - 量增价跌
    elif avg_on_sale_change > 5 and avg_price_change < -2:
        phase_signals.append("下跌期 - 恐慌性抛售")
        main_phase = "下跌期"
        phase_score += 40
        
        # 暴跌期
        if avg_price_change < -8:
            phase_signals.append("暴跌期 - 踩踏式下跌")
            phase_score += 15
    
    # 6. 筑底期 - 量缩价跌
    elif avg_on_sale_change < -2 and avg_price_change < -1:
        phase_signals.append("筑底期 - 抛压逐渐减轻")
        main_phase = "筑底期"
        phase_score += 30
        
        # 底部企稳
        if recent_price_change > avg_price_change:  # 近期跌幅收窄
            phase_signals.append("底部企稳 - 下跌动能衰竭")
            phase_score += 10
    
    # 7. 横盘期 - 量价都平稳
    elif abs(avg_on_sale_change) < 3 and abs(avg_price_change) < 1.5:
        phase_signals.append("横盘整理期 - 多空力量均衡")
        main_phase = "横盘期"
        phase_score += 20
        
        # 收敛整理
        if abs(recent_on_sale_change) < abs(avg_on_sale_change):
            phase_signals.append("收敛整理 - 变盘在即")
            phase_score += 10
    
    # === 特殊阶段判断 ===
    
    # 量价背离阶段
    correlation = trends['correlation']
    if abs(correlation) > 0.7:
        if correlation > 0:
            phase_signals.append("异常阶段 - 量价同向异常")
        else:
            phase_signals.append("健康阶段 - 量价反向正常")
        phase_score += 5
    
    # 波动率分析
    on_sale_volatility = calculate_volatility(on_sale_changes)
    price_volatility = calculate_volatility(price_changes)
    
    if on_sale_volatility > 15 or price_volatility > 5:
        phase_signals.append("高波动期 - 市场情绪激烈")
        phase_score += 10
    elif on_sale_volatility < 5 and price_volatility < 2:
        phase_signals.append("低波动期 - 市场缺乏活力")
        phase_score += 5
    
    return {
        'main_phase': main_phase,
        'signals': phase_signals,
        'score': phase_score,
        'avg_on_sale_change': avg_on_sale_change,
        'avg_price_change': avg_price_change,
        'on_sale_volatility': on_sale_volatility,
        'price_volatility': price_volatility
    }

def generate_comprehensive_analysis(main_force_behavior, market_phase, trends):
    """基于量价关系生成主力意图分析和操作建议"""
    analysis = {
        'summary': '',
        'key_points': [],
        'trading_suggestion': '',
        'risk_warning': '',
        'confidence_level': 0,
        'main_intention': '',
        'next_move': ''
    }
    
    # 综合置信度
    total_confidence = main_force_behavior['confidence'] + market_phase['score']
    analysis['confidence_level'] = min(total_confidence, 100)
    
    # 获取关键信息
    main_intention = main_force_behavior.get('main_intention', '观望等待')
    main_phase = market_phase['main_phase']
    signals = main_force_behavior['signals']
    phase_signals = market_phase['signals']
    
    # 关键要点
    analysis['key_points'].extend(signals[:2])  # 主力行为信号
    analysis['key_points'].extend(phase_signals[:1])  # 行情阶段信号
    
    # 生成摘要
    analysis['summary'] = f"当前处于{main_phase}，主力意图：{main_intention}"
    analysis['main_intention'] = main_intention
    
    # === 基于量价关系的操作建议 ===
    
    # 1. 吸筹期策略
    if main_phase == "吸筹期":
        if "深度吸筹" in str(phase_signals):
            analysis['trading_suggestion'] = "主力深度吸筹，可逢低分批建仓"
            analysis['next_move'] = "继续收集筹码，等待启动时机"
            analysis['risk_warning'] = "吸筹期可能较长，需要耐心等待"
        else:
            analysis['trading_suggestion'] = "主力开始吸筹，可小量试探性建仓"
            analysis['next_move'] = "观察吸筹力度，准备加仓"
            analysis['risk_warning'] = "确认吸筹信号后再加大仓位"
    
    # 2. 启动期策略
    elif main_phase == "启动期":
        if main_intention == "继续拉升":
            analysis['trading_suggestion'] = "行情启动确认，建议积极参与"
            analysis['next_move'] = "主力将持续推高价格"
            analysis['risk_warning'] = "注意控制仓位，设置止损位"
        else:
            analysis['trading_suggestion'] = "启动信号出现，可适量跟进"
            analysis['next_move'] = "测试市场反应，决定后续力度"
            analysis['risk_warning'] = "观察是否为假突破"
    
    # 3. 拉升期策略
    elif main_phase == "拉升期":
        if "加速拉升" in str(phase_signals):
            analysis['trading_suggestion'] = "加速拉升阶段，享受趋势红利"
            analysis['next_move'] = "主力全力推高，吸引跟风盘"
            analysis['risk_warning'] = "加速期接近尾声，准备减仓"
        else:
            analysis['trading_suggestion'] = "稳步拉升中，持有为主"
            analysis['next_move'] = "稳步推高价格，控制节奏"
            analysis['risk_warning'] = "注意主力出货信号"
    
    # 4. 出货期策略
    elif main_phase == "出货期":
        if main_intention == "快速出货":
            analysis['trading_suggestion'] = "主力急于出货，立即离场"
            analysis['next_move'] = "快速清仓，不计成本"
            analysis['risk_warning'] = "避免抄底，严格止损"
        else:
            analysis['trading_suggestion'] = "主力开始出货，逐步减仓"
            analysis['next_move'] = "边拉边出，维持价格"
            analysis['risk_warning'] = "出货期风险极高，及时离场"
    
    # 5. 下跌期策略
    elif main_phase == "下跌期":
        if "暴跌期" in str(phase_signals):
            analysis['trading_suggestion'] = "恐慌性下跌，空仓观望"
            analysis['next_move'] = "任由价格下跌，清洗市场"
            analysis['risk_warning'] = "暴跌期不宜抄底"
        else:
            analysis['trading_suggestion'] = "下跌趋势确立，保持观望"
            analysis['next_move'] = "继续施压，清洗浮筹"
            analysis['risk_warning'] = "等待下跌结束信号"
    
    # 6. 筑底期策略
    elif main_phase == "筑底期":
        if main_intention == "准备反弹":
            analysis['trading_suggestion'] = "筑底完成，可考虑布局"
            analysis['next_move'] = "准备新一轮行情"
            analysis['risk_warning'] = "确认底部信号后再行动"
        else:
            analysis['trading_suggestion'] = "底部区域，可分批建仓"
            analysis['next_move'] = "继续收集低价筹码"
            analysis['risk_warning'] = "筑底过程可能反复"
    
    # 7. 横盘期策略
    elif main_phase == "横盘期":
        if "变盘在即" in str(phase_signals):
            analysis['trading_suggestion'] = "变盘临近，密切关注方向"
            analysis['next_move'] = "准备选择突破方向"
            analysis['risk_warning'] = "变盘方向不明，控制仓位"
        else:
            analysis['trading_suggestion'] = "横盘整理中，区间操作"
            analysis['next_move'] = "维持价格区间，消化获利盘"
            analysis['risk_warning'] = "整理期避免重仓"
    
    # 默认策略
    else:
        analysis['trading_suggestion'] = "信号不明确，保持观望"
        analysis['next_move'] = "等待明确的量价信号"
        analysis['risk_warning'] = "不明确阶段避免盲目操作"
    
    # === 特殊情况处理 ===
    
    # 量价背离情况
    if "量价背离" in str(signals):
        if "上涨乏力" in str(signals):
            analysis['trading_suggestion'] = "量价背离警告，建议减仓"
            analysis['risk_warning'] = "顶部背离风险，及时离场"
        elif "下跌乏力" in str(signals):
            analysis['trading_suggestion'] = "底部背离机会，可适量建仓"
            analysis['risk_warning'] = "确认反转信号后加仓"
    
    # 根据置信度调整建议
    if analysis['confidence_level'] < 30:
        analysis['trading_suggestion'] = "信号置信度较低，" + analysis['trading_suggestion']
        analysis['risk_warning'] += "，建议谨慎决策"
    elif analysis['confidence_level'] > 70:
        analysis['trading_suggestion'] = "信号明确，" + analysis['trading_suggestion']
        analysis['risk_warning'] += "，但仍需严格风控"
    
    return analysis

def calculate_correlation(x, y):
    """计算相关系数"""
    if len(x) != len(y) or len(x) < 2:
        return 0
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(x[i] ** 2 for i in range(n))
    sum_y2 = sum(y[i] ** 2 for i in range(n))
    
    denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
    if denominator == 0:
        return 0
    
    correlation = (n * sum_xy - sum_x * sum_y) / denominator
    return correlation

def calculate_moving_average(data, window):
    """计算移动平均"""
    if len(data) < window:
        return data
    
    ma = []
    for i in range(len(data)):
        if i < window - 1:
            ma.append(data[i])
        else:
            avg = sum(data[i-window+1:i+1]) / window
            ma.append(avg)
    
    return ma

def calculate_volatility(data):
    """计算波动率"""
    if len(data) < 2:
        return 0
    
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    volatility = variance ** 0.5
    
    return volatility

def simulate_historical_data(item_name, days=7):
    """
    模拟历史数据（用于演示，实际应用中需要真实的历史数据）
    
    Args:
        item_name (str): 物品名称
        days (int): 模拟天数
        
    Returns:
        list: 模拟的历史数据
    """
    import random
    from datetime import datetime, timedelta
    
    # 获取当前数据作为基准
    current_data = get_on_sale_data_by_url(item_name)
    if not current_data.get('success'):
        return []
    
    base_count = current_data['total_on_sale']
    base_price = min([p['min_price'] for p in current_data['platforms'] if p['min_price'] > 0], default=1000)
    
    historical_data = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        
        # 模拟数据变化
        count_variation = random.uniform(-0.2, 0.2)  # ±20%变化
        price_variation = random.uniform(-0.1, 0.1)  # ±10%变化
        
        simulated_count = int(base_count * (1 + count_variation))
        simulated_price = base_price * (1 + price_variation)
        
        historical_data.append({
            'date': date,
            'on_sale_count': simulated_count,
            'min_price': simulated_price
        })
    
    return historical_data 