import gym
import numpy as np
import pandas as pd

class TradingEnv(gym.Env):
    """
    A basic gym environment for backtesting with historical data.
    We'll adapt for RL usage or for a custom approach.
    """

    def __init__(self, df: pd.DataFrame, initial_balance=10000):
        super(TradingEnv, self).__init__()

        # df is a pandas DataFrame with columns like:
        # ['timestamp', 'open', 'high', 'low', 'close', 'volume', ...]
        self.df = df.reset_index(drop=True)
        self.current_step = 0
        self.initial_balance = initial_balance
        self.balance = initial_balance

        # Define action space: 4 discrete actions (0=hold, 1=open long, 2=open short, 3=close)
        self.action_space = gym.spaces.Discrete(4)

        # We'll keep observation space simple: (close_price, position_size, position_type_val, balance, volume)
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(5,), dtype=np.float32
        )

        # Position tracking
        self.position_size = 0.0
        self.position_type = None  # "long" or "short"
        self.entry_price = 0.0

    def _get_observation(self):
        row = self.df.iloc[self.current_step]
        close_price = row["close"]
        volume = row["volume"]

        # Convert position_type into numeric
        if self.position_type == "long":
            position_type_val = 1.0
        elif self.position_type == "short":
            position_type_val = -1.0
        else:
            position_type_val = 0.0

        obs = np.array([
            close_price,
            self.position_size,
            position_type_val,
            self.balance,
            volume
        ], dtype=np.float32)

        return obs

    def step(self, action):
        done = False
        reward = 0.0

        row = self.df.iloc[self.current_step]
        close_price = row["close"]

        if action == 1:  # open long
            if self.position_type is None:  # Only open if no position
                self.position_type = "long"
                self.entry_price = close_price
                # Example position sizing: risk 1% of current balance
                risk_amount = self.balance * 0.01
                self.position_size = risk_amount / close_price

        elif action == 2:  # open short
            if self.position_type is None:
                self.position_type = "short"
                self.entry_price = close_price
                risk_amount = self.balance * 0.01
                self.position_size = risk_amount / close_price

        elif action == 3:  # close position
            if self.position_type is not None:
                # Calculate PnL
                if self.position_type == "long":
                    pnl = (close_price - self.entry_price) * self.position_size
                else:  # short
                    pnl = (self.entry_price - close_price) * self.position_size

                self.balance += pnl
                reward += pnl

                # Reset position
                self.position_type = None
                self.position_size = 0.0
                self.entry_price = 0.0

        # Move to next step
        self.current_step += 1
        if self.current_step >= len(self.df) - 1:
            done = True

        obs = self._get_observation()
        return obs, reward, done, {}

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.position_size = 0.0
        self.position_type = None
        self.entry_price = 0.0
        return self._get_observation()
