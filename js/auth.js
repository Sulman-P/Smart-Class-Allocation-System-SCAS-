// Authentication logic for login page

document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (Auth.isAuthenticated()) {
        window.location.href = '/dashboard.html';
        return;
    }
    
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const loginText = document.getElementById('loginText');
    const loginSpinner = document.getElementById('loginSpinner');
    const loginError = document.getElementById('loginError');
    const errorMessage = document.getElementById('errorMessage');
    
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        
        // Show loading state
        loginBtn.disabled = true;
        loginText.textContent = 'Signing in...';
        loginSpinner.classList.remove('hidden');
        loginError.classList.add('hidden');
        
        try {
            const response = await API.post('/auth/login', { email, password });
            
            if (response.success && response.token && response.user) {
                Auth.setSession(response.token, response.user);
                showToast('Welcome back, ' + response.user.fullname + '!', 'success');
                
                setTimeout(() => {
                    window.location.href = '/dashboard.html';
                }, 500);
            } else {
                throw new Error(response.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            
            let message = 'Login failed. Please check your credentials.';
            if (error.data && error.data.details) {
                message = error.data.details;
            } else if (error.data && error.data.error) {
                message = error.data.error;
            } else if (error.message) {
                message = error.message;
            }
            
            errorMessage.textContent = message;
            loginError.classList.remove('hidden');
            showToast(message, 'error');
        } finally {
            loginBtn.disabled = false;
            loginText.textContent = 'Sign In';
            loginSpinner.classList.add('hidden');
        }
    });
    
    // Demo credentials autofill
    const demoBtn = document.createElement('button');
    demoBtn.type = 'button';
    demoBtn.className = 'mt-4 text-sm text-indigo-600 hover:text-indigo-500 w-full';
    demoBtn.innerHTML = '<i class="fas fa-robot mr-1"></i> Autofill Demo Credentials';
    demoBtn.addEventListener('click', () => {
        document.getElementById('email').value = 'admin@nhs.edu';
        document.getElementById('password').value = 'password123';
        showToast('Demo credentials filled!', 'info');
    });
    loginForm.appendChild(demoBtn);
});
