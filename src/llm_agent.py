'''GPT-4によってアクションを生成'''
import openai
import os
import json
import logging
from dotenv import load_dotenv
from typing import Dict, Any

from src.battle_history import BattleHistory



class LLM_Agent:
  def __init__(self, model: str = 'gpt-4', temperature: float = 0.7, max_tokens: int = 50):
    load_dotenv()
    openai.api_key = os.getenv("open_API_KEY")
    self.model = model
    self.temprature = temperature
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
    prompt = self._create_prompt(battle_state, battle_history)
    self.logger.debug(f"LLM Prompt: {prompt}")

    try:
      response = await openai.ChatCompletion.acreate(
        model=self.model,
        messages = [
          {"role": "system", "content": "あなたはとても強いポケモントレーナーです"},
          {"role": "user", "content": prompt}
        ],
        max_tokens = self.max_tokens,
        temperature = self.temperature,
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


  def _get_team(self, team_builder: ConstantTeambuilder) -> Dict[str, Any]:
    """
    チーム情報を取得します。

    :param team_builder: ConstantTeambuilder オブジェクト。
    :return: チーム情報の辞書。
    """
    team = []
    for mon_str in team_builder.converted_team.split('\n'):
      mon = self._parse_mon(mon_str)
      if mon:
        team.append(mon)
    return {"pokemons": team}


  def _parse_mon(self, mon_str: str) -> Dict[str, Any]:
        """
        パイプ区切りのポケモン情報を辞書に変換します。

        :param mon_str: パイプ区切りのポケモン情報。
        :return: ポケモン情報の辞書。
        """
        parts = mon_str.split('|')
        if len(parts) < 12:
            return {}
        return {
            "nickname": parts[0] or None,
            "species": parts[1] or None,
            "item": parts[2] or None,
            "ability": parts[3] or None,
            "moves": parts[4].split(',') if parts[4] else [],
            "nature": parts[5] or None,
            "evs": [int(x) if x else 0 for x in parts[6].split(',')],
            "gender": parts[7] or None,
            "ivs": [int(x) if x else 31 for x in parts[8].split(',')],
            "shiny": 'S' in parts[9],
            "level": int(parts[10]) if parts[10] else 100,
            "happiness": int(parts[11]) if parts[11] else 70,
            "hiddenpowertype": None,  # 必要に応じて設定
            "gmax": 'G' in parts[12] if len(parts) > 12 else False,
            "tera_type": parts[13] if len(parts) > 13 else None,
        }
