import streamlit as st
import pandas as pd
from database import DatabaseManager
from datetime import datetime
import re
import os

# 尝试导入支付配置，如果不存在则使用默认配置
try:
    from config.payment_config import get_payment_config, validate_payment_config
except ImportError:
    def get_payment_config():
        return {
            "account": "请在payment_config.py中配置您的支付宝账号",
            "name": "请配置收款人姓名",
            "qr_code_image": None,
            "real_payment_mode": True,
            "payment_note": "交易策略分析平台会员充值",
            "contact": {}
        }
    
    def validate_payment_config():
        return False, "请先创建payment_config.py配置文件"

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def init_session_state(self):
        """初始化会话状态"""
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'portfolio' not in st.session_state or not isinstance(st.session_state.portfolio, dict):
            st.session_state.portfolio = {
                'cash': 100000,
                'total_value': 100000,
                'positions': {},
                'inventory': {},
                'trade_history': [],
                'max_items_per_symbol': 1000
            }
        else:
            # 健壮性兜底
            p = st.session_state.portfolio
            if not isinstance(p.get('positions'), dict):
                p['positions'] = {}
            if not isinstance(p.get('inventory'), dict):
                p['inventory'] = {}
            if not isinstance(p.get('trade_history'), list):
                p['trade_history'] = []
            if 'cash' not in p:
                p['cash'] = 100000
            if 'total_value' not in p:
                p['total_value'] = 100000
            if 'max_items_per_symbol' not in p:
                p['max_items_per_symbol'] = 1000
        if 'membership' not in st.session_state:
            st.session_state.membership = None
    
    def is_authenticated(self) -> bool:
        """检查用户是否已认证"""
        return st.session_state.get('authenticated', False) and st.session_state.get('user') is not None
    
    def get_current_user(self):
        """获取当前用户"""
        return st.session_state.get('user')
    
    def validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple:
        """验证密码强度"""
        if len(password) < 6:
            return False, "密码长度至少6位"
        if len(password) > 20:
            return False, "密码长度不能超过20位"
        return True, "密码格式正确"
    
    def login_page(self):
        """登录页面"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🔐 用户登录</h1>
            <p>请登录您的账户以继续使用交易策略分析平台</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 创建登录和注册标签页
        login_tab, register_tab = st.tabs(["🔑 登录", "📝 注册"])
        
        with login_tab:
            self._render_login_form()
        
        with register_tab:
            self._render_register_form()
    
    def _render_login_form(self):
        """渲染登录表单"""
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
                
                success, user_data = self.db.login_user(username, password)
                if success:
                    st.session_state.user = user_data
                    st.session_state.authenticated = True
                    
                    # 加载用户账户数据
                    self.load_user_data()
                    
                    st.success(f"欢迎回来，{user_data['display_name']}！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
    
    def _render_register_form(self):
        """渲染注册表单"""
        with st.form("register_form"):
            st.subheader("注册新账户")
            
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("用户名", placeholder="请输入用户名")
                email = st.text_input("邮箱", placeholder="请输入邮箱地址")
            with col2:
                display_name = st.text_input("显示名称", placeholder="请输入显示名称")
                password = st.text_input("密码", type="password", placeholder="请输入密码")
            
            confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
            
            # 服务条款
            agree_terms = st.checkbox("我已阅读并同意服务条款和隐私政策")
            
            register_button = st.form_submit_button("📝 注册", use_container_width=True)
            
            if register_button:
                # 验证输入
                if not all([username, email, display_name, password, confirm_password]):
                    st.error("请填写完整的注册信息")
                    return
                
                if not agree_terms:
                    st.error("请同意服务条款和隐私政策")
                    return
                
                if password != confirm_password:
                    st.error("两次输入的密码不一致")
                    return
                
                if not self.validate_email(email):
                    st.error("邮箱格式不正确")
                    return
                
                valid_password, password_msg = self.validate_password(password)
                if not valid_password:
                    st.error(password_msg)
                    return
                
                # 注册用户
                success, message = self.db.register_user(username, email, password, display_name)
                if success:
                    st.success("注册成功！请使用您的账户登录")
                    st.balloons()
                else:
                    st.error(message)
    
    def load_user_data(self):
        """加载用户数据"""
        if not self.is_authenticated():
            return
        
        user_id = st.session_state.user['id']
        
        # 加载账户数据
        account_data = self.db.get_user_account(user_id)
        if account_data:
            # 健壮性处理
            if not isinstance(account_data.get('positions'), dict):
                account_data['positions'] = {}
            if not isinstance(account_data.get('inventory'), dict):
                account_data['inventory'] = {}
            if not isinstance(account_data.get('trade_history'), list):
                account_data['trade_history'] = []
            if 'cash' not in account_data:
                account_data['cash'] = 100000
            if 'total_value' not in account_data:
                account_data['total_value'] = 100000
            if 'max_items_per_symbol' not in account_data:
                account_data['max_items_per_symbol'] = 1000
            st.session_state.portfolio = account_data
        else:
            # 如果没有账户数据，创建默认账户
            st.session_state.portfolio = {
                'cash': 100000,
                'total_value': 100000,
                'positions': {},
                'inventory': {},
                'trade_history': [],
                'max_items_per_symbol': 1000
            }
        
        # 加载会员状态
        membership_data = self.db.get_membership_status(user_id)
        st.session_state.membership = membership_data
    
    def save_user_data(self):
        """保存用户数据"""
        if not self.is_authenticated():
            return
        
        user_id = st.session_state.user['id']
        portfolio = st.session_state.portfolio
        
        # 保存账户数据
        self.db.save_user_account(user_id, portfolio)
    
    def logout(self):
        """用户登出"""
        # 保存数据
        self.save_user_data()
        
        # 清除会话状态
        st.session_state.user = None
        st.session_state.authenticated = False
        st.session_state.portfolio = None
        st.session_state.membership = None
        
        st.success("已安全退出")
        st.rerun()
    
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
    
    def render_recharge_page(self):
        """渲染充值页面"""
        if not st.session_state.get('show_recharge', False):
            return
        
        st.markdown("### 💳 会员充值")
        
        user = st.session_state.user
        membership = st.session_state.membership
        
        # 当前状态
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📊 当前状态</h4>
                <p><strong>会员类型:</strong> {'高级会员' if membership['is_active'] else '基础会员'}</p>
                <p><strong>资金额度:</strong> {'100万元' if membership['is_active'] else '10万元'}</p>
                <p><strong>剩余天数:</strong> {membership['days_remaining']}天</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💎 高级会员特权</h4>
                <p>• 💰 100万元交易资金</p>
                <p>• 📊 完整数据分析</p>
                <p>• 🎯 高级策略回测</p>
                <p>• 💾 数据永久保存</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 充值选项
        st.markdown("#### 💳 充值选项")
        
        if not membership['is_active']:
            # 新用户充值
            st.markdown("""
            <div style="background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); 
                        padding: 20px; border-radius: 15px; border: 2px solid #4CAF50; margin-bottom: 20px;">
                <h3 style="color: #2E7D32; margin-top: 0;">🎉 高级会员套餐</h3>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="color: #1B5E20; margin: 0;">¥15/月</h2>
                        <p style="margin: 5px 0; color: #388E3C;">享受100万元交易体验</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; font-size: 0.9em; color: #666;">30天有效期</p>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">自动到期</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("💳 立即充值 ¥15", use_container_width=True, type="primary"):
                    # 显示支付宝收款码
                    st.markdown("### 💰 支付宝扫码支付")
                    st.markdown("""
                    <div style="text-align: center; padding: 20px; background: #f0f8ff; border-radius: 10px; margin: 20px 0;">
                        <h4>请使用支付宝扫描下方二维码完成支付</h4>
                        <p style="color: #666;">支付金额: <strong style="color: #ff4500;">¥15.00</strong></p>
                        <p style="color: #666;">支付完成后请点击下方"确认支付"按钮</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 这里您可以放置您的支付宝收款码图片
                    # st.image("您的支付宝收款码图片路径", width=300)
                    
                    # 显示支付宝收款信息
                    payment_config = get_payment_config()
                    config_valid, config_msg = validate_payment_config()
                    
                    if not config_valid:
                        st.warning(f"⚠️ {config_msg}")
                        st.info("请在项目目录下的 payment_config.py 文件中配置您的支付宝收款信息")
                    
                    # 显示收款码图片（如果有）
                    if payment_config.get("qr_code_image") and os.path.exists(payment_config["qr_code_image"]):
                        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
                        with col_img2:
                            st.image(payment_config["qr_code_image"], caption="支付宝收款码", width=300)
                    
                    # 显示收款信息
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; border: 2px dashed #1976D2; border-radius: 10px; margin: 20px 0;">
                        <h4>💳 支付宝收款信息</h4>
                        <p><strong>收款账号:</strong> {payment_config.get('account', '未配置')}</p>
                        <p><strong>收款人:</strong> {payment_config.get('name', '未配置')}</p>
                        <p><strong>收款金额:</strong> ¥15.00</p>
                        <p><strong>备注信息:</strong> {payment_config.get('payment_note', '会员充值')}</p>
                        <p style="color: #ff4500; font-size: 0.9em;">请在转账时备注您的用户名: {user['username']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 显示客服联系方式（如果有）
                    contact = payment_config.get('contact', {})
                    if any(contact.values()):
                        contact_info = []
                        if contact.get('qq'): contact_info.append(f"QQ: {contact['qq']}")
                        if contact.get('wechat'): contact_info.append(f"微信: {contact['wechat']}")
                        if contact.get('email'): contact_info.append(f"邮箱: {contact['email']}")
                        if contact.get('phone'): contact_info.append(f"电话: {contact['phone']}")
                        
                        if contact_info:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 10px; background: #f5f5f5; border-radius: 5px; margin: 10px 0;">
                                <p style="margin: 0; font-size: 0.9em; color: #666;">
                                    <strong>客服联系:</strong> {' | '.join(contact_info)}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 确认支付按钮
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    with col_b:
                        if st.button("✅ 确认已完成支付", use_container_width=True, type="secondary"):
                            success, message = self.db.create_recharge_record(user['id'], 15.0, 'premium')
                            if success:
                                st.success(message)
                                # 模拟支付成功
                                record_id = int(message.split(': ')[1])
                                success, pay_message = self.db.process_recharge(user['id'], record_id)
                                if success:
                                    st.success("🎉 充值成功！您已成为高级会员！")
                                    st.balloons()
                                    # 重新加载用户数据
                                    self.load_user_data()
                                    st.rerun()
                                else:
                                    st.error(pay_message)
                            else:
                                st.error(message)
        else:
            # 续费
            end_date = datetime.strptime(membership['end_date'], '%Y-%m-%d %H:%M:%S')
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); 
                        padding: 20px; border-radius: 15px; border: 2px solid #FF9800; margin-bottom: 20px;">
                <h3 style="color: #F57C00; margin-top: 0;">🔄 会员续费</h3>
                <p>当前会员将于 <strong>{end_date.strftime('%Y年%m月%d日')}</strong> 到期</p>
                <p>续费后有效期将延长30天</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 续费 ¥15", use_container_width=True, type="primary"):
                    # 显示支付宝收款码
                    st.markdown("### 💰 支付宝扫码续费")
                    st.markdown("""
                    <div style="text-align: center; padding: 20px; background: #fff8e1; border-radius: 10px; margin: 20px 0;">
                        <h4>请使用支付宝扫描下方二维码完成续费</h4>
                        <p style="color: #666;">续费金额: <strong style="color: #ff4500;">¥15.00</strong></p>
                        <p style="color: #666;">续费完成后请点击下方"确认支付"按钮</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 这里您可以放置您的支付宝收款码图片
                    # st.image("您的支付宝收款码图片路径", width=300)
                    
                    # 显示支付宝收款信息
                    payment_config = get_payment_config()
                    config_valid, config_msg = validate_payment_config()
                    
                    if not config_valid:
                        st.warning(f"⚠️ {config_msg}")
                        st.info("请在项目目录下的 payment_config.py 文件中配置您的支付宝收款信息")
                    
                    # 显示收款码图片（如果有）
                    if payment_config.get("qr_code_image") and os.path.exists(payment_config["qr_code_image"]):
                        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
                        with col_img2:
                            st.image(payment_config["qr_code_image"], caption="支付宝收款码", width=300)
                    
                    # 显示收款信息
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; border: 2px dashed #FF9800; border-radius: 10px; margin: 20px 0;">
                        <h4>💳 支付宝收款信息</h4>
                        <p><strong>收款账号:</strong> {payment_config.get('account', '未配置')}</p>
                        <p><strong>收款人:</strong> {payment_config.get('name', '未配置')}</p>
                        <p><strong>续费金额:</strong> ¥15.00</p>
                        <p><strong>备注信息:</strong> 交易平台会员续费</p>
                        <p style="color: #ff4500; font-size: 0.9em;">请在转账时备注您的用户名: {user['username']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 显示客服联系方式（如果有）
                    contact = payment_config.get('contact', {})
                    if any(contact.values()):
                        contact_info = []
                        if contact.get('qq'): contact_info.append(f"QQ: {contact['qq']}")
                        if contact.get('wechat'): contact_info.append(f"微信: {contact['wechat']}")
                        if contact.get('email'): contact_info.append(f"邮箱: {contact['email']}")
                        if contact.get('phone'): contact_info.append(f"电话: {contact['phone']}")
                        
                        if contact_info:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 10px; background: #f5f5f5; border-radius: 5px; margin: 10px 0;">
                                <p style="margin: 0; font-size: 0.9em; color: #666;">
                                    <strong>客服联系:</strong> {' | '.join(contact_info)}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 确认支付按钮
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    with col_b:
                        if st.button("✅ 确认已完成续费", use_container_width=True, type="secondary"):
                            success, message = self.db.create_recharge_record(user['id'], 15.0, 'premium')
                            if success:
                                st.success(message)
                                # 模拟支付成功
                                record_id = int(message.split(': ')[1])
                                success, pay_message = self.db.process_recharge(user['id'], record_id)
                                if success:
                                    st.success("🎉 续费成功！会员有效期已延长！")
                                    # 重新加载用户数据
                                    self.load_user_data()
                                    st.rerun()
                                else:
                                    st.error(pay_message)
                            else:
                                st.error(message)
        
        # 充值历史
        st.markdown("#### 📜 充值历史")
        recharge_history = self.db.get_user_recharge_history(user['id'])
        
        if recharge_history:
            history_data = []
            for record in recharge_history:
                status_map = {
                    'pending': '⏳ 待支付',
                    'completed': '✅ 已完成',
                    'failed': '❌ 失败',
                    'expired': '⏰ 已过期'
                }
                
                history_data.append({
                    '订单号': record['id'],
                    '金额': f"¥{record['amount']:.0f}",
                    '类型': '高级会员' if record['type'] == 'premium' else '基础充值',
                    '状态': status_map.get(record['status'], record['status']),
                    '创建时间': record['created_at']
                })
            
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("暂无充值记录")
        
        # 关闭按钮
        if st.button("❌ 关闭", use_container_width=True):
            st.session_state.show_recharge = False
            st.rerun()
    
    def render_user_stats(self):
        """渲染用户统计信息"""
        if not self.is_authenticated():
            return
        
        user_id = st.session_state.user['id']
        stats = self.db.get_user_stats(user_id)
        
        st.markdown("### 📊 交易统计")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总交易次数", stats['total_trades'])
        with col2:
            st.metric("买入次数", stats['buy_trades'])
        with col3:
            st.metric("卖出次数", stats['sell_trades'])
        with col4:
            st.metric("胜率", f"{stats['win_rate']:.1f}%")
        
        col1, col2 = st.columns(2)
        with col1:
            pnl_color = "normal" if stats['total_pnl'] >= 0 else "inverse"
            st.metric("总盈亏", f"¥{stats['total_pnl']:.2f}", delta=None)
        with col2:
            st.metric("盈利次数", stats['profitable_trades'])

def init_auth_session():
    """初始化认证会话"""
    auth = AuthManager()
    auth.init_session_state()

def load_user_data():
    """加载用户数据"""
    auth = AuthManager()
    auth.load_user_data()

def save_user_data():
    """保存用户数据"""
    auth = AuthManager()
    auth.save_user_data() 