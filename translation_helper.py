import logging
from googletrans import Translator
from flask import session

# Initialize the translator
translator = Translator()

# Dictionary to cache translations to reduce API calls
translation_cache = {}

def translate_text(text, target_lang='en', source_lang=None):
    """
    Translate text to the target language.
    
    Args:
        text (str): Text to translate
        target_lang (str): Target language code (e.g. 'fr', 'es', 'ru')
        source_lang (str, optional): Source language code, auto-detected if None
        
    Returns:
        str: Translated text or original text if translation fails
    """
    if not text:
        return text
    
    # Check for None or empty text
    if text is None:
        return ""
        
    # Make sure text is a string
    if not isinstance(text, str):
        text = str(text)
    
    if target_lang == 'en' or target_lang is None:
        # No need to translate if target is English (our base language)
        return text
    
    # Create a cache key
    cache_key = f"{text}:{source_lang}:{target_lang}"
    
    # Check if translation is already in cache
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    try:
        result = translator.translate(text, dest=target_lang, src=source_lang)
        translated_text = result.text
        
        # Cache the result for future use
        translation_cache[cache_key] = translated_text
        
        return translated_text
    except Exception as e:
        logging.error(f"Translation error: {e}")
        # Return original text if translation fails
        return text

def get_translated_field(obj, field_name):
    """
    Get a translated field value from an object (Product or Category).
    
    Args:
        obj: The object containing the field
        field_name (str): Name of the field to translate
        
    Returns:
        str: Translated field value or original value if translation fails
    """
    current_lang = session.get('language', 'en')
    
    # Get the original field value
    original_value = getattr(obj, field_name, '')
    
    # Check for None value to avoid translation error
    if original_value is None:
        return ''
    
    # No need to translate if language is English
    if current_lang == 'en':
        return original_value
    
    return translate_text(original_value, target_lang=current_lang)