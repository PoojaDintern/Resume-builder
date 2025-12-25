// script.js

// JSON Data
const statesData = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chandigarh",
    "CH": "Chhattisgarh",
    "DN": "Dadra and Nagar Haveli",
    "DD": "Daman and Diu",
    "DL": "Delhi",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JK": "Jammu and Kashmir",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OR": "Odisha",
    "PY": "Puducherry",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal"
};

const statePincodes = {
    "Andhra Pradesh": "500001",
    "Arunachal Pradesh": "791111",
    "Assam": "781001",
    "Bihar": "800001",
    "Chhattisgarh": "492001",
    "Goa": "403001",
    "Gujarat": "380001",
    "Haryana": "122001",
    "Himachal Pradesh": "171001",
    "Jharkhand": "834001",
    "Karnataka": "560001",
    "Kerala": "695001",
    "Madhya Pradesh": "462001",
    "Maharashtra": "400001",
    "Manipur": "795001",
    "Meghalaya": "793001",
    "Mizoram": "796001",
    "Nagaland": "797001",
    "Odisha": "751001",
    "Punjab": "160001",
    "Rajasthan": "302001",
    "Sikkim": "737101",
    "Tamil Nadu": "600001",
    "Telangana": "500001",
    "Tripura": "799001",
    "Uttar Pradesh": "226001",
    "Uttarakhand": "248001",
    "West Bengal": "700001"
};

const bangaloreAreasData = {
    "city": "Bangalore",
    "state": "Karnataka",
    "areas": [
        "Whitefield", "Koramangala", "Indiranagar", "Jayanagar", "Malleshwaram",
        "BTM Layout", "Electronic City", "Hebbal", "JP Nagar", "Marathahalli",
        "MG Road", "Banashankari", "Rajajinagar", "HSR Layout", "Yelahanka",
        "Bellandur", "Sarjapur Road", "KR Puram", "Basavanagudi", "Vijayanagar",
        "Ulsoor", "Domlur", "Nagawara", "RT Nagar", "Kengeri", "Mysore Road",
        "Peenya", "Yeshwanthpur", "Sanjay Nagar", "Frazer Town", "Cooke Town",
        "Richmond Town", "Shivajinagar", "Majestic", "Chandapura", "Hoskote",
        "Bannerghatta Road", "Kanakapura Road", "Thanisandra", "Hennur",
        "Horamavu", "Kadugodi", "Varthur", "Devanahalli", "Airport Road"
    ]
};

const languagesData = [
    { "label": "Assamese", "value": "Assamese" },
    { "label": "Bengali", "value": "Bengali" },
    { "label": "English", "value": "English" },
    { "label": "Gujarati", "value": "Gujarati" },
    { "label": "Hindi", "value": "Hindi" },
    { "label": "Kannada", "value": "Kannada" },
    { "label": "Konkani", "value": "Konkani" },
    { "label": "Malayalam", "value": "Malayalam" },
    { "label": "Manipuri", "value": "Manipuri" },
    { "label": "Marathi", "value": "Marathi" },
    { "label": "Mizo", "value": "Mizo" },
    { "label": "Odia", "value": "Odia" },
    { "label": "Punjabi", "value": "Punjabi" },
    { "label": "Tamil", "value": "Tamil" },
    { "label": "Telugu", "value": "Telugu" }
];

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

// Global variable to store the form data
let savedFormData = null;

$(document).ready(function() {
    // Populate States dropdown
    const stateSelect = $('#state');
    Object.entries(statesData).sort((a, b) => a[1].localeCompare(b[1])).forEach(([code, name]) => {
        stateSelect.append(new Option(name, name.toLowerCase().replace(/\s+/g, '_')));
    });

    // Populate Bangalore Areas
    const bangaloreAreasSelect = $('#bangaloreAreas');
    bangaloreAreasData.areas.forEach(area => {
        bangaloreAreasSelect.append(new Option(area, area.toLowerCase().replace(/\s+/g, '_')));
    });

    // Populate Languages
    const languageSelect = $('#language');
    languagesData.forEach(lang => {
        languageSelect.append(new Option(lang.label, lang.value));
    });

    // Populate Preferred Cities (all unique cities from stateCityMap)
    const multiCitySelect = $('#multiCity');
    const allCities = [...new Set(Object.values(stateCityMap).flat())].sort();
    allCities.forEach(city => {
        multiCitySelect.append(new Option(city, city.toLowerCase().replace(/\s+/g, '_')));
    });

    // Populate Service Pincodes
    const multiPincodeSelect = $('#multiPincode');
    Object.entries(statePincodes).sort((a, b) => a[0].localeCompare(b[0])).forEach(([state, pincode]) => {
        multiPincodeSelect.append(new Option(`${pincode} - ${state}`, pincode));
    });

    // Initialize Select2 for multi-select dropdowns
    $('#multiCity').select2({
        theme: 'bootstrap-5',
        placeholder: 'Select cities',
        allowClear: true,
        width: '100%'
    });

    $('#multiPincode').select2({
        theme: 'bootstrap-5',
        placeholder: 'Select pincodes',
        allowClear: true,
        width: '100%'
    });

    $('#language').select2({
        theme: 'bootstrap-5',
        placeholder: 'Select languages',
        allowClear: true,
        width: '100%'
    });

    $('#bangaloreAreas').select2({
        theme: 'bootstrap-5',
        placeholder: 'Select Bangalore areas',
        allowClear: true,
        width: '100%'
    });

    // State change handler - populate cities
    $('#state').on('change', function() {
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
            citySelect.append(new Option('Select State First', ''));
        }
    });

    // Set max date for DOB (must be at least 18 years old)
    const today = new Date();
    const maxDate = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
    const maxDateString = maxDate.toISOString().split('T')[0];
    document.getElementById('dob').setAttribute('max', maxDateString);

    // Set max date for onboarding date (today)
    const todayString = today.toISOString().split('T')[0];
    document.getElementById('onboardingDate').setAttribute('max', todayString);

    // Contact number validation - only numbers, max 10 digits
    const contactInput = document.getElementById('contact');
    
    contactInput.addEventListener('input', function(e) {
        let value = this.value.replace(/[^0-9]/g, '');
        if (value.length > 10) {
            value = value.slice(0, 10);
        }
        this.value = value;
    });

    contactInput.addEventListener('focus', function() {
        this.value = this.value.replace(/\s/g, '');
    });

    contactInput.addEventListener('blur', function() {
        let value = this.value.replace(/\s/g, '');
        if (value.length === 10) {
            this.value = value.replace(/(\d{5})(\d{5})/, '$1 $2');
        }
    });

    // Postal code validation - only numbers
    document.getElementById('postalCode').addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
        if (this.value.length > 6) {
            this.value = this.value.slice(0, 6);
        }
    });

    // Form validation
    const form = document.getElementById('registrationForm');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();

        const contactInput = document.getElementById('contact');
        const contactValue = contactInput.value.replace(/\s/g, '');
        contactInput.value = contactValue;

        const genderSelected = document.querySelector('input[name="gender"]:checked');
        const genderError = document.getElementById('genderError');
        
        if (!genderSelected) {
            genderError.textContent = 'Please select a gender.';
            genderError.style.display = 'block';
        } else {
            genderError.style.display = 'none';
        }

        if (form.checkValidity() && genderSelected) {
            const formData = {
                personalInformation: {
                    name: document.getElementById('name').value,
                    contact: contactValue,
                    dateOfBirth: document.getElementById('dob').value,
                    gender: genderSelected.value
                },
                addressInformation: {
                    addressLine1: document.getElementById('address1').value,
                    addressLine2: document.getElementById('address2').value || null,
                    state: document.getElementById('state').value,
                    city: document.getElementById('city').value,
                    postalCode: document.getElementById('postalCode').value,
                    bangaloreAreas: $('#bangaloreAreas').val() || []
                },
                additionalInformation: {
                    preferredCities: $('#multiCity').val() || [],
                    servicePincodes: $('#multiPincode').val() || [],
                    languagesKnown: $('#language').val() || []
                },
                accountInformation: {
                    status: document.getElementById('status').value,
                    onboardingDate: document.getElementById('onboardingDate').value,
                    type: document.getElementById('type').value
                },
                submittedAt: new Date().toISOString()
            };

            savedFormData = formData;

            console.log('Form Data (JSON Format):');
            console.log(JSON.stringify(formData, null, 2));
            
            displayFormSummary(formData);
            
            form.style.display = 'none';
            document.getElementById('formSummary').classList.add('show');
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        form.classList.add('was-validated');
    });

    form.addEventListener('reset', function() {
        form.classList.remove('was-validated');
        document.getElementById('genderError').style.display = 'none';
        $('.select2').val(null).trigger('change');
        
        // Reset city dropdown
        $('#city').empty().append(new Option('Select State First', '')).prop('disabled', true);
        
        form.style.display = 'block';
        document.getElementById('formSummary').classList.remove('show');
        
        savedFormData = null;
    });

    document.querySelectorAll('input[name="gender"]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            document.getElementById('genderError').style.display = 'none';
        });
    });

    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            this.style.borderColor = '#667eea';
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.style.borderColor = '#e0e0e0';
            }
        });
    });

    form.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
        }
    });

    $('.form-container').hide().fadeIn(600);

    form.addEventListener('submit', function() {
        setTimeout(() => {
            const firstError = document.querySelector('.is-invalid, .form-check-input:invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 100);
    });
});

// Display Form Summary Function
function displayFormSummary(data) {
    const summaryContent = document.getElementById('summaryContent');
    
    const formatArray = (arr) => {
        if (!arr || arr.length === 0) return '<span class="text-muted">Not specified</span>';
        return arr.map(item => `<span class="badge">${item}</span>`).join(' ');
    };
    
    const capitalize = (str) => {
        return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
    };
    
    const summaryHTML = `
        <div class="summary-section">
            <div class="summary-section-title">Personal Information</div>
            <div class="summary-row">
                <div class="summary-label">Full Name:</div>
                <div class="summary-value">${data.personalInformation.name}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Contact Number:</div>
                <div class="summary-value">${data.personalInformation.contact}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Date of Birth:</div>
                <div class="summary-value">${formatDate(data.personalInformation.dateOfBirth)}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Gender:</div>
                <div class="summary-value">${capitalize(data.personalInformation.gender)}</div>
            </div>
        </div>
        
        <div class="summary-section">
            <div class="summary-section-title">Address Information</div>
            <div class="summary-row">
                <div class="summary-label">Address Line 1:</div>
                <div class="summary-value">${data.addressInformation.addressLine1}</div>
            </div>
            ${data.addressInformation.addressLine2 ? `
            <div class="summary-row">
                <div class="summary-label">Address Line 2:</div>
                <div class="summary-value">${data.addressInformation.addressLine2}</div>
            </div>` : ''}
            <div class="summary-row">
                <div class="summary-label">State:</div>
                <div class="summary-value">${capitalize(data.addressInformation.state)}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">City:</div>
                <div class="summary-value">${capitalize(data.addressInformation.city)}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Postal Code:</div>
                <div class="summary-value">${data.addressInformation.postalCode}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Bangalore Areas:</div>
                <div class="summary-value">${formatArray(data.addressInformation.bangaloreAreas?.map(a => capitalize(a)))}</div>
            </div>
        </div>
        
        <div class="summary-section">
            <div class="summary-section-title">Additional Information</div>
            <div class="summary-row">
                <div class="summary-label">Preferred Cities:</div>
                <div class="summary-value">${formatArray(data.additionalInformation.preferredCities?.map(c => capitalize(c)))}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Service Pincodes:</div>
                <div class="summary-value">${formatArray(data.additionalInformation.servicePincodes)}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Languages Known:</div>
                <div class="summary-value">${formatArray(data.additionalInformation.languagesKnown)}</div>
            </div>
        </div>
        
        <div class="summary-section">
            <div class="summary-section-title">Account Information</div>
            <div class="summary-row">
                <div class="summary-label">Status:</div>
                <div class="summary-value">${capitalize(data.accountInformation.status)}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Onboarding Date:</div>
                <div class="summary-value">${formatDate(data.accountInformation.onboardingDate)}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Type:</div>
                <div class="summary-value">${capitalize(data.accountInformation.type)}</div>
            </div>
        </div>
    `;
    
    summaryContent.innerHTML = summaryHTML;
}

// Edit Form Function
function editForm() {
    document.getElementById('registrationForm').style.display = 'block';
    document.getElementById('formSummary').classList.remove('show');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Additional utility functions
function validateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    
    return age >= 18;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function isValidPhoneNumber(phone) {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone);
}

function isValidPostalCode(code) {
    const postalRegex = /^[0-9]{6}$/;
    return postalRegex.test(code);
}