import pandas as pd
import os

# 定义初始持仓数据
# Ticker: 股票代码 (美股直接写代码，港股加.HK，A股加.SS/.SZ)
# Shares: 持仓数量
# Avg_Cost: 平均成本 (仅用于记录，不影响调仓计算)
# Target_Pct: 目标仓位比例 (所有项之和最好为1.0)
# Currency: 资产计价货币 (USD, HKD, CNY)
data = {
    'Ticker': [
        # USD holdings
        'VOO', 'NVDA', 'AAPL', 'TLT',
        # HK holdings (Requires .HK suffix)
        '0700.HK', '09988.HK', 
        # CNY holdings (Domestic Mutual Funds - 6 digits, fetched from TianTian Fund)
        '001632', '005827',
        # CNY holdings (Exchange Traded - require .SS/.SZ suffix, fetched from Yahoo)
        '600519.SS' 
    ],
    'Name': [
        # USD holdings
        'Vanguard S&P 500', 'NVIDIA', 'Apple', '20+ Year Treasury Bond',
        # HK holdings
        'Tencent (腾讯)', 'Alibaba (阿里)',
        # CNY holdings
        '天弘中证食品饮料ETF联接C', '易方达蓝筹精选混合',
        '贵州茅台'
    ],
    'Shares': [
        10, 5, 20, 10,
        100, 100, 
        1000, 500, 
        100
    ],
    'Avg_Cost': [0.0] * 9,
    'Target_Pct': [0.15, 0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    'Currency': [
        'USD','USD','USD','USD', 
        'HKD','HKD',             
        'CNY','CNY','CNY'
    ]
    
}

# 转换为 DataFrame
df = pd.DataFrame(data)

# 文件名
file_name = 'my_portfolio.xlsx'

# 检查文件是否存在，避免覆盖用户数据
if not os.path.exists(file_name):
    try:
        df.to_excel(file_name, index=False)
        print(f"✅ 成功创建初始配置文件: {file_name}")
        print("请打开该 Excel 文件，修改您的实际持仓和目标比例。")
    except Exception as e:
        print(f"❌ 创建文件失败: {e}")
else:
    print(f"ℹ️ 文件 {file_name} 已存在，跳过创建。")
