from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db import connection
import json
import traceback
from .models import (
    PlayerProfile, GameSession, ShopItem, 
    PlayerPurchase, Achievement, PlayerAchievement
)


def home(request):
    return render(request, 'game/home.html')


def handle_database_error(e):
    """處理資料庫連接錯誤，返回友好的錯誤訊息"""
    error_str = str(e).lower()
    if 'timeout' in error_str or 'connection' in error_str or 'pooler.supabase.com' in error_str:
        return '無法連接到資料庫伺服器，請稍後再試。如果問題持續存在，可能是資料庫服務暫時無法使用。'
    elif 'operationalerror' in error_str or 'database' in error_str:
        return '資料庫操作失敗，請稍後再試。'
    else:
        # 對於其他錯誤，返回原始錯誤訊息（但簡化技術細節）
        return str(e)


def get_or_create_profile(user):
    """獲取或創建玩家資料
    
    如果玩家資料不存在，則創建新的玩家資料，所有數值預設為0
    如果玩家資料已存在，則返回現有資料，不會修改任何數值
    """
    profile, created = PlayerProfile.objects.get_or_create(
        user=user,
        defaults={
            'coins': 0,
            'total_clicks': 0,
            'best_clicks_per_round': 0,
            'total_games_played': 0,
            'battle_wins': 0,
        }
    )
    return profile


@csrf_exempt
@require_http_methods(["POST"])
def api_login_or_register(request):
    """登錄或註冊用戶"""
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username:
            return JsonResponse({'error': '用戶名不能為空'}, status=400)
        
        # 嘗試獲取用戶，如果不存在則創建
        user, created = User.objects.get_or_create(username=username)
        if created:
            # 新用戶：設置不可用密碼
            user.set_unusable_password()
            user.save()
        else:
            # 已存在的用戶：如果密碼為空，設置為不可用
            # 這樣可以確保超級帳號等無密碼用戶能正常登錄
            if not user.password:
                user.set_unusable_password()
                user.save()
        
        # 登錄用戶（使用 backend 參數確保可以登錄無密碼用戶）
        # 對於無密碼用戶，必須明確指定 backend
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # 獲取或創建玩家資料
        profile = get_or_create_profile(user)
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
            },
            'profile': {
                'username': user.username,
                'created_at': profile.created_at.isoformat(),
                'battle_wins': profile.battle_wins,
                'coins': profile.coins,
                'total_clicks': profile.total_clicks,
                'best_clicks_per_round': profile.best_clicks_per_round,
                'total_games_played': profile.total_games_played,
            }
        })
    except Exception as e:
        error_message = handle_database_error(e)
        return JsonResponse({'error': error_message}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    """登出用戶"""
    try:
        logout(request)
        return JsonResponse({'success': True})
    except Exception as e:
        error_message = handle_database_error(e)
        return JsonResponse({'error': error_message}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_profile(request):
    """獲取玩家資料"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登錄'}, status=401)
    
    profile = get_or_create_profile(request.user)
    
    # 獲取玩家購買記錄（使用 select_related 優化，避免 N+1 查詢）
    purchases = PlayerPurchase.objects.filter(user=request.user).select_related('shop_item')
    player_items = {}
    for purchase in purchases:
        player_items[purchase.shop_item.item_type] = {
            'level': purchase.level,
            'effect_value': purchase.shop_item.effect_value * purchase.level
        }
    
    # 獲取已解鎖的成就（已使用 select_related 優化）
    achievements = PlayerAchievement.objects.filter(user=request.user).select_related('achievement')
    unlocked_achievements = [
        {
            'id': ach.achievement.id,
            'name': ach.achievement.name,
            'icon': ach.achievement.icon,
            'reward_claimed': ach.reward_claimed,
        }
        for ach in achievements
    ]
    
    # 獲取用戶選擇的徽章信息（優化：一次性查詢所有需要的成就和解鎖狀態）
    badge_ids = [profile.badge_1_id, profile.badge_2_id, profile.badge_3_id]
    valid_badge_ids = [bid for bid in badge_ids if bid is not None]
    
    # 一次性查詢所有需要的成就
    badge_achievements = {}
    if valid_badge_ids:
        achievements_dict = {
            ach.id: ach for ach in Achievement.objects.filter(id__in=valid_badge_ids)
        }
        # 一次性查詢所有已解鎖的成就ID
        unlocked_achievement_ids = set(
            PlayerAchievement.objects.filter(user=request.user, achievement_id__in=valid_badge_ids)
            .values_list('achievement_id', flat=True)
        )
        
        for ach_id in valid_badge_ids:
            if ach_id in achievements_dict and ach_id in unlocked_achievement_ids:
                ach = achievements_dict[ach_id]
                badge_achievements[ach_id] = {
                    'id': ach.id,
                    'icon': ach.icon,
                    'name': ach.name,
                }
    
    # 構建徽章列表
    badges = []
    for badge_id in badge_ids:
        if badge_id and badge_id in badge_achievements:
            badges.append(badge_achievements[badge_id])
        else:
            badges.append(None)
    
    return JsonResponse({
        'profile': {
            'username': request.user.username,
            'created_at': profile.created_at.isoformat(),
            'battle_wins': profile.battle_wins,
            'coins': profile.coins,
            'total_clicks': profile.total_clicks,
            'best_clicks_per_round': profile.best_clicks_per_round,
            'total_games_played': profile.total_games_played,
        },
        'purchases': player_items,
        'achievements': unlocked_achievements,
        'badges': badges,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_submit_game(request):
    """提交遊戲結果"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登錄'}, status=401)
    
    try:
        data = json.loads(request.body)
        clicks = int(data.get('clicks', 0))
        game_duration = float(data.get('game_duration', 10.0))
        
        profile = get_or_create_profile(request.user)
        
        with transaction.atomic():
            # 計算金幣
            # 基礎時間（10秒）內：每次點擊1金幣
            # 延長時間（由商店物品升級增加的秒數）內：每次點擊2金幣（基礎時間的兩倍）
            base_time = 10.0
            if game_duration <= base_time:
                # 基礎時間內的點擊，每次1金幣
                coins_earned = clicks
            else:
                # 有延長時間，需要區分基礎時間和延長時間的點擊
                # 假設點擊均勻分佈，計算基礎時間和延長時間的點擊數
                # 延長時間內的點擊獲得2倍金幣（相對於基礎時間的1金幣）
                base_clicks = int(clicks * (base_time / game_duration))
                extra_clicks = clicks - base_clicks
                coins_earned = base_clicks + (extra_clicks * 2)
            
            # 創建遊戲記錄
            session = GameSession.objects.create(
                user=request.user,
                clicks=clicks,
                game_duration=game_duration,
                coins_earned=coins_earned
            )
            
            # 更新玩家資料
            profile.coins += coins_earned
            profile.total_clicks += clicks
            profile.total_games_played += 1
            if clicks > profile.best_clicks_per_round:
                profile.best_clicks_per_round = clicks
            profile.save()
            
            # 檢查成就
            new_achievements = check_achievements(request.user, profile, clicks)
            
            # 優化：直接返回最新的歷史記錄，避免前端再次請求
            # 只查詢最新的 10 筆記錄（與前端 loadHistory 的 limit 一致）
            recent_sessions = GameSession.objects.filter(user=request.user).order_by('-played_at')[:10]
            recent_history = [
                {
                    'clicks': s.clicks,
                    'game_duration': s.game_duration,
                    'coins_earned': s.coins_earned,
                    'played_at': s.played_at.isoformat(),
                }
                for s in recent_sessions
            ]
            
        return JsonResponse({
            'success': True,
            'coins_earned': coins_earned,
            'new_achievements': new_achievements,
            'profile': {
                'username': request.user.username,
                'created_at': profile.created_at.isoformat(),
                'battle_wins': profile.battle_wins,
                'coins': profile.coins,
                'total_clicks': profile.total_clicks,
                'best_clicks_per_round': profile.best_clicks_per_round,
                'total_games_played': profile.total_games_played,
            },
            'history': recent_history,  # 包含最新歷史記錄
        })
    except Exception as e:
        error_message = handle_database_error(e)
        return JsonResponse({'error': error_message}, status=500)


def check_achievements(user, profile, current_clicks):
    """檢查並解鎖成就"""
    new_achievements = []
    
    # 獲取所有成就
    all_achievements = Achievement.objects.all()
    
    # 優化：一次性查詢所有已解鎖的成就ID，避免 N+1 查詢
    unlocked_achievement_ids = set(
        PlayerAchievement.objects.filter(user=user)
        .values_list('achievement_id', flat=True)
    )
    
    for achievement in all_achievements:
        # 檢查是否已解鎖（使用集合查找，O(1) 時間複雜度）
        if achievement.id in unlocked_achievement_ids:
            continue
        
        # 檢查是否達到目標
        unlocked = False
        if achievement.achievement_type == 'total_clicks':
            if profile.total_clicks >= achievement.target_value:
                unlocked = True
        elif achievement.achievement_type == 'single_round':
            if current_clicks >= achievement.target_value:
                unlocked = True
        elif achievement.achievement_type == 'total_games':
            if profile.total_games_played >= achievement.target_value:
                unlocked = True
        
        if unlocked:
            # 解鎖成就
            player_achievement = PlayerAchievement.objects.create(
                user=user,
                achievement=achievement,
                reward_claimed=False
            )
            
            # 自動領取獎勵
            if achievement.reward_coins > 0:
                profile.coins += achievement.reward_coins
                profile.save()
                player_achievement.reward_claimed = True
                player_achievement.save()
            
            new_achievements.append({
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'icon': achievement.icon,
                'reward_coins': achievement.reward_coins,
            })
    
    return new_achievements


@csrf_exempt
@require_http_methods(["GET"])
def api_get_shop(request):
    """獲取商店物品列表"""
    items = ShopItem.objects.all()
    shop_data = []
    
    # 優化：一次性查詢所有購買記錄，避免 N+1 查詢
    purchases_dict = {}
    extra_button_level = 0
    if request.user.is_authenticated:
        # 一次性查詢該用戶的所有購買記錄
        purchases = PlayerPurchase.objects.filter(user=request.user).select_related('shop_item')
        purchases_dict = {purchase.shop_item_id: purchase for purchase in purchases}
        
        # 檢查是否有額外點擊按鈕
        extra_button_item = ShopItem.objects.filter(item_type='extra_button').first()
        if extra_button_item and extra_button_item.id in purchases_dict:
            extra_button_level = purchases_dict[extra_button_item.id].level
    
    for item in items:
        # 從字典中獲取玩家當前等級（避免單獨查詢）
        current_level = 0
        if request.user.is_authenticated and item.id in purchases_dict:
            current_level = purchases_dict[item.id].level
        
        # 計算下一級價格（價格遞增：基礎價格 * (等級 + 1)）
        next_level_price = item.base_price * (current_level + 1) if current_level < item.max_level else None
        
        # 對於自動點擊器，檢查前置條件（需要額外點擊按鈕）
        requires_extra_button = item.item_type == 'auto_clicker'
        can_upgrade = current_level < item.max_level and next_level_price is not None
        
        # 如果沒有額外點擊按鈕且沒有自動點擊器，自動點擊器不能升級
        # 如果已經有自動點擊器（current_level > 0），則可以升級
        if requires_extra_button and extra_button_level == 0 and current_level == 0:
            can_upgrade = False
        
        # 判斷是否為未購買狀態（等級為0且未達到最大等級）
        is_unpurchased = current_level == 0 and current_level < item.max_level
        
        shop_data.append({
            'id': item.id,
            'name': item.name,
            'type': item.item_type,
            'description': item.description,
            'base_price': item.base_price,
            'effect_value': item.effect_value,
            'max_level': item.max_level,
            'current_level': current_level,
            'next_level_price': next_level_price,
            'can_upgrade': can_upgrade,
            'requires_extra_button': requires_extra_button and extra_button_level == 0 and current_level == 0,
            'is_unpurchased': is_unpurchased,
        })
    
    return JsonResponse({'items': shop_data})


@csrf_exempt
@require_http_methods(["POST"])
def api_purchase_item(request):
    """購買商店物品"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登錄'}, status=401)
    
    try:
        data = json.loads(request.body)
        item_id = int(data.get('item_id'))
        
        shop_item = ShopItem.objects.get(id=item_id)
        profile = get_or_create_profile(request.user)
        
        # 對於自動點擊器，檢查前置條件（需要額外點擊按鈕）
        if shop_item.item_type == 'auto_clicker':
            extra_button_item = ShopItem.objects.filter(item_type='extra_button').first()
            if extra_button_item:
                extra_button_purchase = PlayerPurchase.objects.filter(
                    user=request.user,
                    shop_item=extra_button_item
                ).first()
                if not extra_button_purchase or extra_button_purchase.level == 0:
                    return JsonResponse({'error': '需要先購買「額外點擊按鈕」才能購買自動點擊器'}, status=400)
        
        # 獲取當前購買記錄
        purchase = PlayerPurchase.objects.filter(user=request.user, shop_item=shop_item).first()
        current_level = purchase.level if purchase else 0
        
        if current_level >= shop_item.max_level:
            return JsonResponse({'error': '已達到最大等級'}, status=400)
        
        # 計算價格
        price = shop_item.base_price * (current_level + 1)
        
        if profile.coins < price:
            return JsonResponse({'error': '金幣不足'}, status=400)
        
        with transaction.atomic():
            # 扣除金幣
            profile.coins -= price
            profile.save()
            
            # 更新或創建購買記錄
            if purchase:
                purchase.level += 1
                purchase.price_paid = price
                purchase.save()
            else:
                purchase = PlayerPurchase.objects.create(
                    user=request.user,
                    shop_item=shop_item,
                    level=1,
                    price_paid=price
                )
            
            # 如果購買的是額外點擊按鈕，自動附加1等級的自動點擊器
            if shop_item.item_type == 'extra_button' and purchase.level == 1:
                # 檢查是否已有自動點擊器
                auto_clicker_item = ShopItem.objects.filter(item_type='auto_clicker').first()
                if auto_clicker_item:
                    auto_clicker_purchase = PlayerPurchase.objects.filter(
                        user=request.user,
                        shop_item=auto_clicker_item
                    ).first()
                    
                    # 如果沒有自動點擊器，創建1等級的自動點擊器
                    if not auto_clicker_purchase:
                        PlayerPurchase.objects.create(
                            user=request.user,
                            shop_item=auto_clicker_item,
                            level=1,
                            price_paid=0  # 免費附加
                        )
        
        return JsonResponse({
            'success': True,
            'new_level': purchase.level,
            'coins_remaining': profile.coins,
            'item_name': shop_item.name,
        })
    except ShopItem.DoesNotExist:
        return JsonResponse({'error': '物品不存在'}, status=404)
    except Exception as e:
        error_message = handle_database_error(e)
        return JsonResponse({'error': error_message}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_achievements(request):
    """獲取所有成就列表"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登錄'}, status=401)
    
    all_achievements = Achievement.objects.all()
    unlocked_ids = set(
        PlayerAchievement.objects.filter(user=request.user)
        .values_list('achievement_id', flat=True)
    )
    
    achievements_data = []
    for achievement in all_achievements:
        achievements_data.append({
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'type': achievement.achievement_type,
            'target_value': achievement.target_value,
            'reward_coins': achievement.reward_coins,
            'icon': achievement.icon,
            'unlocked': achievement.id in unlocked_ids,
        })
    
    return JsonResponse({'achievements': achievements_data})


@csrf_exempt
@require_http_methods(["GET"])
def api_get_game_history(request):
    """獲取遊戲歷史記錄"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登錄'}, status=401)
    
    limit = int(request.GET.get('limit', 10))
    # 使用 order_by 確保使用索引（模型 Meta 中已定義 ordering，但明確指定更安全）
    sessions = GameSession.objects.filter(user=request.user).order_by('-played_at')[:limit]
    
    history = [
        {
            'clicks': s.clicks,
            'game_duration': s.game_duration,
            'coins_earned': s.coins_earned,
            'played_at': s.played_at.isoformat(),
        }
        for s in sessions
    ]
    
    return JsonResponse({'history': history})


@csrf_exempt
@require_http_methods(["POST"])
def api_update_badges(request):
    """更新用戶選擇的成就徽章"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登錄'}, status=401)
    
    try:
        data = json.loads(request.body)
        badge_1_id = data.get('badge_1_id')
        badge_2_id = data.get('badge_2_id')
        badge_3_id = data.get('badge_3_id')
        
        profile = get_or_create_profile(request.user)
        
        # 驗證徽章ID是否有效且用戶已解鎖
        unlocked_achievement_ids = set(
            PlayerAchievement.objects.filter(user=request.user)
            .values_list('achievement_id', flat=True)
        )
        
        badges_to_check = [badge_1_id, badge_2_id, badge_3_id]
        for badge_id in badges_to_check:
            if badge_id is not None:
                if badge_id not in unlocked_achievement_ids:
                    return JsonResponse({'error': f'成就ID {badge_id} 尚未解鎖'}, status=400)
                if not Achievement.objects.filter(id=badge_id).exists():
                    return JsonResponse({'error': f'成就ID {badge_id} 不存在'}, status=400)
        
        # 更新徽章
        profile.badge_1_id = badge_1_id
        profile.badge_2_id = badge_2_id
        profile.badge_3_id = badge_3_id
        profile.save()
        
        # 返回更新後的徽章信息
        badge_ids = [profile.badge_1_id, profile.badge_2_id, profile.badge_3_id]
        badges = []
        for badge_id in badge_ids:
            if badge_id:
                achievement = Achievement.objects.get(id=badge_id)
                badges.append({
                    'id': achievement.id,
                    'icon': achievement.icon,
                    'name': achievement.name,
                })
            else:
                badges.append(None)
        
        return JsonResponse({
            'success': True,
            'badges': badges,
        })
    except Exception as e:
        error_message = handle_database_error(e)
        return JsonResponse({'error': error_message}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_rollback_shop_level(request):
    """回溯商店等級（僅限超級帳號）"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登錄'}, status=401)
    
    # 檢查是否為超級帳號
    if request.user.username != 'super_test':
        return JsonResponse({'error': '無權限訪問'}, status=403)
    
    try:
        data = json.loads(request.body)
        item_id = int(data.get('item_id'))
        target_level = int(data.get('target_level', 0))
        
        shop_item = ShopItem.objects.get(id=item_id)
        profile = get_or_create_profile(request.user)
        
        # 驗證目標等級範圍
        if target_level < 0 or target_level > shop_item.max_level:
            return JsonResponse({'error': f'目標等級必須在 0 到 {shop_item.max_level} 之間'}, status=400)
        
        # 獲取當前購買記錄
        purchase = PlayerPurchase.objects.filter(user=request.user, shop_item=shop_item).first()
        current_level = purchase.level if purchase else 0
        
        if target_level == current_level:
            return JsonResponse({'error': '目標等級與當前等級相同'}, status=400)
        
        with transaction.atomic():
            if target_level == 0:
                # 如果回溯到等級 0，刪除購買記錄
                if purchase:
                    purchase.delete()
            else:
                # 更新購買記錄的等級
                if purchase:
                    purchase.level = target_level
                    # 計算到目標等級的總價格（用於記錄）
                    total_price = 0
                    for level in range(target_level):
                        total_price += shop_item.base_price * (level + 1)
                    purchase.price_paid = total_price
                    purchase.save()
                else:
                    # 如果沒有購買記錄但目標等級 > 0，創建新記錄
                    total_price = 0
                    for level in range(target_level):
                        total_price += shop_item.base_price * (level + 1)
                    purchase = PlayerPurchase.objects.create(
                        user=request.user,
                        shop_item=shop_item,
                        level=target_level,
                        price_paid=total_price
                    )
        
        return JsonResponse({
            'success': True,
            'item_id': item_id,
            'item_name': shop_item.name,
            'old_level': current_level,
            'new_level': target_level,
            'message': f'已將 {shop_item.name} 從等級 {current_level} 回溯到等級 {target_level}'
        })
    except ShopItem.DoesNotExist:
        return JsonResponse({'error': '物品不存在'}, status=404)
    except ValueError as e:
        return JsonResponse({'error': '無效的參數值'}, status=400)
    except Exception as e:
        error_message = handle_database_error(e)
        return JsonResponse({'error': error_message}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_rollback_all_shop_items(request):
    """批量回溯所有商店物品到初始狀態（僅限超級帳號）"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登錄'}, status=401)
    
    # 檢查是否為超級帳號
    if request.user.username != 'super_test':
        return JsonResponse({'error': '無權限訪問'}, status=403)
    
    try:
        with transaction.atomic():
            # 獲取所有購買記錄
            purchases = PlayerPurchase.objects.filter(user=request.user)
            rolled_back_items = []
            
            for purchase in purchases:
                if purchase.level > 0:
                    rolled_back_items.append({
                        'item_name': purchase.shop_item.name,
                        'old_level': purchase.level
                    })
                    purchase.delete()
            
            return JsonResponse({
                'success': True,
                'rolled_back_count': len(rolled_back_items),
                'items': rolled_back_items,
                'message': f'已將 {len(rolled_back_items)} 個商店物品回溯到初始狀態'
            })
    except Exception as e:
        error_message = handle_database_error(e)
        return JsonResponse({'error': error_message}, status=500)