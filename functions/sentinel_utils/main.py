import json
import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def handler(event, context):
    try:
        data = json.loads(event.get("body", "{}"))
        token = data.get("access_token", "")
        action = data.get("action", "")

        headers = {"Authorization": f"Bearer {token}"}

        if action == "db_stats":
            resp = httpx.get(f"{BACKEND_URL}/api/v1/admin/system/health", headers=headers, timeout=10)
            return resp.json() if resp.status_code == 200 else {"status": "error", "message": str(resp.status_code)}

        if action == "export_csv":
            resource_type = data.get("resource_type", "cases")
            resp = httpx.post(
                f"{BACKEND_URL}/api/v1/export/csv/{resource_type}",
                headers=headers, timeout=30,
            )
            if resp.status_code == 200:
                import base64
                return {
                    "status": "success",
                    "content_type": resp.headers.get("content-type", "text/csv"),
                    "content_base64": base64.b64encode(resp.content).decode(),
                    "filename": resp.headers.get("content-disposition", f"export-{resource_type}.csv"),
                }
            return {"status": "error", "message": f"Backend returned {resp.status_code}"}

        return {"status": "success", "message": f"Utils function invoked: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
