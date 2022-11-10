def cppi(risky_r, safe_r=None, m=3, start=1000, floor=0.8, riskfree_rate=0.035, drawdown=None):

    dates = risky_r.index
    n_steps = len(dates)
    account_value = start
    floor_value = start * floor
    peak = account_value

    if isinstance(risky_r, pd.Series):  # in that case we can work with not only DataFrames but also with Series.
        risky_r = pd.DataFrame(risky_r, columns=["R"])

    if safe_r is None:
        safe_r = pd.DataFrame().reindex_like(risky_r)
        safe_r.values[:] = riskfree_rate / 252

    # History
    account_history = pd.DataFrame().reindex_like(risky_r)
    risky_w_history = pd.DataFrame().reindex_like(risky_r)
    cushion_history = pd.DataFrame().reindex_like(risky_r)
    floorval_history = pd.DataFrame().reindex_like(risky_r)
    peak_history = pd.DataFrame().reindex_like(risky_r)

    for step in range(n_steps):

        if drawdown is not None:
            peak = np.maximum(peak, account_value)
            floor_value = peak * (1 - drawdown)

        cushion = (account_value - floor_value) / account_value
        risky_w = m * cushion
        risky_w = np.minimum(risky_w, 1)  # to avoid leveraging the money
        risky_w = np.maximum(risky_w, 0)  # well, that just makes sense, we cannot invest negative values

        safe_w = 1 - risky_w
        risky_alloc = account_value * risky_w
        safe_alloc = account_value * safe_w

        # recomputing value of account i.e. invest money with respect to returns
        account_value = risky_alloc * (1 + risky_r.iloc[step]) + safe_alloc * (1 + safe_r.iloc[step])

        # collecting  data for the history
        cushion_history.iloc[step] = cushion
        risky_w_history.iloc[step] = risky_w
        account_history.iloc[step] = account_value
        floorval_history.iloc[step] = floor_value
        peak_history.iloc[step] = peak

    risky_wealth = start * (1 + risky_r).cumprod()

    backtest_result = {
                        "Wealth": account_history,           # Asset Value History
                        "Risky Wealth": risky_wealth,
                        "Risk Budget": cushion_history,      # Risk Budget History
                        "Risky Allocation": risky_w_history, # Risky Weight History
                        "m": m,
                        "start": start,
                        "floor": floor,
                        "risky_r": risky_r,
                        "safe_r": safe_r,
                        "drawdown": drawdown,
                        "peak": peak_history,
                        "floor": floorval_history
                        }
    return backtest_result
