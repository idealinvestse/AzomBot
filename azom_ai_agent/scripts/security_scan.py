#!/usr/bin/env python3
"""
Automatisk säkerhetsgranskning för AZOM AI Agent.

Kör bandit och safety för att identifiera säkerhetsproblem i kodbas och beroenden.
Används i CI/CD-pipeline och som pre-commit hook.
"""
import os
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple


def run_bandit() -> Tuple[bool, str]:
    """
    Kör Bandit för statisk kodanalys av säkerhetsrisker.
    
    Returns:
        Tuple med (success, output_text)
    """
    print("Kör Bandit statisk säkerhetsanalys...")
    
    try:
        result = subprocess.run(
            ["bandit", "-r", "app", "-f", "json", "-c", "pyproject.toml"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.returncode == 0:
            print("✅ Bandit-analys slutförd utan allvarliga problem.")
            return True, result.stdout
        else:
            try:
                # Försök tolka JSON-output för att visa mer detaljerad information
                data = json.loads(result.stdout)
                issues = data.get("results", [])
                
                if issues:
                    print(f"❌ Bandit hittade {len(issues)} potentiella säkerhetsproblem:")
                    for i, issue in enumerate(issues, 1):
                        print(f"  Problem {i}: {issue.get('issue_text')} i {issue.get('filename')}:{issue.get('line_number')}")
                else:
                    print("❌ Bandit misslyckades men hittade inga specifika problem.")
            except json.JSONDecodeError:
                print(f"❌ Bandit misslyckades: {result.stderr}")
                
            return False, result.stdout
    except FileNotFoundError:
        print("❌ Bandit är inte installerat. Installera med 'pip install bandit'.")
        return False, "Bandit not installed"


def run_safety() -> Tuple[bool, str]:
    """
    Kör Safety för att identifiera sårbarheter i beroenden.
    
    Returns:
        Tuple med (success, output_text)
    """
    print("Kontrollerar paketberoenden efter kända sårbarheter...")
    
    try:
        result = subprocess.run(
            ["safety", "check", "--full-report", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.returncode == 0:
            print("✅ Inga kända sårbarheter hittades i paketen.")
            return True, result.stdout
        else:
            try:
                # Försök tolka JSON för att visa vilka paket som har problem
                data = json.loads(result.stdout)
                vulnerabilities = data.get("vulnerabilities", [])
                
                if vulnerabilities:
                    print(f"❌ Hittade {len(vulnerabilities)} sårbarheter i beroenden:")
                    critical_count = 0
                    
                    for vuln in vulnerabilities:
                        severity = vuln.get("severity", "").upper()
                        package = vuln.get("package_name")
                        affected = vuln.get("vulnerable_spec")
                        advisory = vuln.get("advisory")
                        
                        if severity == "HIGH" or severity == "CRITICAL":
                            critical_count += 1
                            
                        print(f"  - {severity}: {package} {affected} - {advisory}")
                    
                    # Enligt kodstandarden ska allvarliga sårbarheter (CVSS ≥ 7) blockera
                    if critical_count > 0:
                        print(f"\n⛔ {critical_count} kritiska/höga sårbarheter blockerar bygget.")
                    
                    return critical_count == 0, result.stdout
                else:
                    print("❓ Safety returnerade fel men hittade inga sårbarheter.")
            except json.JSONDecodeError:
                print(f"❌ Safety-kontroll misslyckades: {result.stderr}")
                
            return False, result.stdout
    except FileNotFoundError:
        print("❌ Safety är inte installerat. Installera med 'pip install safety'.")
        return False, "Safety not installed"


def main() -> int:
    """
    Huvudfunktion som kör säkerhetsgranskningar och returnerar statuskod.
    
    Returns:
        0 om alla kontroller lyckades, annars en felkod
    """
    print("🔒 AZOM AI Agent säkerhetsgranskning")
    print("=" * 60)
    
    # Säkerställ att vi kör från projektroten
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    
    bandit_success, _ = run_bandit()
    safety_success, _ = run_safety()
    
    print("\n" + "=" * 60)
    
    if bandit_success and safety_success:
        print("✅ Alla säkerhetskontroller godkända!")
        return 0
    else:
        print("❌ Säkerhetskontroller misslyckades, se detaljer ovan.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
