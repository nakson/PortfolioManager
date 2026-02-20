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
        'AXP','BND','COST','GOOG','IWY','MOAT','NFLX','NVDA','O','PFF','VEA','VGSH','VOO',
        'CRYPTO_STABLE','CRYPTO_COINS',
        # HK holdings (已加 .HK)
        '02269.HK','02331.HK','03288.HK','09618.HK',
        # CNY holdings (原始代码保留，按需后续加 .SS/.SZ)
        '001632','010955','00968','01005','006484','007540','160424','007339','010365','001691',
        '023884','022365','019891','011840','005693','020256'
    ],
    'Name': [
        # USD holdings
        '美国运通','美全债指数','好市多','谷歌','IWY','MOAT','Netflix','NVIDIA','Realty Income','PFF','VEA','VGSH','VOO',
        'crypto_稳定币','crypto_coins',
        # HK holdings
        '药明生物','李宁','海天味业','京东集团',
        # CNY holdings
        '天弘中证食品饮料ETF联接C','天弘中证智能汽车指数发起式A','广发养老指数A','汇添富中证精准医疗指数(LOF)A',
        '广发中债1-3年国开债指数A','华泰保兴安悦债券A','华安创业板50ETF联接C','易方达沪深300ETF联接C',
        '鹏华中证香港银行指数(LOF)C','南方香港成长灵活配置混合','华夏中证金融科技主题ETF发起式联接A','永赢科技智选混合发起C',
        '华夏中证2000ETF发起式联接A','天弘中证人工智能C','广发中证军工ETF联接C','中欧中证机器人指数发起C'
    ],
    'Shares': [0]* (15 + 4 + 16),  # 以上 Ticker 数量的占位 0（请确保长度匹配）
    'Avg_Cost': [0.0] * (15 + 4 + 16),
    'Target_Pct': [0.0] * (15 + 4 + 16),
    'Currency': [
        # USD group    
        'USD','USD','USD','USD','USD','USD','USD','USD','USD','USD','USD','USD','USD', 
        'USD','USD',
        # HK group
        'HKD','HKD','HKD','HKD',             
        # CNY group
        'CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY','CNY'
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
