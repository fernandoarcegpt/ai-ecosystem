#!/usr/bin/env python3
"""
Knowledge Broker — único punto de escritura hacia el vault de Obsidian.
Lee ~/ai-ecosystem/staging/, valida cada nota, y si aprueba, la escribe
al vault real vía Local REST API con MCP.
"""

import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".obsidian-broker" / ".env")

OBSIDIAN_URL = f"https://127.0.0.1:{os.getenv('OBSIDIAN_PORT', '27124')}"
OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY")

STAGING_DIR = Path(__file__).parent / "staging"


def validate(content: str) -> dict:
    """
    Valida una nota antes de aprobarla para el vault.
    Ajusta esta lógica según tus reglas reales (mismo contrato que Hermes).
    """
    if not content.strip():
        return {"aprobado": False, "tipo": "vacio", "detalle": "contenido vacío"}
    return {"aprobado": True, "tipo": "ruflo_report", "detalle": "ok"}


def write_to_vault(filename: str, content: str) -> bool:
    """Escribe una nota en el vault de Obsidian vía Local REST API."""
    resp = requests.put(
        f"{OBSIDIAN_URL}/vault/{filename}",
        headers={
            "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
            "Content-Type": "text/markdown",
        },
        data=content.encode("utf-8"),
        verify=False,
    )
    return resp.status_code in (200, 204)


def process_staging():
    """Procesa todos los .md pendientes en staging/."""
    if not STAGING_DIR.exists():
        print(f"[Broker] No existe {STAGING_DIR}, nada que procesar.")
        return

    for md_file in STAGING_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        result = validate(content)

        if result["aprobado"]:
            ok = write_to_vault(md_file.name, content)
            if ok:
                print(f"[Broker] ✓ {md_file.name} escrito al vault")
                md_file.unlink()  # limpia staging tras éxito
            else:
                print(f"[Broker] ✗ {md_file.name} falló al escribir al vault")
        else:
            print(f"[Broker] ⏸ {md_file.name} rechazado: {result['detalle']}")


if __name__ == "__main__":
    process_staging()
