'''GPT-4によってアクションを生成'''
import openai
import os
import json
import logging
from dotenv import load_dotenv
from typing import Dict, Any

from src.battle_history import BattleHistory



class LLM_Agent:
  def __init__(self, model: str = 'gpt-4', temprature: float = 0.7, max_tokens: int = 50):
    load_dotenv()
    openai.api_key = os.getenv("open_API_KEY")
    self.model = model
    self.temprature = temprature
    self.max_tokens = max_tokens
    self.logger = logging.getLogger("LLM_Agent")
    if not self.logger.handlers:
      handler = logging.StreamHandler()
      formatter = logging.Formatter(
         "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      )
      handler.setFormatter(formatter)
      self.logger.addHandler(handler)
      self.logger.setLevel(logging.INFO)

  def load_team(self, filepath: str) -> Dict[str, Any]:
    """
    ファイルからチームを読み込む
    """
    with open(filepath, 'r') as f:
      data = json.load(f)
    return data.get("team", [])

  async def decide_action(self, battle_state : str, battle_history: BattleHistory) -> str:
    """
    バトル状況とバトル履歴に基づいて最適なアクションを決定します。

    :param battle_state: 現在のバトル状況を説明する文字列。
    :param battle_history: BattleHistory オブジェクト。
    :return: 選択されたアクション。
    """
    prompt = self._create_prpmpt(battle_state, battle_history)
    self.logger.debug(f"LLM Prompt: {prompt}")

    try:
      response = await openai.ChatCompletion.acreate(
        model=self.model,
        messages = [
          {"role": "system", "content": "あなたはとても強いポケモントレーナーです"},
          {"role": "user", "content": prompt}
        ],
        max_tokens = self.max_tokens,
        temprature = self.temprature,
      )
      action = response.choices[0].message['content'].strip()
      self.logger.info(f"LLM selected action: {action}")
      return action
    except Exception as e:
      self.logger.error(f"Error with API: {e}")
      return "Struggle" #default action


  def _create_prompt(self, battle_state: str, battle_history: BattleHistory) -> str:
    """
    GPTモデルに送信するプロンプトを作成。
    :param battle_state: 現在のバトル状況を説明する文字列。
    :param battle_history: BattleHistory オブジェクト。
    :return: GPTモデルに送信するプロンプト。
    """
    prompt = f"""
team: {json.dumps(self._get_team(), encure_acsii=False, indent = 2)}

Battle History: {json.dumps(battle_history.history, ensure_ascii=False, indent=2)
}

Current State of Battle: {battle_state}

Choose one of the nest actions(technique, Pokemon to exchange) to take next. The action should be ancwered with the name of the technique or the name of Pokemon to exchange.
    """
    return prompt
