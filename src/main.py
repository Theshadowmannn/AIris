import pandas as pd
import logging
from pathlib import Path

from src.data_fetcher import DataFetcher
from src.environment import TradingEnv

# If you plan to use stable-baselines3:
# from stable_baselines3 import PPO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting AIris...")

    data_fetcher = DataFetcher()

    # Example: fetch coingecko data for Bitcoin (past 30 days)
    cg_data = data_fetcher.get_coingecko_history(coin_id="bitcoin", vs_currency="usd", days=30)

    if cg_data and "prices" in cg_data:
        price_data = cg_data["prices"]  # list of [timestamp, price]
        df = pd.DataFrame(price_data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.rename(columns={"price": "close"})
        # Create dummy OHLC and volume
        df["open"] = df["close"]
        df["high"] = df["close"]
        df["low"] = df["close"]
        df["volume"] = 1000  # placeholder

        # Initialize environment
        env = TradingEnv(df, initial_balance=10000)

        # Example random actions just to demonstrate environment usage
        obs = env.reset()
        done = False
        total_reward = 0.0

        while not done:
            action = env.action_space.sample()  # random
            obs, reward, done, info = env.step(action)
            total_reward += reward

        logger.info(f"Finished random policy. Final Reward: {total_reward:.2f} | Final Balance: {env.balance:.2f}")
    else:
        logger.warning("Coingecko data was not fetched properly. Check your API keys or network.")

if __name__ == "__main__":
    main()
