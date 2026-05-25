let cpuChart;
let memoryChart;
let socket = io();

// Инициализация графиков
function initCharts() {
    const ctx = document.getElementById('cpuChart').getContext('2d');
    cpuChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'CPU Usage %',
                data: [],
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)'
            }]
        },
        options: {
            responsive: true,
            animation: false
        }
    });
    
    const memCtx = document.getElementById('memoryChart').getContext('2d');
    memoryChart = new Chart(memCtx, {
        type: 'doughnut',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#ff6b6b', '#4CAF50']
            }]
        }
    });
}

// Обновление данных через WebSocket
socket.on('cpu_update', (data) => {
    updateTemperatures(data.temperatures);
    updateFrequencies(data.frequencies);
    updateGovernor(data.governor);
    
    // Обновление графика CPU
    if (cpuChart.data.labels.length > 20) {
        cpuChart.data.labels.shift();
        cpuChart.data.datasets[0].data.shift();
    }
    cpuChart.data.labels.push(new Date().toLocaleTimeString());
    cpuChart.data.datasets[0].data.push(Math.max(...data.cpu_usage));
    cpuChart.update();
});

async function refreshData() {
    const response = await fetch('/api/current_stats');
    const data = await response.json();
    updateTemperatures(data.temperatures);
    updateFrequencies(data.frequencies);
    updateMemory(data.memory);
    updateGovernor(data.governor);
    
    // Обновление списка governor'ов
    const select = document.getElementById('governor-select');
    select.innerHTML = data.available_governors.map(g => 
        `<option value="${g}" ${g === data.governor ? 'selected' : ''}>${g}</option>`
    ).join('');
    
    loadStats();
}

function updateTemperatures(temps) {
    const div = document.getElementById('temperatures');
    div.innerHTML = Object.entries(temps).map(([name, temp]) => 
        `<div class="temp-item ${temp > 80 ? 'temp-high' : ''}">${name}: ${temp}°C</div>`
    ).join('');
}

function updateFrequencies(freqs) {
    const div = document.getElementById('frequencies');
    div.innerHTML = Object.entries(freqs).map(([cpu, freq]) => 
        `<div class="freq-item">${cpu}: ${freq} GHz</div>`
    ).join('');
}

function updateMemory(memory) {
    const div = document.getElementById('memory');
    div.innerHTML = `Всего: ${memory.total} GB<br>Использовано: ${memory.used} GB (${memory.percent}%)`;
    memoryChart.data.datasets[0].data = [memory.percent, 100 - memory.percent];
    memoryChart.update();
}

function updateGovernor(gov) {
    const select = document.getElementById('governor-select');
    if (select && !select.disabled) {
        select.value = gov;
    }
}

async function setGovernor() {
    const select = document.getElementById('governor-select');
    const governor = select.value;
    const response = await fetch('/api/set_governor', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({governor: governor})
    });
    const result = await response.json();
    if (result.success) {
        alert('Governor изменен успешно!');
    } else {
        alert('Ошибка: ' + result.error);
    }
}

async function loadStats() {
    const response = await fetch('/api/stats');
    const stats = await response.json();
    const div = document.getElementById('stats');
    div.innerHTML = `
        <p>🌡️ Максимальная температура: ${stats.max_temp || 0}°C</p>
        <p>❄️ Минимальная температура: ${stats.min_temp || 0}°C</p>
        <p>📊 Средняя температура: ${stats.avg_temp || 0}°C</p>
        <p>📝 Всего записей: ${stats.total_records || 0}</p>
    `;
}

// Запуск
initCharts();
refreshData();
setInterval(refreshData, 5000);
socket.emit('request_update');