// dashboard.js

let userData = [];
let cityChart, weeklyChart;

// Form data
const stateCityMap = {
    "andhra_pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore"],
    "arunachal_pradesh": ["Itanagar", "Naharlagun"],
    "assam": ["Guwahati", "Silchar", "Dibrugarh"],
    "bihar": ["Patna", "Gaya", "Bhagalpur"],
    "chhattisgarh": ["Raipur", "Bilaspur", "Durg"],
    "goa": ["Panaji", "Margao"],
    "gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "haryana": ["Gurgaon", "Faridabad", "Panipat"],
    "himachal_pradesh": ["Shimla", "Dharamshala", "Solan"],
    "jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad"],
    "karnataka": ["Bangalore", "Mysore", "Mangalore", "Hubli"],
    "kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    "madhya_pradesh": ["Bhopal", "Indore", "Jabalpur"],
    "maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
    "manipur": ["Imphal"],
    "meghalaya": ["Shillong"],
    "mizoram": ["Aizawl"],
    "nagaland": ["Kohima", "Dimapur"],
    "odisha": ["Bhubaneswar", "Cuttack", "Rourkela"],
    "punjab": ["Chandigarh", "Ludhiana", "Amritsar"],
    "rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota"],
    "sikkim": ["Gangtok"],
    "tamil_nadu": ["Chennai", "Coimbatore", "Madurai", "Trichy"],
    "telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "tripura": ["Agartala"],
    "uttar_pradesh": ["Lucknow", "Kanpur", "Noida", "Agra"],
    "uttarakhand": ["Dehradun", "Haridwar"],
    "west_bengal": ["Kolkata", "Howrah", "Durgapur"]
};

const statesData = {
    "Andhra Pradesh": "andhra_pradesh",
    "Arunachal Pradesh": "arunachal_pradesh",
    "Assam": "assam",
    "Bihar": "bihar",
    "Chhattisgarh": "chhattisgarh",
    "Goa": "goa",
    "Gujarat": "gujarat",
    "Haryana": "haryana",
    "Himachal Pradesh": "himachal_pradesh",
    "Jharkhand": "jharkhand",
    "Karnataka": "karnataka",
    "Kerala": "kerala",
    "Madhya Pradesh": "madhya_pradesh",
    "Maharashtra": "maharashtra",
    "Manipur": "manipur",
    "Meghalaya": "meghalaya",
    "Mizoram": "mizoram",
    "Nagaland": "nagaland",
    "Odisha": "odisha",
    "Punjab": "punjab",
    "Rajasthan": "rajasthan",
    "Sikkim": "sikkim",
    "Tamil Nadu": "tamil_nadu",
    "Telangana": "telangana",
    "Tripura": "tripura",
    "Uttar Pradesh": "uttar_pradesh",
    "Uttarakhand": "uttarakhand",
    "West Bengal": "west_bengal"
};

const bangaloreAreasData = ["Whitefield", "Koramangala", "Indiranagar", "Jayanagar", "Malleshwaram", "BTM Layout", "Electronic City", "Hebbal", "JP Nagar", "Marathahalli", "MG Road", "Banashankari", "Rajajinagar", "HSR Layout", "Yelahanka", "Bellandur", "Sarjapur Road", "KR Puram", "Basavanagudi", "Vijayanagar", "Peenya"];

const languagesData = ["Assamese", "Bengali", "English", "Gujarati", "Hindi", "Kannada", "Konkani", "Malayalam", "Manipuri", "Marathi", "Mizo", "Odia", "Punjabi", "Tamil", "Telugu"];

const statePincodes = {
    "Andhra Pradesh": "500001",
    "Assam": "781001",
    "Bihar": "800001",
    "Chhattisgarh": "492001",
    "Goa": "403001",
    "Gujarat": "380001",
    "Haryana": "122001",
    "Himachal Pradesh": "171001",
    "Karnataka": "560001",
    "Kerala": "695001",
    "Maharashtra": "400001",
    "Tamil Nadu": "600001",
    "Telangana": "500001",
    "Uttar Pradesh": "226001",
    "West Bengal": "700001"
};

// Handle file upload
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    document.getElementById('fileName').textContent = `Selected: ${file.name}`;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            
            // Handle different JSON structures
            if (data.submissions && Array.isArray(data.submissions)) {
                // Format from registration form
                userData = data.submissions.map(s => convertSubmissionToUser(s));
            } else if (Array.isArray(data)) {
                // Direct array format
                userData = data;
            } else {
                userData = [data];
            }
            
            document.getElementById('uploadSection').classList.add('hidden');
            document.getElementById('dashboardSection').classList.remove('hidden');
            
            initializeDashboard();
        } catch (error) {
            alert('Error parsing JSON file. Please check the file format.');
            console.error(error);
        }
    };
    reader.readAsText(file);
}

// Convert registration submission format to user format
function convertSubmissionToUser(submission) {
    if (submission.personalInformation) {
        return {
            name: submission.personalInformation.name,
            contact: submission.personalInformation.contact,
            dateOfBirth: submission.personalInformation.dateOfBirth,
            gender: submission.personalInformation.gender,
            addressLine1: submission.addressInformation.addressLine1,
            addressLine2: submission.addressInformation.addressLine2,
            city: submission.addressInformation.city,
            state: submission.addressInformation.state,
            postalCode: submission.addressInformation.postalCode,
            bangaloreAreas: submission.addressInformation.bangaloreAreas || [],
            preferredCities: submission.additionalInformation.preferredCities || [],
            servicePincodes: submission.additionalInformation.servicePincodes || [],
            languagesKnown: submission.additionalInformation.languagesKnown || [],
            type: submission.accountInformation.type,
            status: submission.accountInformation.status,
            onboardingDate: submission.accountInformation.onboardingDate,
            submittedAt: submission.submittedAt
        };
    }
    return submission;
}

function initializeDashboard() {
    calculateStats();
    populateTable();
    createCityChart();
    createWeeklyChart();
}

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

function capitalize(str) {
    if (!str) return '';
    return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

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

function getCityData() {
    const cityCount = {};
    userData.forEach(user => {
        const city = capitalize(user.city);
        cityCount[city] = (cityCount[city] || 0) + 1;
    });
    return cityCount;
}

function getTimelineData() {
    const onboardingDates = {};
    const submittedDates = {};
    
    userData.forEach(user => {
        const onboardingDate = new Date(user.onboardingDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const submittedDate = new Date(user.submittedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        
        onboardingDates[onboardingDate] = (onboardingDates[onboardingDate] || 0) + 1;
        submittedDates[submittedDate] = (submittedDates[submittedDate] || 0) + 1;
    });
    
    const allDates = [...new Set([...Object.keys(onboardingDates), ...Object.keys(submittedDates)])];
    allDates.sort((a, b) => new Date(a + ', 2025') - new Date(b + ', 2025'));
    
    return {
        labels: allDates,
        onboardingData: allDates.map(date => onboardingDates[date] || 0),
        submittedData: allDates.map(date => submittedDates[date] || 0)
    };
}

function createCityChart() {
    if (cityChart) cityChart.destroy();
    
    const cityData = getCityData();
    const cityCtx = document.getElementById('cityChart').getContext('2d');
    cityChart = new Chart(cityCtx, {
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
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function createWeeklyChart() {
    if (weeklyChart) weeklyChart.destroy();
    
    const timelineData = getTimelineData();
    const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
    weeklyChart = new Chart(weeklyCtx, {
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
                    labels: { usePointStyle: true, padding: 15, font: { size: 12, weight: '600' } }
                }
            },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

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

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}

// Download updated JSON file
function downloadUpdatedJSON() {
    const jsonData = JSON.stringify(userData, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'updated_users_data.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Navigation handling
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            if (page === 'dashboard') {
                document.getElementById('uploadSection').classList.add('hidden');
                document.getElementById('registrationSection').classList.add('hidden');
                if (userData.length > 0) {
                    document.getElementById('dashboardSection').classList.remove('hidden');
                } else {
                    document.getElementById('uploadSection').classList.remove('hidden');
                }
            } else if (page === 'new-registration') {
                document.getElementById('uploadSection').classList.add('hidden');
                document.getElementById('dashboardSection').classList.add('hidden');
                document.getElementById('registrationSection').classList.remove('hidden');
                initializeRegistrationForm();
            } else if (page === 'users') {
                if (userData.length > 0) {
                    document.getElementById('uploadSection').classList.add('hidden');
                    document.getElementById('registrationSection').classList.add('hidden');
                    document.getElementById('dashboardSection').classList.remove('hidden');
                    setTimeout(() => {
                        document.getElementById('userTableSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                } else {
                    alert('Please upload a JSON file first to view users.');
                }
            }
        });
    });
});

// Initialize registration form
function initializeRegistrationForm() {
    // Populate States
    const stateSelect = $('#state');
    stateSelect.empty().append(new Option('Select State', ''));
    Object.entries(statesData).sort((a, b) => a[0].localeCompare(b[0])).forEach(([name, value]) => {
        stateSelect.append(new Option(name, value));
    });

    // Populate Bangalore Areas
    const bangaloreAreasSelect = $('#bangaloreAreas');
    bangaloreAreasSelect.empty();
    bangaloreAreasData.forEach(area => {
        bangaloreAreasSelect.append(new Option(area, area.toLowerCase().replace(/\s+/g, '_')));
    });

    // Populate Languages
    const languageSelect = $('#language');
    languageSelect.empty();
    languagesData.forEach(lang => {
        languageSelect.append(new Option(lang, lang));
    });

    // Populate Preferred Cities
    const multiCitySelect = $('#multiCity');
    multiCitySelect.empty();
    const allCities = [...new Set(Object.values(stateCityMap).flat())].sort();
    allCities.forEach(city => {
        multiCitySelect.append(new Option(city, city.toLowerCase().replace(/\s+/g, '_')));
    });

    // Populate Service Pincodes
    const multiPincodeSelect = $('#multiPincode');
    multiPincodeSelect.empty();
    Object.entries(statePincodes).sort((a, b) => a[0].localeCompare(b[0])).forEach(([state, pincode]) => {
        multiPincodeSelect.append(new Option(`${pincode} - ${state}`, pincode));
    });

    // Initialize Select2
    $('#multiCity, #multiPincode, #language, #bangaloreAreas').select2({
        theme: 'bootstrap-5',
        placeholder: 'Select options',
        allowClear: true,
        width: '100%'
    });

    // State change handler
    $('#state').off('change').on('change', function() {
        const selectedState = $(this).val();
        const citySelect = $('#city');
        
        citySelect.empty().append(new Option('Select City', ''));
        
        if (selectedState && stateCityMap[selectedState]) {
            citySelect.prop('disabled', false);
            stateCityMap[selectedState].forEach(city => {
                citySelect.append(new Option(city, city.toLowerCase().replace(/\s+/g, '_')));
            });
        } else {
            citySelect.prop('disabled', true);
        }
    });

    // Date constraints
    const today = new Date();
    const maxDate = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
    document.getElementById('dob').setAttribute('max', maxDate.toISOString().split('T')[0]);
    document.getElementById('onboardingDate').setAttribute('max', today.toISOString().split('T')[0]);

    // Form submission
    const form = document.getElementById('registrationForm');
    form.onsubmit = function(e) {
        e.preventDefault();
        
        const genderSelected = document.querySelector('input[name="gender"]:checked');
        if (!genderSelected) {
            document.getElementById('genderError').textContent = 'Please select a gender.';
            return;
        }

        if (form.checkValidity()) {
            const newUser = {
                name: document.getElementById('name').value,
                contact: document.getElementById('contact').value,
                dateOfBirth: document.getElementById('dob').value,
                gender: genderSelected.value,
                addressLine1: document.getElementById('address1').value,
                addressLine2: document.getElementById('address2').value,
                city: document.getElementById('city').value,
                state: document.getElementById('state').value,
                postalCode: document.getElementById('postalCode').value,
                bangaloreAreas: $('#bangaloreAreas').val() || [],
                preferredCities: $('#multiCity').val() || [],
                servicePincodes: $('#multiPincode').val() || [],
                languagesKnown: $('#language').val() || [],
                type: document.getElementById('type').value,
                status: document.getElementById('status').value,
                onboardingDate: document.getElementById('onboardingDate').value,
                submittedAt: new Date().toISOString()
            };

            // Add to userData array
            userData.push(newUser);
            
            // Download updated JSON file automatically
            downloadUpdatedJSON();
            
            // Show success message
            alert('Registration submitted successfully! Updated JSON file has been downloaded.');
            
            // Reset form
            form.reset();
            form.classList.remove('was-validated');
            $('.select2').val(null).trigger('change');
            
            // Switch to dashboard and update it
            document.querySelectorAll('.nav-link')[0].click();
            initializeDashboard();
        }
        form.classList.add('was-validated');
    };
}