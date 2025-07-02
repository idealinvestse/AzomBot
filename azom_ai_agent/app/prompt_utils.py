import re
from datetime import datetime
from typing import Dict

def inject_prompt_vars(prompt: str, context: Dict[str, str]):
    now = datetime.now()
    default_vars = {
        'CURRENT_DATE': now.strftime('%Y-%m-%d'),
        'CURRENT_TIME': now.strftime('%H:%M'),
    }
    if context:
        default_vars.update(context)
    def replace_var(match):
        var = match.group(1)
        return str(default_vars.get(var, '{{' + var + '}}'))
    return re.sub(r'\{\{([A-Z0-9_]+)\}\}', replace_var, prompt)

def select_prompts(context: Dict[str, str]):
    paths = [
        'data/prompts/azom_iexpertpro_v3.md'
    ]
    if context.get('safety_flag'):
        paths.append('data/prompts/azom_safetyfilter_v1.md')
    if context.get('session_memory'):
        paths.append('data/prompts/azom_memoryinject_v1.md')
    return paths

def compose_full_prompt(user_prompt: str, context: Dict[str, str]):
    texts = []
    for path in select_prompts(context):
        try:
            with open(path, encoding='utf-8') as f:
                texts.append(inject_prompt_vars(f.read(), context))
        except FileNotFoundError:
            # Skip missing prompt file in test/dev environments
            continue
    
    # Fallback defaults if no prompt files were found
    if not texts:
        texts.append("AZOM Systemprompt: Du är en hjälpsam AI-assistent från AZOM.")
    if context.get('safety_flag') and not any('säkerhet' in t.lower() or 'restriktiv' in t.lower() for t in texts):
        texts.append("Säkerhetsfilter: Var restriktiv och fokusera på säkerhet.")
    return '\n\n'.join(texts) + '\n\n' + user_prompt
