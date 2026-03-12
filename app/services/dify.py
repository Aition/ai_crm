import os
import uuid
import httpx


class DifyClient:
    def __init__(self):
        self.base_url = (os.getenv("DIFY_BASE_URL") or "").rstrip("/")
        self.api_key = os.getenv("DIFY_API_KEY")
        self.process_url = os.getenv("DIFY_MESSAGE_PROCESS_URL")
        self.kb_upsert_url = os.getenv("DIFY_KB_UPSERT_URL")
        self.kb_workflow_url = os.getenv("DIFY_KB_WORKFLOW_URL")
        self.kb_api_key = os.getenv("DIFY_KB_API_KEY") or self.api_key
        self.kb_dataset_id = os.getenv("DIFY_KB_DATASET_ID")
        self.closed_kb_dataset_id = os.getenv("CLOSED_ISSUES_KB_DATASET_ID")
        self.kb_doc_form = os.getenv("DIFY_KB_DOC_FORM", "qa_model")
        self.kb_doc_language = os.getenv("DIFY_KB_DOC_LANGUAGE", "中文")
        self.kb_indexing_technique = os.getenv("DIFY_KB_INDEXING_TECHNIQUE", "high_quality")
        self.kb_name_prefix = os.getenv("DIFY_KB_NAME_PREFIX", "CRMQA::")
        self.kb_q_key = os.getenv("DIFY_KB_INPUT_Q", "question")
        self.kb_a_key = os.getenv("DIFY_KB_INPUT_A", "answer")
        self.kb_group_key = os.getenv("DIFY_KB_INPUT_GROUP", "group")
        self.kb_segment_key = os.getenv("DIFY_KB_INPUT_SEGMENT", "segment")
        self.input_key = os.getenv("DIFY_WORKFLOW_INPUT_KEY", "text")
        self.response_mode = os.getenv("DIFY_RESPONSE_MODE", "streaming")
        self.mock = os.getenv("DIFY_MOCK", "true").lower() == "true"

    def _api_url(self, path: str) -> str:
        if self.base_url.endswith("/v1"):
            return f"{self.base_url}{path}"
        return f"{self.base_url}/v1{path}"

    def _headers(self):
        if not self.api_key:
            return {"Content-Type": "application/json"}
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _kb_headers(self):
        if not self.kb_api_key:
            return {"Content-Type": "application/json"}
        return {"Authorization": f"Bearer {self.kb_api_key}", "Content-Type": "application/json"}

    def _require_kb_dataset(self, dataset_id: str):
        if not dataset_id:
            raise ValueError("DIFY_KB_DATASET_ID is required for KB sync")

    def _list_kb_documents(self, dataset_id: str, page=1, limit=50):
        self._require_kb_dataset(dataset_id)
        url = self._api_url(f"/datasets/{dataset_id}/documents")
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._kb_headers(), params={"page": page, "limit": limit})
            resp.raise_for_status()
            return resp.json()

    def _find_kb_doc_id_by_name(self, dataset_id: str, name):
        page = 1
        while True:
            payload = self._list_kb_documents(dataset_id=dataset_id, page=page, limit=50)
            items = payload.get("data") or []
            for item in items:
                if item.get("name") == name:
                    return item.get("id")
            if not payload.get("has_more"):
                break
            page += 1
        return None

    def _delete_kb_document(self, dataset_id: str, document_id):
        self._require_kb_dataset(dataset_id)
        url = self._api_url(f"/datasets/{dataset_id}/documents/{document_id}")
        with httpx.Client(timeout=30) as client:
            resp = client.delete(url, headers=self._kb_headers())
            if resp.status_code == 404:
                return {"result": "not_found"}
            resp.raise_for_status()
            return resp.json() if resp.text else {"result": "success"}

    def _create_kb_document(
        self,
        dataset_id: str,
        name,
        text,
        metadata=None,
        doc_form_override: str = None,
        process_mode_override: str = None,
    ):
        self._require_kb_dataset(dataset_id)
        url = self._api_url(f"/datasets/{dataset_id}/document/create-by-text")
        process_rule = {"mode": "automatic"}
        if process_mode_override != "automatic":
            process_rule = {
                "mode": "custom",
                "rules": {
                    "pre_processing_rules": [],
                    "segmentation": {"max_tokens": 1000},
                },
            }
        category = (metadata or {}).get("category")
        if category == "常见问题":
            process_rule = {"mode": "automatic"}
        doc_form = doc_form_override or self.kb_doc_form
        payload = {
            "name": name,
            "text": text,
            "doc_form": doc_form,
            "process_rule": process_rule,
            "indexing_technique": self.kb_indexing_technique,
        }
        if self.kb_doc_language:
            payload["doc_language"] = self.kb_doc_language
        if metadata:
            payload["doc_metadata"] = metadata
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers=self._kb_headers(), json=payload)
            if resp.status_code >= 400:
                raise ValueError(f"Dify KB create failed {resp.status_code}: {resp.text[:500]}")
            return resp.json()

    def process_message(self, content, group_name=None):
        if self.mock or not self.process_url:
            return {
                "task_id": f"mock-{uuid.uuid4().hex[:10]}",
                "stage2": "{\n  \"atomic_issues\": [\n    {\n      \"id\": \"1\",\n      \"question\": \"是否支持中转代理？\",\n      \"answer\": \"支持，需升级到2.0.6。\",\n      \"status\": \"answered\",\n      \"confidence\": 1.0\n    }\n  ]\n}\n",
                "stage3": "```json\n{\n  \"themes\": [\n    {\n      \"theme_id\": \"T001\",\n      \"theme_title\": \"配置云机中转代理功能\",\n      \"business_category\": \"产品功能\",\n      \"priority\": \"medium\",\n      \"has_new_evolution\": false,\n      \"subthemes\": [\n        {\n          \"subtheme_id\": \"S001\",\n          \"title\": \"中转代理设置方法\",\n          \"state\": \"EXPLICITLY_CLOSED\",\n          \"related_atomic_ids\": [\"1\"],\n          \"close_reason\": \"\",\n          \"latest_qa\": {\n            \"question\": \"是否支持中转代理？\",\n            \"answer\": \"支持，需升级到2.0.6。\"\n          }\n        }\n      ]\n    }\n  ]\n}\n```\n",
            }
        payload = {
            "inputs": {self.input_key: content},
            "response_mode": self.response_mode,
            "user": group_name or "crm",
        }
        timeout = httpx.Timeout(600.0, read=600.0)
        with httpx.Client(timeout=timeout) as client:
            if self.response_mode == "streaming":
                try:
                    with client.stream("POST", self.process_url, headers=self._headers(), json=payload) as resp:
                        if resp.status_code >= 400:
                            return {
                                "error": "Dify 请求失败",
                                "status_code": resp.status_code,
                                "raw_text": resp.text[:1000],
                                "request_payload": {
                                    "inputs": {self.input_key: f"{content[:200]}..."},
                                    "response_mode": self.response_mode,
                                    "user": group_name or "crm",
                                },
                            }
                        outputs = None
                        text_chunks = []
                        for line in resp.iter_lines():
                            if not line:
                                continue
                            if line.startswith("data:"):
                                data_str = line[5:].strip()
                            else:
                                continue
                            if not data_str:
                                continue
                            try:
                                event = httpx.Response(200, content=data_str).json()
                            except ValueError:
                                continue
                            event_type = event.get("event")
                            if event_type == "text_chunk":
                                chunk = event.get("data", {}).get("text", "")
                                if chunk:
                                    text_chunks.append(chunk)
                            if event_type == "workflow_finished":
                                outputs = event.get("data", {}).get("outputs")
                                break
                        return {
                            "data": {"outputs": outputs or {}},
                            "text": "".join(text_chunks),
                        }
                except httpx.ReadTimeout:
                    return {
                        "error": "Dify 请求超时",
                        "status_code": 504,
                    }
            resp = client.post(self.process_url, headers=self._headers(), json=payload)
            if resp.status_code >= 400:
                return {
                    "error": "Dify 请求失败",
                    "status_code": resp.status_code,
                    "raw_text": resp.text[:1000],
                    "request_payload": {
                        "inputs": {self.input_key: f"{content[:200]}..."},
                        "response_mode": self.response_mode,
                        "user": group_name or "crm",
                    },
                }
            try:
                return resp.json()
            except ValueError:
                return {
                    "error": "Dify 返回非 JSON",
                    "status_code": resp.status_code,
                    "raw_text": resp.text[:500],
                }

    def upsert_kb(self, question, answer, group_name=None, metadata=None):
        if self.mock or not self.kb_upsert_url:
            return {"doc_id": f"mock-doc-{uuid.uuid4().hex[:8]}"}
        payload = {
            "question": question,
            "answer": answer,
            "group": group_name,
            "metadata": metadata or {},
        }
        with httpx.Client(timeout=30) as client:
            resp = client.post(self.kb_upsert_url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            return resp.json()

    def upsert_kb_dataset(self, name, question, answer, metadata=None, existing_doc_id=None):
        return self.upsert_kb_dataset_in(
            dataset_id=self.kb_dataset_id,
            name=name,
            question=question,
            answer=answer,
            metadata=metadata,
            existing_doc_id=existing_doc_id,
        )

    def upsert_kb_dataset_in(
        self,
        dataset_id,
        name,
        question,
        answer,
        metadata=None,
        existing_doc_id=None,
        doc_form_override: str = None,
        process_mode_override: str = None,
    ):
        if self.mock:
            return {"doc_id": f"mock-doc-{uuid.uuid4().hex[:8]}"}
        text = f"问：{question}\n答：{answer}"
        doc_id = existing_doc_id
        if not doc_id:
            doc_id = self._find_kb_doc_id_by_name(dataset_id, name)
        if doc_id:
            self._delete_kb_document(dataset_id, doc_id)
        created = self._create_kb_document(
            dataset_id=dataset_id,
            name=name,
            text=text,
            metadata=metadata,
            doc_form_override=doc_form_override,
            process_mode_override=process_mode_override,
        )
        doc = created.get("document") if isinstance(created, dict) else {}
        return {"doc_id": doc.get("id") or created.get("document_id") or doc_id}

    def upsert_kb_group_document(self, name, text, metadata=None, existing_doc_id=None):
        return self.upsert_kb_group_document_in(
            dataset_id=self.kb_dataset_id,
            name=name,
            text=text,
            metadata=metadata,
            existing_doc_id=existing_doc_id,
        )

    def upsert_kb_group_document_in(
        self,
        dataset_id,
        name,
        text,
        metadata=None,
        existing_doc_id=None,
        doc_form_override: str = None,
        process_mode_override: str = None,
    ):
        if self.mock:
            return {"doc_id": f"mock-doc-{uuid.uuid4().hex[:8]}"}
        doc_id = existing_doc_id
        if not doc_id:
            doc_id = self._find_kb_doc_id_by_name(dataset_id, name)
        if doc_id:
            self._delete_kb_document(dataset_id, doc_id)
        created = self._create_kb_document(
            dataset_id=dataset_id,
            name=name,
            text=text,
            metadata=metadata,
            doc_form_override=doc_form_override,
            process_mode_override=process_mode_override,
        )
        doc = created.get("document") if isinstance(created, dict) else {}
        return {"doc_id": doc.get("id") or created.get("document_id") or doc_id}

    def upsert_kb_workflow(self, question, answer, group_name=None, segment=None):
        if self.mock or not self.kb_workflow_url:
            return {"doc_id": f"mock-doc-{uuid.uuid4().hex[:8]}"}
        payload = {
            "inputs": {
                self.kb_q_key: question,
                self.kb_a_key: answer,
                self.kb_group_key: group_name or "",
                self.kb_segment_key: segment or "",
            },
            "response_mode": "blocking",
            "user": group_name or "crm",
        }
        timeout = httpx.Timeout(120.0, read=120.0)
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(self.kb_workflow_url, headers=self._headers(), json=payload)
            if resp.status_code >= 400:
                return {"error": resp.text[:500], "status_code": resp.status_code}
            try:
                data = resp.json()
            except ValueError:
                return {"error": "non_json", "status_code": resp.status_code}
        outputs = data.get("data", {}).get("outputs", {}) if isinstance(data, dict) else {}
        return outputs or data
