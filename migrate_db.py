import os
import sys
from sqlalchemy import create_engine, text, Table, Column, Integer, String, Boolean, DateTime, ForeignKey, MetaData
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from datetime import datetime

def migrate_database():
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("Error: DATABASE_URL environment variable not set.")
            sys.exit(1)
            
        # Create engine
        engine = create_engine(database_url)
        
        # Try to connect to check if database exists
        try:
            connection = engine.connect()
            print("Successfully connected to the database.")
            
            # Create product_image table if it doesn't exist
            metadata = MetaData()
            
            # Check if product_image table already exists
            check_table_sql = text("SELECT table_name FROM information_schema.tables WHERE table_name='product_image'")
            result = connection.execute(check_table_sql)
            table_exists = False
            for row in result:
                table_exists = True
                break
            
            if table_exists:
                print("Table 'product_image' already exists.")
            else:
                # Create product_image table
                product_image = Table(
                    'product_image',
                    metadata,
                    Column('id', Integer, primary_key=True),
                    Column('image_file', String(255), nullable=False),
                    Column('is_primary', Boolean, default=False),
                    Column('display_order', Integer, default=0),
                    Column('created_at', DateTime, default=datetime.utcnow),
                    Column('product_id', Integer, ForeignKey('product.id'), nullable=False)
                )
                
                metadata.create_all(engine)
                print("Successfully created 'product_image' table.")
            
            connection.close()
            
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")
            sys.exit(1)
            
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()