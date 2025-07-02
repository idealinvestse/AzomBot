import os
import re
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

async def inject_prompt_vars(prompt: str, context: Dict[str, Any]) -> str:
    """
    Ersätter variabler i prompten med värden från context.
    
    Args:
        prompt: Prompttext med variabler på formen {{VAR_NAME}}
        context: Dictionary med variabelvärden
        
    Returns:
        Prompttext med ersätta variabler
    """
    now = datetime.now()
    default_vars: Dict[str, Union[str, int, float]] = {
        'CURRENT_DATE': now.strftime('%Y-%m-%d'),
        'CURRENT_TIME': now.strftime('%H:%M'),
    }
    if context:
        default_vars.update(context)
        
    def replace_var(match) -> str:
        var = match.group(1)
        return str(default_vars.get(var, '{{' + var + '}}'))
        
    return re.sub(r'\{\{([A-Z0-9_]+)\}\}', replace_var, prompt)

async def select_prompts(context: Dict[str, Any]) -> List[Path]:
    """
    Väljer lämpliga promptfiler baserat på context.
    
    Args:
        context: Dictionary med context-information
        
    Returns:
        Lista med Path-objekt till promptfiler
    """
    base_dir = Path('data/prompts')
    paths: List[Path] = [
        base_dir / 'azom_iexpertpro_v3.md'
    ]
    
    if context.get('safety_flag'):
        paths.append(base_dir / 'azom_safetyfilter_v1.md')
        
    if context.get('session_memory'):
        paths.append(base_dir / 'azom_memoryinject_v1.md')
        
    return paths

async def compose_full_prompt(user_prompt: str, context: Dict[str, Any]) -> str:
    """
    Sammanställer en komplett prompt med system- och användarprompt.
    
    Args:
        user_prompt: Användarens fråga eller direktiv
        context: Dictionary med context-information
        
    Returns:
        Komplett prompt för LLM
    """
    texts: List[str] = []
    prompt_paths = await select_prompts(context)
    
    for path in prompt_paths:
        try:
            # Asynkron filöppning för att minimera blockering av event-loop
            async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                texts.append(await inject_prompt_vars(content, context))
        except FileNotFoundError:
            # Skip missing prompt file in test/dev environments
            continue
    
    # Fallback defaults if no prompt files were found
    if not texts:
        texts.append("AZOM Systemprompt: Du är en hjälpsam AI-assistent från AZOM.")
        
    if context.get('safety_flag') and not any('säkerhet' in t.lower() or 'restriktiv' in t.lower() for t in texts):
        texts.append("Säkerhetsfilter: Var restriktiv och fokusera på säkerhet.")
        
    return '\n\n'.join(texts) + '\n\n' + user_prompt
