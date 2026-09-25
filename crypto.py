# crypto.py - Encryption and Decryption Functions (Updated with RSA)

import random
import math
import json

# Import RSA functions

# Add these frequency tables at the top of crypto.py
ENGLISH_FREQ = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
    'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
    'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
    'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29,
    'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
}

FRENCH_FREQ = {
    'E': 14.72, 'A': 7.64, 'S': 7.93, 'I': 7.53, 'T': 7.24,
    'N': 7.10, 'R': 6.55, 'U': 6.31, 'L': 5.46, 'O': 5.38,
    'D': 3.67, 'C': 3.26, 'P': 3.03, 'M': 2.97, 'V': 1.63,
    'Q': 1.36, 'F': 1.06, 'B': 1.01, 'G': 0.87, 'H': 0.74,
    'J': 0.61, 'X': 0.39, 'Y': 0.31, 'Z': 0.21, 'W': 0.11, 'K': 0.05
}

ARABIC_FREQ = {
    'ا': 12.81, 'ل': 9.98, 'ي': 8.90, 'م': 7.49, 'و': 7.16,
    'ن': 6.71, 'ر': 5.91, 'ت': 5.80, 'ب': 4.88, 'ع': 4.57,
    'ه': 3.95, 'ق': 3.26, 'د': 3.18, 'س': 2.89, 'ف': 2.73,
    'ك': 2.57, 'ج': 2.02, 'ح': 1.85, 'خ': 1.51, 'ص': 1.39,
    'ش': 1.38, 'ط': 1.20, 'ز': 1.09, 'ض': 0.98, 'ث': 0.93,
    'غ': 0.89, 'ظ': 0.47, 'ذ': 0.34
}

LANGUAGE_FREQ = {
    'english': ENGLISH_FREQ,
    'french': FRENCH_FREQ,
    'arabic': ARABIC_FREQ
}

def calculate_chi_squared(text, freq_table):
    """Calculate chi-squared statistic for text against expected frequency"""
    if not text:
        return float('inf')
    
    # Count letter frequencies in text
    letter_count = {}
    total = 0
    
    for char in text.upper():
        if char in freq_table:
            letter_count[char] = letter_count.get(char, 0) + 1
            total += 1
    
    if total == 0:
        return float('inf')
    
    # Calculate chi-squared
    chi_squared = 0
    for letter in freq_table:
        expected = (freq_table[letter] / 100) * total
        observed = letter_count.get(letter, 0)
        if expected > 0:
            chi_squared += ((observed - expected) ** 2) / expected
    
    return chi_squared

def auto_decrypt_caesar(ciphertext, language='english'):
    """
    Automatically decrypt Caesar cipher using frequency analysis
    Returns: (decrypted_text, key, confidence_score)
    """
    if language not in LANGUAGE_FREQ:
        language = 'english'
    
    freq_table = LANGUAGE_FREQ[language]
    best_score = float('inf')
    best_key = 0
    best_plaintext = ""
    
    # Try all 26 possible shifts
    for shift in range(26):
        plaintext = caesar_encrypt(ciphertext, -shift)
        score = calculate_chi_squared(plaintext, freq_table)
        
        if score < best_score:
            best_score = score
            best_key = shift
            best_plaintext = plaintext
    
    # Calculate confidence (inverse of chi-squared, normalized)
    # Lower chi-squared = better match = higher confidence
    confidence = max(0, min(100, 100 - (best_score / 10)))
    
    return best_plaintext, best_key, confidence

def detect_language(text):
    """Detect the most likely language of the text"""
    best_lang = 'english'
    best_score = float('inf')
    
    for lang, freq_table in LANGUAGE_FREQ.items():
        score = calculate_chi_squared(text, freq_table)
        if score < best_score:
            best_score = score
            best_lang = lang
    
    return best_lang

def caesar_encrypt(text, key):
    try:
        shift = int(key)  # Convert to integer
    except (ValueError, TypeError):
        shift = 7  # Default shift if conversion fails
    
    return "".join(chr((ord(c) + shift - 65) % 26 + 65) if c.isupper()
        else chr((ord(c) + shift - 97) % 26 + 97) if c.islower()
        else c for c in text)
    
    
def vigenere_encrypt(text, key):
    key = key.upper()
    result, j = [], 0
    for c in text:
        if c.isalpha():
            shift = ord(key[j % len(key)]) - 65
            base = 65 if c.isupper() else 97
            result.append(chr((ord(c) + shift - base) % 26 + base))
            j += 1
        else:
            result.append(c)
    return "".join(result)

def vigenere_decrypt(text, key):
    key = key.upper()
    result, j = [], 0
    for c in text:
        if c.isalpha():
            shift = ord(key[j % len(key)]) - 65
            base = 65 if c.isupper() else 97
            result.append(chr((ord(c) - shift - base) % 26 + base))
            j += 1
        else:
            result.append(c)
    return "".join(result)

def substitution_encrypt(text, sub_map):
    return "".join(sub_map.get(c.upper(), c.upper()).lower() if c.islower()
                  else sub_map.get(c, c) for c in text)

def substitution_decrypt(text, sub_map):
    rev = {v: k for k, v in sub_map.items()}
    return "".join(rev.get(c.upper(), c.upper()).lower() if c.islower() else rev.get(c, c) for c in text)

# Cracking Functions
def chi_squared_score(text, freq_table):
    text = text.upper()
    observed = {}
    total_letters = 0
    for c in text:
        if c.isalpha() or c == ' ':
            observed[c] = observed.get(c, 0) + 1
            total_letters += 1
    if total_letters == 0:
        return float('inf')
    score = 0.0
    for letter, expected_freq in freq_table.items():
        expected = expected_freq * total_letters
        observed_count = observed.get(letter, 0)
        score += (observed_count - expected) ** 2 / expected if expected > 0 else 0
    return score

def crack_caesar(ciphertext, languages=[("French", FRENCH_FREQ), ("English", ENGLISH_FREQ)]):
    ciphertext = ciphertext.upper()
    if len(ciphertext.strip()) < 10:
        return None, None, "Texte trop court (<10 caractères)"
    results = []
    for shift in range(26):
        decrypted = caesar_encrypt(ciphertext, -shift % 26)
        for lang_name, freq in languages:
            score = chi_squared_score(decrypted, freq)
            results.append((score, shift, decrypted, lang_name))
    results.sort(key=lambda x: x[0])
    top_score, top_shift, top_text, top_lang = results[0]
    if len(results) > 1:
        confidence_ratio = results[1][0] / (top_score + 1e-9)
        confidence = "Très élevée" if confidence_ratio > 3 else "Élevée" if confidence_ratio > 1.5 else "Moyenne"
    else:
        confidence = "Élevée"
    return top_text, top_shift, f"{top_lang} (décalage {top_shift}) – Confiance : {confidence}"

# Transposition functions

def get_column_order(key):
    """
    Get the column order based on alphabetical sorting of the key.
    Example: "GRAIN" -> [2, 4, 0, 1, 3] (A=0, G=1, I=2, N=3, R=4)
    """
    key = key.upper()
    # Create list of (letter, original_index) tuples
    indexed_key = [(char, idx) for idx, char in enumerate(key)]
    # Sort by letter
    sorted_key = sorted(indexed_key)
    # Extract the order
    order = [item[1] for item in sorted_key]
    return order

def transposition_encrypt(text, key):
    """
    Encrypt text using rectangular transposition with a keyword.
    
    Args:
        text: Plain text to encrypt
        key: Keyword for transposition
    
    Returns:
        Encrypted text
    """
    if not key:
        return text
    
    key = key.upper()
    key_length = len(key)
    
    # Remove spaces and convert to uppercase
    text = text.replace(" ", "").upper()
    
    # Calculate number of rows needed
    num_rows = (len(text) + key_length - 1) // key_length
    
    # Pad the text with 'X' if necessary
    padding_needed = (num_rows * key_length) - len(text)
    text += 'X' * padding_needed
    
    # Create the grid
    grid = []
    for i in range(num_rows):
        row = text[i * key_length:(i + 1) * key_length]
        grid.append(list(row))
    
    # Get column order based on key
    column_order = get_column_order(key)
    
    # Read columns in the order specified by the key
    result = []
    for col_idx in column_order:
        for row in grid:
            result.append(row[col_idx])
    
    return ''.join(result)

def transposition_decrypt(ciphertext, key):
    """
    Decrypt text encrypted with rectangular transposition.
    
    Args:
        ciphertext: Encrypted text
        key: Keyword used for encryption
    
    Returns:
        Decrypted text
    """
    if not key:
        return ciphertext
    
    key = key.upper()
    key_length = len(key)
    
    # Calculate number of rows
    num_rows = len(ciphertext) // key_length
    
    # Get column order
    column_order = get_column_order(key)
    
    # Create reverse order (to know which column to read first)
    reverse_order = [0] * key_length
    for i, pos in enumerate(column_order):
        reverse_order[pos] = i
    
    # Create empty grid
    grid = [['' for _ in range(key_length)] for _ in range(num_rows)]
    
    # Fill the grid column by column in the order they were written
    idx = 0
    for col_idx in column_order:
        for row in range(num_rows):
            grid[row][col_idx] = ciphertext[idx]
            idx += 1
    
    # Read the grid row by row
    result = []
    for row in grid:
        result.extend(row)
    
    # Remove padding 'X' at the end
    plaintext = ''.join(result).rstrip('X')
    
    return plaintext