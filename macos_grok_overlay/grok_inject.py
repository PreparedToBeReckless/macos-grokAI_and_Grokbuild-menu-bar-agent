import json


def build_submit_question_js(question):
    """Return JavaScript that fills Grok's chat input and submits a question."""
    question_literal = json.dumps(question)
    return f"""
(function(question) {{
  const q = (question || '').trim();
  if (!q) return {{ ok: false, reason: 'empty' }};

  function visible(el) {{
    if (!el) return false;
    const style = window.getComputedStyle(el);
    return style && style.visibility !== 'hidden' && style.display !== 'none';
  }}

  const candidates = [
    ...document.querySelectorAll('textarea'),
    ...document.querySelectorAll('[contenteditable="true"]'),
    ...document.querySelectorAll('[role="textbox"]'),
  ].filter(visible);

  const input = candidates.sort((a, b) => {{
    const ar = a.getBoundingClientRect();
    const br = b.getBoundingClientRect();
    return (br.bottom - ar.bottom) || (br.right - ar.right);
  }})[0];

  if (!input) return {{ ok: false, reason: 'no-input' }};

  if (input.tagName === 'TEXTAREA') {{
    const setter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype,
      'value'
    )?.set;
    if (setter) setter.call(input, q);
    else input.value = q;
    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
  }} else {{
    input.textContent = q;
    input.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: q }}));
  }}
  input.focus();

  const buttons = [...document.querySelectorAll('button')].filter(visible);
  const submit = buttons.find((btn) => {{
    const label = (btn.getAttribute('aria-label') || btn.textContent || '').toLowerCase();
    return !btn.disabled && /send|submit|ask|arrow|enter/.test(label);
  }});

  if (submit) {{
    submit.click();
    return {{ ok: true, method: 'button' }};
  }}

  input.dispatchEvent(new KeyboardEvent('keydown', {{
    key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
  }}));
  input.dispatchEvent(new KeyboardEvent('keyup', {{
    key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
  }}));
  return {{ ok: true, method: 'enter' }};
}})({question_literal});
"""