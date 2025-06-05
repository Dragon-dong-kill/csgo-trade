import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import streamlit as st

class DatabaseManager:
    def __init__(self, db_path: str = "trading_platform.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # 用户账户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                cash REAL NOT NULL DEFAULT 100000,
                total_value REAL NOT NULL DEFAULT 100000,
                positions TEXT DEFAULT '{}',
                inventory TEXT DEFAULT '{}',
                trade_history TEXT DEFAULT '[]',
                max_items_per_symbol INTEGER DEFAULT 1000,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 充值记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recharge_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                recharge_type TEXT NOT NULL,
                payment_method TEXT,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 会员状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS membership_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                membership_type TEXT NOT NULL DEFAULT 'basic',
                start_date DATETIME,
                end_date DATETIME,
                is_active BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total_amount REAL NOT NULL,
                pnl_amount REAL DEFAULT 0,
                pnl_percent REAL DEFAULT 0,
                trade_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str, display_name: str) -> Tuple[bool, str]:
        """用户注册"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查用户名和邮箱是否已存在
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                return False, "用户名或邮箱已存在"
            
            # 创建用户
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, display_name))
            
            user_id = cursor.lastrowid
            
            # 创建用户账户（基础版10万资金，初始化所有字段）
            cursor.execute('''
                INSERT INTO user_accounts (user_id, cash, total_value, positions, inventory, trade_history, max_items_per_symbol)
                VALUES (?, 100000, 100000, '{}', '{}', '[]', 1000)
            ''', (user_id,))
            
            # 创建会员状态记录
            cursor.execute('''
                INSERT INTO membership_status (user_id, membership_type, is_active)
                VALUES (?, 'basic', 0)
            ''', (user_id,))
            
            conn.commit()
            return True, "注册成功"
            
        except Exception as e:
            conn.rollback()
            return False, f"注册失败: {str(e)}"
        finally:
            conn.close()
    
    def login_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """用户登录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, username, email, display_name, is_active
                FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            if not user:
                return False, None
            
            if not user[4]:  # is_active
                return False, None
            
            # 更新最后登录时间
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user[0],))
            
            conn.commit()
            
            return True, {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'display_name': user[3]
            }
            
        except Exception as e:
            return False, None
        finally:
            conn.close()
    
    def get_user_account(self, user_id: int) -> Optional[Dict]:
        """获取用户账户信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT cash, total_value, positions, inventory, trade_history, max_items_per_symbol
                FROM user_accounts WHERE user_id = ?
            ''', (user_id,))
            
            account = cursor.fetchone()
            if not account:
                return None
            
            return {
                'cash': account[0],
                'total_value': account[1],
                'positions': json.loads(account[2]) if account[2] else {},
                'inventory': json.loads(account[3]) if account[3] else {},
                'trade_history': json.loads(account[4]) if account[4] else [],
                'max_items_per_symbol': account[5]
            }
            
        except Exception as e:
            return None
        finally:
            conn.close()
    
    def save_user_account(self, user_id: int, account_data: Dict) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE user_accounts 
                SET cash = ?, total_value = ?, positions = ?, inventory = ?, 
                    trade_history = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                account_data['cash'],
                account_data['total_value'],
                json.dumps(account_data['positions']),
                json.dumps(account_data['inventory']),
                json.dumps(account_data['trade_history']),
                user_id
            ))
            
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO user_accounts (user_id, cash, total_value, positions, inventory, trade_history, max_items_per_symbol)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    account_data['cash'],
                    account_data['total_value'],
                    json.dumps(account_data['positions']),
                    json.dumps(account_data['inventory']),
                    json.dumps(account_data['trade_history']),
                    account_data.get('max_items_per_symbol', 1000)
                ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            # 确保连接正确关闭
            if conn:
                conn.close()
    
    def add_trade_record(self, user_id: int, trade_data: Dict) -> bool:
        """添加交易记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO trade_records 
                (user_id, symbol, action, quantity, price, total_amount, pnl_amount, pnl_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                trade_data['symbol'],
                trade_data['action'],
                trade_data['quantity'],
                trade_data['price'],
                trade_data['total'],
                trade_data.get('pnl_amount', 0),
                trade_data.get('pnl_percent', 0)
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_membership_status(self, user_id: int) -> Dict:
        """获取用户会员状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT membership_type, start_date, end_date, is_active
                FROM membership_status 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (user_id,))
            
            membership = cursor.fetchone()
            if not membership:
                return {
                    'type': 'basic',
                    'is_active': False,
                    'start_date': None,
                    'end_date': None,
                    'days_remaining': 0
                }
            
            # 检查会员是否过期
            is_active = membership[3]
            days_remaining = 0
            
            if membership[2]:  # end_date存在
                end_date = datetime.strptime(membership[2], '%Y-%m-%d %H:%M:%S')
                if end_date > datetime.now():
                    days_remaining = (end_date - datetime.now()).days
                    is_active = True
                else:
                    is_active = False
                    # 更新会员状态为过期
                    cursor.execute('''
                        UPDATE membership_status 
                        SET is_active = 0 
                        WHERE user_id = ?
                    ''', (user_id,))
                    conn.commit()
            
            return {
                'type': membership[0],
                'is_active': is_active,
                'start_date': membership[1],
                'end_date': membership[2],
                'days_remaining': days_remaining
            }
            
        except Exception as e:
            return {
                'type': 'basic',
                'is_active': False,
                'start_date': None,
                'end_date': None,
                'days_remaining': 0
            }
        finally:
            conn.close()
    
    def create_recharge_record(self, user_id: int, amount: float, recharge_type: str) -> Tuple[bool, str]:
        """创建充值记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 计算过期时间（30天后）
            expires_at = datetime.now() + timedelta(days=30)
            
            cursor.execute('''
                INSERT INTO recharge_records 
                (user_id, amount, recharge_type, status, expires_at)
                VALUES (?, ?, ?, 'pending', ?)
            ''', (user_id, amount, recharge_type, expires_at))
            
            record_id = cursor.lastrowid
            conn.commit()
            
            return True, f"充值订单创建成功，订单号: {record_id}"
            
        except Exception as e:
            conn.rollback()
            return False, f"创建充值订单失败: {str(e)}"
        finally:
            conn.close()
    
    def process_recharge(self, user_id: int, record_id: int) -> Tuple[bool, str]:
        """处理充值（模拟支付成功）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 获取充值记录
            cursor.execute('''
                SELECT amount, recharge_type, status, expires_at
                FROM recharge_records 
                WHERE id = ? AND user_id = ?
            ''', (record_id, user_id))
            
            record = cursor.fetchone()
            if not record:
                return False, "充值记录不存在"
            
            if record[2] != 'pending':
                return False, "该订单已处理"
            
            # 检查是否过期
            expires_at = datetime.strptime(record[3], '%Y-%m-%d %H:%M:%S')
            if expires_at < datetime.now():
                return False, "充值订单已过期"
            
            # 更新充值记录状态
            cursor.execute('''
                UPDATE recharge_records 
                SET status = 'completed' 
                WHERE id = ?
            ''', (record_id,))
            
            # 如果是会员充值，更新会员状态
            if record[1] == 'premium':
                start_date = datetime.now()
                end_date = start_date + timedelta(days=30)
                
                cursor.execute('''
                    UPDATE membership_status 
                    SET membership_type = 'premium', 
                        start_date = ?, 
                        end_date = ?, 
                        is_active = 1
                    WHERE user_id = ?
                ''', (start_date, end_date, user_id))
                
                # 升级用户资金到100万
                cursor.execute('''
                    UPDATE user_accounts 
                    SET cash = cash + 900000,
                        total_value = total_value + 900000
                    WHERE user_id = ?
                ''', (user_id,))
            
            conn.commit()
            return True, "充值成功！"
            
        except Exception as e:
            conn.rollback()
            return False, f"充值处理失败: {str(e)}"
        finally:
            conn.close()
    
    def get_user_recharge_history(self, user_id: int) -> List[Dict]:
        """获取用户充值历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, amount, recharge_type, status, created_at, expires_at
                FROM recharge_records 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            records = cursor.fetchall()
            return [
                {
                    'id': record[0],
                    'amount': record[1],
                    'type': record[2],
                    'status': record[3],
                    'created_at': record[4],
                    'expires_at': record[5]
                }
                for record in records
            ]
            
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """获取用户统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 获取交易统计
            cursor.execute('''
                SELECT COUNT(*) as total_trades,
                       SUM(CASE WHEN action = '买入' THEN 1 ELSE 0 END) as buy_trades,
                       SUM(CASE WHEN action = '卖出' THEN 1 ELSE 0 END) as sell_trades,
                       SUM(CASE WHEN action = '卖出' AND pnl_amount > 0 THEN 1 ELSE 0 END) as profitable_trades,
                       SUM(CASE WHEN action = '卖出' THEN pnl_amount ELSE 0 END) as total_pnl
                FROM trade_records 
                WHERE user_id = ?
            ''', (user_id,))
            
            stats = cursor.fetchone()
            
            total_trades = stats[0] or 0
            sell_trades = stats[2] or 0
            profitable_trades = stats[3] or 0
            total_pnl = stats[4] or 0
            
            win_rate = (profitable_trades / sell_trades * 100) if sell_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'buy_trades': stats[1] or 0,
                'sell_trades': sell_trades,
                'profitable_trades': profitable_trades,
                'total_pnl': total_pnl,
                'win_rate': win_rate
            }
            
        except Exception as e:
            return {
                'total_trades': 0,
                'buy_trades': 0,
                'sell_trades': 0,
                'profitable_trades': 0,
                'total_pnl': 0,
                'win_rate': 0
            }
        finally:
            conn.close()