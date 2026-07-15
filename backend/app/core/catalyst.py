# SentinelsAI - Zoho Catalyst SDK Helper
from app.core.config import settings


def get_catalyst_app():
    try:
        from zcatalyst import app as catalyst_app
        app = catalyst_app.initialize_app(
            {
                "project_id": settings.CATALYST_PROJECT_ID,
                "client_id": settings.CATALYST_CLIENT_ID,
                "client_secret": settings.CATALYST_CLIENT_SECRET,
                "refresh_token": settings.CATALYST_REFRESH_TOKEN,
                "region": settings.CATALYST_REGION,
            }
        )
        return app
    except ImportError:
        return None
    except Exception:
        return None


def get_stratus_bucket(bucket_name: str = "sentinelai-evidence"):
    app = get_catalyst_app()
    if app:
        try:
            from zcatalyst import stratus
            return stratus.bucket(app, bucket_name)
        except ImportError:
            return None
    return None


def get_catalyst_user_info(request):
    try:
        from zcatalyst.auth import authenticated_user
        return authenticated_user.get_user_details(request)
    except ImportError:
        return None
    except Exception:
        return None
