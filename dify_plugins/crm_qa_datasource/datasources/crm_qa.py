import httpx
from dify_plugin import OnlineDocumentDatasource
from dify_plugin.entities.datasource import (
    DatasourceGetPagesResponse,
    OnlineDocumentPage,
    OnlineDocumentInfo,
    GetOnlineDocumentPageContentRequest,
)


class CrmQaDatasource(OnlineDocumentDatasource):
    def _get_pages(self, datasource_parameters: dict):
        credentials = self.runtime.credentials
        base_url = credentials.get("base_url")
        api_key = credentials.get("api_key")
        timeout = float(credentials.get("timeout") or 10)

        group_id = datasource_parameters.get("group_id")
        updated_since = datasource_parameters.get("updated_since")

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        params = {"group_id": group_id}
        if updated_since:
            params["updated_since"] = updated_since

        resp = httpx.get(f"{base_url.rstrip('/')}/api/kb/pages", headers=headers, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        pages = []
        for p in data.get("pages", []):
            pages.append(
                OnlineDocumentPage(
                    page_id=str(p.get("id")),
                    name=p.get("name") or "",
                    updated_at=p.get("updated_at"),
                )
            )

        info = OnlineDocumentInfo(
            workspace_id=str(data.get("workspace_id")),
            workspace_name=data.get("workspace_name") or "",
            pages=pages,
            total=len(pages),
        )
        return DatasourceGetPagesResponse(result=[info])

    def _get_content(self, request: GetOnlineDocumentPageContentRequest):
        credentials = self.runtime.credentials
        base_url = credentials.get("base_url")
        api_key = credentials.get("api_key")
        timeout = float(credentials.get("timeout") or 10)

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        params = {
            "group_id": request.workspace_id,
            "qa_id": request.page_id,
        }

        resp = httpx.get(f"{base_url.rstrip('/')}/api/kb/content", headers=headers, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("content") or ""

        yield self.create_variable_message("content", content)
