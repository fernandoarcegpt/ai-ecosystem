#!/usr/bin/env python3
"""
Audit script for Hermes ecosystem before codebase-memory-mcp integration.
"""

import os
import json
import sys
from pathlib import Path

def audit_project_structure():
    """Audit the current project structure"""
    print("=" * 70)
    print("AUDITORÍA DE ESTRUCTURA DEL PROYECTO - ai-ecosystem")
    print("=" * 70)
    
    base_path = Path("/home/fernando/ai-ecosystem")
    
    # Core directories
    important_dirs = {
        "src/": "Código fuente principal",
        "knowledge-service/": "Servicio de Knowledge Broker",
        "storage/": "Almacenamiento KùzuDB para memoria",
        ".hermes/": "Configuración y plugins de Hermes",
        ".hermes/skills/": "Skills de Hermes",
        ".hermes/plugins/": "Plugins de Hermes", 
        "hermes-agent/": "Agente Hermes",
        "src/": "Código fuente principal",
        "patches/": "Sistema de gestión de parches",
        "notex/": "Notex para procesamiento de documentos",
        "library/": "Biblioteca/Documentación"
    }
    
    print("\n📁 ESTRUCTURA DE DIRECTORIOS:")
    for dir_path, description in important_dirs.items():
        full_path = base_path / dir_path
        exists = full_path.exists()
        status = "✅ EXISTE" if exists else "❌ NO ENCONTRADO"
        size_info = ""
        if exists and full_path.is_dir():
            try:
                file_count = sum(len(files) for _, _, files in os.walk(full_path))
                total_size = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file())
                size_info = f" ({file_count} archivos, ~{total_size/(1024*1024):.1f} MB)"
            except Exception as e:
                size_info = f" (error al contar: {e})"
        print(f"{status} {dir_path:<25} {description}{size_info}")

def audit_hermes_config():
    """Audit Hermes configuration"""
    print("\n⚙️ CONFIGURACIÓN DE HERMES:")
    
    config_path = Path("/home/fernando/.hermes/config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # Check for key sections
        sections = {
            "platform_toolsets": "toolsets de plataforma configurados",
            "memory.memory_enabled": "memoria básica habilitada", 
            "delegation.max_iterations": "delegación configurada",
            "skills.creation_nudge_interval": "intervalo de creación de skills"
        }
        
        for section, description in sections.items():
            if section in config_content:
                print(f"✅ {section}")
            else:
                print(f"❌ {section} - NO ENCONTRADO")
    else:
        print("❌ /home/fernando/.hermes/config.yaml - NO ENCONTRADO")

def audit_skills():
    """Audit Hermes skills"""
    print("\n🛠️ SKILLS DE HERMES:")
    
    skills_path = Path("/home/fernando/.hermes/skills")
    if skills_path.exists():
        skills_list = []
        for skill_dir in skills_path.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    with open(skill_file, 'r') as f:
                        content = f.read()
                        if 'name:' in content:
                            # Extract skill name from content
                            lines = content.split('\n')
                            for line in lines:
                                if line.strip().startswith('name:'):
                                    skill_name = line.strip().split(':', 1)[1].strip()
                                    skills_list.append(skill_name)
                                    break
        
        if skills_list:
            print(f"Encontradas {len(skills_list)} skills:")
            for skill in sorted(skills_list):
                print(f"  ✅ {skill}")
        else:
            print("❌ No se pudo detectar ninguna skill")
    else:
        print("❌ /home/fernando/.hermes/skills - NO ENCONTRADO")

def audit_plugins():
    """Audit Hermes plugins"""
    print("\n🔌 PLUGINS DE HERMES:")
    
    plugins_path = Path("/home/fernando/.hermes/plugins")
    if plugins_path.exists():
        plugins = list(plugins_path.iterdir())
        if plugins:
            print(f"Encontrados {len(plugins)} plugins:")
            for plugin in sorted(plugins, key=lambda x: x.name):
                if plugin.is_dir():
                    plugin_file = plugin / "SKILL.md" or plugin / "PLUGIN.md"
                    if plugin_file.exists():
                        with open(plugin_file, 'r') as f:
                            content = f.read()
                            if 'name:' in content:
                                lines = content.split('\n')
                                for line in lines:
                                    if line.strip().startswith('name:'):
                                        plugin_name = line.strip().split(':', 1)[1].strip()
                                        print(f"  ✅ {plugin_name}")
                                        break
        else:
            print("❌ No se encontraron plugins")
    else:
        print("❌ /home/fernando/.hermes/plugins - NO ENCONTRADO")

def audit_mcp_servers():
    """Audit existing MCP servers"""
    print("\n🔌 SERVIDORES MCP:")
    
    mcp_path = Path("/home/fernando/ai-ecosystem/.mcp.json")
    if mcp_path.exists():
        with open(mcp_path, 'r') as f:
            mcp_config = json.load(f)
        
        mcp_servers = mcp_config.get('mcpServers', {})
        print(f"Encontrados {len(mcp_servers)} servidores MCP:")
        
        for server_name, server_config in mcp_servers.items():
            command = server_config.get('command', 'N/A')
            args = server_config.get('args', [])
            optional = server_config.get('optional', False)
            status = "OPTIONAL" if optional else "MANDATORY"
            print(f"  ✅ {server_name:<20} {command} {' '.join(args)}")
            
    else:
        print("❌ /home/fernando/ai-ecosystem/.mcp.json - NO ENCONTRADO")

def audit_knowledge_broker():
    """Audit Knowledge Broker functionality"""
    print("\n🧠 KNOWLEDGE BROKER:")
    
    kb_path = Path("/home/fernando/ai-ecosystem/knowledge_broker.py")
    if kb_path.exists():
        with open(kb_path, 'r') as f:
            content = f.read()
        
        kb_functions = []
        if 'validate(' in content:
            kb_functions.append("validate")
        if 'write_to_vault(' in content:
            kb_functions.append("write_to_vault")
        if 'process_staging(' in content:
            kb_functions.append("process_staging")
        
        print(f"Funciones implementadas: {kb_functions}")
        
        # Check related files
        staging_dir = Path("/home/fernando/ai-ecosystem/staging")
        if staging_dir.exists():
            staging_files = list(staging_dir.glob("*.md"))
            print(f"  ✅ Staging directory: {len(staging_files)} archivos .md pendientes")
        else:
            print("  ❌ Directory staging/ no encontrado")
            
    else:
        print("❌ knowledge_broker.py - NO ENCONTRADO")

def audit_basic_memory():
    """Audit Basic Memory system"""
    print("\n📝 BASIC MEMORY:")
    
    # Check if there's a memories directory in .hermes
    memories_path = Path("/home/fernando/.hermes/memories")
    if memories_path.exists():
        memories = list(memories_path.iterdir())
        print(f"Encontrados {len(memories)} archivos de memoria básica")
        
        for memory in sorted(memories, key=lambda x: x.name):
            if memory.is_file():
                with open(memory, 'r') as f:
                    content = f.read()
                    if len(content.strip()) > 0:
                        print(f"  ✅ {memory.name} ({len(content)} chars)")
                    else:
                        print(f"  ⚠️ {memory.name} (vacío)")
    else:
        print("❌ /home/fernando/.hermes/memories - NO ENCONTRADO")

def audit_okf():
    """Audit OKF system"""
    print("\n🔍 OKF (Open Knowledge Framework):")
    
    okf_path = Path("/home/fernando/ai-ecosystem/okf_demo.py")
    if okf_path.exists():
        with open(okf_path, 'r') as f:
            content = f.read()
        
        if 'procedures' in content.lower():
            print("✅ Procedimientos OKF implementados")
        if 'knowledge' in content.lower():
            print("✅ Conocimiento OKF implementado")
            
    # Check procedures directory
    procedures_path = Path("/home/fernando/ai-ecosystem/procedures")
    if procedures_path.exists():
        procedures = list(procedures_path.glob("*.md"))
        print(f"  ✅ Procedures directory: {len(procedures)} archivos .md")
    else:
        print("❌ /home/fernando/ai-ecosystem/procedures - NO ENCONTRADO")

def audit_claude_code_integration():
    """Audit Claude Code integration"""
    print("\n🤖 INTEGRACIÓN DE CLAUDE CODE:")
    
    # Check for Claude Code related files
    claude_files = [
        Path("/home/fernando/.hermes/hermes-agent"),
        Path("/home/fernando/ai-ecosystem/.claude"),
    ]
    
    for claude_path in claude_files:
        if claude_path.exists():
            print(f"✅ {claude_path.relative_to('/')}")
        else:
            print(f"❌ {claude_path.relative_to('/')} - NO ENCONTRADO")

def audit_system_prompt():
    """Audit System Prompt content"""
    print("\n📜 SYSTEM PROMPT:")
    
    # Check for system prompt files
    system_prompt_files = [
        Path("/home/fernando/.hermes/config.yaml"),
        Path("/home/fernando/ai-ecosystem/CLAUDE.md"),
        Path("/home/fernando/ai-ecosystem/SYSTEM_BLUEPRINT.md"),
    ]
    
    for prompt_file in system_prompt_files:
        if prompt_file.exists():
            print(f"✅ {prompt_file.name}")
        else:
            print(f"❌ {prompt_file.name} - NO ENCONTRADO")

def audit_reasoning_policies():
    """Audit reasoning policies"""
    print("\n🧮 POLÍTICAS DE RAZONAMIENTO:")
    
    policies_path = Path("/home/fernando/ai-ecosystem/reasoning")
    if policies_path.exists():
        policies = list(policies_path.glob("*.py"))
        print(f"Encontradas {len(policies)} políticas de razonamiento")
        
        for policy in sorted(policies, key=lambda x: x.name):
            print(f"  ✅ {policy.name}")
    else:
        print("❌ /home/fernando/ai-ecosystem/reasoning - NO ENCONTRADO")

def audit_tests():
    """Audit test suite"""
    print("\n🧪 TESTS:")
    
    tests_path = Path("/home/fernando/ai-ecosystem/tests")
    if tests_path.exists():
        test_files = list(tests_path.glob("*.py"))
        print(f"Encontrados {len(test_files)} archivos de prueba")
        
        for test_file in sorted(test_files, key=lambda x: x.name):
            print(f"  ✅ {test_file.name}")
    else:
        print("❌ /home/fernando/ai-ecosystem/tests - NO ENCONTRADO")

def audit_recent_patches():
    """Audit recent patches created"""
    print("\n🔧 PARCHES RECIENTES:")
    
    patches_path = Path("/home/fernando/ai-ecosystem/patches")
    if patches_path.exists():
        patch_dirs = [d for d in patches_path.iterdir() if d.is_dir()]
        if patch_dirs:
            print(f"Creados {len(patch_dirs)} parches:")
            for patch_dir in sorted(patch_dirs, key=lambda x: x.name):
                print(f"  ✅ {patch_dir.name}")
        else:
            print("❌ No hay directorios de parches")
    else:
        print("❌ /home/fernando/ai-ecosystem/patches - NO ENCONTRADO")

def main():
    print("INICIAR AUDITORÍA DEL ECOSISTEMA DE HERMES")
    print("=" * 70)
    
    audit_project_structure()
    audit_hermes_config()
    audit_skills()
    audit_plugins()
    audit_mcp_servers()
    audit_knowledge_broker()
    audit_basic_memory()
    audit_okf()
    audit_claude_code_integration()
    audit_system_prompt()
    audit_reasoning_policies()
    audit_tests()
    audit_recent_patches()
    
    print("\n" + "=" * 70)
    print("AUDITORÍA COMPLETADA")
    print("=" * 70)
    
    # Generate a summary report
    summary = {
        "project_structure_audited": True,
        "skills_found": len(Path("/home/fernando/.hermes/skills").iterdir()) if Path("/home/fernando/.hermes/skills").exists() else 0,
        "plugins_found": len(Path("/home/fernando/.hermes/plugins").iterdir()) if Path("/home/fernando/.hermes/plugins").exists() else 0,
        "mcp_servers_configured": len(json.load(open("/home/fernando/ai-ecosystem/.mcp.json", 'r'))["mcpServers"]) if Path("/home/fernando/ai-ecosystem/.mcp.json").exists() else 0,
        "patches_created": len([d for d in Path("/home/fernando/ai-ecosystem/patches").iterdir() if d.is_dir()]) if Path("/home/fernando/ai-ecosystem/patches").exists() else 0,
        "knowledge_broker_active": Path("/home/fernando/ai-ecosystem/knowledge_broker.py").exists(),
        "okf_active": Path("/home/fernando/ai-ecosystem/okf_demo.py").exists(),
        "codebase_memory_mcp": "NOT FOUND - needs installation"
    }
    
    print("\n📊 RESUMEN DE AUDITORÍA:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return summary

if __name__ == "__main__":
    audit_result = main()
    sys.exit(0)