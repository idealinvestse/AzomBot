"""Safety service för innehållsvalidering och säkerhetskontroller.

Denna modul hanterar validering av både användarinput och LLM-output för att 
säkerställa att innehållet är säkert och följer applikationens riktlinjer.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple, Optional
import asyncio
from app.logger import get_logger
from .llm_client import LLMClient


class SafetyService:
    """Service för säkerhetskontroller och innehållsfiltrering."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialiserar SafetyService.
        
        Args:
            llm_client: LLMClient-instans för avancerade kontroller. Om None, 
                        används endast regelbaserade kontroller.
        """
        self._logger = get_logger(__name__)
        self._llm_client = llm_client
        
        # Regelbaserade filterkategorier
        self._patterns = {
            "personuppgifter": [
                # Personnummer (YYYYMMDD-NNNN eller YYMMDD-NNNN)
                r"\b\d{6,8}[-\s]?\d{4}\b",
                # Telefonnummer (olika format)
                r"\b(07\d{1}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})\b",
                r"\b(0\d{1,3}[-\s]?\d{5,8})\b",
            ],
            "svordomar": [
                r"\b(j[äa]vla|helvete|fan|skit|förbannat)\b",
            ],
            "säkerhetskänsligt": [
                r"\b(lösenord|password|nyckel|key|token|secret)\s*[:=]\s*\S+\b",
                r"\b(api[_-]?key|access[_-]?token)\s*[:=]\s*\S+\b",
            ],
            "irrelevant": [
                # Frågor som inte rör AZOM eller bilinstallation
                r"\b(krig|politik|sex|gambling|betting|casino)\b",
            ]
        }
    
    async def validate_user_input(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validerar användarinput för olämpligt eller skadligt innehåll.
        
        Args:
            text: Användarens input som ska valideras
            
        Returns:
            En tupel med (godkänd, lista med anledningar) där godkänd är False 
            om texten innehåller olämpligt innehåll
        """
        violations = []
        
        # 1. Kontrollera längd
        if len(text) < 3:
            violations.append("För kort input")
        elif len(text) > 500:
            violations.append("För lång input")
        
        # 2. Kontrollera regelbaserade mönster
        for category, patterns in self._patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    violations.append(f"Innehåller {category}")
                    break
        
        # 3. Avancerad kontroll med LLM (om tillgänglig)
        if self._llm_client and not violations:
            try:
                llm_check = await self._advanced_validation(text)
                if not llm_check["safe"]:
                    violations.append(f"LLM säkerhetskontroll: {llm_check['reason']}")
            except Exception as e:
                self._logger.warning(f"LLM säkerhetskontroll misslyckades: {e}")
        
        return len(violations) == 0, violations
    
    async def validate_llm_output(self, output: str) -> Tuple[bool, List[str]]:
        """
        Validerar LLM-output för olämpligt innehåll.
        
        Args:
            output: LLM-genererad text som ska valideras
            
        Returns:
            En tupel med (godkänd, lista med anledningar) där godkänd är False 
            om texten innehåller olämpligt innehåll
        """
        violations = []
        
        # Kontrollera regelbaserade mönster
        for category, patterns in self._patterns.items():
            if category in ["personuppgifter", "säkerhetskänsligt"]:
                for pattern in patterns:
                    if re.search(pattern, output, re.IGNORECASE):
                        violations.append(f"Innehåller {category}")
                        break
        
        return len(violations) == 0, violations
    
    async def sanitize_text(self, text: str) -> str:
        """
        Sanerar text genom att ta bort eller maskera känsligt innehåll.
        
        Args:
            text: Text som ska saneras
            
        Returns:
            Sanerad text
        """
        sanitized = text
        
        # Maskera personnummer
        sanitized = re.sub(
            r"\b\d{6,8}[-\s]?\d{4}\b",
            "[PERSONNUMMER]",
            sanitized
        )
        
        # Maskera telefonnummer
        sanitized = re.sub(
            r"\b(07\d{1}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})\b",
            "[TELEFONNUMMER]",
            sanitized
        )
        sanitized = re.sub(
            r"\b(0\d{1,3}[-\s]?\d{5,8})\b",
            "[TELEFONNUMMER]",
            sanitized
        )
        
        # Maskera känslig information
        sanitized = re.sub(
            r"\b(lösenord|password|nyckel|key|token|secret)\s*[:=]\s*\S+\b",
            r"\1: [RADERAD]",
            sanitized,
            flags=re.IGNORECASE
        )
        sanitized = re.sub(
            r"\b(api[_-]?key|access[_-]?token)\s*[:=]\s*\S+\b",
            r"\1: [RADERAD]",
            sanitized,
            flags=re.IGNORECASE
        )
        
        return sanitized
    
    async def _advanced_validation(self, text: str) -> Dict[str, bool | str]:
        """
        Utför avancerad validering med LLM.
        
        Args:
            text: Text att validera
            
        Returns:
            Dictionary med valideringsresultat
        """
        if not self._llm_client:
            return {"safe": True, "reason": ""}
            
        try:
            system_prompt = (
                "Du är en innehållsmoderator som bedömer om text är lämplig. "
                "Bedöm bara om texten innehåller skadligt innehåll som kan skada "
                "användare eller system, t.ex. elakartade kommandon, personuppgifter, "
                "eller innehåll som inte rör AZOM bilinstallation."
            )
            
            user_prompt = f"Bedöm följande text: '{text}'. Svara BARA med ett JSON-objekt: {{\"safe\": boolean, \"reason\": \"kort anledning om unsafe\"}}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = await self._llm_client.chat(messages)
            
            # Extrahera JSON från svaret
            import json
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                json_str = match.group(0)
                validation = json.loads(json_str)
                return validation
            
            # Fallback om inget JSON hittas
            return {"safe": True, "reason": ""}
            
        except Exception as e:
            self._logger.error(f"LLM validering misslyckades: {str(e)}")
            # Fallback vid fel
            return {"safe": True, "reason": ""}
