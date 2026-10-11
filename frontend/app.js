// 로컬 개발 환경 및 배포 환경 대응
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'https://your-render-backend-url.onrender.com'; // Render 백엔드 주소 입력

let currentConversationId = null;

document.addEventListener('DOMContentLoaded', () => {
  loadSummary();
  loadDataList();
  loadConversations();

  document.getElementById('chatForm').addEventListener('submit', handleChatSubmit);
  document.getElementById('addDataForm').addEventListener('submit', handleAddData);
  document.getElementById('newChatBtn').addEventListener('click', startNewChat);
});

// 1. 요약 정보 로드
async function loadSummary() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/summary`);
    const data = await res.json();
    document.getElementById('summaryPeriod').innerText = data.period;
    document.getElementById('summaryCount').innerText = `${data.count}개`;
    document.getElementById('summaryStats').innerText = `${data.metrics.average} / ${data.metrics.max}`;
    document.getElementById('summaryTrend').innerText = data.trend;
  } catch (err) {
    console.error('요약 정보 불러오기 실패:', err);
  }
}

// 2. AI 채팅 전송
async function handleChatSubmit(e) {
  e.preventDefault();
  const inputEl = document.getElementById('chatInput');
  const message = inputEl.value.trim();
  if (!message) return;

  appendMessage('user', message);
  inputEl.value = '';
  showLoading(true);

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: currentConversationId })
    });
    const data = await res.json();
    appendMessage('assistant', data.reply);
    currentConversationId = data.conversation_id;
    loadConversations();
  } catch (err) {
    appendMessage('assistant', '오류가 발생했습니다. 다시 시도해 주세요.');
  } finally {
    showLoading(false);
  }
}

function appendMessage(role, text) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.innerText = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function showLoading(isLoading) {
  const el = document.getElementById('loadingIndicator');
  if (isLoading) el.classList.remove('hidden');
  else el.classList.add('hidden');
}

// 3. 시계열 데이터 목록 및 CRUD
async function loadDataList() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data`);
    const items = await res.json();
    const tbody = document.getElementById('dataTableBody');
    tbody.innerHTML = '';
    items.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.date}</td>
        <td>${item.value}</td>
        <td>${item.memo}</td>
        <td><button class="del-btn" onclick="deleteData('${item.id}')">삭제</button></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('데이터 목록 불러오기 실패:', err);
  }
}

async function handleAddData(e) {
  e.preventDefault();
  const date = document.getElementById('inputDate').value;
  const value = parseFloat(document.getElementById('inputValue').value);
  const memo = document.getElementById('inputMemo').value;

  await fetch(`${API_BASE_URL}/api/data`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ date, value, memo })
  });

  document.getElementById('addDataForm').reset();
  loadDataList();
  loadSummary();
}

async function deleteData(id) {
  if (!confirm('이 데이터를 삭제하시겠습니까?')) return;
  await fetch(`${API_BASE_URL}/api/data/${id}`, { method: 'DELETE' });
  loadDataList();
  loadSummary();
}

// 4. 대화 기록 목록 및 불러오기
async function loadConversations() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations`);
    const list = await res.json();
    const ul = document.getElementById('conversationList');
    ul.innerHTML = '';
    list.forEach(c => {
      const li = document.createElement('li');
      li.innerText = c.title;
      li.onclick = () => loadSingleConversation(c.id);
      ul.appendChild(li);
    });
  } catch (err) {
    console.error('대화 목록 불러오기 실패:', err);
  }
}

async function loadSingleConversation(id) {
  currentConversationId = id;
  const res = await fetch(`${API_BASE_URL}/api/conversations/${id}`);
  const data = await res.json();
  const container = document.getElementById('chatMessages');
  container.innerHTML = '';
  data.messages.forEach(m => appendMessage(m.role, m.content));
}

function startNewChat() {
  currentConversationId = null;
  document.getElementById('chatMessages').innerHTML = '';
}