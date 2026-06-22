import json
import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def handler(event, context):
    try:
        data = json.loads(event.get("body", "{}"))
        session_id = data.get("session_id", "")
        case_ids = data.get("case_ids", [])
        include_charts = data.get("include_charts", False)
        token = data.get("access_token", "")

        headers = {"Authorization": f"Bearer {token}"}
        resp = httpx.post(
            f"{BACKEND_URL}/api/v1/export/pdf",
            json={
                "session_id": session_id,
                "case_ids": case_ids,
                "include_charts": include_charts,
            },
            headers=headers,
            timeout=60,
        )

        if resp.status_code == 200:
            import base64
            content_base64 = base64.b64encode(resp.content).decode()
            return {
                "status": "success",
                "content_type": resp.headers.get("content-type", "application/pdf"),
                "content_base64": content_base64,
                "filename": resp.headers.get("content-disposition", f"report-{session_id[:8]}.pdf"),
            }

        return {"status": "error", "message": f"Backend returned {resp.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
