import os
import logging
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from models import db, Admin, StatsUser, Category, Product, Banner, VisitorStat, ProductView
from multi_image import save_main_image, save_additional_images, get_additional_images, delete_product_images, allowed_file

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure upload folders
UPLOAD_FOLDERS = {
    'product': 'static/uploads/products',
    'category': 'static/uploads/categories',
    'banner': 'static/uploads/banners'
}

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Limit file uploads to 5MB
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection
app.secret_key = os.environ.get('SESSION_SECRET', 'default_secret_key_for_development')

# Add the ProxyFix middleware
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database with app
db.init_app(app)
migrate = Migrate(app, db)

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    if Admin.query.count() == 0:
        admin = Admin(
            username="A",
            password_hash=generate_password_hash("a")
        )
        db.session.add(admin)
        db.session.commit()
        
    # Create stats user if not exists
    if StatsUser.query.count() == 0:
        stats_user = StatsUser(
            username="abdu",
            password_hash=generate_password_hash("123")
        )
        db.session.add(stats_user)
        db.session.commit()
    
    # Add demo data if no category exists
    if Category.query.count() == 0:
        # Create categories
        categories = [
            Category(name="Electronics", description="Gadgets and devices for everyday use"),
            Category(name="Clothing", description="Fashion items and accessories"),
            Category(name="Books", description="Physical and digital books")
        ]
        db.session.add_all(categories)
        db.session.commit()
        
        # Create products for each category
        electronics = [
            Product(name="Smartphone", description="High-end smartphone with latest features", price=999.99, stock=10, is_hot=True, category_id=1),
            Product(name="Laptop", description="Powerful laptop for work and gaming", price=1299.99, stock=5, is_trending=True, category_id=1),
            Product(name="Headphones", description="Wireless headphones with noise cancellation", price=199.99, stock=20, category_id=1)
        ]
        
        clothing = [
            Product(name="T-shirt", description="Cotton t-shirt with logo", price=19.99, stock=50, category_id=2),
            Product(name="Jeans", description="Classic blue jeans", price=49.99, stock=30, is_trending=True, category_id=2),
            Product(name="Sneakers", description="Comfortable sneakers for everyday wear", price=79.99, stock=15, is_hot=True, category_id=2)
        ]
        
        books = [
            Product(name="Fiction Bestseller", description="Popular fiction book", price=14.99, stock=25, category_id=3),
            Product(name="Cooking Book", description="Recipes for beginners", price=24.99, stock=8, category_id=3),
            Product(name="Self-help Guide", description="Tips for personal development", price=18.99, stock=12, is_hot=True, category_id=3)
        ]
        
        db.session.add_all(electronics + clothing + books)
        db.session.commit()
        
        # Create banners
        banners = [
            Banner(title="Summer Sale", subtitle="Up to 50% off on selected items", button_text="Shop Now", button_link="/categories", active=True),
            Banner(title="New Collection", subtitle="Check out our latest additions", button_text="Discover", button_link="/categories", active=True)
        ]
        
        db.session.add_all(banners)
        db.session.commit()

# Middleware for language detection
@app.before_request
def track_visitor():
    if request.endpoint and not request.endpoint.startswith('static'):
        date = datetime.utcnow().date()
        hour = datetime.utcnow().hour
        visitor_ip = request.remote_addr
        
        # Check if visitor already counted in this hour
        existing = VisitorStat.query.filter_by(
            visitor_ip=visitor_ip,
            date=date,
            hour=hour
        ).first()
        
        if not existing:
            visitor_stat = VisitorStat(
                visitor_ip=visitor_ip,
                date=date,
                hour=hour
            )
            db.session.add(visitor_stat)
            db.session.commit()

def track_product_view(product_id):
    """Track when a product is viewed"""
    # Get current date
    today = datetime.now().date()
    
    # Create or update product view stats
    product_view = ProductView.query.filter_by(
        product_id=product_id,
        view_date=today
    ).first()
    
    if product_view:
        product_view.view_count += 1
    else:
        product_view = ProductView(
            product_id=product_id,
            view_date=today,
            view_count=1
        )
        db.session.add(product_view)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error tracking product view: {str(e)}")

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Routes
@app.route('/')
def index():
    trending_products = Product.query.filter_by(is_trending=True).limit(6).all()
    hot_products = Product.query.filter_by(is_hot=True).limit(6).all()
    categories = Category.query.limit(6).all()
    banners = Banner.query.filter_by(active=True).all()
    
    # Get products ordered by creation date (newest first) for "New Arrivals"
    new_arrivals = Product.query.order_by(Product.created_at.desc()).limit(6).all()
    
    # Get popular products (those with the most views)
    popular_products = Product.query.order_by(Product.views.desc()).limit(6).all()
    
    return render_template('index.html', 
                           trending_products=trending_products, 
                           hot_products=hot_products,
                           categories=categories,
                           banners=banners,
                           new_arrivals=new_arrivals,
                           popular_products=popular_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Track product view
    track_product_view(product_id)

    # Get all images for this product
    product_images = []
    
    # First add the main image if it exists
    if product.image_file:
        product_images.append({
            'image_url': product.image_url,
            'is_primary': True
        })
    
    # Get additional images
    additional_images = get_additional_images(product.id)
    product_images.extend(additional_images)
    
    # If no images were found, add a placeholder
    if not product_images:
        color = hash(product.name) % 999999
        placeholder_url = f"https://placehold.co/500x500/{color:06x}/FFFFFF?text={product.name.replace(' ', '+')}"
        product_images.append({
            'image_url': placeholder_url,
            'is_primary': True
        })
    
    # Get wishlist product IDs
    wishlist_product_ids = session.get('wishlist', [])
    
    return render_template('product.html', 
                          product=product, 
                          product_images=product_images,
                          related_products=related_products,
                          wishlist_product_ids=wishlist_product_ids)

@app.route('/category/<int:category_id>')
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    
    return render_template('category.html', category=category, products=products)

@app.route('/categories')
def all_categories():
    categories = Category.query.all()
    return render_template('category.html', categories=categories, products=None)

@app.route('/wishlist')
def wishlist():
    wishlist_data = session.get('wishlist', [])
    wishlist_products = []
    
    if wishlist_data:
        wishlist_products = Product.query.filter(Product.id.in_(wishlist_data)).all()
    
    return render_template('wishlist.html', products=wishlist_products)

@app.route('/wishlist/add/<int:product_id>')
def add_to_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get current wishlist
    wishlist = session.get('wishlist', [])
    
    # Add product to wishlist if not already there
    if product_id not in wishlist:
        wishlist.append(product_id)
        session['wishlist'] = wishlist
        flash('Product added to wishlist!', 'success')
    else:
        flash('Product already in wishlist!', 'info')
    
    # Redirect back to product page
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/wishlist/remove/<int:product_id>')
def remove_from_wishlist(product_id):
    # Get current wishlist
    wishlist = session.get('wishlist', [])
    
    # Remove product from wishlist if present
    if product_id in wishlist:
        wishlist.remove(product_id)
        session['wishlist'] = wishlist
        flash('Product removed from wishlist!', 'success')
    else:
        flash('Product not in wishlist!', 'info')
    
    # Redirect back to previous page
    return redirect(request.referrer or url_for('wishlist'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid login credentials!', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    if 'admin_logged_in' in session:
        session.clear()  # Clear all session data including CSRF token
    
    return redirect(url_for('admin_login'))

# Admin decorator
def admin_required(view_func):
    def wrapped_view(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return view_func(*args, **kwargs)
    
    # Preserve function metadata
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Prepare stats dictionary for the template
    stats = {
        'product_count': Product.query.count(),
        'category_count': Category.query.count(),
        'banner_count': Banner.query.filter_by(active=True).count(),
        'visitor_count': VisitorStat.query.filter(VisitorStat.date == datetime.utcnow().date()).distinct(VisitorStat.visitor_ip).count()
    }
    
    # Get most viewed products
    popular_products = Product.query.order_by(Product.views.desc()).limit(5).all()
    
    # Get products with low stock (less than 5 items)
    low_stock_products = Product.query.filter(Product.stock > 0, Product.stock < 5).order_by(Product.stock.asc()).limit(5).all()
    
    # Get admin name
    admin = Admin.query.first()
    current_user_name = admin.username if admin else 'Administrator'
    
    return render_template('admin/dashboard.html', 
                           stats=stats,
                           popular_products=popular_products,
                           low_stock_products=low_stock_products,
                           current_user_name=current_user_name)

@app.route('/admin/products', methods=['GET', 'POST'])
@admin_required
def admin_products():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        category_id = int(request.form.get('category_id'))
        affiliate_link = request.form.get('affiliate_link', '')
        
        # Get checkbox values
        is_hot = bool(request.form.get('is_hot'))
        is_new = bool(request.form.get('is_new'))
        is_sale = bool(request.form.get('is_sale'))
        is_trending = bool(request.form.get('is_trending'))
        
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            affiliate_link=affiliate_link,
            is_hot=is_hot,
            is_new=is_new,
            is_sale=is_sale,
            is_trending=is_trending
        )
        
        # Save the product first to get an ID
        db.session.add(product)
        db.session.flush()  # Get the ID without committing
        
        # Handle main image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                filename = save_main_image(image_file, type='product')
                if filename:
                    product.image_file = filename
        
        # Handle additional images upload (always try to save 5 images by duplicating if needed)
        if 'additional_images' in request.files:
            additional_files = request.files.getlist('additional_images')
            if additional_files:
                # If we have at least one valid file, we'll create 5 images from it
                valid_files = [f for f in additional_files if f and allowed_file(f.filename)]
                if valid_files:
                    save_additional_images(valid_files, product.id, type='product')
        
        # Now commit the transaction
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    products = Product.query.all()
    categories = Category.query.all()
    
    # Get admin name
    admin = Admin.query.first()
    current_user_name = admin.username if admin else 'Administrator'
    
    return render_template('admin/products.html', 
                           products=products, 
                           categories=categories,
                           current_user_name=current_user_name)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', 0))
        product.stock = int(request.form.get('stock', 0))
        product.category_id = int(request.form.get('category_id'))
        product.is_hot = bool(request.form.get('is_hot'))
        product.is_new = bool(request.form.get('is_new'))
        product.is_sale = bool(request.form.get('is_sale'))
        product.is_trending = bool(request.form.get('is_trending'))
        product.affiliate_link = request.form.get('affiliate_link')
        
        # Handle main image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                # Delete old image if exists
                old_image = product.image_file
                if old_image:
                    old_image_path = os.path.join('static/uploads/products', old_image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Save new image
                filename = save_main_image(image_file, type='product')
                if filename:
                    product.image_file = filename
        
        # Handle main image deletion
        if 'delete_image' in request.form and product.image_file:
            image_path = os.path.join('static/uploads/products', product.image_file)
            if os.path.exists(image_path):
                os.remove(image_path)
            product.image_file = None
            
        # Handle additional images upload
        if 'additional_images' in request.files:
            additional_files = request.files.getlist('additional_images')
            # If the checkbox to replace all additional images is checked, delete existing ones
            if 'replace_additional_images' in request.form:
                # Delete all existing additional images first
                product_image_dir = "static/uploads/products"
                if os.path.exists(product_image_dir):
                    for filename in os.listdir(product_image_dir):
                        if filename.startswith(f"{product.id}_add_") and allowed_file(filename):
                            image_path = os.path.join(product_image_dir, filename)
                            if os.path.exists(image_path):
                                os.remove(image_path)
            
            # Now add the new additional images (will auto-generate 5 images if possible)
            if additional_files:
                # Filter to valid files
                valid_files = [f for f in additional_files if f and allowed_file(f.filename)]
                if valid_files:
                    save_additional_images(valid_files, product.id, type='product')
        
        # Handle additional images deletion if checkbox checked
        if 'delete_additional_images' in request.form:
            # Delete all additional images
            product_image_dir = "static/uploads/products"
            if os.path.exists(product_image_dir):
                for filename in os.listdir(product_image_dir):
                    if filename.startswith(f"{product.id}_add_") and allowed_file(filename):
                        image_path = os.path.join(product_image_dir, filename)
                        if os.path.exists(image_path):
                            os.remove(image_path)
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = Category.query.all()
    additional_images = get_additional_images(product_id)
    
    # Get admin name
    admin = Admin.query.first()
    current_user_name = admin.username if admin else 'Administrator'
    
    return render_template('admin/products.html', 
                           product=product, 
                           additional_images=additional_images,
                           categories=categories, 
                           edit_mode=True,
                           current_user_name=current_user_name)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Delete all product images (main and additional)
    delete_product_images(product_id, product.image_file)
    
    # Delete related product views
    ProductView.query.filter_by(product_id=product_id).delete()
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        category = Category(name=name, description=description)
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                filename = save_main_image(image_file, type='category')
                if filename:
                    category.image_file = filename
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    categories = Category.query.all()
    
    # Get admin name
    admin = Admin.query.first()
    current_user_name = admin.username if admin else 'Administrator'
    
    return render_template('admin/categories.html', 
                          categories=categories,
                          current_user_name=current_user_name)

@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                # Delete old image if exists
                old_image = category.image_file
                if old_image:
                    old_image_path = os.path.join('static/uploads/categories', old_image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Save new image
                filename = save_main_image(image_file, type='category')
                if filename:
                    category.image_file = filename
        
        # Handle image deletion
        if 'delete_image' in request.form and category.image_file:
            image_path = os.path.join('static/uploads/categories', category.image_file)
            if os.path.exists(image_path):
                os.remove(image_path)
            category.image_file = None
        
        db.session.commit()
        
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    # Get admin name
    admin = Admin.query.first()
    current_user_name = admin.username if admin else 'Administrator'
    
    return render_template('admin/categories.html', 
                         category=category, 
                         edit_mode=True,
                         current_user_name=current_user_name)

@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if Product.query.filter_by(category_id=category_id).first():
        flash('Cannot delete category with associated products!', 'danger')
        return redirect(url_for('admin_categories'))
    
    # Delete category image if exists
    if category.image_file:
        image_path = os.path.join('static/uploads/categories', category.image_file)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/banners', methods=['GET', 'POST'])
@admin_required
def admin_banners():
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        button_text = request.form.get('button_text')
        button_link = request.form.get('button_link')
        active = 'active' in request.form
        
        banner = Banner(
            title=title,
            subtitle=subtitle,
            button_text=button_text,
            button_link=button_link,
            active=active
        )
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                filename = save_main_image(image_file, type='banner')
                if filename:
                    banner.image_file = filename
        
        db.session.add(banner)
        db.session.commit()
        
        flash('Banner added successfully!', 'success')
        return redirect(url_for('admin_banners'))
    
    banners = Banner.query.all()
    
    # Get admin name
    admin = Admin.query.first()
    current_user_name = admin.username if admin else 'Administrator'
    
    return render_template('admin/banners.html', 
                          banners=banners,
                          current_user_name=current_user_name)

@app.route('/admin/banners/edit/<int:banner_id>', methods=['GET', 'POST'])
@admin_required
def edit_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    
    if request.method == 'POST':
        banner.title = request.form.get('title')
        banner.subtitle = request.form.get('subtitle')
        banner.button_text = request.form.get('button_text')
        banner.button_link = request.form.get('button_link')
        banner.active = 'active' in request.form
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                # Delete old image if exists
                old_image = banner.image_file
                if old_image:
                    old_image_path = os.path.join('static/uploads/banners', old_image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Save new image
                filename = save_main_image(image_file, type='banner')
                if filename:
                    banner.image_file = filename
        
        # Handle image deletion
        if 'delete_image' in request.form and banner.image_file:
            image_path = os.path.join('static/uploads/banners', banner.image_file)
            if os.path.exists(image_path):
                os.remove(image_path)
            banner.image_file = None
        
        db.session.commit()
        
        flash('Banner updated successfully!', 'success')
        return redirect(url_for('admin_banners'))
    
    # Get admin name
    admin = Admin.query.first()
    current_user_name = admin.username if admin else 'Administrator'
    
    return render_template('admin/banners.html', 
                         banner=banner, 
                         edit_mode=True,
                         current_user_name=current_user_name)

@app.route('/admin/banners/delete/<int:banner_id>', methods=['POST'])
@admin_required
def delete_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    
    # Delete banner image if exists
    if banner.image_file:
        image_path = os.path.join('static/uploads/banners', banner.image_file)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(banner)
    db.session.commit()
    
    flash('Banner deleted successfully!', 'success')
    return redirect(url_for('admin_banners'))

# Stats routes
@app.route('/stats/login', methods=['GET', 'POST'])
def stats_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        stats_user = StatsUser.query.filter_by(username=username).first()
        
        if stats_user and check_password_hash(stats_user.password_hash, password):
            session['stats_logged_in'] = True
            return redirect(url_for('stats_dashboard'))
        else:
            flash('Invalid login credentials!', 'danger')
    
    return render_template('stats/login.html')

@app.route('/stats/logout')
def stats_logout():
    if 'stats_logged_in' in session:
        session.clear()  # Clear all session data including CSRF token
    
    return redirect(url_for('stats_login'))

# Stats decorator
def stats_required(view_func):
    def wrapped_view(*args, **kwargs):
        if not session.get('stats_logged_in'):
            return redirect(url_for('stats_login'))
        return view_func(*args, **kwargs)
    
    # Preserve function metadata
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

@app.route('/stats')
@stats_required
def stats_dashboard():
    # Count total visitors
    total_visitors = VisitorStat.query.count()
    
    # Count today's visitors
    today = datetime.utcnow().date()
    today_visitors = VisitorStat.query.filter_by(date=today).count()
    
    # Count total product views
    total_views = ProductView.query.count()
    
    # Get last hour visitors
    current_hour = datetime.utcnow().hour
    last_hour_visitors = VisitorStat.query.filter_by(
        date=today,
        hour=current_hour
    ).count()
    
    # Get last 6 hours visitors
    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    last_6h_visitors = VisitorStat.query.filter(
        VisitorStat.date >= six_hours_ago.date(),
        db.or_(
            db.and_(VisitorStat.date > six_hours_ago.date()),
            db.and_(
                VisitorStat.date == six_hours_ago.date(),
                VisitorStat.hour >= six_hours_ago.hour
            )
        )
    ).count()
    
    # Get last 24 hours visitors
    yesterday = today - timedelta(days=1)
    last_24h_visitors = VisitorStat.query.filter(
        db.or_(
            VisitorStat.date == today,
            VisitorStat.date == yesterday
        )
    ).count()
    
    # Get most viewed products
    most_viewed_products = Product.query.order_by(Product.views.desc()).limit(5).all()
    
    # Get most popular categories (by products viewed)
    most_popular_categories = db.session.query(
        Category,
        db.func.count(ProductView.id).label('views_count')
    ).join(Product, Product.category_id == Category.id)\
     .join(ProductView, ProductView.product_id == Product.id)\
     .group_by(Category.id)\
     .order_by(db.desc('views_count'))\
     .limit(5).all()
    
    return render_template('stats/dashboard.html',
                           total_visitors=total_visitors,
                           today_visitors=today_visitors,
                           total_views=total_views,
                           last_hour_visitors=last_hour_visitors,
                           last_6h_visitors=last_6h_visitors,
                           last_24h_visitors=last_24h_visitors,
                           most_viewed_products=most_viewed_products,
                           most_popular_categories=most_popular_categories)

# API routes for stats dashboard
@app.route('/api/stats/visitors')
@stats_required
def stats_visitors_api():
    days = int(request.args.get('days', 7))
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Query visitors per day
    daily_stats = db.session.query(
        VisitorStat.date,
        db.func.count(VisitorStat.id).label('count')
    ).filter(VisitorStat.date.between(start_date, end_date))\
     .group_by(VisitorStat.date)\
     .order_by(VisitorStat.date).all()
    
    # Prepare data for chart
    dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    counts = [0] * days
    
    for stat in daily_stats:
        day_index = (stat.date - start_date).days
        if 0 <= day_index < days:
            counts[day_index] = stat.count
    
    return jsonify({
        'labels': dates,
        'data': counts
    })

@app.route('/api/stats/hourly')
@stats_required
def stats_hourly_api():
    time_span = request.args.get('span', '24h')
    
    # Determine time range based on span
    now = datetime.utcnow()
    if time_span == '1h':
        hours_back = 1
    elif time_span == '6h':
        hours_back = 6
    elif time_span == '12h':
        hours_back = 12
    else:  # 24h
        hours_back = 24
    
    # Create the hourly intervals
    hourly_data = [0] * hours_back
    hourly_labels = []
    
    for i in range(hours_back):
        hour = (now.hour - i) % 24
        hourly_labels.insert(0, f"{hour}:00")
        
        # Query data for this hour
        current_date = now.date()
        if hour > now.hour:
            # Previous day
            current_date = current_date - timedelta(days=1)
        
        count = VisitorStat.query.filter_by(
            date=current_date,
            hour=hour
        ).count()
        
        hourly_data[hours_back - i - 1] = count
    
    return jsonify({
        'labels': hourly_labels,
        'data': hourly_data
    })

@app.route('/api/stats/products')
@stats_required
def stats_products_api():
    # Get most viewed products
    most_viewed_products = db.session.query(
        Product.name,
        db.func.count(ProductView.id).label('views_count')
    ).join(ProductView, ProductView.product_id == Product.id)\
     .group_by(Product.id)\
     .order_by(db.desc('views_count'))\
     .limit(5).all()
    
    return jsonify({
        'labels': [p.name for p in most_viewed_products],
        'data': [p.views_count for p in most_viewed_products]
    })

@app.route('/api/stats/categories')
@stats_required
def stats_categories_api():
    # Get most popular categories
    most_popular_categories = db.session.query(
        Category.name,
        db.func.count(ProductView.id).label('views_count')
    ).join(Product, Product.category_id == Category.id)\
     .join(ProductView, ProductView.product_id == Product.id)\
     .group_by(Category.id)\
     .order_by(db.desc('views_count'))\
     .limit(5).all()
    
    return jsonify({
        'labels': [c.name for c in most_popular_categories],
        'data': [c.views_count for c in most_popular_categories]
    })

@app.route('/change-language')
def change_language():
    lang = request.args.get('lang', 'en')
    session['language'] = lang
    
    # Get referer URL or default to home page
    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)