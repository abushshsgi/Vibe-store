import os
import uuid
from werkzeug.utils import secure_filename

# Upload folder configuration
UPLOAD_FOLDERS = {
    'product': 'static/uploads/products',
    'category': 'static/uploads/categories',
    'banner': 'static/uploads/banners'
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
MAX_IMAGES_PER_PRODUCT = 5

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder(folder_type):
    """Make sure the upload folder exists"""
    folder = UPLOAD_FOLDERS.get(folder_type, UPLOAD_FOLDERS['product'])
    os.makedirs(folder, exist_ok=True)
    return folder

def save_main_image(file, type='product'):
    """Save a single main image file"""
    if not file or not allowed_file(file.filename):
        return None
        
    # Generate unique filename
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"main_{uuid.uuid4().hex}.{ext}"
    
    # Save the file
    folder = ensure_upload_folder(type)
    file_path = os.path.join(folder, unique_filename)
    file.save(file_path)
    
    return unique_filename

def save_additional_images(files, product_id, type='product'):
    """Save multiple additional image files for a product"""
    if not files or not product_id:
        return []
        
    saved_filenames = []
    folder = ensure_upload_folder(type)
    
    # Limit to maximum number of additional images
    valid_files = [f for f in files if f and allowed_file(f.filename)]
    
    # If we need exactly 5 images but don't have enough, duplicate the files we have
    if len(valid_files) < MAX_IMAGES_PER_PRODUCT:
        # Calculate how many duplicates we need for each file to reach 5 total
        original_count = len(valid_files)
        if original_count > 0:  # Avoid division by zero
            files_needed = MAX_IMAGES_PER_PRODUCT - original_count
            extra_files = []
            
            # Duplicate files cyclically until we reach 5
            for i in range(files_needed):
                extra_files.append(valid_files[i % original_count])
            
            valid_files.extend(extra_files)
    
    # Limit to maximum number
    valid_files = valid_files[:MAX_IMAGES_PER_PRODUCT]
    
    # Save each file with a unique name that includes the product ID
    for i, file in enumerate(valid_files):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{product_id}_add_{i+1}_{uuid.uuid4().hex}.{ext}"
        
        file_path = os.path.join(folder, unique_filename)
        file.save(file_path)
        saved_filenames.append(unique_filename)
    
    return saved_filenames

def delete_product_images(product_id, main_image=None, type='product'):
    """Delete all images associated with a product"""
    folder = ensure_upload_folder(type)
    
    # Delete main image if provided
    if main_image:
        main_image_path = os.path.join(folder, main_image)
        if os.path.exists(main_image_path):
            os.remove(main_image_path)
    
    # Delete all additional images
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename.startswith(f"{product_id}_add_") and allowed_file(filename):
                image_path = os.path.join(folder, filename)
                if os.path.exists(image_path):
                    os.remove(image_path)

def get_additional_images(product_id, type='product'):
    """Get all additional images for a product"""
    folder = ensure_upload_folder(type)
    additional_images = []
    
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename.startswith(f"{product_id}_add_") and allowed_file(filename):
                image_url = f"/static/uploads/products/{filename}"
                additional_images.append({
                    'filename': filename,
                    'image_url': image_url
                })
    
    # Sort images by their order number (extracted from filename)
    additional_images.sort(key=lambda x: int(x['filename'].split('_')[2]))
    
    return additional_images