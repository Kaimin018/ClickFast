"""
設置社交登入應用
自動配置 Google、Facebook、Instagram 等社交登入應用
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = '設置社交登入應用（Google、Facebook、Instagram）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--site-domain',
            type=str,
            default='127.0.0.1:8000',
            help='Site 域名（預設: 127.0.0.1:8000）'
        )
        parser.add_argument(
            '--use-env',
            action='store_true',
            help='從環境變數讀取 Client ID 和 Secret'
        )

    def handle(self, *args, **options):
        site_domain = options['site_domain']
        use_env = options['use_env']

        self.stdout.write('正在設置社交登入應用...')

        # 確保 Site 存在
        site, created = Site.objects.get_or_create(
            domain=site_domain,
            defaults={'name': 'ClickFast Site'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ 創建 Site: {site_domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Site 已存在: {site_domain}'))

        # 定義社交應用配置
        social_apps_config = [
            {
                'provider': 'google',
                'name': 'Google',
                'client_id_env': 'GOOGLE_CLIENT_ID',
                'secret_env': 'GOOGLE_CLIENT_SECRET',
                'default_client_id': 'your_google_client_id_here',
                'default_secret': 'your_google_secret_here',
            },
            {
                'provider': 'facebook',
                'name': 'Facebook',
                'client_id_env': 'FACEBOOK_CLIENT_ID',
                'secret_env': 'FACEBOOK_CLIENT_SECRET',
                'default_client_id': 'your_facebook_app_id_here',
                'default_secret': 'your_facebook_secret_here',
            },
            {
                'provider': 'instagram',
                'name': 'Instagram',
                'client_id_env': 'INSTAGRAM_CLIENT_ID',
                'secret_env': 'INSTAGRAM_CLIENT_SECRET',
                'default_client_id': 'your_instagram_client_id_here',
                'default_secret': 'your_instagram_secret_here',
            },
        ]

        for app_config in social_apps_config:
            provider = app_config['provider']
            
            # 獲取 Client ID 和 Secret
            if use_env:
                client_id = os.getenv(app_config['client_id_env'], '')
                secret = os.getenv(app_config['secret_env'], '')
            else:
                client_id = app_config['default_client_id']
                secret = app_config['default_secret']

            # 如果使用環境變數但沒有設置，跳過
            if use_env and (not client_id or not secret):
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ 跳過 {app_config["name"]}：環境變數 {app_config["client_id_env"]} 或 {app_config["secret_env"]} 未設置'
                    )
                )
                continue

            # 創建或更新 SocialApp
            app, created = SocialApp.objects.get_or_create(
                provider=provider,
                defaults={
                    'name': app_config['name'],
                    'client_id': client_id,
                    'secret': secret,
                }
            )

            if not created:
                # 如果已存在，更新配置
                app.name = app_config['name']
                app.client_id = client_id
                app.secret = secret
                app.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 更新 {app_config["name"]} 應用配置')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 創建 {app_config["name"]} 應用')
                )

            # 確保應用已添加到 Site
            if site not in app.sites.all():
                app.sites.add(site)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 將 {app_config["name"]} 添加到 Site')
                )

            # 檢查是否為預設值（需要用戶配置）
            if client_id == app_config['default_client_id']:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ {app_config["name"]} 使用預設值，請在 Django Admin 中更新 Client ID 和 Secret'
                    )
                )

        self.stdout.write(self.style.SUCCESS('\n社交登入應用設置完成！'))
        self.stdout.write(
            self.style.WARNING(
                '\n重要提示：\n'
                '1. 如果使用預設值，請前往 Django Admin (http://127.0.0.1:8000/admin/) 更新 Client ID 和 Secret\n'
                '2. 或使用 --use-env 參數從環境變數讀取配置\n'
                '3. 需要從各平台獲取 OAuth 憑證，詳見 guidance/social-login-setup.md'
            )
        )

