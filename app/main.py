import datetime as dt
import hashlib
import json
import os
import re
from typing import Optional, List

from fastapi import FastAPI, Depends, Request, Form, HTTPException, Header, Body, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from dotenv import load_dotenv
import httpx
from urllib.parse import urlparse
from html import unescape

from .db import Base, engine, get_db, SessionLocal
from .models import (
    CustomerGroup,
    RawMessage,
    Review,
    QAItem,
    AppSetting,
    AnalysisTask,
    AnalysisLog,
    AnalysisResult,
    GroupProfile,
    RpaGroupConfig,
    GroupDisplayMap,
    GroupMember,
    OperationLog,
    BotIntegration,
    BotChannel,
    BotMessage,
    BotReply,
    ClosedIssue,
    ClosedIssueDoc,
)
from .services.company_api import CompanyApiClient
from .services.dify import DifyClient
from .services.wecom import WeComClient

load_dotenv()

app = FastAPI(title="AI CRM - Customer Group Analysis")

CRM_KB_API_KEY = os.getenv("CRM_KB_API_KEY")
DOC_FETCH_ALLOW_DOMAIN = os.getenv("DOC_FETCH_ALLOW_DOMAIN", "newdoc.armcloud.net")
DOC_FETCH_BASE_URL = os.getenv("DOC_FETCH_BASE_URL", "http://newdoc.armcloud.net")
RPA_BASE_URL = (os.getenv("RPA_BASE_URL") or "http://127.0.0.1:9876").rstrip("/")
CRM_PUBLIC_BASE_URL = (os.getenv("CRM_PUBLIC_BASE_URL") or "").rstrip("/")
CLOSED_ISSUES_API_BASE = (os.getenv("CLOSED_ISSUES_API_BASE") or "http://192.168.230.157:3000").rstrip("/")
CLOSED_ISSUES_API_KEY = os.getenv("CLOSED_ISSUES_API_KEY") or "ca_dd0975eb981ec4bc43cc3c6e74b16e30428ee9b20d5c0433"
CLOSED_ISSUES_KB_PREFIX = os.getenv("CLOSED_ISSUES_KB_PREFIX") or "CRMCLOSED::"
CLOSED_ISSUES_KB_DATASET_ID = os.getenv("CLOSED_ISSUES_KB_DATASET_ID") or "d885b9a8-4aaf-4ea2-8a2f-324a43a58795"
CLOSED_ISSUES_KB_DOC_FORM = os.getenv("CLOSED_ISSUES_KB_DOC_FORM") or "text_model"
CLOSED_ISSUES_KB_PROCESS_MODE = os.getenv("CLOSED_ISSUES_KB_PROCESS_MODE") or "automatic"

app.mount("/static", StaticFiles(directory="/Users/joey/ai_crm/app/static"), name="static")

templates = Jinja2Templates(directory="/Users/joey/ai_crm/app/templates")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


def get_setting(db: Session, key: str) -> Optional[str]:
    setting = db.query(AppSetting).filter_by(key=key).first()
    return setting.value if setting else None


def upsert_setting(db: Session, key: str, value: str) -> None:
    setting = db.query(AppSetting).filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        db.add(AppSetting(key=key, value=value))


def _require_kb_api_key(auth_header: Optional[str]) -> None:
    if not CRM_KB_API_KEY:
        return
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing API key")
    token = auth_header
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
    if token != CRM_KB_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/api/docs/fetch")
def fetch_doc(path: str, db: Session = Depends(get_db)):
    if not path:
        raise HTTPException(status_code=400, detail="Missing path")
    base = (DOC_FETCH_BASE_URL or "").strip().rstrip("/")
    if not base:
        raise HTTPException(status_code=500, detail="Missing base url")
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md is allowed")
    full_url = f"{base}{path}"
    parsed = urlparse(full_url)
    allow_domain = (DOC_FETCH_ALLOW_DOMAIN or "").strip().lower()
    if allow_domain and parsed.netloc.lower() != allow_domain:
        raise HTTPException(status_code=403, detail="Domain not allowed")
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.get(full_url)
            resp.raise_for_status()
            return {"text": resp.text, "url": full_url}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Fetch failed: {exc}")


@app.get("/api/docs/toc")
def fetch_doc_toc(path: str, db: Session = Depends(get_db)):
    if not path:
        raise HTTPException(status_code=400, detail="Missing path")
    base = (DOC_FETCH_BASE_URL or "").strip().rstrip("/")
    if not base:
        raise HTTPException(status_code=500, detail="Missing base url")
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith(".html"):
        raise HTTPException(status_code=400, detail="Only .html is allowed")
    full_url = f"{base}{path}"
    parsed = urlparse(full_url)
    allow_domain = (DOC_FETCH_ALLOW_DOMAIN or "").strip().lower()
    if allow_domain and parsed.netloc.lower() != allow_domain:
        raise HTTPException(status_code=403, detail="Domain not allowed")
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.get(full_url)
            resp.raise_for_status()
            html_text = resp.text
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Fetch failed: {exc}")

    headings = []
    for match in re.finditer(r"<h([2-4])\\s+[^>]*id=[\"']([^\"']+)[\"'][^>]*>(.*?)</h\\1>", html_text, re.I | re.S):
        level = int(match.group(1))
        anchor = match.group(2)
        raw = match.group(3)
        text = re.sub(r"<[^>]+>", "", raw)
        text = unescape(text).strip()
        if not text:
            continue
        desc = ""
        tail = html_text[match.end(): match.end() + 2000]
        p_match = re.search(r"<p[^>]*>(.*?)</p>", tail, re.I | re.S)
        if p_match:
            desc_raw = re.sub(r"<[^>]+>", "", p_match.group(1))
            desc = unescape(desc_raw).strip()
        headings.append({"level": level, "title": text, "anchor": anchor, "desc": desc})
    if not headings:
        for match in re.finditer(r"<a[^>]*class=[\"']header-anchor[\"'][^>]*href=[\"']#([^\"']+)[\"'][^>]*>.*?<span>(.*?)</span>", html_text, re.I | re.S):
            anchor = match.group(1)
            raw = match.group(2)
            text = re.sub(r"<[^>]+>", "", raw)
            text = unescape(text).strip()
            if not text:
                continue
            desc = ""
            tail = html_text[match.end(): match.end() + 2000]
            p_match = re.search(r"<p[^>]*>(.*?)</p>", tail, re.I | re.S)
            if p_match:
                desc_raw = re.sub(r"<[^>]+>", "", p_match.group(1))
                desc = unescape(desc_raw).strip()
            headings.append({"level": 0, "title": text, "anchor": anchor, "desc": desc})
    return {"url": full_url, "headings": headings}


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    groups = db.query(CustomerGroup).order_by(CustomerGroup.id.desc()).all()
    counts = {g.id: g.message_total or 0 for g in groups}
    analyzed_counts = {}
    last_completed_at = {}
    for g in groups:
        latest_task = _get_last_completed_task(db, g.id)
        analyzed_counts[g.id] = latest_task.message_count if latest_task and latest_task.message_count else 0
        if latest_task:
            last_completed_at[g.id] = latest_task.finished_at or latest_task.started_at
    if groups:
        def _sort_key(group: CustomerGroup):
            analyzed = 1 if analyzed_counts.get(group.id, 0) > 0 else 0
            ts = last_completed_at.get(group.id)
            ts_value = ts.timestamp() if ts else 0
            return (-analyzed, -ts_value, -(analyzed_counts.get(group.id, 0) or 0), -(group.message_total or 0), -group.id)

        groups = sorted(groups, key=_sort_key)
    un_analyzed_counts = {
        g.id: max((g.message_total or 0) - analyzed_counts.get(g.id, 0), 0) for g in groups
    }
    api_base = get_setting(db, "company_api_base") or "http://192.168.230.160:19000/api"
    api_key = get_setting(db, "company_api_key") or ""
    group_id = request.query_params.get("group_id")
    task_id = request.query_params.get("task_id")
    selected_group = None
    if group_id:
        selected_group = db.query(CustomerGroup).filter_by(id=int(group_id)).first()
    if not selected_group and groups:
        selected_group = groups[0]

    current_task = None
    history = []
    logs = []
    result = None
    if selected_group:
        history = (
            db.query(AnalysisTask)
            .filter_by(group_id=selected_group.id)
            .order_by(AnalysisTask.started_at.desc())
            .all()
        )
        if task_id:
            current_task = (
                db.query(AnalysisTask)
                .filter_by(id=int(task_id), group_id=selected_group.id)
                .first()
            )
        else:
            current_task = history[0] if history else None
        if current_task:
            logs = (
                db.query(AnalysisLog)
                .filter_by(task_id=current_task.id)
                .order_by(AnalysisLog.created_at.asc())
                .all()
            )
            result = (
                db.query(AnalysisResult)
                .filter_by(task_id=current_task.id)
                .first()
            )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "groups": groups,
            "counts": counts,
            "analyzed_counts": analyzed_counts,
            "un_analyzed_counts": un_analyzed_counts,
            "api_base": api_base,
            "api_key": api_key,
            "selected_group": selected_group,
            "current_task": current_task,
            "history": history,
            "logs": logs,
            "result": result,
        },
    )


@app.post("/sync/groups")
def sync_groups(db: Session = Depends(get_db)):
    api_base = get_setting(db, "company_api_base") or "http://192.168.230.160:19000/api"
    api_key = get_setting(db, "company_api_key")
    client = CompanyApiClient(base_url=api_base, token=api_key)
    groups = client.list_groups()
    for g in groups:
        existing = db.query(CustomerGroup).filter_by(external_id=g["id"]).first()
        if existing:
            existing.name = g.get("name") or existing.name
        else:
            db.add(
                CustomerGroup(
                    external_id=g["id"],
                    name=g.get("name", g["id"]),
                    message_total=None,
                )
            )
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/settings/company-api")
def save_company_api_settings(
    api_base: str = Form(...),
    api_key: str = Form(""),
    db: Session = Depends(get_db),
):
    upsert_setting(db, "company_api_base", api_base.strip())
    upsert_setting(db, "company_api_key", api_key.strip())
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/settings/closed-issues-api")
def save_closed_issues_api_settings(
    api_base: str = Form(...),
    api_key: str = Form(""),
    kb_doc_form: str = Form(""),
    kb_process_mode: str = Form(""),
    db: Session = Depends(get_db),
):
    upsert_setting(db, "closed_issues_api_base", api_base.strip())
    upsert_setting(db, "closed_issues_api_key", api_key.strip())
    if kb_doc_form:
        upsert_setting(db, "closed_issues_kb_doc_form", kb_doc_form.strip())
    if kb_process_mode:
        upsert_setting(db, "closed_issues_kb_process_mode", kb_process_mode.strip())
    db.commit()
    return RedirectResponse(url="/closed-issues", status_code=303)


def _parse_json_from_text(text: str):
    if not text:
        return None
    cleaned = text.strip()
    if "```" in cleaned:
        start = cleaned.find("```json")
        if start == -1:
            start = cleaned.find("```")
            start = start + 3
        else:
            start = start + len("```json")
        end = cleaned.find("```", start)
        if end != -1:
            cleaned = cleaned[start:end].strip()
    if "<think" in cleaned.lower():
        cleaned = re.sub(r"<think>[\\s\\S]*?</think>", "", cleaned, flags=re.I).strip()
        cleaned = re.sub(r"<think>[\\s\\S]*", "", cleaned, flags=re.I).strip()
    if "{" in cleaned and "}" in cleaned:
        cleaned = cleaned[cleaned.find("{") : cleaned.rfind("}") + 1].strip()
    try:
        import json

        return json.loads(cleaned)
    except Exception:
        return None


def _build_result_from_dify(payload):
    outputs = payload.get("data", {}).get("outputs") if isinstance(payload, dict) else None
    streamed_text = payload.get("text") if isinstance(payload, dict) else None
    stage2_raw = outputs.get("stage2") if isinstance(outputs, dict) else None
    stage3_raw = outputs.get("stage3") if isinstance(outputs, dict) else None
    stage2_json = _parse_json_from_text(stage2_raw)
    stage3_json = _parse_json_from_text(stage3_raw)

    topics = []
    themes = (stage3_json or {}).get("themes", [])
    for theme in themes:
        subthemes = theme.get("subthemes", [])
        questions = []
        closed_states = {"EXPLICITLY_CLOSED", "FINAL_CLOSED"}
        closed_count = 0
        for sub in subthemes:
            state = sub.get("state", "")
            if state in closed_states:
                closed_count += 1
            latest = sub.get("latest_qa") or {}
            questions.append(
                {
                    "title": sub.get("title") or "未命名子问题",
                    "qa_chain": [
                        {
                            "q": latest.get("question", ""),
                            "a": latest.get("answer", ""),
                            "status": state or "OPEN",
                        }
                    ],
                }
            )
        status = "已解决" if subthemes and closed_count == len(subthemes) else "进行中"
        topics.append(
            {
                "title": theme.get("theme_title") or "未命名主题",
                "status": status,
                "last_updated": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                "span": "-",
                "message_count": len(subthemes),
                "participants": [],
                "questions": questions,
            }
        )
    return {
        "topics": topics,
        "raw": {"stage2": stage2_json, "stage3": stage3_json},
    }


def _calc_closed_stats(themes: list) -> dict:
    closed_states = {"EXPLICITLY_CLOSED", "FINAL_CLOSED"}
    total = 0
    closed = 0
    for theme in themes:
        subthemes = theme.get("subthemes", []) if isinstance(theme, dict) else []
        for sub in subthemes:
            total += 1
            if (sub.get("state") or "") in closed_states:
                closed += 1
    rate = round((closed / total), 4) if total else 0
    return {"total": total, "closed": closed, "rate": rate}


def _build_group_profile(stage3: dict) -> dict:
    themes = (stage3 or {}).get("themes", []) if isinstance(stage3, dict) else []
    closed_stats = _calc_closed_stats(themes)
    theme_summaries = []
    category_count = {}
    for theme in themes:
        if not isinstance(theme, dict):
            continue
        subthemes = theme.get("subthemes", []) or []
        closed_count = 0
        closed_states = {"EXPLICITLY_CLOSED", "FINAL_CLOSED"}
        top_questions = []
        for sub in subthemes:
            if not isinstance(sub, dict):
                continue
            if (sub.get("state") or "") in closed_states:
                closed_count += 1
            latest = sub.get("latest_qa") or {}
            if latest.get("question") or latest.get("answer"):
                top_questions.append(
                    {
                        "question": latest.get("question") or "",
                        "answer": latest.get("answer") or "",
                        "state": sub.get("state") or "OPEN",
                    }
                )
            if len(top_questions) >= 3:
                break
        category = theme.get("business_category") or "未分类"
        category_count[category] = category_count.get(category, 0) + len(subthemes)
        theme_summaries.append(
            {
                "title": theme.get("theme_title") or "未命名主题",
                "business_category": category,
                "priority": theme.get("priority") or "medium",
                "subtheme_count": len(subthemes),
                "closed_count": closed_count,
                "top_questions": top_questions,
            }
        )

    theme_summaries.sort(key=lambda t: t.get("subtheme_count", 0), reverse=True)
    top_themes = theme_summaries[:5]
    top_titles = [t.get("title") for t in top_themes if t.get("title")]
    summary_text = "主要问题集中在：" + "、".join(top_titles) if top_titles else "暂无明显聚合问题。"
    if closed_stats["total"]:
        summary_text += f" 闭环 {closed_stats['closed']}/{closed_stats['total']}。"
    top_categories = sorted(category_count.items(), key=lambda i: i[1], reverse=True)
    summary = {
        "summary_text": summary_text,
        "top_categories": [c[0] for c in top_categories[:3]],
        "top_themes": top_themes,
    }
    return {
        "summary": summary,
        "topics": theme_summaries,
        "closed_stats": closed_stats,
    }


def _extract_stage_json(payload):
    outputs = payload.get("data", {}).get("outputs") if isinstance(payload, dict) else None
    stage2_raw = outputs.get("stage2") if isinstance(outputs, dict) else None
    stage3_raw = outputs.get("stage3") if isinstance(outputs, dict) else None
    if isinstance(payload, dict) and (payload.get("stage2") or payload.get("stage3")):
        stage2_raw = stage2_raw or payload.get("stage2")
        stage3_raw = stage3_raw or payload.get("stage3")
    streamed_text = payload.get("text") if isinstance(payload, dict) else ""
    if not stage2_raw and not stage3_raw and streamed_text:
        stage2_raw = streamed_text
        stage3_raw = streamed_text
    stage2_json = _parse_json_from_text(stage2_raw) or {}
    stage3_json = _parse_json_from_text(stage3_raw) or {}
    return stage2_json, stage3_json


def _candidate_token(analysis_result_id: int, subtheme_id: str) -> str:
    return f"{analysis_result_id}:{subtheme_id}"


def _parse_candidate_token(token: str):
    if not token:
        return None, ""
    if ":" in token:
        left, right = token.split(":", 1)
        try:
            return int(left), right
        except ValueError:
            return None, right
    return None, token


def _find_candidate_from_result(result: AnalysisResult, subtheme_id: str):
    stage3 = (result.result_json or {}).get("raw", {}).get("stage3") or {}
    for theme in stage3.get("themes", []):
        for sub in theme.get("subthemes", []):
            if sub.get("subtheme_id") == subtheme_id:
                latest = sub.get("latest_qa") or {}
                return {
                    "theme_id": theme.get("theme_id"),
                    "theme_title": theme.get("theme_title") or "",
                    "subtheme_id": subtheme_id,
                    "subtheme_title": sub.get("title") or "",
                    "question": latest.get("question") or "",
                    "answer": latest.get("answer") or "",
                    "summary": sub.get("title") or "",
                }
    return None


def _find_theme_by_subtheme(result: AnalysisResult, subtheme_id: str):
    stage3 = (result.result_json or {}).get("raw", {}).get("stage3") or {}
    for theme in stage3.get("themes", []):
        for sub in theme.get("subthemes", []):
            if sub.get("subtheme_id") == subtheme_id:
                return theme
    return None


def _kb_doc_name(prefix: str, source_id: str) -> str:
    return f"{prefix}{source_id}"


def _kb_metadata_from_review(message: RawMessage, review: Review):
    trace_id = message.external_message_id or f"raw:{message.id}"
    metadata = {
        "trace_id": trace_id,
        "source_id": str(message.external_message_id or message.id),
        "group_id": message.group_id,
        "group_name": message.group.name if message.group else "",
        "segment": review.segment,
        "review_id": review.id,
        "message_id": message.external_message_id or message.id,
    }
    return metadata


def _closed_issue_hash(item: dict) -> str:
    raw = {
        "customer": (item.get("customer") or "").strip(),
        "title": (item.get("title") or "").strip(),
        "summary": (item.get("summary") or "").strip(),
        "team": item.get("team") or [],
        "originalVoices": item.get("originalVoices") or [],
        "rootCause": (item.get("rootCause") or "").strip(),
        "resolution": (item.get("resolution") or "").strip(),
    }
    try:
        text = json.dumps(raw, ensure_ascii=False, sort_keys=True)
    except TypeError:
        text = str(raw)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_closed_issues(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            items = data.get("items") or data.get("records")
            if isinstance(items, list):
                return items
        items = payload.get("items") or payload.get("records")
        if isinstance(items, list):
            return items
    return []


def _closed_issue_kb_payload(issue: ClosedIssue) -> tuple:
    question = issue.title or "已闭环问题"
    answer_parts = []
    if issue.summary:
        answer_parts.append(f"摘要：{issue.summary}")
    if issue.root_cause:
        answer_parts.append(f"根因：{issue.root_cause}")
    if issue.resolution:
        answer_parts.append(f"处理方式：{issue.resolution}")
    team = issue.team if isinstance(issue.team, list) else []
    if team:
        answer_parts.append("归属团队：" + "、".join([str(t) for t in team if t]))
    voices = issue.original_voices if isinstance(issue.original_voices, list) else []
    if voices:
        answer_parts.append("原声：\n" + "\n".join([f"- {v}" for v in voices if v]))
    answer = "\n".join(answer_parts) if answer_parts else "暂无详细信息。"
    metadata = {
        "source": "closed_issue",
        "category": "已闭环问题",
        "customer": issue.customer or "",
        "title": issue.title or "",
        "summary": issue.summary or "",
        "root_cause": issue.root_cause or "",
        "team": team,
    }
    return question, answer, metadata


def _closed_issue_doc_payload(customer: str, issues: list) -> tuple:
    clean_customer = (customer or "未知客户").strip()
    parts = []
    for idx, issue in enumerate(issues, start=1):
        title = issue.title or "未命名问题"
        summary = issue.summary or "无摘要"
        root = issue.root_cause or "无根因"
        resolution = issue.resolution or "无处理方式"
        team = "、".join(issue.team) if isinstance(issue.team, list) and issue.team else "未知团队"
        voices = ""
        if isinstance(issue.original_voices, list) and issue.original_voices:
            voices = "\n".join([f"- {v}" for v in issue.original_voices if v])
        section = [
            f"问题 {idx}：{title}",
            f"摘要：{summary}",
            f"归属团队：{team}",
            f"根因：{root}",
            f"处理方式：{resolution}",
        ]
        if voices:
            section.append("原声：\n" + voices)
        parts.append("\n".join(section))
    text = f"客户：{clean_customer}\n\n" + "\n\n---\n\n".join(parts)
    metadata = {
        "source": "closed_issue",
        "category": "已闭环问题",
        "customer": clean_customer,
        "count": len(issues),
    }
    return clean_customer, text, metadata


def _kb_metadata_from_item(item: QAItem):
    trace_id = str(item.id)
    if item.source_review and item.source_review.message:
        trace_id = item.source_review.message.external_message_id or f"raw:{item.source_review.message.id}"
    metadata = {
        "trace_id": trace_id,
        "source_id": str(item.id),
        "group_id": item.group_id,
        "group_name": item.group.name if item.group else "",
        "segment": item.source_review.segment if item.source_review else "",
        "review_id": item.source_review_id,
        "category": item.category,
        "tags": item.tags,
        "product": item.product,
        "version_range": item.version_range,
        "keywords": item.keywords,
        "quality_score": item.quality_score,
        "is_generic": item.is_generic,
    }
    if item.source_review and item.source_review.message:
        metadata["message_id"] = item.source_review.message.external_message_id or item.source_review.message.id
    return metadata


def _build_group_doc_text(items):
    by_theme = {}
    for item in items:
        seg = ""
        if item.source_review and item.source_review.segment:
            seg = item.source_review.segment.strip()
        seg = seg or "未分类"
        by_theme.setdefault(seg, []).append(item)
    blocks = []
    for theme, theme_items in by_theme.items():
        blocks.append(f"## 主题：{theme}")
        for idx, item in enumerate(theme_items, start=1):
            q = (item.question or "").strip()
            a = (item.answer or "").strip()
            if not q and not a:
                continue
            blocks.append(f"### QA {idx}\n问：{q}\n答：{a}")
    return "\n\n".join(blocks).strip()


def _log_operation(db: Session, action: str, status: str, message: str, group_id: Optional[int] = None):
    db.add(
        OperationLog(
            group_id=group_id,
            action=action,
            status=status,
            message=message,
        )
    )
    db.commit()


def _upsert_group_profile(db: Session, group_id: int, task_id: Optional[int], profile_payload: dict) -> GroupProfile:
    profile = db.query(GroupProfile).filter_by(group_id=group_id).first()
    if profile:
        existing_summary = profile.summary_json or {}
        summary = profile_payload.get("summary") or {}
        # Preserve manually maintained fields on refresh
        for key in ("manual_notes", "manual_tags", "manual_summary"):
            if key in existing_summary and key not in summary:
                summary[key] = existing_summary.get(key)
        profile.last_task_id = task_id
        profile.summary_json = summary
        profile.topics_json = profile_payload.get("topics")
        profile.closed_stats_json = profile_payload.get("closed_stats")
        db.commit()
        return profile
    profile = GroupProfile(
        group_id=group_id,
        last_task_id=task_id,
        summary_json=profile_payload.get("summary"),
        topics_json=profile_payload.get("topics"),
        closed_stats_json=profile_payload.get("closed_stats"),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _upsert_rpa_config(db: Session, group_id: int, status: str = "pending") -> RpaGroupConfig:
    config = db.query(RpaGroupConfig).filter_by(group_id=group_id).first()
    if config:
        if status == "active" and (config.config_json or {}).get("blocked"):
            return config
        config.status = status
        if status == "active":
            config.created_at = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
        if not config.config_json:
            config.config_json = {"source": "placeholder"}
        db.commit()
        return config
    config = RpaGroupConfig(group_id=group_id, status=status, config_json={"source": "placeholder"})
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def _rpa_request(method: str, path: str, params: Optional[dict] = None, payload: Optional[dict] = None) -> dict:
    url = f"{RPA_BASE_URL}{path}"
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.request(method, url, params=params, json=payload)
            if resp.status_code >= 400:
                return {"error": f"{resp.status_code}", "text": resp.text}
            if not resp.text:
                return {"result": "ok"}
            return resp.json()
    except Exception as exc:
        return {"error": str(exc)}


def _rpa_merge_roomid_and_start(db: Session, group: CustomerGroup) -> dict:
    if not group.external_id:
        return {"error": "missing_roomid"}
    current = _rpa_request("GET", "/config")
    if current.get("error"):
        return current
    payload = {"only_roomids_append": group.external_id}
    company_api_base = get_setting(db, "company_api_base")
    company_api_key = get_setting(db, "company_api_key")
    if company_api_base:
        payload["company_api_base"] = company_api_base
    if company_api_key:
        payload["company_api_key"] = company_api_key
    if CRM_PUBLIC_BASE_URL:
        payload["dify_reply_base"] = CRM_PUBLIC_BASE_URL
    payload["dify_reply_path"] = "/api/wecom/dify/reply"
    if CRM_KB_API_KEY:
        payload["crm_kb_api_key"] = CRM_KB_API_KEY
    updated = _rpa_request("POST", "/config", payload=payload)
    if updated.get("error"):
        return updated
    started = _rpa_request("POST", "/poller/start")
    if started.get("error"):
        return started
    return {"result": "ok", "roomid": group.external_id}


def _rpa_remove_roomid(db: Session, group: CustomerGroup) -> dict:
    if not group.external_id:
        return {"error": "missing_roomid"}
    current = _rpa_request("GET", "/config")
    if current.get("error"):
        return current
    only_roomids = current.get("only_roomids") or []
    if not isinstance(only_roomids, list):
        only_roomids = []
    if group.external_id in only_roomids:
        only_roomids = [rid for rid in only_roomids if rid != group.external_id]
    payload = {"only_roomids_replace": only_roomids}
    updated = _rpa_request("POST", "/config", payload=payload)
    if updated.get("error"):
        return updated
    return {"result": "ok", "roomid": group.external_id}


def _get_or_create_integration(db: Session, provider: str, name: Optional[str] = None) -> BotIntegration:
    integration = db.query(BotIntegration).filter_by(provider=provider).first()
    if integration:
        return integration
    integration = BotIntegration(provider=provider, name=name or provider)
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


def _upsert_bot_channel(
    db: Session,
    provider: str,
    external_id: str,
    name: Optional[str] = None,
    group_id: Optional[int] = None,
) -> BotChannel:
    channel = (
        db.query(BotChannel)
        .filter_by(provider=provider, external_id=external_id)
        .first()
    )
    if channel:
        if name:
            channel.name = name
        if group_id is not None:
            channel.group_id = group_id
        db.commit()
        return channel
    channel = BotChannel(
        provider=provider,
        external_id=external_id,
        name=name,
        group_id=group_id,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def _get_text_from_dify_result(result: dict) -> str:
    if not result:
        return ""
    if isinstance(result, dict):
        text = result.get("text")
        if text:
            return text.strip()
        # Handle mock payloads with stage2/stage3
        if result.get("stage3"):
            stage3 = result.get("stage3") or ""
            try:
                json_str = stage3
                match = re.search(r"```json\\s*([\\s\\S]*?)```", stage3, re.I)
                if match:
                    json_str = match.group(1)
                payload = json.loads(json_str)
                themes = payload.get("themes") or []
                if themes:
                    subthemes = themes[0].get("subthemes") or []
                    if subthemes and subthemes[0].get("latest_qa"):
                        answer = subthemes[0]["latest_qa"].get("answer")
                        if isinstance(answer, str) and answer.strip():
                            return answer.strip()
            except Exception:
                pass
        if result.get("stage2"):
            stage2 = result.get("stage2") or ""
            try:
                payload = json.loads(stage2)
                issues = payload.get("atomic_issues") or []
                if issues:
                    answer = issues[0].get("answer")
                    if isinstance(answer, str) and answer.strip():
                        return answer.strip()
            except Exception:
                pass
        outputs = result.get("data", {}).get("outputs")
        if isinstance(outputs, dict):
            for key in ("answer", "reply", "text", "output"):
                value = outputs.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return ""
    return ""


def _get_quick_reply_text() -> str:
    return (os.getenv("WECOM_QUICK_REPLY_TEXT") or "收到，正在分析，请稍等。").strip()


def _clean_dify_answer(text: str) -> str:
    if not text:
        return ""
    if "</think>" in text.lower():
        parts = re.split(r"</think>", text, flags=re.I)
        text = parts[-1]
    cleaned = re.sub(r"<think>[\\s\\S]*?</think>", "", text, flags=re.I)
    cleaned = re.sub(r"<think>[\\s\\S]*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"[\\s\\n]*$", "", cleaned)
    cleaned = cleaned.strip()
    return cleaned


def _extract_dify_text(event: dict) -> str:
    if not isinstance(event, dict):
        return ""
    event_type = (event.get("event") or "").lower()
    if event_type:
        if event_type not in {"agent_message", "message", "message_delta", "agent_message_delta"}:
            return ""
    for key in ("answer", "text", "content", "message", "delta"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return value
    data = event.get("data")
    if isinstance(data, dict):
        for key in ("answer", "text", "content", "message", "delta"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return ""


def _call_wecom_dify_agent(content: str, user_id: Optional[str] = None) -> dict:
    api_key = (os.getenv("WECOM_DIFY_API_KEY") or "").strip()
    base_url = (os.getenv("WECOM_DIFY_BASE_URL") or "").strip().rstrip("/")
    app_id = (os.getenv("WECOM_DIFY_APP_ID") or "").strip()
    response_mode = (os.getenv("WECOM_DIFY_RESPONSE_MODE") or "streaming").strip()
    debug_raw = (os.getenv("WECOM_DIFY_DEBUG_RAW") or "false").lower() == "true"
    if not api_key or not base_url:
        return {"answer": "", "raw": []}
    url = f"{base_url}/v1/chat-messages"
    payload = {
        "inputs": {},
        "query": content,
        "response_mode": response_mode,
        "user": user_id or "wecom",
    }
    if app_id:
        payload["inputs"]["app_id"] = app_id
    try:
        timeout = httpx.Timeout(60.0, read=60.0)
        with httpx.Client(timeout=timeout) as client:
            if response_mode == "streaming":
                with client.stream("POST", url, headers={"Authorization": f"Bearer {api_key}"}, json=payload) as resp:
                    if resp.status_code >= 400:
                        return {"answer": "", "raw": [f"http_{resp.status_code}"]}
                    answer_text = ""
                    raw_samples = []
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        if line.startswith("data:"):
                            data_str = line[5:].strip()
                        else:
                            continue
                        if data_str == "[DONE]":
                            break
                        try:
                            event = httpx.Response(200, content=data_str).json()
                        except ValueError:
                            continue
                        if isinstance(event, dict):
                            chunk = _extract_dify_text(event)
                            if isinstance(chunk, str) and chunk:
                                if chunk.startswith(answer_text):
                                    answer_text = chunk
                                elif answer_text.startswith(chunk):
                                    pass
                                else:
                                    answer_text += chunk
                            if len(raw_samples) < 5:
                                raw_samples.append(event)
                    answer_text = _clean_dify_answer(answer_text.strip())
                    return {"answer": answer_text, "raw": raw_samples, "debug_raw": raw_samples if debug_raw else []}
            resp = client.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload)
            if resp.status_code >= 400:
                return {"answer": "", "raw": [f"http_{resp.status_code}"]}
            data = resp.json()
            answer = data.get("answer") or ""
            if isinstance(answer, str):
                return {"answer": _clean_dify_answer(answer.strip()), "raw": [data], "debug_raw": [data] if debug_raw else []}
    except Exception:
        return {"answer": "", "raw": ["exception"]}
    return {"answer": "", "raw": []}


def _call_wecom_dify_closure(payload: dict) -> dict:
    api_key = (os.getenv("WECOM_DIFY_CLOSURE_API_KEY") or "").strip()
    base_url = (os.getenv("WECOM_DIFY_BASE_URL") or "").strip().rstrip("/")
    app_id = (os.getenv("WECOM_DIFY_CLOSURE_APP_ID") or "").strip()
    if not api_key or not base_url or not app_id:
        return {"error": "missing_dify_closure_config"}
    url = f"{base_url}/v1/workflows/run"
    raw_inputs = payload.get("inputs") if isinstance(payload.get("inputs"), dict) else {}
    query_raw = payload.get("query")
    if isinstance(query_raw, str) and query_raw.strip():
        try:
            query_inputs = json.loads(query_raw)
            if isinstance(query_inputs, dict):
                raw_inputs = {**query_inputs, **raw_inputs}
        except Exception:
            pass
    qa_list = payload.get("qa_list") or raw_inputs.get("qa_list") or []
    recent_messages = payload.get("recent_messages") or raw_inputs.get("recent_messages") or []
    if not isinstance(qa_list, str):
        qa_list = json.dumps(qa_list, ensure_ascii=False)
    if not isinstance(recent_messages, str):
        recent_messages = json.dumps(recent_messages, ensure_ascii=False)
    inputs = {
        "topic_id": payload.get("topic_id") or raw_inputs.get("topic_id"),
        "topic_summary": payload.get("topic_summary") or raw_inputs.get("topic_summary"),
        "qa_list": qa_list,
        "recent_messages": recent_messages,
        "latest_user_message": payload.get("latest_user_message") or raw_inputs.get("latest_user_message"),
        "latest_reply": payload.get("latest_reply") or raw_inputs.get("latest_reply"),
        "context": payload.get("context") or raw_inputs.get("context") or {},
        "app_id": app_id,
    }
    if not isinstance(inputs["context"], str):
        inputs["context"] = json.dumps(inputs["context"], ensure_ascii=False)
    data = {
        "inputs": inputs,
        "response_mode": "blocking",
        "user": payload.get("user") or "wecom_closure",
    }
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=data)
            if resp.status_code >= 400:
                return {"error": f"http_{resp.status_code}", "text": resp.text}
            return resp.json()
    except Exception as exc:
        return {"error": str(exc)}


def _send_wecom_rpa_reply(target: str, message: str) -> dict:
    base_url = (os.getenv("WECOM_RPA_BASE_URL") or "http://127.0.0.1:8765").rstrip("/")
    if not target or not message:
        return {"ok": False, "error": "target_or_message_missing"}
    url = f"{base_url}/reply"
    payload = {"target": target, "message": message}
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(url, json=payload)
            if resp.status_code >= 400:
                return {"ok": False, "error": f"http_{resp.status_code}"}
            data = resp.json()
            if isinstance(data, dict) and data.get("ok") is True:
                return {"ok": True}
            return {"ok": False, "error": data.get("error") or "send_failed"}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}


def _clean_message_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text
    # Replace fenced code blocks with placeholder
    cleaned = re.sub(r"```[\s\S]*?```", "【代码块】", cleaned)
    # Replace raw URLs with placeholder
    cleaned = re.sub(r"https?://\S+", "【链接】", cleaned)
    # Normalize whitespace
    cleaned = re.sub(r"\s+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip()


def _parse_ts(value: Optional[str]):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _merge_messages(messages, gap_seconds: int = 180):
    merged = []
    current = None
    for msg in messages:
        content = msg.get("content") or ""
        if not content:
            continue
        sender = msg.get("sender") or msg.get("sender_id") or msg.get("from") or ""
        ts = msg.get("received_at_dt")
        if (
            current
            and sender
            and current.get("sender") == sender
            and ts
            and current.get("received_at_dt")
            and (ts - current.get("received_at_dt")).total_seconds() <= gap_seconds
        ):
            current["content"] = (current.get("content") or "").rstrip() + "\n" + content.lstrip()
            current["received_at_dt"] = ts
        else:
            if current:
                merged.append(current)
            current = {"content": content, "sender": sender, "received_at_dt": ts}
    if current:
        merged.append(current)
    return merged


def _truncate_log(text: str, limit: int = 2000) -> str:
    if text is None:
        return ""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"...(截断，共{len(text)}字)"


def _get_last_analysis_ts(db: Session, group_id: int) -> Optional[dt.datetime]:
    key = f"analysis_last_ts:{group_id}"
    setting = db.query(AppSetting).filter_by(key=key).first()
    if not setting:
        return None
    return _parse_ts(setting.value)


def _set_last_analysis_ts(db: Session, group_id: int, ts: dt.datetime) -> None:
    key = f"analysis_last_ts:{group_id}"
    value = ts.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    setting = db.query(AppSetting).filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        db.add(AppSetting(key=key, value=value))


def _get_last_completed_task(
    db: Session, group_id: int, exclude_task_id: Optional[int] = None
) -> Optional[AnalysisTask]:
    query = db.query(AnalysisTask).filter_by(group_id=group_id)
    if exclude_task_id:
        query = query.filter(AnalysisTask.id != exclude_task_id)
    query = query.filter(AnalysisTask.message_count.isnot(None))
    return (
        query.order_by(AnalysisTask.finished_at.desc().nullslast(), AnalysisTask.started_at.desc())
        .first()
    )


def _create_analysis_task(db: Session, group: CustomerGroup) -> Optional[AnalysisTask]:
    running = (
        db.query(AnalysisTask)
        .filter_by(group_id=group.id, status="running")
        .first()
    )
    if running:
        return None
    now = dt.datetime.utcnow()
    version_label = now.strftime("%Y-%m-%d %H:%M")
    task = AnalysisTask(
        group_id=group.id,
        status="running",
        version_label=version_label,
    )
    db.add(task)
    db.flush()
    db.add(AnalysisLog(task_id=task.id, stage="数据清洗", message="开始拉取群聊消息。"))
    db.commit()
    return task


@app.post("/analysis/run")
def run_analysis(
    request: Request,
    group_id: int = Form(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    wants_json = "application/json" in (request.headers.get("accept") or "").lower() or request.headers.get("x-requested-with") == "XMLHttpRequest"
    group = db.query(CustomerGroup).filter_by(id=group_id).first()
    if not group:
        if wants_json:
            return JSONResponse({"ok": False, "error": "group_not_found"}, status_code=404)
        return RedirectResponse(url="/", status_code=303)
    api_base = get_setting(db, "company_api_base") or "http://192.168.230.160:19000/api"
    api_key = get_setting(db, "company_api_key")
    api = CompanyApiClient(base_url=api_base, token=api_key)
    try:
        group.message_total = api.fetch_group_message_total(group.external_id)
        db.commit()
    except Exception:
        pass
    task = _create_analysis_task(db, group)
    if not task:
        if wants_json:
            running = (
                db.query(AnalysisTask)
                .filter_by(group_id=group.id, status="running")
                .order_by(AnalysisTask.started_at.desc())
                .first()
            )
            return JSONResponse(
                {"ok": True, "status": "running", "task_id": running.id if running else None},
                status_code=200,
            )
        return RedirectResponse(url=f"/?group_id={group.id}", status_code=303)

    if background_tasks is not None:
        background_tasks.add_task(_run_analysis_task, task.id, False)
    else:
        _run_analysis_task(task.id, False)
    if wants_json:
        return JSONResponse({"ok": True, "status": "running", "task_id": task.id}, status_code=200)
    return RedirectResponse(url=f"/?group_id={group.id}&task_id={task.id}", status_code=303)


@app.post("/bots/analysis/batch")
def bots_batch_analysis(
    roomids: Optional[List[str]] = Form(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    if not roomids:
        return RedirectResponse(url="/bots", status_code=303)
    api_base = get_setting(db, "company_api_base") or "http://192.168.230.160:19000/api"
    api_key = get_setting(db, "company_api_key")
    api = CompanyApiClient(base_url=api_base, token=api_key)
    group_name_map = {}
    try:
        group_name_map = {g.get("id"): g.get("name") for g in api.list_groups() if g.get("id")}
    except Exception:
        group_name_map = {}
    updated_groups = 0
    created = 0
    skipped = 0
    selected_roomids = []
    for rid in roomids:
        group = db.query(CustomerGroup).filter_by(external_id=rid).first()
        if not group:
            continue
        cfg = db.query(RpaGroupConfig).filter_by(group_id=group.id).first()
        if cfg and cfg.config_json and cfg.config_json.get("blocked"):
            cfg.config_json.pop("blocked", None)
            cfg.status = "queued"
        if group_name_map.get(group.external_id):
            group.name = group_name_map[group.external_id]
        try:
            group.message_total = api.fetch_group_message_total(group.external_id)
        except Exception:
            pass
        updated_groups += 1
        if group.external_id:
            selected_roomids.append(group.external_id)
        task = _create_analysis_task(db, group)
        if task:
            created += 1
            if background_tasks is not None:
                background_tasks.add_task(_run_analysis_task, task.id, True)
            else:
                _run_analysis_task(task.id, True)
        else:
            skipped += 1
        _upsert_rpa_config(db, group.id, status="queued")
        _log_operation(
            db,
            action="bot_batch_analysis",
            status="ok",
            message=f"group_id={group.id} queued",
            group_id=group.id,
        )
    if updated_groups:
        db.commit()
        _log_operation(
            db,
            action="bot_groups_sync",
            status="ok",
            message=f"synced={updated_groups}",
            group_id=None,
        )
    if selected_roomids:
        _log_operation(
            db,
            action="rpa_config_sync",
            status="ok",
            message=f"queued_roomids={len(selected_roomids)}",
            group_id=None,
        )
    _log_operation(
        db,
        action="bot_batch_analysis_summary",
        status="ok",
        message=f"created={created}, skipped={skipped}",
        group_id=None,
    )
    return RedirectResponse(url="/bots", status_code=303)


def _run_analysis_task(task_id: int, enable_takeover: bool = False) -> None:
    db = SessionLocal()
    try:
        task = db.query(AnalysisTask).filter_by(id=task_id).first()
        if not task:
            return
        group = db.query(CustomerGroup).filter_by(id=task.group_id).first()
        if not group:
            task.status = "failed"
            db.commit()
            return

        api_base = get_setting(db, "company_api_base") or "http://192.168.230.160:19000/api"
        api_key = get_setting(db, "company_api_key")
        api = CompanyApiClient(base_url=api_base, token=api_key)

        total = group.message_total or 0
        last_task = _get_last_completed_task(db, group.id, exclude_task_id=task.id)
        analyzed_count = last_task.message_count if last_task and last_task.message_count else 0
        un_analyzed = max(total - analyzed_count, 0)
        extra = int(analyzed_count * 0.1)
        target_count = un_analyzed + extra
        min_chars = 200
        if un_analyzed == 0:
            task.status = "completed"
            task.message_count = total
            task.segments_count = 0
            task.qa_count = 0
            task.topics_count = 0
            task.closed_topics_count = 0
            task.finished_at = dt.datetime.utcnow()
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="完成",
                    message="未分析为 0，跳过分析，直接接管。",
                )
            )
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="QA 抽取",
                    message="无新增消息，跳过抽取。",
                )
            )
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="主题聚合",
                    message="无新增消息，跳过聚合。",
                )
            )
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="画像汇总",
                    message="无新增消息，保持历史画像。",
                )
            )
            if enable_takeover:
                try:
                    rpa_resp = _rpa_merge_roomid_and_start(db, group)
                    if rpa_resp.get("error"):
                        db.add(
                            AnalysisLog(
                                task_id=task.id,
                                stage="RPA同步",
                                message=f"同步失败：{rpa_resp.get('error')}",
                            )
                        )
                        _log_operation(
                            db,
                            action="rpa_config_sync",
                            status="failed",
                            message=f"group_id={group.id} {rpa_resp.get('error')}",
                            group_id=group.id,
                        )
                    else:
                        _upsert_rpa_config(db, group.id, status="active")
                        db.add(
                            AnalysisLog(
                                task_id=task.id,
                                stage="RPA同步",
                                message="已写入RPA配置并启动轮询。",
                            )
                        )
                        _log_operation(
                            db,
                            action="rpa_config_sync",
                            status="ok",
                            message=f"group_id={group.id} roomid={group.external_id}",
                            group_id=group.id,
                        )
                except Exception as exc:
                    db.add(
                        AnalysisLog(
                            task_id=task.id,
                            stage="RPA同步",
                            message=f"同步异常：{exc}",
                        )
                    )
            db.commit()
            return

        page = 1
        hard_cap = int(os.getenv("ANALYSIS_HARD_CAP", "2000") or 2000)
        hard_cap = max(200, hard_cap)
        page_size = int(os.getenv("ANALYSIS_PAGE_SIZE", "50") or 50)
        page_size = max(20, min(page_size, hard_cap))
        merge_gap = int(os.getenv("ANALYSIS_MERGE_GAP_SECONDS", "180") or 180)
        last_ts = _get_last_analysis_ts(db, group.id)
        if not last_ts and last_task:
            last_ts = last_task.finished_at or last_task.started_at
            if last_ts:
                db.add(
                    AnalysisLog(
                        task_id=task.id,
                        stage="数据清洗",
                        message="未记录 last_ts，使用上次任务时间作为增量起点。",
                    )
                )
                db.commit()
        incremental = last_ts is not None
        if incremental:
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="数据清洗",
                    message=f"增量模式：从 {last_ts.isoformat()} 起拉取新消息。",
                )
            )
        else:
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="数据清洗",
                    message="全量模式：从群聊首条消息开始拉取。",
                )
            )
        db.commit()

        raw_all = []
        while True:
            since_arg = None
            if incremental:
                since_arg = last_ts.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")
            batch = api.fetch_group_messages(group.external_id, since=since_arg, limit=page_size, page=page)
            if not batch:
                break
            if not isinstance(batch, list):
                db.add(
                    AnalysisLog(
                        task_id=task.id,
                        stage="数据清洗",
                        message=f"消息拉取异常：返回类型 {type(batch).__name__}",
                    )
                )
                db.commit()
                break
            raw_msgs = []
            for msg in batch:
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content") or ""
                if not content:
                    continue
                raw_msgs.append(
                    {
                        "content": content,
                        "sender": msg.get("sender") or msg.get("sender_id") or msg.get("from"),
                        "received_at_dt": _parse_ts(msg.get("received_at")),
                    }
                )
            raw_all.extend(raw_msgs)
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="数据清洗",
                    message=(
                        f"分页拉取 page={page}, page_size={page_size}，接口返回 {len(batch)} 条，"
                        f"原始消息 {len(raw_msgs)} 条。"
                    ),
                )
            )
            if len(raw_all) >= hard_cap:
                db.add(
                    AnalysisLog(
                        task_id=task.id,
                        stage="数据清洗",
                        message=f"达到抓取上限 {hard_cap} 条，停止继续拉取。",
                    )
                )
                break
            if len(batch) < page_size:
                break
            page += 1

        raw_total = len(raw_all)
        raw_all.sort(
            key=lambda item: item.get("received_at_dt") or dt.datetime.min
        )
        merged = _merge_messages(raw_all, gap_seconds=merge_gap)
        if incremental and target_count > 0 and len(merged) > target_count:
            merged = merged[-target_count:]

        # preview logs removed by request

        cleaned_texts = []
        total_chars = 0
        total_cleaned = 0
        last_used_dt = None
        for item in merged:
            text = _clean_message_text(item.get("content") or "")
            if not text:
                continue
            cleaned_texts.append(text)
            total_chars += len(text)
            total_cleaned += 1
            if item.get("received_at_dt"):
                last_used_dt = item.get("received_at_dt")

        max_single_chars = int(os.getenv("ANALYSIS_BATCH_MAX_SINGLE", "8000") or 8000)
        split_chars = int(os.getenv("ANALYSIS_BATCH_SPLIT_CHARS", "5000") or 5000)
        batches = []
        if cleaned_texts:
            if total_chars <= max_single_chars:
                batches.append((cleaned_texts, len(cleaned_texts), total_chars))
            else:
                idx = 0
                while idx < len(cleaned_texts):
                    remaining_texts = cleaned_texts[idx:]
                    remaining_chars = sum(len(t) for t in remaining_texts)
                    if remaining_chars <= max_single_chars:
                        batches.append((remaining_texts, len(remaining_texts), remaining_chars))
                        break
                    current = []
                    batch_chars = 0
                    batch_count = 0
                    while idx < len(cleaned_texts) and batch_chars < split_chars:
                        text = cleaned_texts[idx]
                        current.append(text)
                        batch_chars += len(text)
                        batch_count += 1
                        idx += 1
                    batches.append((current, batch_count, batch_chars))

        if last_used_dt:
            _set_last_analysis_ts(db, group.id, last_used_dt)
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="数据清洗",
                    message=f"本次分析结束时间戳：{last_used_dt.isoformat()}",
                )
            )
        db.add(
            AnalysisLog(
                task_id=task.id,
                stage="数据清洗",
                message=(
                    f"总数 {total}，未分析 {un_analyzed}，追加历史 {extra}（按已分析的10%），"
                    f"本次拉取 {raw_total} 条，清洗后 {total_cleaned} 条（{total_chars} 字），分为 {len(batches)} 批。"
                ),
            )
        )

        dify = DifyClient()
        db.add(
            AnalysisLog(
                task_id=task.id,
                stage="QA 抽取",
                message=f"调用 Dify 工作流中，共 {len(batches)} 批。",
            )
        )
        db.commit()
        if not batches:
            task.status = "failed"
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="QA 抽取",
                    message="未获取到可分析的消息批次。",
                )
            )
            db.commit()
            return

        combined_stage2 = {"atomic_issues": []}
        combined_stage3 = {"themes": []}
        for idx, (texts, cnt, chars) in enumerate(batches, start=1):
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="QA 抽取",
                    message=f"批次 {idx}/{len(batches)}：{cnt} 条，{chars} 字。",
                )
            )
            db.commit()
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="QA 抽取",
                    message=f"批次 {idx} 开始调用 Dify。",
                )
            )
            db.commit()
            payload = dify.process_message("\n".join(texts), group.name)
            if isinstance(payload, dict) and payload.get("error"):
                db.add(
                    AnalysisLog(
                        task_id=task.id,
                        stage="QA 抽取",
                        message=f"批次 {idx} Dify 返回异常：{payload.get('error')}（{payload.get('status_code')}）",
                    )
                )
                db.add(
                    AnalysisLog(
                        task_id=task.id,
                        stage="接管失败",
                        message="Dify 调用异常，接管终止。",
                    )
                )
                raw_text = payload.get("raw_text") or ""
                if raw_text:
                    db.add(
                        AnalysisLog(
                            task_id=task.id,
                            stage="QA 抽取",
                            message=f"Dify 响应片段：{raw_text}",
                        )
                    )
                request_payload = payload.get("request_payload")
                if request_payload:
                    db.add(
                        AnalysisLog(
                            task_id=task.id,
                            stage="QA 抽取",
                            message=f"Dify 请求体片段：{request_payload}",
                        )
                    )
                task.status = "failed"
                db.commit()
                return

            stage2_json, stage3_json = _extract_stage_json(payload)
            combined_stage2["atomic_issues"].extend(stage2_json.get("atomic_issues") or [])
            combined_stage3["themes"].extend(stage3_json.get("themes") or [])
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="QA 抽取",
                    message=f"批次 {idx} Dify 调用完成。",
                )
            )
            db.commit()

        combined_payload = {
            "data": {
                "outputs": {
                    "stage2": json.dumps(combined_stage2, ensure_ascii=False),
                    "stage3": json.dumps(combined_stage3, ensure_ascii=False),
                }
            }
        }
        result_payload = _build_result_from_dify(combined_payload)
        atomic = combined_stage2.get("atomic_issues", [])
        themes = combined_stage3.get("themes", [])
        stage2_snippet = json.dumps(combined_stage2, ensure_ascii=False)[:200].replace("\n", " ")
        stage3_snippet = json.dumps(combined_stage3, ensure_ascii=False)[:200].replace("\n", " ")
        db.add(
            AnalysisLog(
                task_id=task.id,
                stage="QA 抽取",
                message="Dify 批次完成，汇总结果解析中。",
            )
        )
        if atomic:
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="QA 抽取",
                    message=f"stage2 片段：{stage2_snippet}",
                )
            )
        else:
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="QA 抽取",
                    message="stage2 为空。",
                )
            )
        if themes:
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="主题聚合",
                    message=f"stage3 片段：{stage3_snippet}",
                )
            )
        else:
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="主题聚合",
                    message="stage3 为空。",
                )
            )

        task.status = "completed"
        newly_counted = min(raw_total, un_analyzed) if un_analyzed is not None else raw_total
        task.message_count = (analyzed_count or 0) + newly_counted
        task.segments_count = len(atomic)
        task.qa_count = len(atomic)
        task.topics_count = len(themes)
        task.closed_topics_count = sum(
            1
            for t in themes
            if all(s.get("state") in {"EXPLICITLY_CLOSED", "FINAL_CLOSED"} for s in t.get("subthemes", []))
        )
        task.finished_at = dt.datetime.utcnow()
        db.add(AnalysisResult(task_id=task.id, result_json=result_payload))
        try:
            group_local = group
            if not group_local:
                raise RuntimeError("group_not_found")
            profile_payload = _build_group_profile(combined_stage3)
            _upsert_group_profile(db, group_local.id, task.id, profile_payload)
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="画像汇总",
                    message="群聊画像已生成。",
                )
            )
            if enable_takeover:
                rpa_resp = _rpa_merge_roomid_and_start(db, group_local)
                if rpa_resp.get("error"):
                    db.add(
                        AnalysisLog(
                            task_id=task.id,
                            stage="RPA同步",
                            message=f"同步失败：{rpa_resp.get('error')}",
                        )
                    )
                    _log_operation(
                        db,
                        action="rpa_config_sync",
                        status="failed",
                        message=f"group_id={group_local.id} {rpa_resp.get('error')}",
                        group_id=group_local.id,
                    )
                else:
                    _upsert_rpa_config(db, group_local.id, status="active")
                    db.add(
                        AnalysisLog(
                            task_id=task.id,
                            stage="RPA同步",
                            message="已写入RPA配置并启动轮询。",
                        )
                    )
                    _log_operation(
                        db,
                        action="rpa_config_sync",
                        status="ok",
                        message=f"group_id={group_local.id} roomid={group_local.external_id}",
                        group_id=group_local.id,
                    )
        except Exception as exc:
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="画像汇总",
                    message=f"群聊画像生成失败：{exc}",
                )
            )
            db.add(
                AnalysisLog(
                    task_id=task.id,
                    stage="接管失败",
                    message="画像汇总异常，接管终止。",
                )
            )
        db.add(
            AnalysisLog(
                task_id=task.id,
                stage="完成",
                message="分析完成并生成结果。",
            )
        )
        db.commit()
    except Exception as exc:
        try:
            task = db.query(AnalysisTask).filter_by(id=task_id).first()
            if task:
                task.status = "failed"
                db.add(
                    AnalysisLog(
                        task_id=task_id,
                        stage="异常",
                        message=str(exc),
                    )
                )
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@app.get("/api/analysis/status")
def analysis_status(group_id: int, task_id: Optional[int] = None, db: Session = Depends(get_db)):
    task = None
    if task_id:
        task = db.query(AnalysisTask).filter_by(id=task_id, group_id=group_id).first()
    if not task:
        task = (
            db.query(AnalysisTask)
            .filter_by(group_id=group_id)
            .order_by(AnalysisTask.started_at.desc())
            .first()
        )
    if not task:
        return {"task": None, "logs": []}
    logs = (
        db.query(AnalysisLog)
        .filter_by(task_id=task.id)
        .order_by(AnalysisLog.created_at.asc())
        .all()
    )
    return {
        "task": {
            "id": task.id,
            "status": task.status,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "finished_at": task.finished_at.isoformat() if task.finished_at else None,
            "segments_count": task.segments_count,
            "qa_count": task.qa_count,
            "topics_count": task.topics_count,
            "closed_topics_count": task.closed_topics_count,
            "message_count": task.message_count,
        },
        "logs": [
            {
                "stage": log.stage,
                "message": log.message,
                "created_at": log.created_at.isoformat() if log.created_at else "",
            }
            for log in logs
        ],
    }


@app.get("/api/analysis/logs")
def analysis_logs_api(limit: int = 50, db: Session = Depends(get_db)):
    logs = (
        db.query(AnalysisLog, AnalysisTask, CustomerGroup)
        .join(AnalysisTask, AnalysisLog.task_id == AnalysisTask.id)
        .join(CustomerGroup, AnalysisTask.group_id == CustomerGroup.id)
        .order_by(AnalysisLog.created_at.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return {
        "logs": [
            {
                "group_id": group.id,
                "group_name": group.name,
                "task_id": task.id,
                "stage": log.stage,
                "message": log.message,
                "created_at": log.created_at.isoformat() if log.created_at else "",
            }
            for log, task, group in logs
        ]
    }


@app.get("/api/groups/{roomid}/profile")
def group_profile_api(roomid: str, db: Session = Depends(get_db)):
    group = db.query(CustomerGroup).filter_by(external_id=roomid).first()
    if not group:
        raise HTTPException(status_code=404, detail="group not found")
    display_map = db.query(GroupDisplayMap).filter_by(group_id=group.id).first()
    display_name = (display_map.display_name if display_map and display_map.display_name else None) or group.name
    members = db.query(GroupMember).filter_by(group_id=group.id).order_by(GroupMember.id.asc()).all()
    profile = db.query(GroupProfile).filter_by(group_id=group.id).first()
    if not profile:
        return {
            "group_id": group.id,
            "group_name": group.name,
            "display_id": display_name,
            "members": [
                {
                    "id": m.id,
                    "external_user_id": m.external_user_id,
                    "name": m.name,
                    "nickname": m.nickname,
                    "real_name": m.real_name,
                    "role": m.role,
                    "profile_text": m.profile_text,
                }
                for m in members
            ],
            "profile": None,
        }
    return {
        "group_id": group.id,
        "group_name": group.name,
        "display_id": display_name,
        "members": [
            {
                "id": m.id,
                "external_user_id": m.external_user_id,
                "name": m.name,
                "nickname": m.nickname,
                "real_name": m.real_name,
                "role": m.role,
                "profile_text": m.profile_text,
            }
            for m in members
        ],
        "last_task_id": profile.last_task_id,
        "summary": profile.summary_json,
        "topics": profile.topics_json,
        "closed_stats": profile.closed_stats_json,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


@app.get("/rpa/config")
def rpa_config():
    return _rpa_request("GET", "/config")


@app.post("/rpa/config")
def rpa_config_update(payload: dict = Body(...), db: Session = Depends(get_db)):
    resp = _rpa_request("POST", "/config", payload=payload)
    _log_operation(
        db,
        action="rpa_config_update",
        status="ok" if not resp.get("error") else "failed",
        message=resp.get("error") or "updated",
        group_id=None,
    )
    return resp


@app.post("/rpa/poller/{action}")
def rpa_poller_action(action: str, db: Session = Depends(get_db)):
    if action not in {"start", "stop", "run_once"}:
        raise HTTPException(status_code=400, detail="invalid action")
    resp = _rpa_request("POST", f"/poller/{action}")
    _log_operation(
        db,
        action=f"rpa_poller_{action}",
        status="ok" if not resp.get("error") else "failed",
        message=resp.get("error") or "ok",
        group_id=None,
    )
    return resp


@app.get("/rpa/logs")
def rpa_logs(
    limit: int = 50,
    offset: int = 0,
    start: Optional[int] = None,
    end: Optional[int] = None,
    session_id: Optional[str] = None,
    roomid: Optional[str] = None,
    sender_id: Optional[str] = None,
    level: Optional[str] = None,
    event: Optional[str] = None,
    db: Session = Depends(get_db),
):
    params = {
        "limit": limit,
        "offset": offset,
    }
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    if session_id:
        params["session_id"] = session_id
    if roomid:
        params["roomid"] = roomid
    if sender_id:
        params["sender_id"] = sender_id
    if level:
        params["level"] = level
    if event:
        params["event"] = event
    resp = _rpa_request("GET", "/logs", params=params)
    if resp.get("error"):
        return resp
    roomids = []
    for item in resp.get("data") or []:
        rid = item.get("roomid")
        if rid:
            roomids.append(rid)
    if not roomids:
        resp["roomid_map"] = {}
        return resp
    groups = db.query(CustomerGroup).filter(CustomerGroup.external_id.in_(roomids)).all()
    group_map = {g.external_id: g for g in groups}
    display_maps = db.query(GroupDisplayMap).filter(GroupDisplayMap.group_id.in_([g.id for g in groups])).all()
    display_map = {m.group_id: m.display_name for m in display_maps if m.display_name}
    roomid_map = {}
    for rid, group in group_map.items():
        display = display_map.get(group.id) or group.name
        roomid_map[rid] = display if display == group.name else f"{group.name}:{display}"
    resp["roomid_map"] = roomid_map
    return resp


@app.get("/rpa/sessions")
def rpa_sessions(
    session_id: Optional[str] = None,
    roomid: Optional[str] = None,
    sender_id: Optional[str] = None,
):
    params = {}
    if session_id:
        params["session_id"] = session_id
    if roomid:
        params["roomid"] = roomid
    if sender_id:
        params["sender_id"] = sender_id
    return _rpa_request("GET", "/sessions", params=params)


@app.get("/rpa/records")
def rpa_records(
    roomid: Optional[str] = None,
    sender_id: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
):
    params = {
        "limit": limit,
        "offset": offset,
    }
    if roomid:
        params["roomid"] = roomid
    if sender_id:
        params["sender_id"] = sender_id
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    return _rpa_request("GET", "/records", params=params)


@app.post("/rpa/replied/clear")
def rpa_replied_clear(payload: Optional[dict] = Body(None), db: Session = Depends(get_db)):
    resp = _rpa_request("POST", "/replied/clear", payload=payload or {})
    _log_operation(
        db,
        action="rpa_replied_clear",
        status="ok" if not resp.get("error") else "failed",
        message=resp.get("error") or "cleared",
        group_id=None,
    )
    return resp


@app.post("/analysis/{group_id}/reset")
def reset_analysis(group_id: int, db: Session = Depends(get_db)):
    group = db.query(CustomerGroup).filter_by(id=group_id).first()
    if not group:
        return RedirectResponse(url="/", status_code=303)

    # Clear profile task reference to avoid FK violation
    profile = db.query(GroupProfile).filter_by(group_id=group.id).first()
    if profile and profile.last_task_id:
        profile.last_task_id = None
        db.commit()

    task_ids = [
        t.id
        for t in db.query(AnalysisTask.id).filter_by(group_id=group.id).all()
    ]
    if task_ids:
        db.query(AnalysisLog).filter(AnalysisLog.task_id.in_(task_ids)).delete(synchronize_session=False)
        db.query(AnalysisResult).filter(AnalysisResult.task_id.in_(task_ids)).delete(synchronize_session=False)
        db.query(AnalysisTask).filter(AnalysisTask.id.in_(task_ids)).delete(synchronize_session=False)
    db.commit()

    return RedirectResponse(url=f"/?group_id={group.id}", status_code=303)


@app.get("/groups/{group_id}", response_class=HTMLResponse)
def group_detail(group_id: int, request: Request, db: Session = Depends(get_db)):
    group = db.query(CustomerGroup).filter_by(id=group_id).first()
    if not group:
        return RedirectResponse(url="/", status_code=303)
    messages = (
        db.query(RawMessage)
        .filter_by(group_id=group_id)
        .order_by(RawMessage.id.desc())
        .all()
    )
    pending = [m for m in messages if m.status == "pending_review"]
    reviewed = [m for m in messages if m.status != "pending_review"]
    return templates.TemplateResponse(
        "group.html",
        {
            "request": request,
            "group": group,
            "pending": pending,
            "reviewed": reviewed,
        },
    )


@app.post("/groups/{group_id}/analyze")
def analyze_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(CustomerGroup).filter_by(id=group_id).first()
    if not group:
        return RedirectResponse(url="/", status_code=303)

    last_msg = (
        db.query(RawMessage)
        .filter_by(group_id=group_id)
        .order_by(RawMessage.received_at.desc().nullslast())
        .first()
    )
    since = None
    if last_msg and last_msg.received_at:
        since = last_msg.received_at.isoformat()

    api_base = get_setting(db, "company_api_base") or "http://192.168.230.160:19000/api"
    api_key = get_setting(db, "company_api_key")
    api = CompanyApiClient(base_url=api_base, token=api_key)
    dify = DifyClient()
    messages = api.fetch_group_messages(group.external_id, since=since)

    for msg in messages:
        existing = (
            db.query(RawMessage)
            .filter_by(external_message_id=msg["id"])
            .first()
        )
        if existing:
            continue
        analysis = dify.process_message(msg["content"], group.name)
        received_at = None
        if msg.get("received_at"):
            try:
                received_at = dt.datetime.fromisoformat(msg["received_at"].replace("Z", "+00:00"))
            except ValueError:
                received_at = None
        raw = RawMessage(
            group_id=group.id,
            external_message_id=msg["id"],
            content=msg["content"],
            received_at=received_at,
            dify_task_id=analysis.get("task_id"),
            analysis_json=analysis,
            status="pending_review",
        )
        db.add(raw)
    db.commit()
    return RedirectResponse(url=f"/groups/{group_id}", status_code=303)


@app.get("/reviews/{message_id}", response_class=HTMLResponse)
def review_message(message_id: int, request: Request, db: Session = Depends(get_db)):
    message = db.query(RawMessage).filter_by(id=message_id).first()
    if not message:
        return RedirectResponse(url="/", status_code=303)
    group = message.group
    analysis = message.analysis_json or {}
    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "message": message,
            "group": group,
            "analysis": analysis,
        },
    )


@app.post("/reviews/{message_id}/approve")
def approve_message(
    message_id: str,
    group_id: Optional[int] = Form(None),
    segment: str = Form(...),
    question: str = Form(...),
    answer: str = Form(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    product: Optional[str] = Form(None),
    version_range: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),
    quality_score: Optional[int] = Form(None),
    is_generic: Optional[str] = Form(None),
    reason: Optional[str] = Form(None),
    steps: Optional[str] = Form(None),
    conditions: Optional[str] = Form(None),
    action: Optional[str] = Form("push"),
    reviewer: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # message_id is either raw message id (numeric) or unified candidate subtheme_id
    if str(message_id).isdigit():
        message = db.query(RawMessage).filter_by(id=int(message_id)).first()
        if not message:
            return RedirectResponse(url="/", status_code=303)
    else:
        external_id = str(message_id)
        message = db.query(RawMessage).filter_by(external_message_id=external_id).first()
        if not message:
            if not group_id:
                return RedirectResponse(url="/qa", status_code=303)
            message = RawMessage(
                group_id=group_id,
                external_message_id=external_id,
                content=question or "",
                received_at=dt.datetime.utcnow(),
                analysis_json={"question": question, "answer": answer, "summary": ""},
                status="pending_review",
            )
            db.add(message)
            db.flush()

    review = db.query(Review).filter_by(message_id=message.id).first()
    if review:
        review.reviewer = reviewer
        review.segment = segment
        review.notes = notes
    else:
        review = Review(
            message_id=message.id,
            reviewer=reviewer,
            segment=segment,
            notes=notes,
        )
        db.add(review)
        db.flush()

    qa = db.query(QAItem).filter_by(source_review_id=review.id).first()
    if qa:
        qa.question = question
        qa.answer = answer
        qa.category = category
        qa.tags = tags
        qa.product = product
        qa.version_range = version_range
        qa.keywords = keywords
        qa.quality_score = quality_score
        qa.is_generic = (is_generic == "true") if is_generic is not None else None
        qa.reason = reason
        qa.steps = steps
        qa.conditions = conditions
        qa.status = "approved"
    else:
        qa = QAItem(
            group_id=message.group_id,
            question=question,
            answer=answer,
            source_review_id=review.id,
            category=category,
            tags=tags,
            product=product,
            version_range=version_range,
            keywords=keywords,
            quality_score=quality_score,
            is_generic=(is_generic == "true") if is_generic is not None else None,
            reason=reason,
            steps=steps,
            conditions=conditions,
            status="approved",
        )
        db.add(qa)
        db.flush()

    if action == "save":
        qa.dify_sync_status = "pending"
    message.status = "reviewed"
    db.commit()

    if action != "save":
        qa_sync_group(message.group_id, db)

    return RedirectResponse(url="/qa", status_code=303)


@app.post("/reviews/{message_id}/reject")
def reject_message(
    message_id: int,
    reviewer: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    message = db.query(RawMessage).filter_by(id=message_id).first()
    if not message:
        return RedirectResponse(url="/", status_code=303)

    review = Review(
        message_id=message.id,
        reviewer=reviewer,
        segment="rejected",
        notes=notes,
    )
    db.add(review)
    message.status = "rejected"
    db.commit()

    return RedirectResponse(url=f"/groups/{message.group_id}", status_code=303)


@app.get("/qa", response_class=HTMLResponse)
def qa_list(request: Request, db: Session = Depends(get_db)):
    groups = db.query(CustomerGroup).order_by(CustomerGroup.name.asc()).all()
    group_id = request.query_params.get("group_id")
    tab = request.query_params.get("tab", "pool")
    status_filter = request.query_params.get("status")
    message_id = request.query_params.get("message_id")

    selected_group = None
    if group_id:
        selected_group = db.query(CustomerGroup).filter_by(id=int(group_id)).first()
    if not selected_group and groups:
        selected_group = groups[0]

    pending = []
    reviewed = []
    queue = []
    logs = []
    review_message = None
    review_group = None
    review_analysis = {}
    if selected_group:
        latest_result = (
            db.query(AnalysisResult)
            .join(AnalysisTask, AnalysisResult.task_id == AnalysisTask.id)
            .filter(AnalysisTask.group_id == selected_group.id)
            .order_by(AnalysisResult.id.desc())
            .first()
        )
        pending = []
        if latest_result:
            stage3 = (latest_result.result_json or {}).get("raw", {}).get("stage3") or {}
            candidate_ids = []
            for theme in stage3.get("themes", []):
                theme_title = theme.get("theme_title") or ""
                for sub in theme.get("subthemes", []):
                    sub_id = sub.get("subtheme_id") or ""
                    token = _candidate_token(latest_result.id, sub_id)
                    external_id = token
                    candidate_ids.append(token)
                    latest = sub.get("latest_qa") or {}
                    pending.append(
                        {
                            "id": token,
                            "external_id": external_id,
                            "question": latest.get("question") or "",
                            "answer": latest.get("answer") or "",
                            "summary": sub.get("title") or "",
                            "theme_title": theme_title,
                            "state": sub.get("state") or "",
                            "created_at": latest_result.created_at,
                        }
                    )
            if candidate_ids:
                existing = (
                    db.query(RawMessage.external_message_id, RawMessage.status)
                    .filter(RawMessage.external_message_id.in_(candidate_ids))
                    .all()
                )
                reviewed_ids = {
                    eid for (eid, status) in existing if status and status != "pending_review"
                }
                if reviewed_ids:
                    pending = [item for item in pending if item.get("external_id") not in reviewed_ids]
        query = db.query(QAItem).filter_by(group_id=selected_group.id)
        if status_filter:
            query = query.filter(QAItem.status == status_filter)
        reviewed = query.order_by(QAItem.id.desc()).all()
        queue = (
            db.query(QAItem)
            .filter_by(group_id=selected_group.id, status="approved")
            .order_by(QAItem.id.desc())
            .all()
        )
        logs = (
            db.query(QAItem)
            .filter_by(group_id=selected_group.id)
            .order_by(QAItem.dify_synced_at.desc().nullslast(), QAItem.id.desc())
            .limit(100)
            .all()
        )
        if message_id:
            review_message = (
                db.query(RawMessage).filter_by(id=int(message_id), group_id=selected_group.id).first()
            )
            if review_message:
                review_group = review_message.group
                review_analysis = review_message.analysis_json or {}
    return templates.TemplateResponse(
        "qa.html",
        {
            "request": request,
            "groups": groups,
            "selected_group": selected_group,
            "pending": pending,
            "reviewed": reviewed,
            "queue": queue,
            "logs": logs,
            "tab": tab,
            "status_filter": status_filter or "",
            "review_message": review_message,
            "review_group": review_group,
            "review_analysis": review_analysis,
            "status_counts": {
                "pending": len(pending),
                "approved": len([i for i in reviewed if i.status == "approved"]),
                "pushed": len([i for i in reviewed if i.status == "pushed"]),
            },
        },
    )


@app.get("/closed-issues", response_class=HTMLResponse)
def closed_issues_list(request: Request, db: Session = Depends(get_db)):
    api_base = get_setting(db, "closed_issues_api_base") or CLOSED_ISSUES_API_BASE
    api_key = get_setting(db, "closed_issues_api_key") or CLOSED_ISSUES_API_KEY
    kb_doc_form = get_setting(db, "closed_issues_kb_doc_form") or CLOSED_ISSUES_KB_DOC_FORM
    if not kb_doc_form:
        kb_doc_form = "text"
    kb_process_mode = get_setting(db, "closed_issues_kb_process_mode") or CLOSED_ISSUES_KB_PROCESS_MODE
    query = request.query_params.get("q", "").strip()
    error = request.query_params.get("error", "").strip()
    issues_query = db.query(ClosedIssue)
    if query:
        like = f"%{query}%"
        issues_query = issues_query.filter(
            (ClosedIssue.title.ilike(like)) | (ClosedIssue.customer.ilike(like))
        )
    issues = issues_query.order_by(
        ClosedIssue.kb_synced_at.desc().nullslast(),
        ClosedIssue.id.desc(),
    ).all()
    total = len(issues)
    synced = len([i for i in issues if i.kb_sync_status == "success"])
    pending = total - synced
    return templates.TemplateResponse(
        "closed_issues.html",
        {
            "request": request,
            "issues": issues,
            "api_base": api_base,
            "api_key": api_key,
            "kb_doc_form": kb_doc_form,
            "kb_process_mode": kb_process_mode,
            "query": query,
            "error": error,
            "total": total,
            "synced": synced,
            "pending": pending,
        },
    )


@app.post("/closed-issues/fetch")
def closed_issues_fetch(db: Session = Depends(get_db)):
    api_base = get_setting(db, "closed_issues_api_base") or CLOSED_ISSUES_API_BASE
    api_key = get_setting(db, "closed_issues_api_key") or CLOSED_ISSUES_API_KEY
    url = f"{api_base.rstrip('/')}/api/external/issues/closed"
    headers = {"Content-Type": "application/json"}
    if not api_key:
        return RedirectResponse(url="/closed-issues?error=missing_api_key", status_code=303)
    headers["X-API-Key"] = api_key
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=headers, params={"apikey": api_key})
            resp.raise_for_status()
            payload = resp.json()
    except httpx.HTTPStatusError as exc:
        msg = f"{exc.response.status_code} {exc.response.text[:200]}"
        return RedirectResponse(url=f"/closed-issues?error={msg}", status_code=303)
    except Exception as exc:
        msg = str(exc)
        return RedirectResponse(url=f"/closed-issues?error={msg}", status_code=303)
    items = _extract_closed_issues(payload)
    created = 0
    updated = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        source_hash = _closed_issue_hash(item)
        issue = db.query(ClosedIssue).filter_by(source_hash=source_hash).first()
        team = item.get("team") or []
        voices = item.get("originalVoices") or []
        if issue:
            issue.customer = item.get("customer") or issue.customer
            issue.title = item.get("title") or issue.title
            issue.summary = item.get("summary") or issue.summary
            issue.team = team if isinstance(team, list) else []
            issue.original_voices = voices if isinstance(voices, list) else []
            issue.root_cause = item.get("rootCause") or issue.root_cause
            issue.resolution = item.get("resolution") or issue.resolution
            issue.raw_json = item
            updated += 1
        else:
            db.add(
                ClosedIssue(
                    source_hash=source_hash,
                    customer=item.get("customer"),
                    title=item.get("title"),
                    summary=item.get("summary"),
                    team=team if isinstance(team, list) else [],
                    original_voices=voices if isinstance(voices, list) else [],
                    root_cause=item.get("rootCause"),
                    resolution=item.get("resolution"),
                    raw_json=item,
                )
            )
            created += 1
    db.commit()
    return RedirectResponse(url="/closed-issues", status_code=303)


@app.post("/closed-issues/sync")
def closed_issues_sync(
    mode: str = Form("pending"),
    ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
):
    dify = DifyClient()
    if ids:
        issues = db.query(ClosedIssue).filter(ClosedIssue.id.in_(ids)).all()
    elif mode == "all":
        issues = db.query(ClosedIssue).all()
    else:
        issues = (
            db.query(ClosedIssue)
            .filter((ClosedIssue.kb_sync_status.is_(None)) | (ClosedIssue.kb_sync_status != "success"))
            .all()
        )
    grouped = {}
    for issue in issues:
        key = (issue.customer or "未知客户").strip()
        grouped.setdefault(key, []).append(issue)

    kb_doc_form = get_setting(db, "closed_issues_kb_doc_form") or CLOSED_ISSUES_KB_DOC_FORM
    if not kb_doc_form:
        kb_doc_form = "text"
    kb_process_mode = get_setting(db, "closed_issues_kb_process_mode") or CLOSED_ISSUES_KB_PROCESS_MODE
    for customer, customer_issues in grouped.items():
        name, text, metadata = _closed_issue_doc_payload(customer, customer_issues)
        try:
            content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            doc = db.query(ClosedIssueDoc).filter_by(customer=customer).first()
            existing_doc_id = doc.doc_id if doc else None
            result = dify.upsert_kb_group_document_in(
                dataset_id=CLOSED_ISSUES_KB_DATASET_ID,
                name=f"{CLOSED_ISSUES_KB_PREFIX}{customer}",
                text=text,
                metadata=metadata,
                existing_doc_id=existing_doc_id,
                doc_form_override=kb_doc_form,
                process_mode_override=kb_process_mode,
            )
            doc_id = result.get("doc_id") if isinstance(result, dict) else existing_doc_id
            if doc:
                doc.doc_id = doc_id
                doc.last_hash = content_hash
                doc.synced_at = dt.datetime.utcnow()
            else:
                db.add(
                    ClosedIssueDoc(
                        customer=customer,
                        doc_id=doc_id,
                        last_hash=content_hash,
                        synced_at=dt.datetime.utcnow(),
                    )
                )
            for issue in customer_issues:
                issue.kb_doc_id = doc_id
                issue.kb_sync_status = "success"
                issue.kb_sync_error = None
                issue.kb_synced_at = dt.datetime.utcnow()
        except Exception as exc:
            for issue in customer_issues:
                issue.kb_sync_status = "failed"
                issue.kb_sync_error = str(exc)
                issue.kb_synced_at = dt.datetime.utcnow()
    db.commit()
    return RedirectResponse(url="/closed-issues", status_code=303)


@app.get("/bots", response_class=HTMLResponse)
def bots_dashboard(request: Request, db: Session = Depends(get_db)):
    integrations = db.query(BotIntegration).order_by(BotIntegration.created_at.desc()).all()
    channels = (
        db.query(BotChannel)
        .order_by(BotChannel.created_at.desc())
        .limit(200)
        .all()
    )
    messages = (
        db.query(BotMessage)
        .order_by(BotMessage.created_at.desc())
        .limit(200)
        .all()
    )
    replies = (
        db.query(BotReply)
        .order_by(BotReply.created_at.desc())
        .limit(200)
        .all()
    )
    groups = db.query(CustomerGroup).order_by(CustomerGroup.name.asc()).all()
    counts = {g.id: g.message_total or 0 for g in groups}
    analyzed_counts = {}
    for g in groups:
        latest_task = _get_last_completed_task(db, g.id)
        analyzed_counts[g.id] = latest_task.message_count if latest_task and latest_task.message_count else 0
    un_analyzed_counts = {
        g.id: max((g.message_total or 0) - analyzed_counts.get(g.id, 0), 0) for g in groups
    }
    profiles = db.query(GroupProfile).all()
    rpa_configs = db.query(RpaGroupConfig).all()
    profile_map = {p.group_id: p for p in profiles}
    rpa_map = {c.group_id: c for c in rpa_configs}
    now = dt.datetime.now(dt.timezone.utc)
    tz_local = dt.timezone(dt.timedelta(hours=8))
    rpa_view = {}
    for cfg in rpa_configs:
        created = cfg.created_at or now
        if created.tzinfo is None:
            created = created.replace(tzinfo=dt.timezone.utc)
        total_seconds = max((now - created).total_seconds(), 0)
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        duration_text = f"{days}天{hours}小时{minutes}分钟"
        stats = cfg.config_json or {}
        replied = stats.get("replied_count") or stats.get("replied") or stats.get("reply_count") or 0
        status_key = (cfg.status or "").lower()
        if status_key in ("active", "running", "monitoring"):
            status_cn = "监管中"
            status_class = "status-monitor"
        elif status_key in ("replying", "responding"):
            status_cn = "正在回复"
            status_class = "status-reply"
        elif status_key in ("inactive", "stopped", "disabled"):
            status_cn = "未接管"
            status_class = "status-off"
        else:
            status_cn = cfg.status or "-"
            status_class = "status-off"
        start_local = created.astimezone(tz_local)
        start_text = start_local.strftime("%Y-%m-%d %H:%M")
        rpa_view[cfg.group_id] = {
            "duration_text": duration_text,
            "start_ts": int(created.timestamp()),
            "start_text": start_text,
            "replied": replied,
            "status_cn": status_cn,
            "status_class": status_class,
        }
    display_maps = db.query(GroupDisplayMap).all()
    display_map = {m.group_id: m for m in display_maps}
    return templates.TemplateResponse(
        "bots.html",
        {
            "request": request,
            "integrations": integrations,
            "channels": channels,
            "messages": messages,
            "replies": replies,
            "groups": groups,
            "counts": counts,
            "analyzed_counts": analyzed_counts,
            "un_analyzed_counts": un_analyzed_counts,
            "profile_map": profile_map,
            "rpa_map": rpa_map,
            "rpa_view": rpa_view,
            "display_map": display_map,
        },
    )


@app.post("/bots/channels/bind")
def bind_bot_channel(
    provider: str = Form(...),
    external_id: str = Form(...),
    name: Optional[str] = Form(None),
    group_roomid: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    group_id = None
    if group_roomid:
        group = db.query(CustomerGroup).filter_by(external_id=group_roomid).first()
        group_id = group.id if group else None
    channel = _upsert_bot_channel(
        db,
        provider=provider.strip(),
        external_id=external_id.strip(),
        name=(name or "").strip() or None,
        group_id=group_id,
    )
    _log_operation(
        db,
        action="bot_channel_bind",
        status="ok",
        message=f"{provider}:{external_id} -> group_id={group_id or '-'}",
        group_id=group_id,
    )
    return RedirectResponse(url="/bots", status_code=303)


@app.post("/bots/takeover/cancel")
def cancel_takeover(
    roomid: str = Form(...),
    db: Session = Depends(get_db),
):
    group = db.query(CustomerGroup).filter_by(external_id=roomid).first()
    if not group:
        return RedirectResponse(url="/bots", status_code=303)
    resp = _rpa_remove_roomid(db, group)
    if resp.get("error"):
        _log_operation(
            db,
            action="rpa_takeover_cancel",
            status="failed",
            message=f"group_id={group.id} {resp.get('error')}",
            group_id=group.id,
        )
        return RedirectResponse(url="/bots", status_code=303)
    cfg = db.query(RpaGroupConfig).filter_by(group_id=group.id).first()
    if cfg:
        cfg.status = "inactive"
        if not cfg.config_json:
            cfg.config_json = {}
        cfg.config_json["blocked"] = True
        db.commit()
    _log_operation(
        db,
        action="rpa_takeover_cancel",
        status="ok",
        message=f"group_id={group.id} roomid={group.external_id}",
        group_id=group.id,
    )
    return RedirectResponse(url="/bots", status_code=303)


@app.get("/audiences", response_class=HTMLResponse)
def audiences_page(request: Request, db: Session = Depends(get_db)):
    groups = db.query(CustomerGroup).order_by(CustomerGroup.name.asc()).all()
    roomid = request.query_params.get("roomid")
    selected = None
    if roomid:
        selected = db.query(CustomerGroup).filter_by(external_id=roomid).first()
    if not selected and groups:
        selected = groups[0]
    members = db.query(GroupMember).filter_by(group_id=selected.id).order_by(GroupMember.id.asc()).all() if selected else []
    profile = db.query(GroupProfile).filter_by(group_id=selected.id).first() if selected else None
    return templates.TemplateResponse(
        "audiences.html",
        {
            "request": request,
            "groups": groups,
            "selected_group": selected,
            "members": members,
            "profile": profile,
        },
    )


@app.post("/audiences/profile/save")
def audiences_profile_save(
    roomid: str = Form(...),
    manual_notes: str = Form(""),
    manual_tags: str = Form(""),
    manual_summary: str = Form(""),
    db: Session = Depends(get_db),
):
    group = db.query(CustomerGroup).filter_by(external_id=roomid).first()
    if not group:
        return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)
    profile = db.query(GroupProfile).filter_by(group_id=group.id).first()
    summary = profile.summary_json if profile and profile.summary_json else {}
    summary = dict(summary) if isinstance(summary, dict) else {}
    summary["manual_notes"] = manual_notes.strip()
    summary["manual_tags"] = manual_tags.strip()
    summary["manual_summary"] = manual_summary.strip()
    if profile:
        profile.summary_json = summary
        db.commit()
    else:
        profile = GroupProfile(
            group_id=group.id,
            last_task_id=None,
            summary_json=summary,
            topics_json=[],
            closed_stats_json={},
        )
        db.add(profile)
        db.commit()
    return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)


@app.post("/audiences/members/save")
def audiences_member_save(
    roomid: str = Form(...),
    member_id: Optional[int] = Form(None),
    external_user_id: str = Form(""),
    name: str = Form(""),
    nickname: str = Form(""),
    real_name: str = Form(""),
    role: str = Form(""),
    profile_text: str = Form(""),
    db: Session = Depends(get_db),
):
    group = db.query(CustomerGroup).filter_by(external_id=roomid).first()
    if not group:
        return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)
    if member_id:
        member = db.query(GroupMember).filter_by(id=member_id, group_id=group.id).first()
    else:
        member = None
    if member:
        member.external_user_id = external_user_id.strip() or None
        member.name = name.strip() or member.name
        member.nickname = nickname.strip() or None
        member.real_name = real_name.strip() or None
        member.role = role.strip() or None
        member.profile_text = profile_text.strip() or None
    else:
        member = GroupMember(
            group_id=group.id,
            external_user_id=external_user_id.strip() or None,
            name=name.strip() or "未命名",
            nickname=nickname.strip() or None,
            real_name=real_name.strip() or None,
            role=role.strip() or None,
            profile_text=profile_text.strip() or None,
        )
        db.add(member)
    db.commit()
    return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)


@app.post("/audiences/members/delete")
def audiences_member_delete(
    member_id: int = Form(...),
    roomid: str = Form(...),
    db: Session = Depends(get_db),
):
    group = db.query(CustomerGroup).filter_by(external_id=roomid).first()
    if not group:
        return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)
    db.query(GroupMember).filter_by(id=member_id, group_id=group.id).delete()
    db.commit()
    return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)


@app.post("/audiences/members/sync")
def audiences_members_sync(
    roomid: str = Form(...),
    db: Session = Depends(get_db),
):
    group = db.query(CustomerGroup).filter_by(external_id=roomid).first()
    if not group:
        return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)
    api_base = get_setting(db, "company_api_base") or "http://192.168.230.160:19000/api"
    api_key = get_setting(db, "company_api_key")
    api = CompanyApiClient(base_url=api_base, token=api_key)
    groups = api.list_groups(include_users=True)
    target = None
    for g in groups:
        gid = g.get("roomid") or g.get("id") or g.get("chatid") or g.get("group_id")
        if gid == group.external_id:
            target = g
            break
    if not target:
        return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)
    members = (
        target.get("member_list")
        or target.get("memberList")
        or target.get("members")
        or target.get("users")
        or []
    )
    existing = db.query(GroupMember).filter_by(group_id=group.id).all()
    existing_by_ext = {m.external_user_id: m for m in existing if m.external_user_id}
    existing_by_name = {m.name: m for m in existing if m.name}
    seen_ids = set()
    for mem in members:
        name = (
            mem.get("display_name")
            or mem.get("displayName")
            or mem.get("name")
            or mem.get("userid")
            or mem.get("user_id")
            or mem.get("external_userid")
            or "未命名"
        )
        role_type = mem.get("type")
        role = "内部" if role_type == 1 else "外部" if role_type == 2 else None
        ext_id = mem.get("userid") or mem.get("user_id") or mem.get("external_userid") or mem.get("external_user_id")
        member = existing_by_ext.get(ext_id) if ext_id else None
        if not member and not ext_id:
            member = existing_by_name.get(name)
        if member:
            member.external_user_id = ext_id or member.external_user_id
            member.name = name or member.name
            member.role = role or member.role
            seen_ids.add(member.id)
        else:
            member = GroupMember(
                group_id=group.id,
                external_user_id=ext_id,
                name=name,
                role=role,
            )
            db.add(member)
    db.commit()
    return RedirectResponse(url=f"/audiences?roomid={roomid}", status_code=303)


@app.post("/bots/groups/display-map")
def update_group_display_map(
    group_roomid: str = Form(...),
    display_name: str = Form(""),
    db: Session = Depends(get_db),
):
    group = db.query(CustomerGroup).filter_by(external_id=group_roomid).first()
    if not group:
        return RedirectResponse(url="/bots", status_code=303)
    display_name = display_name.strip()
    mapping = db.query(GroupDisplayMap).filter_by(group_id=group.id).first()
    if mapping:
        mapping.display_name = display_name or None
    else:
        mapping = GroupDisplayMap(group_id=group.id, display_name=display_name or None)
        db.add(mapping)
    db.commit()
    _log_operation(
        db,
        action="group_display_map_update",
        status="ok",
        message=f"group_id={group.id} display={display_name or '-'}",
        group_id=group.id,
    )
    return RedirectResponse(url="/bots", status_code=303)


@app.post("/bots/clear-messages")
def clear_bot_messages(db: Session = Depends(get_db)):
    # Delete replies first due to FK constraints
    db.query(BotReply).delete(synchronize_session=False)
    db.query(BotMessage).delete(synchronize_session=False)
    db.commit()
    _log_operation(db, action="bot_clear_messages", status="ok", message="cleared bot messages")
    return RedirectResponse(url="/bots", status_code=303)


@app.post("/bots/clear-logs")
def clear_bot_logs(db: Session = Depends(get_db)):
    db.query(OperationLog).delete(synchronize_session=False)
    db.commit()
    return RedirectResponse(url="/bots", status_code=303)


@app.post("/bots/appchat/create")
def create_app_chat(
    name: str = Form(...),
    owner: str = Form(...),
    userlist: str = Form(...),
    chatid: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    users = [u.strip() for u in userlist.split(",") if u.strip()]
    if owner and owner not in users:
        users.insert(0, owner)
    wecom = WeComClient(scope="app")
    result = wecom.create_app_chat(name=name.strip(), owner=owner.strip(), userlist=users, chatid=(chatid or "").strip() or None)
    if result.get("ok"):
        _log_operation(db, action="wecom_appchat_create", status="ok", message=f"创建群聊成功 {result.get('data', {}).get('chatid')}", group_id=None)
    else:
        _log_operation(db, action="wecom_appchat_create", status="failed", message=f"创建群聊失败 {result.get('error')}", group_id=None)
    return RedirectResponse(url="/bots", status_code=303)


@app.post("/bots/appchat/send")
def send_app_chat_message(
    chatid: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    wecom = WeComClient(scope="app")
    result = wecom.send_app_chat_message(chatid=chatid.strip(), content=content.strip())
    if result.get("ok"):
        _log_operation(db, action="wecom_appchat_send", status="ok", message="应用群聊发送成功", group_id=None)
    else:
        _log_operation(db, action="wecom_appchat_send", status="failed", message=f"应用群聊发送失败 {result.get('error')}", group_id=None)
    return RedirectResponse(url="/bots", status_code=303)




@app.post("/api/wecom/dify/reply")
def wecom_dify_reply(
    payload: dict = Body(...),
    authorization: Optional[str] = Header(None),
):
    # Optional API key protection (reuse CRM_KB_API_KEY)
    _require_kb_api_key(authorization)
    query = (payload.get("query") or payload.get("message") or "").strip()
    user = (payload.get("user") or "").strip() or None
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")
    result = _call_wecom_dify_agent(query, user_id=user)
    answer = (result.get("answer") or "").strip()
    return {"answer": answer, "ok": bool(answer)}


@app.post("/api/wecom/dify/closure")
def wecom_dify_closure(
    payload: dict = Body(...),
    authorization: Optional[str] = Header(None),
):
    _require_kb_api_key(authorization)
    result = _call_wecom_dify_closure(payload or {})
    return result


async def _handle_wecom_callback(
    scope: str,
    body: bytes,
    msg_signature: Optional[str],
    timestamp: Optional[str],
    nonce: Optional[str],
    db: Session,
):
    wecom = WeComClient(scope=scope)
    if not wecom.debug_plaintext and not wecom.is_callback_configured():
        raise HTTPException(status_code=501, detail="WeCom callback not configured yet")

    payload = {}
    if wecom.debug_plaintext:
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:invalid_json")
            return {"result": "invalid_json"}
    else:
        try:
            from xml.etree import ElementTree as ET
            xml_root = ET.fromstring(body.decode("utf-8"))
            encrypt_text = xml_root.findtext("Encrypt")
        except Exception:
            _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:invalid_xml")
            raise HTTPException(status_code=400, detail="Invalid XML")
        if encrypt_text:
            if not msg_signature or not timestamp or not nonce:
                _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:missing_signature_params")
                raise HTTPException(status_code=400, detail="Missing signature params")
            if not wecom.verify_signature(msg_signature, timestamp, nonce, encrypt_text):
                _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:invalid_signature")
                raise HTTPException(status_code=403, detail="Invalid signature")
            plain = wecom.decrypt_message(encrypt_text)
            if not plain:
                reason = wecom.last_error or "decrypt_failed"
                _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:{reason}")
                raise HTTPException(status_code=400, detail="Decrypt failed")
            try:
                xml_plain = ET.fromstring(plain)
                payload = {child.tag: (child.text or "") for child in xml_plain}
            except Exception:
                _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:invalid_decrypted_xml")
                raise HTTPException(status_code=400, detail="Invalid decrypted XML")
        else:
            payload = {child.tag: (child.text or "") for child in xml_root}
            _log_operation(db, action="wecom_callback_warn", status="ok", message=f"{scope}:missing_encrypt_use_plain")

    external_group_id = (
        payload.get("roomid")
        or payload.get("external_group_id")
        or payload.get("ChatId")
        or payload.get("RoomId")
        or payload.get("RoomID")
        or ""
    ).strip()
    group_name = (payload.get("group_name") or payload.get("ChatName") or "").strip() or None
    sender_name = (payload.get("sender") or payload.get("sender_name") or payload.get("FromUserName") or "").strip() or None
    sender_id = (payload.get("sender_id") or payload.get("userid") or payload.get("FromUserName") or "").strip() or None
    content = (payload.get("content") or payload.get("Content") or "").strip()
    if not content:
        content = json.dumps(payload, ensure_ascii=False)[:2000]
    external_message_id = (payload.get("msgid") or payload.get("external_message_id") or payload.get("MsgId") or "").strip() or None
    mentioned_list = payload.get("MentionedList") or payload.get("mentioned_list") or ""
    mentioned_mobile_list = payload.get("MentionedMobileList") or payload.get("mentioned_mobile_list") or ""
    is_mentioned = bool(payload.get("is_mentioned"))
    if not is_mentioned:
        if isinstance(mentioned_list, str) and mentioned_list:
            is_mentioned = True
        if isinstance(mentioned_mobile_list, str) and mentioned_mobile_list:
            is_mentioned = True
    if not is_mentioned and content and "@" in content:
        is_mentioned = True
    if scope == "app":
        is_mentioned = True

    if not external_group_id:
        if scope == "app":
            external_group_id = sender_id or (external_message_id or "app_direct")
        else:
            raise HTTPException(status_code=400, detail="Missing roomid")

    received_at = None
    raw_ts = payload.get("received_at") or payload.get("msgtime")
    if raw_ts:
        try:
            if isinstance(raw_ts, (int, float)):
                received_at = dt.datetime.utcfromtimestamp(float(raw_ts))
            elif isinstance(raw_ts, str):
                received_at = dt.datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        except Exception:
            received_at = None

    channel = _upsert_bot_channel(
        db,
        provider=f"wecom_{scope}",
        external_id=external_group_id,
        name=group_name,
    )

    existing = None
    if external_message_id:
        existing = (
            db.query(BotMessage)
            .filter_by(channel_id=channel.id, external_message_id=external_message_id)
            .first()
        )
    if existing:
        return {"result": "dup"}

    msg = BotMessage(
        channel_id=channel.id,
        external_message_id=external_message_id,
        sender_name=sender_name,
        sender_id=sender_id,
        content=content,
        received_at=received_at,
        is_mentioned=is_mentioned,
        auto_reply=is_mentioned,
        meta_json=payload,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    _log_operation(db, action="wecom_receive", status="ok", message=f"{scope}:收到消息", group_id=channel.group_id)

    if is_mentioned:
        quick_text = _get_quick_reply_text()
        quick_reply = BotReply(
            message_id=msg.id,
            provider=f"wecom_{scope}",
            content=quick_text,
            status="queued",
            reply_mode="quick",
        )
        db.add(quick_reply)
        db.commit()
        if quick_text:
            _log_operation(db, action="wecom_send_quick_start", status="running", message=f"{scope}:发送快速回复", group_id=channel.group_id)
            if scope == "app":
                send_result = wecom.send_app_message(
                    to_user=sender_id,
                    content=quick_text,
                )
            else:
                send_result = wecom.send_group_message(
                    external_group_id=external_group_id,
                    content=quick_text,
                    at_user_ids=[sender_id] if sender_id else None,
                )
            if send_result.get("ok"):
                quick_reply.status = "sent"
                quick_reply.sent_at = dt.datetime.utcnow()
                _log_operation(db, action="wecom_send_quick", status="ok", message=f"{scope}:快速回复已发送", group_id=channel.group_id)
            else:
                quick_reply.status = "failed"
                quick_reply.error = send_result.get("error") or "send_failed"
                _log_operation(db, action="wecom_send_quick", status="failed", message=f"{scope}:快速回复失败 {quick_reply.error}", group_id=channel.group_id)
            db.commit()

        _log_operation(db, action="wecom_dify_start", status="running", message=f"{scope}:调用Dify", group_id=channel.group_id)
        dify_resp = _call_wecom_dify_agent(content, user_id=sender_id)
        reply_text = dify_resp.get("answer") or ""
        debug_raw = dify_resp.get("debug_raw") or []
        if debug_raw:
            try:
                debug_text = json.dumps(debug_raw, ensure_ascii=False)[:1200]
            except Exception:
                debug_text = str(debug_raw)[:1200]
            _log_operation(db, action="wecom_dify_raw", status="ok", message=debug_text, group_id=channel.group_id)
        if reply_text:
            _log_operation(db, action="wecom_dify_done", status="ok", message=f"{scope}:Dify结果已生成", group_id=channel.group_id)
        else:
            raw_preview = dify_resp.get("raw") or []
            try:
                raw_text = json.dumps(raw_preview, ensure_ascii=False)[:800]
            except Exception:
                raw_text = str(raw_preview)[:800]
            _log_operation(db, action="wecom_dify_done", status="failed", message=f"{scope}:Dify无有效回复 {raw_text}", group_id=channel.group_id)
        if reply_text:
            reply = BotReply(
                message_id=msg.id,
                provider=f"wecom_{scope}",
                content=reply_text,
                status="queued",
                reply_mode="auto",
            )
            db.add(reply)
            db.commit()
            _log_operation(db, action="wecom_send_dify_start", status="running", message=f"{scope}:发送Dify回复", group_id=channel.group_id)
            if scope == "app":
                send_result = wecom.send_app_message(
                    to_user=sender_id,
                    content=reply_text,
                )
            else:
                send_result = wecom.send_group_message(
                    external_group_id=external_group_id,
                    content=reply_text,
                    at_user_ids=[sender_id] if sender_id else None,
                )
            if send_result.get("ok"):
                reply.status = "sent"
                reply.sent_at = dt.datetime.utcnow()
                _log_operation(db, action="wecom_send_dify", status="ok", message=f"{scope}:Dify回复已发送", group_id=channel.group_id)
            else:
                reply.status = "failed"
                reply.error = send_result.get("error") or "send_failed"
                _log_operation(db, action="wecom_send_dify", status="failed", message=f"{scope}:Dify回复失败 {reply.error}", group_id=channel.group_id)
            db.commit()

    if wecom.debug_plaintext:
        return {"result": "ok"}
    encrypted = wecom.encrypt_message("success")
    if not encrypted:
        return PlainTextResponse("success")
    encrypt_text, signature, ts, nonce = encrypted
    response_xml = (
        "<xml>"
        f"<Encrypt><![CDATA[{encrypt_text}]]></Encrypt>"
        f"<MsgSignature><![CDATA[{signature}]]></MsgSignature>"
        f"<TimeStamp>{ts}</TimeStamp>"
        f"<Nonce><![CDATA[{nonce}]]></Nonce>"
        "</xml>"
    )
    return PlainTextResponse(response_xml, media_type="application/xml")


@app.post("/integrations/wecom/app/callback")
async def wecom_app_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    msg_signature: Optional[str] = None,
    timestamp: Optional[str] = None,
    nonce: Optional[str] = None,
    db: Session = Depends(get_db),
):
    body = await request.body()
    background_tasks.add_task(_handle_wecom_callback, "app", body, msg_signature, timestamp, nonce, db)
    return PlainTextResponse("success")


@app.post("/integrations/wecom/contact/callback")
async def wecom_contact_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    msg_signature: Optional[str] = None,
    timestamp: Optional[str] = None,
    nonce: Optional[str] = None,
    db: Session = Depends(get_db),
):
    body = await request.body()
    background_tasks.add_task(_handle_wecom_callback, "contact", body, msg_signature, timestamp, nonce, db)
    return PlainTextResponse("success")


def _wecom_verify_get(scope: str, msg_signature: Optional[str], signature: Optional[str], timestamp: Optional[str], nonce: Optional[str], echostr: Optional[str], db: Session):
    wecom = WeComClient(scope=scope)
    if wecom.debug_plaintext:
        return PlainTextResponse("ok")
    signature_value = msg_signature or signature
    if not (signature_value and timestamp and nonce and echostr):
        _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:missing_params_get")
        raise HTTPException(status_code=400, detail="Missing params")
    if not wecom.verify_signature(signature_value, timestamp, nonce, echostr):
        _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:invalid_signature_get")
        raise HTTPException(status_code=403, detail="Invalid signature")
    plain = wecom.decrypt_message(echostr)
    if not plain:
        _log_operation(db, action="wecom_callback_error", status="failed", message=f"{scope}:{wecom.last_error or 'decrypt_failed_get'}")
        raise HTTPException(status_code=400, detail="Decrypt failed")
    return PlainTextResponse(plain)


@app.get("/integrations/wecom/app/callback")
def wecom_app_callback_verify(
    msg_signature: Optional[str] = None,
    signature: Optional[str] = None,
    timestamp: Optional[str] = None,
    nonce: Optional[str] = None,
    echostr: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return _wecom_verify_get("app", msg_signature, signature, timestamp, nonce, echostr, db)


@app.get("/integrations/wecom/contact/callback")
def wecom_contact_callback_verify(
    msg_signature: Optional[str] = None,
    signature: Optional[str] = None,
    timestamp: Optional[str] = None,
    nonce: Optional[str] = None,
    echostr: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return _wecom_verify_get("contact", msg_signature, signature, timestamp, nonce, echostr, db)


@app.get("/integrations/wecom/diagnose")
def wecom_diagnose(scope: str = "contact"):
    wecom = WeComClient(scope=scope)
    aes_key = (wecom.encoding_aes_key or "")
    aes_len = len(aes_key)
    try:
        decoded = wecom._get_aes_key()  # type: ignore[attr-defined]
        decoded_len = len(decoded) if decoded else 0
    except Exception:
        decoded_len = 0
    return {
        "scope": scope,
        "corp_id_loaded": bool(wecom.corp_id),
        "token_loaded": bool(wecom.token),
        "aes_key_length": aes_len,
        "aes_decoded_length": decoded_len,
        "aes_key_fingerprint": wecom.aes_key_fingerprint(),
        "debug_plaintext": wecom.debug_plaintext,
    }


@app.post("/integrations/wecom/send")
def wecom_send_message(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    external_group_id = (payload.get("external_group_id") or payload.get("roomid") or "").strip()
    content = (payload.get("content") or "").strip()
    if not external_group_id or not content:
        raise HTTPException(status_code=400, detail="Missing external_group_id/content")
    at_user_ids = payload.get("at_user_ids") or []
    channel = _upsert_bot_channel(
        db,
        provider="wecom",
        external_id=external_group_id,
        name=(payload.get("group_name") or "").strip() or None,
        group_id=payload.get("group_id"),
    )
    msg = BotMessage(
        channel_id=channel.id,
        content=content,
        sender_name="system",
        sender_id="system",
        received_at=dt.datetime.utcnow(),
        is_mentioned=bool(at_user_ids),
        auto_reply=False,
        status="triggered",
        meta_json=payload,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    reply = BotReply(
        message_id=msg.id,
        provider="wecom",
        content=content,
        status="queued",
        reply_mode="manual",
    )
    db.add(reply)
    db.commit()

    wecom = WeComClient(scope="contact")
    send_result = wecom.send_group_message(
        external_group_id=external_group_id,
        content=content,
        at_user_ids=at_user_ids,
    )
    if send_result.get("ok"):
        reply.status = "sent"
        reply.sent_at = dt.datetime.utcnow()
    else:
        reply.status = "failed"
        reply.error = send_result.get("error") or "send_failed"
    db.commit()

    return {"result": "ok", "reply_status": reply.status}


@app.post("/qa/{qa_id}/sync")
def qa_sync(qa_id: int, db: Session = Depends(get_db)):
    item = db.query(QAItem).filter_by(id=qa_id).first()
    if not item:
        return {"ok": False, "error": "QA not found"}
    return qa_sync_group(item.group_id, db)


@app.post("/qa/group/{group_id}/sync-all")
def qa_sync_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(CustomerGroup).filter_by(id=group_id).first()
    if not group:
        return {"ok": False, "error": "Group not found"}
    dify = DifyClient()
    items = (
        db.query(QAItem)
        .filter_by(group_id=group_id)
        .filter(QAItem.status.in_(["approved", "pushed"]))
        .order_by(QAItem.id.asc())
        .all()
    )
    text = _build_group_doc_text(items)
    theme_titles = []
    for item in items:
        if item.source_review and item.source_review.segment:
            seg = item.source_review.segment.strip()
            if seg and seg not in theme_titles:
                theme_titles.append(seg)
    subtheme_titles = []
    if theme_titles:
        latest_result = (
            db.query(AnalysisResult)
            .join(AnalysisTask, AnalysisResult.task_id == AnalysisTask.id)
            .filter(AnalysisTask.group_id == group.id)
            .order_by(AnalysisResult.id.desc())
            .first()
        )
        if latest_result:
            stage3 = (latest_result.result_json or {}).get("raw", {}).get("stage3") or {}
            for theme in stage3.get("themes", []):
                if theme.get("theme_title") not in theme_titles:
                    continue
                for sub in theme.get("subthemes", []):
                    title = sub.get("title") or ""
                    if title and title not in subtheme_titles:
                        subtheme_titles.append(title)
    metadata = {
        "group_id": group.id,
        "group_name": group.name,
        "source": "crm_qa_group",
        "themes": theme_titles,
        "subthemes": subtheme_titles,
    }
    try:
        current_name = _kb_doc_name(dify.kb_name_prefix, group.name)
        legacy_name = _kb_doc_name(dify.kb_name_prefix, f"group:{group.id}")
        if legacy_name != current_name:
            try:
                legacy_id = dify._find_kb_doc_id_by_name(legacy_name)
                if legacy_id:
                    dify._delete_kb_document(legacy_id)
            except Exception:
                pass
        kb_result = dify.upsert_kb_group_document(
            name=current_name,
            text=text,
            metadata=metadata,
            existing_doc_id=None,
        )
        doc_id = kb_result.get("doc_id") if isinstance(kb_result, dict) else None
        for item in items:
            item.dify_doc_id = doc_id
            item.dify_sync_status = "success" if doc_id else "failed"
            item.dify_synced_at = dt.datetime.utcnow()
            if doc_id:
                item.status = "pushed"
        _log_operation(
            db,
            action="sync_group",
            status="success" if doc_id else "failed",
            message=f"群文档同步完成，条目 {len(items)}，doc_id={doc_id or '-'}",
            group_id=group.id,
        )
    except Exception as exc:
        for item in items:
            item.dify_sync_status = "failed"
            item.dify_sync_error = str(exc)
            item.dify_synced_at = dt.datetime.utcnow()
        db.commit()
        _log_operation(
            db,
            action="sync_group",
            status="failed",
            message=f"群文档同步失败：{str(exc)}",
            group_id=group.id,
        )
        return {"ok": False, "error": str(exc)}
    db.commit()
    return {"ok": True, "doc_id": doc_id}


@app.get("/qa/story/{candidate_id}")
def qa_story(candidate_id: str, request: Request, db: Session = Depends(get_db)):
    result_id, subtheme_id = _parse_candidate_token(candidate_id)
    group_id = None
    result = None
    try:
        group_id = int(request.query_params.get("group_id") or 0)
    except Exception:
        group_id = None
    if result_id:
        result = db.query(AnalysisResult).filter_by(id=result_id).first()
    if not result and group_id:
        result = (
            db.query(AnalysisResult)
            .join(AnalysisTask, AnalysisResult.task_id == AnalysisTask.id)
            .filter(AnalysisTask.group_id == group_id)
            .order_by(AnalysisResult.id.desc())
            .first()
        )
    if not result:
        result = db.query(AnalysisResult).order_by(AnalysisResult.id.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    task = db.query(AnalysisTask).filter_by(id=result.task_id).first()
    group = db.query(CustomerGroup).filter_by(id=task.group_id).first() if task else None
    candidate = _find_candidate_from_result(result, subtheme_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    history = []
    theme = _find_theme_by_subtheme(result, subtheme_id)
    if theme:
        for sub in theme.get("subthemes", []):
            latest = sub.get("latest_qa") or {}
            history.append(
                {
                    "q": latest.get("question") or "",
                    "a": latest.get("answer") or "",
                    "status": sub.get("state") or "",
                    "updated_at": None,
                }
            )

    return {
        "group_name": group.name if group else "",
        "question": candidate.get("question") or "",
        "answer": candidate.get("answer") or "",
        "summary": candidate.get("summary") or "",
        "content": "",
        "segment": candidate.get("theme_title") or "",
        "subtheme": candidate.get("subtheme_title") or "",
        "customer_name": "",
        "agent_name": "",
        "status": "pending_review",
        "history": history,
    }


@app.post("/qa/batch/approve")
def qa_batch_approve(payload: dict = Body(...), db: Session = Depends(get_db)):
    ids = payload.get("ids") or []
    group_id = payload.get("group_id")
    reviewer = payload.get("reviewer") or "batch"
    segment = payload.get("segment") or "auto"
    approved = 0
    for message_id in ids:
        question = ""
        answer = ""
        if str(message_id).isdigit():
            message = db.query(RawMessage).filter_by(id=int(message_id)).first()
            if not message:
                continue
            analysis = message.analysis_json or {}
            question = analysis.get("question") or (message.content[:80] if message.content else "问题")
            answer = analysis.get("answer") or message.content or "-"
        else:
            result_id, subtheme_id = _parse_candidate_token(str(message_id))
            result = None
            if result_id:
                result = db.query(AnalysisResult).filter_by(id=result_id).first()
            if not result and group_id:
                result = (
                    db.query(AnalysisResult)
                    .join(AnalysisTask, AnalysisResult.task_id == AnalysisTask.id)
                    .filter(AnalysisTask.group_id == int(group_id))
                    .order_by(AnalysisResult.id.desc())
                    .first()
                )
            if not result:
                result = db.query(AnalysisResult).order_by(AnalysisResult.id.desc()).first()
            if not result:
                continue
            candidate = _find_candidate_from_result(result, subtheme_id)
            if not candidate and group_id:
                recent_results = (
                    db.query(AnalysisResult)
                    .join(AnalysisTask, AnalysisResult.task_id == AnalysisTask.id)
                    .filter(AnalysisTask.group_id == int(group_id))
                    .order_by(AnalysisResult.id.desc())
                    .limit(5)
                    .all()
                )
                for res in recent_results:
                    candidate = _find_candidate_from_result(res, subtheme_id)
                    if candidate:
                        result = res
                        break
            if not candidate:
                continue
            question = candidate.get("question") or "问题"
            answer = candidate.get("answer") or "-"
            segment = candidate.get("theme_title") or segment
            external_id = str(message_id)
            message = db.query(RawMessage).filter_by(external_message_id=external_id).first()
            if not message:
                if not group_id:
                    continue
                message = RawMessage(
                    group_id=int(group_id),
                    external_message_id=external_id,
                    content=question,
                    received_at=dt.datetime.utcnow(),
                    analysis_json={"question": question, "answer": answer, "summary": ""},
                    status="pending_review",
                )
                db.add(message)
                db.flush()
        review = db.query(Review).filter_by(message_id=message.id).first()
        if review:
            review.reviewer = reviewer
            review.segment = segment
            review.notes = "batch approve"
        else:
            review = Review(
                message_id=message.id,
                reviewer=reviewer,
                segment=segment,
                notes="batch approve",
            )
            db.add(review)
            db.flush()
        qa = db.query(QAItem).filter_by(source_review_id=review.id).first()
        if qa:
            qa.question = question
            qa.answer = answer
            qa.status = "approved"
        else:
            qa = QAItem(
                group_id=message.group_id,
                question=question,
                answer=answer,
                source_review_id=review.id,
                status="approved",
            )
            db.add(qa)
        message.status = "reviewed"
        approved += 1
    db.commit()
    return {"approved": approved}


@app.post("/qa/batch/reject")
def qa_batch_reject(payload: dict = Body(...), db: Session = Depends(get_db)):
    ids = payload.get("ids") or []
    group_id = payload.get("group_id")
    reviewer = payload.get("reviewer") or "batch"
    rejected = 0
    for message_id in ids:
        if str(message_id).isdigit():
            message = db.query(RawMessage).filter_by(id=int(message_id)).first()
            if not message:
                continue
        else:
            _result_id, _subtheme_id = _parse_candidate_token(str(message_id))
            external_id = str(message_id)
            message = db.query(RawMessage).filter_by(external_message_id=external_id).first()
            if not message and group_id:
                message = RawMessage(
                    group_id=int(group_id),
                    external_message_id=external_id,
                    content="",
                    received_at=dt.datetime.utcnow(),
                    analysis_json={},
                    status="pending_review",
                )
                db.add(message)
                db.flush()
            if not message:
                continue
        review = db.query(Review).filter_by(message_id=message.id).first()
        if review:
            review.reviewer = reviewer
            review.segment = "rejected"
            review.notes = "batch reject"
        else:
            review = Review(
                message_id=message.id,
                reviewer=reviewer,
                segment="rejected",
                notes="batch reject",
            )
            db.add(review)
        message.status = "rejected"
        rejected += 1
    db.commit()
    return {"rejected": rejected}


@app.post("/qa/batch/tag")
def qa_batch_tag(payload: dict = Body(...), db: Session = Depends(get_db)):
    ids = payload.get("ids") or []
    tags = payload.get("tags") or ""
    updated = 0
    for qa_id in ids:
        item = db.query(QAItem).filter_by(id=qa_id).first()
        if not item:
            continue
        item.tags = tags
        updated += 1
    db.commit()
    return {"updated": updated}


@app.post("/qa/batch/push")
def qa_batch_push(payload: dict = Body(...), db: Session = Depends(get_db)):
    ids = payload.get("ids") or []
    dify = DifyClient()
    group_ids = (
        db.query(QAItem.group_id)
        .filter(QAItem.id.in_(ids))
        .distinct()
        .all()
    )
    pushed = 0
    errors = []
    for (gid,) in group_ids:
        if not gid:
            continue
        result = qa_sync_group(gid, db)
        if isinstance(result, dict) and result.get("ok") is False:
            errors.append({"group_id": gid, "error": result.get("error")})
            continue
        pushed += 1
    db.commit()
    _log_operation(
        db,
        action="batch_push",
        status="failed" if errors else "success",
        message=f"批量入库群 {len(group_ids)} 个，成功 {pushed}",
        group_id=None,
    )
    if errors:
        return {"ok": False, "pushed": pushed, "errors": errors}
    return {"ok": True, "pushed": pushed}


@app.post("/qa/batch/sync")
def qa_batch_sync(payload: dict = Body(...), db: Session = Depends(get_db)):
    ids = payload.get("ids") or []
    group_id = payload.get("group_id")
    if not ids and group_id:
        return qa_sync_group(int(group_id), db)
    group_ids = (
        db.query(QAItem.group_id)
        .filter(QAItem.id.in_(ids))
        .distinct()
        .all()
    )
    synced = 0
    errors = []
    for (gid,) in group_ids:
        if not gid:
            continue
        result = qa_sync_group(gid, db)
        if isinstance(result, dict) and result.get("ok") is False:
            errors.append({"group_id": gid, "error": result.get("error")})
            continue
        synced += 1
    db.commit()
    _log_operation(
        db,
        action="batch_sync",
        status="failed" if errors else "success",
        message=f"批量同步群 {len(group_ids)} 个，成功 {synced}",
        group_id=None,
    )
    if errors:
        return {"ok": False, "synced": synced, "errors": errors}
    return {"ok": True, "synced": synced}


@app.post("/qa/batch/delete")
def qa_batch_delete(payload: dict = Body(...), db: Session = Depends(get_db)):
    ids = payload.get("ids") or []
    if not ids:
        return {"ok": True, "deleted": 0}
    items = db.query(QAItem).filter(QAItem.id.in_(ids)).all()
    for item in items:
        if item.source_review and item.source_review.message:
            item.source_review.message.status = "pending_review"
    group_ids = (
        db.query(QAItem.group_id)
        .filter(QAItem.id.in_(ids))
        .distinct()
        .all()
    )
    deleted = (
        db.query(QAItem)
        .filter(QAItem.id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    errors = []
    for (gid,) in group_ids:
        if not gid:
            continue
        result = qa_sync_group(gid, db)
        if isinstance(result, dict) and result.get("ok") is False:
            errors.append({"group_id": gid, "error": result.get("error")})
    _log_operation(
        db,
        action="batch_delete",
        status="failed" if errors else "success",
        message=f"批量删除 {deleted} 条，同步群 {len(group_ids)} 个",
        group_id=None,
    )
    if errors:
        return {"ok": False, "deleted": deleted, "errors": errors}
    return {"ok": True, "deleted": deleted}


@app.get("/api/kb/ping")
def kb_ping(authorization: Optional[str] = Header(None)):
    _require_kb_api_key(authorization)
    return {"status": "ok"}


@app.get("/api/kb/pages")
def kb_pages(
    group_id: int,
    updated_since: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    _require_kb_api_key(authorization)
    group = db.query(CustomerGroup).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    query = db.query(QAItem).filter_by(group_id=group.id)
    if updated_since:
        try:
            since_dt = dt.datetime.fromisoformat(updated_since.replace("Z", "+00:00"))
            query = query.filter(QAItem.updated_at >= since_dt)
        except ValueError:
            pass
    items = query.order_by(QAItem.updated_at.desc().nullslast(), QAItem.id.desc()).all()
    pages = []
    for item in items:
        ts = item.updated_at or item.created_at
        pages.append(
            {
                "id": str(item.id),
                "name": item.question[:80] if item.question else f"qa-{item.id}",
                "updated_at": ts.isoformat() if ts else None,
            }
        )
    return {
        "workspace_id": str(group.id),
        "workspace_name": group.name,
        "pages": pages,
    }


@app.get("/api/kb/content")
def kb_content(
    group_id: int,
    qa_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    _require_kb_api_key(authorization)
    group = db.query(CustomerGroup).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    item = db.query(QAItem).filter_by(id=qa_id, group_id=group.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="QA not found")
    content = (
        f"[group] {group.name}\n"
        f"[segment] {item.source_review.segment}\n"
        f"[question] {item.question}\n"
        f"[answer] {item.answer}\n"
        f"[qa_id] {item.id}\n"
    )
    return {
        "workspace_id": str(group.id),
        "workspace_name": group.name,
        "page_id": str(item.id),
        "content": content,
    }


@app.get("/api/qa/logs")
def qa_logs(
    group_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(OperationLog)
    if group_id:
        query = query.filter(OperationLog.group_id == group_id)
    items = (
        query.order_by(OperationLog.created_at.desc(), OperationLog.id.desc())
        .limit(min(max(limit, 1), 200))
        .all()
    )
    logs = [
        {
            "id": item.id,
            "action": item.action,
            "status": item.status,
            "message": item.message,
            "created_at": item.created_at.isoformat() if item.created_at else "",
        }
        for item in items
    ]
    return {"logs": logs}
