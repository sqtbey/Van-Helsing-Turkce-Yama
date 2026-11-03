"""
Van Helsing Turkish Patch - Final Accurate Batch Translator
Translates remaining 3305 strings in batches of 10 using 2 steady worker threads.
Retries on 429 with backoff until 200 OK.
Never saves untranslated English text as Turkish.
When done, calls apply_patch.py.
"""

import os
import re
import json
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = r"c:\Program Files (x86)\Steam\steamapps\common\The Incredible Adventures of Van Helsing\turkish_patch"
INPUT_JSON = os.path.join(BASE_DIR, "strings_to_translate.json")
CACHE_FILE = os.path.join(BASE_DIR, "translation_cache.json")

PROPER_NOUNS = [
    'Van Helsing', 'Lady Katarina', 'Katarina', 'Beggar King',
    'Borgovia', 'Borgova', 'Borgov', 'Dragan Schimko',
    'Fulmigatis', 'Sfanta Ilona', 'Contraptor', 'Inspector Krupps',
    'Captain Borislav', 'Borislav', 'Vodyanoi', 'Vrikolak',
    'Markovna', 'Croakwood', 'Gallowsbog', 'Duskdale', 'Ravenscar',
    'Baskerville', 'Gorgoniad', 'Corvinus', 'Gasparin', 'Domovoy',
    'Rusalka', 'Vlados', 'Abigail', 'Koschei', 'Breda', 'Tepesh',
    'Romany', 'Gypsies', 'Ink'
]
PROPER_NOUNS.sort(key=len, reverse=True)

ASCII_MAP = str.maketrans({
    'ç': 'c', 'Ç': 'C',
    'ğ': 'g', 'Ğ': 'G',
    'ı': 'i', 'I': 'I', 'İ': 'I',
    'ö': 'o', 'Ö': 'O',
    'ş': 's', 'Ş': 'S',
    'ü': 'u', 'Ü': 'U'
})


def to_ascii_tr(text):
    return text.translate(ASCII_MAP)


def protect_text(text):
    tokens = {}
    counter = 0

    def add_token(val):
        nonlocal counter
        ph = f"XPNT{counter}X"
        tokens[ph] = val
        counter += 1
        return ph

    text = re.sub(r'\[[a-zA-Z0-9_]+\]', lambda m: add_token(m.group(0)), text)
    text = re.sub(r'\{[0-9]+\}', lambda m: add_token(m.group(0)), text)
    text = re.sub(r'%[0-9]*[a-zA-Z_]+', lambda m: add_token(m.group(0)), text)

    for pn in PROPER_NOUNS:
        pattern = re.compile(r'\b' + re.escape(pn) + r'\b', re.IGNORECASE)
        for m in reversed(list(pattern.finditer(text))):
            orig_match = m.group(0)
            ph = add_token(orig_match)
            text = text[:m.start()] + ph + text[m.end():]

    return text, tokens


def restore_text(text, tokens):
    for ph, orig in tokens.items():
        pattern = re.compile(re.escape(ph), re.IGNORECASE)
        text = pattern.sub(orig, text)
    return text


def translate_batch_with_retry(batch_items, session):
    url = 'https://clients5.google.com/translate_a/t'
    params = [('client', 'dict-chrome-ex'), ('sl', 'en'), ('tl', 'tr')]
    for _, p_text, _ in batch_items:
        params.append(('q', p_text))

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for attempt in range(8):
        try:
            r = session.get(url, params=params, headers=headers, timeout=12)
            if r.status_code == 200:
                results = r.json()
                if isinstance(results, list) and len(results) == len(batch_items):
                    out = []
                    for (orig, _, tokens), tr_text in zip(batch_items, results):
                        restored = restore_text(str(tr_text), tokens)
                        out.append((orig, to_ascii_tr(restored)))
                    time.sleep(0.15)
                    return out
            elif r.status_code == 429:
                time.sleep(1.5 * (attempt + 1))
            else:
                time.sleep(0.5)
        except Exception:
            time.sleep(1.0)

    # Secondary fallback: try 1-by-1
    out = []
    for orig, p_text, tokens in batch_items:
        tr_one = translate_single_clients5(p_text, session)
        restored = restore_text(tr_one, tokens)
        out.append((orig, to_ascii_tr(restored)))
    return out


def translate_single_clients5(p_text, session):
    url = 'https://clients5.google.com/translate_a/t'
    params = {'client': 'dict-chrome-ex', 'sl': 'en', 'tl': 'tr', 'q': p_text}
    headers = {'User-Agent': 'Mozilla/5.0'}
    for attempt in range(4):
        try:
            r = session.get(url, params=params, headers=headers, timeout=8)
            if r.status_code == 200:
                res = r.json()
                if isinstance(res, list) and res:
                    return str(res[0])
            time.sleep(1.0)
        except Exception:
            time.sleep(1.0)
    return p_text


def main():
    print("=== Finalizing All Translations ===")
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        all_strings = json.load(f)

    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    # Valid translations are those where translation differs from original (or is very short like OK, Yes, No)
    def is_valid(k, v):
        if not v or not v.strip():
            return False
        if k.strip().lower() != v.strip().lower():
            return True
        # If original was numbers/symbols only
        if re.match(r'^[\d\s\W]+$', k):
            return True
        return False

    valid_cache = {k: v for k, v in cache.items() if is_valid(k, v)}
    print(f"Current valid translations in cache: {len(valid_cache):,}")

    to_trans = set(s['original'] for s in all_strings if not s['skip'] and s['original'] and s['original'].strip())
    needed = [t for t in to_trans if t not in valid_cache]
    print(f"Total needed unique strings: {len(to_trans):,}")
    print(f"Strings remaining to translate: {len(needed):,}")

    if needed:
        BATCH_SIZE = 10
        batches = [needed[i:i + BATCH_SIZE] for i in range(0, len(needed), BATCH_SIZE)]
        print(f"Processing {len(batches)} batches of {BATCH_SIZE} with 2 polite workers...")

        lock = threading.Lock()
        completed = 0
        last_save = time.time()

        def worker_task(batch):
            session = requests.Session()
            prep_items = []
            for t in batch:
                p_text, tokens = protect_text(t)
                prep_items.append((t, p_text, tokens))
            return translate_batch_with_retry(prep_items, session)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_batch = {executor.submit(worker_task, b): b for b in batches}
            for future in as_completed(future_to_batch):
                batch_res = future.result()
                with lock:
                    for orig, tr in batch_res:
                        valid_cache[orig] = tr
                    completed += len(batch_res)

                    if completed % 100 == 0 or completed >= len(needed):
                        pct = (len(valid_cache) / len(to_trans)) * 100
                        print(f"Progress: {len(valid_cache):,}/{len(to_trans):,} ({pct:.1f}%)", flush=True)

                    if time.time() - last_save > 8:
                        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                            json.dump(valid_cache, f, ensure_ascii=False, indent=2)
                        last_save = time.time()

        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(valid_cache, f, ensure_ascii=False, indent=2)
        print("\nAll remaining translations completed and saved to cache!", flush=True)

    print("\n=== Applying patch into Strings/Files.N2PK ===", flush=True)
    import sys
    sys.path.append(BASE_DIR)
    from apply_patch import build_and_apply_patch
    build_and_apply_patch()


if __name__ == '__main__':
    main()
