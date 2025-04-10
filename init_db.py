from app import app, db
from models import Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    # Ma'lumotlar bazasi jadvallarini yaratish
    db.create_all()
    
    # Admin foydalanuvchini yaratish
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin foydalanuvchi yaratildi!")
    
    print("Ma'lumotlar bazasi muvaffaqiyatli yaratildi!")
