"""Razonamiento espacial verificable con Shapely y PyProj."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from pyproj import Geod
from shapely.geometry import shape

from .engine_contracts import EngineResult, ReasoningCapability, ReasoningProfile


class SpatialEngineAdapter:
    name = "shapely_pyproj"
    capabilities: Sequence[ReasoningCapability] = (ReasoningCapability.SPATIAL,)
    priority = 50

    def _spec(self, problem: Any) -> Dict[str, Any]:
        indicators = dict(getattr(problem, "structural_indicators", {}) or {})
        return dict(indicators.get("spatial_spec") or {})

    def can_handle(self, problem: Any, profile: ReasoningProfile) -> bool:
        spec = self._spec(problem)
        return profile.requires(ReasoningCapability.SPATIAL) and bool(
            spec.get("geometries") and spec.get("queries")
        )

    def execute(self, problem: Any, context: Optional[Dict[str, Any]] = None) -> EngineResult:
        spec = self._spec(problem)
        try:
            raw_geometries = dict(spec.get("geometries") or {})
            queries = list(spec.get("queries") or [])
            if not raw_geometries:
                raise ValueError("spatial_spec.geometries is required")
            if not queries:
                raise ValueError("spatial_spec.queries is required")

            geometries = {name: shape(value) for name, value in raw_geometries.items()}
            geod = Geod(ellps=str(spec.get("ellipsoid") or "WGS84"))
            results = []

            for query in queries:
                operation = str(query.get("op", "")).lower()
                left_name = str(query.get("left", ""))
                right_name = str(query.get("right", ""))
                if left_name not in geometries or right_name not in geometries:
                    raise ValueError(f"Unknown geometry in query: {query}")
                left = geometries[left_name]
                right = geometries[right_name]

                if operation == "contains":
                    value = left.contains(right)
                elif operation == "within":
                    value = left.within(right)
                elif operation == "intersects":
                    value = left.intersects(right)
                elif operation == "touches":
                    value = left.touches(right)
                elif operation == "overlaps":
                    value = left.overlaps(right)
                elif operation == "distance":
                    value = float(left.distance(right))
                elif operation == "geodesic_distance_m":
                    if left.geom_type != "Point" or right.geom_type != "Point":
                        raise ValueError("geodesic_distance_m requires Point geometries")
                    _, _, value = geod.inv(left.x, left.y, right.x, right.y)
                    value = float(value)
                else:
                    raise ValueError(f"Unsupported spatial operation: {operation}")

                results.append(
                    {
                        "op": operation,
                        "left": left_name,
                        "right": right_name,
                        "value": value,
                    }
                )

            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="success",
                data={"queries": results, "ellipsoid": str(spec.get("ellipsoid") or "WGS84")},
                evidence={"spatial_queries": results},
                validation={"valid": True, "query_count": len(results)},
                transfer_payload={"spatial_results": results},
                deterministic=True,
            )
        except Exception as exc:
            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="formalization_error",
                formalization_errors=[str(exc)],
                validation={"valid": False},
                deterministic=True,
            )
