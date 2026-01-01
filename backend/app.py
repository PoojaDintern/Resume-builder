"""
Flask Main Application - Complete Version with Dashboard Support
-----------------------------------------------------------------
Fixed for SQL Server PascalCase column names
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from datetime import datetime

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


# ==================== HEALTH CHECK ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Resume Builder API is running',
        'timestamp': datetime.now().isoformat()
    })


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
        
        # Get all resumes using correct column names
        cursor.execute("""
            SELECT ResumeID, ResumeTitle, Status, CreatedDate 
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
                'institution_name': e[0],  # College
                'university_name': e[1],   # University
                'course_name': e[2],       # Course
                'year_of_completion': e[3], # Year
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


# ==================== GET SINGLE RESUME ====================
@app.route('/api/resume/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    """Get a single resume by ID"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Get resume basic info
        cursor.execute("SELECT * FROM Resumes WHERE ResumeID = ?", (resume_id,))
        resume = cursor.fetchone()
        
        if not resume:
            return jsonify({
                'success': False,
                'message': 'Resume not found'
            }), 404
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {}
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_resume: {str(e)}")
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
        
        # Insert resume
        cursor.execute("""
            INSERT INTO Resumes (ResumeTitle, Status, CreatedDate) 
            VALUES (?, ?, ?)
        """, (
            data.get('resume_title', 'Untitled Resume'),
            'Draft',
            datetime.now()
        ))
        conn.commit()
        
        # Get the inserted resume_id
        cursor.execute("SELECT @@IDENTITY")
        resume_id = cursor.fetchone()[0]
        
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
                    resume_id, edu.get('institution_name'), edu.get('university_name'),
                    edu.get('course_name'), edu.get('year_of_completion'), 
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
    print("Resume Builder API Server - READY")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("API base URL: http://localhost:5000/api")
    print("\nAvailable endpoints:")
    print("  GET  /api/health          - Health check")
    print("  GET  /api/schema          - Check database schema")
    print("  GET  /api/resumes         - Get all resumes (Dashboard)")
    print("  GET  /api/resume/<id>     - Get resume by ID")
    print("  POST /api/resume          - Create new resume")
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