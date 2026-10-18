'use strict';

const API_BASE_URL = (window.APP_CONFIG?.API_BASE_URL ||
  (['localhost', '127.0.0.1'].includes(location.hostname) ? 'http://127.0.0.1:8000' : '')).replace(/\/$/, '');
let currentConversationId = null;
let busy = false;
let dataItems = [];
const el = id => document.getElementById(id);
const status = message => { el('status').textContent = message; };

async function request(route, options = {}) {
  if (!API_BASE_URL) throw new Error('API_BASE_URL 설정을 확인하세요.');
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 90000);
  try {
    const response = await fetch(API_BASE_URL + route, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
      signal: controller.signal
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(typeof data.detail === 'string' ? data.detail : '입력값과 서버 설정을 확인하세요.');
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('서버 응답이 지연됩니다. 잠시 후 다시 시도하세요.');
    throw error;
  } finally { clearTimeout(timeout); }
}

function appendMessage(role, text) {
  const message = document.createElement('div');
  message.className = 'msg ' + role;
  message.textContent = text;
  el('chatMessages').append(message);
  el('chatMessages').scrollTop = el('chatMessages').scrollHeight;
}

async function loadSummary() {
  const data = await request('/api/data/summary');
  el('summaryPeriod').textContent = data.period;
  el('summaryCount').textContent = data.count + '개';
  el('summaryStats').textContent = data.metrics.average + ' / ' + data.metrics.max;
  el('summaryTrend').textContent = data.trend;
}

async function loadDataList() {
  dataItems = await request('/api/data');
  const body = el('dataTableBody');
  body.replaceChildren();
  dataItems.forEach(item => {
    const row = document.createElement('tr');
    [item.date, item.value, item.memo].forEach(value => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.append(cell);
    });
    const cell = document.createElement('td');
    const button = document.createElement('button');
    button.textContent = '삭제';
    button.className = 'del-btn';
    button.onclick = async () => {
      if (!confirm('이 데이터를 삭제하시겠습니까?')) return;
      button.disabled = true;
      try {
        await request('/api/data/' + encodeURIComponent(item.id), { method: 'DELETE' });
        await refreshData();
        status('데이터가 삭제되었습니다.');
      } catch (error) { status(error.message); }
      finally { button.disabled = false; }
    };
    cell.append(button);
    row.append(cell);
    body.append(row);
  });
  renderChart(dataItems);
}

async function refreshData() { await Promise.all([loadSummary(), loadDataList()]); }

async function loadConversations() {
  const items = await request('/api/conversations');
  el('conversationList').replaceChildren();
  items.forEach(item => {
    const li = document.createElement('li');
    const button = document.createElement('button');
    button.textContent = item.title;
    button.onclick = async () => {
      if (busy) return;
      setBusy(true);
      try {
        const data = await request('/api/conversations/' + encodeURIComponent(item.id));
        currentConversationId = item.id;
        el('chatMessages').replaceChildren();
        data.messages.forEach(message => appendMessage(message.role, message.content));
        status('대화를 불러왔습니다.');
      } catch (error) { status(error.message); }
      finally { setBusy(false); }
    };
    li.append(button);
    el('conversationList').append(li);
  });
}

function setBusy(value) {
  busy = value;
  el('chatForm').querySelector('button').disabled = value;
  el('chatInput').disabled = value;
  el('newChatBtn').disabled = value;
}

function renderChart(items) {
  const svg = el('timeSeriesChart');
  svg.replaceChildren();
  if (!items.length) return;
  const values = items.map(item => item.value);
  const low = Math.min(...values);
  const span = Math.max(...values) - low || 1;
  const points = values.map((value, i) =>
    (20 + i * 760 / Math.max(1, values.length - 1)) + ',' + (180 - (value - low) * 150 / span)
  ).join(' ');
  const line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
  line.setAttribute('points', points);
  line.setAttribute('fill', 'none');
  line.setAttribute('stroke', '#2563eb');
  line.setAttribute('stroke-width', '3');
  svg.append(line);
  const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  label.setAttribute('x', '20');
  label.setAttribute('y', '210');
  label.textContent = items[0].date + ' ~ ' + items[items.length - 1].date + ' | 최소 ' + low + ' / 최대 ' + Math.max(...values) + ' 시간';
  svg.append(label);
}

el('chatForm').addEventListener('submit', async event => {
  event.preventDefault();
  const message = el('chatInput').value.trim();
  if (!message || busy) return;
  setBusy(true);
  el('loadingIndicator').classList.remove('hidden');
  try {
    const data = await request('/api/chat', {
      method: 'POST', body: JSON.stringify({ message, conversation_id: currentConversationId })
    });
    appendMessage('user', message);
    appendMessage('assistant', data.reply);
    el('chatInput').value = '';
    currentConversationId = data.conversation_id;
    status('답변과 대화가 저장되었습니다.');
    await loadConversations();
  } catch (error) { status(error.message); }
  finally {
    setBusy(false);
    el('loadingIndicator').classList.add('hidden');
  }
});

el('addDataForm').addEventListener('submit', async event => {
  event.preventDefault();
  const button = event.currentTarget.querySelector('button');
  button.disabled = true;
  try {
    await request('/api/data', { method: 'POST', body: JSON.stringify({
      date: el('inputDate').value, value: Number(el('inputValue').value), memo: el('inputMemo').value
    }) });
    el('addDataForm').reset();
    await refreshData();
    status('데이터가 저장되었습니다.');
  } catch (error) { status(error.message); }
  finally { button.disabled = false; }
});

el('newChatBtn').onclick = () => {
  if (busy) return;
  currentConversationId = null;
  el('chatMessages').replaceChildren();
  status('새 대화를 시작합니다.');
};
el('darkModeToggle').onclick = () => {
  const dark = document.body.classList.toggle('dark-theme');
  el('darkModeToggle').setAttribute('aria-pressed', String(dark));
};
el('exportCsvBtn').onclick = () => {
  // Quote delimiters and prevent spreadsheet formulas in exported text.
  const quote = value => '"' + String(value).replace(/^[=+@-]/, "'$&").replaceAll('"', '""') + '"';
  const lines = [['ID', 'Date', 'Value', 'Memo'], ...dataItems.map(item =>
    [item.id, item.date, item.value, item.memo])];
  const csv = '\uFEFF' + lines.map(row => row.map(quote).join(',')).join('\r\n');
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'learning_data.csv';
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

Promise.all([refreshData(), loadConversations()])
  .then(() => status('연결되었습니다. 데이터 단위: 학습 시간'))
  .catch(error => status(error.message));
