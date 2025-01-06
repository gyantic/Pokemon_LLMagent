# main.py

import asyncio
import os
import logging
from dotenv import load_dotenv

from src.teambuilder import ConstantTeambuilder
from src.llm_agent import LLM_Agent
from src.battle_history import BattleHistory

from pokemon_showdown import Client, Battle, BattleEvent

# ログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

async def main():
    # 環境変数のロード
    load_dotenv()

    # チームデータの準備（提供されたチームデータ）
    team_data = """
Dragonite @ Leftovers
Ability: Multiscale
Level: 50
Tera Type: Normal
EVs: 244 HP / 4 Atk / 140 Def / 116 SpD / 4 Spe
Adamant Nature
- Earthquake
- Extreme Speed
- Encore
- Roost

Garchomp @ Sitrus Berry
Ability: Rough Skin
Level: 50
Tera Type: Fairy
EVs: 204 HP / 92 SpD / 212 Spe
Jolly Nature
- Earthquake
- Stealth Rock
- Rock Tomb
- Spikes

Gholdengo @ Choice Specs
Ability: Good as Gold
Level: 50
Tera Type: Steel
EVs: 20 HP / 4 Def / 212 SpA / 44 SpD / 228 Spe
Modest Nature
IVs: 0 Atk
- Trick
- Shadow Ball
- Trick
- Make It Rain

Archaludon @ Air Balloon
Ability: Stamina
Level: 50
Tera Type: Steel
EVs: 188 HP / 4 Def / 196 SpA / 12 SpD / 108 Spe
Modest Nature
IVs: 0 Atk
- Body Press
- Thunderbolt
- Flash Cannon
- Roar

Ursaluna-Bloodmoon @ Assault Vest
Ability: Mind's Eye
Level: 50
Tera Type: Fairy
EVs: 196 HP / 4 Def / 204 SpA / 100 SpD / 4 Spe
Modest Nature
IVs: 0 Atk
- Blood Moon
- Moonblast
- Earth Power
- Vacuum Wave

Meowscarada @ Focus Sash
Ability: Overgrow
Level: 50
Tera Type: Dark
EVs: 252 Atk / 4 SpD / 252 Spe
Jolly Nature
- Toxic Spikes
- Taunt
- Sucker Punch
- Knock Off
    """.strip()

    # ConstantTeambuilderのインスタンスを作成
    team_builder = ConstantTeambuilder(team=team_data)

    # LLM_Agentのインスタンスを作成
    llm_agent = LLM_Agent(model='gpt-4', temperature=0.7, max_tokens=50)

    # BattleHistoryのインスタンスを作成
    battle_history = BattleHistory()

    # Pokémon Showdownクライアントの初期化
    showdown_username = os.getenv("SHOWDOWN_USERNAME")
    showdown_password = os.getenv("SHOWDOWN_PASSWORD")

    client = Client()
    await client.login(username=showdown_username, password=showdown_password)

    # バトルに参加
    battle = await client.join_battle("BSS Reg G")

    async def on_battle_start(battle: Battle):
        logger.info("バトルが開始されました。")

    async def on_turn(battle: Battle):
        # 自分のアクティブポケモンを取得
        my_pokemon = battle.my_active_pokemon
        if not my_pokemon:
            logger.warning("アクティブポケモンが見つかりません。")
            return

        # 相手のアクティブポケモンを取得
        opponent_pokemon = battle.opponent_active_pokemon
        if not opponent_pokemon:
            logger.warning("相手のアクティブポケモンが見つかりません。")
            return

        # バトルの状態を説明する文字列を作成
        battle_state = f"""
My Pokémon: {my_pokemon.species}
My HP: {my_pokemon.current_hp} / {my_pokemon.max_hp}
Opponent Pokémon: {opponent_pokemon.species}
Opponent HP: {opponent_pokemon.current_hp} / {opponent_pokemon.max_hp}
        """.strip()

        # バトル履歴を更新
        battle_history.add_event({
            "turn": battle.turn,
            "my_pokemon": my_pokemon.species,
            "opponent_pokemon": opponent_pokemon.species,
            "actions": battle.actions
        })

        # LLM_Agentを使用してアクションを決定
        action = await llm_agent.decide_action(battle_state, battle_history, team_builder)

        # 選択されたアクションに基づいて動作
        if action in my_pokemon.moves:
            logger.info(f"選択された技: {action}")
            await battle.choose_move(action)
        elif action in [mon.species for mon in team_builder.team_pokemons]:
            logger.info(f"ポケモンを交換: {action}")
            await battle.choose_switch(action)
        else:
            logger.warning(f"無効なアクション: {action}. Struggleを選択します。")
            await battle.choose_move("Struggle")

    async def on_battle_end(battle: Battle):
        logger.info("バトルが終了しました。")
        await client.disconnect()

    # イベントハンドラの登録
    client.add_event_handler("battle_start", on_battle_start)
    client.add_event_handler("turn", on_turn)
    client.add_event_handler("battle_end", on_battle_end)

    # イベントループの開始
    await client.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
