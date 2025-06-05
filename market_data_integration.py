import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import on_sale_data

def display_on_sale_analysis(item_name):
    """
    显示在售量分析界面
    
    Args:
        item_name (str): 物品名称
    """
    st.subheader(f"📊 {item_name} - 在售量分析")
    
    # 获取在售量数据
    with st.spinner("正在获取在售量数据..."):
        on_sale_result = on_sale_data.get_on_sale_data_by_name(item_name)
    
    if not on_sale_result.get('success'):
        st.error(f"❌ 获取在售量数据失败: {on_sale_result.get('error', '未知错误')}")
        return None
    
    # 显示总在售量
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="总在售量",
            value=f"{on_sale_result['total_on_sale']:,}",
            help="所有平台的在售数量总和"
        )
    
    with col2:
        # 进行供需分析
        supply_analysis = on_sale_data.analyze_supply_demand(on_sale_result)
        if supply_analysis.get('success'):
            st.metric(
                label="供应状况",
                value=supply_analysis['supply_level'],
                help=f"供应评分: {supply_analysis['supply_score']}/100"
            )
    
    with col3:
        st.metric(
            label="更新时间",
            value=on_sale_result['update_time'],
            help="数据最后更新时间"
        )
    
    # 显示各平台详情
    st.subheader("🏪 各平台在售详情")
    
    platforms_data = on_sale_result['platforms']
    if platforms_data:
        # 创建数据框
        df = pd.DataFrame(platforms_data)
        
        # 显示表格
        st.dataframe(
            df,
            column_config={
                "platform": "平台名称",
                "on_sale_count": st.column_config.NumberColumn(
                    "在售数量",
                    format="%d"
                ),
                "min_price": st.column_config.NumberColumn(
                    "最低价格",
                    format="%.2f"
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # 创建可视化图表
        create_on_sale_charts(df, on_sale_result['total_on_sale'])
    
    # 显示供需分析
    if supply_analysis.get('success'):
        st.subheader("📈 供需分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**分析结果:** {supply_analysis['analysis']}")
        
        with col2:
            st.success(f"**交易建议:** {supply_analysis['recommendation']}")
    
    return on_sale_result

def create_on_sale_charts(df, total_on_sale):
    """
    创建在售量可视化图表
    
    Args:
        df (pd.DataFrame): 平台数据
        total_on_sale (int): 总在售量
    """
    col1, col2 = st.columns(2)
    
    with col1:
        # 饼图 - 各平台在售量分布
        fig_pie = px.pie(
            df, 
            values='on_sale_count', 
            names='platform',
            title='各平台在售量分布',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 条形图 - 各平台在售数量
        fig_bar = px.bar(
            df, 
            x='platform', 
            y='on_sale_count',
            title='各平台在售数量对比',
            color='on_sale_count',
            color_continuous_scale='viridis'
        )
        fig_bar.update_layout(
            xaxis_title="平台",
            yaxis_title="在售数量",
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 散点图 - 价格与在售量关系
    if 'min_price' in df.columns and df['min_price'].sum() > 0:
        fig_scatter = px.scatter(
            df, 
            x='min_price', 
            y='on_sale_count',
            size='on_sale_count',
            color='platform',
            title='价格与在售量关系',
            hover_data=['platform']
        )
        fig_scatter.update_layout(
            xaxis_title="最低价格",
            yaxis_title="在售数量",
            height=400
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

def integrate_on_sale_with_kline(kline_df, on_sale_data):
    """
    将在售量数据与K线数据结合分析
    
    Args:
        kline_df (pd.DataFrame): K线数据
        on_sale_data (dict): 在售量数据
        
    Returns:
        dict: 综合分析结果
    """
    if not on_sale_data.get('success') or kline_df.empty:
        return {
            'success': False,
            'error': '数据不完整，无法进行综合分析'
        }
    
    # 获取最新价格和成交量
    latest_price = kline_df['close'].iloc[-1]
    latest_volume = kline_df['volume'].iloc[-1]
    avg_volume = kline_df['volume'].mean()
    
    # 计算在售量与成交量比值
    total_on_sale = on_sale_data['total_on_sale']
    on_sale_volume_ratio = total_on_sale / avg_volume if avg_volume > 0 else 0
    
    # 综合分析
    analysis = {
        'success': True,
        'latest_price': latest_price,
        'latest_volume': latest_volume,
        'avg_volume': avg_volume,
        'total_on_sale': total_on_sale,
        'on_sale_volume_ratio': on_sale_volume_ratio,
        'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 生成综合建议
    if on_sale_volume_ratio < 5:
        analysis['market_condition'] = '供需平衡'
        analysis['recommendation'] = '市场供需相对平衡，可正常交易'
    elif on_sale_volume_ratio < 10:
        analysis['market_condition'] = '供应偏多'
        analysis['recommendation'] = '在售量相对较高，建议谨慎买入'
    else:
        analysis['market_condition'] = '供应过剩'
        analysis['recommendation'] = '在售量过高，建议暂缓买入或考虑卖出'
    
    return analysis

def display_integrated_analysis(kline_df, on_sale_data, item_name):
    """
    显示K线与在售量的综合分析
    
    Args:
        kline_df (pd.DataFrame): K线数据
        on_sale_data (dict): 在售量数据
        item_name (str): 物品名称
    """
    st.subheader(f"🔄 {item_name} - 综合市场分析")
    
    # 进行综合分析
    integrated_result = integrate_on_sale_with_kline(kline_df, on_sale_data)
    
    if not integrated_result.get('success'):
        st.error(f"❌ 综合分析失败: {integrated_result.get('error')}")
        return
    
    # 显示关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="最新价格",
            value=f"{integrated_result['latest_price']:.2f}",
            help="最新收盘价"
        )
    
    with col2:
        st.metric(
            label="最新成交量",
            value=f"{integrated_result['latest_volume']:,.0f}",
            help="最新成交量"
        )
    
    with col3:
        st.metric(
            label="平均成交量",
            value=f"{integrated_result['avg_volume']:,.0f}",
            help="历史平均成交量"
        )
    
    with col4:
        st.metric(
            label="在售量/成交量比",
            value=f"{integrated_result['on_sale_volume_ratio']:.1f}",
            help="在售量与平均成交量的比值"
        )
    
    # 显示市场状况和建议
    col1, col2 = st.columns(2)
    
    with col1:
        if integrated_result['on_sale_volume_ratio'] < 5:
            st.success(f"**市场状况:** {integrated_result['market_condition']}")
        elif integrated_result['on_sale_volume_ratio'] < 10:
            st.warning(f"**市场状况:** {integrated_result['market_condition']}")
        else:
            st.error(f"**市场状况:** {integrated_result['market_condition']}")
    
    with col2:
        st.info(f"**综合建议:** {integrated_result['recommendation']}")

def add_on_sale_to_sidebar():
    """
    在侧边栏添加在售量分析选项
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 在售量分析")
    
    # 物品选择
    available_items = list(on_sale_data.ITEM_ID_MAP.keys())
    selected_item = st.sidebar.selectbox(
        "选择物品",
        available_items,
        key="on_sale_item_selector"
    )
    
    # 分析按钮
    if st.sidebar.button("获取在售量数据", key="get_on_sale_data"):
        st.session_state.show_on_sale_analysis = True
        st.session_state.selected_on_sale_item = selected_item
    
    return selected_item 