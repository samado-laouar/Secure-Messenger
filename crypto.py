# crypto.py - Encryption and Decryption Functions (Updated)

import random
import math
import json

# Common words dictionary for auto-decryption
ENGLISH_WORDS = {
    'THE', 'BE', 'TO', 'OF', 'AND', 'A', 'IN', 'THAT', 'HAVE', 'I',
    'IT', 'FOR', 'NOT', 'ON', 'WITH', 'HE', 'AS', 'YOU', 'DO', 'AT',
    'THIS', 'BUT', 'HIS', 'BY', 'FROM', 'THEY', 'WE', 'SAY', 'HER', 'SHE',
    'OR', 'AN', 'WILL', 'MY', 'ONE', 'ALL', 'WOULD', 'THERE', 'THEIR', 'WHAT',
    'SO', 'UP', 'OUT', 'IF', 'ABOUT', 'WHO', 'GET', 'WHICH', 'GO', 'ME',
    'WHEN', 'MAKE', 'CAN', 'LIKE', 'TIME', 'NO', 'JUST', 'HIM', 'KNOW', 'TAKE',
    'PEOPLE', 'INTO', 'YEAR', 'YOUR', 'GOOD', 'SOME', 'COULD', 'THEM', 'SEE', 'OTHER',
    'THAN', 'THEN', 'NOW', 'LOOK', 'ONLY', 'COME', 'ITS', 'OVER', 'THINK', 'ALSO',
    'BACK', 'AFTER', 'USE', 'TWO', 'HOW', 'OUR', 'WORK', 'FIRST', 'WELL', 'WAY',
    'EVEN', 'NEW', 'WANT', 'BECAUSE', 'ANY', 'THESE', 'GIVE', 'DAY', 'MOST', 'US',
    'IS', 'WAS', 'ARE', 'BEEN', 'HAS', 'HAD', 'WERE', 'SAID', 'DID', 'HAVING',
    'MAY', 'SHOULD', 'AFTER', 'VERY', 'THROUGH', 'MUST', 'WHERE', 'MUCH', 'BEFORE', 'RIGHT'
}

FRENCH_WORDS = {
    'LE', 'DE', 'UN', 'ÊTRE', 'ET', 'À', 'IL', 'AVOIR', 'NE', 'JE',
    'SON', 'QUE', 'SE', 'QUI', 'CE', 'DANS', 'EN', 'DU', 'ELLE', 'AU',
    'POUR', 'PAS', 'QUE', 'VOUS', 'PAR', 'SUR', 'FAIRE', 'PLUS', 'DIRE', 'ME',
    'ON', 'MON', 'LUI', 'NOUS', 'COMME', 'MAIS', 'POUVOIR', 'AVEC', 'TON', 'TOUT',
    'Y', 'ALLER', 'VOIR', 'EN', 'BIEN', 'OÙ', 'SANS', 'TU', 'OU', 'LEUR',
    'HOMME', 'SI', 'DEUX', 'COMMENT', 'AUTRE', 'VOULOIR', 'DEVOIR', 'DONC', 'TRÈS', 'AUSSI',
    'SAVOIR', 'ENCORE', 'QUAND', 'MÊME', 'TOUT', 'CETTE', 'DEPUIS', 'CELUI', 'CELLE', 'CEUX',
    'ÉTAIT', 'DONT', 'TOUS', 'PEUT', 'SONT', 'SUIS', 'AVEZ', 'SERA', 'FONT', 'CETTE',
    'GRAND', 'AUTRE', 'MOINS', 'AVANT', 'ALORS', 'JOUR', 'TEMPS', 'CHOSE', 'FOIS', 'TOUJOURS',
    'OUI', 'NON', 'JAMAIS', 'RIEN', 'PERSONNE', 'QUELQUE', 'CHAQUE', 'TROP', 'ASSEZ', 'BEAUCOUP'
}

ARABIC_WORDS = {
    'في', 'من', 'على', 'إلى', 'هذا', 'أن', 'كان', 'قد', 'ما', 'لا',
    'هو', 'التي', 'عن', 'مع', 'أو', 'كل', 'هي', 'بعد', 'قبل', 'حتى',
    'عند', 'منذ', 'خلال', 'أول', 'آخر', 'جميع', 'كيف', 'لماذا', 'أين', 'متى'
}

LANGUAGE_DICT = {
    'english': ENGLISH_WORDS,
    'french': FRENCH_WORDS,
    'arabic': ARABIC_WORDS
}

# Frequency tables for chi-squared analysis
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

def count_dictionary_words(text, word_dict):
    """Count how many dictionary words appear in the text"""
    words = text.upper().split()
    count = 0
    for word in words:
        # Remove punctuation
        clean_word = ''.join(c for c in word if c.isalpha())
        if clean_word in word_dict:
            count += 1
    return count

def calculate_chi_squared(text, freq_table):
    """Calculate chi-squared statistic for text against expected frequency"""
    if not text:
        return float('inf')
    
    letter_count = {}
    total = 0
    
    for char in text.upper():
        if char in freq_table:
            letter_count[char] = letter_count.get(char, 0) + 1
            total += 1
    
    if total == 0:
        return float('inf')
    
    chi_squared = 0
    for letter in freq_table:
        expected = (freq_table[letter] / 100) * total
        observed = letter_count.get(letter, 0)
        if expected > 0:
            chi_squared += ((observed - expected) ** 2) / expected
    
    return chi_squared

def auto_decrypt_caesar(ciphertext, language='english'):
    """
    Automatically decrypt Caesar cipher using dictionary words and frequency analysis
    Returns: (decrypted_text, key, confidence_score)
    """
    if language not in LANGUAGE_FREQ:
        language = 'english'
    
    freq_table = LANGUAGE_FREQ[language]
    word_dict = LANGUAGE_DICT.get(language, ENGLISH_WORDS)
    
    best_score = -1
    best_key = 0
    best_plaintext = ""
    
    # Try all 26 possible shifts
    results = []
    for shift in range(26):
        plaintext = caesar_encrypt(ciphertext, -shift)
        
        # Count dictionary words
        word_count = count_dictionary_words(plaintext, word_dict)
        
        # Calculate chi-squared score (lower is better)
        chi_score = calculate_chi_squared(plaintext, freq_table)
        
        # Combined score: prioritize word matches, use chi-squared as tiebreaker
        # Normalize chi-squared to 0-100 scale (inverse)
        chi_normalized = max(0, 100 - chi_score)
        
        # Weight: 70% word matches, 30% frequency analysis
        combined_score = (word_count * 70) + (chi_normalized * 0.3)
        
        results.append((combined_score, shift, plaintext, word_count))
        
        if combined_score > best_score:
            best_score = combined_score
            best_key = shift
            best_plaintext = plaintext
    
    # Sort by score
    results.sort(reverse=True, key=lambda x: x[0])
    
    # Calculate confidence based on score difference
    if len(results) > 1:
        score_diff = results[0][0] - results[1][0]
        confidence = min(100, max(0, 50 + score_diff * 2))
    else:
        confidence = 50
    
    # Boost confidence if we found dictionary words
    word_count = results[0][3]
    if word_count > 0:
        confidence = min(100, confidence + (word_count * 5))
    
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
        shift = int(key)
    except (ValueError, TypeError):
        shift = 3
    
    # Normalize shift to 0-25 range
    shift = shift % 26
    
    result = []
    for c in text:
        if c.isupper():
            result.append(chr((ord(c) - 65 + shift) % 26 + 65))
        elif c.islower():
            result.append(chr((ord(c) - 97 + shift) % 26 + 97))
        else:
            result.append(c)
    return "".join(result)

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
    """Fixed substitution cipher encryption"""
    result = []
    for c in text:
        if c.isupper():
            result.append(sub_map.get(c, c))
        elif c.islower():
            upper_c = c.upper()
            encrypted_upper = sub_map.get(upper_c, upper_c)
            result.append(encrypted_upper.lower())
        else:
            result.append(c)
    return "".join(result)

def substitution_decrypt(text, sub_map):
    """Fixed substitution cipher decryption"""
    # Create reverse mapping
    rev = {v: k for k, v in sub_map.items()}
    
    result = []
    for c in text:
        if c.isupper():
            result.append(rev.get(c, c))
        elif c.islower():
            upper_c = c.upper()
            decrypted_upper = rev.get(upper_c, upper_c)
            result.append(decrypted_upper.lower())
        else:
            result.append(c)
    return "".join(result)

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

def get_column_order(key):
    """Get the column order based on alphabetical sorting of the key"""
    key = key.upper()
    indexed_key = [(char, idx) for idx, char in enumerate(key)]
    sorted_key = sorted(indexed_key)
    order = [item[1] for item in sorted_key]
    return order

def transposition_encrypt(text, key):
    """Encrypt text using rectangular transposition with a keyword"""
    if not key:
        return text
    
    key = key.upper()
    key_length = len(key)
    
    text = text.replace(" ", "").upper()
    num_rows = (len(text) + key_length - 1) // key_length
    padding_needed = (num_rows * key_length) - len(text)
    text += 'X' * padding_needed
    
    grid = []
    for i in range(num_rows):
        row = text[i * key_length:(i + 1) * key_length]
        grid.append(list(row))
    
    column_order = get_column_order(key)
    
    result = []
    for col_idx in column_order:
        for row in grid:
            result.append(row[col_idx])
    
    return ''.join(result)

def transposition_decrypt(ciphertext, key):
    """Decrypt text encrypted with rectangular transposition"""
    if not key:
        return ciphertext
    
    key = key.upper()
    key_length = len(key)
    num_rows = len(ciphertext) // key_length
    
    column_order = get_column_order(key)
    reverse_order = [0] * key_length
    for i, pos in enumerate(column_order):
        reverse_order[pos] = i
    
    grid = [['' for _ in range(key_length)] for _ in range(num_rows)]
    
    idx = 0
    for col_idx in column_order:
        for row in range(num_rows):
            grid[row][col_idx] = ciphertext[idx]
            idx += 1
    
    result = []
    for row in grid:
        result.extend(row)
    
    plaintext = ''.join(result).rstrip('X')
    return plaintext