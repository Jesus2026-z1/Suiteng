// Configuración
const API_URL = 'http://localhost:5000/api';
let currentDonationId = null;
let monthlyChart = null;

// ============================================================
// INICIALIZACIÓN
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // Cargar estadísticas mensuales
    loadMonthlyStats();
    
    // Cargar donantes recientes
    loadRecentDonors();
    
    // Event listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Cambio de método de pago
    document.querySelectorAll('input[name="paymentMethod"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const cryptoOptions = document.getElementById('cryptoOptions');
            if (this.value === 'crypto') {
                cryptoOptions.style.display = 'block';
            } else {
                cryptoOptions.style.display = 'none';
            }
        });
    });
    
    // Formulario de donativo
    document.getElementById('donationForm').addEventListener('submit', handleDonation);
    
    // Cerrar modal
    document.querySelector('.close-modal').addEventListener('click', function() {
        document.getElementById('cryptoModal').style.display = 'none';
    });
    
    // Cerrar modal al hacer click fuera
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('cryptoModal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// ============================================================
// CARGA DE DATOS
// ============================================================

async function loadMonthlyStats() {
    try {
        const response = await fetch(`${API_URL}/donations/monthly-stats`);
        const data = await response.json();
        
        if (data.success) {
            renderMonthlyChart(data.data, data.goal, data.total_raised);
            updateGoalProgress(data.total_raised, data.goal);
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

async function loadRecentDonors() {
    try {
        const response = await fetch(`${API_URL}/donations/recent?limit=10`);
        const data = await response.json();
        
        if (data.success) {
            renderRecentDonors(data.donations);
        }
    } catch (error) {
        console.error('Error cargando donantes:', error);
    }
}

function renderMonthlyChart(data, goal, totalRaised) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    // Preparar datos
    const labels = data.map(d => {
        const [year, month] = d.month.split('-');
        return `${month}/${year}`;
    });
    
    const amounts = data.map(d => d.total_usd);
    
    // Destruir gráfico anterior si existe
    if (monthlyChart) {
        monthlyChart.destroy();
    }
    
    // Crear nuevo gráfico
    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Donativos (USD)',
                data: amounts,
                backgroundColor: 'rgba(0, 102, 204, 0.6)',
                borderColor: 'rgba(0, 102, 204, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toLocaleString() + ' USD';
                        }
                    }
                }
            }
        }
    });
}

function updateGoalProgress(totalRaised, goal) {
    const progress = (totalRaised / goal) * 100;
    document.getElementById('progressText').textContent = 
        `Progreso: $${totalRaised.toLocaleString()} de $${goal.toLocaleString()} (${progress.toFixed(1)}%)`;
}

function renderRecentDonors(donations) {
    const container = document.getElementById('recentDonors');
    
    if (donations.length === 0) {
        container.innerHTML = '<p class="no-donors">Sé el primero en donar</p>';
        return;
    }
    
    container.innerHTML = donations.map(d => `
        <div class="donor-item">
            <div class="donor-avatar">${getInitials(d.donor)}</div>
            <div class="donor-info">
                <span class="donor-name">${d.donor}</span>
                <span class="donor-amount">$${d.amount_usd.toLocaleString()} USD</span>
                ${d.message ? `<p class="donor-message">"${d.message}"</p>` : ''}
            </div>
            <span class="donor-time">${formatDate(d.date)}</span>
        </div>
    `).join('');
}

// ============================================================
// MANEJO DE DONATIVOS
// ============================================================

async function handleDonation(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const paymentMethod = formData.get('paymentMethod');
    
    const donationData = {
        amount: parseFloat(formData.get('amount')),
        fiat_currency: formData.get('fiatCurrency'),
        name: formData.get('name'),
        email: formData.get('email'),
        anonymous: formData.get('anonymous') === 'on',
        message: formData.get('message')
    };
    
    if (paymentMethod === 'paypal') {
        await createPaypalDonation(donationData);
    } else {
        donationData.crypto = formData.get('crypto');
        await createCryptoDonation(donationData);
    }
}

async function createPaypalDonation(data) {
    try {
        const btn = document.querySelector('.btn-donate');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        
        const response = await fetch(`${API_URL}/donations/create-paypal`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Redirigir a PayPal
            window.location.href = result.approval_url;
        } else {
            alert('Error: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al procesar el donativo');
    } finally {
        const btn = document.querySelector('.btn-donate');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-heart"></i> <span>Donar Ahora</span>';
    }
}

async function createCryptoDonation(data) {
    try {
        const btn = document.querySelector('.btn-donate');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
        
        const response = await fetch(`${API_URL}/donations/create-crypto`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentDonationId = result.donation_id;
            showCryptoPaymentModal(result);
        } else {
            alert('Error: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al procesar el donativo');
    } finally {
        const btn = document.querySelector('.btn-donate');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-heart"></i> <span>Donar Ahora</span>';
    }
}

function showCryptoPaymentModal(data) {
    const modal = document.getElementById('cryptoModal');
    
    document.getElementById('cryptoAmount').textContent = data.crypto_amount;
    document.getElementById('cryptoSymbol').textContent = data.crypto;
    document.getElementById('network').textContent = data.network;
    document.getElementById('walletAddress').textContent = data.wallet_address;
    document.getElementById('qrCode').innerHTML = `<img src="${data.qr_code}" alt="QR Code">`;
    
    modal.style.display = 'block';
}

function copyAddress() {
    const address = document.getElementById('walletAddress').textContent;
    navigator.clipboard.writeText(address).then(() => {
        alert('Dirección copiada al portapapeles');
    });
}

async function verifyTransaction() {
    const txHash = document.getElementById('txHash').value.trim();
    const statusEl = document.getElementById('verificationStatus');
    
    if (!txHash) {
        statusEl.textContent = 'Ingresa el hash de transacción';
        statusEl.className = 'verification-status error';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/donations/verify-crypto/${currentDonationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tx_hash: txHash })
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusEl.textContent = `✅ Verificado! Confirmaciones: ${result.confirmations}`;
            statusEl.className = 'verification-status success';
            
            setTimeout(() => {
                document.getElementById('cryptoModal').style.display = 'none';
                loadRecentDonors();
                loadMonthlyStats();
            }, 2000);
        } else {
            statusEl.textContent = `⏳ ${result.error} (Confirmaciones: ${result.confirmations || 0})`;
            statusEl.className = 'verification-status warning';
        }
        
    } catch (error) {
        statusEl.textContent = 'Error al verificar';
        statusEl.className = 'verification-status error';
    }
}

// ============================================================
// UTILIDADES
// ============================================================

function getInitials(name) {
    if (!name || name === 'Anónimo') return 'A';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

function formatDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 60) return `Hace ${minutes} min`;
    if (hours < 24) return `Hace ${hours} horas`;
    if (days < 7) return `Hace ${days} días`;
    
    return date.toLocaleDateString('es-ES');
}