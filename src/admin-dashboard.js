document.addEventListener('DOMContentLoaded', function() {
    fetch('/profile')
        .then(response => response.json())
        .then(data => {
            if (data.role === 'admin') {
                const adminDashboardLink = document.getElementById('admin-dashboard-link');
                if (adminDashboardLink) {
                    adminDashboardLink.style.display = 'block';
                }
            }
        })
        .catch(error => console.error('Error fetching user profile:', error));
});

let userRoleChart, docTypesChart;

function initCharts() {
    const userRoleCtx = document.getElementById('user-role-chart')?.getContext('2d');
    const docTypesCtx = document.getElementById('doc-types-chart')?.getContext('2d');

    if (userRoleCtx) {
        userRoleChart = new Chart(userRoleCtx, {
            type: 'doughnut',
            data: { labels: [], datasets: [{ data: [], backgroundColor: ['#00ffff', '#00cccc', '#00aaaa'] }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } } }
        });
    }

    if (docTypesCtx) {
        docTypesChart = new Chart(docTypesCtx, {
            type: 'bar',
            data: { labels: [], datasets: [{ label: 'Count', data: [], backgroundColor: '#00ffff' }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }
}

function updateDashboard(data) {
    document.getElementById('total-users').textContent = data.total_users;
    document.getElementById('admin-count').textContent = data.admin_count;
    document.getElementById('user-count').textContent = data.user_count;
    document.getElementById('docs-processed').textContent = data.docs_processed;

    if (userRoleChart) {
        userRoleChart.data.labels = Object.keys(data.user_roles);
        userRoleChart.data.datasets[0].data = Object.values(data.user_roles);
        userRoleChart.update();
    }

    if (docTypesChart) {
        docTypesChart.data.labels = Object.keys(data.doc_types);
        docTypesChart.data.datasets[0].data = Object.values(data.doc_types);
        docTypesChart.update();
    }
}

function loadDashboardData() {
    fetch('/api/dashboard_data')
        .then(res => res.json())
        .then(data => {
            updateDashboard(data);
        })
        .catch(error => console.error('Error loading dashboard data:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    loadDashboardData(); 
});