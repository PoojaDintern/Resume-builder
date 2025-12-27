// User Data from JSON files - All registrations
const userData = [
    {
        name: "pooja.D",
        contact: "6361571272",
        dateOfBirth: "2007-12-14",
        gender: "female",
        addressLine1: "peenya",
        addressLine2: "rajgopalnagar",
        city: "vijayawada",
        state: "andhra_pradesh",
        postalCode: "560012",
        bangaloreAreas: ["indiranagar"],
        preferredCities: ["ahmedabad"],
        servicePincodes: ["800001"],
        languagesKnown: ["English"],
        type: "individual",
        status: "active",
        onboardingDate: "2025-12-13",
        submittedAt: "2025-12-25"
    },
    {
        name: "Pooja.D",
        contact: "6361571272",
        dateOfBirth: "2007-12-08",
        gender: "female",
        addressLine1: "peenya",
        addressLine2: "GKW layout",
        city: "visakhapatnam",
        state: "andhra_pradesh",
        postalCode: "560091",
        bangaloreAreas: ["malleshwaram"],
        preferredCities: ["aizawl"],
        servicePincodes: ["800001"],
        languagesKnown: ["English"],
        type: "individual",
        status: "active",
        onboardingDate: "2025-12-14",
        submittedAt: "2025-12-25"
    },
    {
        name: "Pooja.D",
        contact: "6361571272",
        dateOfBirth: "2006-01-25",
        gender: "female",
        addressLine1: "Peenya",
        addressLine2: "rajgopalanagara",
        city: "bangalore",
        state: "karnataka",
        postalCode: "560089",
        bangaloreAreas: ["koramangala", "malleshwaram"],
        preferredCities: ["bangalore", "hyderabad"],
        servicePincodes: ["560001"],
        languagesKnown: ["marathi", "tamil"],
        type: "individual",
        status: "active",
        onboardingDate: "2025-12-19",
        submittedAt: "2025-12-24"
    },
    {
        name: "sujatha",
        contact: "8765432345",
        dateOfBirth: "2007-12-16",
        gender: "female",
        addressLine1: "peenya",
        addressLine2: "gkw layout",
        city: "bangalore",
        state: "karnataka",
        postalCode: "560089",
        bangaloreAreas: ["peenya"],
        preferredCities: ["durg"],
        servicePincodes: ["800001"],
        languagesKnown: ["Hindi"],
        type: "sub_agency",
        status: "inactive",
        onboardingDate: "2025-12-07",
        submittedAt: "2025-12-26"
    },
    {
        name: "dasharathan",
        contact: "0987654324",
        dateOfBirth: "2007-12-04",
        gender: "female",
        addressLine1: "kormangala",
        addressLine2: "kbn layout",
        city: "shimla",
        state: "himachal_pradesh",
        postalCode: "987654",
        bangaloreAreas: ["malleshwaram"],
        preferredCities: ["agra"],
        servicePincodes: ["500001"],
        languagesKnown: ["English"],
        type: "individual",
        status: "active",
        onboardingDate: "2025-12-20",
        submittedAt: "2025-12-26"
    },
    {
        name: "dasharathan",
        contact: "0987654323",
        dateOfBirth: "2007-12-09",
        gender: "male",
        addressLine1: "peenya",
        addressLine2: "khb colony",
        city: "panaji",
        state: "goa",
        postalCode: "987654",
        bangaloreAreas: ["indiranagar"],
        preferredCities: ["amritsar"],
        servicePincodes: ["492001"],
        languagesKnown: ["Gujarati"],
        type: "sub_agency",
        status: "active",
        onboardingDate: "2025-12-12",
        submittedAt: "2025-12-26"
    },
    {
        name: "sujatha",
        contact: "0987654323",
        dateOfBirth: "2007-12-08",
        gender: "female",
        addressLine1: "kormangala",
        addressLine2: "kgh",
        city: "guwahati",
        state: "assam",
        postalCode: "876543",
        bangaloreAreas: [],
        preferredCities: [],
        servicePincodes: [],
        languagesKnown: [],
        type: "agency",
        status: "inactive",
        onboardingDate: "2025-12-18",
        submittedAt: "2025-12-26"
    },
    {
        name: "rithun",
        contact: "0987654324",
        dateOfBirth: "2007-12-16",
        gender: "male",
        addressLine1: "peenya",
        addressLine2: "kgns layout",
        city: "vijayawada",
        state: "andhra_pradesh",
        postalCode: "098765",
        bangaloreAreas: ["koramangala"],
        preferredCities: ["aizawl"],
        servicePincodes: ["800001"],
        languagesKnown: ["Bengali"],
        type: "individual",
        status: "inactive",
        onboardingDate: "2025-12-16",
        submittedAt: "2025-12-26"
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

// Capitalize function
function capitalize(str) {
    if (!str) return '';
    return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Populate table
function populateTable() {
    const tbody = document.getElementById('userTableBody');
    tbody.innerHTML = '';
    
    userData.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.name}</td>
            <td><span class="status-badge status-${user.status}">${capitalize(user.status)}</span></td>
            <td>${capitalize(user.city)}</td>
        `;
        tbody.appendChild(row);
    });
}

// City-wise data
function getCityData() {
    const cityCount = {};
    userData.forEach(user => {
        const city = capitalize(user.city);
        cityCount[city] = (cityCount[city] || 0) + 1;
    });
    return cityCount;
}

// Get registration timeline data
function getTimelineData() {
    const onboardingDates = {};
    const submittedDates = {};
    
    userData.forEach(user => {
        // Format dates to short format
        const onboardingDate = new Date(user.onboardingDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const submittedDate = new Date(user.submittedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        
        onboardingDates[onboardingDate] = (onboardingDates[onboardingDate] || 0) + 1;
        submittedDates[submittedDate] = (submittedDates[submittedDate] || 0) + 1;
    });
    
    // Get all unique dates and sort them
    const allDates = [...new Set([...Object.keys(onboardingDates), ...Object.keys(submittedDates)])];
    allDates.sort((a, b) => new Date(a + ', 2025') - new Date(b + ', 2025'));
    
    return {
        labels: allDates,
        onboardingData: allDates.map(date => onboardingDates[date] || 0),
        submittedData: allDates.map(date => submittedDates[date] || 0)
    };
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
const timelineData = getTimelineData();
const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
const weeklyChart = new Chart(weeklyCtx, {
    type: 'line',
    data: {
        labels: timelineData.labels,
        datasets: [{
            label: 'Onboarding Date',
            data: timelineData.onboardingData,
            borderColor: 'rgba(102, 126, 234, 1)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true,
            borderWidth: 3,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: 'rgba(102, 126, 234, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
        }, {
            label: 'Submitted Date',
            data: timelineData.submittedData,
            borderColor: 'rgba(16, 185, 129, 1)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true,
            borderWidth: 3,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: 'rgba(16, 185, 129, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 15,
                    font: {
                        size: 12,
                        weight: '600'
                    }
                }
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