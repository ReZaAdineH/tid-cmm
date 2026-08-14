"""TID-CMM — Threat-Informed Detection Capability Maturity Model."""
__version__ = "1.0.0"
from .model import load_model, validate_model, export_json  # noqa: F401
from .scoring import Response, score_assessment, band_for  # noqa: F401
