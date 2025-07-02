from app.prompt_utils import inject_prompt_vars, compose_full_prompt

def test_inject_prompt_vars_basic():
    prompt = 'Hej {{USER_NAME}}, idag är det {{CURRENT_DATE}}.'
    result = inject_prompt_vars(prompt, {'USER_NAME': 'Anders'})
    assert 'Anders' in result and 'Hej' in result
    assert 'CURRENT_DATE' not in result  # Ska ha bytts ut

def test_inject_prompt_vars_unknown():
    result = inject_prompt_vars('Test {{UNKNOWN_VAR}}', {})
    assert '{{UNKNOWN_VAR}}' in result

def test_compose_full_prompt_basic():
    user_prompt = 'Vad rekommenderar du?'
    context = {'USER_NAME': 'Anna'}
    full = compose_full_prompt(user_prompt, context)
    assert user_prompt in full
    assert 'AZOM' in full  # Bör alltid innehålla systemprompten

def test_compose_full_prompt_safety():
    user_prompt = 'Är det risk?' 
    context = {'USER_NAME': 'Anna', 'safety_flag': True}
    full = compose_full_prompt(user_prompt, context)
    assert 'säkerhet' in full.lower() or 'restriktiv' in full.lower()
