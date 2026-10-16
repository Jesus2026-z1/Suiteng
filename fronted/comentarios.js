// Configuración
const API_URL = 'http://localhost:5000/api';
let currentOffset = 0;
const LIMIT = 10;

// ============================================================
// INICIALIZACIÓN
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // Cargar comentarios
    loadComments();
    
    // Cargar estadísticas
    loadStats();
    
    // Event listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Formulario de comentario
    document.getElementById('commentForm').addEventListener('submit', handleCommentSubmit);
    
    // Contador de caracteres
    const messageInput = document.getElementById('message');
    const charCount = document.querySelector('.char-count');
    
    messageInput.addEventListener('input', function() {
        charCount.textContent = `${this.value.length} / 2000 caracteres`;
    });
    
    // Cargar más comentarios
    document.getElementById('loadMore').addEventListener('click', function() {
        currentOffset += LIMIT;
        loadComments();
    });
    
    // Checkbox anónimo
    const anonymousCheckbox = document.getElementById('anonymous');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    
    anonymousCheckbox.addEventListener('change', function() {
        if (this.checked) {
            nameInput.required = false;
            emailInput.required = false;
            nameInput.disabled = true;
            emailInput.disabled = true;
        } else {
            nameInput.required = true;
            emailInput.required = true;
            nameInput.disabled = false;
            emailInput.disabled = false;
        }
    });
}

// ============================================================
// CARGA DE DATOS
// ============================================================

async function loadComments() {
    try {
        const response = await fetch(`${API_URL}/comments?limit=${LIMIT}&offset=${currentOffset}`);
        const data = await response.json();
        
        if (data.success) {
            renderComments(data.comments, currentOffset === 0);
            
            // Ocultar botón si no hay más comentarios
            const loadMoreBtn = document.getElementById('loadMore');
            if (data.comments.length < LIMIT) {
                loadMoreBtn.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error cargando comentarios:', error);
        document.getElementById('commentsList').innerHTML = `
            <div class="no-comments">
                <i class="fas fa-exclamation-circle"></i>
                Error al cargar comentarios
            </div>
        `;
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/comments/stats`);
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            document.getElementById('totalComments').textContent = stats.total;
            document.getElementById('avgRating').textContent = stats.average_rating.toFixed(1);
            
            // Renderizar estrellas
            const fullStars = Math.floor(stats.average_rating);
            const emptyStars = 5 - fullStars;
            document.getElementById('avgStars').textContent = 
                '★'.repeat(fullStars) + '☆'.repeat(emptyStars);
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

function renderComments(comments, clear = false) {
    const container = document.getElementById('commentsList');
    
    if (clear) {
        container.innerHTML = '';
    }
    
    if (comments.length === 0 && clear) {
        container.innerHTML = `
            <div class="no-comments">
                <i class="fas fa-comment-slash"></i>
                <p>Sé el primero en comentar</p>
            </div>
        `;
        return;
    }
    
    comments.forEach(comment => {
        const commentEl = createCommentElement(comment);
        container.appendChild(commentEl);
    });
}

function createCommentElement(comment) {
    const div = document.createElement('div');
    div.className = 'comment-item';
    
    const initials = getInitials(comment.author);
    const stars = '★'.repeat(comment.rating) + '☆'.repeat(5 - comment.rating);
    const date = formatDate(comment.date);
    
    div.innerHTML = `
        <div class="comment-header">
            <div class="comment-avatar">${initials}</div>
            <div class="comment-info">
                <span class="comment-name">${escapeHtml(comment.author)}</span>
                ${comment.title ? `<span class="comment-title">${escapeHtml(comment.title)}</span>` : ''}
                <div class="comment-rating">${stars}</div>
            </div>
            <span class="comment-date">${date}</span>
        </div>
        <div class="comment-text">${escapeHtml(comment.content)}</div>
    `;
    
    return div;
}

// ============================================================
// ENVÍO DE COMENTARIO
// ============================================================

async function handleCommentSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('.btn-submit');
    const formMessage = document.getElementById('formMessage');
    
    // Obtener rating
    const ratingInput = form.querySelector('input[name="rating"]:checked');
    if (!ratingInput) {
        showFormMessage('Por favor selecciona una calificación', 'error');
        return;
    }
    
    // Preparar datos
    const data = {
        rating: parseInt(ratingInput.value),
        name: form.querySelector('#name').value.trim(),
        email: form.querySelector('#email').value.trim(),
        title: form.querySelector('#title').value.trim(),
        message: form.querySelector('#message').value.trim(),
        anonymous: form.querySelector('#anonymous').checked
    };
    
    // Validar
    if (!data.message || data.message.length < 10) {
        showFormMessage('El comentario debe tener al menos 10 caracteres', 'error');
        return;
    }
    
    // Deshabilitar botón
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    
    try {
        const response = await fetch(`${API_URL}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showFormMessage('✅ Comentario enviado. Será publicado después de revisión.', 'success');
            form.reset();
            
            // Recargar estadísticas
            loadStats();
        } else {
            const errorMsg = result.errors ? result.errors.join(', ') : 'Error al enviar comentario';
            showFormMessage(`❌ ${errorMsg}`, 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showFormMessage('❌ Error de conexión. Intenta de nuevo.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> <span>Enviar Comentario</span>';
    }
}

function showFormMessage(message, type) {
    const formMessage = document.getElementById('formMessage');
    formMessage.textContent = message;
    formMessage.className = `form-message ${type}`;
    
    setTimeout(() => {
        formMessage.style.display = 'none';
    }, 5000);
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

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}