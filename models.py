from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import session

# Create database instance
db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StatsUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_file = db.Column(db.String(255))  # Path to the uploaded image file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)
    
    # Get image URL (uploaded image or placeholder)
    @property
    def image_url(self):
        if self.image_file:
            return f"/static/uploads/categories/{self.image_file}"
        else:
            # Fallback to placeholder if no image uploaded
            color = hash(self.name) % 999999
            return f"https://placehold.co/500x500/{color:06x}/FFFFFF?text={self.name.replace(' ', '+')}"
            
    # Get translated name
    @property
    def translated_name(self):
        current_lang = session.get('language', 'en')
        if current_lang == 'en':
            return self.name
        
        # Lazy import to avoid circular imports
        from translation_helper import translate_text
        return translate_text(self.name, target_lang=current_lang)
    
    # Get translated description
    @property
    def translated_description(self):
        current_lang = session.get('language', 'en')
        if not self.description or current_lang == 'en':
            return self.description
        
        # Lazy import to avoid circular imports
        from translation_helper import translate_text
        return translate_text(self.description, target_lang=current_lang)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    is_hot = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    is_sale = db.Column(db.Boolean, default=False)
    is_trending = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(255))  # Path to the main uploaded image file
    affiliate_link = db.Column(db.String(500))  # Amazon affiliate link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    
    # Get image URL (uploaded image or placeholder)
    @property
    def image_url(self):
        if self.image_file:
            return f"/static/uploads/products/{self.image_file}"
        else:
            # Fallback to placeholder if no image uploaded
            color = hash(self.name) % 999999
            return f"https://placehold.co/500x500/{color:06x}/FFFFFF?text={self.name.replace(' ', '+')}"
            
    # Get translated name
    @property
    def translated_name(self):
        current_lang = session.get('language', 'en')
        if current_lang == 'en':
            return self.name
        
        # Lazy import to avoid circular imports
        from translation_helper import translate_text
        return translate_text(self.name, target_lang=current_lang)
    
    # Get translated description
    @property
    def translated_description(self):
        current_lang = session.get('language', 'en')
        if not self.description or current_lang == 'en':
            return self.description
        
        # Lazy import to avoid circular imports
        from translation_helper import translate_text
        return translate_text(self.description, target_lang=current_lang)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    button_text = db.Column(db.String(50))
    button_link = db.Column(db.String(200))
    image_file = db.Column(db.String(255))  # Path to the uploaded image file
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Get image URL (uploaded image or placeholder)
    @property
    def image_url(self):
        if self.image_file:
            return f"/static/uploads/banners/{self.image_file}"
        else:
            # Fallback to placeholder if no image uploaded
            color = hash(self.title) % 999999
            return f"https://placehold.co/1200x400/{color:06x}/FFFFFF?text={self.title.replace(' ', '+')}"
            
    # Get translated title
    @property
    def translated_title(self):
        current_lang = session.get('language', 'en')
        if current_lang == 'en':
            return self.title
        
        # Lazy import to avoid circular imports
        from translation_helper import translate_text
        return translate_text(self.title, target_lang=current_lang)
    
    # Get translated subtitle
    @property
    def translated_subtitle(self):
        current_lang = session.get('language', 'en')
        if not self.subtitle or current_lang == 'en':
            return self.subtitle
        
        # Lazy import to avoid circular imports
        from translation_helper import translate_text
        return translate_text(self.subtitle, target_lang=current_lang)
        
    # Get translated button text
    @property
    def translated_button_text(self):
        current_lang = session.get('language', 'en')
        if not self.button_text or current_lang == 'en':
            return self.button_text
        
        # Lazy import to avoid circular imports
        from translation_helper import translate_text
        return translate_text(self.button_text, target_lang=current_lang)

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(255), nullable=False)  # Path to the uploaded image file
    is_primary = db.Column(db.Boolean, default=False)  # Is this the primary image
    display_order = db.Column(db.Integer, default=0)  # Order in which to display images
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Get image URL
    @property
    def image_url(self):
        return f"/static/uploads/products/{self.image_file}"

class VisitorStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitor_ip = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    visitor_ip = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    product = db.relationship('Product', backref='views_data', lazy=True)
