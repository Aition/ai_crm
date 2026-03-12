import httpx
from dify_plugin import DatasourceProvider
from dify_plugin.errors import ToolProviderCredentialValidationError


class CrmQaProvider(DatasourceProvider):
    def _validate_credentials(self, credentials: dict):
        base_url = credentials.get("base_url")
        api_key = credentials.get("api_key")
        timeout = float(credentials.get("timeout") or 10)
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        try:
            resp = httpx.get(f"{base_url.rstrip('/')}/api/kb/ping", headers=headers, timeout=timeout)
            if resp.status_code >= 400:
                raise ToolProviderCredentialValidationError(resp.text)
        except Exception as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc
