# Save this as: app.py
# Complete Flask Application with Role-Based Authentication + Tracking + Master Data + Job Management

"""
Flask Main Application - With Role-Based Authentication, Analytics Tracking, Master Data, and Job Management
-----------------------------------------------------------------
Handles authentication, job management, resume operations, visitor/download tracking, and master data
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
    """Login user - automatically detects user type from database"""
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        hashed_password = hash_password(password)
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, first_name, last_name, email, phone, type
            FROM users
            WHERE username = ? AND password = ?
        """, (username, hashed_password))
        
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

# ==================== SECTORS CRUD ====================

@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """Get all sectors from database"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SectorID, SectorName, IsActive
            FROM Sectors 
            WHERE IsActive = 1
            ORDER BY SectorName
        """)
        
        sectors = []
        for row in cursor.fetchall():
            sectors.append({
                'SectorID': row[0],
                'SectorName': row[1],
                'IsActive': row[2]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': sectors
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_sectors: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sectors', methods=['POST'])
def create_sector():
    """Create new sector"""
    try:
        data = request.get_json()
        
        if not data.get('SectorName'):
            return jsonify({'success': False, 'message': 'Sector name is required'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Sectors (SectorName, IsActive, CreatedAt)
            VALUES (?, 1, GETDATE())
        """, (data['SectorName'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sector created successfully'}), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_sector: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sectors/<int:sector_id>', methods=['PUT'])
def update_sector(sector_id):
    """Update sector"""
    try:
        data = request.get_json()
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Sectors 
            SET SectorName = ?, UpdatedDate = GETDATE()
            WHERE SectorID = ?
        """, (data['SectorName'], sector_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sector updated successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in update_sector: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sectors/<int:sector_id>', methods=['DELETE'])
def delete_sector(sector_id):
    """Delete sector (soft delete)"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Sectors 
            SET IsActive = 0, UpdatedDate = GETDATE()
            WHERE SectorID = ?
        """, (sector_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sector deleted successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in delete_sector: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== COUNTRIES CRUD ====================

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get all countries"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT CountryID, CountryName, CountryCode, IsActive
            FROM Countries 
            WHERE IsActive = 1
            ORDER BY CountryName
        """)
        
        countries = []
        for row in cursor.fetchall():
            countries.append({
                'CountryID': row[0],
                'CountryName': row[1],
                'CountryCode': row[2],
                'IsActive': row[3]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': countries})
        
    except Exception as e:
        print(f"❌ ERROR in get_countries: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/countries', methods=['POST'])
def create_country():
    """Create new country"""
    try:
        data = request.get_json()
        
        if not data.get('CountryName'):
            return jsonify({'success': False, 'message': 'Country name is required'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Countries (CountryName, CountryCode, IsActive, CreatedAt)
            VALUES (?, ?, 1, GETDATE())
        """, (data['CountryName'], data.get('CountryCode', '')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Country created successfully'}), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_country: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/countries/<int:country_id>', methods=['PUT'])
def update_country(country_id):
    """Update country"""
    try:
        data = request.get_json()
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Countries 
            SET CountryName = ?, CountryCode = ?, UpdatedDate = GETDATE()
            WHERE CountryID = ?
        """, (data['CountryName'], data.get('CountryCode', ''), country_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Country updated successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in update_country: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/countries/<int:country_id>', methods=['DELETE'])
def delete_country(country_id):
    """Delete country (soft delete)"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Countries 
            SET IsActive = 0, UpdatedDate = GETDATE()
            WHERE CountryID = ?
        """, (country_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Country deleted successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in delete_country: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== STATES CRUD ====================

@app.route('/api/states', methods=['GET'])
def get_states():
    """Get all states or filter by country"""
    try:
        country_id = request.args.get('country_id')
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        if country_id:
            cursor.execute("""
                SELECT s.StateID, s.StateName, s.StateCode, s.CountryID, c.CountryName, s.IsActive
                FROM States s
                JOIN Countries c ON s.CountryID = c.CountryID
                WHERE s.IsActive = 1 AND s.CountryID = ?
                ORDER BY s.StateName
            """, (country_id,))
        else:
            cursor.execute("""
                SELECT s.StateID, s.StateName, s.StateCode, s.CountryID, c.CountryName, s.IsActive
                FROM States s
                JOIN Countries c ON s.CountryID = c.CountryID
                WHERE s.IsActive = 1
                ORDER BY c.CountryName, s.StateName
            """)
        
        states = []
        for row in cursor.fetchall():
            states.append({
                'StateID': row[0],
                'StateName': row[1],
                'StateCode': row[2],
                'CountryID': row[3],
                'CountryName': row[4],
                'IsActive': row[5]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': states})
        
    except Exception as e:
        print(f"❌ ERROR in get_states: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/states', methods=['POST'])
def create_state():
    """Create new state"""
    try:
        data = request.get_json()
        
        if not data.get('StateName') or not data.get('CountryID'):
            return jsonify({'success': False, 'message': 'State name and country are required'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO States (CountryID, StateName, StateCode, IsActive, CreatedAt)
            VALUES (?, ?, ?, 1, GETDATE())
        """, (data['CountryID'], data['StateName'], data.get('StateCode', '')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'State created successfully'}), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_state: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/states/<int:state_id>', methods=['PUT'])
def update_state(state_id):
    """Update state"""
    try:
        data = request.get_json()
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE States 
            SET CountryID = ?, StateName = ?, StateCode = ?, UpdatedDate = GETDATE()
            WHERE StateID = ?
        """, (data['CountryID'], data['StateName'], data.get('StateCode', ''), state_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'State updated successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in update_state: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/states/<int:state_id>', methods=['DELETE'])
def delete_state(state_id):
    """Delete state (soft delete)"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE States 
            SET IsActive = 0, UpdatedDate = GETDATE()
            WHERE StateID = ?
        """, (state_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'State deleted successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in delete_state: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== CITIES CRUD ====================

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get all cities or filter by state"""
    try:
        state_id = request.args.get('state_id')
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        if state_id:
            cursor.execute("""
                SELECT c.CityID, c.CityName, c.StateID, s.StateName, co.CountryID, co.CountryName, c.IsActive
                FROM Cities c
                JOIN States s ON c.StateID = s.StateID
                JOIN Countries co ON s.CountryID = co.CountryID
                WHERE c.IsActive = 1 AND c.StateID = ?
                ORDER BY c.CityName
            """, (state_id,))
        else:
            cursor.execute("""
                SELECT c.CityID, c.CityName, c.StateID, s.StateName, co.CountryID, co.CountryName, c.IsActive
                FROM Cities c
                JOIN States s ON c.StateID = s.StateID
                JOIN Countries co ON s.CountryID = co.CountryID
                WHERE c.IsActive = 1
                ORDER BY co.CountryName, s.StateName, c.CityName
            """)
        
        cities = []
        for row in cursor.fetchall():
            cities.append({
                'CityID': row[0],
                'CityName': row[1],
                'StateID': row[2],
                'StateName': row[3],
                'CountryID': row[4],
                'CountryName': row[5],
                'IsActive': row[6]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': cities})
        
    except Exception as e:
        print(f"❌ ERROR in get_cities: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cities', methods=['POST'])
def create_city():
    """Create new city"""
    try:
        data = request.get_json()
        
        if not data.get('CityName') or not data.get('StateID'):
            return jsonify({'success': False, 'message': 'City name and state are required'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Cities (StateID, CityName, IsActive, CreatedAt)
            VALUES (?, ?, 1, GETDATE())
        """, (data['StateID'], data['CityName']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'City created successfully'}), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_city: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cities/<int:city_id>', methods=['PUT'])
def update_city(city_id):
    """Update city"""
    try:
        data = request.get_json()
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Cities 
            SET StateID = ?, CityName = ?, UpdatedDate = GETDATE()
            WHERE CityID = ?
        """, (data['StateID'], data['CityName'], city_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'City updated successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in update_city: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cities/<int:city_id>', methods=['DELETE'])
def delete_city(city_id):
    """Delete city (soft delete)"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Cities 
            SET IsActive = 0, UpdatedDate = GETDATE()
            WHERE CityID = ?
        """, (city_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'City deleted successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in delete_city: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== COURSES CRUD ====================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT CourseID, CourseName, CourseType, Description, IsActive
            FROM Courses 
            WHERE IsActive = 1
            ORDER BY CourseName
        """)
        
        courses = []
        for row in cursor.fetchall():
            courses.append({
                'CourseID': row[0],
                'CourseName': row[1],
                'CourseType': row[2],
                'Description': row[3],
                'IsActive': row[4]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': courses})
        
    except Exception as e:
        print(f"❌ ERROR in get_courses: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/courses', methods=['POST'])
def create_course():
    """Create new course"""
    try:
        data = request.get_json()
        
        if not data.get('CourseName'):
            return jsonify({'success': False, 'message': 'Course name is required'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Courses (CourseName, CourseType, Description, IsActive, CreatedAt)
            VALUES (?, ?, ?, 1, GETDATE())
        """, (data['CourseName'], data.get('CourseType', ''), data.get('Description', '')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Course created successfully'}), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_course: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update course"""
    try:
        data = request.get_json()
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Courses 
            SET CourseName = ?, CourseType = ?, Description = ?, UpdatedDate = GETDATE()
            WHERE CourseID = ?
        """, (data['CourseName'], data.get('CourseType', ''), data.get('Description', ''), course_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Course updated successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in update_course: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete course (soft delete)"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Courses 
            SET IsActive = 0, UpdatedDate = GETDATE()
            WHERE CourseID = ?
        """, (course_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Course deleted successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in delete_course: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== JOB SKILLS MASTER CRUD ====================

@app.route('/api/job-skills-master', methods=['GET'])
def get_job_skills_master():
    """Get all skills from JobSkillsMaster"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SkillID, SkillName, Category, IsActive
            FROM JobSkillsMaster 
            WHERE IsActive = 1
            ORDER BY SkillName
        """)
        
        skills = []
        for row in cursor.fetchall():
            skills.append({
                'SkillID': row[0],
                'SkillName': row[1],
                'Category': row[2],
                'IsActive': row[3]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': skills})
        
    except Exception as e:
        print(f"❌ ERROR in get_job_skills_master: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/job-skills-master', methods=['POST'])
def create_job_skill_master():
    """Create new skill in JobSkillsMaster"""
    try:
        data = request.get_json()
        
        if not data.get('SkillName'):
            return jsonify({'success': False, 'message': 'Skill name is required'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO JobSkillsMaster (SkillName, Category, IsActive, CreatedAt)
            VALUES (?, ?, 1, GETDATE())
        """, (data['SkillName'], data.get('Category', '')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Skill created successfully'}), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_job_skill_master: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/job-skills-master/<int:skill_id>', methods=['PUT'])
def update_job_skill_master(skill_id):
    """Update skill in JobSkillsMaster"""
    try:
        data = request.get_json()
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE JobSkillsMaster 
            SET SkillName = ?, Category = ?
            WHERE SkillID = ?
        """, (data['SkillName'], data.get('Category', ''), skill_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Skill updated successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in update_job_skill_master: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/job-skills-master/<int:skill_id>', methods=['DELETE'])
def delete_job_skill_master(skill_id):
    """Delete skill from JobSkillsMaster (soft delete)"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE JobSkillsMaster 
            SET IsActive = 0
            WHERE SkillID = ?
        """, (skill_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Skill deleted successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in delete_job_skill_master: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== COMPANIES CRUD ====================

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get all companies"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT CompanyID, CompanyName, CreatedAt
            FROM Companies 
            ORDER BY CompanyName
        """)
        
        companies = []
        for row in cursor.fetchall():
            companies.append({
                'CompanyID': row[0],
                'CompanyName': row[1],
                'CreatedAt': str(row[2]) if row[2] else None
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': companies})
        
    except Exception as e:
        print(f"❌ ERROR in get_companies: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/companies', methods=['POST'])
def create_company():
    """Create new company"""
    try:
        data = request.get_json()
        
        if not data.get('CompanyName'):
            return jsonify({'success': False, 'message': 'Company name is required'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Companies (CompanyName, CreatedAt)
            VALUES (?, GETDATE())
        """, (data['CompanyName'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Company created successfully'}), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_company: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== JOB TYPES CRUD ====================

@app.route('/api/job-types', methods=['GET'])
def get_job_types():
    """Get all job types"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT JobTypeID, JobTypeName, IsActive
            FROM JobTypes 
            WHERE IsActive = 1
            ORDER BY JobTypeName
        """)
        
        job_types = []
        for row in cursor.fetchall():
            job_types.append({
                'JobTypeID': row[0],
                'JobTypeName': row[1],
                'IsActive': row[2]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': job_types})
        
    except Exception as e:
        print(f"❌ ERROR in get_job_types: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== JOB POSTINGS MANAGEMENT (USING Jobs TABLE) ====================

@app.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    """Get all job postings from Jobs table"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                j.JobID, j.JobTitle, c.CompanyName, j.JobDescription,
                j.ExperienceRequired, j.Package, jt.JobTypeName, co.CourseName,
                s.SectorName, cnt.CountryName, st.StateName, ct.CityName,
                j.CreatedAt, u.username as posted_by
            FROM Jobs j
            LEFT JOIN Companies c ON j.CompanyID = c.CompanyID
            LEFT JOIN JobTypes jt ON j.JobTypeID = jt.JobTypeID
            LEFT JOIN Courses co ON j.CourseID = co.CourseID
            LEFT JOIN Sectors s ON j.SectorID = s.SectorID
            LEFT JOIN Countries cnt ON j.CountryID = cnt.CountryID
            LEFT JOIN States st ON j.StateID = st.StateID
            LEFT JOIN Cities ct ON j.CityID = ct.CityID
            LEFT JOIN users u ON j.PostedByUserID = u.id
            WHERE j.IsActive = 1
            ORDER BY j.CreatedAt DESC
        """)
        
        jobs = []
        for row in cursor.fetchall():
            job_id = row[0]
            
            # Get skills for this job from JobSkills table
            cursor.execute("""
                SELECT jsm.SkillName
                FROM JobSkills js
                JOIN JobSkillsMaster jsm ON js.SkillID = jsm.SkillID
                WHERE js.JobID = ?
            """, (job_id,))
            
            skills = [s[0] for s in cursor.fetchall()]
            
            jobs.append({
                'id': job_id,
                'job_title': row[1],
                'company_name': row[2],
                'job_description': row[3],
                'experience_required': row[4],
                'package': row[5],
                'job_type': row[6],
                'education': row[7],
                'sector': row[8],
                'country': row[9],
                'state': row[10],
                'city': row[11],
                'created_at': str(row[12]) if row[12] else None,
                'posted_by': row[13],
                'skills_required': skills
            })
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'jobs': jobs, 'count': len(jobs)})
        
    except Exception as e:
        print(f"❌ ERROR in get_all_jobs: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_by_id(job_id):
    """Get single job posting by ID from Jobs table"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                j.JobID, j.JobTitle, c.CompanyName, j.JobDescription,
                j.ExperienceRequired, j.Package, jt.JobTypeName, co.CourseName,
                s.SectorName, cnt.CountryName, st.StateName, ct.CityName,
                j.CreatedAt, u.username as posted_by
            FROM Jobs j
            LEFT JOIN Companies c ON j.CompanyID = c.CompanyID
            LEFT JOIN JobTypes jt ON j.JobTypeID = jt.JobTypeID
            LEFT JOIN Courses co ON j.CourseID = co.CourseID
            LEFT JOIN Sectors s ON j.SectorID = s.SectorID
            LEFT JOIN Countries cnt ON j.CountryID = cnt.CountryID
            LEFT JOIN States st ON j.StateID = st.StateID
            LEFT JOIN Cities ct ON j.CityID = ct.CityID
            LEFT JOIN users u ON j.PostedByUserID = u.id
            WHERE j.JobID = ? AND j.IsActive = 1
        """, (job_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Job not found'}), 404
        
        # Get skills for this job
        cursor.execute("""
            SELECT jsm.SkillName
            FROM JobSkills js
            JOIN JobSkillsMaster jsm ON js.SkillID = jsm.SkillID
            WHERE js.JobID = ?
        """, (job_id,))
        
        skills = [s[0] for s in cursor.fetchall()]
        
        job = {
            'id': row[0],
            'job_title': row[1],
            'company_name': row[2],
            'job_description': row[3],
            'experience_required': row[4],
            'package': row[5],
            'job_type': row[6],
            'education': row[7],
            'sector': row[8],
            'country': row[9],
            'state': row[10],
            'city': row[11],
            'created_at': str(row[12]) if row[12] else None,
            'posted_by': row[13],
            'skills_required': skills
        }
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'job': job})
        
    except Exception as e:
        print(f"❌ ERROR in get_job_by_id: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job posting in Jobs table"""
    try:
        data = request.get_json()
        
        # TODO: Get user ID from session/token - using default for now
        user_id = data.get('user_id', 1)
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Get or create company
        cursor.execute("SELECT CompanyID FROM Companies WHERE CompanyName = ?", (data['company_name'],))
        company = cursor.fetchone()
        
        if company:
            company_id = company[0]
        else:
            cursor.execute("INSERT INTO Companies (CompanyName, CreatedAt) VALUES (?, GETDATE())", (data['company_name'],))
            conn.commit()
            cursor.execute("SELECT @@IDENTITY")
            company_id = cursor.fetchone()[0]
        
        # Get or create sector
        sector_id = None
        if data.get('sector'):
            cursor.execute("SELECT SectorID FROM Sectors WHERE SectorName = ?", (data['sector'],))
            sector = cursor.fetchone()
            if not sector:
                cursor.execute("INSERT INTO Sectors (SectorName, IsActive, CreatedAt) VALUES (?, 1, GETDATE())", (data['sector'],))
                conn.commit()
                cursor.execute("SELECT @@IDENTITY")
                sector_id = cursor.fetchone()[0]
            else:
                sector_id = sector[0]
        
        # Get or create course
        course_id = None
        if data.get('course'):
            cursor.execute("SELECT CourseID FROM Courses WHERE CourseName = ?", (data['course'],))
            course = cursor.fetchone()
            if not course:
                cursor.execute("INSERT INTO Courses (CourseName, IsActive, CreatedAt) VALUES (?, 1, GETDATE())", (data['course'],))
                conn.commit()
                cursor.execute("SELECT @@IDENTITY")
                course_id = cursor.fetchone()[0]
            else:
                course_id = course[0]
        
        # Get or create country
        country_id = None
        if data.get('country'):
            cursor.execute("SELECT CountryID FROM Countries WHERE CountryName = ?", (data['country'],))
            country = cursor.fetchone()
            if not country:
                cursor.execute("INSERT INTO Countries (CountryName, IsActive, CreatedAt) VALUES (?, 1, GETDATE())", (data['country'],))
                conn.commit()
                cursor.execute("SELECT @@IDENTITY")
                country_id = cursor.fetchone()[0]
            else:
                country_id = country[0]
        
        # Get or create state
        state_id = None
        if data.get('state') and country_id:
            cursor.execute("SELECT StateID FROM States WHERE StateName = ? AND CountryID = ?", (data['state'], country_id))
            state = cursor.fetchone()
            if not state:
                cursor.execute("INSERT INTO States (StateName, CountryID, IsActive, CreatedAt) VALUES (?, ?, 1, GETDATE())", (data['state'], country_id))
                conn.commit()
                cursor.execute("SELECT @@IDENTITY")
                state_id = cursor.fetchone()[0]
            else:
                state_id = state[0]
        
        # Get or create city
        city_id = None
        if data.get('city') and state_id:
            cursor.execute("SELECT CityID FROM Cities WHERE CityName = ? AND StateID = ?", (data['city'], state_id))
            city = cursor.fetchone()
            if not city:
                cursor.execute("INSERT INTO Cities (CityName, StateID, IsActive, CreatedAt) VALUES (?, ?, 1, GETDATE())", (data['city'], state_id))
                conn.commit()
                cursor.execute("SELECT @@IDENTITY")
                city_id = cursor.fetchone()[0]
            else:
                city_id = city[0]
        
        # Get or create job type
        job_type_id = None
        if data.get('job_type'):
            cursor.execute("SELECT JobTypeID FROM JobTypes WHERE JobTypeName = ?", (data['job_type'],))
            job_type = cursor.fetchone()
            if not job_type:
                cursor.execute("INSERT INTO JobTypes (JobTypeName, IsActive, CreatedAt) VALUES (?, 1, GETDATE())", (data['job_type'],))
                conn.commit()
                cursor.execute("SELECT @@IDENTITY")
                job_type_id = cursor.fetchone()[0]
            else:
                job_type_id = job_type[0]
        
        # Insert job posting into Jobs table
        cursor.execute("""
            INSERT INTO Jobs (
                JobTitle, CompanyID, JobDescription, SectorID, CourseID,
                CountryID, StateID, CityID, JobTypeID, ExperienceRequired,
                Package, PostedByUserID, IsActive, CreatedAt
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE())
        """, (
            data['job_title'],
            company_id,
            data['job_description'],
            sector_id,
            course_id,
            country_id,
            state_id,
            city_id,
            job_type_id,
            data['experience_required'],
            data['package'],
            user_id
        ))
        
        conn.commit()
        cursor.execute("SELECT @@IDENTITY")
        job_id = cursor.fetchone()[0]
        
        # Add skills to JobSkills table
        if data.get('skills_required'):
            for skill_name in data['skills_required']:
                # Get or create skill in JobSkillsMaster
                cursor.execute("SELECT SkillID FROM JobSkillsMaster WHERE SkillName = ?", (skill_name,))
                skill = cursor.fetchone()
                
                if skill:
                    skill_id = skill[0]
                else:
                    cursor.execute("INSERT INTO JobSkillsMaster (SkillName, IsActive, CreatedAt) VALUES (?, 1, GETDATE())", (skill_name,))
                    conn.commit()
                    cursor.execute("SELECT @@IDENTITY")
                    skill_id = cursor.fetchone()[0]
                
                # Link skill to job in JobSkills table
                cursor.execute("""
                    INSERT INTO JobSkills (JobID, SkillID, CreatedAt)
                    VALUES (?, ?, GETDATE())
                """, (job_id, skill_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Job created successfully: ID {job_id}")
        
        return jsonify({
            'success': True,
            'message': 'Job posting created successfully',
            'job_id': int(job_id)
        }), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_job: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update an existing job posting in Jobs table"""
    try:
        data = request.get_json()
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        # Check if job exists
        cursor.execute("SELECT JobID FROM Jobs WHERE JobID = ? AND IsActive = 1", (job_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Job not found'}), 404
        
        # Update job
        cursor.execute("""
            UPDATE Jobs 
            SET JobTitle = ?, JobDescription = ?, ExperienceRequired = ?, 
                Package = ?, UpdatedDate = GETDATE()
            WHERE JobID = ?
        """, (
            data.get('job_title'),
            data.get('job_description'),
            data.get('experience_required'),
            data.get('package'),
            job_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Job updated successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in update_job: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job posting from Jobs table (soft delete)"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT JobID FROM Jobs WHERE JobID = ? AND IsActive = 1", (job_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Job not found'}), 404
        
        cursor.execute("UPDATE Jobs SET IsActive = 0, UpdatedDate = GETDATE() WHERE JobID = ?", (job_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Job deleted successfully'})
        
    except Exception as e:
        print(f"❌ ERROR in delete_job: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== VISITOR & DOWNLOAD TRACKING ====================

@app.route('/api/visitor/increment', methods=['POST'])
def increment_visitor():
    """Increment visitor count"""
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT TOP 1 ResumeID, VisitorCount 
            FROM Resumes 
            ORDER BY UpdatedDate DESC
        """)
        
        result = cursor.fetchone()
        
        if result:
            resume_id = result[0]
            current_count = result[1] or 0
            
            cursor.execute("""
                UPDATE Resumes 
                SET VisitorCount = ?, UpdatedDate = GETDATE()
                WHERE ResumeID = ?
            """, (current_count + 1, resume_id))
            
            new_count = current_count + 1
        else:
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
        
        return jsonify({
            'success': True,
            'resume_id': int(resume_id),
            'visitor_count': new_count
        })
        
    except Exception as e:
        print(f"❌ ERROR in increment_visitor: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download/increment', methods=['POST'])
def increment_download():
    """Increment download count"""
    try:
        data = request.get_json()
        resume_id = data.get('resume_id')
        
        if not resume_id:
            return jsonify({'success': False, 'message': 'Resume ID is required'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DownloadCount 
            FROM Resumes 
            WHERE ResumeID = ?
        """, (resume_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Resume not found'}), 404
        
        current_count = result[0] or 0
        
        cursor.execute("""
            UPDATE Resumes 
            SET DownloadCount = ?, UpdatedDate = GETDATE()
            WHERE ResumeID = ?
        """, (current_count + 1, resume_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'resume_id': int(resume_id),
            'download_count': current_count + 1
        })
        
    except Exception as e:
        print(f"❌ ERROR in increment_download: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ANALYTICS ====================
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get total visitor and download counts"""
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
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== RESUME MANAGEMENT ====================

@app.route('/api/resumes', methods=['GET'])
def get_all_resumes():
    """Get all resumes"""
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
            return jsonify({'success': True, 'data': [], 'count': 0})
        
        result = []
        for resume in resumes:
            resume_id = resume[0]
            
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
            } if p else {'full_name': 'Unknown', 'email': 'No email', 'location': 'N/A'}
            
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
            
            cursor.execute("""
                SELECT SkillType, SkillName 
                FROM Skills 
                WHERE ResumeID = ?
            """, (resume_id,))
            skills = [{
                'skill_type': s[0],
                'skill_name': s[1]
            } for s in cursor.fetchall()]
            
            cursor.execute("""
                SELECT CertificationName 
                FROM Certifications 
                WHERE ResumeID = ?
            """, (resume_id,))
            certifications = [{
                'certification_name': c[0]
            } for c in cursor.fetchall()]
            
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
        
        return jsonify({'success': True, 'data': result, 'count': len(result)})
        
    except Exception as e:
        print(f"❌ ERROR in get_all_resumes: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/resume', methods=['POST'])
def create_resume():
    """Create a new resume"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Resumes (ResumeTitle, Status, VisitorCount, DownloadCount, CreatedDate, UpdatedDate) 
            VALUES (?, ?, 0, 0, GETDATE(), GETDATE())
        """, (data.get('resume_title', 'Untitled Resume'), 'Draft'))
        conn.commit()
        
        cursor.execute("SELECT @@IDENTITY")
        resume_id = cursor.fetchone()[0]
        
        if 'personal_info' in data:
            pi = data['personal_info']
            cursor.execute("""
                INSERT INTO PersonalInformation 
                (ResumeID, FullName, Email, PhoneNumber, DateOfBirth, Location, 
                LinkedInURL, GitHubURL, CareerObjective, CreatedDate) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (resume_id, pi.get('full_name'), pi.get('email'), 
                pi.get('phone_number'), pi.get('date_of_birth'), pi.get('location'),
                pi.get('linkedin_url'), pi.get('github_url'), pi.get('career_objective')))
        
        if 'work_experience' in data:
            for work in data['work_experience']:
                cursor.execute("""
                    INSERT INTO WorkExperience 
                    (ResumeID, CompanyName, JobRole, DateOfJoin, LastWorkingDate, Experience, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                """, (resume_id, work.get('company_name'), work.get('job_role'),
                    work.get('date_of_join'), work.get('last_working_date'), work.get('experience')))
        
        if 'education' in data:
            for edu in data['education']:
                cursor.execute("""
                    INSERT INTO Education 
                    (ResumeID, College, University, Course, Year, CGPA, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                """, (resume_id, edu.get('college'), edu.get('university'),
                    edu.get('course'), edu.get('year'), edu.get('cgpa')))
        
        if 'projects' in data:
            for proj in data['projects']:
                cursor.execute("""
                    INSERT INTO Projects 
                    (ResumeID, ProjectTitle, ProjectLink, Organization, Description, CreatedDate) 
                    VALUES (?, ?, ?, ?, ?, GETDATE())
                """, (resume_id, proj.get('project_title'), proj.get('project_link'),
                    proj.get('organization'), proj.get('description')))
        
        if 'skills' in data:
            for skill in data['skills']:
                cursor.execute("""
                    INSERT INTO Skills (ResumeID, SkillType, SkillName, CreatedDate) 
                    VALUES (?, ?, ?, GETDATE())
                """, (resume_id, skill.get('skill_type'), skill.get('skill_name')))
        
        if 'certifications' in data:
            for cert in data['certifications']:
                cursor.execute("""
                    INSERT INTO Certifications (ResumeID, CertificationName, CreatedDate) 
                    VALUES (?, ?, GETDATE())
                """, (resume_id, cert.get('certification_name')))
        
        if 'interests' in data:
            for interest in data['interests']:
                cursor.execute("""
                    INSERT INTO Interests (ResumeID, InterestName, CreatedDate) 
                    VALUES (?, ?, GETDATE())
                """, (resume_id, interest.get('interest_name')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Resume created successfully', 'resume_id': int(resume_id)}), 201
        
    except Exception as e:
        print(f"❌ ERROR in create_resume: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    """Run the application"""
    
    print("\n" + "="*50)
    print("Resume Builder API Server - COMPLETE")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("API base URL: http://localhost:5000/api")
    print("\nPress CTRL+C to stop the server")
    print("="*50 + "\n")
    
    try:
        Config.test_connection()
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)