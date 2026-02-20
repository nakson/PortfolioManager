# 表头显示映射配置

# 持仓详情表头映射
HOLDINGS_COLS_MAPPING = {
    'Name': '名称',
    'Ticker': '代码',
    'Shares': '持仓股数',
    'Current_Price': '当前价格',
    'Market_Value_USD': '市值 (USD)',
    'Current_Pct': '当前占比',
    'Target_Pct': '目标占比',
    'Gap_USD': '调仓缺口 (USD)'
}

# 操作建议表头映射
ACTIONS_COLS_MAPPING = {
    'Name': '名称',
    'Ticker': '代码',
    'Suggestion': '操作建议',
    'Gap_USD': '资金变动 (USD)',
    'Currency': '原币种'
}
