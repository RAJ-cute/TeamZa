import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///hr_platform.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

def from_json(value):
    """Custom Jinja2 filter to parse JSON strings"""
    try:
        import json
        return json.loads(value) if value else []
    except (json.JSONDecodeError, TypeError, ValueError):
        return []

# Register the filter after app initialization
app.jinja_env.filters['from_json'] = from_json

with app.app_context():
    # Import models first
    import models  # noqa: F401
    
    # Ensure clean database creation
    try:
        db.drop_all()
        print("Dropped all existing tables")
    except Exception as e:
        print(f"Drop tables warning: {e}")
    
    # Create all tables with proper schema
    db.create_all()
    print("Database tables created successfully!")
    
    # Verify the Employee table has the correct columns
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    employee_columns = [col['name'] for col in inspector.get_columns('employee')]
    print(f"Employee table columns: {employee_columns}")

# Import routes after database is ready
import routes  # noqa: F401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
