"""
Data Models and Validation - FIXED VERSION
---------------------------
Handles data validation and database operations
"""

from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

# ==========================================
# VALIDATION SCHEMAS
# ==========================================

class PersonalInfoSchema(Schema):
    """Validates personal information"""
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    phone_number = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    date_of_birth = fields.Str(required=True)
    location = fields.Str(required=True, validate=validate.Length(max=100))
    photo_path = fields.Str(allow_none=True)
    linkedin_url = fields.Str(allow_none=True)
    github_url = fields.Str(allow_none=True)
    career_objective = fields.Str(required=True)


class WorkExperienceSchema(Schema):
    """Validates work experience"""
    company_name = fields.Str(allow_none=True)
    job_role = fields.Str(allow_none=True)
    date_of_join = fields.Str(allow_none=True)
    last_working_date = fields.Str(allow_none=True)
    experience = fields.Str(allow_none=True)


class EducationSchema(Schema):
    """Validates education"""
    college = fields.Str(allow_none=True)
    university = fields.Str(allow_none=True)
    course = fields.Str(allow_none=True)
    year = fields.Int(allow_none=True)
    cgpa = fields.Str(allow_none=True)


class ProjectSchema(Schema):
    """Validates projects"""
    project_title = fields.Str(allow_none=True)
    project_link = fields.Str(allow_none=True)
    organization = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)


class SkillSchema(Schema):
    """Validates skills"""
    skill_type = fields.Str(required=True)
    skill_name = fields.Str(required=True)


class CertificationSchema(Schema):
    """Validates certifications"""
    certification_name = fields.Str(required=True)


class InterestSchema(Schema):
    """Validates hobbies/interests"""
    interest_name = fields.Str(required=True)


class ResumeSchema(Schema):
    """Main Resume Schema"""
    personal_info = fields.Nested(PersonalInfoSchema, required=True)
    work_experience = fields.List(fields.Nested(WorkExperienceSchema), required=False)
    education = fields.List(fields.Nested(EducationSchema), required=False)
    projects = fields.List(fields.Nested(ProjectSchema), required=False)
    skills = fields.List(fields.Nested(SkillSchema), required=False)
    certifications = fields.List(fields.Nested(CertificationSchema), required=False)
    interests = fields.List(fields.Nested(InterestSchema), required=False)
    resume_title = fields.Str(allow_none=True)
    signature = fields.Str(required=True)


# ==========================================
# DATABASE OPERATIONS
# ==========================================

class ResumeModel:
    """Handles all database operations for resumes"""
    
    def __init__(self, connection):
        """Initialize with database connection"""
        self.conn = connection
        self.cursor = connection.cursor()
    
    def create_resume(self, resume_data):
        """
        Saves complete resume to database
        
        Args:
            resume_data: Complete resume data from frontend
            
        Returns:
            dict: Success/error message with resume_id
        """
        try:
            # Validate data
            schema = ResumeSchema()
            validated_data = schema.load(resume_data)
            
            print("✓ Data validated successfully")
            
            # Set defaults for optional fields
            if 'work_experience' not in validated_data:
                validated_data['work_experience'] = []
            if 'education' not in validated_data:
                validated_data['education'] = []
            if 'projects' not in validated_data:
                validated_data['projects'] = []
            if 'skills' not in validated_data:
                validated_data['skills'] = []
            if 'certifications' not in validated_data:
                validated_data['certifications'] = []
            if 'interests' not in validated_data:
                validated_data['interests'] = []
            
            # Insert into Resumes table
            resume_title = validated_data.get('resume_title') or \
                          f"{validated_data['personal_info']['full_name']}'s Resume"
            
            self.cursor.execute("""
                INSERT INTO Resumes (ResumeTitle, Status, CreatedDate)
                OUTPUT INSERTED.ResumeID
                VALUES (?, 'Draft', GETDATE())
            """, (resume_title,))
            
            resume_id = self.cursor.fetchone()[0]
            print(f"✓ Resume created with ID: {resume_id}")
            
            # Insert Personal Information
            personal = validated_data['personal_info']
            self.cursor.execute("""
                INSERT INTO PersonalInformation 
                (ResumeID, FullName, Email, PhoneNumber, DateOfBirth, Location, 
                 PhotoPath, LinkedInURL, GitHubURL, CareerObjective, CreatedDate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                resume_id,
                personal['full_name'],
                personal['email'],
                personal['phone_number'],
                personal['date_of_birth'],
                personal['location'],
                personal.get('photo_path'),
                personal.get('linkedin_url'),
                personal.get('github_url'),
                personal['career_objective']
            ))
            print("✓ Personal info saved")
            
            # Insert Work Experience
            work_count = 0
            for work in validated_data.get('work_experience', []):
                if work.get('company_name') or work.get('job_role'):
                    self.cursor.execute("""
                        INSERT INTO WorkExperience 
                        (ResumeID, CompanyName, JobRole, DateOfJoin, 
                         LastWorkingDate, Experience, CreatedDate)
                        VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                    """, (
                        resume_id,
                        work.get('company_name'),
                        work.get('job_role'),
                        work.get('date_of_join'),
                        work.get('last_working_date'),
                        work.get('experience')
                    ))
                    work_count += 1
            print(f"✓ Saved {work_count} work experiences")
            
            # Insert Education
            edu_count = 0
            for edu in validated_data.get('education', []):
                if edu.get('college') or edu.get('course'):
                    self.cursor.execute("""
                        INSERT INTO Education 
                        (ResumeID, College, University, Course, Year, CGPA, CreatedDate)
                        VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                    """, (
                        resume_id,
                        edu.get('college'),
                        edu.get('university'),
                        edu.get('course'),
                        edu.get('year'),
                        edu.get('cgpa')
                    ))
                    edu_count += 1
            print(f"✓ Saved {edu_count} education entries")
            
            # Insert Projects
            proj_count = 0
            for project in validated_data.get('projects', []):
                if project.get('project_title'):
                    self.cursor.execute("""
                        INSERT INTO Projects 
                        (ResumeID, ProjectTitle, ProjectLink, Organization, 
                         Description, CreatedDate)
                        VALUES (?, ?, ?, ?, ?, GETDATE())
                    """, (
                        resume_id,
                        project.get('project_title'),
                        project.get('project_link'),
                        project.get('organization'),
                        project.get('description')
                    ))
                    proj_count += 1
            print(f"✓ Saved {proj_count} projects")
            
            # Insert Skills
            skill_count = 0
            for skill in validated_data.get('skills', []):
                self.cursor.execute("""
                    INSERT INTO Skills 
                    (ResumeID, SkillType, SkillName, CreatedDate)
                    VALUES (?, ?, ?, GETDATE())
                """, (
                    resume_id,
                    skill['skill_type'],
                    skill['skill_name']
                ))
                skill_count += 1
            print(f"✓ Saved {skill_count} skills")
            
            # Insert Certifications
            cert_count = 0
            for cert in validated_data.get('certifications', []):
                self.cursor.execute("""
                    INSERT INTO Certifications 
                    (ResumeID, CertificationName, CreatedDate)
                    VALUES (?, ?, GETDATE())
                """, (
                    resume_id,
                    cert['certification_name']
                ))
                cert_count += 1
            print(f"✓ Saved {cert_count} certifications")
            
            # Insert Interests
            interest_count = 0
            for interest in validated_data.get('interests', []):
                self.cursor.execute("""
                    INSERT INTO Interests 
                    (ResumeID, InterestName, CreatedDate)
                    VALUES (?, ?, GETDATE())
                """, (
                    resume_id,
                    interest['interest_name']
                ))
                interest_count += 1
            print(f"✓ Saved {interest_count} interests")
            
            # Commit all changes
            self.conn.commit()
            print("✓ All data committed to database")
            
            return {
                'success': True,
                'message': 'Resume created successfully',
                'resume_id': resume_id
            }
            
        except ValidationError as e:
            self.conn.rollback()
            print(f"❌ Validation error: {e.messages}")
            return {
                'success': False,
                'message': 'Validation error',
                'errors': e.messages
            }
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Database error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Database error: {str(e)}'
            }
    
    def get_resume(self, resume_id):
        """Retrieves complete resume from database"""
        try:
            # Get resume info
            self.cursor.execute("""
                SELECT ResumeID, ResumeTitle, Status, CreatedDate
                FROM Resumes
                WHERE ResumeID = ?
            """, (resume_id,))
            
            resume = self.cursor.fetchone()
            if not resume:
                return {'success': False, 'message': 'Resume not found'}
            
            # Get all related data
            self.cursor.execute("SELECT * FROM PersonalInformation WHERE ResumeID = ?", (resume_id,))
            personal_info = self.cursor.fetchone()
            
            self.cursor.execute("SELECT * FROM WorkExperience WHERE ResumeID = ?", (resume_id,))
            work_experience = self.cursor.fetchall()
            
            self.cursor.execute("SELECT * FROM Education WHERE ResumeID = ?", (resume_id,))
            education = self.cursor.fetchall()
            
            self.cursor.execute("SELECT * FROM Projects WHERE ResumeID = ?", (resume_id,))
            projects = self.cursor.fetchall()
            
            self.cursor.execute("SELECT * FROM Skills WHERE ResumeID = ?", (resume_id,))
            skills = self.cursor.fetchall()
            
            self.cursor.execute("SELECT * FROM Certifications WHERE ResumeID = ?", (resume_id,))
            certifications = self.cursor.fetchall()
            
            self.cursor.execute("SELECT * FROM Interests WHERE ResumeID = ?", (resume_id,))
            interests = self.cursor.fetchall()
            
            return {
                'success': True,
                'data': {
                    'resume': resume,
                    'personal_info': personal_info,
                    'work_experience': work_experience,
                    'education': education,
                    'projects': projects,
                    'skills': skills,
                    'certifications': certifications,
                    'interests': interests
                }
            }
            
        except Exception as e:
            print(f"❌ Error retrieving resume: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()