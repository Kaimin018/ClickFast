from django.core.management.base import BaseCommand
from game.models import ShopItem, Achievement


class Command(BaseCommand):
    help = '初始化遊戲數據（商店物品和成就）'

    def handle(self, *args, **options):
        self.stdout.write('Initializing game data...')

        # 創建商店物品
        shop_items = [
            {
                'name': '遊戲時間延長',
                'item_type': 'time_extension',
                'description': '增加遊戲時間，每次升級增加2秒。延長時間內點擊獲得的金幣為兩倍',
                'base_price': 50,
                'effect_value': 2.0,  # 每次升級增加2秒
                'max_level': 10,
            },
            {
                'name': '額外點擊按鈕',
                'item_type': 'extra_button',
                'description': '增加額外的點擊按鈕，每次升級增加1個按鈕。首次購買時會自動獲得1等級的自動點擊器',
                'base_price': 100,
                'effect_value': 1.0,  # 每次升級增加1個按鈕
                'max_level': 5,
            },
            {
                'name': '自動點擊器',
                'item_type': 'auto_clicker',
                'description': '自動點擊器：Lv.1每3秒點擊1次，Lv.2每2秒點擊1次，Lv.3每1秒點擊1次，Lv.4+每秒點擊(等級-2)次。需要先購買「額外點擊按鈕」才能購買',
                'base_price': 200,
                'effect_value': 5.0,  # 此值不再使用，頻率由等級直接計算
                'max_level': 10,
            },
        ]

        for item_data in shop_items:
            item, created = ShopItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created shop item: {item.name}'))
            else:
                # 更新現有物品的描述和其他可更新字段
                updated = False
                if item.description != item_data['description']:
                    item.description = item_data['description']
                    updated = True
                if item.base_price != item_data['base_price']:
                    item.base_price = item_data['base_price']
                    updated = True
                if item.effect_value != item_data['effect_value']:
                    item.effect_value = item_data['effect_value']
                    updated = True
                if item.max_level != item_data['max_level']:
                    item.max_level = item_data['max_level']
                    updated = True
                if updated:
                    item.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated shop item: {item.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Shop item already exists: {item.name}'))

        # 創建成就
        achievements = [
            {
                'name': '初出茅廬',
                'description': '總點擊次數達到100次',
                'achievement_type': 'total_clicks',
                'target_value': 100,
                'reward_coins': 50,
                'icon': '🎯',
            },
            {
                'name': '點擊達人',
                'description': '總點擊次數達到1000次',
                'achievement_type': 'total_clicks',
                'target_value': 1000,
                'reward_coins': 500,
                'icon': '🔥',
            },
            {
                'name': '點擊大師',
                'description': '總點擊次數達到10000次',
                'achievement_type': 'total_clicks',
                'target_value': 10000,
                'reward_coins': 5000,
                'icon': '👑',
            },
            {
                'name': '單局突破',
                'description': '單局點擊超過50次',
                'achievement_type': 'single_round',
                'target_value': 50,
                'reward_coins': 100,
                'icon': '⚡',
            },
            {
                'name': '單局高手',
                'description': '單局點擊超過100次',
                'achievement_type': 'single_round',
                'target_value': 100,
                'reward_coins': 500,
                'icon': '💪',
            },
            {
                'name': '單局傳奇',
                'description': '單局點擊超過200次',
                'achievement_type': 'single_round',
                'target_value': 200,
                'reward_coins': 2000,
                'icon': '🌟',
            },
            {
                'name': '遊戲新手',
                'description': '完成10局遊戲',
                'achievement_type': 'total_games',
                'target_value': 10,
                'reward_coins': 100,
                'icon': '🎮',
            },
            {
                'name': '遊戲老手',
                'description': '完成50局遊戲',
                'achievement_type': 'total_games',
                'target_value': 50,
                'reward_coins': 500,
                'icon': '🏅',
            },
            {
                'name': '遊戲大師',
                'description': '完成100局遊戲',
                'achievement_type': 'total_games',
                'target_value': 100,
                'reward_coins': 2000,
                'icon': '🏆',
            },
        ]

        for ach_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=ach_data['name'],
                defaults=ach_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created achievement: {achievement.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Achievement already exists: {achievement.name}'))

        self.stdout.write(self.style.SUCCESS('\nGame data initialization completed!'))
