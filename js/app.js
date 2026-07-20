// Smart Class Allocation - Core Application

const API_BASE_URL = window.location.origin.includes('localhost') 
    ? 'http://localhost:8787/api' 
    : 'https://smart-class-allocation-api.workers.dev/api';

// Global state
const AppState = {
    user: null,
    token: null,
    schoolId: null,
    currentPage: window.location.pathname,
    students: [],
    pagination: null,
    filters: {
        search: '',
        gender: '',
        boardingStatus: '',
        sort: 'weighted_average:desc',
        page: 1,
        limit: 20
    }
};

// Auth utilities
const Auth = {
    getToken() {
        return localStorage.getItem('auth_token') || null;
    },
    
    getUser() {
        try {
            const user = localStorage.getItem('user_data');
            return user ? JSON.parse(user) : null;
        } catch {
            return null;
        }
    },
    
    isAuthenticated() {
        return !!this.getToken() && !!this.getUser();
    },
    
    setSession(token, user) {
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user_data', JSON.stringify(user));
        AppState.token = token;
        AppState.user = user;
        AppState.schoolId = user.schoolId;
    },
    
    clearSession() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        AppState.token = null;
        AppState.user = null;
        AppState.schoolId = null;
    },
    
    getHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
            'X-School-Id': AppState.schoolId || ''
        };
    }
};

// API Client
const API = {
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            ...Auth.getHeaders(),
            ...options.headers
        };
        
        const config = {
            ...options,
            headers,
            credentials: 'include'
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw {
                    status: response.status,
                    statusText: response.statusText,
                    data
                };
            }
            
            return data;
        } catch (error) {
            if (error.status === 401) {
                Auth.clearSession();
                window.location.href = '/login.html';
            }
            throw error;
        }
    },
    
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    },
    
    put(endpoint, body) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    },
    
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },
    
    upload(endpoint, formData) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Authorization': Auth.getToken() ? `Bearer ${Auth.getToken()}` : '',
            'X-School-Id': AppState.schoolId || ''
        };
        
        return fetch(url, {
            method: 'POST',
            headers,
            body: formData
        }).then(res => res.json());
    }
};

// Toast notifications
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const iconMap = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${iconMap[type] || iconMap.info} mr-2"></i>
        ${message}
    `;
    
    document.body.appendChild(toast);
    
    // Trigger show animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });
    
    // Auto hide
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

// Navigation utilities
function navigateTo(path) {
    window.location.href = path;
}

function updateNavLinks() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Initialize app
async function initializeApp() {
    // Check authentication
    if (!Auth.isAuthenticated()) {
        // Allow login page access
        if (!window.location.pathname.includes('login.html')) {
            window.location.href = '/login.html';
        }
        return;
    }
    
    // Update user display
    const user = Auth.getUser();
    if (user) {
        const displayEl = document.getElementById('userDisplay');
        if (displayEl) {
            displayEl.textContent = `👤 ${user.fullname}`;
        }
        AppState.schoolId = user.schoolId;
    }
    
    // Setup logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            Auth.clearSession();
            showToast('Logged out successfully', 'info');
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 500);
        });
    }
    
    // Update nav links
    updateNavLinks();
    
    // Page-specific initialization
    const page = window.location.pathname;
    if (page.includes('dashboard.html') && typeof initDashboard === 'function') {
        await initDashboard();
    } else if (page.includes('students.html') && typeof initStudents === 'function') {
        await initStudents();
    } else if (page.includes('upload.html') && typeof initUpload === 'function') {
        await initUpload();
    }
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Export for other scripts
window.AppState = AppState;
window.Auth = Auth;
window.API = API;
window.showToast = showToast;
window.navigateTo = navigateTo;
