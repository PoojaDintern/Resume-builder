// Get user data from session
function getUserData() {
    const user = sessionStorage.getItem('user');
    if (user) {
        try {
            return JSON.parse(user);
        } catch (e) {
            return null;
        }
    }
    return null;
}

// Initialize user display in header
function initializeUserDisplay() {
    const userData = getUserData();
    
    if (!userData) {
        // Redirect to login if no user data
        window.location.href = 'login.html';
        return;
    }

    const fullName = `${userData.first_name || ''} ${userData.last_name || ''}`.trim();
    const displayName = fullName || userData.username || 'User';
    const email = userData.email || 'user@email.com';

    let initials = 'U';
    if (fullName) {
        initials = fullName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    } else if (userData.username) {
        initials = userData.username[0].toUpperCase();
    }

    document.getElementById('headerAvatar').textContent = initials;
    document.getElementById('headerUserName').textContent = displayName;
    document.getElementById('dropdownAvatar').textContent = initials;
    document.getElementById('dropdownUserName').textContent = displayName;
    document.getElementById('dropdownUserEmail').textContent = email;
}

// Toggle dropdown menu
function toggleDropdown() {
    document.getElementById('userDropdown').classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('userDropdown');
    const trigger = document.querySelector('.profile-trigger');
    
    if (trigger && !trigger.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

// Open settings modal
function openSettings() {
    document.getElementById('settingsModal').classList.add('show');
    toggleDropdown();
}

// Close settings modal
function closeSettings() {
    document.getElementById('settingsModal').classList.remove('show');
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeSettings();
            }
        });
    }
});

// Toggle setting switch
function toggleSetting(element) {
    element.classList.toggle('active');
    const settingTitle = element.parentElement.querySelector('.setting-title').textContent.trim();
    const isActive = element.classList.contains('active');
    localStorage.setItem('setting_' + settingTitle.replace(/\s+/g, '_'), isActive);
}

// Switch account
function switchAccount() {
    if (confirm('Are you sure you want to switch accounts? This will log you out.')) {
        sessionStorage.clear();
        window.location.href = 'login.html';
    }
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        sessionStorage.clear();
        window.location.href = 'login.html';
    }
}


// Global state
let counts = {
    work: 0,
    education: 0,
    project: 0,
    professionalSkill: 0,
    technicalSkill: 0,
    personalSkill: 0,
    hobby: 0,
    cert: 0
};

let vis = {
    work: {},
    education: {},
    project: {},
    cert: {}
};

let photo = '';
let currentResumeId = null; // Store the current resume ID

// ==================== TRACKING FUNCTIONS ====================

// Track visitor when page loads
async function trackVisitor() {
    try {
        const response = await fetch('http://localhost:5000/api/visitor/increment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();
        if (result.success) {
            console.log('✓ Visitor tracked. Resume ID:', result.resume_id, 'Count:', result.visitor_count);
            currentResumeId = result.resume_id; // Store the resume ID
        }
    } catch (error) {
        console.error('Failed to track visitor:', error);
    }
}

// Track download when PDF is downloaded
async function trackDownload() {
    try {
        console.log('Tracking download for resume ID:', currentResumeId);
        
        const response = await fetch('http://localhost:5000/api/download/increment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                resume_id: currentResumeId 
            })
        });
        
        const result = await response.json();
        if (result.success) {
            console.log('✓ Download tracked. Resume ID:', result.resume_id, 'Count:', result.download_count);
        } else {
            console.error('Download tracking failed:', result.message);
        }
    } catch (error) {
        console.error('Failed to track download:', error);
    }
}

// Track visitor on page load
window.addEventListener('DOMContentLoaded', () => {
    trackVisitor();
});

// ==================== EXISTING FUNCTIONS ====================

// Calculate experience duration
function calculateExperience(startDate, endDate) {
    if (!startDate || !endDate) return '';
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    if (end < start) return '';
    
    let years = end.getFullYear() - start.getFullYear();
    let months = end.getMonth() - start.getMonth();
    
    if (months < 0) {
        years--;
        months += 12;
    }
    
    let result = [];
    if (years > 0) result.push(years + (years === 1 ? ' year' : ' years'));
    if (months > 0) result.push(months + (months === 1 ? ' month' : ' months'));
    
    return result.join(' ') || '';
}

// Add dynamic item to sections
function addItem(type) {
    if (counts[type] > 0) {
        const lastId = counts[type];
        let isEmpty = false;
        
        if (type === 'work') {
            const company = document.getElementById(`company-${lastId}`)?.value.trim();
            const role = document.getElementById(`role-${lastId}`)?.value.trim();
            isEmpty = !company && !role;
        } else if (type === 'education') {
            const college = document.getElementById(`college-${lastId}`)?.value.trim();
            const course = document.getElementById(`course-${lastId}`)?.value.trim();
            isEmpty = !college && !course;
        } else if (type === 'project') {
            const name = document.getElementById(`projectName-${lastId}`)?.value.trim();
            const desc = document.getElementById(`projectDesc-${lastId}`)?.value.trim();
            isEmpty = !name && !desc;
        } else if (type === 'professionalSkill') {
            const skill = document.getElementById(`professionalSkillName-${lastId}`)?.value.trim();
            isEmpty = !skill;
        } else if (type === 'technicalSkill') {
            const skill = document.getElementById(`technicalSkillName-${lastId}`)?.value.trim();
            isEmpty = !skill;
        } else if (type === 'personalSkill') {
            const skill = document.getElementById(`personalSkillName-${lastId}`)?.value.trim();
            isEmpty = !skill;
        } else if (type === 'hobby') {
            const hobby = document.getElementById(`hobbyName-${lastId}`)?.value.trim();
            isEmpty = !hobby;
        } else if (type === 'cert') {
            const name = document.getElementById(`certName-${lastId}`)?.value.trim();
            const org = document.getElementById(`certOrg-${lastId}`)?.value.trim();
            isEmpty = !name && !org;
        }
        
        if (isEmpty) {
            const lastItem = document.getElementById(`${type}-${lastId}`);
            if (lastItem) {
                lastItem.classList.add('error-shake');
                setTimeout(() => {
                    lastItem.classList.remove('error-shake');
                }, 1500);
            }
            return;
        }
    }
    
    const id = ++counts[type];
    const container = document.getElementById(type + 'Container');
    const div = document.createElement('div');
    div.className = 'dynamic-item';
    div.id = `${type}-${id}`;
    
    let html = '<div class="item-header">';
    
    // Left side - visibility toggle (only for first item in work/education/project/cert)
    if(['work', 'education', 'project', 'cert'].includes(type)) {
        vis[type][id] = true;
        if (id === 1) {
            html += `<div class="move-buttons"><button class="visibility-toggle" onclick="toggleVis('${type}',${id})" title="Toggle"><i class="fas fa-eye"></i></button></div>`;
        } else {
            html += `<div class="move-buttons"></div>`;
        }
    } else {
        html += `<div class="move-buttons"></div>`;
    }
    
    // Right side - move up, move down, delete buttons
    html += `<div class="move-buttons">
        <button class="move-btn" onclick="moveUp('${type}Container','${type}-${id}')" title="Move Up"><i class="fas fa-arrow-up"></i></button>
        <button class="move-btn" onclick="moveDown('${type}Container','${type}-${id}')" title="Move Down"><i class="fas fa-arrow-down"></i></button>
        <button class="delete-item-btn" onclick="removeItem('${type}-${id}')" style="display:${id > 1 ? 'flex' : 'none'}" title="Delete"><i class="fas fa-trash"></i></button>
    </div></div>`;

    if(type === 'work') {
        html += `<div class="row mb-2">
            <div class="col-6"><input class="form-control" id="company-${id}" placeholder="Company"></div>
            <div class="col-6"><input class="form-control" id="role-${id}" placeholder="Role"></div>
        </div>
        <div class="row mb-2">
            <div class="col-6">
                <label class="form-label" style="font-size: 12px;">Start Date</label>
                <input type="date" class="form-control" id="startDate-${id}" onchange="updateExperience(${id})">
            </div>
            <div class="col-6">
                <label class="form-label" style="font-size: 12px;">End Date</label>
                <input type="date" class="form-control" id="endDate-${id}" onchange="updateExperience(${id})">
            </div>
        </div>
        <div class="experience-info" id="exp-${id}"></div>`;
    } else if(type === 'education') {
        html += `<div class="row mb-2">
            <div class="col-6"><input class="form-control" id="college-${id}" placeholder="Institution"></div>
            <div class="col-6"><input class="form-control" id="course-${id}" placeholder="Degree"></div>
        </div>
        <div class="row">
            <div class="col-6">
                <label class="form-label" style="font-size: 12px;">Passing Year</label>
                <input type="number" class="form-control" id="year-${id}" placeholder="Year" min="1950" max="2100">
            </div>
            <div class="col-6">
                <label class="form-label" style="font-size: 12px;">Percentage/CGPA</label>
                <input class="form-control" id="percentage-${id}" placeholder="e.g., 85% or 8.5 CGPA">
            </div>
        </div>`;
    } else if(type === 'project') {
        html += `<input class="form-control mb-2" id="projectName-${id}" placeholder="Project Name" style="max-width: 500px;">
        <textarea class="form-control mb-2" id="projectDesc-${id}" placeholder="Description" rows="3"></textarea>
        <input type="url" class="form-control" id="projectLink-${id}" placeholder="Link (optional)" style="max-width: 500px;">`;
    } else if(type === 'professionalSkill') {
        html += `<input class="form-control skill-input" id="professionalSkillName-${id}" placeholder="e.g., Project Management" required>`;
    } else if(type === 'technicalSkill') {
        html += `<input class="form-control skill-input" id="technicalSkillName-${id}" placeholder="e.g., Python" required>`;
    } else if(type === 'personalSkill') {
        html += `<input class="form-control skill-input" id="personalSkillName-${id}" placeholder="e.g., Time Management" required>`;
    } else if(type === 'hobby') {
        html += `<input class="form-control hobby-input" id="hobbyName-${id}" placeholder="e.g., Reading" required>`;
    } else if(type === 'cert') {
        html += `<input class="form-control mb-2" id="certName-${id}" placeholder="Certificate Name" style="max-width: 500px;">
        <input class="form-control mb-2" id="certOrg-${id}" placeholder="Organization" style="max-width: 500px;">
        <input type="number" class="form-control" id="certYear-${id}" placeholder="Year" min="1950" max="2100" style="max-width: 200px;">`;
    }
    
    div.innerHTML = html;
    container.appendChild(div);
    updateSection(type.charAt(0).toUpperCase() + type.slice(1));
}

// Update experience display in form
function updateExperience(id) {
    const startDate = document.getElementById(`startDate-${id}`).value;
    const endDate = document.getElementById(`endDate-${id}`).value;
    const expDiv = document.getElementById(`exp-${id}`);
    
    const exp = calculateExperience(startDate, endDate);
    if (exp) {
        expDiv.textContent = `Experience: ${exp}`;
        expDiv.classList.add('show');
    } else {
        expDiv.classList.remove('show');
    }
}

// Toggle visibility
function toggleVis(type, id) {
    vis[type][id] = !vis[type][id];
    const btn = document.querySelector(`#${type}-${id} .visibility-toggle`);
    btn.classList.toggle('hidden');
    btn.querySelector('i').className = vis[type][id] ? 'fas fa-eye' : 'fas fa-eye-slash';
}

// Move item up
function moveUp(cId, iId) {
    const c = document.getElementById(cId);
    const i = document.getElementById(iId);
    const p = i.previousElementSibling;
    if(p) c.insertBefore(i, p);
}

// Move item down
function moveDown(cId, iId) {
    const c = document.getElementById(cId);
    const i = document.getElementById(iId);
    const n = i.nextElementSibling;
    if(n) c.insertBefore(n, i);
}

// Remove item
function removeItem(id) {
    document.getElementById(id)?.remove();
}

// Update current section indicator
function updateSection(name) {
    document.getElementById('currentSection').textContent = name;
}

// Photo upload handler
document.getElementById('photo').addEventListener('change', e => {
    const f = e.target.files[0];
    if(f) {
        const r = new FileReader();
        r.onload = e => photo = e.target.result;
        r.readAsDataURL(f);
    }
});

// Validation
['email', 'phone', 'dob', 'linkedin', 'social'].forEach(id => {
    document.getElementById(id).addEventListener('blur', function() {
        const v = this.value.trim();
        let err = '';
        
        if(id === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) {
            err = 'Invalid email format';
        }
        
        if(id === 'phone' && v && v.replace(/\D/g, '').length !== 10) {
            err = 'Must be 10 digits';
        }
        
        if(id === 'dob' && v) {
            const age = Math.floor((new Date() - new Date(v)) / 31557600000);
            if(age < 18 || age > 100) {
                err = 'Age must be 18-100';
            }
        }
        
        if(id === 'linkedin' && v) {
            if(!v.startsWith('http://') && !v.startsWith('https://')) {
                err = 'URL must start with http:// or https://';
            } else if(!v.includes('linkedin.com')) {
                err = 'Must be a LinkedIn URL';
            }
        }
        
        if(id === 'social' && v) {
            if(!v.startsWith('http://') && !v.startsWith('https://')) {
                err = 'URL must start with http:// or https://';
            }
        }
        
        if(err) {
            this.classList.add('error-input');
            document.getElementById(id + '-error').textContent = err;
            document.getElementById(id + '-error').classList.add('show');
        } else {
            this.classList.remove('error-input');
            document.getElementById(id + '-error').classList.remove('show');
        }
    });
});

// Preview resume function
async function previewResume() {
    const req = ['fullName', 'email', 'dob', 'phone', 'location', 'objective', 'signature'];
    let valid = true;
    let errors = [];
    
    document.getElementById('errorBox').classList.remove('show');
    document.getElementById('errorList').innerHTML = '';
    
    document.querySelectorAll('.error-input').forEach(el => el.classList.remove('error-input'));
    document.querySelectorAll('.error-message').forEach(el => el.classList.remove('show'));
    
    req.forEach(id => {
        const el = document.getElementById(id);
        if(!el.value.trim()) {
            el.classList.add('error-input');
            const label = el.previousElementSibling?.textContent.replace('*', '').trim() || id;
            const errorMsg = `${label} is required`;
            document.getElementById(id + '-error').textContent = errorMsg;
            document.getElementById(id + '-error').classList.add('show');
            errors.push(errorMsg);
            valid = false;
        }
    });
    
    const emailEl = document.getElementById('email');
    if(emailEl.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailEl.value)) {
        emailEl.classList.add('error-input');
        const errorMsg = 'Email format is invalid';
        document.getElementById('email-error').textContent = errorMsg;
        document.getElementById('email-error').classList.add('show');
        errors.push(errorMsg);
        valid = false;
    }
    
    const phoneEl = document.getElementById('phone');
    if(phoneEl.value.trim() && phoneEl.value.replace(/\D/g, '').length !== 10) {
        phoneEl.classList.add('error-input');
        const errorMsg = 'Phone number must be exactly 10 digits';
        document.getElementById('phone-error').textContent = errorMsg;
        document.getElementById('phone-error').classList.add('show');
        errors.push(errorMsg);
        valid = false;
    }
    
    const dobEl = document.getElementById('dob');
    if(dobEl.value) {
        const age = Math.floor((new Date() - new Date(dobEl.value)) / 31557600000);
        if(age < 18 || age > 100) {
            dobEl.classList.add('error-input');
            const errorMsg = 'Age must be between 18-100 years';
            document.getElementById('dob-error').textContent = errorMsg;
            document.getElementById('dob-error').classList.add('show');
            errors.push(errorMsg);
            valid = false;
        }
    }
    
    const linkedinEl = document.getElementById('linkedin');
    if(linkedinEl.value.trim()) {
        if(!linkedinEl.value.startsWith('http://') && !linkedinEl.value.startsWith('https://')) {
            linkedinEl.classList.add('error-input');
            const errorMsg = 'LinkedIn URL must start with http:// or https://';
            document.getElementById('linkedin-error').textContent = errorMsg;
            document.getElementById('linkedin-error').classList.add('show');
            errors.push(errorMsg);
            valid = false;
        } else if(!linkedinEl.value.includes('linkedin.com')) {
            linkedinEl.classList.add('error-input');
            const errorMsg = 'Must be a valid LinkedIn URL';
            document.getElementById('linkedin-error').textContent = errorMsg;
            document.getElementById('linkedin-error').classList.add('show');
            errors.push(errorMsg);
            valid = false;
        }
    }
    
    const socialEl = document.getElementById('social');
    if(socialEl.value.trim()) {
        if(!socialEl.value.startsWith('http://') && !socialEl.value.startsWith('https://')) {
            socialEl.classList.add('error-input');
            const errorMsg = 'GitHub/Portfolio URL must start with http:// or https://';
            document.getElementById('social-error').textContent = errorMsg;
            document.getElementById('social-error').classList.add('show');
            errors.push(errorMsg);
            valid = false;
        }
    }
    
    let hasProSkill = false, hasTechSkill = false, hasPerSkill = false, hasHobby = false;
    
    for(let i = 1; i <= counts.professionalSkill; i++) {
        const el = document.getElementById(`professionalSkillName-${i}`);
        if(el && el.value.trim()) hasProSkill = true;
    }
    
    for(let i = 1; i <= counts.technicalSkill; i++) {
        const el = document.getElementById(`technicalSkillName-${i}`);
        if(el && el.value.trim()) hasTechSkill = true;
    }
    
    for(let i = 1; i <= counts.personalSkill; i++) {
        const el = document.getElementById(`personalSkillName-${i}`);
        if(el && el.value.trim()) hasPerSkill = true;
    }
    
    for(let i = 1; i <= counts.hobby; i++) {
        const el = document.getElementById(`hobbyName-${i}`);
        if(el && el.value.trim()) hasHobby = true;
    }
    
    if(!hasProSkill) {
        errors.push('At least one Professional Skill is required');
        valid = false;
    }
    if(!hasTechSkill) {
        errors.push('At least one Technical Skill is required');
        valid = false;
    }
    if(!hasPerSkill) {
        errors.push('At least one Personal Skill is required');
        valid = false;
    }
    if(!hasHobby) {
        errors.push('At least one Hobby is required');
        valid = false;
    }
    
    if(!valid) {
        const errorBox = document.getElementById('errorBox');
        const errorList = document.getElementById('errorList');
        errorList.innerHTML = errors.map(err => `<li>${err}</li>`).join('');
        errorBox.classList.add('show');
        errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }
    
    // Set name and location
    document.getElementById('resumeName').textContent = document.getElementById('fullName').value;
    const location = document.getElementById('location').value;
    document.getElementById('resumeLocation').innerHTML = `<i class="fas fa-map-marker-alt"></i>${location}`;
    
    // Set contact info (excluding DOB)
    let contact = '';
    ['email', 'phone', 'linkedin', 'social'].forEach(id => {
        const v = document.getElementById(id).value;
        if(v) {
            const icons = {
                email: 'envelope',
                phone: 'phone',
                linkedin: 'linkedin',
                social: 'github'
            };
            contact += `<div class="contact-item"><i class="fas fa-${icons[id]}"></i><span>${v}</span></div>`;
        }
    });
    document.getElementById('resumeContact').innerHTML = contact;
    
    // Set photo
    const showPhoto = document.getElementById('showPhotoInResume').checked;
    if(photo && showPhoto) {
        document.getElementById('resumePhoto').src = photo;
        document.getElementById('resumePhoto').style.display = 'block';
    } else {
        document.getElementById('resumePhoto').style.display = 'none';
    }
    
    // Set objective
    const obj = document.getElementById('objective').value;
    if(obj) {
        document.getElementById('resumeObj').textContent = obj;
        document.getElementById('objSection').style.display = 'block';
    }
    
    // Set work experience
    let work = '';
    for(let i = 1; i <= counts.work; i++) {
        if(document.getElementById(`work-${i}`) && vis.work[i]) {
            const c = document.getElementById(`company-${i}`).value;
            const r = document.getElementById(`role-${i}`).value;
            const startDate = document.getElementById(`startDate-${i}`).value;
            const endDate = document.getElementById(`endDate-${i}`).value;
            
            if(c || r) {
                const exp = calculateExperience(startDate, endDate);
                work += `<div class="work-item mb-3">`;
                if(r) work += `<h5>${r}</h5>`;
                if(c) work += `<p><strong>${c}</strong></p>`;
                if(startDate && endDate) {
                    work += `<p style="font-size: 14px; color: #666;">${new Date(startDate).toLocaleDateString()} - ${new Date(endDate).toLocaleDateString()}`;
                    if(exp) work += ` <span style="font-style: italic;">(Experience: ${exp})</span>`;
                    work += `</p>`;
                }
                work += `</div>`;
            }
        }
    }
    if(work) {
        document.getElementById('resumeWork').innerHTML = work;
        document.getElementById('workSection').style.display = 'block';
    } else {
        document.getElementById('workSection').style.display = 'none';
    }
    
    // Set education
    let edu = '';
    for(let i = 1; i <= counts.education; i++) {
        if(document.getElementById(`education-${i}`) && vis.education[i]) {
            const col = document.getElementById(`college-${i}`).value;
            const crs = document.getElementById(`course-${i}`).value;
            const year = document.getElementById(`year-${i}`).value;
            const perc = document.getElementById(`percentage-${i}`).value;
            
            if(col || crs) {
                edu += `<div class="edu-item mb-3">`;
                if(crs) edu += `<h5>${crs}</h5>`;
                if(col) edu += `<p>${col}</p>`;
                if(year || perc) {
                    edu += `<p style="font-size: 14px; color: #666;">`;
                    if(year) edu += `Year: ${year}`;
                    if(year && perc) edu += ` | `;
                    if(perc) edu += `Score: ${perc}`;
                    edu += `</p>`;
                }
                edu += `</div>`;
            }
        }
    }
    if(edu) {
        document.getElementById('resumeEdu').innerHTML = edu;
        document.getElementById('eduSection').style.display = 'block';
    } else {
        document.getElementById('eduSection').style.display = 'none';
    }
    
    // Set projects
    let proj = '';
    for(let i = 1; i <= counts.project; i++) {
        if(document.getElementById(`project-${i}`) && vis.project[i]) {
            const n = document.getElementById(`projectName-${i}`).value;
            const d = document.getElementById(`projectDesc-${i}`).value;
            const l = document.getElementById(`projectLink-${i}`).value;
            if(n || d) {
                proj += `<div class="mb-3">`;
                if(n) proj += `<h5>${n}</h5>`;
                if(d) proj += `<p>${d}</p>`;
                if(l) proj += `<p style="font-size: 13px;"><i class="fas fa-link"></i> <a href="${l}" target="_blank">${l}</a></p>`;
                proj += `</div>`;
            }
        }
    }
    if(proj) {
        document.getElementById('resumeProj').innerHTML = proj;
        document.getElementById('projSection').style.display = 'block';
    } else {
        document.getElementById('projSection').style.display = 'none';
    }
    
    // Set skills
    let professionalSkills = '';
    for(let i = 1; i <= counts.professionalSkill; i++) {
        const s = document.getElementById(`professionalSkillName-${i}`)?.value;
        if(s && s.trim()) {
            professionalSkills += `<p>${s.trim()}</p>`;
        }
    }
    
    let technicalSkills = '';
    for(let i = 1; i <= counts.technicalSkill; i++) {
        const s = document.getElementById(`technicalSkillName-${i}`)?.value;
        if(s && s.trim()) {
            technicalSkills += `<p>${s.trim()}</p>`;
        }
    }
    
    let personalSkills = '';
    for(let i = 1; i <= counts.personalSkill; i++) {
        const s = document.getElementById(`personalSkillName-${i}`)?.value;
        if(s && s.trim()) {
            personalSkills += `<p>${s.trim()}</p>`;
        }
    }
    
    if(professionalSkills) {
        document.getElementById('resumeProfessionalSkills').innerHTML = professionalSkills;
        document.getElementById('professionalSkillsDiv').style.display = 'block';
    } else {
        document.getElementById('professionalSkillsDiv').style.display = 'none';
    }
    
    if(technicalSkills) {
        document.getElementById('resumeTechnicalSkills').innerHTML = technicalSkills;
        document.getElementById('technicalSkillsDiv').style.display = 'block';
    } else {
        document.getElementById('technicalSkillsDiv').style.display = 'none';
    }
    
    if(personalSkills) {
        document.getElementById('resumePersonalSkills').innerHTML = personalSkills;
        document.getElementById('personalSkillsDiv').style.display = 'block';
    } else {
        document.getElementById('personalSkillsDiv').style.display = 'none';
    }
    
    if(professionalSkills || technicalSkills || personalSkills) {
        document.getElementById('skillSection').style.display = 'block';
    } else {
        document.getElementById('skillSection').style.display = 'none';
    }
    
    // Set hobbies
    let hobbies = '';
    for(let i = 1; i <= counts.hobby; i++) {
        const h = document.getElementById(`hobbyName-${i}`)?.value;
        if(h && h.trim()) {
            hobbies += `<p>${h.trim()}</p>`;
        }
    }
    if(hobbies) {
        document.getElementById('resumeHobbies').innerHTML = hobbies;
        document.getElementById('hobbySection').style.display = 'block';
    } else {
        document.getElementById('hobbySection').style.display = 'none';
    }
    
    // Set certificates
    let certs = '';
    for(let i = 1; i <= counts.cert; i++) {
        if(document.getElementById(`cert-${i}`) && vis.cert[i]) {
            const n = document.getElementById(`certName-${i}`)?.value;
            const o = document.getElementById(`certOrg-${i}`)?.value;
            const y = document.getElementById(`certYear-${i}`)?.value;
            if(n || o) {
                certs += `<div class="mb-3">`;
                if(n) certs += `<h6>${n}</h6>`;
                if(o) certs += `<p>${o}</p>`;
                if(y) certs += `<p style="font-size: 13px; color: #666;">Year: ${y}</p>`;
                certs += `</div>`;
            }
        }
    }
    if(certs) {
        document.getElementById('resumeCerts').innerHTML = certs;
        document.getElementById('certSection').style.display = 'block';
    } else {
        document.getElementById('certSection').style.display = 'none';
    }
    
    // Set signature
    document.getElementById('resumeSig').textContent = document.getElementById('signature').value;
    
    // Show preview
    document.getElementById('formSection').style.display = 'none';
    document.getElementById('resumePreview').style.display = 'block';
    updateSection('Preview');
}

// Back to form
function backToForm() {
    document.getElementById('formSection').style.display = 'block';
    document.getElementById('resumePreview').style.display = 'none';
    updateSection('Form');
}

// Download PDF - UPDATED WITH TRACKING
async function downloadPDF() {
    // IMPORTANT: Track download BEFORE generating PDF
    
    await trackDownload();
    
    const element = document.getElementById("resumePreview");
    const buttons = element.querySelector(".text-center.mt-4");

    if (buttons) buttons.style.display = "none";

    element.style.width = "210mm";
    element.style.margin = "0 auto";
    element.style.padding = "15mm";
    element.style.boxShadow = "none";
    element.style.borderRadius = "0";
    element.style.overflow = "visible";

    const A4_HEIGHT_PX = 1122;
    const contentHeight = element.scrollHeight;

    let scale = 1.35;
    if (contentHeight > A4_HEIGHT_PX) {
        scale = A4_HEIGHT_PX / contentHeight;
        scale = Math.max(scale, 0.75);
    }

    const opt = {
        margin: 0,
        filename: (document.getElementById("fullName")?.value || "Resume") + ".pdf",
        image: { type: "jpeg", quality: 1 },
        html2canvas: {
            scale: scale,
            scrollY: 0,
            useCORS: true
        },
        jsPDF: {
            unit: "mm",
            format: "a4",
            orientation: "portrait"
        },
        pagebreak: { mode: ["avoid-all"] }
    };

    html2pdf()
        .from(element)
        .set(opt)
        .save()
        .then(() => {
            console.log('✓ PDF downloaded successfully');
            if (buttons) buttons.style.display = "flex";
        })
        .catch(err => {
            console.error('PDF download error:', err);
            if (buttons) buttons.style.display = "flex";
        });
}

// Wrapper function for save button
async function saveToDatabase() {
    console.log('Save button clicked!');
    const result = await saveResumeToDatabase();
    
    if (result.success) {
        alert(`✓ Resume saved successfully!\nResume ID: ${result.resume_id}`);
        // Store the resume ID for download tracking
        currentResumeId = result.resume_id;
    } else {
        alert(`❌ Failed to save resume:\n${result.message}`);
    }
}

// Initialize with one item of each major section
['work', 'education', 'project', 'professionalSkill', 'technicalSkill', 'personalSkill', 'hobby', 'cert'].forEach(t => addItem(t));