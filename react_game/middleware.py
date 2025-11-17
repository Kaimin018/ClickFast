"""
自定義中間件，用於處理 serverless 環境中的 session 錯誤
"""
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.backends.base import SessionBase
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SafeSessionMiddleware(SessionMiddleware):
    """
    安全的 Session 中間件，在資料庫連接失敗時不會導致整個請求崩潰
    
    這個中間件解決了 Django 5.x 在 serverless 環境（如 Vercel）中
    可能出現的 'SessionStore' object has no attribute '_session_cache' 錯誤
    """
    
    def process_request(self, request):
        """
        處理請求，初始化 session
        
        如果資料庫連接失敗，會優雅地處理錯誤，而不是讓整個請求崩潰
        """
        try:
            # 嘗試正常初始化 session
            super().process_request(request)
        except (AttributeError, ImproperlyConfigured) as e:
            # 處理 _session_cache 錯誤或其他 session 配置錯誤
            error_msg = str(e).lower()
            if '_session_cache' in error_msg or 'session' in error_msg:
                logger.warning(
                    f"Session 初始化失敗（可能是資料庫連接問題）: {e}",
                    exc_info=True
                )
                # 創建一個空的 session store，避免後續錯誤
                # 這會導致用戶未登錄，但至少不會讓整個請求崩潰
                session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
                request.session = self.SessionStore(session_key or None)
                # 確保 session 對象有必要的屬性
                if not hasattr(request.session, '_session_cache'):
                    request.session._session_cache = {}
            else:
                # 其他錯誤，重新拋出
                raise
        except Exception as e:
            # 其他未預期的錯誤（如資料庫連接超時）
            logger.error(
                f"Session 初始化時發生未預期錯誤: {e}",
                exc_info=True
            )
            # 創建一個空的 session store，避免後續錯誤
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            request.session = self.SessionStore(session_key or None)
            # 確保 session 對象有必要的屬性
            if not hasattr(request.session, '_session_cache'):
                request.session._session_cache = {}
    
    def process_response(self, request, response):
        """
        處理響應，保存 session
        
        如果保存失敗，記錄錯誤但不影響響應
        """
        try:
            return super().process_response(request, response)
        except Exception as e:
            # 如果保存 session 失敗，記錄錯誤但不影響響應
            logger.warning(
                f"Session 保存失敗（可能是資料庫連接問題）: {e}",
                exc_info=True
            )
            return response

