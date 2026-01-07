"""
Database Configuration - Complete Version
----------------------------
Manages database connection using Windows Authentication
"""
import pyodbc

class Config:
    """Configuration class for database connection"""
    
    # Database Configuration
    DB_SERVER = 'POOJA\\SQLEXPRESS'  # Your SQL Server instance
    DB_NAME = 'Resume'
    
    # Connection string using Windows Authentication
    CONNECTION_STRING = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={DB_SERVER};'
        f'DATABASE={DB_NAME};'
        f'Trusted_Connection=yes;'
    )
    
    @staticmethod
    def get_db_connection():
        """
        Creates and returns a database connection
        
        Returns:
            pyodbc.Connection: Active database connection
        """
        try:
            connection = pyodbc.connect(Config.CONNECTION_STRING)
            print("✓ Database connected successfully")
            return connection
        except pyodbc.Error as e:
            print(f"❌ Database connection error: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Make sure SQL Server is running")
            print("2. Verify database 'Resume' exists")
            print("3. Check Windows Authentication is enabled")
            print("4. Try: services.msc > SQL Server (SQLEXPRESS) > Start")
            raise

    @staticmethod
    def test_connection():
        """Test database connection"""
        try:
            conn = Config.get_db_connection()
            cursor = conn.cursor()
            
            # Test query
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"✓ SQL Server version: {version[0][:80]}...")
            
            # Check if VisitorCount and DownloadCount columns exist
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Resumes' 
                AND COLUMN_NAME IN ('VisitorCount', 'DownloadCount')
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            if 'VisitorCount' in columns:
                print("✓ VisitorCount column exists")
            else:
                print("⚠️  VisitorCount column missing - run schema update")
            
            if 'DownloadCount' in columns:
                print("✓ DownloadCount column exists")
            else:
                print("⚠️  DownloadCount column missing - run schema update")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False


if __name__ == '__main__':
    """Test the connection when run directly"""
    print("\n" + "="*50)
    print("Testing Database Connection")
    print("="*50)
    Config.test_connection()
    print("="*50 + "\n")