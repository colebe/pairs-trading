import matplotlib.pyplot as plt

def plot_spread_and_signals(spread, signals, title="Spread & Z-score"):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(spread, label='Spread')
    ax1.set_title(title)
    ax1.set_ylabel('Spread')

    long_entries = signals['long_entry'] & ~signals['long_entry'].shift(1).fillna(False)
    short_entries = signals['short_entry'] & ~signals['short_entry'].shift(1).fillna(False)
    exits = signals['exit'] & ~signals['exit'].shift(1).fillna(False)

    ax1.plot(spread[long_entries], 'g^', label='Long Entry')
    ax1.plot(spread[short_entries], 'rv', label='Short Entry')
    ax1.plot(spread[exits], 'ko', label='Exit')

    ax1.legend()
    plt.show()