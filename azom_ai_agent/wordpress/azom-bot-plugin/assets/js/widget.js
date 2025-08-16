(function(){
  if (typeof window === 'undefined') return;
  const cfg = window.AZOM_BOT_CONFIG || {};
  const BASE_URL = (cfg.baseUrl || 'http://localhost:8001').replace(/\/$/, '');
  const ENDPOINT_PATH = cfg.endpointPath || '/chat/azom';
  const API_TYPE = cfg.apiType || 'pipeline'; // 'pipeline' or 'core'
  const DEFAULT_MODE = cfg.defaultMode || 'light';
  const TITLE = cfg.title || 'AZOM Support';
  const WELCOME = cfg.welcome || 'Hej! Hur kan jag hjälpa dig idag?';
  const POSITION = cfg.position === 'left' ? 'left' : 'right';
  const COLOR = cfg.color || '#2563eb';
  const BUTTON_LABEL = cfg.buttonLabel || 'Chatta med AZOM';

  // Create root container if shortcode not present
  let root = document.getElementById('azom-bot-root');
  if (!root) {
    root = document.createElement('div');
    root.id = 'azom-bot-root';
    document.body.appendChild(root);
  }

  // Inject CSS variables
  root.style.setProperty('--azom-primary', COLOR);

  // Build UI
  const wrapper = document.createElement('div');
  wrapper.className = 'azom-bot-wrapper azom-pos-' + POSITION;

  const toggleBtn = document.createElement('button');
  toggleBtn.className = 'azom-bot-toggle';
  toggleBtn.setAttribute('aria-expanded', 'false');
  toggleBtn.textContent = BUTTON_LABEL;

  const panel = document.createElement('div');
  panel.className = 'azom-bot-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-hidden', 'true');

  const header = document.createElement('div');
  header.className = 'azom-bot-header';
  header.textContent = TITLE;

  const body = document.createElement('div');
  body.className = 'azom-bot-body';

  const welcomeMsg = document.createElement('div');
  welcomeMsg.className = 'azom-msg azom-bot';
  welcomeMsg.textContent = WELCOME;
  body.appendChild(welcomeMsg);

  const form = document.createElement('form');
  form.className = 'azom-bot-form';
  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = 'Skriv ett meddelande...';
  input.setAttribute('aria-label', 'Meddelande');
  const send = document.createElement('button');
  send.type = 'submit';
  send.textContent = 'Skicka';
  form.appendChild(input);
  form.appendChild(send);

  panel.appendChild(header);
  panel.appendChild(body);
  panel.appendChild(form);

  wrapper.appendChild(toggleBtn);
  wrapper.appendChild(panel);
  root.appendChild(wrapper);

  let open = false;
  function setOpen(v){
    open = v; 
    panel.setAttribute('aria-hidden', String(!open));
    toggleBtn.setAttribute('aria-expanded', String(open));
    if (open) {
      panel.classList.add('open');
      input.focus({preventScroll:true});
    } else {
      panel.classList.remove('open');
    }
  }

  toggleBtn.addEventListener('click', function(){ setOpen(!open); });

  function appendUser(msg){
    const el = document.createElement('div');
    el.className = 'azom-msg azom-user';
    el.textContent = msg;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }
  function appendBot(msg){
    const el = document.createElement('div');
    el.className = 'azom-msg azom-bot';
    el.textContent = msg;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }
  function appendError(msg){
    const el = document.createElement('div');
    el.className = 'azom-msg azom-error';
    el.textContent = msg;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }

  async function sendMessage(text){
    const url = BASE_URL + ENDPOINT_PATH;
    const payload = API_TYPE === 'core' ? { prompt: text } : { message: text };
    const headers = { 'Content-Type': 'application/json', 'X-AZOM-Mode': DEFAULT_MODE };
    try {
      const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(payload) });
      if (!res.ok) {
        const info = await safeJson(res);
        throw new Error((info && (info.detail || info.error)) || ('HTTP ' + res.status));
      }
      const data = await res.json();
      // Core API returns {response}; Pipeline may return {response} or {message}
      const reply = data.response || data.message || 'Inget svar';
      appendBot(reply);
    } catch (e) {
      appendError('Fel: ' + (e && e.message ? e.message : 'Okänt fel'));
    }
  }

  async function safeJson(res){
    try { return await res.json(); } catch { return null; }
  }

  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    const text = (input.value || '').trim();
    if (!text) return;
    appendUser(text);
    input.value = '';
    sendMessage(text);
  });
})();
