// User Data from JSON files
const userData = [
    {
        name: "pooja.D",
        status: "active",
        city: "vijayawada",
        type: "individual",
        onboardingDate: "2025-12-13",
        submittedAt: "2025-12-25"
    },
    {
        name: "Pooja.D",
        status: "active",
        city: "visakhapatnam",
        type: "individual",
        onboardingDate: "2025-12-14",
        submittedAt: "2025-12-25"
    }
];

// Calculate statistics
function calculateStats() {
    const total = userData.length;
    const agency = userData.filter(u => u.type === 'agency').length;
    const individual = userData.filter(u => u.type === 'individual').length;
    const subAgency = userData.filter(u => u.type === 'sub_agency').length;

    document.getElementById('totalUsers').textContent = total;
    document.getElementById('agencyCount').textContent = agency;
    document.getElementById('individualCount').textContent = individual;
    document.getElementById('subAgencyCount').textContent = subAgency;
}

// Populate table
function populateTable() {
    const tbody = document.getElementById('userTableBody');
    tbody.innerHTML = '';
    
    userData.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.name}</td>
            <td><span class="status-badge status-${user.status}">${user.status.charAt(0).toUpperCase() + user.status.slice(1)}</span></td>
            <td>${user.city.charAt(0).toUpperCase() + user.city.slice(1)}</td>
        `;
        tbody.appendChild(row);
    });
}

// City-wise data
function getCityData() {
    const cityCount = {};
    userData.forEach(user => {
        const city = user.city.charAt(0).toUpperCase() + user.city.slice(1);
        cityCount[city] = (cityCount[city] || 0) + 1;
    });
    return cityCount;
}

// City Chart
const cityData = getCityData();
const cityCtx = document.getElementById('cityChart').getContext('2d');
const cityChart = new Chart(cityCtx, {
    type: 'bar',
    data: {
        labels: Object.keys(cityData),
        datasets: [{
            label: 'Users',
            data: Object.values(cityData),
            backgroundColor: 'rgba(102, 126, 234, 0.8)',
            borderColor: 'rgba(102, 126, 234, 1)',
            borderWidth: 2,
            borderRadius: 8
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                },
                grid: {
                    color: 'rgba(0,0,0,0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});

// Registration dates chart
const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
const weeklyChart = new Chart(weeklyCtx, {
    type: 'line',
    data: {
        labels: ['Dec 13', 'Dec 14', 'Dec 25'],
        datasets: [{
            label: 'Onboarding Date',
            data: [1, 1, 0],
            borderColor: 'rgba(102, 126, 234, 1)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true,
            borderWidth: 3
        }, {
            label: 'Submitted Date',
            data: [0, 0, 2],
            borderColor: 'rgba(16, 185, 129, 1)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true,
            borderWidth: 3
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'top',
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                },
                grid: {
                    color: 'rgba(0,0,0,0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});

// Search/Filter Function
function filterTable() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toUpperCase();
    const table = document.getElementById('userTable');
    const tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        let txtValue = tr[i].textContent || tr[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            tr[i].style.display = '';
        } else {
            tr[i].style.display = 'none';
        }
    }
}

// Toggle Sidebar for Mobile
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}

// Initialize on page load
calculateStats();
populateTable();