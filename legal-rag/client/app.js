const API_BASE_URL = 'http://localhost:8000/api/v1';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const queryInput = document.getElementById('queryInput');
const queryBtn = document.getElementById('queryBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsArea = document.getElementById('resultsArea');
const answerText = document.getElementById('answerText');
const citationsList = document.getElementById('citationsList');

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

queryBtn.addEventListener('click', handleQuery);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleQuery();
});

// Functions
async function handleFileUpload(file) {
    if (file.type !== 'application/pdf') {
        showStatus('Please upload a PDF file.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showStatus('Uploading and processing...', 'normal');

    try {
        const response = await fetch(`${API_BASE_URL}/ingest`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const data = await response.json();
        showStatus(`Ingestion started! Task ID: ${data.task_id}`, 'success');
    } catch (error) {
        console.error('Error:', error);
        showStatus('Upload failed. Please try again.', 'error');
    }
}

async function handleQuery() {
    const query = queryInput.value.trim();
    if (!query) return;

    // Reset UI
    resultsArea.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');
    queryBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) throw new Error('Query failed');

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to get answer. Please check the backend connection.');
    } finally {
        loadingIndicator.classList.add('hidden');
        queryBtn.disabled = false;
    }
}

function displayResults(data) {
    answerText.textContent = data.answer;
    citationsList.innerHTML = '';

    data.citations.forEach(citation => {
        const card = document.createElement('div');
        card.className = 'citation-card';
        card.innerHTML = `
            <div class="citation-header">
                <span>${citation.source}</span>
                <span>Page ${citation.page}</span>
            </div>
            <div class="citation-text">"${citation.chunk_text_snippet}"</div>
        `;
        citationsList.appendChild(card);
    });

    resultsArea.classList.remove('hidden');
}

function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = 'status-message ' + type;
}
