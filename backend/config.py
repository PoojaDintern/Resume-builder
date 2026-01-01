"""
Database Configuration - FIXED VERSION
----------------------------
Manages database connection using Windows Authentication
"""
import pyodbc

class Config:
    """Configuration class for database connection"""
    
    # Database Configuration
    DB_SERVER = 'POOJA\\SQLEXPRESS'  # Your SQL Server instance
    DB_NAME = 'resume_builder'
    
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
            print("2. Verify database 'resume_builder' exists")
            print("3. Check Windows Authentication is enabled")
            print("4. Try: services.msc > SQL Server (SQLEXPRESS) > Start")
            raise

    @staticmethod
    def test_connection():
        """Test database connection"""
        try:
            conn = Config.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"✓ SQL Server version: {version[0][:50]}...")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False


if __name__ == '__main__':
    """Test the connection when run directly"""
    print("Testing database connection...")
    Config.test_connection()