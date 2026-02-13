let copyBtn, resultContainer, resultDesc, resultOnt, btnReboot;

document.addEventListener('DOMContentLoaded', () => {
  copyBtn = document.getElementById('copyBtn');
  resultContainer = document.getElementById('resultContainer');
  resultDesc = document.getElementById('resultDescription');
  resultOnt = document.getElementById('resultOnt');
  btnReboot = document.getElementById('btnReboot');
});

async function runReboot() {
  const form = document.getElementById('rebootForm');
  if (!form.reportValidity()) return;

  const serial = document.getElementById('serial').value.trim();
  const oltIp = document.getElementById('oltSelect').value;

  resultContainer.style.display = 'block';
  resultDesc.textContent = 'Отправка команды перезагрузки...';
  resultOnt.textContent = '';
  if (btnReboot) btnReboot.disabled = true;
  if (copyBtn) copyBtn.disabled = true;

  try {
    const resp = await fetch('/api/reboot_onu', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ serial, olt_ip: oltIp })
    });

    if (!resp.ok) {
      throw new Error('HTTP ' + resp.status);
    }

    const data = await resp.json(); // {ok: true/false, message: "..."}
    const ok = Boolean(data.ok);
    const msg = data.message || (ok ? 'Команда перезагрузки отправлена.' : 'Не удалось перезагрузить ONU.');

    resultOnt.textContent = ok ? 'OK' : 'ОШИБКА';
    resultOnt.className = ok ? 'status-ok' : 'status-fail';
    resultDesc.textContent = msg;

    if (copyBtn) copyBtn.disabled = false;
  } catch (e) {
    resultOnt.textContent = 'ОШИБКА';
    resultOnt.className = 'status-fail';
    resultDesc.textContent = 'Ошибка запроса: ' + e.message;
    if (copyBtn) copyBtn.disabled = true;
  } finally {
    if (btnReboot) btnReboot.disabled = false;
  }
}

function copyResult() {
  const text = `Статус: ${resultOnt.textContent}\n${resultDesc.textContent}`;
  navigator.clipboard.writeText(text).catch(console.error);
}
