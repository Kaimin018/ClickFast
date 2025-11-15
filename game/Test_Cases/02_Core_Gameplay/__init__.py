"""
核心遊戲玩法測試模組
測試遊戲核心機制：點擊、計時、金幣計算、記錄更新等
"""

from .TC_GAME_001_Game_Flow import GameFlowTestCase
from .TC_GAME_002_Coin_Calculation import CoinCalculationTestCase
from .TC_GAME_003_Record_Update import RecordUpdateTestCase
from .TC_GAME_004_Game_History import GameHistoryTestCase

__all__ = [
    'GameFlowTestCase',
    'CoinCalculationTestCase',
    'RecordUpdateTestCase',
    'GameHistoryTestCase',
]

