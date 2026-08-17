#!/usr/bin/env bash
# -------------------------------------------------
# Wrapper seguro para lanzar process_wiki.py por dominio
# -------------------------------------------------
# Cambia al directorio del proyecto
cd /home/fernando/ai-ecosystem || exit 1

# Lista de dominios a procesar
DOMAINS=("claude" "hermes")

# Procesa cada dominio
for domain in "${DOMAINS[@]}"; do
    echo "Procesando dominio: $domain"
    python3 process_wiki.py "$domain"
done

# Guarda la salida para depuración
exec >> /home/fernando/ai-ecosystem/cron_wiki.log 2>&1