"""
Van Helsing Turkish Patch - Patch Builder & Applier
Applies translations from translation_cache.json into game XMLs and packs them into Strings/Files.N2PK.
Rules:
  - NEVER translate proper nouns (Van Helsing, Katarina, Borgova, Beggar King, etc.)
  - Keep item names, skill names, perk names in original English.
  - Translate all item descriptions, skill descriptions, quest names, quest objectives,
    dialogues, UI menus, and battle events.
  - Convert all Turkish special characters to ASCII equivalents.
"""

import os
import re
import json
import shutil
from n2pk_tool import pack_n2pk

GAME_DIR = r"c:\Program Files (x86)\Steam\steamapps\common\The Incredible Adventures of Van Helsing"
STRINGS_DIR = os.path.join(GAME_DIR, "Strings")
PATCH_DIR = os.path.join(GAME_DIR, "turkish_patch")
EXTRACTED_DIR = os.path.join(PATCH_DIR, "extracted_xml")
TRANSLATED_DIR = os.path.join(PATCH_DIR, "translated_xml")
CACHE_JSON = os.path.join(PATCH_DIR, "translation_cache.json")
TARGET_N2PK = os.path.join(STRINGS_DIR, "Files.N2PK")
ORIGINAL_BACKUP_N2PK = os.path.join(STRINGS_DIR, "Files.N2PK.original_backup")

# Files where item/skill names should NOT be translated (only descriptions)
ITEM_FILES = {
    'lang_artifacts.xml',
    'lang_skills.xml',
    'lang_perks.xml',
    'lang_soldiers.xml',
    'dlc_lang_artifacts.xml',
    'dlc_lang_soldiers.xml'
}

# Tags representing item/ability names
SKIP_PARENT_TAGS = {
    'name', 'setname', 'weapontype', 'armortype', 'subtypes',
    'types', 'rarity', 'condition', 'conditions'
}

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


def build_and_apply_patch():
    print("=== Step 1: Loading Translations Cache ===")
    with open(CACHE_JSON, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    print(f"Loaded {len(cache):,} translations from cache.")

    os.makedirs(TRANSLATED_DIR, exist_ok=True)

    print("\n=== Step 2: Applying Translations to XML Files ===")
    xml_files = sorted([f for f in os.listdir(EXTRACTED_DIR) if f.endswith('.xml')])
    total_translated = 0
    total_preserved_names = 0
    total_untranslated = 0

    for fname in xml_files:
        src_path = os.path.join(EXTRACTED_DIR, fname)
        dst_path = os.path.join(TRANSLATED_DIR, fname)

        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()

        is_item_file = fname in ITEM_FILES
        file_trans_count = 0
        file_name_preserve_count = 0

        def replace_with_parent(match):
            nonlocal file_trans_count, file_name_preserve_count
            nonlocal total_translated, total_preserved_names, total_untranslated

            parent_tag = match.group(1)
            original_text = match.group(2)

            # Skip language name declarations
            if original_text.strip() in ('English', 'eng'):
                return match.group(0)

            # In item/skill files, preserve the item/skill Name
            if is_item_file and parent_tag.lower() in SKIP_PARENT_TAGS:
                file_name_preserve_count += 1
                total_preserved_names += 1
                return match.group(0)

            # Look up translation in cache
            if original_text in cache:
                tr = to_ascii_tr(cache[original_text])
                file_trans_count += 1
                total_translated += 1
                return f'<{parent_tag}>\n\t\t\t\t<eng>{tr}</eng>\n\t\t\t</{parent_tag}>'
            else:
                total_untranslated += 1
                return match.group(0)

        # Match <ParentTag> ... <eng>Text</eng> ... </ParentTag>
        new_content = re.sub(
            r'<([A-Za-z0-9_]+)>\s*<eng>(.*?)</eng>\s*</\1>',
            replace_with_parent,
            content,
            flags=re.DOTALL
        )

        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if file_trans_count > 0 or file_name_preserve_count > 0:
            print(f"  {fname}: {file_trans_count} translated, {file_name_preserve_count} item/skill names preserved")

    print(f"\nSummary:")
    print(f"  Total translated strings: {total_translated:,}")
    print(f"  Total item/skill names kept original: {total_preserved_names:,}")
    print(f"  Total untranslated: {total_untranslated}")

    print("\n=== Step 3: Packing Turkish N2PK ===")
    if not os.path.exists(ORIGINAL_BACKUP_N2PK):
        print(f"Creating original backup: {ORIGINAL_BACKUP_N2PK}")
        shutil.copy2(TARGET_N2PK, ORIGINAL_BACKUP_N2PK)
    else:
        print(f"Using existing original backup template: {ORIGINAL_BACKUP_N2PK}")

    pack_n2pk(TRANSLATED_DIR, TARGET_N2PK, ORIGINAL_BACKUP_N2PK)

    # Copy to turkish_patch folder for standalone installer
    standalone_dest = os.path.join(PATCH_DIR, "Files.N2PK")
    shutil.copy2(TARGET_N2PK, standalone_dest)
    print(f"Copied patched N2PK to standalone installer: {standalone_dest}")

    print("\n=== Turkish Patch Applied Successfully! ===")


if __name__ == '__main__':
    build_and_apply_patch()
