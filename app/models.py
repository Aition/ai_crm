from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base


class CustomerGroup(Base):
    __tablename__ = "customer_groups"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(128), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    message_total = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("RawMessage", back_populates="group")
    qa_items = relationship("QAItem", back_populates="group")
    profile = relationship("GroupProfile", back_populates="group", uselist=False)
    rpa_config = relationship("RpaGroupConfig", back_populates="group", uselist=False)
    display_map = relationship("GroupDisplayMap", back_populates="group", uselist=False)


class RawMessage(Base):
    __tablename__ = "raw_messages"
    __table_args__ = (
        UniqueConstraint("external_message_id", name="uq_raw_messages_external_message_id"),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("customer_groups.id"), nullable=False)
    external_message_id = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=True)
    dify_task_id = Column(String(128), nullable=True)
    analysis_json = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, default="pending_review")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("CustomerGroup", back_populates="messages")
    review = relationship("Review", back_populates="message", uselist=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("raw_messages.id"), unique=True, nullable=False)
    reviewer = Column(String(128), nullable=True)
    segment = Column(String(128), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("RawMessage", back_populates="review")
    qa_item = relationship("QAItem", back_populates="source_review", uselist=False)


class QAItem(Base):
    __tablename__ = "qa_items"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("customer_groups.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_review_id = Column(Integer, ForeignKey("reviews.id"), unique=True, nullable=False)
    dify_doc_id = Column(String(128), nullable=True)
    category = Column(String(128), nullable=True)
    tags = Column(Text, nullable=True)
    product = Column(String(128), nullable=True)
    version_range = Column(String(128), nullable=True)
    keywords = Column(Text, nullable=True)
    quality_score = Column(Integer, nullable=True)
    is_generic = Column(Boolean, nullable=True)
    reason = Column(Text, nullable=True)
    steps = Column(Text, nullable=True)
    conditions = Column(Text, nullable=True)
    dify_sync_status = Column(String(32), nullable=True)
    dify_sync_error = Column(Text, nullable=True)
    dify_synced_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    group = relationship("CustomerGroup", back_populates="qa_items")
    source_review = relationship("Review", back_populates="qa_item")


class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(128), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("customer_groups.id"), nullable=False)
    status = Column(String(32), nullable=False, default="running")
    version_label = Column(String(64), nullable=False)
    message_count = Column(Integer, nullable=True)
    segments_count = Column(Integer, nullable=True)
    qa_count = Column(Integer, nullable=True)
    topics_count = Column(Integer, nullable=True)
    closed_topics_count = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    group = relationship("CustomerGroup")
    logs = relationship("AnalysisLog", back_populates="task")
    result = relationship("AnalysisResult", back_populates="task", uselist=False)


class AnalysisLog(Base):
    __tablename__ = "analysis_logs"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("analysis_tasks.id"), nullable=False)
    stage = Column(String(32), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("AnalysisTask", back_populates="logs")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("analysis_tasks.id"), unique=True, nullable=False)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("AnalysisTask", back_populates="result")


class ClosedIssue(Base):
    __tablename__ = "closed_issues"

    id = Column(Integer, primary_key=True)
    source_hash = Column(String(64), unique=True, nullable=False)
    customer = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    team = Column(JSON, nullable=True)
    original_voices = Column(JSON, nullable=True)
    root_cause = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    raw_json = Column(JSON, nullable=True)
    kb_doc_id = Column(String(128), nullable=True)
    kb_sync_status = Column(String(32), nullable=True)
    kb_sync_error = Column(Text, nullable=True)
    kb_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClosedIssueDoc(Base):
    __tablename__ = "closed_issue_docs"

    id = Column(Integer, primary_key=True)
    customer = Column(String(255), unique=True, nullable=False)
    doc_id = Column(String(128), nullable=True)
    last_hash = Column(String(64), nullable=True)
    synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GroupProfile(Base):
    __tablename__ = "group_profiles"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("customer_groups.id"), unique=True, nullable=False)
    last_task_id = Column(Integer, ForeignKey("analysis_tasks.id"), nullable=True)
    summary_json = Column(JSON, nullable=True)
    topics_json = Column(JSON, nullable=True)
    closed_stats_json = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("CustomerGroup", back_populates="profile")


class RpaGroupConfig(Base):
    __tablename__ = "rpa_group_configs"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("customer_groups.id"), unique=True, nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    config_json = Column(JSON, nullable=True)
    last_error = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("CustomerGroup", back_populates="rpa_config")


class GroupDisplayMap(Base):
    __tablename__ = "group_display_maps"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("customer_groups.id"), unique=True, nullable=False)
    display_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    group = relationship("CustomerGroup", back_populates="display_map")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("customer_groups.id"), nullable=False)
    external_user_id = Column(String(128), nullable=True)
    name = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=True)
    real_name = Column(String(255), nullable=True)
    role = Column(String(64), nullable=True)
    profile_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    group = relationship("CustomerGroup")


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, nullable=True)
    action = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BotIntegration(Base):
    __tablename__ = "bot_integrations"

    id = Column(Integer, primary_key=True)
    provider = Column(String(32), nullable=False)
    name = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    config_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BotChannel(Base):
    __tablename__ = "bot_channels"
    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uq_bot_channels_provider_external"),
    )

    id = Column(Integer, primary_key=True)
    provider = Column(String(32), nullable=False)
    external_id = Column(String(128), nullable=False)
    name = Column(String(255), nullable=True)
    group_id = Column(Integer, ForeignKey("customer_groups.id"), nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("CustomerGroup")
    messages = relationship("BotMessage", back_populates="channel")


class BotMessage(Base):
    __tablename__ = "bot_messages"
    __table_args__ = (
        UniqueConstraint("channel_id", "external_message_id", name="uq_bot_messages_channel_external"),
    )

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("bot_channels.id"), nullable=False)
    external_message_id = Column(String(128), nullable=True)
    sender_name = Column(String(128), nullable=True)
    sender_id = Column(String(128), nullable=True)
    content = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=True)
    is_mentioned = Column(Boolean, nullable=False, default=False)
    auto_reply = Column(Boolean, nullable=False, default=False)
    status = Column(String(32), nullable=False, default="received")
    dify_task_id = Column(String(128), nullable=True)
    meta_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    channel = relationship("BotChannel", back_populates="messages")
    replies = relationship("BotReply", back_populates="message")


class BotReply(Base):
    __tablename__ = "bot_replies"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("bot_messages.id"), nullable=False)
    provider = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="draft")
    reply_mode = Column(String(32), nullable=False, default="manual")
    external_message_id = Column(String(128), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    message = relationship("BotMessage", back_populates="replies")
