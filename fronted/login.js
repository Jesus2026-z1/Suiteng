const API_URL = 'https://tu-backend.railway.app/api';

document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const remember = document.querySelector('input[name="remember"]').checked;
    
    const submitBtn = this.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Iniciando sesión...';
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Guardar token
            if (remember) {
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('user_info', JSON.stringify(data.user));
            } else {
                sessionStorage.setItem('auth_token', data.token);
                sessionStorage.setItem('user_info', JSON.stringify(data.user));
            }
            
            showNotification('success', data.mensaje || 'Bienvenido!');
            
            // Construir URL con datos del usuario para Streamlit
            const streamlitUrl = 'http://localhost:8501';
            const params = new URLSearchParams({
                user: data.user.username,
                name: data.user.nombre_completo,
                email: data.user.email,
                rol: data.user.rol,
                token: data.token
            });
            
            // Redirigir a Streamlit con los datos
            setTimeout(() => {
                window.location.href = `${streamlitUrl}/?${params.toString()}`;
            }, 1000);
            
        } else {
            showNotification('error', data.error || 'Error al iniciar sesión');
            
            if (data.intentos_restantes !== undefined) {
                const intentosDiv = document.querySelector('.intentos-restantes');
                if (intentosDiv) {
                    intentosDiv.textContent = `Intentos restantes: ${data.intentos_restantes}`;
                }
            }
        }
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('error', 'Error de conexión. Verifica que el backend esté corriendo.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
});

// Función de notificaciones
function showNotification(type, message) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    `;
    
    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);