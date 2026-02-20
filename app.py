import streamlit as st
import pandas as pd
import yfinance as yf
import time
import requests
import re
import json
from config import HOLDINGS_COLS_MAPPING, ACTIONS_COLS_MAPPING

# 设置页面配置
st.set_page_config(page_title="Personal Portfolio Rebalancer", layout="wide")

# 常量定义
EXCEL_FILE = "my_portfolio.xlsx"
CURRENCY_PAIRS = ["CNY=X", "HKD=X"]  # 获取 USD 对 CNY 和 HKD 的汇率

# 初始化 Session State 用于缓存数据
if "rates" not in st.session_state:
    st.session_state.rates = {}
if "prices" not in st.session_state:
    st.session_state.prices = {}

def get_exchange_rates():
    """获取最新汇率 (相对于 USD)"""
    rates = {}
    try:
        tickers = yf.Tickers(" ".join(CURRENCY_PAIRS))
        for pair in CURRENCY_PAIRS:
            # yfinance 返回的是 1 USD = x Local Currency
            price = tickers.tickers[pair].history(period="1d")["Close"].iloc[-1]
            rates[pair] = price
    except Exception as e:
        st.error(f"无法获取汇率数据: {e}")
    # 填充默认值防止崩溃 (如果API完全失败)
    if "CNY=X" not in rates:
        rates["CNY=X"] = 7.25 # 保底默认值
    if "HKD=X" not in rates:
        rates["HKD=X"] = 7.80 # 保底默认值
        
    return rates

def get_ttjj_price(fund_code):
    """
    通过天天基金接口获取基金净值
    API: http://fundgz.1234567.com.cn/js/{code}.js
    返回: float or None
    """
    url = f"http://fundgz.1234567.com.cn/js/{fund_code}.js"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # 返回格式通常是: jsonpgz({"fundcode":"001156","name":"...","jzrq":"2023-11-10","dwjz":"1.2345",...});
            content = response.text
            # 使用正则提取 JSON 部分 (括号里的内容)
            match = re.search(r'jsonpgz\((.*?)\);', content)
            if match:
                json_str = match.group(1)
                data = json.loads(json_str)
                # "dwjz" 是单位净值
                return float(data.get('dwjz', 0))
    except Exception as e:
        print(f"Error fetching fund {fund_code} from TTJJ: {e}")
    return None

def get_stock_prices(ticker_list):
    """
    获取资产最新价格 (混合处理 Yahoo Finance 和 天天基金)
    规则: 
    - 6位数字 -> 天天基金 (CNY)
    - 其他 -> Yahoo Finance
    """
    prices = {}
    if not ticker_list:
        return prices
        
    yf_tickers = []
    
    # 1. 分类 Ticker
    for ticker in ticker_list:
        str_ticker = str(ticker).strip()
        
        # 尝试补全前导零 (如果看起来像数字且长度小于6)
        if str_ticker.isdigit() and len(str_ticker) < 6:
             str_ticker = str_ticker.zfill(6)

        # 简单判断: 6位纯数字认为是国内基金代码 (天天基金)
        if re.match(r'^\d{6}$', str_ticker):
            price = get_ttjj_price(str_ticker)
            if price is not None:
                prices[str_ticker] = price
            else:
                prices[str_ticker] = 0.0
                print(f"Failed to fetch price for {str_ticker} from TTJJ")
        else:
            yf_tickers.append(str_ticker)
            
    # 2. 批量获取 Yahoo Finance 数据
    if yf_tickers:
        try:
            # download 5 days to ensure we get the last valid close even if markets are out of sync
            data = yf.download(yf_tickers, period="5d", group_by='ticker', progress=False)

            if len(yf_tickers) == 1:
                ticker = yf_tickers[0]
                # Single ticker: DataFrame cols are Open, High, Low, Close...
                if 'Close' in data.columns:
                    series = data['Close'].dropna()
                    if not series.empty:
                        prices[ticker] = series.iloc[-1].item()
            else:
                # Multiple tickers: Columns are MultiIndex (Ticker, PriceType)
                for ticker in yf_tickers:
                    try:
                        # 对于 MultiIndex, data[ticker] 取出该 ticker 的 DataFrame
                        if ticker in data.columns:
                            df_ticker = data[ticker]
                            if 'Close' in df_ticker.columns:
                                series = df_ticker['Close'].dropna()
                                if not series.empty:
                                    prices[ticker] = series.iloc[-1].item()
                    except Exception as e:
                        print(f"Error processing {ticker} in YF data: {e}")

        except Exception as e:
            st.error(f"无法获取 Yahoo Finance 股价数据: {e}")
            
    return prices

def load_portfolio():
    """加载 Excel 配置文件"""
    try:
        # 强制读取 Ticker 为字符串，保留前导零 (例如 001632)
        return pd.read_excel(EXCEL_FILE, dtype={'Ticker': str})
    except FileNotFoundError:
        st.error(f"未找到配置文件 {EXCEL_FILE}，请先运行 generate_data.py 生成。")
        return pd.DataFrame()

# --- 侧边栏 ---
st.sidebar.title("设置与输入")

if st.sidebar.button("刷新数据 (Reload Data)"):
    st.cache_data.clear()
    st.rerun()

cash_injection = st.sidebar.number_input(
    "本期投入现金 (USD)", 
    min_value=0.0, 
    value=1000.0, 
    step=100.0,
    help="计划新投入的资金，单位：美元"
)

# --- 主界面 ---
st.title("💰 组合再平衡仪表盘 (USD 本位)")

# 1. 加载数据
df = load_portfolio()
if df.empty:
    st.stop()

# 2. 获取实时数据
with st.spinner('正在获取最新市场数据...'):
    # 获取汇率
    rates = get_exchange_rates() 
    usd_cny = rates.get("CNY=X", 7.25)
    usd_hkd = rates.get("HKD=X", 7.80)

    # 获取股价
    tickers = df['Ticker'].tolist()
    # 调用新的混合获取函数
    prices = get_stock_prices(tickers)

# 3. 计算资产价值
current_values_usd = []
current_prices = []

for index, row in df.iterrows():
    ticker = str(row['Ticker']).strip()
    shares = row['Shares']
    currency = row['Currency']
    
    # 获取当前价格
    price = prices.get(ticker, 0.0)
    current_prices.append(price)
    
    # 计算市值 (本地货币)
    market_val_local = price * shares
    
    # 转换为 USD
    if currency == 'USD':
        market_val_usd = market_val_local
    elif currency == 'HKD':
        market_val_usd = market_val_local / usd_hkd
    elif currency == 'CNY':
        market_val_usd = market_val_local / usd_cny
    else:
        market_val_usd = 0.0 # 未知货币
    
    current_values_usd.append(market_val_usd)

df['Current_Price'] = current_prices
df['Market_Value_USD'] = current_values_usd

# 4. 计算总资产与目标
total_asset_usd = df['Market_Value_USD'].sum()
new_total_equity = total_asset_usd + cash_injection

# 5. 计算再平衡与操作建议
target_values = []
actions = []
action_shares_list = []

for index, row in df.iterrows():
    ticker = row['Ticker']
    price = row['Current_Price']
    currency = row['Currency']
    
    # 目标市值
    target_val = new_total_equity * row['Target_Pct']
    target_values.append(target_val)
    
    # 缺口 (Gap)
    current_val = row['Market_Value_USD']
    gap_usd = target_val - current_val
    
    # 建议操作 (买入/卖出)
    # 将缺口 USD 转回本地货币以计算股数
    if currency == 'USD':
        gap_local = gap_usd
        buy_price = price
    elif currency == 'HKD':
        gap_local = gap_usd * usd_hkd
        buy_price = price
    elif currency == 'CNY':
        gap_local = gap_usd * usd_cny
        buy_price = price
    else:
        gap_local = 0
        buy_price = 1

    # 计算建议股数 (向下取整，避免超买，美股可包含小数但这里简单处理为整数显示，实际交易可微调)
    if buy_price > 0:
        action_shares = gap_local / buy_price
    else:
        action_shares = 0
        
    actions.append(gap_usd)
    action_shares_list.append(action_shares)

df['Target_Value_USD'] = target_values
df['Gap_USD'] = actions
df['Action_Shares'] = action_shares_list

# --- 模块 A: 资产概览 ---
col1, col2, col3 = st.columns(3)
col1.metric("当前持仓总市值 (USD)", f"${total_asset_usd:,.2f}")
col2.metric("新投入资金 (USD)", f"${cash_injection:,.2f}")
col3.metric("预估新总资产 (USD)", f"${new_total_equity:,.2f}")

st.markdown("---")

# --- 模块 B: 持仓详情 ---
st.subheader("📊 持仓详情 (Holdings)")

# 格式化显示列
display_df = df.copy()
display_df['Current_Pct'] = display_df['Market_Value_USD'] / total_asset_usd

# 添加'Name'列，确保如果Excel中没有Name列也不会报错（兼容旧文件）
if 'Name' not in display_df.columns:
    display_df['Name'] = display_df['Ticker']

display_df = display_df[['Name', 'Ticker', 'Shares', 'Current_Price', 'Market_Value_USD', 'Current_Pct', 'Target_Pct', 'Gap_USD']]

# 重命名列头为中文
display_df.rename(columns=HOLDINGS_COLS_MAPPING, inplace=True)

# 样式设置
def highlight_gap(val):
    color = 'red' if val < 0 else 'green'
    return f'color: {color}'

st.dataframe(
    display_df.style.format({
        HOLDINGS_COLS_MAPPING.get('Current_Price', 'Current_Price'): '{:.3f}',
        HOLDINGS_COLS_MAPPING.get('Market_Value_USD', 'Market_Value_USD'): '${:,.2f}',
        HOLDINGS_COLS_MAPPING.get('Current_Pct', 'Current_Pct'): '{:.1%}',
        HOLDINGS_COLS_MAPPING.get('Target_Pct', 'Target_Pct'): '{:.1%}',
        HOLDINGS_COLS_MAPPING.get('Gap_USD', 'Gap_USD'): '${:+,.2f}'
    }).applymap(highlight_gap, subset=[HOLDINGS_COLS_MAPPING.get('Gap_USD', 'Gap_USD')])
)

# --- 模块 C: 操作建议 ---
st.subheader("📋 操作建议 (Rebalance Actions)")

action_df = df.copy()

# 添加'Name'列兼容性
if 'Name' not in action_df.columns:
    action_df['Name'] = action_df['Ticker']

action_df = action_df[['Name', 'Ticker', 'Currency', 'Current_Price', 'Gap_USD', 'Action_Shares']]

# 仅显示需要操作的行（通过设置阈值，比如变动超过 10 美元）
action_df = action_df[abs(action_df['Gap_USD']) > 10]

def make_action_text(row):
    shares = row['Action_Shares']
    if shares > 0:
        return f"🔵 买入 {shares:.2f} 股"
    else:
        return f"🔴 卖出 {abs(shares):.2f} 股"

if not action_df.empty:
    action_df['Suggestion'] = action_df.apply(make_action_text, axis=1)
    
    # 准备展示数据并重命名
    final_action_df = action_df[['Ticker', 'Suggestion', 'Gap_USD', 'Currency']].rename(
        columns=ACTIONS_COLS_MAPPING
    )
    
    st.table(final_action_df)
else:
    st.info("✅ 当前持仓已非常接近目标比例，无需操作。")

# 调试信息 (可选)
with st.expander("查看汇率信息"):
    st.write(f"USD/CNY Rate: {usd_cny:.4f}")
    st.write(f"USD/HKD Rate: {usd_hkd:.4f}")
