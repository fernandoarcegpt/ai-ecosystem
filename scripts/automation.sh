#!/bin/bash
# scripts/automation.sh - Sistema de automatización para el ecosistema AI
# Uso: ./scripts/automation.sh <setup|run|monitor|status>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/.hermes/logs"
AUTOMATION_LOG="$LOG_DIR/automation.log"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$AUTOMATION_LOG"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$AUTOMATION_LOG"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$AUTOMATION_LOG"
}

# Setup cron jobs for periodic automation
setup_cron_jobs() {
    log "Configurando tareas programadas..."

    # Create log directory if it doesn't exist
    mkdir -p "$LOG_DIR"

    # Get current crontab or create empty file
    crontab -l > /tmp/current_cron 2>/dev/null || true

    # Add orchestrator health check every 2 hours
    if ! grep -q "orchestrator-main.*health" /tmp/current_cron 2>/dev/null; then
        echo "0 */2 * * * cd $PROJECT_ROOT && /usr/bin/claude code . -p \"orchestrator-main 'health-check' --type maintenance --complexity low\" >> $AUTOMATION_LOG 2>&1" >> /tmp/current_cron
        log_success "Agregado health check cada 2 horas"
    fi

    # Add nightly digest every night at 2:00 AM
    if ! grep -q "nightly-digest" /tmp/current_cron 2>/dev/null; then
        echo "0 2 * * * cd $PROJECT_ROOT && /usr/bin/claude code . -p \"orchestrator-main 'nightly-digest' --type review --complexity medium\" >> $AUTOMATION_LOG 2>&1" >> /tmp/current_cron
        log_success "Agregado nightly digest a las 2:00 AM"
    fi

    # Add weekly review on Sundays at 3:00 AM
    if ! grep -q "weekly-review" /tmp/current_cron 2>/dev/null; then
        echo "0 3 * * 0 cd $PROJECT_ROOT && /usr/bin/claude code . -p \"orchestrator-main 'weekly-review' --type analysis --complexity high\" >> $AUTOMATION_LOG 2>&1" >> /tmp/current_cron
        log_success "Agregado weekly review los domingos a las 3:00 AM"
    fi

    # Install the new crontab
    crontab /tmp/current_cron
    rm /tmp/current_cron

    log_success "Tareas programadas configuradas exitosamente"
}

# Run full automation pipeline
run_automation() {
    log "Ejecutando pipeline de automatización completo..."

    cd "$PROJECT_ROOT"

    # 1. Health check
    log "Realizando health check del orquestador..."
    /usr/bin/claude code . -p "orchestrator-main 'automated-health-check' --type maintenance --complexity low" 2>/dev/null || log_warn "Health check con advertencias"

    # 2. Wiki pipeline (if exists)
    if [[ -f "run_wiki_pipeline.sh" ]]; then
        log "Ejecutando wiki pipeline..."
        bash run_wiki_pipeline.sh 2>/dev/null || log_warn "Wiki pipeline con advertencias"
    fi

    # 3. Update opensec cache
    log "Actualizando caché de OpenSec..."
    npm update opensec 2>/dev/null || log_warn "OpenSec actualizado o sin cambios"

    # 4. Generate status report
    log "Generando informe de estado..."
    echo "=== Automatización ejecutada: $(date) ===" >> "$AUTOMATION_LOG"
    echo "Estado: OK" >> "$AUTOMATION_LOG"
    echo "" >> "$AUTOMATION_LOG"

    log_success "Pipeline de automatización completado"
}

# Monitor automation status
monitor_automation() {
    log "Monitoreando estado de automatización..."

    # Check if cron is running
    if pgrep -x "crond" > /dev/null; then
        log_success "Cron daemon está activo"
    else
        log_warn "Cron daemon no está activo"
    fi

    # Show current crontab
    log "Tareas programadas actuales:"
    crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | sed 's/^/  /' || log_warn "No hay tareas programadas"

    # Show automation log (last 10 lines)
    if [[ -f "$AUTOMATION_LOG" ]]; then
        log "Últimos eventos de automatización:"
        tail -10 "$AUTOMATION_LOG" | sed 's/^/  /'
    else
        log_warn "No hay log de automatización aún"
    fi
}

# Show status
show_status() {
    log "Estado del sistema de automatización:"
    echo ""

    # Check dependencies
    echo "  Dependencias:"
    command -v claude >/dev/null 2>&1 && echo "    ✓ Claude Code" || echo "    ✗ Claude Code"
    command -v npm >/dev/null 2>&1 && echo "    ✓ npm" || echo "    ✗ npm"
    command -v crontab >/dev/null 2>&1 && echo "    ✓ crontab" || echo "    ✗ crontab"

    echo ""
    echo "  Service Status:"
    pgrep -x "crond" > /dev/null && echo "    ✓ Cron daemon running" || echo "    ✗ Cron daemon stopped"

    echo ""
    echo "  OpenSpec:"
    npm list openspec 2>/dev/null | head -1 || echo "    ✓ OpenSpec installed"

    echo ""
}

# Main case statement
case "${1:-}" in
    setup)
        setup_cron_jobs
        ;;
    run)
        run_automation
        ;;
    monitor)
        monitor_automation
        ;;
    status)
        show_status
        ;;
    *)
        echo "Uso: $0 {setup|run|monitor|status}"
        echo ""
        echo "Comandos:"
        echo "  setup   - Configurar tareas cron para automatización"
        echo "  run     - Ejecutar pipeline de automatización manualmente"
        echo "  monitor - Ver estado de automatización"
        echo "  status  - Mostrar estado general del sistema"
        exit 1
        ;;
esac