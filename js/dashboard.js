// Dashboard logic

async function initDashboard() {
    try {
        await loadDashboardStats();
        await loadRecentActivity();
    } catch (error) {
        console.error('Dashboard init error:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

async function loadDashboardStats() {
    try {
        const response = await API.get('/upload/stats');
        
        if (response.success && response.stats) {
            const stats = response.stats;
            
            // Update stat cards
            document.getElementById('statsGrid').innerHTML = `
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm text-slate-500">Total Students</p>
                            <p class="text-3xl font-bold text-slate-800">${stats.total || 0}</p>
                        </div>
                        <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                            <i class="fas fa-users text-xl text-indigo-600"></i>
                        </div>
                    </div>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm text-slate-500">Male Students</p>
                            <p class="text-3xl font-bold text-slate-800">${stats.byGender?.male || 0}</p>
                        </div>
                        <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <i class="fas fa-mars text-xl text-blue-600"></i>
                        </div>
                    </div>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm text-slate-500">Female Students</p>
                            <p class="text-3xl font-bold text-slate-800">${stats.byGender?.female || 0}</p>
                        </div>
                        <div class="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
                            <i class="fas fa-venus text-xl text-pink-600"></i>
                        </div>
                    </div>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm text-slate-500">Boarders</p>
                            <p class="text-3xl font-bold text-slate-800">${stats.byBoardingStatus?.boarder || 0}</p>
                        </div>
                        <div class="w-12 h-12 bg-cyan-100 rounded-lg flex items-center justify-center">
                            <i class="fas fa-home text-xl text-cyan-600"></i>
                        </div>
                    </div>
                </div>
            `;
            
            // Update chart
            updateChart(stats);
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
        document.getElementById('statsGrid').innerHTML = `
            <div class="col-span-full text-center py-8 text-slate-500">
                <i class="fas fa-exclamation-circle text-2xl mb-2"></i>
                <p>Failed to load statistics</p>
            </div>
        `;
    }
}

function updateChart(stats) {
    const total = stats.total || 1;
    const maxHeight = 160;
    
    const maleHeight = ((stats.byGender?.male || 0) / total) * maxHeight;
    const femaleHeight = ((stats.byGender?.female || 0) / total) * maxHeight;
    const boarderHeight = ((stats.byBoardingStatus?.boarder || 0) / total) * maxHeight;
    const dayHeight = ((stats.byBoardingStatus?.day || 0) / total) * maxHeight;
    
    document.getElementById('maleBar').style.height = `${maleHeight}px`;
    document.getElementById('maleCount').textContent = stats.byGender?.male || 0;
    
    document.getElementById('femaleBar').style.height = `${femaleHeight}px`;
    document.getElementById('femaleCount').textContent = stats.byGender?.female || 0;
    
    document.getElementById('boarderBar').style.height = `${boarderHeight}px`;
    document.getElementById('boarderCount').textContent = stats.byBoardingStatus?.boarder || 0;
    
    document.getElementById('dayBar').style.height = `${dayHeight}px`;
    document.getElementById('dayCount').textContent = stats.byBoardingStatus?.day || 0;
}

async function loadRecentActivity() {
    const activityContainer = document.getElementById('recentActivity');
    
    try {
        // Fetch recent students (last 5)
        const response = await API.get('/students?page=1&limit=5&sort=created_at:desc');
        
        if (response.success && response.students && response.students.length > 0) {
            activityContainer.innerHTML = response.students.map(student => `
                <div class="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg">
                    <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                        <i class="fas fa-user-graduate text-sm text-indigo-600"></i>
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-slate-800 truncate">
                            ${student.full_name}
                        </p>
                        <p class="text-xs text-slate-500">
                            ${student.admission_no} • Added ${new Date(student.created_at).toLocaleDateString()}
                        </p>
                    </div>
                    <span class="text-xs px-2 py-1 rounded-full ${student.gender === 'Male' ? 'bg-blue-100 text-blue-700' : 'bg-pink-100 text-pink-700'}">
                        ${student.gender}
                    </span>
                </div>
            `).join('');
        } else {
            activityContainer.innerHTML = `
                <div class="text-center py-8 text-slate-500">
                    <i class="fas fa-inbox text-2xl mb-2"></i>
                    <p>No recent activity</p>
                    <p class="text-sm mt-1">Upload students to get started</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load activity:', error);
        activityContainer.innerHTML = `
            <div class="text-center py-8 text-slate-500">
                <i class="fas fa-exclamation-circle text-2xl mb-2"></i>
                <p>Failed to load activity</p>
            </div>
        `;
    }
}

// Make initDashboard globally accessible
window.initDashboard = initDashboard;
