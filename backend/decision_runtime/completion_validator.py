from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

from backend.decision_runtime.event_bus import event_bus, Event, EventPriority


class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    BLOCK = "block"


@dataclass
class ValidationResult:
    name: str
    status: ValidationStatus
    details: str = ""
    weight: float = 1.0


ValidationCheck = Callable[[Dict[str, Any]], ValidationResult]


class CompletionValidator:
    def __init__(self):
        self._checks: List[ValidationCheck] = []
        self._init_default_checks()

    def _init_default_checks(self):
        self.register(self._check_requirements)
        self.register(self._check_architecture)
        self.register(self._check_implementation)
        self.register(self._check_tests)
        self.register(self._check_review)
        self.register(self._check_documentation)
        self.register(self._check_memory)
        self.register(self._check_risks)
        self.register(self._check_performance)
        self.register(self._check_security)
        self.register(self._check_constitution)

    def register(self, check: ValidationCheck):
        self._checks.append(check)

    def unregister(self, check: ValidationCheck):
        if check in self._checks:
            self._checks.remove(check)

    def validate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        results: List[ValidationResult] = []
        for check in self._checks:
            try:
                result = check(context)
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    name=check.__name__ if hasattr(check, "__name__") else "unknown",
                    status=ValidationStatus.FAIL,
                    details=f"Validation error: {e}",
                ))

        passed = sum(1 for r in results if r.status == ValidationStatus.PASS)
        total_weight = sum(r.weight for r in results)
        passed_weight = sum(r.weight for r in results if r.status in (ValidationStatus.PASS, ValidationStatus.WARN))
        score = round((passed_weight / total_weight * 100) if total_weight > 0 else 100, 1)

        blocking = [r for r in results if r.status == ValidationStatus.BLOCK]
        failures = [r for r in results if r.status == ValidationStatus.FAIL]

        event_bus.publish(Event(
            topic="completion.validated",
            source="completion_validator",
            data={
                "score": score,
                "passed": len(blocking) == 0,
                "total_checks": len(results),
                "passed_checks": passed,
                "blocking_issues": [b.name for b in blocking],
            },
            priority=EventPriority.NORMAL,
            correlation_id=context.get("correlation_id"),
        ))

        return {
            "completable": len(blocking) == 0,
            "score": score,
            "checks": [
                {"name": r.name, "status": r.status.value, "details": r.details}
                for r in results
            ],
            "passed_checks": passed,
            "total_checks": len(results),
            "blocking_issues": [b.name for b in blocking],
            "failed_checks": [f.name for f in failures],
        }

    def _check_requirements(self, ctx: Dict) -> ValidationResult:
        met = ctx.get("requirements_met", False)
        return ValidationResult(
            name="requirements_met",
            status=ValidationStatus.PASS if met else ValidationStatus.BLOCK,
            details="All mandatory requirements satisfied" if met else "Requirements not satisfied",
            weight=3.0,
        )

    def _check_architecture(self, ctx: Dict) -> ValidationResult:
        validated = ctx.get("architecture_validated", False)
        return ValidationResult(
            name="architecture_validated",
            status=ValidationStatus.PASS if validated else ValidationStatus.BLOCK,
            details="Architecture validated" if validated else "Architecture not validated",
            weight=2.0,
        )

    def _check_implementation(self, ctx: Dict) -> ValidationResult:
        complete = ctx.get("implementation_complete", False)
        return ValidationResult(
            name="implementation_complete",
            status=ValidationStatus.PASS if complete else ValidationStatus.FAIL,
            details="Implementation complete" if complete else "Implementation incomplete",
            weight=2.0,
        )

    def _check_tests(self, ctx: Dict) -> ValidationResult:
        passed = ctx.get("tests_passed", False)
        return ValidationResult(
            name="tests_passed",
            status=ValidationStatus.PASS if passed else ValidationStatus.BLOCK,
            details="All tests passed" if passed else "Tests not passing",
            weight=3.0,
        )

    def _check_review(self, ctx: Dict) -> ValidationResult:
        passed = ctx.get("review_passed", False)
        return ValidationResult(
            name="review_passed",
            status=ValidationStatus.PASS if passed else ValidationStatus.FAIL,
            details="Review completed" if passed else "Review pending",
            weight=2.0,
        )

    def _check_documentation(self, ctx: Dict) -> ValidationResult:
        updated = ctx.get("documentation_updated", False)
        return ValidationResult(
            name="documentation_updated",
            status=ValidationStatus.PASS if updated else ValidationStatus.WARN,
            details="Documentation updated" if updated else "Documentation not updated",
            weight=1.0,
        )

    def _check_memory(self, ctx: Dict) -> ValidationResult:
        updated = ctx.get("memory_updated", False)
        return ValidationResult(
            name="memory_updated",
            status=ValidationStatus.PASS if updated else ValidationStatus.WARN,
            details="Memory updated" if updated else "Memory not updated",
            weight=1.0,
        )

    def _check_risks(self, ctx: Dict) -> ValidationResult:
        documented = ctx.get("risks_documented", False)
        return ValidationResult(
            name="risks_documented",
            status=ValidationStatus.PASS if documented else ValidationStatus.WARN,
            details="Risks documented" if documented else "Risks not documented",
            weight=1.0,
        )

    def _check_performance(self, ctx: Dict) -> ValidationResult:
        evaluated = ctx.get("performance_evaluated", True)
        critical = ctx.get("performance_critical", False)
        if critical and not evaluated:
            return ValidationResult(
                name="performance_evaluated",
                status=ValidationStatus.FAIL,
                details="Performance not evaluated for critical path",
                weight=1.5,
            )
        return ValidationResult(
            name="performance_evaluated",
            status=ValidationStatus.PASS,
            details="Performance OK" if evaluated else "Not evaluated",
            weight=1.0,
        )

    def _check_security(self, ctx: Dict) -> ValidationResult:
        checked = ctx.get("security_checked", True)
        issues = ctx.get("security_issues", False)
        if issues:
            return ValidationResult(
                name="security_checked",
                status=ValidationStatus.BLOCK,
                details="Security issues unresolved",
                weight=3.0,
            )
        return ValidationResult(
            name="security_checked",
            status=ValidationStatus.PASS if checked else ValidationStatus.WARN,
            details="Security checked" if checked else "Security not checked",
            weight=2.0,
        )

    def _check_constitution(self, ctx: Dict) -> ValidationResult:
        compliant = ctx.get("constitution_compliant", True)
        return ValidationResult(
            name="constitution_compliant",
            status=ValidationStatus.PASS if compliant else ValidationStatus.BLOCK,
            details="Constitution compliant" if compliant else "Constitution violation detected",
            weight=5.0,
        )


completion_validator = CompletionValidator()
