import os
import uuid
from werkzeug.utils import secure_filename

# Настройки для загрузки файлов
UPLOAD_FOLDERS = {
    'product': 'static/uploads/products',
    'category': 'static/uploads/categories',
    'banner': 'static/uploads/banners'
}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.lower().split('.')[-1] in ALLOWED_EXTENSIONS

def save_image(file, type='product'):
    """
    Сохраняет загруженное изображение в соответствующую директорию.
    
    Args:
        file: Объект загруженного файла
        type: Тип изображения (product, category, banner)
        
    Returns:
        Имя сохраненного файла или None, если ошибка
    """
    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла
        filename = secure_filename(file.filename)
        ext = filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Определяем корректную директорию для загрузки
        upload_folder = UPLOAD_FOLDERS.get(type, UPLOAD_FOLDERS['product'])
        
        # Создаем директорию, если ее нет
        os.makedirs(upload_folder, exist_ok=True)
        
        # Сохраняем файл
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def save_multiple_images(files, product_id=None, type='product'):
    """
    Сохраняет несколько загруженных изображений в соответствующую директорию.
    
    Args:
        files: Список объектов загруженных файлов
        product_id: ID продукта (для связи дополнительных изображений с продуктом)
        type: Тип изображения (product, category, banner)
        
    Returns:
        Список имен сохраненных файлов
    """
    saved_files = []
    
    for i, file in enumerate(files):
        if file and allowed_file(file.filename):
            # Генерируем уникальное имя файла с ID продукта, если он предоставлен
            if product_id:
                filename = secure_filename(file.filename)
                ext = filename.split('.')[-1]
                unique_filename = f"{product_id}_{i+1}_{uuid.uuid4().hex}.{ext}"
                
                # Определяем корректную директорию для загрузки
                upload_folder = UPLOAD_FOLDERS.get(type, UPLOAD_FOLDERS['product'])
                
                # Создаем директорию, если ее нет
                os.makedirs(upload_folder, exist_ok=True)
                
                # Сохраняем файл
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                
                saved_files.append(unique_filename)
            else:
                # Если ID продукта не указан, используем стандартный метод
                filename = save_image(file, type)
                if filename:
                    saved_files.append(filename)
    
    return saved_files
