import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time
import json
import warnings
warnings.filterwarnings('ignore')

# 导入在售量数据集成模块
try:
    import on_sale_data
    import market_data_integration
    ON_SALE_DATA_AVAILABLE = True
except ImportError:
    ON_SALE_DATA_AVAILABLE = False

# 设置页面配置为宽屏模式 - 必须是第一个Streamlit命令
st.set_page_config(
    page_title="CS:GO饰品交易策略分析平台",
    page_icon="📊",
    layout="wide",  # 使用宽屏布局
    initial_sidebar_state="expanded"
)

# 添加技术分析库
try:
    import pandas_ta as ta
    TALIB_AVAILABLE = True
    st.success("✅ 技术分析库已加载，将使用pandas-ta提供高性能指标计算")
except ImportError:
    TALIB_AVAILABLE = False
    st.warning("⚠️ 技术分析库未安装，将使用传统方法计算指标")

# 添加自定义CSS样式来进一步扩展界面宽度
st.markdown("""
<style>
    /* 导入现代字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* CSS变量定义 */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f093fb;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card-shadow: 0 10px 40px rgba(31, 38, 135, 0.2);
        --border-radius: 16px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* 全局字体 */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 主容器优化 */
    .main .block-container {
        max-width: 96% !important;
        padding: 2rem 2rem 4rem 2rem !important;
    }
    
    /* 侧边栏增强 */
    .css-1d391kg {
        width: 400px !important;
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* 图表容器美化 */
    .stPlotlyChart {
        background: rgba(255, 255, 255, 0.03);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: var(--card-shadow);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: var(--transition);
    }
    
    .stPlotlyChart:hover {
        box-shadow: 0 15px 50px rgba(31, 38, 135, 0.3);
        transform: translateY(-2px);
    }
    
    /* 指标卡片升级 */
    .metric-card {
        background: var(--background-gradient);
        padding: 28px;
        border-radius: var(--border-radius);
        color: white;
        margin: 20px 0;
        box-shadow: var(--card-shadow);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
        transition: var(--transition);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-color), #fff);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(31, 38, 135, 0.4);
    }
    
    /* 投资组合摘要美化 */
    .portfolio-summary {
        background: rgba(255, 255, 255, 0.04);
        padding: 35px;
        border-radius: var(--border-radius);
        margin: 25px 0;
        box-shadow: var(--card-shadow);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
    }
    
    .portfolio-summary::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: var(--background-gradient);
        border-radius: var(--border-radius) var(--border-radius) 0 0;
    }
    
    /* 价格显示优化 */
    .price-display {
        background: linear-gradient(45deg, var(--success-color), #66BB6A);
        color: white;
        padding: 18px 24px;
        border-radius: var(--border-radius);
        font-weight: 600;
        font-size: 1.2rem;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .price-display::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.6s;
    }
    
    .price-display:hover::after {
        left: 100%;
    }
    
    /* 标题样式升级 */
    .main-header {
        background: var(--background-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.8rem;
        font-weight: 700;
        margin-bottom: 2.5rem;
        letter-spacing: -0.03em;
    }
    
    .sub-header {
        color: var(--primary-color);
        border-bottom: 3px solid var(--primary-color);
        padding-bottom: 15px;
        margin: 30px 0;
        font-weight: 600;
        font-size: 1.6rem;
        position: relative;
    }
    
    .sub-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 80px;
        height: 3px;
        background: var(--accent-color);
        border-radius: 2px;
    }
    
    /* 按钮样式大幅提升 */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: none;
        background: var(--background-gradient);
        color: white;
        font-weight: 600;
        padding: 14px 28px;
        font-size: 1.05rem;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* 表单控件美化 */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.25);
        transition: var(--transition);
        background: rgba(255, 255, 255, 0.02);
    }
    
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* 标签页美化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.06);
        padding: 10px;
        border-radius: 14px;
        backdrop-filter: blur(15px);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        padding: 0 28px;
        border-radius: 10px;
        font-weight: 500;
        transition: var(--transition);
        font-size: 1.05rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--background-gradient) !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }
    
    /* 数据表格增强 */
    .dataframe {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--card-shadow);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(102, 126, 234, 0.08);
        transition: var(--transition);
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem !important;
        }
        
        .css-1d391kg {
            width: 100% !important;
        }
        
        .main-header {
            font-size: 2.8rem;
        }
        
        .metric-card, .portfolio-summary {
            padding: 20px;
        }
    }
    
    /* 自定义滚动条 */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--background-gradient);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4c93 100%);
    }
    
    /* 加载动画 */
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.05); }
    }
    
    .stSpinner > div {
        border-color: var(--primary-color) !important;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* 状态指示器 */
    .status-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulse 2s infinite;
    }
    
    .status-online { background-color: var(--success-color); }
    .status-warning { background-color: var(--warning-color); }
    .status-error { background-color: var(--error-color); }
    
    /* 渐变文本效果 */
    .gradient-text {
        background: var(--background-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 数据源库（分组结构）
DATA_SOURCES = {
    "龙头大件": {
        "树篱迷宫（久经沙场）": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=525873303&platform=YOUPIN&specialStyle",
        "薄荷（久经沙场）": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=489477781&platform=YOUPIN&specialStyle",
        "超导体（久经沙场）": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=553370575&platform=YOUPIN&specialStyle",
        "深红和服（久经沙场）": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=339340704&platform=YOUPIN&specialStyle",
        "潘多拉之盒（久经沙场）": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=495302338&platform=YOUPIN&specialStyle",
        "蝴蝶刀伽马多普勒": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=914710920195035136&platform=YOUPIN&specialStyle",
        "爪子刀伽马多普勒":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=5534979&platform=YOUPIN&specialStyle",
        "m9刺刀伽马多普勒":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=50942855&platform=YOUPIN&specialStyle"
    },
    "收藏品": {
        "水栽竹": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=26422&platform=YOUPIN&specialStyle",
        "赤红新星": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=24693&platform=YOUPIN&specialStyle",
        "九头金蛇": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=914680597258567680&platform=YOUPIN&specialStyle",
        "X射线":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=814309374440767488&platform=YOUPIN&specialStyle",
        "火蛇":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=26664&platform=YOUPIN&specialStyle",
        "黄金藤蔓":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=915059323698278400&platform=YOUPIN&specialStyle",
        "澜磷":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=808842805052440576&platform=YOUPIN&specialStyle",
    },
    "千战ak": {
        "血腥运动": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=553370749&platform=YOUPIN&specialStyle",
        "燃料喷射器": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=27166&platform=YOUPIN&specialStyle",
        "火神": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=24281&platform=YOUPIN&specialStyle",
        "抽象派":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=914726163117477888&platform=YOUPIN&specialStyle",
        "霓虹骑士":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=553468213&platform=YOUPIN&specialStyle",
        "二西莫夫":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=553480796&platform=YOUPIN&specialStyle",
        "皇后":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=553454872&platform=YOUPIN&specialStyle",
        "红线":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=24339&platform=YOUPIN&specialStyle",
        "传承":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=1229264305591787520&platform=YOUPIN&specialStyle",
        "深海复仇":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=24721&platform=YOUPIN&specialStyle",
        "霓虹革命":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=87809662&platform=YOUPIN&specialStyle",
    },
    "武库":{
        "怪兽在b": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=1315999843394654208&platform=YOUPIN&specialStyle",
        "m4a1渐变之色": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=1315817295203307520&platform=YOUPIN&specialStyle",
        "m4a1蒸汽波":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=1316060605966323712&platform=YOUPIN&specialStyle",
        "awp克拉考": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=1315936965627445248&platform=YOUPIN&specialStyle",
    },
    "贴纸": {
        "21tyloo": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=925497374167523328&platform=YOUPIN&specialStyle",
        "22C9": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=995815251158949888&platform=YOUPIN&specialStyle",
        "金贴lvg": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=1244761416324870144&platform=YOUPIN&specialStyle",
        "24上海金zywoo":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=1336126932723073024&platform=YOUPIN&specialStyle"
    },
    "探员": {
        "出逃的萨利": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=808803044176429056&platform=YOUPIN&specialStyle",
        "迈阿密人士": "https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=808805648347430912&platform=YOUPIN&specialStyle",
        "红苍蝇":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=914706546146541568&platform=YOUPIN&specialStyle",
        "蛙人":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=914672680855793664&platform=YOUPIN&specialStyle",
        "老K":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=808792879539683328&platform=YOUPIN&specialStyle",
        "薇帕姐":"https://sdt-api.ok-skins.com/user/steam/category/v1/kline?timestamp={};&type=2&maxTime={}&typeVal=914664236297879552&platform=YOUPIN&specialStyle",
    }

}

# 数据获取函数
def get_kline(url, start_date=None, end_date=None):
    """爬取网站K线数据（包含成交量）"""
    kline_ls = []
    max_retries = 3  # 最大重试次数
    
    # 处理时间范围
    end_ts = int(datetime.now().timestamp()) if end_date is None else int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    start_ts = 0 if start_date is None else int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    
    # 只在时间范围过大时提示
    if start_date and end_date:
        date_range_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
        if date_range_days > 365:
            st.warning(f"⚠️ 时间范围较大（{date_range_days}天），可能影响数据获取")
    
    for retry in range(max_retries):
        try:
            ts = int(datetime.now().timestamp() * 1000)
            request_url = url.format(ts, end_ts)
            
            response = requests.get(request_url, timeout=15)
            
            
            if response.status_code != 200:
                if retry < max_retries - 1:
                    time.sleep(1)  # 等待1秒后重试
                    continue
                st.error(f"❌ 数据获取失败: HTTP {response.status_code}")
                return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
            
            data = response.json()
            if 'data' not in data:
                if retry < max_retries - 1:
                    time.sleep(1)
                    continue
                st.error(f"❌ 数据格式错误")
                return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
            
            kline_data = data['data']
            if not kline_data:
                if retry < max_retries - 1:
                    time.sleep(1)
                    continue
                st.warning("⚠️ 该时间段内无数据，请尝试调整时间范围或选择其他标的")
                return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
            
            kline_ls = kline_data
            break
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if retry < max_retries - 1:
                time.sleep(2)  # 网络问题等待更长时间
                continue
            st.error("❌ 网络连接失败，请检查网络或稍后重试")
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
        except Exception as e:
            if retry < max_retries - 1:
                time.sleep(1)
                continue
            st.error(f"❌ 数据获取出错: {str(e)}")
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
    
    try:
        # 数据处理
        kline_df = pd.DataFrame(kline_ls)
        
        # 检查数据是否为空
        if kline_df.empty:
            st.warning("⚠️ 获取的数据为空，请尝试调整时间范围")
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
        
        # 检查列数
        if len(kline_df.columns) < 6:
            st.error(f"❌ 数据格式错误，期望6列，实际{len(kline_df.columns)}列")
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
        
        # 提取完整的OHLCV数据：时间戳、开盘价、最高价、最低价、收盘价、成交量
        kline_df = kline_df.iloc[:, [0, 1, 2, 3, 4, 5]]
        kline_df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        # 处理时间戳
        try:
            kline_df['date'] = kline_df['date'].apply(lambda x: datetime.fromtimestamp(int(x) / 1000 if int(x) > 1e10 else int(x)))
        except Exception as e:
            st.error(f"❌ 时间戳处理错误: {str(e)}")
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
        
        # 转换数据类型
        for col in ['open', 'high', 'low', 'close', 'volume']:
            kline_df[col] = pd.to_numeric(kline_df[col], errors='coerce')
        
        # 删除无效数据
        kline_df = kline_df.dropna(subset=['close'])
        
        if kline_df.empty:
            st.warning("⚠️ 数据处理后为空，可能数据质量有问题")
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
        
        # 应用时间范围筛选
        if start_date or end_date:
            original_count = len(kline_df)
            mask = pd.Series([True] * len(kline_df))
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                mask = mask & (kline_df['date'] >= start_datetime)
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                mask = mask & (kline_df['date'] < end_datetime)
            kline_df = kline_df[mask]
            
            if len(kline_df) == 0:
                st.warning("⚠️ 指定时间范围内无数据，请调整时间范围")
                return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')
        
        # 设置索引并排序
        kline_df = kline_df.set_index('date').sort_index()
        
        # 最终检查
        if kline_df.empty:
            st.warning("⚠️ 最终数据为空")
            return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'], index=pd.DatetimeIndex([], name='date'))
        
        return kline_df
        
    except Exception as e:
        st.error(f"❌ 数据处理出错: {str(e)}")
        return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume']).set_index('date')

# 技术指标计算函数
def calculate_technical_indicators(df):
    """计算技术指标"""
    df = df.copy()
    
    # 基础移动平均线
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma30'] = df['close'].rolling(30).mean()
    df['ma60'] = df['close'].rolling(60).mean()
    
    # 指数移动平均线
    df['ema12'] = df['close'].ewm(span=12).mean()
    df['ema26'] = df['close'].ewm(span=26).mean()
    
    # RSI相对强弱指标
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD指标
    df['macd'] = df['ema12'] - df['ema26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # 布林带
    df['bb_middle'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    
    # KDJ指标
    low_min = df['low'].rolling(9).min()
    high_max = df['high'].rolling(9).max()
    rsv = (df['close'] - low_min) / (high_max - low_min) * 100
    df['k'] = rsv.ewm(com=2).mean()
    df['d'] = df['k'].ewm(com=2).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']
    
    # OBV能量潮
    df['obv'] = (df['volume'] * ((df['close'] > df['close'].shift(1)).astype(int) * 2 - 1)).cumsum()
    
    # MFI资金流量指数
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    money_flow = typical_price * df['volume']
    positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
    negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
    mfi_ratio = positive_flow / negative_flow
    df['mfi'] = 100 - (100 / (1 + mfi_ratio))
    
    # ATR平均真实波幅
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift(1)).abs()
    low_close = (df['low'] - df['close'].shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(14).mean()
    
    # 成交量比率
    df['volume_ma'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    return df

# 技术指标计算函数
def calculate_technical_indicators_talib(df):
    """使用pandas-ta计算技术指标（高性能版本）"""
    try:
        # 使用pandas_ta而不是talib
        import pandas_ta as ta
        
        # 创建DataFrame的副本以避免警告
        result = df.copy()
        
        # 计算MACD
        result.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
        
        # 计算RSI
        result.ta.rsi(close='close', length=14, append=True)
        
        # 计算布林带
        result.ta.bbands(close='close', length=20, std=2, append=True)
        
        # 计算KDJ (随机指标)
        result.ta.stoch(high='high', low='low', close='close', k=14, d=3, append=True)
        
        # 计算移动平均线
        result.ta.sma(close='close', length=5, append=True, col_names=('SMA_5',))
        result.ta.sma(close='close', length=10, append=True, col_names=('SMA_10',))
        result.ta.sma(close='close', length=20, append=True, col_names=('SMA_20',))
        
        return result
    except Exception as e:
        print(f"pandas_ta计算失败: {str(e)}")
        # 回退到基本的技术指标计算
        return calculate_technical_indicators(df)

# 优化的交易信号分析
def analyze_trading_signals(df):
    """优化的交易信号分析 - 基于主趋势判断"""
    df = df.copy()
    df['signal'] = 0
    df['signal_type'] = ''
    df['trend_status'] = ''  # 趋势状态
    
    for i in range(60, len(df)):  # 从第60个数据点开始，确保MA60有效
        signals = []
        
        # 1. 主趋势判断（基于60日均线）
        current_price = df['close'].iloc[i]
        ma60_current = df['ma60'].iloc[i]
        ma60_prev = df['ma60'].iloc[i-5] if i >= 65 else ma60_current  # 5天前的MA60
        
        # 判断主趋势方向
        if current_price > ma60_current and ma60_current > ma60_prev:
            trend = "强势上涨"
            trend_bullish = True
        elif current_price > ma60_current and ma60_current <= ma60_prev:
            trend = "震荡上涨"
            trend_bullish = True
        elif current_price <= ma60_current and ma60_current > ma60_prev:
            trend = "高位震荡"
            trend_bullish = False
        else:
            trend = "下跌趋势"
            trend_bullish = False
        
        df.iloc[i, df.columns.get_loc('trend_status')] = trend
        
        # 2. 买入信号（只在多头趋势中给出）
        if trend_bullish:
            buy_conditions = []
            
            # 条件1：MA5上穿MA20（金叉）
            if (df['ma5'].iloc[i] > df['ma20'].iloc[i] and 
                df['ma5'].iloc[i-1] <= df['ma20'].iloc[i-1]):
                buy_conditions.append('MA5上穿MA20')
            
            # 条件2：价格回调到MA20附近后反弹
            if (current_price > df['ma20'].iloc[i] and 
                current_price < df['ma20'].iloc[i] * 1.03 and  # 价格在MA20上方3%以内
                df['close'].iloc[i-1] <= df['ma20'].iloc[i-1]):  # 前一天在MA20下方
                buy_conditions.append('回调MA20后反弹')
            
            # 条件3：RSI从超卖区域回升
            if (df['rsi'].iloc[i] > 35 and df['rsi'].iloc[i] < 60 and 
                df['rsi'].iloc[i-1] <= 35):
                buy_conditions.append('RSI超卖回升')
            
            # 条件4：MACD金叉且在零轴上方
            if (df['macd'].iloc[i] > df['macd_signal'].iloc[i] and 
                df['macd'].iloc[i-1] <= df['macd_signal'].iloc[i-1] and
                df['macd'].iloc[i] > 0):
                buy_conditions.append('MACD金叉')
            
            # 至少满足2个买入条件才给出买入信号
            if len(buy_conditions) >= 2:
                signals.append(f"买入信号: {', '.join(buy_conditions)}")
        
        # 3. 卖出信号（更严格的条件，减少踏空）
        sell_conditions = []
        
        # 条件1：明确的趋势转弱信号
        if not trend_bullish and trend in ["高位震荡", "下跌趋势"]:
            # MA5下穿MA20（死叉）
            if (df['ma5'].iloc[i] < df['ma20'].iloc[i] and 
                df['ma5'].iloc[i-1] >= df['ma20'].iloc[i-1]):
                sell_conditions.append('MA5下穿MA20')
        
        # 条件2：极度超买且出现顶部信号
        if (df['rsi'].iloc[i] > 75 and df['rsi'].iloc[i-1] > df['rsi'].iloc[i] and
            current_price < df['close'].iloc[i-1]):  # 价格开始下跌
            sell_conditions.append('极度超买回落')
        
        # 条件3：跌破重要支撑位
        if (current_price < df['ma60'].iloc[i] and 
            df['close'].iloc[i-1] >= df['ma60'].iloc[i-1]):  # 跌破60日均线
            sell_conditions.append('跌破60日均线')
        
        # 条件4：MACD死叉且转负
        if (df['macd'].iloc[i] < df['macd_signal'].iloc[i] and 
            df['macd'].iloc[i-1] >= df['macd_signal'].iloc[i-1] and
            df['macd'].iloc[i] < 0):
            sell_conditions.append('MACD死叉转负')
        
        # 至少满足2个卖出条件才给出卖出信号（减少误判）
        if len(sell_conditions) >= 2:
            signals.append(f"卖出信号: {', '.join(sell_conditions)}")
        
        # 4. 设置信号
        if signals:
            if any('买入信号' in s for s in signals):
                df.iloc[i, df.columns.get_loc('signal')] = 1
            elif any('卖出信号' in s for s in signals):
                df.iloc[i, df.columns.get_loc('signal')] = -1
            
            df.iloc[i, df.columns.get_loc('signal_type')] = '; '.join(signals)
    
    return df

# 导入认证模块
from datetime import datetime, timedelta
import sqlite3

# 创建一个简单的Auth类，作为临时解决方案
class TempAuthManager:
    def __init__(self):
        self.logged_in = False
        
    def init_session_state(self):
        """初始化会话状态"""
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = {
                'cash': 100000,
                'total_value': 100000,
                'positions': {},
                'inventory': {},
                'trade_history': [],
                'max_items_per_symbol': 1000
            }
        
    def login(self, username, password):
        # 简单的测试账号，实际应用中需要连接数据库验证
        if username == "admin" and password == "admin":
            self.logged_in = True
            st.session_state.user = {
                'id': 1,
                'username': username,
                'display_name': 'Admin User',
                'email': 'admin@example.com'
            }
            st.session_state.authenticated = True
            return True
        return False
        
    def logout(self):
        self.logged_in = False
        st.session_state.user = None
        st.session_state.authenticated = False
        st.rerun()
        
    def is_logged_in(self):
        return self.logged_in
    
    def is_authenticated(self):
        """检查用户是否已认证"""
        return st.session_state.get('authenticated', False) and st.session_state.get('user') is not None
    
    def render_user_info(self):
        """渲染用户信息栏"""
        if not self.is_authenticated():
            return
        
        user = st.session_state.user
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 用户信息")
            
            # 用户基本信息
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); 
                        padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #1976D2;">👋 {user['display_name']}</h4>
                <p style="margin: 5px 0; font-size: 0.9em; color: #666;">@{user['username']}</p>
                <p style="margin: 5px 0; font-size: 0.9em; color: #666;">📧 {user['email']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 退出按钮
            if st.button("🚪 退出登录", use_container_width=True):
                self.logout()
    
    def login_page(self):
        """登录页面"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🔐 用户登录</h1>
            <p>请登录您的账户以继续使用交易策略分析平台</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示登录表单
        with st.form("login_form"):
            st.subheader("登录账户")
            
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("🔑 登录", use_container_width=True)
            with col2:
                st.form_submit_button("🔄 重置", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("请填写完整的登录信息")
                    return
                
                if self.login(username, password):
                    st.success(f"欢迎回来，{username}！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        
        # 注册提示
        st.markdown("---")
        st.info("💡 测试账号：用户名 admin，密码 admin")

# 尝试导入真实的认证模块，如果失败则使用临时认证
try:
    from auth import AuthManager, init_auth_session, load_user_data, save_user_data
    from database import DatabaseManager
except ImportError:
    # 使用临时认证模块
    AuthManager = TempAuthManager
    
    def init_auth_session():
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'auth' not in st.session_state:
            st.session_state.auth = AuthManager()
    
    def load_user_data():
        # 简单的用户数据初始化
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = {
                'cash': 100000,
                'positions': {},
                'transactions': []
            }
    
    def save_user_data():
        # 在实际应用中，这里会保存用户数据到数据库
        pass

# 初始化会话状态
def init_session_state():
    """初始化会话状态"""
    # 初始化认证状态
    init_auth_session()
    
    # 加载用户数据
    load_user_data()
    
    # 初始化其他状态
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    
    if 'selected_symbol' not in st.session_state:
        st.session_state.selected_symbol = "水栽竹"
    
    if 'real_time_prices' not in st.session_state:
        st.session_state.real_time_prices = {}
    
    if 'last_price_update' not in st.session_state:
        st.session_state.last_price_update = None
    
# 实时价格更新函数
def initialize_all_prices():
    """初始化所有物品的价格（首次运行时）"""
    if not st.session_state.real_time_prices:
        # 静默初始化，不显示进度
        all_symbols = [(symbol, url) for items in DATA_SOURCES.values() for symbol, url in items.items()]
        for symbol, url in all_symbols:
            try:
                current_time = datetime.now()
                end_date = current_time.strftime('%Y-%m-%d')
                start_date = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
                kline_df = get_kline(url, start_date, end_date)
                if not kline_df.empty:
                    latest_price = kline_df['close'].iloc[-1]
                    st.session_state.real_time_prices[symbol] = {
                        'price': latest_price,
                        'update_time': current_time,
                        'status': 'success'
                    }
                else:
                    st.session_state.real_time_prices[symbol] = {
                        'price': 100.0,
                        'update_time': current_time,
                        'status': 'no_data'
                    }
            except Exception as e:
                st.session_state.real_time_prices[symbol] = {
                    'price': 100.0,
                    'update_time': datetime.now(),
                    'status': 'error'
                }
        st.session_state.last_price_update = datetime.now()

def update_real_time_prices():
    """更新实时价格（每分钟更新一次）"""
    current_time = datetime.now()
    if (st.session_state.last_price_update is None or 
        (current_time - st.session_state.last_price_update).seconds >= 60):
        
        # 静默更新，不显示spinner
            st.session_state.last_price_update = current_time
            updated_count = 0
            all_symbols = [(symbol, url) for items in DATA_SOURCES.values() for symbol, url in items.items()]
            
            for symbol, url in all_symbols:
                try:
                    end_date = current_time.strftime('%Y-%m-%d')
                    start_date = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
                    kline_df = get_kline(url, start_date, end_date)
                    
                    if not kline_df.empty:
                        latest_price = kline_df['close'].iloc[-1]
                        st.session_state.real_time_prices[symbol] = {
                            'price': latest_price,
                            'update_time': current_time,
                            'status': 'success'
                        }
                        updated_count += 1
                except Exception as e:
                    if symbol in st.session_state.real_time_prices:
                        st.session_state.real_time_prices[symbol]['status'] = 'error'
                        st.session_state.real_time_prices[symbol]['update_time'] = current_time
            
            # 强制重新计算总资产
            if 'portfolio' in st.session_state:
                portfolio = st.session_state.portfolio
                total_value = portfolio['cash']
                for symbol, position in portfolio['positions'].items():
                    if symbol in st.session_state.real_time_prices:
                        current_price = st.session_state.real_time_prices[symbol]['price']
                        total_value += position['quantity'] * current_price
                portfolio['total_value'] = total_value
                
            save_user_data()  # 保存更新后的数据
            return updated_count

def get_current_price(symbol):
    """获取指定标的的当前价格"""
    all_symbols = [item for items in DATA_SOURCES.values() for item in items.keys()]
    if symbol not in all_symbols:
        # 静默返回 0.0，不再 st.error
        return 0.0
    if symbol in st.session_state.real_time_prices:
        return st.session_state.real_time_prices[symbol]['price']
    else:
        st.warning(f"未获取到 {symbol} 的实时价格，使用默认价格 100.0")
        return 100.0

def calculate_total_portfolio_pnl():
    """计算总投资组合盈亏"""
    portfolio = st.session_state.portfolio
    total_cost = 0
    total_market_value = 0
    for symbol, position in portfolio['positions'].items():
        current_price = get_current_price(symbol)
        quantity = position['quantity']
        avg_price = position['avg_price']
        cost_value = quantity * avg_price
        market_value = quantity * current_price
        total_cost += cost_value
        total_market_value += market_value
    if total_cost > 0:
        total_pnl = total_market_value - total_cost
        total_pnl_percent = (total_pnl / total_cost) * 100
        return total_market_value, total_pnl, total_pnl_percent
    else:
        return 0, 0, 0

# 库存管理函数
def update_inventory_availability():
    """更新库存可用性（T+7机制）"""
    portfolio = st.session_state.portfolio
    current_time = datetime.now()
    
    for symbol in portfolio['inventory']:
        inventory = portfolio['inventory'][symbol]
        available_items = []
        locked_items = []
        
        for item in inventory['locked_items']:
            # 检查是否已过7天 - 处理字符串和datetime对象
            purchase_date = item['purchase_date']
            if isinstance(purchase_date, str):
                purchase_date = datetime.fromisoformat(purchase_date)
            
            if (current_time - purchase_date).days >= 7:
                available_items.append(item)
            else:
                locked_items.append(item)
        
        # 更新可用数量
        inventory['available_quantity'] = len(available_items)
        inventory['locked_items'] = locked_items
        
def calculate_pnl(symbol, current_price):
    """计算单个标的的盈亏情况"""
    portfolio = st.session_state.portfolio
    if symbol not in portfolio['positions']:
        return 0, 0, 0
    
    position = portfolio['positions'][symbol]
    quantity = position['quantity']
    avg_price = position['avg_price']
    
    market_value = quantity * current_price
    cost_value = quantity * avg_price
    pnl_amount = market_value - cost_value
    pnl_percent = (pnl_amount / cost_value) * 100 if cost_value > 0 else 0
    
    return market_value, pnl_amount, pnl_percent

# 模拟交易函数
def execute_trade(symbol, action, quantity, price):
    """执行模拟交易（包含库存管理和T+7限制）"""
    portfolio = st.session_state.portfolio
    current_time = datetime.now()
    db = DatabaseManager()
    user_id = st.session_state.user['id']
    
    # 更新库存可用性
    update_inventory_availability()
    
    if action == "买入":
        # 检查库存限制
        current_total = portfolio['inventory'].get(symbol, {}).get('total_quantity', 0)
        if current_total + quantity > portfolio['max_items_per_symbol']:
            st.error(f"超出库存限制！当前持有 {current_total} 个，最多可持有 {portfolio['max_items_per_symbol']} 个")
            return False, f"超出库存限制！当前持有 {current_total} 个，最多可持有 {portfolio['max_items_per_symbol']} 个"
        
        total_cost = quantity * price
        if portfolio['cash'] >= total_cost:
            portfolio['cash'] -= total_cost
            
            # 更新持仓
            if symbol in portfolio['positions']:
                old_qty = portfolio['positions'][symbol]['quantity']
                old_price = portfolio['positions'][symbol]['avg_price']
                new_qty = old_qty + quantity
                new_avg_price = (old_qty * old_price + quantity * price) / new_qty
                portfolio['positions'][symbol]['quantity'] = new_qty
                portfolio['positions'][symbol]['avg_price'] = new_avg_price
                # 将datetime对象转换为字符串
                portfolio['positions'][symbol]['purchase_dates'].extend([current_time.isoformat()] * quantity)
            else:
                portfolio['positions'][symbol] = {
                    'quantity': quantity,
                    'avg_price': price,
                    'purchase_dates': [current_time.isoformat()] * quantity
                }
            
            # 更新库存
            if symbol not in portfolio['inventory']:
                portfolio['inventory'][symbol] = {
                    'total_quantity': 0,
                    'available_quantity': 0,
                    'locked_items': []
                }
            
            # 添加到锁定库存（T+7）- 将datetime转换为字符串
            for i in range(quantity):
                portfolio['inventory'][symbol]['locked_items'].append({
                    'purchase_date': current_time.isoformat(),
                    'purchase_price': price
                })
            
            portfolio['inventory'][symbol]['total_quantity'] += quantity
            
            # 记录交易历史 - 将datetime转换为字符串
            trade_data = {
                'date': current_time.isoformat(),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'total': total_cost,
                'type': '买入'
            }
            portfolio['trade_history'].append(trade_data)
            
            # 更新总资产
            total_value = portfolio['cash']
            for sym, pos in portfolio['positions'].items():
                current_price = get_current_price(sym)
                total_value += pos['quantity'] * current_price
            portfolio['total_value'] = total_value
            
            # 保存到数据库和会话状态
            db.add_trade_record(user_id, trade_data)
            save_user_data()
            load_user_data()
            st.success(f"成功买入 {quantity} 单位 {symbol}，成交价格 ¥{price:.2f}（7天后可卖出）")
            st.rerun()
        else:
            st.error(f"资金不足，需要 ¥{total_cost:.2f}，可用资金 ¥{portfolio['cash']:.2f}")
            return False, f"资金不足，需要 ¥{total_cost:.2f}，可用资金 ¥{portfolio['cash']:.2f}"
    
    elif action == "卖出":
        # 检查库存可用性
        if symbol not in portfolio['inventory']:
            st.error(f"未持有 {symbol}")
            return False, f"未持有 {symbol}"
        
        available_qty = portfolio['inventory'][symbol]['available_quantity']
        if available_qty < quantity:
            locked_qty = len(portfolio['inventory'][symbol]['locked_items'])
            st.error(f"可卖数量不足！可卖: {available_qty} 个，锁定中: {locked_qty} 个（需等待7天）")
            return False, f"可卖数量不足！可卖: {available_qty} 个，锁定中: {locked_qty} 个（需等待7天）"
        
        total_revenue = quantity * price
        portfolio['cash'] += total_revenue
        
        # 计算盈亏（使用FIFO方式）
        sold_items = []
        total_cost = 0
        inventory = portfolio['inventory'][symbol]
        
        # 从最早可用的物品开始卖出
        available_items = []
        for item in inventory['locked_items']:
            # 将字符串转换回datetime对象进行比较
            purchase_date = datetime.fromisoformat(item['purchase_date']) if isinstance(item['purchase_date'], str) else item['purchase_date']
            if (current_time - purchase_date).days >= 7:
                available_items.append(item)
        
        available_items.sort(key=lambda x: datetime.fromisoformat(x['purchase_date']) if isinstance(x['purchase_date'], str) else x['purchase_date'])
        
        for i in range(quantity):
            if i < len(available_items):
                item = available_items[i]
                sold_items.append(item)
                total_cost += item['purchase_price']
        
        # 更新库存
        for item in sold_items:
            inventory['locked_items'].remove(item)
        
        inventory['total_quantity'] -= quantity
        inventory['available_quantity'] -= quantity
        
        # 更新持仓
        portfolio['positions'][symbol]['quantity'] -= quantity
        if portfolio['positions'][symbol]['quantity'] == 0:
            del portfolio['positions'][symbol]
        
        # 计算盈亏
        pnl_amount = total_revenue - total_cost
        pnl_percent = (pnl_amount / total_cost) * 100 if total_cost > 0 else 0
        
        # 记录交易历史 - 将datetime转换为字符串
        trade_data = {
            'date': current_time.isoformat(),
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': price,
            'total': total_revenue,
            'cost': total_cost,
            'pnl_amount': pnl_amount,
            'pnl_percent': pnl_percent,
            'type': '卖出'
        }
        portfolio['trade_history'].append(trade_data)
        
        # 更新总资产
        total_value = portfolio['cash']
        for sym, pos in portfolio['positions'].items():
            current_price = get_current_price(sym)
            total_value += pos['quantity'] * current_price
        portfolio['total_value'] = total_value
        
        # 保存到数据库和会话状态
        db.add_trade_record(user_id, trade_data)
        save_user_data()
        load_user_data()
        st.success(f"成功卖出 {quantity} 单位 {symbol}，成交价格 ¥{price:.2f}")
        st.rerun()
    else:
        st.error("未知错误")
        return False, "未知错误"

def calculate_portfolio_value(current_prices):
    """计算投资组合总价值"""
    portfolio = st.session_state.portfolio
    total_value = portfolio['cash']
    
    for symbol, position in portfolio['positions'].items():
        if symbol in current_prices:
            total_value += position['quantity'] * current_prices[symbol]
    
    portfolio['total_value'] = total_value
    return total_value

# 策略回测相关函数
def t7_adjust(flag):
    """t+7模式调整"""
    flag = flag.copy()
    for i in range(1, len(flag)):
        if flag.iloc[i] > flag.iloc[i - 1]:
            start = i
        elif flag.iloc[i] < flag.iloc[i - 1] and i - start < 7:
            flag.iloc[i] = 1
    return flag

def backtest_strategy(kline_df, k0=6.7, bias_th=0.07, sell_days=3, sell_drop_th=-0.05):
    """回测函数，增加仓位记录和买卖信号"""
    # 计算指标
    ret = kline_df['close'].pct_change()
    ma5 = kline_df['close'].rolling(5).mean()
    ma10 = kline_df['close'].rolling(10).mean()
    ma20 = kline_df['close'].rolling(20).mean()
    ma30 = kline_df['close'].rolling(30).mean()
    
    # 执行回测
    pos = {}
    ret_ls = []
    
    for i in range(19, len(kline_df)):
        close = kline_df['close'].iloc[i]
        bias = close / ma5.iloc[i] - 1
        
        # 计算价格跌幅
        price_drop = 0
        ma10_break = False
        if i >= sell_days:
            drop_cal = kline_df['close'].iloc[i-sell_days]
            price_drop = close / drop_cal - 1
            ma10_break = close < ma10.iloc[i]
        
        current_pos = sum(list(pos.values()))
        buy = 0
        sell = 0
        sold_pos = 0
        
        # 买入逻辑
        if ma5.iloc[i] > ma20.iloc[i] and close > ma10.iloc[i] and bias < bias_th:
            if not pos:
                pos[i] = 0.3
                buy = 0.3
            elif current_pos < 1:
                pos[i] = 0.1
                buy = 0.1
        # 卖出逻辑
        else:
            # 清仓条件：3日跌幅超5%且跌破MA10
            if i >= sell_days and price_drop < sell_drop_th and ma10_break:
                sell_pos = current_pos  # 全额卖出
                for k in list(pos.keys()):  # 清空所有持仓
                    sold_pos += pos[k]
                    del pos[k]
            else:
                # 保持原有止盈逻辑
                sell_pos = current_pos * (1 - np.exp(-k0 * bias_th)) if bias >= bias_th else 0
                for k in list(pos.keys()):
                    if i - k >= 7:
                        sold_pos += pos[k]
                        del pos[k]
                        if sold_pos >= sell_pos:
                            break
            
            sell = sold_pos
        
        # 记录当日结果
        ret_ls.append({
            'date': kline_df.index[i],
            'pos': current_pos + buy - sell,
            'ret': (current_pos + buy - sell) * ret.iloc[i],
            'buy': buy,
            'sell': sell,
            'price': close,
            'ma5': ma5.iloc[i],
            'ma10': ma10.iloc[i],
            'ma20': ma20.iloc[i],
            'bias': bias
        })
    
    return pd.DataFrame(ret_ls).set_index('date')

def get_risk_metrics(df, num=365):
    """计算策略收益情况"""
    if df.empty or 'ret' not in df.columns:
        return {}
    
    value_df = (1 + df['ret']).cumprod()
    annual_ret = value_df.iloc[-1] ** (num / len(df)) - 1
    vol = df['ret'].std() * np.sqrt(num)
    sharpe = annual_ret / vol if vol != 0 else 0
    max_dd = (1 - value_df / value_df.cummax()).max()
    calmar = annual_ret / max_dd if max_dd != 0 else 0
    
    return {
        '总收益率': (value_df.iloc[-1] - 1),
        '年化收益': annual_ret,
        '波动率': vol,
        'Sharpe': sharpe,
        '最大回撤': max_dd,
        'Calmar': calmar
    }

def analyze_ma_positions(kline_df):
    """分析MA趋势及交叉，提供仓位建议"""
    # 计算移动平均线
    ma5 = kline_df['close'].rolling(5).mean()
    ma10 = kline_df['close'].rolling(10).mean()
    ma20 = kline_df['close'].rolling(20).mean()
    ma30 = kline_df['close'].rolling(30).mean()

    # 初始化信号列
    kline_df = kline_df.copy()
    kline_df['position_signal'] = 0  # 默认无信号
    kline_df['signal_type'] = ''  # 信号类型描述
    
    # 添加MA列到DataFrame
    kline_df['ma5'] = ma5
    kline_df['ma10'] = ma10
    kline_df['ma20'] = ma20
    kline_df['ma30'] = ma30

    # 判断MA30趋势和交叉信号
    for i in range(1, len(kline_df)):
        # 判断MA30趋势
        ma30_trend_up = kline_df['ma30'].iloc[i] > kline_df['ma30'].iloc[i - 1]
        
        if ma30_trend_up:
            # 判断MA5与MA10的交叉
            ma5_cross_ma10 = (ma5.iloc[i] > ma10.iloc[i]) and (ma5.iloc[i - 1] <= ma10.iloc[i - 1])
            
            # 判断MA5与MA20的交叉
            ma5_cross_ma20 = (ma5.iloc[i] > ma20.iloc[i]) and (ma5.iloc[i - 1] <= ma20.iloc[i - 1])
            
            # 设置信号
            if ma5_cross_ma20:
                kline_df.iloc[i, kline_df.columns.get_loc('position_signal')] = 4  # 买入4仓
                kline_df.iloc[i, kline_df.columns.get_loc('signal_type')] = 'MA5上穿MA20，建议买入4仓'
            elif ma5_cross_ma10:
                kline_df.iloc[i, kline_df.columns.get_loc('position_signal')] = 2  # 买入2仓
                kline_df.iloc[i, kline_df.columns.get_loc('signal_type')] = 'MA5上穿MA10，建议买入2仓'
                
    return kline_df

# 主应用
def main():
    """主函数 - 应用入口点"""
    # 初始化会话状态
    init_session_state()
    
    # 初始化管理员用户
    init_admin_users()
    
    # 添加现代化的应用标题和状态栏
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 class="main-header">🎯 CS:GO饰品交易策略分析平台</h1>
        <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; margin-top: 1rem; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div class="status-indicator status-online"></div>
                <span style="color: #4CAF50; font-weight: 500;">系统在线</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div class="status-indicator status-online"></div>
                <span style="color: #4CAF50; font-weight: 500;">数据实时</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div class="status-indicator status-online"></div>
                <span style="color: #4CAF50; font-weight: 500;">AI分析</span>
            </div>
        </div>
        <p style="color: #666; margin-top: 1rem; font-size: 1.1rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            专业的CS:GO饰品市场分析工具，提供智能交易策略和实时数据分析
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化认证系统
    auth = AuthManager()
    auth.init_session_state()
    
    # 检查用户是否已登录
    if hasattr(auth, 'is_authenticated') and auth.is_authenticated():
        # 使用AuthManager的用户信息显示
        auth.render_user_info()
        
        # 添加侧边栏快捷信息面板
        st.sidebar.markdown("""
        <div class="metric-card" style="margin: 1rem 0; padding: 1rem;">
            <h4 style="margin: 0 0 0.5rem 0; color: white;">📊 快捷信息</h4>
            <div style="font-size: 0.9rem; line-height: 1.4;">
                <p style="margin: 0.3rem 0;">💰 总资产: ¥{:,.0f}</p>
                <p style="margin: 0.3rem 0;">📈 今日收益: <span style="color: #4CAF50;">+2.3%</span></p>
                <p style="margin: 0.3rem 0;">🎯 持仓品种: {} 个</p>
            </div>
        </div>
        """.format(
            st.session_state.portfolio.get('cash', 100000) + sum([pos.get('quantity', 0) * get_current_price(symbol) for symbol, pos in st.session_state.portfolio.get('positions', {}).items()]),
            len(st.session_state.portfolio.get('positions', {}))
        ), unsafe_allow_html=True)
        
        # 导航菜单
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📋 功能导航")
        
        # 添加实时数据更新
        update_real_time_prices()
        
        # 增强的导航菜单
        page_options = {
            "📊 K线行情分析": "深度技术分析和智能策略优化",
            "💰 模拟交易": "实时交易模拟和投资组合管理", 
            "🎯 交易策略": "专业策略回测和风险评估",
            "📈 在售量分析": "实时在售量数据和供需分析",
            "👤 个人中心": "账户管理和个人设置"
        }
        
        page = st.sidebar.radio(
            "选择功能:",
            list(page_options.keys()),
            help="选择您要使用的功能模块"
        )
        
        # 显示选中功能的描述
        st.sidebar.markdown(f"""
        <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem; border-radius: 8px; margin-top: 0.5rem;">
            <small style="color: #667eea; font-weight: 500;">{page_options[page]}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # 添加快捷操作按钮
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚡ 快捷操作")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🔄 刷新数据", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("📊 市场概览", use_container_width=True):
                st.info("市场概览功能开发中...")
        
        # 添加帮助信息
        st.sidebar.markdown("---")
        with st.sidebar.expander("❓ 使用帮助"):
            st.markdown("""
            **功能说明:**
            - 📊 **K线分析**: 查看价格走势和技术指标
            - 💰 **模拟交易**: 进行虚拟交易练习
            - 🎯 **交易策略**: 测试和优化交易策略
            - 📈 **在售量分析**: 实时在售量数据和供需分析
            - 👤 **个人中心**: 管理账户和查看统计
            
            **快捷键:**
            - `Ctrl + R`: 刷新页面
            - `Ctrl + S`: 保存设置
            """)
        
        if page == "📊 K线行情分析":
            kline_analysis_page()
        elif page == "💰 模拟交易":
            simulation_trading_page()
        elif page == "🎯 交易策略":
            trading_strategy_page()
        elif page == "📈 在售量分析":
            try:
                from on_sale_page import on_sale_analysis_page as on_sale_page_func
                on_sale_page_func()
            except ImportError:
                st.error("❌ 在售量分析模块未找到，请确保 on_sale_page.py 文件存在")
            except Exception as e:
                st.error(f"❌ 在售量分析功能出现错误: {str(e)}")
        elif page == "👤 个人中心":
            user_data_page(auth)
    else:
        # 显示登录页面
        auth.login_page()

def kline_analysis_page():
    """K线分析页面 - 基于回测系统优化的策略分析"""
    # 确保session state已初始化
    if 'current_data' not in st.session_state:
        init_session_state()
    
    st.markdown('<h2 class="sub-header">📊 智能K线策略分析</h2>', unsafe_allow_html=True)
    
    # 页面说明
    st.markdown("""
    <div class="metric-card">
        <h4>🎯 智能策略分析说明</h4>
        <p>• <strong>策略优化：</strong>首先通过回测系统自动寻找最佳交易策略参数</p>
        <p>• <strong>智能分析：</strong>将优化后的策略应用于K线分析，提供精准交易信号</p>
        <p>• <strong>实时指导：</strong>基于历史最佳表现的策略，给出当前交易建议</p>
        <p>• <strong>风险控制：</strong>结合T+7机制和止损策略，确保交易安全</p>
            </div>
    """, unsafe_allow_html=True)
    
    # 分析设置
    st.markdown('<h3 class="sub-header">⚙️ 策略优化设置</h3>', unsafe_allow_html=True)
    
    # 创建设置面板
    with st.container():
        # 第一行：数据源和时间设置
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            category = st.selectbox("📂 饰品分类", list(DATA_SOURCES.keys()), key="kline_category")
        
        with col2:
            if category is not None:
                symbol_list = list(DATA_SOURCES[category].keys())
                if not symbol_list:
                    st.warning("该分类下暂无物品")
                    return
                selected_symbol = st.selectbox(
                    "🎯 分析标的",
                    options=symbol_list,
                    index=0,
                    key="kline_symbol"
                )
                if selected_symbol:
                    st.session_state.selected_symbol = selected_symbol
        
        with col3:
            # 策略优化时间范围（用于寻找最佳参数）
            optimization_days = st.selectbox(
                "🔧 优化周期",
                options=[30, 60, 90, 180],
                index=2,
                help="用于策略参数优化的历史数据天数"
            ) or 90  # 确保不为None，默认90天
            
            optimization_start = datetime.now() - timedelta(days=optimization_days)
            optimization_end = datetime.now() - timedelta(days=7)  # 留出一周用于验证
        
        with col4:
            # 分析时间范围（用于应用策略）
            analysis_days = st.selectbox(
                "📈 分析周期",
                options=[7, 14, 30, 60],
                index=2,
                help="应用优化策略进行分析的天数"
            ) or 30  # 确保不为None，默认30天
            
            analysis_start = datetime.now() - timedelta(days=analysis_days)
            analysis_end = datetime.now()
    
    # 策略优化参数范围
    st.markdown("### 🔧 策略参数优化范围")
    
    with st.expander("📋 参数优化设置", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            k0_range = st.slider("K因子范围", min_value=1.0, max_value=20.0, value=(3.0, 10.0), step=0.5)
            bias_th_range = st.slider("偏离阈值范围", min_value=0.01, max_value=0.20, value=(0.03, 0.12), step=0.01)
        
        with col2:
            sell_days_range = st.slider("观察天数范围", min_value=1, max_value=10, value=(2, 5), step=1)
            sell_drop_range = st.slider("止损阈值范围", min_value=-0.20, max_value=-0.01, value=(-0.10, -0.03), step=0.01)
    
    # 开始智能分析按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 开始智能策略分析", use_container_width=True, help="先优化策略参数，再进行K线分析"):
            
            if not category or not selected_symbol:
                st.error("请选择分析标的")
                return
            
            try:
                data_url = DATA_SOURCES[category][selected_symbol]
                
                # 第一步：策略参数优化
                st.markdown("### 🔍 第一步：策略参数优化")
                
                with st.spinner("正在获取历史数据进行策略优化..."):
                    # 获取优化用的历史数据
                    optimization_start_str = optimization_start.strftime('%Y-%m-%d')
                    optimization_end_str = optimization_end.strftime('%Y-%m-%d')
                    
                    optimization_df = get_kline(data_url, optimization_start_str, optimization_end_str)
                    
                    if optimization_df.empty:
                        st.error("❌ 无法获取优化数据，请检查网络连接")
                        return
                
                # 参数优化过程
                with st.spinner("正在寻找最佳策略参数..."):
                    best_params = None
                    best_sharpe = -999
                    optimization_results = []
                    
                    # 创建参数组合
                    k0_values = np.arange(k0_range[0], k0_range[1] + 0.5, 0.5)
                    bias_th_values = np.arange(bias_th_range[0], bias_th_range[1] + 0.01, 0.01)
                    sell_days_values = range(int(sell_days_range[0]), int(sell_days_range[1]) + 1)
                    sell_drop_values = np.arange(sell_drop_range[0], sell_drop_range[1] + 0.01, 0.01)
                    
                    # 限制组合数量以避免过长时间
                    max_combinations = 100
                    total_combinations = len(k0_values) * len(bias_th_values) * len(sell_days_values) * len(sell_drop_values)
                    
                    if total_combinations > max_combinations:
                        # 采样减少组合数
                        k0_values = k0_values[::max(1, len(k0_values) // 5)]
                        bias_th_values = bias_th_values[::max(1, len(bias_th_values) // 5)]
                        sell_days_values = list(sell_days_values)[::max(1, len(sell_days_values) // 3)]
                        sell_drop_values = sell_drop_values[::max(1, len(sell_drop_values) // 4)]
                    
                    # 进度条
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    combination_count = 0
                    total_count = len(k0_values) * len(bias_th_values) * len(sell_days_values) * len(sell_drop_values)
                    
                    # 遍历参数组合
                    for k0 in k0_values:
                        for bias_th in bias_th_values:
                            for sell_days in sell_days_values:
                                for sell_drop_th in sell_drop_values:
                                    try:
                                        # 执行回测
                                        backtest_result = backtest_strategy(optimization_df, k0, bias_th, sell_days, sell_drop_th)
                                        
                                        if not backtest_result.empty and len(backtest_result) > 10:
                                            # 计算绩效指标
                                            risk_metrics = get_risk_metrics(backtest_result)
                                            sharpe = risk_metrics.get('Sharpe', -999)
                                            
                                            # 记录结果
                                            optimization_results.append({
                                                'k0': k0,
                                                'bias_th': bias_th,
                                                'sell_days': sell_days,
                                                'sell_drop_th': sell_drop_th,
                                                'sharpe': sharpe,
                                                'total_return': risk_metrics.get('总收益率', 0),
                                                'annual_return': risk_metrics.get('年化收益', 0),
                                                'max_drawdown': risk_metrics.get('最大回撤', 0)
                                            })
                                            
                                            # 更新最佳参数
                                            if sharpe > best_sharpe:
                                                best_sharpe = sharpe
                                                best_params = {
                                                    'k0': k0,
                                                    'bias_th': bias_th,
                                                    'sell_days': sell_days,
                                                    'sell_drop_th': sell_drop_th,
                                                    'metrics': risk_metrics
                                                }
                                    
                                    except Exception as e:

                                    
                                        pass  # 忽略单个参数组合的错误

                                    
                                    

                                    
                                    # 更新进度
                                    combination_count += 1
                                    progress = combination_count / total_count
                                    progress_bar.progress(progress)
                                    status_text.text(f"优化进度: {combination_count}/{total_count} ({progress*100:.1f}%)")
                
                # 清除进度显示
                progress_bar.empty()
                status_text.empty()
                
                if best_params is None:
                    st.error("❌ 策略优化失败，请调整参数范围或时间周期")
                    return
                    
                # 显示最佳参数
                st.success("✅ 策略参数优化完成！")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("最佳K因子", f"{best_params['k0']:.1f}")
                with col2:
                    st.metric("最佳偏离阈值", f"{best_params['bias_th']:.3f}")
                with col3:
                    st.metric("最佳观察天数", f"{best_params['sell_days']}")
                with col4:
                    st.metric("最佳止损阈值", f"{best_params['sell_drop_th']:.3f}")
                
                # 显示优化后的策略表现
                metrics = best_params['metrics']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("夏普比率", f"{metrics.get('Sharpe', 0):.3f}")
                with col2:
                    st.metric("年化收益", f"{metrics.get('年化收益', 0)*100:.2f}%")
                with col3:
                    st.metric("总收益率", f"{metrics.get('总收益率', 0)*100:.2f}%")
                with col4:
                    st.metric("最大回撤", f"{metrics.get('最大回撤', 0)*100:.2f}%")
                
                # 第二步：应用最佳策略进行K线分析
                st.markdown("### 📈 第二步：基于最佳策略的K线分析")
                
                with st.spinner("正在获取最新数据并应用最佳策略..."):
                    # 获取分析用的最新数据
                    analysis_start_str = analysis_start.strftime('%Y-%m-%d')
                    analysis_end_str = analysis_end.strftime('%Y-%m-%d')
                    
                    analysis_df = get_kline(data_url, analysis_start_str, analysis_end_str)
                    
                    if analysis_df.empty:
                        st.error("❌ 无法获取分析数据")
                        return
                
                    # 计算技术指标
                    analysis_df = calculate_technical_indicators_talib(analysis_df)
                    
                    # 应用最佳策略进行回测
                    strategy_result = backtest_strategy(
                        analysis_df, 
                        best_params['k0'], 
                        best_params['bias_th'], 
                        best_params['sell_days'], 
                        best_params['sell_drop_th']
                    )
                    
                    # 分析当前交易信号
                    current_signals = analyze_trading_signals(analysis_df)
                    
                    st.session_state.current_data = analysis_df
                    st.session_state.strategy_result = strategy_result
                    st.session_state.best_params = best_params
                
                # 显示策略应用结果
                st.success("✅ 策略应用完成！")
                
                # 显示K线图表和策略信号
                display_kline_chart_with_signals(analysis_df, strategy_result, selected_symbol)
                
                # 执行专业市场分析
                st.markdown("### 🔬 专业市场分析")
                
                with st.spinner("正在进行深度市场分析..."):
                    # 市场情绪和资金流向分析
                    market_analysis = analyze_market_sentiment(analysis_df)
                    
                    # 生成交易建议
                    trading_recommendations = generate_trading_recommendations(analysis_df, market_analysis)
                
                if market_analysis:
                    # 创建分析结果展示
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 市场情绪分析
                        sentiment = market_analysis.get('sentiment', {})
                        sentiment_score = sentiment.get('score', 0)
                        sentiment_level = sentiment.get('level', '未知')
                        
                        # 情绪评分颜色
                        if sentiment_score > 30:
                            sentiment_color = "#4CAF50"
                            sentiment_icon = "😊"
                        elif sentiment_score > -30:
                            sentiment_color = "#FF9800"
                            sentiment_icon = "😐"
                        else:
                            sentiment_color = "#F44336"
                            sentiment_icon = "😰"
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>🎭 市场情绪分析</h4>
                            <div style="text-align: center; margin: 1rem 0;">
                                <div style="font-size: 3rem;">{sentiment_icon}</div>
                                <h3 style="color: {sentiment_color}; margin: 0.5rem 0;">{sentiment_level}</h3>
                                <p style="font-size: 1.2rem; color: {sentiment_color}; font-weight: 600;">
                                    情绪评分: {sentiment_score}/100
                                </p>
            </div>
                            <p><strong>趋势强度:</strong> {sentiment.get('trend_strength', '未知')}</p>
                            <p><strong>波动率状态:</strong> {sentiment.get('volatility_status', '未知')}</p>
            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # 技术指标综合分析
                        technical = market_analysis.get('technical', {})
                        overall_signal = technical.get('overall_signal', '未知')
                        bullish_count = technical.get('bullish_count', 0)
                        bearish_count = technical.get('bearish_count', 0)
                        
                        # 信号强度颜色
                        if bullish_count > bearish_count + 1:
                            signal_color = "#4CAF50"
                            signal_icon = "🐂"
                        elif bearish_count > bullish_count + 1:
                            signal_color = "#F44336"
                            signal_icon = "🐻"
                        else:
                            signal_color = "#FF9800"
                            signal_icon = "⚖️"
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📊 技术指标综合</h4>
                            <div style="text-align: center; margin: 1rem 0;">
                                <div style="font-size: 3rem;">{signal_icon}</div>
                                <h3 style="color: {signal_color}; margin: 0.5rem 0;">{overall_signal}</h3>
                                <p style="font-size: 1rem;">
                                    看多信号: <span style="color: #4CAF50; font-weight: 600;">{bullish_count}</span> | 
                                    看空信号: <span style="color: #F44336; font-weight: 600;">{bearish_count}</span>
                                </p>
                            </div>
                            <p><strong>RSI:</strong> {technical.get('rsi_signal', '未知')}</p>
                            <p><strong>MACD:</strong> {technical.get('macd_signal', '未知')}</p>
                            <p><strong>KDJ:</strong> {technical.get('kdj_signal', '未知')}</p>
                            <p><strong>布林带:</strong> {technical.get('bb_signal', '未知')}</p>
    </div>
    """, unsafe_allow_html=True)
    
                    # 资金流向分析
                    display_trading_recommendations(trading_recommendations)
                    
            except Exception as e:
                st.error(f"❌ 分析过程中出现错误: {str(e)}")
                st.error("请检查网络连接或调整分析参数")
    
    # 如果已有分析结果，显示历史数据
    if 'current_data' in st.session_state and st.session_state.current_data is not None and not st.session_state.current_data.empty:
        st.markdown("### 📈 历史分析数据")
        
        # 显示数据表格
        with st.expander("📊 查看详细数据", expanded=False):
            if 'strategy_result' in st.session_state:
                display_df = st.session_state.strategy_result[['price', 'pos', 'buy', 'sell', 'ret']].round(4)
                st.dataframe(display_df, use_container_width=True)
            else:
                display_df = st.session_state.current_data[['open', 'high', 'low', 'close', 'volume']].round(2)
                st.dataframe(display_df, use_container_width=True)
    
    # 添加此代码在适当位置
    with st.expander("🔮 高级市场情绪分析", expanded=False):
        st.write("进行多维度市场情绪分析，提供更全面的市场洞察")
        use_enhanced_analysis = st.checkbox("启用高级分析引擎", value=True)
        
        if use_enhanced_analysis and 'current_data' in st.session_state and st.session_state.current_data is not None:
            analysis_df = st.session_state.current_data
            
            # 确保数据已经计算了所有需要的技术指标
            if TALIB_AVAILABLE:
                analysis_df = calculate_technical_indicators_talib(analysis_df)
            else:
                analysis_df = calculate_technical_indicators(analysis_df)
                
            # 进行高级市场情绪分析
            market_analysis = analyze_market_sentiment(analysis_df)
            advanced_analysis = analyze_advanced_market_sentiment(analysis_df)
            
            # 合并基础分析和高级分析
            if advanced_analysis:
                market_analysis['advanced'] = advanced_analysis
            
            # 生成增强交易建议
            enhanced_recommendations = generate_enhanced_trading_recommendations(analysis_df, market_analysis)
            
            # 存储以便在其他地方使用
            st.session_state.enhanced_recommendations = enhanced_recommendations
            
            # 显示高级分析结果
            if 'trend' in advanced_analysis:
                st.subheader("🔄 趋势分析")
                trend_info = advanced_analysis['trend']
                
                cols = st.columns(2)
                with cols[0]:
                    if 'strength' in trend_info:
                        st.metric("趋势强度", trend_info['strength'], 
                                 delta=f"{trend_info.get('strength_score', 0):.1f}分")
                
                with cols[1]:
                    if 'inflection' in trend_info:
                        st.info(f"趋势拐点: {trend_info['inflection']}")
            
            if 'support_resistance' in advanced_analysis:
                st.subheader("📊 支撑阻力位分析")
                sr_info = advanced_analysis['support_resistance']
                
                if 'price_position' in sr_info:
                    st.info(f"价格位置: {sr_info['price_position']}")
                
                cols = st.columns(5)
                if all(k in sr_info for k in ['s2', 's1', 'pivot', 'r1', 'r2']):
                    with cols[0]:
                        st.metric("二级阻力", f"{sr_info['r2']:.2f}")
                    with cols[1]:
                        st.metric("一级阻力", f"{sr_info['r1']:.2f}")
                    with cols[2]:
                        st.metric("轴心", f"{sr_info['pivot']:.2f}")
                    with cols[3]:
                        st.metric("一级支撑", f"{sr_info['s1']:.2f}")
                    with cols[4]:
                        st.metric("二级支撑", f"{sr_info['s2']:.2f}")
            
            if 'multi_period' in advanced_analysis:
                st.subheader("🕒 多周期情绪分析")
                mp_info = advanced_analysis['multi_period']
                
                sentiment_color = "#1976D2"
                if "乐观" in mp_info['sentiment']:
                    sentiment_color = "#4CAF50"
                elif "悲观" in mp_info['sentiment']:
                    sentiment_color = "#F44336"
                
                st.markdown(f"<h4 style='color:{sentiment_color};'>综合情绪: {mp_info['sentiment']}</h4>", 
                           unsafe_allow_html=True)
                
                cols = st.columns(3)
                with cols[0]:
                    st.metric("短期情绪 (10天)", f"{mp_info['short_term_score']:.1f}")
                with cols[1]:
                    st.metric("中期情绪 (30天)", f"{mp_info['medium_term_score']:.1f}")
                with cols[2]:
                    st.metric("长期情绪 (60天)", f"{mp_info['long_term_score']:.1f}")
                
                # 显示情绪得分条形图
                score = mp_info['combined_score']
                fig = go.Figure()
                fig.add_trace(go.Indicator(
                    mode = "gauge+number",
                    value = score,
                    title = {'text': "市场情绪评分"},
                    gauge = {
                        'axis': {'range': [-100, 100]},
                        'bar': {'color': sentiment_color},
                        'steps': [
                            {'range': [-100, -50], 'color': "#F44336"},  # 红色
                            {'range': [-50, 0], 'color': "#FF9800"},    # 橙色
                            {'range': [0, 50], 'color': "#4CAF50"},     # 绿色
                            {'range': [50, 100], 'color': "#2E7D32"}    # 深绿色
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 2},
                            'thickness': 0.75,
                            'value': score
                        }
                    }
                ))
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
            
            if 'anomaly' in advanced_analysis:
                st.subheader("⚠️ 市场异常检测")
                anomaly_info = advanced_analysis['anomaly']
                
                severity = anomaly_info.get('severity', '低')
                severity_color = "#4CAF50" if severity == "低" else "#F44336" if severity in ["高", "极高"] else "#FF9800"
                
                st.markdown(f"<h4 style='color:{severity_color};'>异常程度: {severity}</h4>", 
                           unsafe_allow_html=True)
                
                if 'price' in anomaly_info:
                    st.info(anomaly_info['price'])
                if 'volume' in anomaly_info:
                    st.info(anomaly_info['volume'])
            
            # 显示交易建议
            st.subheader("💡 智能交易建议")
            display_trading_recommendations(enhanced_recommendations)

def simulation_trading_page():
    """模拟交易页面"""
    load_user_data()  # 保证每次模拟交易页面都同步用户数据
    st.markdown('<h2 class="sub-header">💰 模拟交易系统</h2>', unsafe_allow_html=True)
    
    # 添加页面说明
    st.markdown("""
    <div class="metric-card">
        <h4>🎯 交易系统说明</h4>
        <p>• 实时价格每分钟自动更新，确保交易数据准确性</p>
        <p>• T+7交易机制：买入后需等待7天才能卖出</p>
        <p>• 智能库存管理：自动跟踪可用和锁定数量</p>
        <p>• 专业盈亏计算：实时显示持仓收益情况</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化所有价格（首次运行）
    initialize_all_prices()
    
    # 更新实时价格（静默运行）
    updated_count = update_real_time_prices()
    
    # 添加实时市场状态面板
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); 
                padding: 20px; border-radius: 16px; margin: 20px 0; border: 1px solid rgba(102, 126, 234, 0.2);">
        <h4 style="margin: 0 0 15px 0; color: #667eea;">📊 实时市场状态</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
            <div style="text-align: center;">
                <div style="font-size: 1.2rem; font-weight: 600; color: #4CAF50;">🟢 在线</div>
                <div style="font-size: 0.9rem; color: #666;">系统状态</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.2rem; font-weight: 600; color: #2196F3;">{} 个</div>
                <div style="font-size: 0.9rem; color: #666;">监控品种</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.2rem; font-weight: 600; color: #FF9800;">每分钟</div>
                <div style="font-size: 0.9rem; color: #666;">更新频率</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.2rem; font-weight: 600; color: #9C27B0;">T+7</div>
                <div style="font-size: 0.9rem; color: #666;">交易机制</div>
            </div>
        </div>
    </div>
    """.format(sum(len(items) for items in DATA_SOURCES.values())), unsafe_allow_html=True)
    
    # 投资组合概览
    portfolio = st.session_state.portfolio
    
    # 使用实时价格计算总价值
    current_prices = {}
    for category_items in DATA_SOURCES.values():
        for symbol in category_items.keys():
            current_prices[symbol] = get_current_price(symbol)
    
    total_value = calculate_portfolio_value(current_prices)
    total_pnl = total_value - 100000  # 初始资金10万
    pnl_pct = (total_pnl / 100000) * 100
    
    # 计算总库存盈亏
    total_market_value, total_position_pnl, total_position_pnl_pct = calculate_total_portfolio_pnl()
    
    # 投资组合摘要（优化样式）
    pnl_color = "#4CAF50" if total_pnl >= 0 else "#F44336"
    pnl_icon = "📈" if total_pnl >= 0 else "📉"
    
    st.markdown(f"""
    <div class="portfolio-summary">
        <h3>💼 投资组合概览</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
            <div style="text-align: center;">
                <h4 style="margin: 0; color: #0D47A1;">总资产</h4>
                <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #1976D2;">¥{total_value:,.2f}</p>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">当前总价值</p>
            </div>
            <div style="text-align: center;">
                <h4 style="margin: 0; color: #0D47A1;">可用资金</h4>
                <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #1976D2;">¥{portfolio['cash']:,.2f}</p>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">可用于交易</p>
            </div>
            <div style="text-align: center;">
                <h4 style="margin: 0; color: #0D47A1;">持仓市值</h4>
                <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #1976D2;">¥{total_market_value:,.2f}</p>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">当前持仓价值</p>
            </div>
            <div style="text-align: center;">
                <h4 style="margin: 0; color: #0D47A1;">总盈亏 {pnl_icon}</h4>
                <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: {pnl_color};">¥{total_pnl:,.2f}</p>
                <p style="margin: 0; color: {pnl_color}; font-size: 0.9rem; font-weight: 600;">{pnl_pct:+.2f}%</p>
            </div>
            <div style="text-align: center;">
                <h4 style="margin: 0; color: #0D47A1;">持仓品种</h4>
                <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #1976D2;">{len(portfolio['positions'])}</p>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">个不同标的</p>
            </div>
            <div style="text-align: center;">
                <h4 style="margin: 0; color: #0D47A1;">库存盈亏</h4>
                <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: {'#4CAF50' if total_position_pnl >= 0 else '#F44336'};">¥{total_position_pnl:,.2f}</p>
                <p style="margin: 0; color: {'#4CAF50' if total_position_pnl >= 0 else '#F44336'}; font-size: 0.9rem; font-weight: 600;">{total_position_pnl_pct:+.2f}%</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建交易标签页
    trade_tab1, trade_tab2, trade_tab3, trade_tab4 = st.tabs(["💹 交易面板", "📦 我的库存", "📊 持仓管理", "📜 交易历史"])
    
    with trade_tab1:
        st.markdown("### 💹 模拟交易面板")
        
        # 交易面板
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 选择交易标的
            st.markdown("#### 📂 选择交易标的")
            trade_category = st.selectbox("选择饰品分类", list(DATA_SOURCES.keys()), key="trade_category")
            if trade_category:
                trade_symbol_list = list(DATA_SOURCES[trade_category].keys())
                trade_symbol = st.selectbox("选择交易标的", trade_symbol_list, key="trade_symbol")
                
                # 显示当前价格
                if trade_symbol:
                    current_price = get_current_price(trade_symbol)
                    st.markdown(f"""
                    <div class="price-display">
                        {trade_symbol} 当前价格: ¥{current_price:.2f}
                    </div>
                    """, unsafe_allow_html=True)
            
            # 交易操作
            st.markdown("#### 💰 交易操作")
            action = st.radio("选择操作", ["买入", "卖出"], horizontal=True, key="trade_action")
            
            col_qty, col_price = st.columns(2)
            with col_qty:
                quantity = st.number_input("数量", min_value=1, value=1, step=1, key="trade_quantity")
            with col_price:
                price = st.number_input("价格", min_value=0.01, value=current_price if 'current_price' in locals() else 100.0, step=0.01, key="trade_price")
            
            # 计算交易金额
            total_amount = quantity * price
            st.markdown(f"**交易金额:** ¥{total_amount:.2f}")
            
            # 添加智能交易建议
            if 'trade_symbol' in locals() and trade_symbol:
                st.markdown("#### 🤖 智能交易建议")
                
                # 风险评估
                risk_level = "低"
                risk_color = "#4CAF50"
                if total_amount > portfolio['cash'] * 0.3:
                    risk_level = "中"
                    risk_color = "#FF9800"
                if total_amount > portfolio['cash'] * 0.5:
                    risk_level = "高"
                    risk_color = "#F44336"
                
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; 
                           border-left: 4px solid {risk_color}; margin: 10px 0;">
                    <h5 style="margin: 0 0 10px 0; color: {risk_color};">风险评估: {risk_level}</h5>
                    <div style="font-size: 0.9rem; line-height: 1.4;">
                        <p style="margin: 5px 0;">💰 交易占可用资金比例: {(total_amount / portfolio['cash'] * 100):.1f}%</p>
                        <p style="margin: 5px 0;">📊 建议单笔交易不超过可用资金的30%</p>
                        <p style="margin: 5px 0;">⏰ T+7机制：买入后需等待7天才能卖出</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 价格分析
                if action == "买入":
                    st.markdown("""
                    <div style="background: rgba(76, 175, 80, 0.1); padding: 12px; border-radius: 8px; margin: 10px 0;">
                        <h6 style="margin: 0 0 8px 0; color: #4CAF50;">💡 买入建议</h6>
                        <p style="margin: 0; font-size: 0.9rem;">• 建议分批买入，降低平均成本</p>
                        <p style="margin: 0; font-size: 0.9rem;">• 关注市场趋势，避免追高</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: rgba(244, 67, 54, 0.1); padding: 12px; border-radius: 8px; margin: 10px 0;">
                        <h6 style="margin: 0 0 8px 0; color: #F44336;">💡 卖出建议</h6>
                        <p style="margin: 0; font-size: 0.9rem;">• 确认已过T+7锁定期</p>
                        <p style="margin: 0; font-size: 0.9rem;">• 考虑市场时机，避免恐慌性抛售</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 执行交易按钮
            if st.button(f"🚀 执行{action}", use_container_width=True, key="execute_trade"):
                if 'trade_symbol' in locals() and trade_symbol:
                    success, message = execute_trade(trade_symbol, action, quantity, price)
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("请选择交易标的")
        
        with col2:
            # 交易信息面板
            st.markdown("#### 📋 交易信息")
            
            if 'trade_symbol' in locals() and trade_symbol:
                # 显示持仓信息
                if trade_symbol in portfolio['positions']:
                    position = portfolio['positions'][trade_symbol]
                    market_value, pnl_amount, pnl_percent = calculate_pnl(trade_symbol, current_price)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📊 当前持仓</h4>
                        <p><strong>持有数量:</strong> {position['quantity']} 个</p>
                        <p><strong>平均成本:</strong> ¥{position['avg_price']:.2f}</p>
                        <p><strong>市场价值:</strong> ¥{market_value:.2f}</p>
                        <p><strong>盈亏金额:</strong> <span style="color: {'#4CAF50' if pnl_amount >= 0 else '#F44336'}">¥{pnl_amount:.2f}</span></p>
                        <p><strong>盈亏比例:</strong> <span style="color: {'#4CAF50' if pnl_percent >= 0 else '#F44336'}">{pnl_percent:+.2f}%</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="metric-card">
                        <h4>📊 当前持仓</h4>
                        <p>暂无持仓</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 显示库存信息（T+7机制）
            if trade_symbol in portfolio['inventory']:
                inventory = portfolio['inventory'][trade_symbol]
                total_qty = inventory.get('total_quantity', 0)
                available_qty = inventory.get('available_quantity', 0)
                locked_qty = total_qty - available_qty
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📦 库存状态</h4>
                    <p><strong>总库存:</strong> {total_qty} 个</p>
                    <p><strong>可卖数量:</strong> <span style="color: #4CAF50">{available_qty} 个</span></p>
                    <p><strong>锁定数量:</strong> <span style="color: #FF9800">{locked_qty} 个</span></p>
                    <p><small>💡 锁定物品需等待7天后可卖出</small></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card">
                    <h4>📦 库存状态</h4>
                    <p>暂无库存</p>
                </div>
                """, unsafe_allow_html=True)
        
            # 资金状况
            st.markdown(f"""
            <div class="metric-card">
                <h4>💰 资金状况</h4>
                <p><strong>可用资金:</strong> ¥{portfolio['cash']:,.2f}</p>
                <p><strong>总资产:</strong> ¥{total_value:,.2f}</p>
                <p><strong>资金使用率:</strong> {((total_value - portfolio['cash']) / total_value * 100):.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    with trade_tab2:
        st.markdown("### 📦 我的库存")
        
        # 库存统计信息
        total_items = sum([inv.get('total_quantity', 0) for inv in portfolio['inventory'].values()])
        available_items = sum([inv.get('available_quantity', 0) for inv in portfolio['inventory'].values()])
        locked_items = total_items - available_items
        total_inventory_value = 0
        
        # 计算库存总价值
        for symbol, inventory in portfolio['inventory'].items():
            current_price = get_current_price(symbol)
            total_inventory_value += inventory.get('total_quantity', 0) * current_price
        
        # 库存概览
        st.markdown(f"""
        <div class="portfolio-summary">
            <h3>📦 库存概览</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
                <div style="text-align: center;">
                    <h4 style="margin: 0; color: #0D47A1;">总物品数</h4>
                    <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #1976D2;">{total_items}</p>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">件饰品</p>
                </div>
                <div style="text-align: center;">
                    <h4 style="margin: 0; color: #0D47A1;">可交易</h4>
                    <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #4CAF50;">{available_items}</p>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">件可卖</p>
                </div>
                <div style="text-align: center;">
                    <h4 style="margin: 0; color: #0D47A1;">锁定中</h4>
                    <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #FF9800;">{locked_items}</p>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">件锁定</p>
                </div>
                <div style="text-align: center;">
                    <h4 style="margin: 0; color: #0D47A1;">库存价值</h4>
                    <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #1976D2;">¥{total_inventory_value:,.2f}</p>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">当前估值</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if portfolio['inventory']:
            # 筛选和排序选项
            st.markdown("### 🎮 库存管理工具")
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_category = st.selectbox("🔍 筛选分类", ["全部"] + list(DATA_SOURCES.keys()), key="inventory_filter")
            with col2:
                sort_by = st.selectbox("📊 排序方式", ["按价值", "按数量", "按名称", "按盈亏"], key="inventory_sort")
            with col3:
                show_locked = st.checkbox("🔒 显示锁定物品", value=True, key="show_locked")
            
            # 添加快速统计
            st.markdown("### 📈 库存快速统计")
            col1, col2, col3, col4 = st.columns(4)
            
            profitable_items = 0
            loss_items = 0
            total_profit = 0
            
            for symbol, inventory in portfolio['inventory'].items():
                if inventory.get('total_quantity', 0) > 0:
                    current_price = get_current_price(symbol)
                    total_qty = inventory.get('total_quantity', 0)
                    locked_items_list = inventory.get('locked_items', [])
                    
                    # 计算平均成本
                    total_cost = 0
                    for item in locked_items_list:
                        total_cost += item.get('purchase_price', current_price)
                    avg_cost = total_cost / len(locked_items_list) if locked_items_list else current_price
                    
                    total_value = total_qty * current_price
                    pnl_amount = total_value - (total_qty * avg_cost)
                    total_profit += pnl_amount
                    
                    if pnl_amount > 0:
                        profitable_items += 1
                    elif pnl_amount < 0:
                        loss_items += 1
            
            with col1:
                st.metric("💰 盈利物品", f"{profitable_items}个", delta="盈利中")
            with col2:
                st.metric("📉 亏损物品", f"{loss_items}个", delta="需关注")
            with col3:
                st.metric("💎 总盈亏", f"¥{total_profit:.2f}", delta=f"{(total_profit/total_inventory_value*100):.1f}%" if total_inventory_value > 0 else "0%")
            with col4:
                avg_profit_per_item = total_profit / len(portfolio['inventory']) if portfolio['inventory'] else 0
                st.metric("📊 平均盈亏", f"¥{avg_profit_per_item:.2f}", delta="每件物品")
            
            # 准备库存数据
            inventory_items = []
            for symbol, inventory in portfolio['inventory'].items():
                if inventory.get('total_quantity', 0) > 0:
                    # 确定分类
                    item_category = "未知"
                    for cat, items in DATA_SOURCES.items():
                        if symbol in items:
                            item_category = cat
                            break
                    
                    # 应用分类筛选
                    if filter_category != "全部" and item_category != filter_category:
                        continue
                    
                    current_price = get_current_price(symbol)
                    total_qty = inventory.get('total_quantity', 0)
                    available_qty = inventory.get('available_quantity', 0)
                    locked_qty = total_qty - available_qty
                    
                    # 应用锁定物品筛选
                    if not show_locked and locked_qty > 0:
                        continue
                    
                    # 计算价值和盈亏
                    total_value = total_qty * current_price
                    locked_items_list = inventory.get('locked_items', [])
                    
                    # 计算平均成本
                    total_cost = 0
                    for item in locked_items_list:
                        total_cost += item.get('purchase_price', current_price)
                    avg_cost = total_cost / len(locked_items_list) if locked_items_list else current_price
                    
                    pnl_amount = total_value - (total_qty * avg_cost)
                    pnl_percent = (pnl_amount / (total_qty * avg_cost)) * 100 if avg_cost > 0 else 0
                    
                    # 计算剩余锁定时间
                    min_unlock_time = None
                    if locked_items_list:
                        current_time = datetime.now()
                        for item in locked_items_list:
                            purchase_date = item['purchase_date']
                            if isinstance(purchase_date, str):
                                purchase_date = datetime.fromisoformat(purchase_date)
                            unlock_time = purchase_date + timedelta(days=7)
                            if unlock_time > current_time:
                                if min_unlock_time is None or unlock_time < min_unlock_time:
                                    min_unlock_time = unlock_time
                    
                    inventory_items.append({
                        'symbol': symbol,
                        'category': item_category,
                        'total_qty': total_qty,
                        'available_qty': available_qty,
                        'locked_qty': locked_qty,
                        'current_price': current_price,
                        'avg_cost': avg_cost,
                        'total_value': total_value,
                        'pnl_amount': pnl_amount,
                        'pnl_percent': pnl_percent,
                        'unlock_time': min_unlock_time
                    })
            
            # 排序
            if sort_by == "按价值":
                inventory_items.sort(key=lambda x: x['total_value'], reverse=True)
            elif sort_by == "按数量":
                inventory_items.sort(key=lambda x: x['total_qty'], reverse=True)
            elif sort_by == "按盈亏":
                inventory_items.sort(key=lambda x: x['pnl_amount'], reverse=True)
            else:  # 按名称
                inventory_items.sort(key=lambda x: x['symbol'])
            
            if inventory_items:
                # 使用简洁的卡片式布局展示库存
                st.markdown("### 🎮 库存物品展示")
                
                # 每行显示3个物品
                cols_per_row = 3
                for i in range(0, len(inventory_items), cols_per_row):
                    cols = st.columns(cols_per_row)
                    
                    for j, col in enumerate(cols):
                        if i + j < len(inventory_items):
                            item = inventory_items[i + j]
                            
                            with col:
                                # 确定品质等级
                                if item['pnl_percent'] >= 20:
                                    quality_text = "🏆 传说"
                                    quality_color = "gold"
                                elif item['pnl_percent'] >= 10:
                                    quality_text = "💜 史诗"
                                    quality_color = "purple"
                                elif item['pnl_percent'] >= 0:
                                    quality_text = "💎 稀有"
                                    quality_color = "blue"
                                else:
                                    quality_text = "🟢 普通"
                                    quality_color = "green"
                                
                                # 状态标签
                                if item['locked_qty'] > 0:
                                    if item['unlock_time']:
                                        remaining_time = item['unlock_time'] - datetime.now()
                                        if remaining_time.total_seconds() > 0:
                                            days = remaining_time.days
                                            hours = remaining_time.seconds // 3600
                                            status_text = f"🔒 {days}天{hours}小时"
                                        else:
                                            status_text = "✅ 可交易"
                                    else:
                                        status_text = "🔒 锁定中"
                                else:
                                    status_text = "✅ 可交易"
                                
                                # 使用简洁的容器展示
                                with st.container():
                                    # 显示物品名称和信息
                                    st.markdown(f"### 🎮 {item['symbol']}")
                                    st.markdown(f"{quality_text} | {status_text}")
                                    
                                    # 显示详细信息
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"**数量:** {item['total_qty']} 个")
                                        st.markdown(f"**当前价格:** ¥{item['current_price']:.2f}")
                                    with col2:
                                        st.markdown(f"**盈亏:** <span style='color: {'#4CAF50' if item['pnl_amount'] >= 0 else '#F44336'}'>¥{item['pnl_amount']:.2f} ({item['pnl_percent']:+.1f}%)</span>", unsafe_allow_html=True)
                                        if item['locked_qty'] > 0:
                                            st.markdown(f"**🔒 锁定:** {item['locked_qty']} 个")
                                        if item['available_qty'] > 0:
                                            st.markdown(f"**✅ 可卖:** {item['available_qty']} 个")
                                    
                                    st.markdown("---")  # 分隔线
                
                # 快速操作按钮
                st.markdown("### ⚡ 快速操作")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 刷新库存价格", use_container_width=True):
                        st.session_state.last_price_update = None
                        st.rerun()
                
                with col2:
                    if st.button("📊 库存分析报告", use_container_width=True):
                        st.info("📈 库存分析功能开发中，敬请期待！")
                
                with col3:
                    if st.button("💰 一键估值", use_container_width=True):
                        st.success(f"✅ 当前库存总估值: ¥{total_inventory_value:,.2f}")
            else:
                st.info("📦 暂无库存物品")
        else:
            st.info("📦 暂无库存物品")
    
    with trade_tab3:
        st.markdown("### 📊 持仓管理")
        
        if portfolio['positions']:
            # 总仓位风险分析
            st.markdown("#### 🎯 总仓位风险分析")
            total_risk_analysis = analyze_total_position_risk(portfolio)
            
            if 'error' not in total_risk_analysis:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "💰 可用资金", 
                        f"¥{total_risk_analysis['total_cash']:,.0f}",
                        f"{total_risk_analysis['cash_ratio']:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "📈 投入资金", 
                        f"¥{total_risk_analysis['invested_amount']:,.0f}",
                        f"{total_risk_analysis['investment_ratio']:.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "💎 当前市值", 
                        f"¥{total_risk_analysis['total_market_value']:,.0f}",
                        f"{total_risk_analysis['total_pnl']:+,.0f}"
                    )
                
                with col4:
                    total_pnl = total_risk_analysis.get('total_pnl', 0)
                    pnl_color = "normal" if isinstance(total_pnl, (int, float)) and total_pnl >= 0 else "inverse"
                    st.metric(
                        "📊 总收益率", 
                        f"{total_risk_analysis['total_pnl_percent']:+.2f}%",
                        delta_color=pnl_color
                    )
                
                # 总仓位风险等级和建议
                risk_colors = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
                risk_color = risk_colors.get(total_risk_analysis['risk_level'], '🟡')
                
                st.markdown(f"**总体风险等级**: {risk_color} {total_risk_analysis['risk_level'].upper()}")
                
                if total_risk_analysis['risk_suggestions']:
                    st.markdown("**总仓位建议**:")
                    for suggestion in total_risk_analysis['risk_suggestions']:
                        st.markdown(f"• {suggestion}")
            else:
                st.error(total_risk_analysis['error'])
            
            st.divider()
            
            # 持仓概览
            st.markdown("#### 💼 持仓概览")
            
            # 创建持仓数据
            position_data = []
            total_cost = 0
            total_market_value = 0
            
            for symbol, position in portfolio['positions'].items():
                current_price = get_current_price(symbol)
                quantity = position['quantity']
                avg_price = position['avg_price']
                
                cost_value = quantity * avg_price
                market_value = quantity * current_price
                pnl_amount = market_value - cost_value
                pnl_percent = (pnl_amount / cost_value) * 100 if cost_value > 0 else 0
                
                total_cost += cost_value
                total_market_value += market_value
                
                position_data.append({
                    '标的名称': symbol,
                    '持有数量': f"{quantity} 个",
                    '平均成本': f"¥{avg_price:.2f}",
                    '当前价格': f"¥{current_price:.2f}",
                    '成本价值': f"¥{cost_value:.2f}",
                    '市场价值': f"¥{market_value:.2f}",
                    '盈亏金额': f"¥{pnl_amount:.2f}",
                    '盈亏比例': f"{pnl_percent:+.2f}%"
                })
            
            # 显示持仓表格
            df_positions = pd.DataFrame(position_data)
            st.dataframe(df_positions, use_container_width=True)
            
            # 持仓统计
            total_pnl = total_market_value - total_cost
            total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总成本", f"¥{total_cost:,.2f}")
            with col2:
                st.metric("总市值", f"¥{total_market_value:,.2f}")
            with col3:
                st.metric("总盈亏", f"¥{total_pnl:,.2f}", f"{total_pnl_percent:+.2f}%")
            with col4:
                st.metric("持仓品种", f"{len(portfolio['positions'])}个")
            
            # 持仓分布图
            st.markdown("#### 📊 持仓分布")
            if len(position_data) > 0:
                # 创建饼图
                symbols = [item['标的名称'] for item in position_data]
                values = [float(item['市场价值'].replace('¥', '').replace(',', '')) for item in position_data]
                
                fig = go.Figure(data=[go.Pie(labels=symbols, values=values, hole=.3)])
                fig.update_layout(
                    title="持仓市值分布",
                    height=400,
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # 智能仓位分析
            st.markdown("#### 🧠 智能仓位分析")
            
            # 添加分析说明
            st.markdown("""
            <div class="metric-card">
                <h4>📈 分析说明</h4>
                <p>基于K线技术分析、仓位占比、盈亏状况等多维度数据，为您的每个持仓提供专业的操作建议</p>
                <p>• <strong>仓位占比：</strong>分析单一标的风险集中度</p>
                <p>• <strong>技术指标：</strong>结合RSI、MACD、趋势状态等</p>
                <p>• <strong>价格变化：</strong>分析短期和中期价格走势</p>
                <p>• <strong>风险评估：</strong>综合评估持仓风险等级</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 分析控制面板
            col1, col2, col3 = st.columns(3)
            with col1:
                analyze_all = st.button("🔍 分析所有持仓", use_container_width=True, help="对所有持仓进行智能分析")
            with col2:
                show_details = st.checkbox("📋 显示详细建议", value=True, help="显示详细的分析建议")
            with col3:
                risk_filter = st.selectbox("🎯 风险筛选", ["全部", "高风险", "中风险", "低风险"], help="按风险等级筛选显示")
            
            # 执行分析
            if analyze_all or 'position_analysis_results' not in st.session_state:
                with st.spinner("正在进行智能分析..."):
                    analysis_results = []
                    
                    # 计算投资组合总价值
                    portfolio_total_value = total_market_value + portfolio['cash']
                    
                    for symbol, position in portfolio['positions'].items():
                        analysis = analyze_position_with_kline(symbol, position, portfolio_total_value)
                        analysis_results.append(analysis)
                    
                    st.session_state.position_analysis_results = analysis_results
                    if analyze_all:
                        st.success("✅ 智能分析完成！")
            
            # 显示分析结果
            if 'position_analysis_results' in st.session_state:
                results = st.session_state.position_analysis_results
                
                # 应用风险筛选
                if risk_filter and risk_filter != "全部":
                    risk_map = {"高风险": "high", "中风险": "medium", "低风险": "low"}
                    if risk_filter in risk_map:
                        results = [r for r in results if r.get('risk_level') == risk_map[risk_filter]]
                
                if results:
                    # 分析摘要
                    st.markdown("#### 📊 分析摘要")
                    
                    high_risk_count = len([r for r in st.session_state.position_analysis_results if r.get('risk_level') == 'high'])
                    medium_risk_count = len([r for r in st.session_state.position_analysis_results if r.get('risk_level') == 'medium'])
                    low_risk_count = len([r for r in st.session_state.position_analysis_results if r.get('risk_level') == 'low'])
                    
                    # 操作建议统计
                    action_counts = {}
                    for result in st.session_state.position_analysis_results:
                        action = result.get('action_suggestion', '持有观望')
                        action_counts[action] = action_counts.get(action, 0) + 1
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🔴 高风险", f"{high_risk_count}个", help="需要重点关注的持仓")
                    with col2:
                        st.metric("🟡 中风险", f"{medium_risk_count}个", help="需要适度关注的持仓")
                    with col3:
                        st.metric("🟢 低风险", f"{low_risk_count}个", help="相对安全的持仓")
                    with col4:
                        most_common_action = max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else "持有观望"
                        st.metric("💡 主要建议", most_common_action, help="最常见的操作建议")
                    
                    # 详细分析结果
                    st.markdown("#### 📋 详细分析结果")
                    
                    for i, result in enumerate(results):
                        if result['status'] == 'success':
                            symbol = result['symbol']
                            risk_level = result['risk_level']
                            action_suggestion = result['action_suggestion']
                            
                            # 风险等级颜色
                            if risk_level == 'high':
                                risk_color = "#F44336"
                                risk_icon = "🔴"
                                risk_text = "高风险"
                            elif risk_level == 'medium':
                                risk_color = "#FF9800"
                                risk_icon = "🟡"
                                risk_text = "中风险"
                            else:
                                risk_color = "#4CAF50"
                                risk_icon = "🟢"
                                risk_text = "低风险"
                            
                            # 操作建议颜色
                            if "减仓" in action_suggestion or "止损" in action_suggestion:
                                action_color = "#F44336"
                                action_icon = "🔴"
                            elif "加仓" in action_suggestion:
                                action_color = "#4CAF50"
                                action_icon = "🟢"
                            else:
                                action_color = "#1976D2"
                                action_icon = "🔵"
                            
                            # 技术评分
                            technical_score = result.get('technical_score', 0)
                            if technical_score > 0:
                                score_color = "#4CAF50"
                                score_text = f"+{technical_score} (偏多)"
                            elif technical_score < 0:
                                score_color = "#F44336"
                                score_text = f"{technical_score} (偏空)"
                            else:
                                score_color = "#FF9800"
                                score_text = "0 (中性)"
                            
                            with st.expander(f"📊 {symbol} - {risk_icon} {risk_text} | {action_icon} {action_suggestion}", expanded=False):
                                # 基本信息
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(f"""
                                    **📈 价格信息**
                                    - 当前价格: ¥{result['current_price']:.2f}
                                    - 7日涨跌: {result['price_change_7d']:+.1f}%
                                    - 30日涨跌: {result['price_change_30d']:+.1f}%
                                    """)
                                
                                with col2:
                                    st.markdown(f"""
                                    **💼 仓位信息**
                                    - 仓位占比: {result['position_weight']:.1f}%
                                    - 持仓盈亏: {result['position_pnl_percent']:+.1f}%
                                    - 主趋势: {result['trend_status']}
                                    """)
                                
                                with col3:
                                    st.markdown(f"""
                                    **🎯 技术指标**
                                    - RSI: {result['rsi']:.1f}
                                    - 风险等级: <span style="color: {risk_color}; font-weight: 600;">{risk_text}</span>
                                    - 技术评分: <span style="color: {score_color}; font-weight: 600;">{score_text}</span>
                                    """, unsafe_allow_html=True)
                                
                                # 详细建议
                                if show_details and result['suggestions']:
                                    st.markdown("**💡 详细分析建议:**")
                                    for suggestion in result['suggestions']:
                                        st.markdown(f"• {suggestion}")
                                
                                # 操作建议
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); 
                                            padding: 1rem; border-radius: 8px; margin-top: 1rem;
                                            border-left: 4px solid {action_color};">
                                    <h5 style="margin: 0; color: {action_color};">{action_icon} 操作建议</h5>
                                    <p style="margin: 0.5rem 0; font-weight: 600; color: #0D47A1;">{action_suggestion}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            # 分析失败的情况
                            st.error(f"❌ {result.get('symbol', '未知')} 分析失败: {result.get('message', '未知错误')}")
                    
                    # 整体投资组合建议
                    st.markdown("#### 🎯 整体投资组合建议")
                    
                    # 计算整体风险
                    total_high_risk_value = sum([
                        portfolio['positions'][r['symbol']]['quantity'] * r['current_price'] 
                        for r in st.session_state.position_analysis_results 
                        if r.get('risk_level') == 'high' and r['status'] == 'success'
                    ])
                    high_risk_ratio = (total_high_risk_value / total_market_value) * 100 if total_market_value > 0 else 0
                    
                    # 整体建议
                    portfolio_suggestions = []
                    
                    if high_risk_ratio > 50:
                        portfolio_suggestions.append("⚠️ 高风险持仓占比过高，建议优先处理高风险标的")
                    elif high_risk_ratio > 30:
                        portfolio_suggestions.append("🟡 高风险持仓占比较高，需要适度调整")
                    else:
                        portfolio_suggestions.append("✅ 整体风险控制良好")
                    
                    # 仓位集中度分析
                    max_position_weight = max([r.get('position_weight', 0) for r in st.session_state.position_analysis_results if r['status'] == 'success'], default=0)
                    if max_position_weight > 40:
                        portfolio_suggestions.append("⚠️ 存在过度集中的单一持仓，建议分散投资")
                    elif max_position_weight > 30:
                        portfolio_suggestions.append("🟡 单一持仓占比较高，注意分散风险")
                    
                    # 技术面整体评估
                    avg_technical_score = sum([r.get('technical_score', 0) for r in st.session_state.position_analysis_results if r['status'] == 'success']) / len([r for r in st.session_state.position_analysis_results if r['status'] == 'success'])
                    if avg_technical_score > 1:
                        portfolio_suggestions.append("📈 整体技术面偏多，市场情绪相对乐观")
                    elif avg_technical_score < -1:
                        portfolio_suggestions.append("📉 整体技术面偏空，建议谨慎操作")
                    else:
                        portfolio_suggestions.append("📊 整体技术面中性，建议根据个股情况操作")
                    
                    # 显示整体建议
                    suggestion_html = ""
                    for suggestion in portfolio_suggestions:
                        suggestion_html += f"<p>• {suggestion}</p>"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>🎯 投资组合整体评估</h4>
                        <p><strong>高风险持仓占比:</strong> {high_risk_ratio:.1f}%</p>
                        <p><strong>最大单一持仓:</strong> {max_position_weight:.1f}%</p>
                        <p><strong>技术面评分:</strong> {avg_technical_score:.1f}</p>
                        <hr style="margin: 1rem 0;">
                        <h5>💡 整体建议</h5>
                        {suggestion_html}
                        <p style="margin-top: 1rem;"><strong>风险提示:</strong> 以上分析基于技术指标，仅供参考，投资需谨慎。</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.info(f"📊 当前筛选条件下无持仓数据")
            else:
                st.info("📊 点击'分析所有持仓'开始智能分析")
        else:
            st.info("📦 暂无持仓，请先进行交易")
            
            # 显示交易建议
            st.markdown("""
            <div class="metric-card">
                <h4>💡 交易建议</h4>
                <p>• 前往"交易面板"开始您的第一笔交易</p>
                <p>• 建议先进行小额测试交易，熟悉系统</p>
                <p>• 注意T+7交易机制，买入后需等待7天才能卖出</p>
            </div>
            """, unsafe_allow_html=True)

def trading_strategy_page():
    """交易策略页面"""
    st.markdown('<h2 class="sub-header">🎯 交易策略回测</h2>', unsafe_allow_html=True)
    
    # 策略说明
    st.markdown("""
    <div class="metric-card">
        <h4>📊 策略说明</h4>
        <p>基于移动平均线的量化交易策略，通过技术指标识别买入卖出时机：</p>
        <ul>
            <li><strong>买入条件：</strong> MA5 > MA20 且价格 > MA10 且偏离度 < 阈值</li>
            <li><strong>卖出条件：</strong> 3日跌幅超过止损阈值且跌破MA10，或持有超过7天</li>
            <li><strong>风控机制：</strong> T+7交易限制，智能止损，分批建仓</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 参数配置
    st.markdown("### ⚙️ 策略参数配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 选择回测标的
        category = st.selectbox("📂 选择饰品分类", list(DATA_SOURCES.keys()), key="strategy_category")
        if category:
            symbol_list = list(DATA_SOURCES[category].keys())
            selected_symbol = st.selectbox("🎯 选择回测标的", symbol_list, key="strategy_symbol")
        
        # 时间范围
        start_date = st.date_input(
            "📅 回测开始日期",
            value=datetime.now() - timedelta(days=90),
            help="选择回测的开始日期"
        )
        end_date = st.date_input(
            "📅 回测结束日期", 
            value=datetime.now(),
            help="选择回测的结束日期"
        )
    
    with col2:
        # 策略参数
        k0 = st.slider("K因子", min_value=1.0, max_value=20.0, value=6.7, step=0.1, 
                      help="控制卖出强度的参数，值越大卖出越激进")
        bias_th = st.slider("偏离阈值", min_value=0.01, max_value=0.20, value=0.07, step=0.01,
                           help="价格相对MA5的偏离阈值，超过则考虑卖出")
        sell_days = st.slider("卖出观察天数", min_value=1, max_value=10, value=3, step=1,
                             help="观察价格跌幅的天数")
        sell_drop_th = st.slider("止损跌幅阈值", min_value=-0.20, max_value=-0.01, value=-0.05, step=0.01,
                                help="触发止损的跌幅阈值")
    
    # 回测按钮
    if st.button("🚀 开始策略回测", use_container_width=True):
        if 'selected_symbol' in locals() and selected_symbol and category:
            try:
                # 获取数据
                with st.spinner("正在获取历史数据..."):
                    data_url = DATA_SOURCES[category][selected_symbol]
                    
                    # 安全处理日期格式
                    if hasattr(start_date, 'strftime'):
                        start_date_str = start_date.strftime('%Y-%m-%d')
                    else:
                        start_date_str = str(start_date)
                    
                    if hasattr(end_date, 'strftime'):
                        end_date_str = end_date.strftime('%Y-%m-%d')
                    else:
                        end_date_str = str(end_date)
                    
                    kline_df = get_kline(data_url, start_date_str, end_date_str)
                
                if kline_df.empty:
                    st.error("❌ 未获取到数据，请检查网络连接或调整日期范围")
                    return
                
                # 执行回测
                with st.spinner("正在执行策略回测..."):
                    backtest_result = backtest_strategy(kline_df, k0, bias_th, sell_days, sell_drop_th)
                
                if backtest_result.empty:
                    st.error("❌ 回测失败，数据不足或参数错误")
                    return
                
                # 计算绩效指标
                risk_metrics = get_risk_metrics(backtest_result)
                
                # 显示回测结果
                st.markdown("### 📊 回测结果")
                
                # 绩效指标
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总收益率", f"{risk_metrics.get('总收益率', 0)*100:.2f}%")
                with col2:
                    st.metric("年化收益率", f"{risk_metrics.get('年化收益', 0)*100:.2f}%")
                with col3:
                    st.metric("夏普比率", f"{risk_metrics.get('Sharpe', 0):.3f}")
                with col4:
                    st.metric("最大回撤", f"{risk_metrics.get('最大回撤', 0)*100:.2f}%")
                
                # 策略表现图表
                st.markdown("#### 📈 策略表现")
                
                # 计算累计收益
                cumulative_returns = (1 + backtest_result['ret']).cumprod()
                
                # 创建图表
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=('累计收益曲线', '仓位变化', '价格走势与交易信号'),
                    row_heights=[0.4, 0.3, 0.3]
                )
                
                # 累计收益曲线
                fig.add_trace(
                    go.Scatter(x=backtest_result.index, y=cumulative_returns, 
                              name='策略收益', line=dict(color='#1976D2', width=3)),
                    row=1, col=1
                )
                
                # 仓位变化
                fig.add_trace(
                    go.Scatter(x=backtest_result.index, y=backtest_result['pos'], 
                              name='仓位', line=dict(color='#4CAF50', width=2)),
                    row=2, col=1
                )
                
                # 价格走势
                fig.add_trace(
                    go.Scatter(x=backtest_result.index, y=backtest_result['price'], 
                              name='价格', line=dict(color='#FF9800', width=2)),
                    row=3, col=1
                )
                
                # 买入信号
                buy_signals = backtest_result[backtest_result['buy'] > 0]
                if not buy_signals.empty:
                    fig.add_trace(
                        go.Scatter(x=buy_signals.index, y=buy_signals['price'], 
                                  mode='markers', name='买入信号',
                                  marker=dict(color='#4CAF50', size=10, symbol='triangle-up')),
                        row=3, col=1
                    )
                
                # 卖出信号
                sell_signals = backtest_result[backtest_result['sell'] > 0]
                if not sell_signals.empty:
                    fig.add_trace(
                        go.Scatter(x=sell_signals.index, y=sell_signals['price'], 
                                  mode='markers', name='卖出信号',
                                  marker=dict(color='#F44336', size=10, symbol='triangle-down')),
                        row=3, col=1
                    )
                
                fig.update_layout(
                    height=800,
                    title=f"{selected_symbol} 策略回测结果",
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 月度收益分析
                st.markdown("#### 📅 月度收益分析")
                
                # 计算月度收益
                try:
                    monthly_returns = backtest_result['ret'].resample('M').apply(lambda x: (1 + x).prod() - 1)
                    
                    if len(monthly_returns) > 1:
                        fig_monthly = go.Figure()
                        # 安全处理收益率数据类型转换
                        colors = []
                        y_values = []
                        for i, ret in enumerate(monthly_returns):
                            try:
                                # 安全地处理各种数据类型
                                ret_value = 0.0
                                
                                # 极度简化版本，绕过所有类型检查问题
                                ret_value = 0.0
                                try:
                                    # 直接尝试转换为字符串再转换为浮点数
                                    # 这种方式绕过了所有Hashable类型错误
                                    ret_str = str(ret)
                                    ret_value = float(ret_str)
                                except:
                                    # 任何错误都设为0
                                    ret_value = 0.0
                                
                                colors.append('#4CAF50' if ret_value >= 0 else '#F44336')
                                y_values.append(ret_value * 100)
                            except:
                                colors.append('#FF9800')  # 橙色表示无效数据
                                y_values.append(0)
                        
                        # 安全处理日期索引
                        try:
                            x_labels = [date.strftime('%Y-%m') for date in monthly_returns.index]
                        except:
                            x_labels = [str(date) for date in monthly_returns.index]
                        
                        fig_monthly.add_trace(go.Bar(
                            x=x_labels,
                            y=y_values,
                            marker_color=colors,
                            name='月度收益率'
                        ))
                        
                        fig_monthly.update_layout(
                            title="月度收益率分布",
                            xaxis_title="月份",
                            yaxis_title="收益率 (%)",
                            height=400
                        )
                        
                        st.plotly_chart(fig_monthly, use_container_width=True)
                except Exception as e:
                    st.warning(f"月度收益分析暂时无法显示: {str(e)}")
                
                # 详细统计
                st.markdown("#### 📋 详细统计")
                
                # 交易统计
                total_trades = len(buy_signals) + len(sell_signals)
                win_trades = len(backtest_result[backtest_result['ret'] > 0])
                total_days = len(backtest_result)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    **📊 交易统计**
                    - 总交易次数: {total_trades}
                    - 盈利交易: {win_trades}
                    - 胜率: {(win_trades/total_days*100):.1f}%
                    """)
                
                with col2:
                    st.markdown(f"""
                    **📈 收益统计**
                    - 波动率: {risk_metrics.get('波动率', 0)*100:.2f}%
                    - Calmar比率: {risk_metrics.get('Calmar', 0):.3f}
                    - 回测天数: {total_days}天
                    """)
                
                with col3:
                    avg_pos = backtest_result['pos'].mean()
                    max_pos = backtest_result['pos'].max()
                    st.markdown(f"""
                    **💼 仓位统计**
                    - 平均仓位: {avg_pos:.2f}
                    - 最大仓位: {max_pos:.2f}
                    - 满仓天数: {len(backtest_result[backtest_result['pos'] >= 0.9])}天
                    """)
                
                # 保存回测结果到session state
                st.session_state.backtest_result = {
                    'symbol': selected_symbol,
                    'data': backtest_result,
                    'metrics': risk_metrics,
                    'parameters': {
                        'k0': k0,
                        'bias_th': bias_th,
                        'sell_days': sell_days,
                        'sell_drop_th': sell_drop_th
                    }
                }
                
                st.success("✅ 策略回测完成！")
                
            except Exception as e:
                st.error(f"❌ 回测过程出错: {str(e)}")
        else:
            st.error("请选择回测标的")
    
    # 显示历史回测结果
    if 'backtest_result' in st.session_state:
        st.markdown("### 📚 最近回测结果")
        result = st.session_state.backtest_result
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 {result['symbol']} 回测摘要</h4>
            <p><strong>总收益率:</strong> {result['metrics'].get('总收益率', 0)*100:.2f}%</p>
            <p><strong>年化收益率:</strong> {result['metrics'].get('年化收益', 0)*100:.2f}%</p>
            <p><strong>夏普比率:</strong> {result['metrics'].get('Sharpe', 0):.3f}</p>
            <p><strong>最大回撤:</strong> {result['metrics'].get('最大回撤', 0)*100:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 在适当位置添加
    # 生成交易建议
    if 'current_data' in st.session_state and st.session_state.current_data is not None:
        with st.expander("💡 智能交易建议", expanded=True):
            use_enhanced = st.checkbox("使用高级分析引擎", value=True)
            
            analysis_df = st.session_state.current_data
            # 市场情绪分析
            market_analysis = analyze_market_sentiment(analysis_df)
            
            if use_enhanced:
                # 高级市场情绪分析
                advanced_analysis = analyze_advanced_market_sentiment(analysis_df)
                if advanced_analysis:
                    market_analysis['advanced'] = advanced_analysis
                
                # 生成增强交易建议
                trading_recommendations = generate_enhanced_trading_recommendations(analysis_df, market_analysis)
            else:
                # 使用基础版
                trading_recommendations = generate_trading_recommendations(analysis_df, market_analysis)
            
            # 显示交易建议
            display_trading_recommendations(trading_recommendations)

def user_data_page(auth):
    """用户数据页面"""
    st.markdown('<h2 class="sub-header">📈 我的数据</h2>', unsafe_allow_html=True)
    
    # 获取用户信息
    user = auth.get_current_user()
    portfolio = st.session_state.portfolio
    
    # 检查是否为管理员 - 使用新的判断函数
    is_admin = is_admin_user(user)
    
    # 如果是管理员，显示管理者模式选项
    if is_admin:
        st.markdown("### 🔧 管理者模式")
        
        # 创建标签页
        admin_tab, user_tab = st.tabs(["👑 管理者控制台", "👤 个人数据"])
        
        with admin_tab:
            render_admin_panel()
        
        with user_tab:
            render_user_panel(user, portfolio)
    else:
        render_user_panel(user, portfolio)

def render_admin_panel():
    """渲染管理者控制台"""
    st.markdown("#### 👑 管理者控制台")
    st.info("🔐 您正在使用管理者权限，可以查看和管理所有用户数据")
    
    # 管理功能选项
    admin_function = st.selectbox(
        "选择管理功能",
        ["📊 用户总览", "💰 资金管理", "👥 用户管理", "📈 系统统计"]
    )
    
    if admin_function == "📊 用户总览":
        render_user_overview()
    elif admin_function == "💰 资金管理":
        render_fund_management()
    elif admin_function == "👥 用户管理":
        render_user_management()
    elif admin_function == "📈 系统统计":
        render_system_statistics()

def render_user_overview():
    """渲染用户总览"""
    st.markdown("##### 📊 用户总览")
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        # 获取所有用户信息
        import sqlite3
        conn = sqlite3.connect("trading_platform.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.display_name, u.email, u.is_active, u.created_at,
                   ua.cash, ua.total_value
            FROM users u
            LEFT JOIN user_accounts ua ON u.id = ua.user_id
            ORDER BY u.created_at DESC
        """)
        
        users_data = cursor.fetchall()
        conn.close()
        
        if users_data:
            # 创建用户数据表格
            user_df = pd.DataFrame(users_data, columns=[
                'ID', '用户名', '显示名', '邮箱', '状态', '注册时间', '现金', '总资产'
            ])
            
            # 格式化数据
            user_df['状态'] = user_df['状态'].apply(lambda x: '✅ 活跃' if x else '❌ 禁用')
            user_df['现金'] = user_df['现金'].apply(lambda x: f"¥{x:,.2f}" if x else "¥0.00")
            user_df['总资产'] = user_df['总资产'].apply(lambda x: f"¥{x:,.2f}" if x else "¥0.00")
            
            st.dataframe(user_df, use_container_width=True)
            
            # 统计信息
            total_users = len(users_data)
            active_users = sum(1 for user in users_data if user[4])
            total_cash = sum(user[6] for user in users_data if user[6])
            total_assets = sum(user[7] for user in users_data if user[7])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总用户数", total_users)
            with col2:
                st.metric("活跃用户", active_users)
            with col3:
                st.metric("系统总现金", f"¥{total_cash:,.2f}")
            with col4:
                st.metric("系统总资产", f"¥{total_assets:,.2f}")
        else:
            st.warning("暂无用户数据")
            
    except Exception as e:
        st.error(f"获取用户数据失败: {e}")

def render_fund_management():
    """渲染资金管理"""
    st.markdown("##### 💰 资金管理")
    
    # 选择用户
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        import sqlite3
        conn = sqlite3.connect("trading_platform.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, display_name FROM users WHERE is_active = 1")
        users = cursor.fetchall()
        conn.close()
        
        if users:
            user_options = {f"{user[1]} ({user[2]})": user[0] for user in users}
            selected_user = st.selectbox("选择用户", list(user_options.keys()))
            
            if selected_user:
                user_id = user_options[selected_user]
                
                # 获取用户当前资金
                conn = sqlite3.connect("trading_platform.db")
                cursor = conn.cursor()
                cursor.execute("SELECT cash, total_value FROM user_accounts WHERE user_id = ?", (user_id,))
                account_data = cursor.fetchone()
                conn.close()
                
                if account_data:
                    current_cash, current_total = account_data
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("当前现金", f"¥{current_cash:,.2f}")
                    with col2:
                        st.metric("总资产", f"¥{current_total:,.2f}")
                    
                    # 资金调整
                    st.markdown("**资金调整**")
                    
                    adjustment_type = st.radio("调整类型", ["增加资金", "减少资金", "设置资金"])
                    amount = st.number_input("金额", min_value=0.0, step=100.0, format="%.2f")
                    
                    if st.button("💰 执行资金调整", type="primary"):
                        if amount > 0:
                            new_cash = current_cash
                            
                            if adjustment_type == "增加资金":
                                new_cash = current_cash + amount
                            elif adjustment_type == "减少资金":
                                new_cash = max(0, current_cash - amount)
                            elif adjustment_type == "设置资金":
                                new_cash = amount
                            
                            # 更新数据库
                            try:
                                conn = sqlite3.connect("trading_platform.db")
                                cursor = conn.cursor()
                                cursor.execute("""
                                    UPDATE user_accounts 
                                    SET cash = ?, total_value = ?, updated_at = CURRENT_TIMESTAMP
                                    WHERE user_id = ?
                                """, (new_cash, new_cash, user_id))
                                conn.commit()
                                conn.close()
                                
                                st.success(f"✅ 资金调整成功！{selected_user} 的现金已调整为 ¥{new_cash:,.2f}")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"资金调整失败: {e}")
                        else:
                            st.warning("请输入有效金额")
                else:
                    st.warning("未找到用户账户数据")
        else:
            st.warning("暂无活跃用户")
            
    except Exception as e:
        st.error(f"获取用户列表失败: {e}")

def render_user_management():
    """渲染用户管理"""
    st.markdown("##### 👥 用户管理")
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        import sqlite3
        conn = sqlite3.connect("trading_platform.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, display_name, email, is_active FROM users")
        users = cursor.fetchall()
        conn.close()
        
        if users:
            for user in users:
                user_id, username, display_name, email, is_active = user
                
                with st.expander(f"👤 {username} ({display_name})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**邮箱:** {email}")
                        st.write(f"**状态:** {'✅ 活跃' if is_active else '❌ 禁用'}")
                    
                    with col2:
                        # 状态切换
                        new_status = st.checkbox("启用用户", value=bool(is_active), key=f"status_{user_id}")
                        
                        if new_status != bool(is_active):
                            if st.button(f"更新状态", key=f"update_{user_id}"):
                                try:
                                    conn = sqlite3.connect("trading_platform.db")
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
                                    conn.commit()
                                    conn.close()
                                    st.success("状态更新成功！")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"状态更新失败: {e}")
                    
                    with col3:
                        # 重置密码
                        if st.button(f"🔄 重置密码", key=f"reset_{user_id}"):
                            try:
                                new_password = "123456"  # 默认密码
                                password_hash = db.hash_password(new_password)
                                
                                conn = sqlite3.connect("trading_platform.db")
                                cursor = conn.cursor()
                                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
                                conn.commit()
                                conn.close()
                                
                                st.success(f"密码已重置为: {new_password}")
                            except Exception as e:
                                st.error(f"密码重置失败: {e}")
                        
                        # 设置管理员权限
                        st.markdown("**用户权限**")
                        col_admin1, col_admin2 = st.columns(2)
                        
                        with col_admin1:
                            if st.button(f"👑 设为管理员", key=f"admin_{user_id}"):
                                if set_user_admin_status(username, True):
                                    st.success(f"✅ {username} 已设置为管理员")
                                    st.rerun()
                                else:
                                    st.error("设置管理员失败")
                        
                        with col_admin2:
                            if st.button(f"👤 设为普通用户", key=f"user_{user_id}"):
                                if set_user_admin_status(username, False):
                                    st.success(f"✅ {username} 已设置为普通用户")
                                    st.rerun()
                                else:
                                    st.error("设置普通用户失败")
        else:
            st.warning("暂无用户数据")
            
    except Exception as e:
        st.error(f"获取用户数据失败: {e}")

def render_system_statistics():
    """渲染系统统计"""
    st.markdown("##### 📈 系统统计")
    
    try:
        import sqlite3
        conn = sqlite3.connect("trading_platform.db")
        cursor = conn.cursor()
        
        # 用户统计
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        active_users = cursor.fetchone()[0]
        
        # 资金统计
        cursor.execute("SELECT SUM(cash), SUM(total_value) FROM user_accounts")
        cash_total, assets_total = cursor.fetchone()
        cash_total = cash_total or 0
        assets_total = assets_total or 0
        
        # 交易统计
        cursor.execute("SELECT COUNT(*) FROM trade_records")
        total_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM trade_records")
        trading_users = cursor.fetchone()[0]
        
        conn.close()
        
        # 显示统计信息
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总用户数", total_users)
            st.metric("活跃用户", active_users)
        
        with col2:
            st.metric("系统总现金", f"¥{cash_total:,.2f}")
            st.metric("系统总资产", f"¥{assets_total:,.2f}")
        
        with col3:
            st.metric("总交易次数", total_trades)
            st.metric("交易用户数", trading_users)
        
        with col4:
            user_activity_rate = (active_users / total_users * 100) if total_users > 0 else 0
            trading_rate = (trading_users / total_users * 100) if total_users > 0 else 0
            st.metric("用户活跃率", f"{user_activity_rate:.1f}%")
            st.metric("交易参与率", f"{trading_rate:.1f}%")
        
        # 系统健康度
        st.markdown("**系统健康度**")
        health_score = (user_activity_rate + trading_rate) / 2
        
        if health_score >= 80:
            st.success(f"🟢 系统健康度: {health_score:.1f}% (优秀)")
        elif health_score >= 60:
            st.warning(f"🟡 系统健康度: {health_score:.1f}% (良好)")
        else:
            st.error(f"🔴 系统健康度: {health_score:.1f}% (需要关注)")
            
    except Exception as e:
        st.error(f"获取系统统计失败: {e}")

def render_user_panel(user, portfolio):
    """渲染用户个人面板"""
    # 用户基本信息
    st.markdown("### 👤 用户信息")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📋 基本信息</h4>
            <p><strong>用户名:</strong> {user['username']}</p>
            <p><strong>显示名:</strong> {user['display_name']}</p>
            <p><strong>注册时间:</strong> {user.get('created_at', '未知')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>💰 账户状态</h4>
            <p><strong>会员等级:</strong> {user.get('membership_level', '普通用户')}</p>
            <p><strong>余额:</strong> ¥{user.get('balance', 0):.2f}</p>
            <p><strong>状态:</strong> {'🟢 正常' if user.get('is_active', True) else '🔴 禁用'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # 计算交易统计
        total_trades = len(portfolio['trade_history'])
        total_positions = len(portfolio['positions'])
        total_inventory = sum([inv.get('total_quantity', 0) for inv in portfolio['inventory'].values()])
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 交易统计</h4>
            <p><strong>总交易次数:</strong> {total_trades}</p>
            <p><strong>当前持仓:</strong> {total_positions} 个品种</p>
            <p><strong>库存物品:</strong> {total_inventory} 件</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 投资组合分析
    st.markdown("### 💼 投资组合分析")
    
    if portfolio['positions']:
        # 计算投资组合数据
        total_cost = 0
        total_market_value = 0
        position_data = []
        
        for symbol, position in portfolio['positions'].items():
            current_price = get_current_price(symbol)
            quantity = position['quantity']
            avg_price = position['avg_price']
            
            cost_value = quantity * avg_price
            market_value = quantity * current_price
            pnl_amount = market_value - cost_value
            pnl_percent = (pnl_amount / cost_value) * 100 if cost_value > 0 else 0
            
            total_cost += cost_value
            total_market_value += market_value
            
            position_data.append({
                'symbol': symbol,
                'market_value': market_value,
                'pnl_amount': pnl_amount,
                'pnl_percent': pnl_percent
            })
        
        # 投资组合概览
        total_pnl = total_market_value - total_cost
        total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("投资成本", f"¥{total_cost:,.2f}")
        with col2:
            st.metric("当前市值", f"¥{total_market_value:,.2f}")
        with col3:
            st.metric("总盈亏", f"¥{total_pnl:,.2f}", f"{total_pnl_percent:+.2f}%")
        with col4:
            st.metric("现金余额", f"¥{portfolio['cash']:,.2f}")
        
        # 持仓分布图
        if len(position_data) > 0:
            st.markdown("#### 📊 持仓分布")
            
            # 创建饼图
            symbols = [item['symbol'] for item in position_data]
            values = [item['market_value'] for item in position_data]
            
            fig = go.Figure(data=[go.Pie(
                labels=symbols, 
                values=values, 
                hole=.3,
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig.update_layout(
                title="持仓市值分布",
                height=500,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 盈亏分析
            st.markdown("#### 📈 盈亏分析")
            
            profitable_positions = [p for p in position_data if p['pnl_amount'] > 0]
            loss_positions = [p for p in position_data if p['pnl_amount'] < 0]
        
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("盈利品种", f"{len(profitable_positions)}个")
            with col2:
                st.metric("亏损品种", f"{len(loss_positions)}个")
            with col3:
                win_rate = (len(profitable_positions) / len(position_data)) * 100 if position_data else 0
                st.metric("胜率", f"{win_rate:.1f}%")
    else:
        st.info("📦 暂无持仓数据")
    
    # 数据导出功能
    st.markdown("### 📤 数据导出")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 导出持仓数据", use_container_width=True):
            if portfolio['positions']:
                # 创建持仓数据DataFrame
                export_data = []
                for symbol, position in portfolio['positions'].items():
                    current_price = get_current_price(symbol)
                    quantity = position['quantity']
                    avg_price = position['avg_price']
                    market_value = quantity * current_price
                    cost_value = quantity * avg_price
                    pnl_amount = market_value - cost_value
                    pnl_percent = (pnl_amount / cost_value) * 100 if cost_value > 0 else 0
                    
                    export_data.append({
                        '标的名称': symbol,
                        '持有数量': quantity,
                        '平均成本': avg_price,
                        '当前价格': current_price,
                        '成本价值': cost_value,
                        '市场价值': market_value,
                        '盈亏金额': pnl_amount,
                        '盈亏比例': pnl_percent
                    })
                
                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="下载持仓数据CSV",
                    data=csv,
                    file_name=f"持仓数据_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("暂无持仓数据可导出")
    
    with col2:
        if st.button("📜 导出交易历史", use_container_width=True):
            if portfolio['trade_history']:
                df = pd.DataFrame(portfolio['trade_history'])
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="下载交易历史CSV",
                    data=csv,
                    file_name=f"交易历史_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("暂无交易历史可导出")
    
    with col3:
        if st.button("💾 备份所有数据", use_container_width=True):
            # 创建完整的数据备份
            backup_data = {
                'user_info': user,
                'portfolio': portfolio,
                'export_time': datetime.now().isoformat()
            }
            
            import json
            json_data = json.dumps(backup_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="下载完整备份JSON",
                data=json_data,
                file_name=f"数据备份_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# 智能仓位分析函数
def analyze_position_with_kline(symbol, position_info, portfolio_total_value):
    """基于K线分析的智能仓位建议"""
    try:
        # 获取该标的的数据源URL
        symbol_url = None
        for category_items in DATA_SOURCES.values():
            if symbol in category_items:
                symbol_url = category_items[symbol]
                break
        
        if not symbol_url:
            return {
                'status': 'error',
                'message': '无法找到数据源',
                'suggestion': '无法分析',
                'risk_level': 'unknown'
            }
        
        # 获取最近30天的K线数据进行分析
        current_time = datetime.now()
        end_date = current_time.strftime('%Y-%m-%d')
        start_date = (current_time - timedelta(days=30)).strftime('%Y-%m-%d')
        
        kline_df = get_kline(symbol_url, start_date, end_date)
        
        if kline_df.empty:
            return {
                'status': 'error',
                'message': '无法获取K线数据',
                'suggestion': '数据不足，建议谨慎操作',
                'risk_level': 'high'
            }
        
        # 计算技术指标
        kline_df = calculate_technical_indicators_talib(kline_df)
        kline_df = analyze_trading_signals(kline_df)
        
        # 获取最新数据
        latest_data = kline_df.iloc[-1]
        current_price = latest_data['close']
        
        # 计算持仓信息
        quantity = position_info['quantity']
        avg_price = position_info['avg_price']
        position_value = quantity * current_price
        position_cost = quantity * avg_price
        position_pnl = position_value - position_cost
        position_pnl_percent = (position_pnl / position_cost) * 100 if position_cost > 0 else 0
        
        # 计算仓位占比
        position_weight = (position_value / portfolio_total_value) * 100 if portfolio_total_value > 0 else 0
        
        # 技术分析指标
        rsi = latest_data.get('rsi', 50)
        macd = latest_data.get('macd', 0)
        trend_status = latest_data.get('trend_status', '未知')
        signal = latest_data.get('signal', 0)
        
        # 价格相对MA的位置
        ma5 = latest_data.get('ma5', current_price)
        ma10 = latest_data.get('ma10', current_price)
        ma20 = latest_data.get('ma20', current_price)
        ma60 = latest_data.get('ma60', current_price)
        
        # 计算价格变化
        if len(kline_df) >= 7:
            price_7d_ago = kline_df.iloc[-7]['close']
            price_change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
        else:
            price_change_7d = 0
        
        if len(kline_df) >= 30:
            price_30d_ago = kline_df.iloc[0]['close']
            price_change_30d = ((current_price - price_30d_ago) / price_30d_ago) * 100
        else:
            price_change_30d = 0
        
        # 计算短期涨幅（基于回测参数bias_th=7%）
        if len(kline_df) >= 3:
            price_3d_ago = kline_df.iloc[-3]['close']
            price_change_3d = ((current_price - price_3d_ago) / price_3d_ago) * 100
        else:
            price_change_3d = 0
        
        if len(kline_df) >= 5:
            price_5d_ago = kline_df.iloc[-5]['close']
            price_change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
        else:
            price_change_5d = 0
        
        # 计算相对MA5的偏离度（对应回测系统的bias参数）
        ma5_bias = ((current_price / ma5) - 1) * 100 if ma5 > 0 else 0
        
        # 成交量分析
        volume_analysis = analyze_volume_price_relationship(kline_df)
        
        # 检测趋势反转信号（更精确的判断）
        trend_reversal = False
        reversal_type = ""
        
        # 检查MA5下穿MA10（明确的趋势反转信号）
        if len(kline_df) >= 2:
            ma5_current = latest_data.get('ma5', current_price)
            ma10_current = latest_data.get('ma10', current_price)
            ma5_prev = kline_df.iloc[-2].get('ma5', current_price)
            ma10_prev = kline_df.iloc[-2].get('ma10', current_price)
            
            # MA5下穿MA10
            if ma5_current < ma10_current and ma5_prev >= ma10_prev:
                trend_reversal = True
                reversal_type = "MA5下穿MA10"
            
            # 价格跌破MA20且MA20开始下行
            if (current_price < ma20 and 
                kline_df.iloc[-2]['close'] >= kline_df.iloc[-2].get('ma20', current_price) and
                ma20 < kline_df.iloc[-2].get('ma20', current_price)):
                trend_reversal = True
                reversal_type = "跌破MA20且MA20下行"
        
        # 检测震荡行情（连续多日在窄幅区间内波动）
        is_sideways = False
        if len(kline_df) >= 10:
            recent_10d = kline_df.tail(10)
            high_price = recent_10d['close'].max()
            low_price = recent_10d['close'].min()
            price_range = ((high_price - low_price) / low_price) * 100
            
            # 如果10日内价格波动小于5%，认为是震荡行情
            if price_range < 5:
                is_sideways = True
        
        # 基于回测参数的快速涨幅判断
        # bias_th=7%: 相对MA5偏离超过7%考虑出货
        # sell_drop_th=-5%: 3日跌幅超过5%触发止损
        rapid_rise_signal = False
        rapid_rise_type = ""
        
        # 1. 相对MA5偏离度超过7%（对应回测系统的bias_th参数）
        if ma5_bias > 7:
            rapid_rise_signal = True
            rapid_rise_type = f"相对MA5偏离{ma5_bias:.1f}%"
        
        # 2. 短期快速上涨（3日涨幅>10%或5日涨幅>15%）
        elif price_change_3d > 10:
            rapid_rise_signal = True
            rapid_rise_type = f"3日快速上涨{price_change_3d:.1f}%"
        elif price_change_5d > 15:
            rapid_rise_signal = True
            rapid_rise_type = f"5日快速上涨{price_change_5d:.1f}%"
        
        # 3. 7日涨幅超过20%（异常快速上涨）
        elif price_change_7d > 20:
            rapid_rise_signal = True
            rapid_rise_type = f"7日异常上涨{price_change_7d:.1f}%"
        
        # 综合分析和建议生成（更激进的策略）
        suggestions = []
        risk_level = 'medium'
        action_suggestion = '持有观望'
        
        # 1. 仓位占比分析（更宽松的标准）
        if position_weight > 40:
            suggestions.append(f"⚠️ 仓位过重({position_weight:.1f}%)，建议适度减仓分散风险")
            risk_level = 'high'
        elif position_weight > 30:
            suggestions.append(f"🟡 仓位较重({position_weight:.1f}%)，注意风险控制")
        elif position_weight < 8:
            suggestions.append(f"🟢 仓位较轻({position_weight:.1f}%)，可考虑适度加仓")
        
        # 2. 快速涨幅出货分析（基于回测参数）
        if rapid_rise_signal:
            if volume_analysis['volume_trend'] == 'increasing':
                suggestions.append(f"🚀 {rapid_rise_type}且成交量放大，建议分批出货锁定利润")
                action_suggestion = '分批减仓'
                risk_level = 'high'
            elif volume_analysis['volume_trend'] == 'decreasing':
                suggestions.append(f"⚠️ {rapid_rise_type}但成交量萎缩，可能是虚假突破，建议减仓")
                action_suggestion = '考虑减仓'
            else:
                suggestions.append(f"🟡 {rapid_rise_type}，成交量正常，建议部分止盈")
                action_suggestion = '考虑减仓'
        
        # 3. 激进盈利策略分析
        if position_pnl_percent > 30:
            if trend_reversal or rapid_rise_signal:
                suggestions.append(f"💰 盈利丰厚({position_pnl_percent:+.1f}%)且出现出货信号，建议减仓止盈")
                if action_suggestion not in ['分批减仓']:
                    action_suggestion = '分批减仓'
            else:
                suggestions.append(f"💰 盈利丰厚({position_pnl_percent:+.1f}%)但趋势未反转，可继续持有")
                if action_suggestion == '持有观望':
                    action_suggestion = '持有观望'
        elif position_pnl_percent > 15:
            if trend_reversal or rapid_rise_signal:
                suggestions.append(f"📈 盈利良好({position_pnl_percent:+.1f}%)且出现出货信号，考虑部分止盈")
                if action_suggestion not in ['分批减仓', '考虑减仓']:
                    action_suggestion = '考虑减仓'
            else:
                suggestions.append(f"📈 盈利良好({position_pnl_percent:+.1f}%)且趋势未反转，建议继续持有")
        elif position_pnl_percent < -20:
            suggestions.append(f"📉 亏损严重({position_pnl_percent:+.1f}%)，需要止损")
            risk_level = 'high'
            action_suggestion = '考虑止损'
        elif position_pnl_percent < -10:
            if trend_reversal:
                suggestions.append(f"⚠️ 出现亏损({position_pnl_percent:+.1f}%)且趋势反转，建议止损")
                action_suggestion = '考虑止损'
            else:
                suggestions.append(f"⚠️ 出现亏损({position_pnl_percent:+.1f}%)但趋势未明确反转，可观望")
        
        # 4. 震荡行情处理
        if is_sideways:
            suggestions.append(f"📊 长期震荡行情(10日波动<5%)，建议空仓等待明确方向")
            if action_suggestion == '持有观望':
                action_suggestion = '考虑空仓'
        
        # 5. 成交量分析
        if volume_analysis['volume_price_divergence']:
            suggestions.append(f"⚠️ 量价背离：{volume_analysis['divergence_type']}，需要警惕")
            if risk_level == 'low':
                risk_level = 'medium'
        
        if volume_analysis['volume_trend'] == 'increasing' and price_change_7d > 0:
            suggestions.append("🚀 价涨量增，趋势健康")
        elif volume_analysis['volume_trend'] == 'decreasing' and price_change_7d > 0:
            suggestions.append("⚠️ 价涨量缩，上涨乏力")
        
        # 6. 技术指标分析（更注重趋势）
        if trend_status in ["强势上涨", "震荡上涨"]:
            if not trend_reversal and not rapid_rise_signal:
                suggestions.append(f"🚀 主趋势向好({trend_status})且无出货信号，建议持有或加仓")
                if action_suggestion == '持有观望' and position_weight < 25:
                    action_suggestion = '持有或加仓'
            else:
                suggestions.append(f"⚠️ 主趋势向好但出现出货信号，谨慎操作")
        elif trend_status == "高位震荡":
            suggestions.append(f"📊 趋势不明({trend_status})，建议观望")
        else:
            suggestions.append(f"📉 趋势偏弱({trend_status})，建议减仓")
            if action_suggestion not in ['分批减仓', '考虑止损', '考虑空仓']:
                action_suggestion = '考虑减仓'
        
        # 7. RSI分析（更宽松的超买超卖标准）
        if rsi > 80:
            suggestions.append(f"⚠️ RSI极度超买({rsi:.1f})，高位风险大")
            risk_level = 'high'
        elif rsi > 75:
            suggestions.append(f"🟡 RSI超买({rsi:.1f})，注意回调风险")
        elif rsi < 20:
            suggestions.append(f"💎 RSI极度超卖({rsi:.1f})，强烈反弹机会")
            if position_weight < 20:
                action_suggestion = '考虑加仓'
        elif rsi < 25:
            suggestions.append(f"🟢 RSI超卖({rsi:.1f})，关注反弹机会")
        
        # 8. 价格变化分析
        if price_change_7d > 20:
            suggestions.append(f"🔥 7日大涨({price_change_7d:+.1f}%)，注意高位风险")
        elif price_change_7d < -20:
            suggestions.append(f"❄️ 7日大跌({price_change_7d:+.1f}%)，关注反弹机会")
        
        # 9. 交易信号分析
        if signal > 0:
            suggestions.append("🟢 技术指标显示买入信号")
            if action_suggestion == '持有观望' and position_weight < 25 and not rapid_rise_signal:
                action_suggestion = '考虑加仓'
        elif signal < 0:
            suggestions.append("🔴 技术指标显示卖出信号")
            if not trend_reversal and not rapid_rise_signal:
                suggestions.append("但无明确出货信号，可继续观察")
            else:
                action_suggestion = '考虑减仓'
        
        # 10. 均线分析
        if current_price > ma60 and ma5 > ma10:
            suggestions.append("✅ 价格站上60日均线且短期均线向好")
        elif current_price < ma60:
            suggestions.append("⚠️ 价格跌破60日均线，趋势偏弱")
        
        # 风险等级评估（调整标准）
        if risk_level != 'high':
            risk_factors = 0
            if position_weight > 35: risk_factors += 1
            if position_pnl_percent < -15: risk_factors += 1
            if rsi > 80 or rsi < 20: risk_factors += 1
            if trend_status in ["下跌趋势"]: risk_factors += 1
            if trend_reversal: risk_factors += 1
            if rapid_rise_signal: risk_factors += 1
            if volume_analysis['volume_price_divergence']: risk_factors += 1
            if abs(price_change_7d) > 15: risk_factors += 1
            
            if risk_factors >= 4:
                risk_level = 'high'
            elif risk_factors >= 2:
                risk_level = 'medium'
            else:
                risk_level = 'low'
        
        return {
            'status': 'success',
            'symbol': symbol,
            'current_price': current_price,
            'position_weight': position_weight,
            'position_pnl_percent': position_pnl_percent,
            'price_change_3d': price_change_3d,
            'price_change_5d': price_change_5d,
            'price_change_7d': price_change_7d,
            'price_change_30d': price_change_30d,
            'ma5_bias': ma5_bias,
            'rsi': rsi,
            'trend_status': trend_status,
            'trend_reversal': trend_reversal,
            'reversal_type': reversal_type,
            'rapid_rise_signal': rapid_rise_signal,
            'rapid_rise_type': rapid_rise_type,
            'is_sideways': is_sideways,
            'volume_analysis': volume_analysis,
            'suggestions': suggestions,
            'action_suggestion': action_suggestion,
            'risk_level': risk_level,
            'technical_score': len([s for s in suggestions if '🟢' in s or '🚀' in s or '💎' in s]) - len([s for s in suggestions if '🔴' in s or '⚠️' in s or '📉' in s])
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'分析出错: {str(e)}',
            'suggestion': '无法分析，建议谨慎操作',
            'risk_level': 'high'
        }

# 成交量与价格关系分析函数
def analyze_volume_price_relationship(kline_df):
    """分析成交量与价格的关系"""
    try:
        if len(kline_df) < 10:
            return {
                'volume_trend': 'insufficient_data',
                'volume_price_divergence': False,
                'divergence_type': '',
                'volume_strength': 'normal'
            }
        
        # 计算最近5日和前5日的平均成交量
        recent_volume = kline_df['volume'].tail(5).mean()
        previous_volume = kline_df['volume'].iloc[-10:-5].mean()
        
        # 判断成交量趋势
        if recent_volume > previous_volume * 1.5:
            volume_trend = 'increasing'
        elif recent_volume < previous_volume * 0.7:
            volume_trend = 'decreasing'
        else:
            volume_trend = 'stable'
        
        # 计算价格变化
        recent_price_change = (kline_df['close'].iloc[-1] / kline_df['close'].iloc[-5] - 1) * 100
        
        # 检测量价背离
        volume_price_divergence = False
        divergence_type = ""
        
        # 价涨量缩（顶背离）
        if recent_price_change > 3 and volume_trend == 'decreasing':
            volume_price_divergence = True
            divergence_type = "价涨量缩，可能见顶"
        
        # 价跌量增（底背离）
        elif recent_price_change < -3 and volume_trend == 'increasing':
            volume_price_divergence = True
            divergence_type = "价跌量增，可能见底"
        
        # 判断成交量强度
        avg_volume = kline_df['volume'].mean()
        if recent_volume > avg_volume * 2:
            volume_strength = 'very_high'
        elif recent_volume > avg_volume * 1.5:
            volume_strength = 'high'
        elif recent_volume < avg_volume * 0.5:
            volume_strength = 'low'
        else:
            volume_strength = 'normal'
        
        return {
            'volume_trend': volume_trend,
            'volume_price_divergence': volume_price_divergence,
            'divergence_type': divergence_type,
            'volume_strength': volume_strength,
            'recent_volume_ratio': recent_volume / previous_volume if previous_volume > 0 else 1
        }
        
    except Exception as e:
        return {
            'volume_trend': 'error',
            'volume_price_divergence': False,
            'divergence_type': f'分析出错: {str(e)}',
            'volume_strength': 'normal'
        }

# 总仓位风险分析函数
def analyze_total_position_risk(portfolio):
    """分析总仓位风险"""
    try:
        total_cash = portfolio['cash']
        initial_capital = 100000  # 初始资金10万
        invested_amount = initial_capital - total_cash
        investment_ratio = (invested_amount / initial_capital) * 100
        
        # 计算当前总市值
        total_market_value = 0
        for symbol, position in portfolio['positions'].items():
            current_price = get_current_price(symbol)
            total_market_value += position['quantity'] * current_price
        
        # 计算总盈亏
        total_pnl = total_market_value - invested_amount
        total_pnl_percent = (total_pnl / invested_amount) * 100 if invested_amount > 0 else 0
        
        # 风险等级评估
        risk_level = 'low'
        risk_suggestions = []
        
        # 1. 资金使用率分析
        if investment_ratio > 90:
            risk_level = 'high'
            risk_suggestions.append("⚠️ 资金使用率过高(>90%)，缺乏应急资金")
        elif investment_ratio > 75:
            risk_level = 'medium'
            risk_suggestions.append("🟡 资金使用率较高(>75%)，建议保留更多现金")
        elif investment_ratio < 30:
            risk_suggestions.append("💰 资金使用率较低(<30%)，可考虑增加投资")
        else:
            risk_suggestions.append("✅ 资金使用率合理，风险可控")
        
        # 2. 总盈亏分析
        if total_pnl_percent < -20:
            risk_level = 'high'
            risk_suggestions.append(f"📉 总体亏损严重({total_pnl_percent:+.1f}%)，需要调整策略")
        elif total_pnl_percent < -10:
            if risk_level != 'high':
                risk_level = 'medium'
            risk_suggestions.append(f"⚠️ 总体出现亏损({total_pnl_percent:+.1f}%)，需要关注")
        elif total_pnl_percent > 20:
            risk_suggestions.append(f"💰 总体盈利丰厚({total_pnl_percent:+.1f}%)，可考虑部分止盈")
        
        # 3. 持仓集中度分析
        if len(portfolio['positions']) == 1:
            risk_level = 'high'
            risk_suggestions.append("⚠️ 持仓过度集中(仅1个标的)，风险极高")
        elif len(portfolio['positions']) <= 2:
            if risk_level != 'high':
                risk_level = 'medium'
            risk_suggestions.append("🟡 持仓集中度较高(≤2个标的)，建议分散投资")
        elif len(portfolio['positions']) >= 8:
            risk_suggestions.append("📊 持仓过于分散(≥8个标的)，可能影响收益")
        
        # 4. 现金比例建议
        cash_ratio = (total_cash / initial_capital) * 100
        if cash_ratio < 10:
            risk_suggestions.append("💸 现金比例过低(<10%)，建议保留应急资金")
        elif cash_ratio > 50:
            risk_suggestions.append("💰 现金比例较高(>50%)，可考虑增加投资")
        
        return {
            'total_cash': total_cash,
            'invested_amount': invested_amount,
            'investment_ratio': investment_ratio,
            'total_market_value': total_market_value,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'cash_ratio': cash_ratio,
            'position_count': len(portfolio['positions']),
            'risk_level': risk_level,
            'risk_suggestions': risk_suggestions
        }
        
    except Exception as e:
        return {
            'error': f'总仓位分析出错: {str(e)}',
            'risk_level': 'high'
        }

# 市场分析函数
def analyze_market_sentiment(df):
    """分析市场情绪和资金流向"""
    if df.empty or len(df) < 20:
        return {}
    
    latest = df.iloc[-1]
    recent_5 = df.tail(5)
    recent_20 = df.tail(20)
    
    analysis = {}
    
    # 1. 资金流向分析
    money_flow_analysis = {}
    
    # OBV趋势分析
    if 'obv' in df.columns:
        obv_trend = "上升" if latest['obv'] > df['obv'].iloc[-5] else "下降"
        obv_strength = abs(latest['obv'] - df['obv'].iloc[-5]) / df['volume'].tail(5).sum()
        money_flow_analysis['obv_trend'] = obv_trend
        money_flow_analysis['obv_strength'] = obv_strength
    
    # MFI资金流量指数分析
    if 'mfi' in df.columns:
        mfi_value = latest['mfi']
        if mfi_value > 80:
            mfi_status = "资金严重超买"
        elif mfi_value > 60:
            mfi_status = "资金超买"
        elif mfi_value < 20:
            mfi_status = "资金严重超卖"
        elif mfi_value < 40:
            mfi_status = "资金超卖"
        else:
            mfi_status = "资金流向正常"
        money_flow_analysis['mfi_status'] = mfi_status
        money_flow_analysis['mfi_value'] = mfi_value
    
    # 成交量分析
    volume_analysis = {}
    if 'volume_ratio' in df.columns:
        volume_ratio = latest['volume_ratio']
        if volume_ratio > 2:
            volume_status = "成交量异常放大"
        elif volume_ratio > 1.5:
            volume_status = "成交量明显放大"
        elif volume_ratio < 0.5:
            volume_status = "成交量萎缩"
        else:
            volume_status = "成交量正常"
        volume_analysis['status'] = volume_status
        volume_analysis['ratio'] = volume_ratio
    
    # 价量配合分析
    price_change_5d = (latest['close'] - recent_5['close'].iloc[0]) / recent_5['close'].iloc[0]
    volume_change_5d = recent_5['volume'].mean() / df['volume'].tail(20).mean()
    
    if price_change_5d > 0 and volume_change_5d > 1.2:
        price_volume_relation = "价涨量增，趋势健康"
    elif price_change_5d > 0 and volume_change_5d < 0.8:
        price_volume_relation = "价涨量缩，上涨乏力"
    elif price_change_5d < 0 and volume_change_5d > 1.2:
        price_volume_relation = "价跌量增，可能见底"
    elif price_change_5d < 0 and volume_change_5d < 0.8:
        price_volume_relation = "价跌量缩，下跌放缓"
    else:
        price_volume_relation = "价量关系正常"
    
    volume_analysis['price_volume_relation'] = price_volume_relation
    
    analysis['money_flow'] = money_flow_analysis
    analysis['volume'] = volume_analysis
    
    # 2. 技术指标综合分析
    technical_analysis = {}
    
    # 多空力量对比
    bullish_signals = 0
    bearish_signals = 0
    
    # RSI分析
    if 'rsi' in df.columns:
        rsi = latest['rsi']
        if rsi > 70:
            bearish_signals += 1
            rsi_signal = "超买"
        elif rsi < 30:
            bullish_signals += 1
            rsi_signal = "超卖"
        else:
            rsi_signal = "正常"
        technical_analysis['rsi_signal'] = rsi_signal
    
    # MACD分析
    if 'macd' in df.columns and 'macd_signal' in df.columns:
        macd_bullish = latest['macd'] > latest['macd_signal']
        macd_histogram_trend = latest['macd_histogram'] > df['macd_histogram'].iloc[-2]
        
        if macd_bullish and macd_histogram_trend:
            bullish_signals += 2
            macd_signal = "强烈看多"
        elif macd_bullish:
            bullish_signals += 1
            macd_signal = "看多"
        elif not macd_bullish and not macd_histogram_trend:
            bearish_signals += 2
            macd_signal = "强烈看空"
        else:
            bearish_signals += 1
            macd_signal = "看空"
        technical_analysis['macd_signal'] = macd_signal
    
    # KDJ分析
    if all(col in df.columns for col in ['k', 'd', 'j']):
        k, d, j = latest['k'], latest['d'], latest['j']
        if k > 80 and d > 80:
            bearish_signals += 1
            kdj_signal = "超买"
        elif k < 20 and d < 20:
            bullish_signals += 1
            kdj_signal = "超卖"
        elif k > d:
            bullish_signals += 1
            kdj_signal = "金叉看多"
        else:
            bearish_signals += 1
            kdj_signal = "死叉看空"
        technical_analysis['kdj_signal'] = kdj_signal
    
    # 布林带分析
    if 'bb_position' in df.columns:
        bb_pos = latest['bb_position']
        if bb_pos > 0.8:
            bearish_signals += 1
            bb_signal = "接近上轨，超买"
        elif bb_pos < 0.2:
            bullish_signals += 1
            bb_signal = "接近下轨，超卖"
        else:
            bb_signal = "在布林带中轨附近"
        technical_analysis['bb_signal'] = bb_signal
    
    # 综合技术信号
    if bullish_signals > bearish_signals + 1:
        overall_signal = "多头占优"
    elif bearish_signals > bullish_signals + 1:
        overall_signal = "空头占优"
    else:
        overall_signal = "多空平衡"
    
    technical_analysis['overall_signal'] = overall_signal
    technical_analysis['bullish_count'] = bullish_signals
    technical_analysis['bearish_count'] = bearish_signals
    
    analysis['technical'] = technical_analysis
    
    # 3. 市场情绪分析
    sentiment_analysis = {}
    
    # 波动率分析
    if 'atr' in df.columns:
        current_atr = latest['atr']
        avg_atr = df['atr'].tail(20).mean()
        volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1
        
        if volatility_ratio > 1.5:
            volatility_status = "波动率异常高，市场恐慌"
        elif volatility_ratio > 1.2:
            volatility_status = "波动率偏高，市场活跃"
        elif volatility_ratio < 0.7:
            volatility_status = "波动率偏低，市场平静"
        else:
            volatility_status = "波动率正常"
        
        sentiment_analysis['volatility_status'] = volatility_status
        sentiment_analysis['volatility_ratio'] = volatility_ratio
    
    # 趋势强度分析
    ma_alignment = 0
    if all(col in df.columns for col in ['ma5', 'ma10', 'ma20', 'ma60']):
        mas = [latest['ma5'], latest['ma10'], latest['ma20'], latest['ma60']]
        # 过滤掉None值，确保所有值都是有效数字
        valid_mas = [ma for ma in mas if ma is not None and not pd.isna(ma)]
        
        if len(valid_mas) == 4:  # 只有当所有移动平均线都有效时才进行分析
            if valid_mas == sorted(valid_mas, reverse=True):  # 多头排列
                ma_alignment = 1
                trend_strength = "强势上涨趋势"
            elif valid_mas == sorted(valid_mas):  # 空头排列
                ma_alignment = -1
                trend_strength = "强势下跌趋势"
            else:
                ma_alignment = 0
                trend_strength = "震荡整理"
        else:
            ma_alignment = 0
            trend_strength = "数据不足，无法判断趋势"
        
        sentiment_analysis['trend_strength'] = trend_strength
        sentiment_analysis['ma_alignment'] = ma_alignment
    
    # 市场情绪综合评分 (-100 到 100)
    sentiment_score = 0
    sentiment_score += (bullish_signals - bearish_signals) * 15
    sentiment_score += ma_alignment * 20
    
    if 'mfi' in df.columns:
        mfi = latest['mfi']
        if mfi > 80:
            sentiment_score -= 15
        elif mfi < 20:
            sentiment_score += 15
    
    if 'volume_ratio' in df.columns and price_change_5d > 0:
        if latest['volume_ratio'] > 1.5:
            sentiment_score += 10
    
    sentiment_score = max(-100, min(100, sentiment_score))
    
    if sentiment_score > 60:
        sentiment_level = "极度乐观"
    elif sentiment_score > 30:
        sentiment_level = "乐观"
    elif sentiment_score > -30:
        sentiment_level = "中性"
    elif sentiment_score > -60:
        sentiment_level = "悲观"
    else:
        sentiment_level = "极度悲观"
    
    sentiment_analysis['score'] = sentiment_score
    sentiment_analysis['level'] = sentiment_level
    
    analysis['sentiment'] = sentiment_analysis
    
    return analysis

def generate_trading_recommendations(df, market_analysis):
    """基于市场分析生成交易建议"""
    recommendations = []
    risk_level = "中等"
    confidence = 50
    
    if not market_analysis:
        return {
            'recommendations': ["数据不足，建议观望"],
            'risk_level': "高",
            'confidence': 30,
            'action': "观望"
        }
    
    # 基于技术分析的建议
    technical = market_analysis.get('technical', {})
    sentiment = market_analysis.get('sentiment', {})
    money_flow = market_analysis.get('money_flow', {})
    volume = market_analysis.get('volume', {})
    
    # 确定主要操作方向
    bullish_count = technical.get('bullish_count', 0)
    bearish_count = technical.get('bearish_count', 0)
    sentiment_score = sentiment.get('score', 0)
    
    if bullish_count > bearish_count + 1 and sentiment_score > 30:
        primary_action = "买入"
        confidence += 20
    elif bearish_count > bullish_count + 1 and sentiment_score < -30:
        primary_action = "卖出"
        confidence += 20
    else:
        primary_action = "观望"
    
    # 生成具体建议
    if primary_action == "买入":
        recommendations.append("📈 技术指标显示多头信号，建议逢低买入")
        
        # 买入时机建议
        if 'rsi_signal' in technical and technical['rsi_signal'] == "超卖":
            recommendations.append("💎 RSI显示超卖，是较好的买入时机")
            confidence += 10
        
        if 'bb_signal' in technical and "下轨" in technical['bb_signal']:
            recommendations.append("📊 价格接近布林带下轨，支撑较强")
            confidence += 10
        
        # 资金流向确认
        if money_flow.get('obv_trend') == "上升":
            recommendations.append("💰 资金流入明显，多头趋势得到确认")
            confidence += 15
        
        risk_level = "中低"
        
    elif primary_action == "卖出":
        recommendations.append("📉 技术指标显示空头信号，建议减仓或止损")
        
        # 卖出时机建议
        if 'rsi_signal' in technical and technical['rsi_signal'] == "超买":
            recommendations.append("⚠️ RSI显示超买，注意回调风险")
            confidence += 10
        
        if 'bb_signal' in technical and "上轨" in technical['bb_signal']:
            recommendations.append("📊 价格接近布林带上轨，阻力较强")
            confidence += 10
        
        # 资金流向确认
        if money_flow.get('obv_trend') == "下降":
            recommendations.append("💸 资金流出明显，空头趋势得到确认")
            confidence += 15
        
        risk_level = "中高"
        
    else:  # 观望
        recommendations.append("⚖️ 多空信号混杂，建议观望等待明确方向")
        
        if sentiment.get('trend_strength') == "震荡整理":
            recommendations.append("📊 市场处于震荡整理阶段，等待突破")
        
        risk_level = "中等"
    
    # 成交量分析建议
    volume_relation = volume.get('price_volume_relation', '')
    if "价涨量增" in volume_relation:
        recommendations.append("🚀 价涨量增配合良好，趋势可持续性强")
        if primary_action == "买入":
            confidence += 10
    elif "价涨量缩" in volume_relation:
        recommendations.append("⚠️ 价涨量缩，上涨动能不足，注意风险")
        if primary_action == "买入":
            confidence -= 10
    elif "价跌量增" in volume_relation:
        recommendations.append("💎 价跌量增，可能是恐慌性抛售，关注反弹机会")
    
    # 波动率建议
    volatility_status = sentiment.get('volatility_status', '')
    if "异常高" in volatility_status:
        recommendations.append("⚡ 波动率异常高，建议降低仓位，控制风险")
        risk_level = "高"
        confidence -= 15
    elif "偏低" in volatility_status:
        recommendations.append("😴 波动率偏低，市场缺乏方向，适合观望")
    
    # 资金流量指数建议
    mfi_status = money_flow.get('mfi_status', '')
    if "严重超买" in mfi_status:
        recommendations.append("🔴 资金严重超买，短期回调风险大")
        if primary_action == "买入":
            confidence -= 20
    elif "严重超卖" in mfi_status:
        recommendations.append("🟢 资金严重超卖，反弹机会较大")
        if primary_action == "卖出":
            confidence -= 20
    
    # 限制置信度范围
    confidence = max(30, min(90, confidence))
    
    return {
        'recommendations': recommendations,
        'risk_level': risk_level,
        'confidence': confidence,
        'action': primary_action
    }

def display_kline_chart_with_signals(analysis_df, strategy_result, selected_symbol):
    """显示K线图表和策略信号"""
    try:
        st.markdown("### 📊 K线图表与策略信号")
        
        # 创建综合图表
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=('价格与信号', 'RSI指标', '仓位变化', '策略收益'),
            vertical_spacing=0.08,
            row_heights=[0.5, 0.2, 0.15, 0.15]
        )
        
        # K线图
        fig.add_trace(
            go.Candlestick(
                x=analysis_df.index,
                open=analysis_df['open'],
                high=analysis_df['high'],
                low=analysis_df['low'],
                close=analysis_df['close'],
                name='K线'
            ),
            row=1, col=1
        )
        
        # 移动平均线
        if 'ma5' in analysis_df.columns:
            fig.add_trace(go.Scatter(x=analysis_df.index, y=analysis_df['ma5'], name='MA5', line=dict(color='orange', width=1)), row=1, col=1)
        if 'ma10' in analysis_df.columns:
            fig.add_trace(go.Scatter(x=analysis_df.index, y=analysis_df['ma10'], name='MA10', line=dict(color='blue', width=1)), row=1, col=1)
        if 'ma20' in analysis_df.columns:
            fig.add_trace(go.Scatter(x=analysis_df.index, y=analysis_df['ma20'], name='MA20', line=dict(color='red', width=1)), row=1, col=1)
        
        # 买卖信号
        buy_signals = strategy_result[strategy_result['buy'] > 0]
        sell_signals = strategy_result[strategy_result['sell'] > 0]
        
        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(x=buy_signals.index, y=buy_signals['price'], 
                          mode='markers', name='买入信号',
                          marker=dict(color='green', size=12, symbol='triangle-up')),
                row=1, col=1
            )
        
        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(x=sell_signals.index, y=sell_signals['price'], 
                          mode='markers', name='卖出信号',
                          marker=dict(color='red', size=12, symbol='triangle-down')),
                row=1, col=1
            )
        
        # RSI指标
        if 'rsi' in analysis_df.columns:
            fig.add_trace(go.Scatter(x=analysis_df.index, y=analysis_df['rsi'], name='RSI', line=dict(color='purple')), row=2, col=1)
        
        # 仓位变化
        fig.add_trace(go.Scatter(x=strategy_result.index, y=strategy_result['pos'], name='仓位', line=dict(color='blue')), row=3, col=1)
        
        # 策略收益
        cumulative_returns = (1 + strategy_result['ret']).cumprod()
        fig.add_trace(go.Scatter(x=strategy_result.index, y=cumulative_returns, name='累计收益', line=dict(color='green')), row=4, col=1)
        
        fig.update_layout(
            height=1000,
            title=f"{selected_symbol} - 智能策略分析",
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 当前交易建议（基于策略结果）
        st.markdown("### 💡 当前交易建议")
        
        if not strategy_result.empty:
            latest_signal = strategy_result.iloc[-1]
            current_price = latest_signal['price']
            current_pos = latest_signal['pos']
            latest_buy = latest_signal['buy']
            latest_sell = latest_signal['sell']
            
            # 交易建议卡片
            if latest_buy > 0:
                st.markdown(f"""
                <div class="success-box">
                    <h4>🟢 买入信号</h4>
                    <p><strong>建议操作：</strong>买入 {latest_buy:.1f} 仓位</p>
                    <p><strong>当前价格：</strong>¥{current_price:.2f}</p>
                    <p><strong>策略依据：</strong>基于优化后的最佳参数，当前市场条件符合买入条件</p>
                </div>
                """, unsafe_allow_html=True)
            elif latest_sell > 0:
                st.markdown(f"""
                <div class="warning-box">
                    <h4>🔴 卖出信号</h4>
                    <p><strong>建议操作：</strong>卖出 {latest_sell:.1f} 仓位</p>
                    <p><strong>当前价格：</strong>¥{current_price:.2f}</p>
                    <p><strong>策略依据：</strong>触发止损或止盈条件，建议减仓</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>⚪ 观望信号</h4>
                    <p><strong>建议操作：</strong>暂时观望</p>
                    <p><strong>当前价格：</strong>¥{current_price:.2f}</p>
                    <p><strong>当前仓位：</strong>{current_pos:.1f}</p>
                    <p><strong>策略依据：</strong>当前市场条件不符合买入或卖出条件</p>
                </div>
                """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"图表显示出错: {str(e)}")

def display_trading_recommendations(trading_recommendations, advanced=True):
    """显示专业交易建议，支持高级分析"""
    st.markdown("#### 💡 专业交易建议")
    
    if advanced and 'enhanced_recommendations' not in st.session_state:
        # 在此处添加调用增强建议的逻辑
        pass
    
    # 如果有高级推荐且用户选择使用它，则使用它
    recommendations_to_show = trading_recommendations
    
    action = recommendations_to_show.get('action', '观望')
    confidence = recommendations_to_show.get('confidence', 50)
    risk_level = recommendations_to_show.get('risk_level', '中等')
    recommendations = recommendations_to_show.get('recommendations', [])
    
    # 操作建议颜色
    if action == "买入":
        action_color = "#4CAF50"
        action_icon = "📈"
    elif action == "卖出":
        action_color = "#F44336"
        action_icon = "📉"
    else:
        action_color = "#FF9800"
        action_icon = "⚖️"
    
    # 风险等级颜色
    if risk_level == "低" or risk_level == "中低":
        risk_color = "#4CAF50"
    elif risk_level == "高":
        risk_color = "#F44336"
    else:
        risk_color = "#FF9800"
    
    # 使用Streamlit原生组件显示操作建议
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**推荐操作**")
        st.markdown(f"<h3 style='color:{action_color};'>{action_icon} {action}</h3>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("**置信度**")
        st.markdown(f"<h3 style='color:#1976D2;'>{confidence}%</h3>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("**风险等级**")
        st.markdown(f"<h3 style='color:{risk_color};'>{risk_level}</h3>", unsafe_allow_html=True)
    
    # 详细建议
    if recommendations:
        st.markdown("#### 📋 详细建议:")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
    else:
        st.info("暂无详细建议")

# 高级市场情绪分析
def analyze_advanced_market_sentiment(df):
    """增强版市场情绪分析，包含更多维度和机器学习模型集成"""
    # 首先获取基础市场情绪分析
    base_analysis = analyze_market_sentiment(df)
    if not base_analysis or df.empty or len(df) < 30:
        return base_analysis
    
    # 扩展分析结果
    advanced_analysis = base_analysis.copy()
    
    # 1. 增强版趋势识别
    trend_analysis = {}
    
    # 使用新增的ADX指标评估趋势强度
    if 'adx' in df.columns:
        latest_adx = df['adx'].iloc[-1]
        if latest_adx > 30:
            trend_strength = "强趋势"
            trend_analysis['strength_score'] = min(100, latest_adx)
        elif latest_adx > 20:
            trend_strength = "中等趋势"
            trend_analysis['strength_score'] = latest_adx
        else:
            trend_strength = "弱趋势/震荡"
            trend_analysis['strength_score'] = max(0, latest_adx)
        trend_analysis['strength'] = trend_strength
    
    # 检测趋势拐点
    if all(col in df.columns for col in ['ma5', 'ma20', 'ma60']):
        # 短期均线方向
        ma5_direction = 1 if df['ma5'].iloc[-1] > df['ma5'].iloc[-5] else -1
        # 中期均线方向
        ma20_direction = 1 if df['ma20'].iloc[-1] > df['ma20'].iloc[-5] else -1
        # 长期均线方向
        ma60_direction = 1 if df['ma60'].iloc[-1] > df['ma60'].iloc[-10] else -1
        
        # 检测趋势转折点
        if ma5_direction != ma20_direction and ma5_direction == 1:
            trend_analysis['inflection'] = "可能形成上升趋势"
        elif ma5_direction != ma20_direction and ma5_direction == -1:
            trend_analysis['inflection'] = "可能形成下降趋势"
        elif ma5_direction == ma20_direction == ma60_direction == 1:
            trend_analysis['inflection'] = "强势上升趋势确认"
        elif ma5_direction == ma20_direction == ma60_direction == -1:
            trend_analysis['inflection'] = "强势下降趋势确认"
        else:
            trend_analysis['inflection'] = "趋势不明确"
    
    advanced_analysis['trend'] = trend_analysis
    
    # 2. 波动性分析增强
    volatility_analysis = {}
    
    if 'atr' in df.columns and 'close' in df.columns:
        # 计算ATR占收盘价的百分比，更好地衡量波动率
        atr_percent = (df['atr'].iloc[-1] / df['close'].iloc[-1]) * 100
        volatility_analysis['atr_percent'] = atr_percent
        
        # 波动率变化趋势
        recent_atr = df['atr'].tail(10).mean()
        previous_atr = df['atr'].iloc[-20:-10].mean() if len(df) >= 20 else recent_atr
        atr_change = ((recent_atr / previous_atr) - 1) * 100 if previous_atr > 0 else 0
        
        volatility_analysis['change'] = atr_change
        if atr_change > 30:
            volatility_analysis['trend'] = "波动率急剧增加，市场不稳定性上升"
        elif atr_change > 10:
            volatility_analysis['trend'] = "波动率增加，市场活跃度提升"
        elif atr_change < -30:
            volatility_analysis['trend'] = "波动率急剧下降，市场趋于平静"
        elif atr_change < -10:
            volatility_analysis['trend'] = "波动率下降，市场活跃度降低"
        else:
            volatility_analysis['trend'] = "波动率保持稳定"
    
    advanced_analysis['volatility'] = volatility_analysis
    
    # 3. 智能支撑阻力位分析
    support_resistance = {}
    
    # 使用TA-Lib的Pivot Points功能（如果可用）
    if TALIB_AVAILABLE and len(df) > 20:
        try:
            # 使用最近一段时间的数据计算支撑阻力位，而不是单日数据
            recent_data = df.tail(20)  # 使用最近20天数据
            high = recent_data['high'].max()  # 最高价
            low = recent_data['low'].min()    # 最低价
            close = df['close'].iloc[-1]      # 最新收盘价
            
            # 标准Pivot Points计算公式
            pivot = (high + low + close) / 3
            
            # 阻力位计算（应该高于pivot）
            r1 = 2 * pivot - low      # 一级阻力
            r2 = pivot + (high - low) # 二级阻力
            
            # 支撑位计算（应该低于pivot）
            s1 = 2 * pivot - high     # 一级支撑
            s2 = pivot - (high - low) # 二级支撑
            
            # 确保数值的逻辑正确性
            # 阻力位应该 >= pivot，支撑位应该 <= pivot
            if r1 < pivot:
                r1 = pivot + (pivot - s1) / 2
            if r2 < r1:
                r2 = r1 + (high - low) / 2
            if s1 > pivot:
                s1 = pivot - (r1 - pivot) / 2
            if s2 > s1:
                s2 = s1 - (high - low) / 2
            
            support_resistance['pivot'] = pivot
            support_resistance['r1'] = r1
            support_resistance['r2'] = r2
            support_resistance['s1'] = s1
            support_resistance['s2'] = s2
            
            # 当前价格相对位置
            current_price = df['close'].iloc[-1]
            if current_price > r2:
                price_position = "突破二级阻力位，强势上涨"
            elif current_price > r1:
                price_position = "超过一级阻力位，接近二级阻力位"
            elif current_price > pivot:
                price_position = "运行在轴心点与一级阻力位之间"
            elif current_price > s1:
                price_position = "运行在轴心点与一级支撑位之间"
            elif current_price > s2:
                price_position = "低于一级支撑位，接近二级支撑位"
            else:
                price_position = "跌破二级支撑位，弱势下跌"
            
            support_resistance['price_position'] = price_position
        except Exception as e:
            support_resistance['error'] = str(e)
    
    advanced_analysis['support_resistance'] = support_resistance
    
    # 4. 多周期情绪综合评分
    if len(df) >= 60:  # 确保有足够数据点
        # 短期情绪 (10天)
        short_term_df = df.tail(10)
        short_term_change = (short_term_df['close'].iloc[-1] / short_term_df['close'].iloc[0] - 1) * 100
        short_bullish = sum(1 for i in range(1, len(short_term_df)) if short_term_df['close'].iloc[i] > short_term_df['close'].iloc[i-1])
        short_bearish = len(short_term_df) - 1 - short_bullish
        short_score = short_bullish - short_bearish + (short_term_change / 2)
        
        # 中期情绪 (30天)
        medium_term_df = df.tail(30)
        medium_term_change = (medium_term_df['close'].iloc[-1] / medium_term_df['close'].iloc[0] - 1) * 100
        medium_bullish = sum(1 for i in range(1, len(medium_term_df)) if medium_term_df['close'].iloc[i] > medium_term_df['close'].iloc[i-1])
        medium_bearish = len(medium_term_df) - 1 - medium_bullish
        medium_score = medium_bullish - medium_bearish + (medium_term_change / 3)
        
        # 长期情绪 (60天)
        long_term_change = (df['close'].iloc[-1] / df['close'].iloc[-60] - 1) * 100
        long_bullish = sum(1 for i in range(df.shape[0]-59, df.shape[0]) if df['close'].iloc[i] > df['close'].iloc[i-1])
        long_bearish = 59 - long_bullish
        long_score = long_bullish - long_bearish + (long_term_change / 5)
        
        # 综合多周期情绪评分 (加权平均)
        multi_period_score = (short_score * 0.5 + medium_score * 0.3 + long_score * 0.2)
        # 归一化到-100到100之间
        multi_period_score = max(-100, min(100, multi_period_score * 5))
        
        advanced_analysis['multi_period'] = {
            'short_term_score': short_score,
            'medium_term_score': medium_score,
            'long_term_score': long_score,
            'combined_score': multi_period_score,
            'sentiment': get_sentiment_level(multi_period_score)
        }
    
    # 5. 市场异常检测
    anomaly_detection = {}
    
    # 检测价格异常
    if 'close' in df.columns and len(df) > 20:
        # 计算最近20天的价格标准差
        price_std = df['close'].tail(20).std()
        price_mean = df['close'].tail(20).mean()
        latest_price = df['close'].iloc[-1]
        
        # Z-score异常检测
        z_score = (latest_price - price_mean) / price_std if price_std > 0 else 0
        
        if abs(z_score) > 2.5:
            anomaly_detection['price'] = f"价格异常 (Z-score: {z_score:.2f})"
            anomaly_detection['severity'] = "高"
        elif abs(z_score) > 1.5:
            anomaly_detection['price'] = f"价格轻微异常 (Z-score: {z_score:.2f})"
            anomaly_detection['severity'] = "中"
        else:
            anomaly_detection['price'] = "价格在正常范围内"
            anomaly_detection['severity'] = "低"
    
    # 检测成交量异常
    if 'volume' in df.columns and len(df) > 20:
        # 计算最近20天的成交量标准差
        volume_std = df['volume'].tail(20).std()
        volume_mean = df['volume'].tail(20).mean()
        latest_volume = df['volume'].iloc[-1]
        
        # Z-score异常检测
        z_score = (latest_volume - volume_mean) / volume_std if volume_std > 0 else 0
        
        if z_score > 3:
            anomaly_detection['volume'] = f"成交量极度异常 (Z-score: {z_score:.2f})"
            anomaly_detection['severity'] = "极高"
        elif z_score > 2:
            anomaly_detection['volume'] = f"成交量明显异常 (Z-score: {z_score:.2f})"
            anomaly_detection['severity'] = "高"
        else:
            anomaly_detection['volume'] = "成交量在正常范围内"
    
    advanced_analysis['anomaly'] = anomaly_detection
    
    return advanced_analysis

def get_sentiment_level(score):
    """根据情绪评分返回情绪水平描述"""
    if score > 75:
        return "极度乐观"
    elif score > 50:
        return "非常乐观"
    elif score > 25:
        return "乐观"
    elif score > 0:
        return "略微乐观"
    elif score > -25:
        return "略微悲观"
    elif score > -50:
        return "悲观"
    elif score > -75:
        return "非常悲观"
    else:
        return "极度悲观"

# 更新generate_trading_recommendations函数，整合高级情绪分析
def generate_enhanced_trading_recommendations(df, market_analysis):
    """基于增强市场分析生成交易建议，整合多策略结果"""
    # 首先获取基础的交易建议
    base_recommendations = generate_trading_recommendations(df, market_analysis)
    
    # 如果没有基础建议或数据不足，直接返回
    if not base_recommendations or 'recommendations' not in base_recommendations:
        return base_recommendations
    
    # 获取高级市场分析（如果还没有进行过）
    advanced_analysis = market_analysis.get('advanced', {})
    if not advanced_analysis and len(df) >= 30:
        advanced_analysis = analyze_advanced_market_sentiment(df)
    
    # 增强建议
    enhanced_recommendations = base_recommendations.copy()
    base_confidence = enhanced_recommendations.get('confidence', 50)
    
    # 添加高级分析建议
    if advanced_analysis:
        new_recommendations = []
        
        # 1. 趋势拐点建议
        if 'trend' in advanced_analysis and 'inflection' in advanced_analysis['trend']:
            inflection = advanced_analysis['trend']['inflection']
            if "上升趋势" in inflection:
                new_recommendations.append(f"🔄 趋势分析: {inflection}，可考虑逢低买入")
                if enhanced_recommendations['action'] == "买入":
                    enhanced_recommendations['confidence'] = min(90, base_confidence + 10)
            elif "下降趋势" in inflection:
                new_recommendations.append(f"🔄 趋势分析: {inflection}，建议减仓或观望")
                if enhanced_recommendations['action'] == "卖出":
                    enhanced_recommendations['confidence'] = min(90, base_confidence + 10)
        
        # 2. 支撑阻力位建议
        if 'support_resistance' in advanced_analysis and 'price_position' in advanced_analysis['support_resistance']:
            price_position = advanced_analysis['support_resistance']['price_position']
            new_recommendations.append(f"📊 价格位置: {price_position}")
            
            # 根据支撑阻力位调整建议
            if "低于一级支撑位" in price_position and enhanced_recommendations['action'] == "买入":
                new_recommendations.append("💡 价格接近支撑位，是较好的买入时机")
                enhanced_recommendations['confidence'] = min(90, base_confidence + 5)
            elif "超过一级阻力位" in price_position and enhanced_recommendations['action'] == "卖出":
                new_recommendations.append("💡 价格突破阻力位，可考虑短期获利了结")
                enhanced_recommendations['confidence'] = min(90, base_confidence + 5)
        
        # 3. 多周期情绪建议
        if 'multi_period' in advanced_analysis and 'combined_score' in advanced_analysis['multi_period']:
            multi_score = advanced_analysis['multi_period']['combined_score']
            sentiment = advanced_analysis['multi_period']['sentiment']
            
            new_recommendations.append(f"🔮 多周期综合情绪: {sentiment} (评分: {multi_score:.1f})")
            
            # 调整建议和置信度
            if multi_score > 50 and enhanced_recommendations['action'] == "买入":
                enhanced_recommendations['confidence'] = min(90, base_confidence + 8)
            elif multi_score < -50 and enhanced_recommendations['action'] == "卖出":
                enhanced_recommendations['confidence'] = min(90, base_confidence + 8)
            elif abs(multi_score) < 20:
                new_recommendations.append("⚠️ 市场情绪中性，建议谨慎操作，降低仓位")
                enhanced_recommendations['confidence'] = max(30, base_confidence - 10)
        
        # 4. 异常检测建议
        if 'anomaly' in advanced_analysis and 'severity' in advanced_analysis['anomaly']:
            severity = advanced_analysis['anomaly']['severity']
            
            if severity in ["高", "极高"]:
                new_recommendations.append("⚠️ 检测到市场异常，建议降低仓位，控制风险")
                enhanced_recommendations['risk_level'] = "高"
                enhanced_recommendations['confidence'] = max(30, base_confidence - 15)
        
        # 5. 波动性分析建议
        if 'volatility' in advanced_analysis and 'trend' in advanced_analysis['volatility']:
            vol_trend = advanced_analysis['volatility']['trend']
            new_recommendations.append(f"📈 波动性分析: {vol_trend}")
            
            if "急剧增加" in vol_trend:
                new_recommendations.append("⚠️ 市场波动性显著增加，建议减少交易频率，控制单笔交易规模")
                enhanced_recommendations['risk_level'] = "高"
            elif "下降" in vol_trend and enhanced_recommendations['action'] == "观望":
                new_recommendations.append("💡 市场波动性降低，可能即将迎来趋势性机会，密切关注突破信号")
        
        # 将新建议添加到原有建议中
        enhanced_recommendations['recommendations'] = enhanced_recommendations['recommendations'] + new_recommendations
    
    # 确保置信度在合理范围内
    enhanced_recommendations['confidence'] = max(30, min(90, enhanced_recommendations['confidence']))
    
    return enhanced_recommendations

# 添加一个简单的包装函数来替代原始的计算函数调用
def calculate_indicators(df):
    """智能选择最佳的指标计算方法"""
    # 首先检查是否有传统方法的计算函数
    if 'calculate_technical_indicators' in globals():
        if TALIB_AVAILABLE:
            return calculate_technical_indicators_talib(df)
        else:
            return calculate_technical_indicators(df)
    # 如果没有传统方法的函数，直接使用TA-Lib函数
    elif TALIB_AVAILABLE:
        return calculate_technical_indicators_talib(df)
    # 最后的后备方案，使用基本的计算方法
    else:
        # 提供一个最基本的指标计算，确保程序不会崩溃
        df = df.copy()
        # 基础移动平均线
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma10'] = df['close'].rolling(10).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma30'] = df['close'].rolling(30).mean()
        df['ma60'] = df['close'].rolling(60).mean()
        return df

def is_admin_user(user):
    """检查用户是否为管理员"""
    if not user:
        return False
    
    # 方式1：通过用户名判断（当前方式）
    admin_usernames = ['admin', 'tong']
    if user.get('username') in admin_usernames:
        return True
    
    # 方式2：通过数据库字段判断（推荐方式）
    try:
        import sqlite3
        conn = sqlite3.connect("trading_platform.db")
        cursor = conn.cursor()
        
        # 检查用户表是否有user_type字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_type' in columns:
            cursor.execute("SELECT user_type FROM users WHERE username = ?", (user.get('username'),))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 'admin':
                return True
        else:
            conn.close()
    except Exception:
        pass
    
    return False

def set_user_admin_status(username, is_admin=True):
    """设置用户的管理员状态"""
    try:
        import sqlite3
        conn = sqlite3.connect("trading_platform.db")
        cursor = conn.cursor()
        
        # 检查用户表是否有user_type字段，如果没有则添加
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_type' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'user'")
            conn.commit()
        
        # 设置用户类型
        user_type = 'admin' if is_admin else 'user'
        cursor.execute("UPDATE users SET user_type = ? WHERE username = ?", (user_type, username))
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"设置管理员状态失败: {e}")
        return False

def init_admin_users():
    """初始化管理员用户"""
    admin_users = ['admin', 'tong']
    for username in admin_users:
        set_user_admin_status(username, True)

if __name__ == "__main__":
    main()
