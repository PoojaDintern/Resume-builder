"""
API Routes - FIXED VERSION
--------------------
Defines API endpoints for frontend-backend communication
"""

from flask import Blueprint, request, jsonify
from config import Config
from model import ResumeModel  # Make sure file is named models.py not model.py
import base64
import os
import traceback

# Create Blueprint
api = Blueprint('api', __name__)


@api.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    URL: GET http://localhost:5000/api/health
    """
    try:
        # Test database connection
        conn = Config.get_db_connection()
        conn.close()
        return jsonify({
            'status': 'ok',
            'message': 'API and Database are running',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Database connection failed',
            'error': str(e)
        }), 500


@api.route('/resume', methods=['POST', 'OPTIONS'])
def create_resume():
    """
    Create new resume
    URL: POST http://localhost:5000/api/resume
    """
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        print("\n" + "="*50)
        print("RECEIVED RESUME DATA")
        print("="*50)
        print(f"Personal Info: {data.get('personal_info', {}).get('full_name', 'N/A')}")
        print(f"Work Experience: {len(data.get('work_experience', []))} entries")
        print(f"Education: {len(data.get('education', []))} entries")
        print(f"Projects: {len(data.get('projects', []))} entries")
        print(f"Skills: {len(data.get('skills', []))} entries")
        print(f"Certifications: {len(data.get('certifications', []))} entries")
        print(f"Interests: {len(data.get('interests', []))} entries")
        print("="*50 + "\n")
        
        # Handle photo if present
        if 'personal_info' in data:
            photo_base64 = data['personal_info'].get('photo_base64')
            
            if photo_base64:
                try:
                    # Extract base64 data
                    if ',' in photo_base64:
                        photo_base64 = photo_base64.split(',')[1]
                    
                    # Create uploads directory
                    upload_dir = 'uploads/photos'
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate filename
                    import uuid
                    filename = f"{uuid.uuid4()}.png"
                    filepath = os.path.join(upload_dir, filename)
                    
                    # Save photo
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(photo_base64))
                    
                    data['personal_info']['photo_path'] = filepath
                    print(f"✓ Photo saved: {filepath}")
                    
                except Exception as e:
                    print(f"⚠ Photo save error: {str(e)}")
                    data['personal_info']['photo_path'] = None
                
                # Remove base64 data
                if 'photo_base64' in data['personal_info']:
                    del data['personal_info']['photo_base64']
        
        # Connect to database
        conn = Config.get_db_connection()
        resume_model = ResumeModel(conn)
        
        # Save resume
        result = resume_model.create_resume(data)
        
        # Close connection
        resume_model.close()
        
        # Return response
        if result['success']:
            print(f"\n✓ SUCCESS: Resume saved with ID {result['resume_id']}\n")
            return jsonify(result), 201
        else:
            print(f"\n❌ ERROR: {result.get('message')}\n")
            return jsonify(result), 400
            
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"\n❌ SERVER ERROR:\n{error_trace}\n")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'trace': error_trace
        }), 500


@api.route('/resume/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    """
    Get resume by ID
    URL: GET http://localhost:5000/api/resume/1
    """
    try:
        conn = Config.get_db_connection()
        resume_model = ResumeModel(conn)
        
        result = resume_model.get_resume(resume_id)
        
        resume_model.close()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@api.route('/resumes', methods=['GET'])
def list_resumes():
    """
    List all resumes
    URL: GET http://localhost:5000/api/resumes
    """
    try:
        conn = Config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.ResumeID, r.ResumeTitle, r.Status, r.CreatedDate,
                   p.FullName, p.Email
            FROM Resumes r
            LEFT JOIN PersonalInformation p ON r.ResumeID = p.ResumeID
            ORDER BY r.CreatedDate DESC
        """)
        
        resumes = []
        for row in cursor.fetchall():
            resumes.append({
                'resume_id': row[0],
                'title': row[1],
                'status': row[2],
                'created_date': str(row[3]),
                'full_name': row[4],
                'email': row[5]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(resumes),
            'data': resumes
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404


@api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


