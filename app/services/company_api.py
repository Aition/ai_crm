import os
import datetime as dt
import httpx


class CompanyApiClient:
    def __init__(self, base_url=None, token=None):
        self.base_url = base_url or os.getenv("COMPANY_API_BASE")
        self.token = token or os.getenv("COMPANY_API_TOKEN")

    def _headers(self):
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def _auth_params(self):
        if not self.token:
            return {}
        return {"apikey": self.token}

    def list_groups(self, include_users: bool = False):
        if not self.base_url:
            return [
                {"id": "g-001", "name": "高潜客户群"},
                {"id": "g-002", "name": "沉默客户群"},
                {"id": "g-003", "name": "活跃客户群"},
            ]
        url = f"{self.base_url.rstrip('/')}/chat/groups"
        params = self._auth_params()
        if include_users:
            params["include_users"] = "true"
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, headers=self._headers(), params=params)
            resp.raise_for_status()
            payload = resp.json()
            data = payload.get("data", [])
            if include_users:
                return data
            return [{"id": g.get("roomid"), "name": g.get("display_name", g.get("roomid"))} for g in data]

    def fetch_group_messages(self, group_external_id, since=None, limit=50, page=1):
        if not self.base_url:
            now = dt.datetime.utcnow()
            return [
                {
                    "id": f"m-{group_external_id}-001",
                    "content": "最近活动少，想了解新功能。",
                    "received_at": (now - dt.timedelta(hours=4)).isoformat() + "Z",
                },
                {
                    "id": f"m-{group_external_id}-002",
                    "content": "续费价格能否有折扣？",
                    "received_at": (now - dt.timedelta(hours=2)).isoformat() + "Z",
                },
            ]
        url = f"{self.base_url.rstrip('/')}/chat/records"
        params = {
            "roomid": group_external_id,
            "page": page,
            "pageSize": limit,
            "include_users": "true",
        }
        if since:
            try:
                since_dt = dt.datetime.fromisoformat(since.replace("Z", "+00:00"))
                params["startTime"] = int(since_dt.timestamp())
            except ValueError:
                pass
        with httpx.Client(timeout=20) as client:
            resp = client.get(url, headers=self._headers(), params={**params, **self._auth_params()})
            resp.raise_for_status()
            payload = resp.json()
            records = payload.get("data", {}).get("records", [])
            messages = []
            for rec in records:
                msgid = rec.get("msgid")
                msgdata = rec.get("msgData") or {}
                if not isinstance(msgdata, dict):
                    msgdata = {}
                content = msgdata.get("content", "")
                msgtime = rec.get("msgtime")
                created_at = rec.get("createdAt") or rec.get("updatedAt")
                received_at = None
                if msgtime:
                    try:
                        ts = int(msgtime) / 1000.0
                        received_at = dt.datetime.utcfromtimestamp(ts).isoformat() + "Z"
                    except (TypeError, ValueError):
                        received_at = None
                if not received_at and created_at:
                    received_at = created_at
                from_info = rec.get("fromInfo") or {}
                if not isinstance(from_info, dict):
                    from_info = {}
                sender = (
                    from_info.get("display_name")
                    or from_info.get("userid")
                    or rec.get("from")
                )
                messages.append(
                    {
                        "id": msgid or f"m-{group_external_id}-{len(messages)+1}",
                        "content": content,
                        "received_at": received_at,
                        "sender": sender,
                    }
                )
            return messages

    def fetch_group_message_total(self, group_external_id):
        if not self.base_url:
            return 0
        url = f"{self.base_url.rstrip('/')}/chat/records"
        params = {"roomid": group_external_id, "page": 1, "pageSize": 1}
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, headers=self._headers(), params={**params, **self._auth_params()})
            resp.raise_for_status()
            payload = resp.json()
            data = payload.get("data", {})
            return int(data.get("total", 0))
