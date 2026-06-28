from __future__ import annotations

import subprocess
from typing import Any


def read_nvidia_smi() -> dict[str, Any]:
    query = "index,name,memory.used,memory.total,utilization.gpu,power.draw"
    cmd = [
        "nvidia-smi",
        f"--query-gpu={query}",
        "--format=csv,noheader,nounits",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return {"available": False, "gpus": [], "detected_gpu_count": 0}

    gpus: list[dict[str, Any]] = []
    for line in out.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 6:
            continue
        idx, name, mem_used, mem_total, util, power = parts
        gpus.append(
            {
                "index": int(idx),
                "name": name,
                "memory_used_mb": float(mem_used),
                "memory_total_mb": float(mem_total),
                "gpu_util_percent": float(util),
                "power_watts": None if power in {"[N/A]", "N/A"} else float(power),
            }
        )
    return {
        "available": bool(gpus),
        "gpus": gpus,
        "detected_gpu_count": len(gpus),
        "detected_gpu_name": gpus[0]["name"] if gpus else None,
    }
