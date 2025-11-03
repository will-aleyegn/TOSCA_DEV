"""
SQLAlchemy database models for TOSCA.

Based on architecture/02_database_schema.md
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class TechUser(Base):
    """Technician/operator user accounts."""

    __tablename__ = "tech_users"

    tech_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # technician, supervisor, admin
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="technician")
    created_subjects: Mapped[list["Subject"]] = relationship(
        "Subject", back_populates="created_by_tech"
    )

    def __repr__(self) -> str:
        return f"<TechUser(id={self.tech_id}, username='{self.username}', role='{self.role}')>"


class Subject(Base):
    """Anonymized subject records for longitudinal tracking."""

    __tablename__ = "subjects"

    subject_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )  # P-YYYY-NNNN
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    created_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False, index=True
    )
    created_by_tech_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tech_users.tech_id")
    )
    last_modified_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Relationships
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="subject")
    created_by_tech: Mapped[Optional["TechUser"]] = relationship(
        "TechUser", back_populates="created_subjects"
    )

    def __repr__(self) -> str:
        return f"<Subject(id={self.subject_id}, code='{self.subject_code}')>"


class Protocol(Base):
    """Saved treatment protocols (templates)."""

    __tablename__ = "protocols"

    protocol_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    protocol_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    protocol_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # constant, linear_ramp, multi_step, custom
    protocol_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    created_by_tech_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tech_users.tech_id")
    )
    last_modified_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_used_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Relationships
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="protocol")

    def __repr__(self) -> str:
        return (
            f"<Protocol(id={self.protocol_id}, name='{self.protocol_name}', "
            f"type='{self.protocol_type}')>"
        )


class Session(Base):
    """Treatment sessions - each subject visit creates one session."""

    __tablename__ = "sessions"

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.subject_id"), nullable=False, index=True
    )
    tech_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tech_users.tech_id"), nullable=False, index=True
    )
    protocol_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("protocols.protocol_id"))

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # in_progress, completed, aborted, paused
    abort_reason: Mapped[Optional[str]] = mapped_column(Text)

    treatment_site: Mapped[Optional[str]] = mapped_column(String(100))
    treatment_notes: Mapped[Optional[str]] = mapped_column(Text)

    protocol_name: Mapped[Optional[str]] = mapped_column(String(100))  # Snapshot
    protocol_data_snapshot: Mapped[Optional[str]] = mapped_column(Text)  # JSON snapshot

    session_folder_path: Mapped[Optional[str]] = mapped_column(String(500))
    video_path: Mapped[Optional[str]] = mapped_column(String(500))

    # Summary statistics
    total_laser_on_time_seconds: Mapped[Optional[float]] = mapped_column(Float)
    avg_power_watts: Mapped[Optional[float]] = mapped_column(Float)
    max_power_watts: Mapped[Optional[float]] = mapped_column(Float)
    total_energy_joules: Mapped[Optional[float]] = mapped_column(Float)

    post_treatment_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="sessions")
    technician: Mapped["TechUser"] = relationship("TechUser", back_populates="sessions")
    protocol: Mapped[Optional["Protocol"]] = relationship("Protocol", back_populates="sessions")

    def __repr__(self) -> str:
        return (
            f"<Session(id={self.session_id}, subject_id={self.subject_id}, status='{self.status}')>"
        )


class SafetyLog(Base):
    """Comprehensive log of all safety-related events."""

    __tablename__ = "safety_log"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    session_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sessions.session_id"), index=True
    )
    tech_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tech_users.tech_id"))

    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e_stop_pressed, interlock_failure, etc.
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # info, warning, critical, emergency
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Hardware state
    system_state: Mapped[Optional[str]] = mapped_column(
        String(20)
    )  # idle, ready, armed, treating, fault
    laser_state: Mapped[Optional[str]] = mapped_column(String(20))
    footpedal_state: Mapped[Optional[bool]] = mapped_column(Boolean)
    smoothing_device_state: Mapped[Optional[bool]] = mapped_column(Boolean)
    photodiode_voltage_v: Mapped[Optional[float]] = mapped_column(Float)

    action_taken: Mapped[Optional[str]] = mapped_column(Text)
    details: Mapped[Optional[str]] = mapped_column(Text)  # JSON

    def __repr__(self) -> str:
        return (
            f"<SafetyLog(id={self.log_id}, type='{self.event_type}', severity='{self.severity}')>"
        )
