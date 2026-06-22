import json
import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def handler(event, context):
    try:
        data = json.loads(event.get("body", "{}"))
        report_type = data.get("report_type", "csv")
        session_id = data.get("session_id", "unknown")
        resource_type = data.get("resource_type", "cases")
        token = data.get("access_token", "")

        headers = {"Authorization": f"Bearer {token}"}

        if report_type == "pdf":
            resp = httpx.post(
                f"{BACKEND_URL}/api/v1/export/pdf",
                json={"session_id": session_id, "case_ids": data.get("case_ids", [])},
                headers=headers,
                timeout=30,
            )
        else:
            resp = httpx.post(
                f"{BACKEND_URL}/api/v1/export/csv/{resource_type}",
                headers=headers,
                timeout=30,
            )

        if resp.status_code == 200:
            import base64
            content_base64 = base64.b64encode(resp.content).decode()
            return {
                "status": "success",
                "content_type": resp.headers.get("content-type", "application/octet-stream"),
                "content_base64": content_base64,
                "filename": resp.headers.get("content-disposition", ""),
            }

        return {"status": "error", "message": f"Backend returned {resp.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
