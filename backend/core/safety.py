import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


SECRET_PATTERNS: Dict[str, str] = {
    "api_key": r"(?i)(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,64})['\"]?",
    "access_token": r"(?i)(?:access[_-]?token|accesstoken)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,64})['\"]?",
    "private_key": r"-----BEGIN\s+(?:RSA|EC|DSA|OPENSSH|PRIVATE)\s+KEY-----",
    "jwt_token": r"eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}",
    "github_token": r"(?i)gh[ps]_[a-zA-Z0-9_\-]{36,}",
    "aws_key": r"(?i)AKIA[0-9A-Z]{16}",
    "password": r"(?i)(?:password|pwd|passwd)\s*[:=]\s*['\"]?([a-zA-Z0-9!@#$%^&*()_+=\-]{8,})['\"]?",
    "connection_string": r"(?i)(?:connection[_-]?string|connstr)\s*[:=]\s*['\"]?([a-zA-Z0-9;:=_\-@.]+)['\"]?",
    "database_url": r"(?i)(?:DATABASE_URL|MONGODB_URI|REDIS_URL|postgres://|mysql://|mongodb://|redis://)[^\s'\"]+",
}


@dataclass
class SecretFinding:
    secret_type: str
    match: str
    line: int
    column: int
    risk: str


class ImpactSeverity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ImpactReport:
    action: str
    target: str
    severity: ImpactSeverity
    affected_resources: List[str]
    risk_level: str
    recovery_difficulty: str
    rollback_available: bool
    recommendation: str
    safe_alternatives: List[str] = field(default_factory=list)


class SecretDetector:
    def scan(self, content: str, filename: str = "") -> List[SecretFinding]:
        findings = []
        for secret_type, pattern in SECRET_PATTERNS.items():
            for match in re.finditer(pattern, content):
                line = content[:match.start()].count("\n") + 1
                col = match.start() - content[:match.start()].rfind("\n")
                risk = "critical" if secret_type in ("private_key", "aws_key", "database_url") else "high"
                findings.append(SecretFinding(
                    secret_type=secret_type, match=match.group(0)[:40],
                    line=line, column=col, risk=risk
                ))
        return findings

    def scan_file(self, path: str) -> Tuple[bool, List[SecretFinding]]:
        try:
            with open(path) as f:
                return True, self.scan(f.read(), path)
        except Exception:
            return False, []


class BackupVerifier:
    def verify(self, backup_path: str) -> Dict:
        from pathlib import Path
        p = Path(backup_path)
        if not p.exists():
            return {"valid": False, "reason": "Backup path does not exist"}
        if p.is_dir():
            files = list(p.rglob("*"))
            return {"valid": True, "type": "directory", "file_count": len(files),
                    "size_bytes": sum(f.stat().st_size for f in files if f.is_file()),
                    "accessible": all(os.access(f, os.R_OK) for f in files if f.is_file())}
        if p.is_file():
            return {"valid": True, "type": "file", "size_bytes": p.stat().st_size,
                    "accessible": os.access(p, os.R_OK)}
        return {"valid": False, "reason": "Unknown path type"}


class ImpactAnalyzer:
    DESTRUCTIVE_ACTIONS = {"delete", "drop", "remove", "destroy", "truncate", "force_push"}
    MODIFY_ACTIONS = {"write", "update", "modify", "rename", "move", "migrate"}
    CRITICAL_PATHS = [
        "agent-docs", "CONSTITUTION", "SAFETY_RULES", "PERMISSION_SYSTEM",
        "HUMAN_APPROVAL_RULES", "SYSTEM_ARCHITECTURE", "MEMORY_ARCHITECTURE",
    ]

    def analyze(self, action: str, target: str) -> ImpactReport:
        action_lower = action.lower()
        target_lower = target.lower()

        is_destructive = any(d in action_lower for d in self.DESTRUCTIVE_ACTIONS)
        is_modify = any(m in action_lower for m in self.MODIFY_ACTIONS)
        is_critical_path = any(c.lower() in target_lower for c in self.CRITICAL_PATHS)
        is_db = any(d in target_lower for d in ["database", "db/", ".db", "migration"])
        is_code = any(c in target_lower for c in [".py", ".ts", ".tsx", ".js", ".jsx"])
        is_config = any(c in target_lower for c in [".json", ".yaml", ".yml", ".env", "config"])

        if is_destructive and is_critical_path:
            severity = ImpactSeverity.CRITICAL
            risk = "critical"
            recovery = "very difficult"
            rollback = False
            rec = "This action targets critical system files. Do not proceed."
        elif is_destructive and is_db:
            severity = ImpactSeverity.HIGH
            risk = "high"
            recovery = "difficult"
            rollback = False
            rec = "Database destruction is irreversible. Verify backup first."
        elif is_destructive:
            severity = ImpactSeverity.HIGH
            risk = "high"
            recovery = "moderate"
            rollback = False
            rec = "Destructive action. Ensure backup exists before proceeding."
        elif is_modify and is_critical_path:
            severity = ImpactSeverity.HIGH
            risk = "high"
            recovery = "moderate"
            rollback = True
            rec = "Modifying critical system files. Backup recommended."
        elif is_modify and is_db:
            severity = ImpactSeverity.MEDIUM
            risk = "medium"
            recovery = "moderate"
            rollback = True
            rec = "Database modification. Rollback plan recommended."
        elif is_modify and is_config:
            severity = ImpactSeverity.MEDIUM
            risk = "medium"
            recovery = "easy"
            rollback = True
            rec = "Configuration change. Verify syntax after modification."
        else:
            severity = ImpactSeverity.LOW
            risk = "low"
            recovery = "easy"
            rollback = True
            rec = "Low impact action. Standard precautions apply."

        affected = []
        if is_critical_path:
            affected.append("Critical system files")
        if is_db:
            affected.append("Database")
        if is_code:
            affected.append("Source code")
        if is_config:
            affected.append("Configuration")

        safe_alternatives = self._get_safe_alternatives(action, is_destructive, is_modify)

        return ImpactReport(
            action=action, target=target, severity=severity,
            affected_resources=affected or ["Target resource"],
            risk_level=risk, recovery_difficulty=recovery,
            rollback_available=rollback, recommendation=rec,
            safe_alternatives=safe_alternatives
        )

    def _get_safe_alternatives(self, action: str, destructive: bool, modify: bool) -> List[str]:
        alts = []
        if destructive:
            alts.append("Move to trash/archive instead of permanent delete")
            alts.append("Rename/disable instead of remove")
            alts.append("Create backup before deletion")
        if not destructive and modify:
            alts.append("Create backup before modification")
        return alts


class SafetyController:
    def __init__(self):
        self.detector = SecretDetector()
        self.verifier = BackupVerifier()
        self.analyzer = ImpactAnalyzer()
        self.audit_log: List[Dict] = []

    def scan_secrets(self, content: str, filename: str = "") -> Dict:
        findings = self.detector.scan(content, filename)
        entry = {"action": "scan_secrets", "findings": len(findings),
                 "timestamp": datetime.utcnow().isoformat()}
        self.audit_log.append(entry)
        return {"findings": [f.__dict__ for f in findings], "count": len(findings),
                "has_secrets": len(findings) > 0}

    def scan_file_secrets(self, path: str) -> Dict:
        ok, findings = self.detector.scan_file(path)
        if not ok:
            return {"error": f"Cannot read {path}", "findings": [], "count": 0, "has_secrets": False}
        return self.scan_secrets("", path)

    def verify_backup(self, backup_path: str) -> Dict:
        return self.verifier.verify(backup_path)

    def analyze_impact(self, action: str, target: str) -> Dict:
        return self.analyzer.analyze(action, target).__dict__

    def check_pre_operation(self, action: str, target: str, content: str = "") -> Dict:
        impact = self.analyze_impact(action, target)
        secrets = self.scan_secrets(content) if content else {"findings": [], "count": 0, "has_secrets": False}
        return {"impact": impact, "secrets": secrets,
                "safe_to_proceed": not secrets["has_secrets"] and impact["severity"] not in ("critical",),
                "timestamp": datetime.utcnow().isoformat()}

    def get_audit_log(self, limit: int = 20) -> List[Dict]:
        return self.audit_log[-limit:]


import os


safety_controller = SafetyController()
