#!/usr/bin/env python3
"""
Script avanzado para búsqueda automática en UNMSM usando Playwright.
Recibe una consulta de búsqueda y devuelve resultados filtrados para información de admisión (2012-2022).
"""

import asyncio
import sys
import re
from playwright.async_api import async_playwright
from datetime import datetime

async def search_unmsm_admission(query):
    """
    Busca información de admisión de UNMSM para años 2012-2022.
    """
    results = []
    async with async_playwright() as p:
        # Lanzar navegador en modo headless para evitar problemas de GUI
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Ir a DuckDuckGo (menos propenso a captchas que Google inicialmente)
            await page.goto("https://duckduckgo.com", timeout=30000)
            await page.wait_for_selector('input[name="q"]', timeout=10000)
            
            # Ingresar consulta de búsqueda
            await page.fill('input[name="q"]', query)
            await page.press('input[name="q"]', 'Enter')
            
            # Esperar a que carguen los resultados
            await page.wait_for_selector('.result__body, .web-result, .result', timeout=15000)
            await page.wait_for_timeout(3000)  # Tiempo extra para carga completa
            
            # Extraer texto de los resultados
            # Selectores comunes en DuckDuckGo
            result_elements = await page.query_selector_all('.result__body, .web-result-snippet, .result-snippet')
            
            for element in result_elements[:10]:  # Limitar a primeros 10 resultados
                text = await element.inner_text()
                if text and len(text.strip()) > 20:  # Filtrar resultados muy cortos
                    results.append(text.strip())
            
            # También intentar obtener títulos y enlaces
            title_elements = await page.query_selector_all('.result__title, .result__url')
            for i, elem in enumerate(title_elements[:5]):
                title = await elem.inner_text()
                if title and len(title.strip()) > 5:
                    if i < len(results):
                        results[i] = f"TÍTULO: {title}\n{results[i]}"
                    else:
                        results.append(f"TÍTULO: {title}")
                        
        except Exception as e:
            print(f"Error durante la búsqueda: {str(e)}", file=sys.stderr)
        finally:
            await browser.close()
    
    return results

def filter_relevant_results(results, years=range(2012, 2023)):
    """
    Filtra resultados para encontrar menciones de primer puesto, puntajes y años relevantes.
    """
    filtered = []
    # Patrones de búsqueda en español
    patterns = [
        r'primer puesto',
        r'primer lugar',
        r'primer puesto.*medicina',
        r'primer puesto.*ingeniería',
        r'puntaje.*[0-9]{4}',  # Ej: puntaje 1500
        r'[0-9]{4}\s*puntaje',
        r'admisión.*[0-9]{4}',
        r'ingreso.*[0-9]{4}',
        r'UNMSM.*[0-9]{4}',
    ]
    
    year_pattern = r'|'.join(map(str, years))
    
    for result in results:
        result_lower = result.lower()
        # Verificar si contiene año en rango y palabras clave
        if any(re.search(pattern, result_lower) for pattern in patterns) or \
           re.search(year_pattern, result):
            # Extraer líneas que contengan información relevante
            lines = result.split('\n')
            relevant_lines = []
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['primer puesto', 'primer lugar', 'puntaje', 'admisión', 'ingreso', 'unmsm']) or \
                   re.search(year_pattern, line):
                    relevant_lines.append(line.strip())
            
            if relevant_lines:
                filtered.append('\n'.join(relevant_lines))
    
    return filtered

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 unmsm_search.py \"tu consulta de búsqueda\"")
        print("Ejemplo: python3 unmsm_search.py \"primer puesto medicina UNMSM 2015\"")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    print(f"Buscando: {query}")
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Ejecutar búsqueda asíncrona
    results = asyncio.run(search_unmsm_admission(query))
    
    if not results:
        print("No se obtuvieron resultados. Puede deberse a:")
        print("- Conexión lenta")
        print("- Sitio bloqueando bots (CAPTCHA)")
        print("- Consulta demasiado específica")
        return
    
    print(f"Se obtuvieron {len(results)} resultados brutos.")
    print("-" * 50)
    
    # Filtrar resultados relevantes
    filtered = filter_relevant_results(results)
    
    if not filtered:
        print("No se encontró información específica sobre puestos de admisión en los años 2012-2022.")
        print("Resultados brutos (primeros 3):")
        for i, res in enumerate(results[:3]):
            print(f"{i+1}. {res[:200]}...")
        return
    
    print(f"Se encontraron {len(filtered)} resultados relevantes:")
    print("=" * 60)
    
    for i, result in enumerate(filted, 1):
        print(f"\nResultado {i}:")
        print("-" * 40)
        print(result)
        print("-" * 40)
    
    # Guardar resultados en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"unmsm_search_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Consulta: {query}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        for i, result in enumerate(filtered, 1):
            f.write(f"Resultado {i}:\n{result}\n{'-'*40}\n\n")
    
    print(f"\nResultados guardados en: {filename}")

if __name__ == "__main__":
    main()