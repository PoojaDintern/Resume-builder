# Save this as: app.py
# Complete Flask Application with Role-Based Authentication + Tracking

"""
Flask Main Application - With Role-Based Authentication and Analytics Tracking
-----------------------------------------------------------------
Handles authentication, job management, resume operations, and visitor/download tracking
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from datetime import datetime
import hashlib
import re

def create_app():
    """Creates and configures the Flask application"""
    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    return app

app = create_app()

# ==================== HELPER FUNCTIONS ====================

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (10 digits)"""
    return re.match(r'^\d{10}$', phone) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

# ==================== HEALTH CHECK ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Resume Builder API is running',
        'timestamp': datetime.now().isoformat()
    })

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/check-availability', methods=['POST'])
def check_availability():
    """Check if username/email/phone is available"""
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        if not field or not value:
            return jsonify({'available': False}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        field_map = {
            'username': 'username',
            'email': 'email',
            'phone': 'phone'
        }
        
        if field not in field_map:
            return jsonify({'available': False}), 400
        
        db_field = field_map[field]
        cursor.execute(f"SELECT COUNT(*) FROM users WHERE {db_field} = ?", (value,))
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({'available': count == 0})
        
    except Exception as e:
        print(f"❌ ERROR in check_availability: {str(e)}")
        return jsonify({'available': False}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user with role/type"""
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        user_type = data.get('type', 'candidate').lower()
        
        if user_type not in ['candidate', 'recruiter', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Invalid account type. Must be candidate, recruiter, or admin.'
            }), 400
        
        if not all([username, first_name, last_name, email, phone, password]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({
                'success': False,
                'message': 'Username must be 3-20 characters'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        if not validate_phone(phone):
            return jsonify({
                'success': False,
                'message': 'Phone number must be 10 digits'
            }), 400
        
        if not validate_password(password):
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters with uppercase, lowercase, and number'
            }), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN username = ? THEN 1 END) as username_exists,
                COUNT(CASE WHEN email = ? THEN 1 END) as email_exists,
                COUNT(CASE WHEN phone = ? THEN 1 END) as phone_exists
            FROM users
        """, (username, email, phone))
        
        result = cursor.fetchone()
        
        if result[0] > 0:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Username already taken'
            }), 400
        
        if result[1] > 0:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400
        
        if result[2] > 0:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Phone number already registered'
            }), 400
        
        hashed_password = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email, phone, password, type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
        """, (username, first_name, last_name, email, phone, hashed_password, user_type))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ User registered successfully: {username} as {user_type}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful'
        }), 201
        
    except Exception as e:
        print(f"❌ ERROR in register: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user with role-based authentication"""
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        user_type = data.get('type', '').lower()
        
        if not username or not password or not user_type:
            return jsonify({
                'success': False,
                'message': 'Username, password, and account type are required'
            }), 400
        
        if user_type not in ['candidate', 'recruiter', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Invalid account type selected'
            }), 400
        
        hashed_password = hash_password(password)
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, first_name, last_name, email, phone, type
            FROM users
            WHERE username = ? AND password = ? AND type = ?
        """, (username, hashed_password, user_type))
        
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            user_data = {
                'id': user[0],
                'username': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'email': user[4],
                'phone': user[5],
                'type': user[6]
            }
            
            print(f"✓ User logged in successfully: {username} as {user[6]}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user_data
            })
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT type FROM users 
                WHERE username = ? AND password = ?
            """, (username, hashed_password))
            
            existing_user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': f'Invalid account type. This account is registered as {existing_user[0]}'
                }), 401
            else:
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401
        
    except Exception as e:
        print(f"❌ ERROR in login: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Login failed. Please try again.'
        }), 500

# ==================== VISITOR & DOWNLOAD TRACKING ====================

@app.route('/api/visitor/increment', methods=['POST'])
def increment_visitor():
    """Increment visitor count - creates new resume or updates existing one"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Get the most recent resume or create a new one
        cursor.execute("""
            SELECT TOP 1 ResumeID, VisitorCount 
            FROM Resumes 
            ORDER BY UpdatedDate DESC
        """)
        
        result = cursor.fetchone()
        
        if result:
            resume_id = result[0]
            current_count = result[1] or 0
            
            # Increment visitor count
            cursor.execute("""
                UPDATE Resumes 
                SET VisitorCount = ?, UpdatedDate = GETDATE()
                WHERE ResumeID = ?
            """, (current_count + 1, resume_id))
            
            new_count = current_count + 1
        else:
            # Create a new resume entry if none exists
            cursor.execute("""
                INSERT INTO Resumes (ResumeTitle, Status, VisitorCount, DownloadCount, CreatedDate, UpdatedDate)
                VALUES (?, ?, 1, 0, GETDATE(), GETDATE())
            """, ('Untitled Resume', 'Draft'))
            
            cursor.execute("SELECT @@IDENTITY")
            resume_id = cursor.fetchone()[0]
            new_count = 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Visitor count incremented for Resume ID {resume_id}: {new_count}")
        
        return jsonify({
            'success': True,
            'resume_id': int(resume_id),
            'visitor_count': new_count
        })
        
    except Exception as e:
        print(f"❌ ERROR in increment_visitor: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/download/increment', methods=['POST'])
def increment_download():
    """Increment download count for a specific resume"""
    try:
        data = request.get_json()
        resume_id = data.get('resume_id')
        
        if not resume_id:
            return jsonify({
                'success': False,
                'message': 'Resume ID is required'
            }), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Check if resume exists and get current download count
        cursor.execute("""
            SELECT DownloadCount 
            FROM Resumes 
            WHERE ResumeID = ?
        """, (resume_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Resume not found'
            }), 404
        
        current_count = result[0] or 0
        
        # Increment download count
        cursor.execute("""
            UPDATE Resumes 
            SET DownloadCount = ?, UpdatedDate = GETDATE()
            WHERE ResumeID = ?
        """, (current_count + 1, resume_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        new_count = current_count + 1
        
        print(f"✓ Download count incremented for Resume ID {resume_id}: {new_count}")
        
        return jsonify({
            'success': True,
            'resume_id': int(resume_id),
            'download_count': new_count
        })
        
    except Exception as e:
        print(f"❌ ERROR in increment_download: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==================== JOB MANAGEMENT ENDPOINTS ====================

@app.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    """Get all job postings"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT JobID, JobTitle, CompanyName, JobDescription, SkillsRequired,
                   Package, ExperienceRequired, JobType, Education, CreatedAt
            FROM JobPostings
            WHERE IsActive = 1
            ORDER BY CreatedAt DESC
        """)
        
        jobs = cursor.fetchall()
        
        result = []
        for job in jobs:
            result.append({
                'id': job[0],
                'job_title': job[1],
                'company_name': job[2],
                'job_description': job[3],
                'skills_required': job[4].split(',') if job[4] else [],
                'package': job[5],
                'experience_required': job[6],
                'job_type': job[7],
                'education': job[8],
                'created_at': job[9].isoformat() if job[9] else None
            })
        
        cursor.close()
        conn.close()
        
        print(f"✓ Retrieved {len(result)} jobs")
        
        return jsonify({
            'success': True,
            'jobs': result,
            'count': len(result)
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_all_jobs: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_by_id(job_id):
    """Get a specific job by ID"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT JobID, JobTitle, CompanyName, JobDescription, SkillsRequired,
                   Package, ExperienceRequired, JobType, Education, CreatedAt
            FROM JobPostings
            WHERE JobID = ? AND IsActive = 1
        """, (job_id,))
        
        job = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if job:
            result = {
                'id': job[0],
                'job_title': job[1],
                'company_name': job[2],
                'job_description': job[3],
                'skills_required': job[4].split(',') if job[4] else [],
                'package': job[5],
                'experience_required': job[6],
                'job_type': job[7],
                'education': job[8],
                'created_at': job[9].isoformat() if job[9] else None
            }
            
            print(f"✓ Retrieved job ID: {job_id}")
            
            return jsonify({
                'success': True,
                'job': result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
    except Exception as e:
        print(f"❌ ERROR in get_job_by_id: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job posting"""
    try:
        data = request.get_json()
        
        required_fields = ['job_title', 'company_name', 'job_description', 
                          'skills_required', 'package', 'experience_required', 
                          'job_type', 'education']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        skills_str = ','.join(data['skills_required']) if isinstance(data['skills_required'], list) else data['skills_required']
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO JobPostings (JobTitle, CompanyName, JobDescription, SkillsRequired,
                            Package, ExperienceRequired, JobType, Education, CreatedAt, IsActive)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME(), 1)
        """, (
            data['job_title'],
            data['company_name'],
            data['job_description'],
            skills_str,
            data['package'],
            data['experience_required'],
            data['job_type'],
            data['education']
        ))
        
        conn.commit()
        
        cursor.execute("SELECT @@IDENTITY")
        job_id = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✓ Job created successfully with ID: {job_id}")
        
        return jsonify({
            'success': True,
            'message': 'Job posting created successfully',
            'job_id': int(job_id)
        }), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_job: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update an existing job posting"""
    try:
        data = request.get_json()
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT JobID FROM JobPostings WHERE JobID = ? AND IsActive = 1", (job_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        update_fields = []
        update_values = []
        
        allowed_fields = {
            'job_title': 'JobTitle',
            'company_name': 'CompanyName',
            'job_description': 'JobDescription',
            'package': 'Package',
            'job_type': 'JobType',
            'experience_required': 'ExperienceRequired',
            'education': 'Education'
        }
        
        for field, db_field in allowed_fields.items():
            if field in data:
                update_fields.append(f"{db_field} = ?")
                update_values.append(data[field])
        
        if 'skills_required' in data:
            skills_str = ','.join(data['skills_required']) if isinstance(data['skills_required'], list) else data['skills_required']
            update_fields.append("SkillsRequired = ?")
            update_values.append(skills_str)
        
        if not update_fields:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'No fields to update'
            }), 400
        
        update_values.append(job_id)
        
        query = f"UPDATE JobPostings SET {', '.join(update_fields)} WHERE JobID = ?"
        cursor.execute(query, update_values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Job {job_id} updated successfully")
        
        return jsonify({
            'success': True,
            'message': 'Job updated successfully'
        })
        
    except Exception as e:
        print(f"❌ ERROR in update_job: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job posting (soft delete)"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT JobID FROM JobPostings WHERE JobID = ? AND IsActive = 1", (job_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        cursor.execute("UPDATE JobPostings SET IsActive = 0 WHERE JobID = ?", (job_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"✓ Job {job_id} deleted successfully")
        
        return jsonify({
            'success': True,
            'message': 'Job deleted successfully'
        })
        
    except Exception as e:
        print(f"❌ ERROR in delete_job: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==================== GLOBAL ANALYTICS ====================
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get total visitor and download counts across all resumes"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                ISNULL(SUM(VisitorCount), 0) as TotalVisitors,
                ISNULL(SUM(DownloadCount), 0) as TotalDownloads,
                MAX(UpdatedDate) as LastUpdated
            FROM Resumes
        """)
        row = cursor.fetchone()
        
        if row:
            total_visitors = row[0]
            total_downloads = row[1]
            last_updated = str(row[2]) if row[2] else None
        else:
            total_visitors = 0
            total_downloads = 0
            last_updated = None
        
        cursor.close()
        conn.close()
        
        print(f"✓ Analytics: Visitors={total_visitors}, Downloads={total_downloads}")
        
        return jsonify({
            'success': True,
            'data': {
                'visitor_count': total_visitors,
                'download_count': total_downloads,
                'last_updated': last_updated
            }
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==================== GET ALL RESUMES ====================
@app.route('/api/resumes', methods=['GET'])
def get_all_resumes():
    """Get all resumes with complete data for dashboard"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ResumeID, ResumeTitle, Status, CreatedDate, 
                   VisitorCount, DownloadCount 
            FROM Resumes 
            ORDER BY CreatedDate DESC
        """)
        resumes = cursor.fetchall()
        
        if not resumes:
            cursor.close()
            conn.close()
            return jsonify({
                'success': True,
                'data': [],
                'count': 0,
                'message': 'No resumes found in database'
            })
        
        result = []
        for resume in resumes:
            resume_id = resume[0]
            
            # Personal info
            cursor.execute("""
                SELECT FullName, Email, PhoneNumber, DateOfBirth, Location, 
                       LinkedInURL, GitHubURL, CareerObjective, PhotoPath
                FROM PersonalInformation 
                WHERE ResumeID = ?
            """, (resume_id,))
            p = cursor.fetchone()
            personal_info = {
                'full_name': p[0] if p and p[0] else 'Unknown',
                'email': p[1] if p and p[1] else 'No email',
                'phone_number': p[2] if p and p[2] else None,
                'date_of_birth': str(p[3]) if p and p[3] else None,
                'location': p[4] if p and p[4] else 'N/A',
                'linkedin_url': p[5] if p and p[5] else None,
                'github_url': p[6] if p and p[6] else None,
                'career_objective': p[7] if p and p[7] else None,
                'photo_path': p[8] if p and len(p) > 8 and p[8] else None
            } if p else {
                'full_name': 'Unknown',
                'email': 'No email',
                'location': 'N/A'
            }
            
            # Work experience
            cursor.execute("""
                SELECT CompanyName, JobRole, DateOfJoin, LastWorkingDate, Experience 
                FROM WorkExperience 
                WHERE ResumeID = ?
            """, (resume_id,))
            work_experience = [{
                'company_name': w[0],
                'job_role': w[1],
                'date_of_join': str(w[2]) if w[2] else None,
                'last_working_date': str(w[3]) if w[3] else None,
                'experience': w[4]
            } for w in cursor.fetchall()]
            
            # Education
            cursor.execute("""
                SELECT College, University, Course, Year, CGPA 
                FROM Education 
                WHERE ResumeID = ?
            """, (resume_id,))
            education = [{
                'institution_name': e[0],
                'university_name': e[1],
                'course_name': e[2],
                'year_of_completion': e[3],
                'cgpa': float(e[4]) if e[4] else None
            } for e in cursor.fetchall()]
            
            # Projects
            cursor.execute("""
                SELECT ProjectTitle, ProjectLink, Organization, Description 
                FROM Projects 
                WHERE ResumeID = ?
            """, (resume_id,))
            projects = [{
                'project_title': p[0],
                'project_link': p[1],
                'organization': p[2],
                'description': p[3]
            } for p in cursor.fetchall()]
            
            # Skills
            cursor.execute("""
                SELECT SkillType, SkillName 
                FROM Skills 
                WHERE ResumeID = ?
            """, (resume_id,))
            skills = [{
                'skill_type': s[0],
                'skill_name': s[1]
            } for s in cursor.fetchall()]
            
            # Certifications
            cursor.execute("""
                SELECT CertificationName 
                FROM Certifications 
                WHERE ResumeID = ?
            """, (resume_id,))
            certifications = [{
                'certification_name': c[0]
            } for c in cursor.fetchall()]
            
            # Interests
            cursor.execute("""
                SELECT InterestName 
                FROM Interests 
                WHERE ResumeID = ?
            """, (resume_id,))
            interests = [{
                'interest_name': i[0]
            } for i in cursor.fetchall()]
            
            result.append({
                'resume_id': resume_id,
                'resume_title': resume[1] if resume[1] else 'Untitled Resume',
                'status': resume[2] if len(resume) > 2 else 'Draft',
                'created_at': str(resume[3]) if resume[3] else None,
                'visitor_count': resume[4] if len(resume) > 4 else 0,
                'download_count': resume[5] if len(resume) > 5 else 0,
                'personal_info': personal_info,
                'work_experience': work_experience,
                'education': education,
                'projects': projects,
                'skills': skills,
                'certifications': certifications,
                'interests': interests
            })
        
        cursor.close()
        conn.close()
        
        print(f"✓ Successfully processed {len(result)} resumes")
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_all_resumes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==================== CREATE RESUME ====================
@app.route('/api/resume', methods=['POST'])
def create_resume():
    """Create a new resume"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Resumes (ResumeTitle, Status, VisitorCount, DownloadCount, CreatedDate, UpdatedDate) 
            VALUES (?, ?, 0, 0, GETDATE(), GETDATE())
        """, (
            data.get('resume_title', 'Untitled Resume'),
            'Draft'
        ))
        conn.commit()
        
        cursor.execute("SELECT @@IDENTITY")
        resume_id = cursor.fetchone()[0]
        
        print(f"✓ Resume created with ID: {resume_id}")
        
        # Insert personal info
        if 'personal_info' in data:
            pi = data['personal_info']
            cursor.execute("""
                INSERT INTO PersonalInformation 
                (ResumeID, FullName, Email, PhoneNumber, DateOfBirth, Location, 
                LinkedInURL, GitHubURL, CareerObjective, CreatedDate) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                resume_id, pi.get('full_name'), pi.get('email'), 
                pi.get('phone_number'), pi.get('date_of_birth'), pi.get('location'),
                pi.get('linkedin_url'), pi.get('github_url'), 
                pi.get('career_objective')
            ))
        
        # Insert work experience
        if 'work_experience' in data:
            for work in data['work_experience']:
                cursor.execute("""
                    INSERT INTO WorkExperience 
                    (ResumeID, CompanyName, JobRole, DateOfJoin, LastWorkingDate, Experience, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                """, (
                    resume_id, work.get('company_name'), work.get('job_role'),
                    work.get('date_of_join'), work.get('last_working_date'), 
                    work.get('experience')
                ))
        
        # Insert education
        if 'education' in data:
            for edu in data['education']:
                cursor.execute("""
                    INSERT INTO Education 
                    (ResumeID, College, University, Course, Year, CGPA, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                """, (
                    resume_id, edu.get('college'), edu.get('university'),
                    edu.get('course'), edu.get('year'), 
                    edu.get('cgpa')
                ))
        
        # Insert projects
        if 'projects' in data:
            for proj in data['projects']:
                cursor.execute("""
                    INSERT INTO Projects 
                    (ResumeID, ProjectTitle, ProjectLink, Organization, Description, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, GETDATE())
                """, (
                    resume_id, proj.get('project_title'), proj.get('project_link'),
                    proj.get('organization'), proj.get('description')
                ))
        
        # Insert skills
        if 'skills' in data:
            for skill in data['skills']:
                cursor.execute("""
                    INSERT INTO Skills (ResumeID, SkillType, SkillName, CreatedDate) 
                    VALUES (?, ?, ?, GETDATE())
                """, (
                    resume_id, skill.get('skill_type'), 
                    skill.get('skill_name')
                ))
        
        # Insert certifications
        if 'certifications' in data:
            for cert in data['certifications']:
                cursor.execute("""
                    INSERT INTO Certifications (ResumeID, CertificationName, CreatedDate) 
                    VALUES (?, ?, GETDATE())
                """, (
                    resume_id, cert.get('certification_name')
                ))
        
        # Insert interests
        if 'interests' in data:
            for interest in data['interests']:
                cursor.execute("""
                    INSERT INTO Interests (ResumeID, InterestName, CreatedDate) 
                    VALUES (?, ?, GETDATE())
                """, (
                    resume_id, interest.get('interest_name')
                ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Resume {resume_id} saved successfully")
        
        return jsonify({
            'success': True,
            'message': 'Resume created successfully',
            'resume_id': int(resume_id)
        }), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_resume: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    """Run the application"""
    
    print("\n" + "="*50)
    print("Resume Builder API Server - WITH TRACKING")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("API base URL: http://localhost:5000/api")
    print("\nAvailable endpoints:")
    print("\n🔐 AUTHENTICATION:")
    print("  POST /api/auth/register")
    print("  POST /api/auth/login")
    print("  POST /api/auth/check-availability")
    print("\n💼 JOB MANAGEMENT:")
    print("  GET  /api/jobs")
    print("  GET  /api/jobs/<id>")
    print("  POST /api/jobs")
    print("  PUT  /api/jobs/<id>")
    print("  DELETE /api/jobs/<id>")
    print("\n📄 RESUME MANAGEMENT:")
    print("  GET  /api/resumes")
    print("  POST /api/resume")
    print("\n📊 ANALYTICS & TRACKING:")
    print("  GET  /api/analytics")
    print("  POST /api/visitor/increment")
    print("  POST /api/download/increment")
    print("\n🔧 UTILITIES:")
    print("  GET  /api/health")
    print("\n🎭 USER ROLES:")
    print("  - Admin → home.html")
    print("  - Recruiter → jobdashboard.html")
    print("  - Candidate → dashboard.html")
    print("\nPress CTRL+C to stop the server")
    print("="*50 + "\n")
    
    # Test database connection
    try:
        Config.test_connection()
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {e}")
        print("Make sure SQL Server is running and database exists.\n")
    
    # Start server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )