"""
Flask Main Application - Complete with Authentication
-----------------------------------------------------------------
Handles all API endpoints including auth, visitor and download tracking
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from datetime import datetime
import hashlib
import re

def create_app():
    """Creates and configures the Flask application"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Enable CORS - allows frontend to call backend
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
    """
    Check if username/email/phone is available
    POST /api/auth/check-availability
    Body: {"field": "username/email/phone", "value": "..."}
    """
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        if not field or not value:
            return jsonify({'available': False}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Map field names to database columns
        field_map = {
            'username': 'username',
            'email': 'email',
            'phone': 'phone'
        }
        
        if field not in field_map:
            return jsonify({'available': False}), 400
        
        db_field = field_map[field]
        
        # Check if value exists
        cursor.execute(f"SELECT COUNT(*) FROM users WHERE {db_field} = ?", (value,))
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'available': count == 0
        })
        
    except Exception as e:
        print(f"❌ ERROR in check_availability: {str(e)}")
        return jsonify({'available': False}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register new user
    POST /api/auth/register
    Body: {
        "username": "...",
        "first_name": "...",
        "last_name": "...",
        "email": "...",
        "phone": "...",
        "password": "..."
    }
    """
    try:
        data = request.get_json()
        
        # Extract data
        username = data.get('username', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        
        # Validate required fields
        if not all([username, first_name, last_name, email, phone, password]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Validate username length
        if len(username) < 3 or len(username) > 20:
            return jsonify({
                'success': False,
                'message': 'Username must be 3-20 characters'
            }), 400
        
        # Validate email
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Validate phone
        if not validate_phone(phone):
            return jsonify({
                'success': False,
                'message': 'Phone number must be 10 digits'
            }), 400
        
        # Validate password strength
        if not validate_password(password):
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters with uppercase, lowercase, and number'
            }), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Check for duplicates
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
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email, phone, password, created_at)
            VALUES (?, ?, ?, ?, ?, ?, GETDATE())
        """, (username, first_name, last_name, email, phone, hashed_password))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ User registered successfully: {username}")
        
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
    """
    Login user
    POST /api/auth/login
    Body: {
        "username": "...",
        "password": "..."
    }
    """
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Hash password
        hashed_password = hash_password(password)
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Check credentials
        cursor.execute("""
            SELECT id, username, first_name, last_name, email, phone
            FROM users
            WHERE username = ? AND password = ?
        """, (username, hashed_password))
        
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            print(f"✓ User logged in successfully: {username}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'first_name': user[2],
                    'last_name': user[3],
                    'email': user[4],
                    'phone': user[5]
                }
            })
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


# ==================== GLOBAL ANALYTICS ====================
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get total visitor and download counts across all resumes"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Sum all visitor counts and download counts from Resumes table
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


# ==================== VISITOR COUNT TRACKING ====================
@app.route('/api/visitor/increment', methods=['POST'])
def increment_visitor():
    """
    Increment visitor count for the most recent resume
    """
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Get the most recent resume ID
        cursor.execute("""
            SELECT TOP 1 ResumeID 
            FROM Resumes 
            ORDER BY CreatedDate DESC
        """)
        result = cursor.fetchone()
        
        if result:
            resume_id = result[0]
            
            # Increment visitor count for this resume
            cursor.execute("""
                UPDATE Resumes 
                SET VisitorCount = VisitorCount + 1,
                    UpdatedDate = GETDATE()
                WHERE ResumeID = ?
            """, (resume_id,))
            conn.commit()
            
            # Get updated count
            cursor.execute("SELECT VisitorCount FROM Resumes WHERE ResumeID = ?", (resume_id,))
            visitor_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"✓ Visitor count incremented for Resume {resume_id} to: {visitor_count}")
            
            return jsonify({
                'success': True,
                'visitor_count': visitor_count,
                'resume_id': resume_id,
                'message': 'Visitor count updated'
            })
        else:
            # No resumes exist yet
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'visitor_count': 0,
                'message': 'No resumes exist yet'
            })
        
    except Exception as e:
        print(f"❌ ERROR in increment_visitor: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== DOWNLOAD COUNT TRACKING ====================
@app.route('/api/download/increment', methods=['POST'])
def increment_download():
    """
    Increment download count for a specific resume
    """
    try:
        data = request.get_json() or {}
        resume_id = data.get('resume_id')
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # If no resume_id provided, get the most recent one
        if not resume_id:
            cursor.execute("""
                SELECT TOP 1 ResumeID 
                FROM Resumes 
                ORDER BY CreatedDate DESC
            """)
            result = cursor.fetchone()
            if result:
                resume_id = result[0]
        
        if resume_id:
            # Increment download count
            cursor.execute("""
                UPDATE Resumes 
                SET DownloadCount = DownloadCount + 1,
                    UpdatedDate = GETDATE()
                WHERE ResumeID = ?
            """, (resume_id,))
            conn.commit()
            
            # Get updated count
            cursor.execute("SELECT DownloadCount FROM Resumes WHERE ResumeID = ?", (resume_id,))
            download_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"✓ Download count incremented for Resume {resume_id} to: {download_count}")
            
            return jsonify({
                'success': True,
                'download_count': download_count,
                'resume_id': resume_id,
                'message': 'Download count updated'
            })
        else:
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'download_count': 0,
                'message': 'No resumes exist yet'
            })
        
    except Exception as e:
        print(f"❌ ERROR in increment_download: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== CHECK DATABASE SCHEMA ====================
@app.route('/api/schema', methods=['GET'])
def check_schema():
    """Check database schema - useful for debugging"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_info = {}
        
        # Get columns for each table
        for table in tables:
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table}'
            """)
            schema_info[table] = [{'column': row[0], 'type': row[1]} for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'tables': tables,
            'schema': schema_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== GET ALL RESUMES (For Dashboard) ====================
@app.route('/api/resumes', methods=['GET'])
def get_all_resumes():
    """Get all resumes with complete data for dashboard"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Get all resumes with visitor and download counts
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
            print(f"Processing resume ID: {resume_id}")
            
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
                'phone_number': None,
                'date_of_birth': None,
                'location': 'N/A',
                'linkedin_url': None,
                'github_url': None,
                'career_objective': None,
                'photo_path': None
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
        
        # Insert resume with default counts of 0
        cursor.execute("""
            INSERT INTO Resumes (ResumeTitle, Status, VisitorCount, DownloadCount, CreatedDate) 
            VALUES (?, ?, 0, 0, ?)
        """, (
            data.get('resume_title', 'Untitled Resume'),
            'Draft',
            datetime.now()
        ))
        conn.commit()
        
        # Get the inserted resume_id
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resume_id, pi.get('full_name'), pi.get('email'), 
                pi.get('phone_number'), pi.get('date_of_birth'), pi.get('location'),
                pi.get('linkedin_url'), pi.get('github_url'), 
                pi.get('career_objective'), datetime.now()
            ))
        
        # Insert work experience
        if 'work_experience' in data:
            for work in data['work_experience']:
                cursor.execute("""
                    INSERT INTO WorkExperience 
                    (ResumeID, CompanyName, JobRole, DateOfJoin, LastWorkingDate, Experience, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    resume_id, work.get('company_name'), work.get('job_role'),
                    work.get('date_of_join'), work.get('last_working_date'), 
                    work.get('experience'), datetime.now()
                ))
        
        # Insert education
        if 'education' in data:
            for edu in data['education']:
                cursor.execute("""
                    INSERT INTO Education 
                    (ResumeID, College, University, Course, Year, CGPA, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    resume_id, edu.get('college'), edu.get('university'),
                    edu.get('course'), edu.get('year'), 
                    edu.get('cgpa'), datetime.now()
                ))
        
        # Insert projects
        if 'projects' in data:
            for proj in data['projects']:
                cursor.execute("""
                    INSERT INTO Projects 
                    (ResumeID, ProjectTitle, ProjectLink, Organization, Description, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    resume_id, proj.get('project_title'), proj.get('project_link'),
                    proj.get('organization'), proj.get('description'), datetime.now()
                ))
        
        # Insert skills
        if 'skills' in data:
            for skill in data['skills']:
                cursor.execute("""
                    INSERT INTO Skills (ResumeID, SkillType, SkillName, CreatedDate) 
                    VALUES (?, ?, ?, ?)
                """, (
                    resume_id, skill.get('skill_type'), 
                    skill.get('skill_name'), datetime.now()
                ))
        
        # Insert certifications
        if 'certifications' in data:
            for cert in data['certifications']:
                cursor.execute("""
                    INSERT INTO Certifications (ResumeID, CertificationName, CreatedDate) 
                    VALUES (?, ?, ?)
                """, (
                    resume_id, cert.get('certification_name'), datetime.now()
                ))
        
        # Insert interests
        if 'interests' in data:
            for interest in data['interests']:
                cursor.execute("""
                    INSERT INTO Interests (ResumeID, InterestName, CreatedDate) 
                    VALUES (?, ?, ?)
                """, (
                    resume_id, interest.get('interest_name'), datetime.now()
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
    print("Resume Builder API Server - COMPLETE VERSION")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("API base URL: http://localhost:5000/api")
    print("\nAvailable endpoints:")
    print("  GET  /api/health                     - Health check")
    print("  POST /api/auth/register              - Register new user")
    print("  POST /api/auth/login                 - Login user")
    print("  POST /api/auth/check-availability    - Check username/email/phone")
    print("  GET  /api/schema                     - Check database schema")
    print("  GET  /api/resumes                    - Get all resumes")
    print("  POST /api/resume                     - Create new resume")
    print("  POST /api/visitor/increment          - Track visitor")
    print("  POST /api/download/increment         - Track download")
    print("  GET  /api/analytics                  - Get visitor & download counts")
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