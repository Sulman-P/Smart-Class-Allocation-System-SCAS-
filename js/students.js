// Students management logic

let currentPage = 1;
let pageSize = 20;
let totalPages = 1;
let totalStudents = 0;

async function initStudents() {
    await loadStudents();
    setupEventListeners();
}

async function loadStudents() {
    const body = document.getElementById('studentsTableBody');
    const spinner = document.getElementById('loadingSpinner');
    const search = document.getElementById('searchInput')?.value || '';
    const gender = document.getElementById('genderFilter')?.value || '';
    const boarding = document.getElementById('boardingFilter')?.value || '';
    const sort = document.getElementById('sortSelect')?.value || 'weighted_average:desc';
    
    // Show spinner
    body.innerHTML = '';
    spinner.classList.remove('hidden');
    
    try {
        // Build query params
        const params = new URLSearchParams({
            page: currentPage,
            limit: pageSize,
            search,
            ...(gender && { gender }),
            ...(boarding && { boarding_status: boarding }),
            sort_by: sort.split(':')[0],
            sort_order: sort.split(':')[1] || 'desc'
        });
        
        const response = await API.get(`/students?${params}`);
        
        spinner.classList.add('hidden');
        
        if (response.success && response.students) {
            totalStudents = response.pagination?.total || 0;
            totalPages = response.pagination?.pages || 1;
            
            renderStudents(response.students);
            updatePagination();
        } else {
            throw new Error('Failed to load students');
        }
    } catch (error) {
        spinner.classList.add('hidden');
        console.error('Load students error:', error);
        body.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-8 text-center text-slate-500">
                    <i class="fas fa-exclamation-circle text-2xl mb-2"></i>
                    <p>Failed to load students</p>
                    <button onclick="initStudents()" class="mt-2 text-indigo-600 hover:text-indigo-700">
                        <i class="fas fa-sync-alt mr-1"></i> Retry
                    </button>
                </td>
            </tr>
        `;
        showToast('Failed to load students', 'error');
    }
}

function renderStudents(students) {
    const body = document.getElementById('studentsTableBody');
    
    if (!students || students.length === 0) {
        body.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-8 text-center text-slate-500">
                    <i class="fas fa-inbox text-3xl mb-2"></i>
                    <p>No students found</p>
                    <p class="text-sm mt-1">Upload student data to get started</p>
                </td>
            </tr>
        `;
        return;
    }
    
    body.innerHTML = students.map(student => {
        const genderBadge = student.gender === 'Male' 
            ? 'bg-blue-100 text-blue-700' 
            : 'bg-pink-100 text-pink-700';
        
        const statusBadge = student.boarding_status === 'Boarder'
            ? 'bg-cyan-100 text-cyan-700'
            : 'bg-amber-100 text-amber-700';
        
        const avgColor = student.weighted_average >= 80 ? 'text-green-600' :
                        student.weighted_average >= 60 ? 'text-yellow-600' :
                        'text-red-600';
        
        return `
            <tr class="hover:bg-slate-50 transition">
                <td class="px-6 py-3 text-sm font-mono text-slate-600">
                    ${student.admission_no}
                </td>
                <td class="px-6 py-3 text-sm font-medium text-slate-800">
                    ${student.full_name}
                </td>
                <td class="px-6 py-3 text-sm">
                    <span class="inline-flex px-2 py-1 rounded-full text-xs font-medium ${genderBadge}">
                        ${student.gender}
                    </span>
                </td>
                <td class="px-6 py-3 text-sm">
                    <span class="inline-flex px-2 py-1 rounded-full text-xs font-medium ${statusBadge}">
                        ${student.boarding_status}
                    </span>
                </td>
                <td class="px-6 py-3 text-sm text-slate-600 text-center">
                    ${student.exam1 !== null ? student.exam1 : '-'}
                </td>
                <td class="px-6 py-3 text-sm text-slate-600 text-center">
                    ${student.exam2 !== null ? student.exam2 : '-'}
                </td>
                <td class="px-6 py-3 text-sm text-slate-600 text-center">
                    ${student.exam3 !== null ? student.exam3 : '-'}
                </td>
                <td class="px-6 py-3 text-sm font-semibold ${avgColor} text-center">
                    ${student.weighted_average !== null ? student.weighted_average.toFixed(2) : '-'}
                </td>
            </tr>
        `;
    }).join('');
}

function updatePagination() {
    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, totalStudents);
    
    document.getElementById('startRange').textContent = totalStudents > 0 ? start : 0;
    document.getElementById('endRange').textContent = end;
    document.getElementById('totalStudents').textContent = totalStudents;
    document.getElementById('pageInfo').textContent = `${currentPage} / ${totalPages || 1}`;
    
    document.getElementById('prevPage').disabled = currentPage <= 1;
    document.getElementById('nextPage').disabled = currentPage >= totalPages;
}

function setupEventListeners() {
    // Search with debounce
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
    searchInput?.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentPage = 1;
            loadStudents();
        }, 300);
    });
    
    // Filter changes
    document.getElementById('genderFilter')?.addEventListener('change', () => {
        currentPage = 1;
        loadStudents();
    });
    
    document.getElementById('boardingFilter')?.addEventListener('change', () => {
        currentPage = 1;
        loadStudents();
    });
    
    document.getElementById('sortSelect')?.addEventListener('change', () => {
        currentPage = 1;
        loadStudents();
    });
    
    // Pagination
    document.getElementById('pageSize')?.addEventListener('change', (e) => {
        pageSize = parseInt(e.target.value);
        currentPage = 1;
        loadStudents();
    });
    
    document.getElementById('prevPage')?.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadStudents();
        }
    });
    
    document.getElementById('nextPage')?.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            loadStudents();
        }
    });
}

// Make functions globally accessible
window.initStudents = initStudents;
window.loadStudents = loadStudents;
