// script.js

// Global variable to store the form data
let savedFormData = null;

$(document).ready(function() {
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

    // Initialize Select2 for Bangalore Areas
    $('#bangaloreAreas').select2({
        theme: 'bootstrap-5',
        placeholder: 'Select Bangalore areas',
        allowClear: true,
        width: '100%'
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
        // Remove all non-numeric characters
        let value = this.value.replace(/[^0-9]/g, '');
        
        // Limit to 10 digits
        if (value.length > 10) {
            value = value.slice(0, 10);
        }
        
        this.value = value;
    });

    // Remove formatting on focus for easier editing
    contactInput.addEventListener('focus', function() {
        this.value = this.value.replace(/\s/g, '');
    });

    // Add formatting on blur (optional visual enhancement)
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

        // Remove any spaces from contact number before validation
        const contactInput = document.getElementById('contact');
        const contactValue = contactInput.value.replace(/\s/g, '');
        contactInput.value = contactValue;

        // Custom gender validation
        const genderSelected = document.querySelector('input[name="gender"]:checked');
        const genderError = document.getElementById('genderError');
        
        if (!genderSelected) {
            genderError.textContent = 'Please select a gender.';
            genderError.style.display = 'block';
        } else {
            genderError.style.display = 'none';
        }

        // Check form validity
        if (form.checkValidity() && genderSelected) {
            // Collect form data in structured JSON format
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
                    city: document.getElementById('city').value,
                    state: document.getElementById('state').value,
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

            // Store the form data globally
            savedFormData = formData;

            // Log the JSON data to console
            console.log('Form Data (JSON Format):');
            console.log(JSON.stringify(formData, null, 2));
            
            // Display form summary
            displayFormSummary(formData);
            
            // Hide the form and show summary
            form.style.display = 'none';
            document.getElementById('formSummary').classList.add('show');
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        form.classList.add('was-validated');
    });

    // Reset form validation on reset
    form.addEventListener('reset', function() {
        form.classList.remove('was-validated');
        document.getElementById('genderError').style.display = 'none';
        $('.select2').val(null).trigger('change');
        
        // Show form and hide summary
        form.style.display = 'block';
        document.getElementById('formSummary').classList.remove('show');
        
        // Clear saved data
        savedFormData = null;
    });

    // Real-time validation for gender
    document.querySelectorAll('input[name="gender"]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            document.getElementById('genderError').style.display = 'none';
        });
    });

    // Add visual feedback for date inputs
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

    // Prevent form submission on Enter key (except in textarea)
    form.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
        }
    });

    // Dynamic state-city mapping (optional enhancement)
    const stateCityMap = {
        'maharashtra': ['mumbai', 'pune'],
        'delhi': ['delhi'],
        'karnataka': ['bangalore'],
        'telangana': ['hyderabad'],
        'tamil_nadu': ['chennai'],
        'west_bengal': ['kolkata'],
        'gujarat': ['ahmedabad']
    };

    document.getElementById('state').addEventListener('change', function() {
        const citySelect = document.getElementById('city');
        const selectedState = this.value;
        
        // This is a simple example - you can enhance this based on your needs
        // For now, it just provides visual feedback
        if (selectedState) {
            citySelect.style.borderColor = '#667eea';
            setTimeout(() => {
                citySelect.style.borderColor = '#e0e0e0';
            }, 500);
        }
    });

    // Add animation on form load
    $('.form-container').hide().fadeIn(600);

    // Smooth scroll to first error
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
    
    // Helper function to format arrays
    const formatArray = (arr) => {
        if (!arr || arr.length === 0) return '<span class="text-muted">Not specified</span>';
        return arr.map(item => `<span class="badge">${item}</span>`).join(' ');
    };
    
    // Helper function to capitalize
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
                <div class="summary-label">City:</div>
                <div class="summary-value">${capitalize(data.addressInformation.city)}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">State:</div>
                <div class="summary-value">${capitalize(data.addressInformation.state)}</div>
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
                <div class="summary-value">${formatArray(data.additionalInformation.languagesKnown?.map(l => capitalize(l)))}</div>
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
        <!--
        <div class="json-preview-section">
            <div class="summary-section-title">JSON Data Preview</div>
            <pre class="json-display">${JSON.stringify(data, null, 2)}</pre>
        </div>
         -->
    `;
    
    summaryContent.innerHTML = summaryHTML;
}

// Edit Form Function
function editForm() {
    document.getElementById('registrationForm').style.display = 'block';
    document.getElementById('formSummary').classList.remove('show');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Download JSON Function
/*function downloadJSON() {
    if (!savedFormData) {
        alert('No data to download!');
        return;
    }
    
    // Convert the data to JSON string with formatting
    const dataStr = JSON.stringify(savedFormData, null, 2);
    
    // Create a Blob from the JSON string
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    // Create a download link
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `registration_${new Date().getTime()}.json`;
    
    // Trigger the download
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    // Show success message
    console.log('JSON file downloaded successfully!');
}
*/
// Additional utility functions

// Validate age (18+)
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

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Validate phone number (exactly 10 digits)
function isValidPhoneNumber(phone) {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone);
}

// Validate postal code (6 digits)
function isValidPostalCode(code) {
    const postalRegex = /^[0-9]{6}$/;
    return postalRegex.test(code);
}