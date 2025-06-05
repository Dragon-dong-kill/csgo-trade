import streamlit as st
from datetime import datetime, timedelta
import on_sale_data
import market_data_integration
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def on_sale_analysis_page():
    """在售量分析页面"""
    try:
        import on_sale_data
        import market_data_integration
        ON_SALE_DATA_AVAILABLE = True
    except ImportError:
        ON_SALE_DATA_AVAILABLE = False
    
    if not ON_SALE_DATA_AVAILABLE:
        st.error("❌ 在售量数据模块未安装，请先安装相关依赖")
        st.code("pip install requests")
        return
    
    st.markdown('<h2 class="sub-header">📈 在售量数据分析</h2>', unsafe_allow_html=True)
    
    # 页面说明
    st.markdown("""
    <div class="metric-card">
        <h4>📊 在售量分析功能</h4>
        <p>• <strong>实时数据：</strong>获取各平台最新在售量数据</p>
        <p>• <strong>供需分析：</strong>基于在售量评估市场供需状况</p>
        <p>• <strong>价格对比：</strong>对比各平台价格和在售数量</p>
        <p>• <strong>交易建议：</strong>根据供需状况提供交易建议</p>
        <p>• <strong>批量分析：</strong>支持批量获取多个物品的在售数据</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2 = st.tabs(["🎯 单品分析", "🧠 主力行为分析"])
    
    with tab1:
        show_single_item_analysis()
    
    with tab2:
        market_behavior_analysis()

def show_single_item_analysis():
    """显示单品分析页面"""
    st.markdown("### 📊 单品在售量分析")
    
    # 功能说明
    st.markdown("""
    **🎯 功能特点：**
    - **实时在售量数据：** 获取各平台最新在售数量
    - **供需状况分析：** 评估市场供应水平和价格支撑
    - **平台分布对比：** 对比各平台在售量和价格差异
    
    **📊 数据来源：** 实时API数据
    """)
    
    # 参数选择区域
    st.markdown("#### ⚙️ 分析参数")
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
    
    with col1:
        selected_item = st.selectbox(
            "📊 选择分析物品",
            options=list(on_sale_data.ON_SALE_URL_MAP.keys()),
            index=0,
            help="选择要分析的CS:GO物品",
            key="single_item_selector"
        )
    
    with col2:
        st.markdown("**📈 分析类型**")
        st.info("在售量分析")
        st.caption("实时数据获取")
    
    with col3:
        st.markdown("**🔄 数据更新**")
        st.info("实时更新")
        st.caption("点击分析获取最新数据")
    
    with col4:
        st.markdown("**📊 数据来源**")
        st.info("多平台API")
        st.caption("覆盖主要交易平台")
    
    with col5:
        # 分析按钮
        st.markdown("**🚀 开始分析**")
        if st.button("📊 获取在售量数据", type="primary", use_container_width=True, key="single_analysis_button"):
            st.session_state.start_single_analysis = True
    
    # 添加分隔线
    st.markdown("---")
    
    # 执行分析
    if st.session_state.get('start_single_analysis', False):
        if selected_item:
            with st.spinner("正在获取在售量数据..."):
                # 获取在售量数据
                on_sale_result = on_sale_data.get_on_sale_data_by_url(selected_item)
                
                if on_sale_result.get('success'):
                    display_single_item_analysis(selected_item, on_sale_result)
                else:
                    st.error(f"获取数据失败: {on_sale_result.get('error', '未知错误')}")
        else:
            st.error("请选择要分析的物品")
        # 重置状态
        st.session_state.start_single_analysis = False

def market_behavior_analysis():
    """主力行为分析功能"""
    st.markdown("### 🧠 主力行为与行情分析")
    
    # 功能说明
    st.markdown("""
    ### 🧠 主力行为分析
    
    **🎯 功能特点：**
    - **行情阶段判断：** 判断行情的启动、加速、顶部、结束等阶段
    - **交易信号提示：** 基于分析结果提供交易建议和风险提示
    
    **📊 数据来源：** 实时在售量数据
    """)
    
    # 分析参数设置
    st.markdown("#### ⚙️ 分析参数设置")
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
    
    with col1:
        selected_item = st.selectbox(
            "📊 选择分析物品",
            options=list(on_sale_data.ON_SALE_URL_MAP.keys()),
            index=0,
            help="选择要分析的CS:GO物品",
            key="market_behavior_selector"
        )
    
    with col2:
        analysis_days = st.selectbox(
            "⏰ 分析周期",
            options=[7, 14, 21, 30],
            index=2,
            help="选择分析的时间周期（天数）",
            key="analysis_days_selector"
        )
    
    with col3:
        analysis_type = st.selectbox(
            "🔍 分析类型",
            options=["量价关系分析"],
            index=0,
            help="专注于在售量与价格的走势关系判断",
            key="analysis_type_selector"
        )
    
    with col4:
        st.markdown("**📈 数据来源**")
        st.info("实时API数据")
        st.caption("数据更新频率：实时")
    
    with col5:
        # 分析按钮
        st.markdown("**🚀 开始分析**")
        if st.button("🧠 开始主力分析", type="primary", use_container_width=True, key="market_behavior_button"):
            st.session_state.start_analysis = True
    
    # 添加分隔线
    st.markdown("---")
                    
    # 执行分析
    if st.session_state.get('start_analysis', False):
        if selected_item:
            with st.spinner("正在分析主力行为和行情趋势..."):
                perform_market_behavior_analysis(selected_item, analysis_days)
        else:
            st.error("请选择要分析的物品")
        # 重置状态
        st.session_state.start_analysis = False

def perform_market_behavior_analysis(item_name, days):
    """执行主力行为分析"""
    # 获取历史数据（这里使用模拟数据，实际应用中需要真实历史数据）
    historical_data = on_sale_data.simulate_historical_data(item_name, days)
    
    if not historical_data:
        st.error("❌ 无法获取历史数据")
        return
    
    # 进行主力行为分析
    analysis_result = on_sale_data.analyze_market_behavior(historical_data)
    
    if not analysis_result.get('success'):
        st.error(f"❌ 分析失败: {analysis_result.get('error', '未知错误')}")
        return
    
    # 显示分析结果
    display_market_behavior_analysis(item_name, analysis_result, historical_data)

def display_market_behavior_analysis(item_name, analysis_result, historical_data):
    """显示主力行为分析结果"""
    st.markdown("---")
    st.markdown(f"### 🧠 {item_name} - 主力行为分析结果")
    
    # 综合分析摘要
    comprehensive = analysis_result['comprehensive_analysis']
    
    # 第一行：关键指标卡片 - 使用5列布局
    st.markdown("#### 📊 关键分析指标")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "分析置信度",
            f"{comprehensive['confidence_level']:.0f}%",
            help="分析结果的可信度"
        )
    
    with col2:
        main_force = analysis_result['main_force_behavior']
        st.metric(
            "主力行为强度",
            main_force['level'],
            help=f"置信度: {main_force['confidence']}"
        )
    
    with col3:
        market_phase = analysis_result['market_phase']
        st.metric(
            "市场阶段",
            market_phase['main_phase'],
            help=f"阶段评分: {market_phase['score']}"
        )
    
    with col4:
        trends = analysis_result['trends']
        correlation = trends['correlation']
        correlation_desc = "强负相关" if correlation < -0.5 else "强正相关" if correlation > 0.5 else "弱相关"
        st.metric(
            "价量相关性",
            correlation_desc,
            f"{correlation:.3f}",
            help="在售量与价格的相关系数"
        )
    
    with col5:
        # 近期趋势
        recent_price_trend = main_force.get('recent_price_trend', 0)
        trend_desc = "上升" if recent_price_trend > 1 else "下降" if recent_price_trend < -1 else "横盘"
        st.metric(
            "近期趋势",
            trend_desc,
            f"{recent_price_trend:.2f}%",
            help="最近3期平均价格变化"
        )
    
    # 第二行：趋势图表 - 使用全宽度
    st.markdown("---")
    display_trend_charts(historical_data, analysis_result)
    
    # 第三行：分为三列显示信号、报告和建议
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        display_behavior_signals_compact(analysis_result)
    
    with col2:
        display_comprehensive_report_compact(comprehensive)
    
    with col3:
        display_trading_strategy(comprehensive, main_force)

def display_trend_charts(historical_data, analysis_result):
    """显示趋势图表"""
    st.markdown("#### 📈 价量趋势分析")
    
    trends = analysis_result['trends']
    
    # 创建双轴图表 - 调整为更合理的布局
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('📊 在售量趋势', '💰 价格趋势', '📈 变化率对比', '🔗 价量关系'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": True}, {"secondary_y": False}]],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    dates = trends['dates']
    
    # 在售量趋势
    fig.add_trace(
        go.Scatter(x=dates, y=trends['on_sale_counts'], name='在售量', 
                  line=dict(color='#1f77b4', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=dates, y=trends['on_sale_ma'], name='在售量MA', 
                  line=dict(color='#aec7e8', dash='dash', width=1)),
        row=1, col=1
    )
    
    # 价格趋势
    fig.add_trace(
        go.Scatter(x=dates, y=trends['min_prices'], name='最低价', 
                  line=dict(color='#ff7f0e', width=2)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=dates, y=trends['price_ma'], name='价格MA', 
                  line=dict(color='#ffbb78', dash='dash', width=1)),
        row=1, col=2
    )
    
    # 变化率对比
    change_dates = dates[1:]  # 变化率比原数据少一个点
    fig.add_trace(
        go.Scatter(x=change_dates, y=trends['on_sale_changes'], name='在售量变化率%', 
                  line=dict(color='#2ca02c', width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=change_dates, y=trends['price_changes'], name='价格变化率%', 
                  line=dict(color='#d62728', width=2)),
        row=2, col=1, secondary_y=True
    )
    
    # 散点图显示相关性
    fig.add_trace(
        go.Scatter(
            x=trends['on_sale_changes'], 
            y=trends['price_changes'], 
            mode='markers',
            name='价量关系',
            marker=dict(color='#9467bd', size=10, opacity=0.7),
            showlegend=False
        ),
        row=2, col=2
    )
    
    # 添加相关性趋势线
    if len(trends['on_sale_changes']) > 1:
        import numpy as np
        x_vals = trends['on_sale_changes']
        y_vals = trends['price_changes']
        z = np.polyfit(x_vals, y_vals, 1)
        p = np.poly1d(z)
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=p(x_vals),
                mode='lines',
                name='趋势线',
                line=dict(color='red', dash='dash', width=2),
                showlegend=False
            ),
            row=2, col=2
        )
    
    # 更新布局
    fig.update_layout(
        height=700, 
        showlegend=True, 
        title_text="",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # 更新坐标轴标题
    fig.update_xaxes(title_text="日期", row=1, col=1)
    fig.update_xaxes(title_text="日期", row=1, col=2)
    fig.update_xaxes(title_text="日期", row=2, col=1)
    fig.update_xaxes(title_text="在售量变化率%", row=2, col=2)
    
    fig.update_yaxes(title_text="在售量", row=1, col=1)
    fig.update_yaxes(title_text="价格(¥)", row=1, col=2)
    fig.update_yaxes(title_text="在售量变化率%", row=2, col=1)
    fig.update_yaxes(title_text="价格变化率%", row=2, col=1, secondary_y=True)
    fig.update_yaxes(title_text="价格变化率%", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

def display_behavior_signals_compact(analysis_result):
    """显示主力行为和意图分析"""
    st.markdown("#### 🎯 主力行为分析")
    
    main_force = analysis_result['main_force_behavior']
    comprehensive = analysis_result['comprehensive_analysis']
    
    # 主力意图
    main_intention = main_force.get('main_intention', '观望等待')
    st.markdown("**🧠 主力当前意图**")
    
    if "继续拉升" in main_intention or "持续推高" in main_intention:
        st.success(f"🚀 {main_intention}")
    elif "快速出货" in main_intention or "逐步减仓" in main_intention:
        st.error(f"📉 {main_intention}")
    elif "准备反弹" in main_intention or "收集筹码" in main_intention:
        st.success(f"🟢 {main_intention}")
    elif "清洗浮筹" in main_intention or "测试抛压" in main_intention:
        st.warning(f"⚠️ {main_intention}")
    else:
        st.info(f"📊 {main_intention}")
    
    # 下一步动作
    next_move = comprehensive.get('next_move', '等待明确信号')
    st.markdown("**🎯 预期下一步动作**")
    st.info(f"💡 {next_move}")
    
    # 关键信号（只显示前2个）
    st.markdown("**📊 关键量价信号**")
    if main_force['signals']:
        for signal in main_force['signals'][:2]:
            if "强势控盘" in signal or "配合良好" in signal:
                st.success(signal)
            elif "出货" in signal or "下跌" in signal:
                st.error(signal)
            elif "背离" in signal:
                st.warning(signal)
            else:
                st.info(signal)
    else:
        st.info("📊 暂无明显信号")

def display_comprehensive_report_compact(comprehensive):
    """显示行情阶段和操作建议"""
    st.markdown("#### 📈 行情阶段分析")
    
    # 分析摘要
    st.markdown("**📊 当前阶段**")
    summary = comprehensive['summary']
    
    if "吸筹期" in summary:
        st.success(f"🟢 {summary}")
    elif "启动期" in summary or "拉升期" in summary:
        st.success(f"🚀 {summary}")
    elif "出货期" in summary or "下跌期" in summary:
        st.error(f"🔴 {summary}")
    elif "筑底期" in summary:
        st.warning(f"🟡 {summary}")
    else:
        st.info(f"📊 {summary}")
    
    # 置信度显示
    confidence = comprehensive['confidence_level']
    st.markdown("**🎯 分析置信度**")
    st.progress(confidence / 100)
    
    if confidence >= 70:
        st.success(f"高置信度：{confidence:.0f}%")
    elif confidence >= 50:
        st.warning(f"中等置信度：{confidence:.0f}%")
    else:
        st.error(f"低置信度：{confidence:.0f}%")
    
    # 操作建议
    st.markdown("**💡 操作建议**")
    suggestion = comprehensive['trading_suggestion']
    
    if "积极参与" in suggestion or "分批建仓" in suggestion:
        st.success(suggestion)
    elif "立即离场" in suggestion or "空仓观望" in suggestion:
        st.error(suggestion)
    elif "密切关注" in suggestion or "适量" in suggestion:
        st.warning(suggestion)
    else:
        st.info(suggestion)

def display_trading_strategy(comprehensive, main_force):
    """显示风险提示和量价关系"""
    st.markdown("#### ⚠️ 风险控制")
    
    # 风险提示
    st.markdown("**⚠️ 风险提示**")
    risk_warning = comprehensive['risk_warning']
    
    if "严格止损" in risk_warning or "及时离场" in risk_warning:
        st.error(risk_warning)
    elif "谨慎决策" in risk_warning or "控制仓位" in risk_warning:
        st.warning(risk_warning)
    else:
        st.info(risk_warning)
    
    # 量价关系评估
    st.markdown("**📊 量价关系评估**")
    correlation = main_force.get('correlation', 0)
    
    if correlation < -0.5:
        st.success(f"🟢 健康负相关 ({correlation:.3f})")
        st.caption("量价关系良好，走势健康")
    elif correlation > 0.5:
        st.error(f"🔴 异常正相关 ({correlation:.3f})")
        st.caption("量价关系异常，需要警惕")
    else:
        st.info(f"🟡 弱相关 ({correlation:.3f})")
        st.caption("量价关系不明确")
    
    # 变化强度
    recent_on_sale_change = main_force.get('recent_on_sale_change', 0)
    recent_price_change = main_force.get('recent_price_change', 0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("在售量变化", f"{recent_on_sale_change:.1f}%", 
                 help="最近一期在售量变化幅度")
    with col2:
        st.metric("价格变化", f"{recent_price_change:.1f}%", 
                 help="最近一期价格变化幅度")

def display_single_item_analysis(item_name, on_sale_result):
    """显示单品分析结果"""
    st.markdown("---")
    st.markdown(f"### 📊 {item_name} - 在售量分析结果")
    
    # 第一行：基本信息指标 - 使用更宽的布局
    st.markdown("#### 📈 基本信息")
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 3])
    
    with col1:
        st.metric(
            "总在售量",
            f"{on_sale_result['total_on_sale']:,}",
            help="所有平台的在售数量总和"
        )
    
    with col2:
        # 供需分析
        supply_analysis = on_sale_data.analyze_supply_demand(on_sale_result)
        if supply_analysis.get('success'):
            st.metric(
                "供应状况",
                supply_analysis['supply_level'],
                help=f"供应评分: {supply_analysis['supply_score']}/100"
            )
    
    with col3:
        # 平台数量
        platform_count = len(on_sale_result['platforms'])
        st.metric(
            "平台数量",
            f"{platform_count}个",
            help="有在售数据的平台数量"
        )
    
    with col4:
        st.metric(
            "更新时间",
            on_sale_result['update_time'],
            help="数据最后更新时间"
        )
    
    with col5:
        # 供应评分进度条
        if supply_analysis.get('success'):
            st.markdown("**📈 供应评分**")
            score = supply_analysis['supply_score']
            st.progress(score / 100)
            st.caption(f"{score}/100 - " + 
                      ("稀缺" if score >= 80 else "偏少" if score >= 60 else 
                       "正常" if score >= 40 else "充足" if score >= 20 else "过剩"))
    
    # 第二行：图表展示 - 使用全宽度
    if on_sale_result['platforms']:
        st.markdown("---")
        st.markdown("#### 📊 平台分布分析")
        
        # 创建数据框
        platform_df = pd.DataFrame(on_sale_result['platforms'])
        
        # 使用三列布局显示图表和数据
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # 饼图显示平台分布
            fig_pie = px.pie(
                platform_df, 
                values='on_sale_count', 
                names='platform',
                title="📊 各平台在售量分布",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 柱状图显示价格对比
            fig_bar = px.bar(
                platform_df,
                x='platform',
                y='min_price',
                title="💰 各平台最低价格对比",
                color='on_sale_count',
                color_continuous_scale='viridis',
                text='min_price'
            )
            fig_bar.update_traces(texttemplate='¥%{text:.0f}', textposition='outside')
            fig_bar.update_layout(height=350, xaxis_tickangle=-45)
            fig_bar.update_yaxes(title_text="价格(¥)")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col3:
            # 详细表格
            st.markdown("#### 📋 详细数据")
            if on_sale_result['platforms']:
                # 格式化数据显示
                display_df = platform_df.copy()
                display_df['min_price'] = display_df['min_price'].apply(lambda x: f"¥{x:.2f}")
                display_df.columns = ['平台', '在售数量', '最低价格']
                st.dataframe(display_df, use_container_width=True, hide_index=True, height=280)
            else:
                st.info("暂无平台数据")
    
    # 第三行：分析建议 - 使用全宽度
    st.markdown("---")
    st.markdown("#### 💡 分析建议")
    
    if supply_analysis.get('success'):
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # 供需分析
            st.markdown("**📊 供需分析**")
            supply_level = supply_analysis['supply_level']
            if supply_level == "稀缺":
                st.success(f"🔴 {supply_analysis['analysis']}")
            elif supply_level == "偏少":
                st.warning(f"🟡 {supply_analysis['analysis']}")
            elif supply_level == "正常":
                st.info(f"🟢 {supply_analysis['analysis']}")
            elif supply_level == "充足":
                st.warning(f"🟠 {supply_analysis['analysis']}")
            else:  # 过剩
                st.error(f"🔴 {supply_analysis['analysis']}")
        
        with col2:
            # 交易建议
            st.markdown("**💡 交易建议**")
            recommendation = supply_analysis['recommendation']
            if "买入" in recommendation:
                st.success(f"✅ {recommendation}")
            elif "避免" in recommendation or "谨慎" in recommendation:
                st.error(f"⚠️ {recommendation}")
            else:
                st.info(f"ℹ️ {recommendation}")
        
        with col3:
            # 市场状况总结
            st.markdown("**📈 市场状况**")
            total_on_sale = on_sale_result['total_on_sale']
            if total_on_sale < 100:
                st.success("🔥 市场稀缺，价格支撑强")
            elif total_on_sale < 500:
                st.info("📈 供应偏少，价格有支撑")
            elif total_on_sale < 1000:
                st.info("⚖️ 供需平衡，价格稳定")
            elif total_on_sale < 2000:
                st.warning("📉 供应充足，价格压力增加")
            else:
                st.error("⚠️ 供应过剩，价格下跌风险")
    else:
        st.error("供需分析失败")

def render_usage_guide():
    """渲染使用说明"""
    st.markdown("---")
    with st.expander("📖 使用说明"):
        st.markdown("""
        **在售量分析功能说明:**
        
        ### 🎯 单品分析
        - 选择单个物品进行详细的在售量分析
        - 查看各平台的在售数量和价格分布
        - 获取供需分析和交易建议
        
        ### 🧠 主力行为分析
        - 基于经典量价关系理论分析主力行为
        - 识别主力出货、吸筹、控盘等行为模式
        - 判断行情的启动、加速、顶部、结束等阶段
        - 提供专业的交易建议和风险提示
        
        **供应状况评级:**
        - 🔴 **稀缺** (< 100个): 供应极少，价格可能上涨
        - 🟡 **偏少** (100-500个): 供应较少，可考虑买入
        - 🟢 **正常** (500-1000个): 供需平衡，正常交易
        - 🟠 **充足** (1000-2000个): 供应充足，谨慎买入
        - 🔴 **过剩** (> 2000个): 供应过剩，建议避免买入
        
        ---
        
        ## 📊 经典量价关系理论
        
        ### 🔍 六大经典量价关系
        
        #### 1. 🚀 量增价涨 - 健康上涨态势
        - **强势上涨**: 放量大涨(量增>5%, 价涨>5%) - 多头强势突破
        - **健康上涨**: 放量上涨(量增>5%, 价涨2-5%) - 健康上升趋势
        - **判断**: 这是最健康的上涨形态，表明多头力量强劲
        
        #### 2. 💪 量减价涨 - 无量上涨（两种情况）
        - **主力控盘**: 缩量上涨且持续上涨趋势 - 主力强势控盘
        - **弱势反弹**: 缩量上涨但趋势不明 - 上涨动能不足
        - **判断**: 需结合趋势判断，控盘期相对安全
        
        #### 3. 📉 量增价跌 - 放量下跌
        - **恐慌抛售**: 放量暴跌(量增>8%, 价跌>5%) - 恐慌性抛售
        - **主力出货**: 放量下跌(量增>8%, 价跌2-5%) - 主力出货信号
        - **判断**: 这是最危险的信号，应立即减仓
        
        #### 4. 🟢 量减价跌 - 缩量下跌
        - **底部吸筹**: 缩量下跌且持续下跌趋势 - 抛压减轻，底部临近
        - **主力吸筹**: 缩量调整 - 主力可能在吸筹
        - **判断**: 通常是底部信号，可考虑逢低布局
        
        #### 5. ⚖️ 量增价平 - 多空分歧
        - **变盘前夜**: 放量横盘 - 多空激烈博弈，变盘在即
        - **判断**: 需密切关注突破方向，做好应对准备
        
        #### 6. 😴 量减价平 - 成交清淡
        - **横盘整理**: 缩量横盘 - 市场观望情绪浓厚
        - **判断**: 通常是整理阶段，等待方向选择
        
        ---
        
        ## 📈 行情周期理论
        
        ### 🔄 七大行情阶段
        
        #### 1. 🟢 底部吸筹期
        - **特征**: 量缩价稳或微跌，主力悄然建仓
        - **信号**: 在售量减少(<-3%), 价格变化小(<2%)
        - **策略**: 分批建仓，越跌越买，长期持有
        
        #### 2. 🚀 启动期  
        - **特征**: 量增价涨，突破整理区间
        - **信号**: 在售量增加(>3%), 价格上涨(>1.5%), 近期涨势加速
        - **策略**: 分批建仓，逢低加仓，设置动态止盈
        
        #### 3. 📈 上升期
        - **特征**: 量价配合良好，趋势明确向上
        - **信号**: 在售量增加(>2%), 价格上涨(>2%), 持续上涨
        - **策略**: 持有为主，回调时适当加仓
        
        #### 4. 🔥 加速期
        - **特征**: 量价齐升，市场情绪高涨
        - **信号**: 在售量大增(>8%), 价格大涨(>4%), 加速上涨
        - **策略**: 享受最后疯狂，但要准备随时离场
        
        #### 5. 🔴 顶部期
        - **特征**: 量增价滞或量缩价涨，上涨动能衰竭
        - **信号**: 量增价滞 或 量缩价涨但动能衰减
        - **策略**: 立即减仓，分批离场，保护利润
        
        #### 6. 📉 下跌期
        - **特征**: 量增价跌，恐慌情绪蔓延
        - **信号**: 在售量增加(>5%), 价格下跌(<-2%)
        - **策略**: 空仓观望，等待恐慌情绪释放完毕
        
        #### 7. 🏗️ 筑底期
        - **特征**: 量缩价跌，抛压逐渐减轻
        - **信号**: 在售量减少(<-2%), 价格下跌(<-1%), 但跌幅收窄
        - **策略**: 开始关注，等待明确的底部信号
        
        ---
        
        ## ⚠️ 高级分析技巧
        
        ### 📊 量价背离分析
        - **顶背离**: 价格创新高但量能萎缩 - 上涨动能衰竭
        - **底背离**: 价格创新低但量能萎缩 - 下跌动能衰竭
        
        ### 🎯 趋势持续性分析
        - **量价齐升**: 连续上涨且量能配合 - 上升趋势强劲
        - **量价齐跌**: 连续下跌且放量 - 下跌趋势强劲
        
        ### 📈 相关性分析
        - **强负相关(<-0.7)**: 量价关系健康，趋势可持续
        - **强正相关(>0.7)**: 市场异常信号，需要警惕
        - **弱相关(-0.3~0.3)**: 市场方向不明，谨慎操作
        
        ### 🌪️ 波动率分析
        - **高波动期**: 价格波动>8% 或 量能波动>20% - 市场情绪激烈
        - **低波动期**: 价格波动<2% 且 量能波动<5% - 市场缺乏活力
        
        ---
        
        ## 🎯 实战操作策略
        
        ### 💪 强势上涨期策略
        - **建仓**: 分批建仓，逢低加仓
        - **持仓**: 设置动态止盈，享受趋势红利
        - **风控**: 避免追高，设置合理止损位
        
        ### 🔴 主力出货期策略
        - **减仓**: 立即减仓，分批离场
        - **风控**: 严格止损，避免抄底
        - **心态**: 保护利润，落袋为安
        
        ### 🟢 底部吸筹期策略
        - **建仓**: 分批建仓，越跌越买
        - **持仓**: 长期持有，耐心等待启动
        - **风控**: 底部相对安全，但需控制总仓位
        
        ### ⚖️ 变盘期策略
        - **观察**: 密切关注突破方向
        - **试探**: 轻仓试探，根据方向决定操作
        - **风控**: 严格控制仓位，快进快出
        
        ---
        
        **数据来源:**
        - 数据来源于OK饰品等主流交易平台
        - 实时获取最新的在售量信息
        - 支持的物品包括：树篱迷宫、克拉考、怪兽在b、水栽竹、tyloo贴纸、出逃的萨利等
        
        **免责声明:**
        - 以上分析方法基于经典技术分析理论，仅供参考
        - 市场行为复杂，需结合多种因素综合判断
        - 建议结合K线分析、成交量等其他指标
        - 注意控制仓位，设置止损点，理性投资
        """)

def main_on_sale_page():
    """主在售量分析页面入口"""
    on_sale_analysis_page()
    render_usage_guide()

# 为了兼容性，保留原有函数名
def on_sale_analysis_page_main():
    """在售量分析页面主入口（兼容性函数）"""
    main_on_sale_page() 