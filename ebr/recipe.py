"""Master Batch Record (MBR) / master recipe model."""
import json
from dataclasses import dataclass
from pathlib import Path

VALID_PHASE_TYPES = {"line_clearance", "equipment_check", "weigh_dispense", "process_parameter",
                     "sampling", "lims_result", "label_print", "yield"}
VALID_SIGNATURES = {"performer", "performer_verifier"}


class RecipeError(Exception):
    pass


@dataclass(frozen=True)
class Phase:
    phase_id: str
    op_id: str
    op_name: str
    type: str
    instruction: str
    signature: str
    spec: dict

    @property
    def has_limits(self) -> bool:
        return "low" in self.spec and "high" in self.spec


@dataclass(frozen=True)
class MasterRecipe:
    mbr_id: str
    version: str
    status: str
    product: dict
    bom: dict[str, dict]
    phases: tuple[Phase, ...]

    @classmethod
    def load(cls, path: str | Path) -> "MasterRecipe":
        raw = json.loads(Path(path).read_text())
        phases = []
        for op in raw["operations"]:
            for ph in op["phases"]:
                spec = {k: v for k, v in ph.items()
                        if k not in {"phase_id", "type", "instruction", "signature"}}
                phases.append(Phase(ph["phase_id"], op["op_id"], op["name"], ph["type"],
                                    ph["instruction"], ph["signature"], spec))
        recipe = cls(raw["mbr_id"], raw["version"], raw["status"], raw["product"],
                     {b["material"]: b for b in raw["bom"]}, tuple(phases))
        recipe.validate()
        return recipe

    def validate(self) -> None:
        ids = [p.phase_id for p in self.phases]
        if len(ids) != len(set(ids)):
            raise RecipeError("Duplicate phase IDs")
        for p in self.phases:
            if p.type not in VALID_PHASE_TYPES:
                raise RecipeError(f"{p.phase_id}: unknown phase type {p.type}")
            if p.signature not in VALID_SIGNATURES:
                raise RecipeError(f"{p.phase_id}: invalid signature rule {p.signature}")
            if p.has_limits and p.spec["low"] > p.spec["high"]:
                raise RecipeError(f"{p.phase_id}: low limit above high limit")
            for m in p.spec.get("materials", []):
                if m not in self.bom:
                    raise RecipeError(f"{p.phase_id}: material {m} not in BOM")

    def require_approved(self) -> None:
        if self.status != "Approved":
            raise RecipeError(f"{self.mbr_id} v{self.version} is '{self.status}'; only Approved MBRs can be used")
