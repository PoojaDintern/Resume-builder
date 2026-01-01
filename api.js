/**
 * API Handler - CORRECTED VERSION
 * --------------------------------
 * Handles all frontend-backend communication
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Make API calls with proper error handling
 */
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        console.log(`[API] ${method} ${API_BASE_URL}${endpoint}`);
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const responseData = await response.json();
        
        console.log('[API] Response:', responseData);
        
        return responseData;
        
    } catch (error) {
        console.error('[API] Error:', error);
        return {
            success: false,
            message: `Network error: ${error.message}`
        };
    }
}

/**
 * Test API connection
 */
async function testConnection() {
    console.log('[API] Testing connection...');
    const result = await apiCall('/health');
    
    if (result.status === 'ok') {
        console.log('✓ Backend connection successful!');
        return true;
    } else {
        console.error('✗ Backend connection failed!');
        console.error('Make sure backend server is running: python app.py');
        return false;
    }
}

/**
 * Collect all resume data from form
 */
function collectResumeData() {
    try {
        console.log('[COLLECT] Starting data collection...');
        
        // Personal Information - REMOVED photo_base64
        const personalInfo = {
            full_name: document.getElementById('fullName')?.value || '',
            email: document.getElementById('email')?.value || '',
            phone_number: document.getElementById('phone')?.value || '',
            date_of_birth: document.getElementById('dob')?.value || '',
            location: document.getElementById('location')?.value || '',
            linkedin_url: document.getElementById('linkedin')?.value || null,
            github_url: document.getElementById('social')?.value || null,
            career_objective: document.getElementById('objective')?.value || ''
        };
        
        console.log('[COLLECT] Personal info:', personalInfo.full_name);
        
        // Work Experience
        const workExperience = [];
        for (let i = 1; i <= counts.work; i++) {
            if (document.getElementById(`work-${i}`)) {
                const company = document.getElementById(`company-${i}`)?.value || '';
                const role = document.getElementById(`role-${i}`)?.value || '';
                const startDate = document.getElementById(`startDate-${i}`)?.value || null;
                const endDate = document.getElementById(`endDate-${i}`)?.value || null;
                
                if (company || role) {
                    const experience = calculateExperience(startDate, endDate);
                    workExperience.push({
                        company_name: company || null,
                        job_role: role || null,
                        date_of_join: startDate,
                        last_working_date: endDate,
                        experience: experience || null
                    });
                }
            }
        }
        console.log('[COLLECT] Work experience entries:', workExperience.length);
        
        // Education
        const education = [];
        for (let i = 1; i <= counts.education; i++) {
            if (document.getElementById(`education-${i}`)) {
                const college = document.getElementById(`college-${i}`)?.value || '';
                const course = document.getElementById(`course-${i}`)?.value || '';
                const year = document.getElementById(`year-${i}`)?.value || null;
                const percentage = document.getElementById(`percentage-${i}`)?.value || null;
                
                if (college || course) {
                    education.push({
                        college: college || null,
                        university: null,
                        course: course || null,
                        year: year ? parseInt(year) : null,
                        cgpa: percentage || null
                    });
                }
            }
        }
        console.log('[COLLECT] Education entries:', education.length);
        
        // Projects
        const projects = [];
        for (let i = 1; i <= counts.project; i++) {
            if (document.getElementById(`project-${i}`)) {
                const name = document.getElementById(`projectName-${i}`)?.value || '';
                const desc = document.getElementById(`projectDesc-${i}`)?.value || '';
                const link = document.getElementById(`projectLink-${i}`)?.value || null;
                
                if (name || desc) {
                    projects.push({
                        project_title: name || null,
                        project_link: link,
                        organization: null,
                        description: desc || null
                    });
                }
            }
        }
        console.log('[COLLECT] Project entries:', projects.length);
        
        // Skills
        const skills = [];
        
        // Professional Skills
        for (let i = 1; i <= counts.professionalSkill; i++) {
            const skill = document.getElementById(`professionalSkillName-${i}`)?.value;
            if (skill && skill.trim()) {
                skills.push({
                    skill_type: 'Professional',
                    skill_name: skill.trim()
                });
            }
        }
        
        // Technical Skills
        for (let i = 1; i <= counts.technicalSkill; i++) {
            const skill = document.getElementById(`technicalSkillName-${i}`)?.value;
            if (skill && skill.trim()) {
                skills.push({
                    skill_type: 'Technical',
                    skill_name: skill.trim()
                });
            }
        }
        
        // Personal Skills
        for (let i = 1; i <= counts.personalSkill; i++) {
            const skill = document.getElementById(`personalSkillName-${i}`)?.value;
            if (skill && skill.trim()) {
                skills.push({
                    skill_type: 'Personal',
                    skill_name: skill.trim()
                });
            }
        }
        console.log('[COLLECT] Total skills:', skills.length);
        
        // Certifications
        const certifications = [];
        for (let i = 1; i <= counts.cert; i++) {
            if (document.getElementById(`cert-${i}`)) {
                const name = document.getElementById(`certName-${i}`)?.value;
                if (name && name.trim()) {
                    certifications.push({
                        certification_name: name.trim()
                    });
                }
            }
        }
        console.log('[COLLECT] Certifications:', certifications.length);
        
        // Interests/Hobbies
        const interests = [];
        for (let i = 1; i <= counts.hobby; i++) {
            const hobby = document.getElementById(`hobbyName-${i}`)?.value;
            if (hobby && hobby.trim()) {
                interests.push({
                    interest_name: hobby.trim()
                });
            }
        }
        console.log('[COLLECT] Interests:', interests.length);
        
        // Resume Title and Signature
        const resumeTitle = `${personalInfo.full_name}'s Resume`;
        const signature = document.getElementById('signature')?.value || '';
        
        // Combine all data
        const resumeData = {
            personal_info: personalInfo,
            work_experience: workExperience,
            education: education,
            projects: projects,
            skills: skills,
            certifications: certifications,
            interests: interests,
            resume_title: resumeTitle,
            signature: signature
        };
        
        console.log('[COLLECT] ✓ Data collection complete');
        return resumeData;
        
    } catch (error) {
        console.error('[COLLECT] Error:', error);
        return null;
    }
}

/**
 * Save resume to database
 */
async function saveResumeToDatabase() {
    try {
        console.log('\n' + '='.repeat(50));
        console.log('SAVING RESUME TO DATABASE');
        console.log('='.repeat(50));
        
        showLoading(true);
        
        // Collect form data
        const resumeData = collectResumeData();
        
        if (!resumeData) {
            showLoading(false);
            return {
                success: false,
                message: 'Failed to collect form data'
            };
        }
        
        // Send to backend
        console.log('[SAVE] Sending data to backend...');
        const result = await apiCall('/resume', 'POST', resumeData);
        
        showLoading(false);
        
        // Handle result
        if (result.success) {
            console.log('✓ SUCCESS: Resume saved with ID', result.resume_id);
            return result;
        } else {
            console.error('❌ SAVE FAILED:', result.message);
            if (result.errors) {
                console.error('Validation errors:', result.errors);
            }
            return result;
        }
        
    } catch (error) {
        showLoading(false);
        console.error('[SAVE] Error:', error);
        return {
            success: false,
            message: error.message
        };
    }
}

/**
 * Load resume from database
 */
async function loadResumeFromDatabase(resumeId) {
    try {
        showLoading(true);
        
        const result = await apiCall(`/resume/${resumeId}`, 'GET');
        
        showLoading(false);
        
        if (result.success) {
            console.log('✓ Resume loaded successfully');
            return result.data;
        } else {
            alert(`Error loading resume: ${result.message}`);
            return null;
        }
        
    } catch (error) {
        showLoading(false);
        console.error('[LOAD] Error:', error);
        return null;
    }
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    let loader = document.getElementById('loadingIndicator');
    
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'loadingIndicator';
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;
        loader.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 10px; text-align: center;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #667eea; 
                            border-radius: 50%; width: 50px; height: 50px; 
                            animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                <p style="color: #667eea; font-weight: 600; margin: 0;">Saving your resume...</p>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(loader);
    }
    
    loader.style.display = show ? 'flex' : 'none';
}

// Test connection when page loads
window.addEventListener('DOMContentLoaded', () => {
    console.log('\n' + '='.repeat(50));
    console.log('RESUME BUILDER - FRONTEND LOADED');
    console.log('='.repeat(50));
    console.log('Testing backend connection...\n');
    testConnection();
});