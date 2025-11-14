from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from game.models import (
    PlayerProfile, ShopItem, PlayerPurchase, 
    Achievement, PlayerAchievement
)
from django.db import transaction


class Command(BaseCommand):
    help = '創建超級帳號，用於測試成就系統和商店物品功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='super_test',
            help='超級帳號的用戶名（預設: super_test）'
        )
        parser.add_argument(
            '--coins',
            type=int,
            default=1000000,
            help='初始金幣數量（預設: 1000000）'
        )

    def handle(self, *args, **options):
        username = options['username']
        coins = options['coins']

        self.stdout.write(f'正在創建超級帳號: {username}...')

        with transaction.atomic():
            # 創建或獲取用戶
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_unusable_password()
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ 創建用戶: {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ 用戶已存在: {username}，將更新資料'))

            # 創建或更新玩家資料
            profile, profile_created = PlayerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'coins': coins,
                    'total_clicks': 50000,
                    'best_clicks_per_round': 500,
                    'total_games_played': 200,
                    'battle_wins': 50,
                }
            )
            
            if not profile_created:
                # 如果資料已存在，更新為超級帳號數值
                profile.coins = coins
                profile.total_clicks = 50000
                profile.best_clicks_per_round = 500
                profile.total_games_played = 200
                profile.battle_wins = 50
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'✓ 更新玩家資料'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ 創建玩家資料'))

            # 購買所有商店物品到最高等級
            shop_items = ShopItem.objects.all()
            total_cost = 0
            
            for item in shop_items:
                # 計算購買到最高等級的總成本
                # 價格計算：base_price * (level + 1)
                cost = 0
                for level in range(item.max_level):
                    cost += item.base_price * (level + 1)
                
                # 獲取或創建購買記錄
                purchase, purchase_created = PlayerPurchase.objects.get_or_create(
                    user=user,
                    shop_item=item,
                    defaults={
                        'level': item.max_level,
                        'price_paid': cost,
                    }
                )
                
                if not purchase_created:
                    # 如果已存在，更新到最高等級
                    purchase.level = item.max_level
                    purchase.price_paid = cost
                    purchase.save()
                
                total_cost += cost
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ 購買物品: {item.name} (等級 {item.max_level}/{item.max_level})'
                    )
                )

            # 扣除購買成本（如果金幣不足，則不扣除，因為這是測試帳號）
            if profile.coins >= total_cost:
                profile.coins -= total_cost
            else:
                # 如果金幣不足，直接設置為足夠的金幣
                profile.coins = coins
            profile.save()

            # 解鎖所有成就
            achievements = Achievement.objects.all()
            unlocked_count = 0
            
            for achievement in achievements:
                player_achievement, created = PlayerAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement,
                    defaults={
                        'reward_claimed': True,  # 標記為已領取獎勵
                    }
                )
                if created:
                    unlocked_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ 解鎖成就: {achievement.name}')
                    )

            self.stdout.write(self.style.SUCCESS(
                f'\n超級帳號創建完成！\n'
                f'用戶名: {username}\n'
                f'金幣: {profile.coins:,}\n'
                f'總點擊: {profile.total_clicks:,}\n'
                f'單局最佳: {profile.best_clicks_per_round}\n'
                f'遊戲局數: {profile.total_games_played}\n'
                f'購買物品數: {shop_items.count()}\n'
                f'解鎖成就數: {unlocked_count}\n'
            ))

