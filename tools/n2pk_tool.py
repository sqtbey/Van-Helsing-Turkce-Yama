"""
Van Helsing N2PK Tool
Neocore Package format:
  - Header: uint32(nameLen) + UTF-16 string "Neocore Package"
  - uint16 padding
  - uint32 unknown (version/flags)
  - uint32 file_count
  - uint16 padding
  - DATA: concatenated file bytes (offset 44)
  - FILE TABLE (at end): sorted by SDBM hash of filename:
      uint32 sdbm_hash + uint32 nameLen + UTF-16 name + uint16(0) + int64 offset + int64 size
"""

import struct
import os
import sys
import re

HEADER_MAGIC = "Neocore Package"
DATA_OFFSET = 44


def sdbm(s):
    """SDBM hash algorithm used by Neocore Games engine."""
    h = 0
    for c in s:
        h = (ord(c) + (h << 6) + (h << 16) - h) & 0xFFFFFFFF
    return h


def extract_n2pk(filepath, output_dir):
    """Extract all XML files from N2PK to output directory."""
    os.makedirs(output_dir, exist_ok=True)

    with open(filepath, 'rb') as f:
        data = f.read()

    # Parse header
    name_len = struct.unpack_from('<I', data, 0)[0]
    magic = data[4:4 + name_len * 2].decode('utf-16-le')
    assert magic == HEADER_MAGIC, f"Invalid N2PK header: {magic}"

    content_bytes = data[DATA_OFFSET:]
    xml_offsets = [m.start() for m in re.finditer(rb'<\?xml version="1\.0"', content_bytes)]
    actual_count = len(xml_offsets)

    entries = []
    pos = len(data)

    for _ in range(actual_count):
        size = struct.unpack_from('<q', data, pos - 8)[0]
        offset = struct.unpack_from('<q', data, pos - 16)[0]
        pos -= 18

        for test_len in range(5, 70):
            nl_pos = pos - test_len * 2 - 4
            if nl_pos < DATA_OFFSET:
                continue
            test_nl = struct.unpack_from('<I', data, nl_pos)[0]
            if test_nl == test_len:
                name_bytes = data[nl_pos + 4: nl_pos + 4 + test_len * 2]
                try:
                    name = name_bytes.decode('utf-16-le')
                    if name.endswith('.xml') or name.endswith('.cfg'):
                        h_pos = nl_pos - 4
                        h = struct.unpack_from('<I', data, h_pos)[0]
                        entries.append({
                            'name': name,
                            'offset': offset,
                            'size': size,
                            'checksum': h
                        })
                        pos = h_pos
                        break
                except Exception:
                    continue

    entries.reverse()

    for entry in entries:
        xml_data = data[DATA_OFFSET + entry['offset']: DATA_OFFSET + entry['offset'] + entry['size']]
        out_path = os.path.join(output_dir, entry['name'])
        with open(out_path, 'wb') as f:
            f.write(xml_data)

    return entries


def pack_n2pk(xml_dir, output_filepath, original_filepath):
    """Pack directory of XML files back into N2PK with SDBM-sorted file table."""
    with open(original_filepath, 'rb') as f:
        orig_data = f.read()

    # Get original entries to know file names
    content_bytes = orig_data[DATA_OFFSET:]
    xml_offsets = [m.start() for m in re.finditer(rb'<\?xml version="1\.0"', content_bytes)]
    actual_count = len(xml_offsets)

    orig_entries = []
    pos = len(orig_data)
    for _ in range(actual_count):
        size = struct.unpack_from('<q', orig_data, pos - 8)[0]
        offset = struct.unpack_from('<q', orig_data, pos - 16)[0]
        pos -= 18

        for test_len in range(5, 70):
            nl_pos = pos - test_len * 2 - 4
            if nl_pos < DATA_OFFSET:
                continue
            test_nl = struct.unpack_from('<I', orig_data, nl_pos)[0]
            if test_nl == test_len:
                name_bytes = orig_data[nl_pos + 4: nl_pos + 4 + test_len * 2]
                try:
                    name = name_bytes.decode('utf-16-le')
                    if name.endswith('.xml') or name.endswith('.cfg'):
                        orig_entries.append({
                            'name': name,
                            'orig_offset': offset,
                            'orig_size': size
                        })
                        pos = nl_pos - 4
                        break
                except Exception:
                    continue

    orig_entries.reverse()

    files_to_pack = []
    for entry in orig_entries:
        p = os.path.join(xml_dir, entry['name'])
        if os.path.exists(p):
            with open(p, 'rb') as f:
                fdata = f.read()
        else:
            fdata = orig_data[DATA_OFFSET + entry['orig_offset']:
                              DATA_OFFSET + entry['orig_offset'] + entry['orig_size']]

        files_to_pack.append({
            'name': entry['name'],
            'data': fdata,
            'sdbm': sdbm(entry['name'])
        })

    # Sort files by SDBM hash in ascending order (Neocore engine requirement)
    files_to_pack.sort(key=lambda x: x['sdbm'])

    new_data = b''
    new_table = b''
    current_offset = 0

    for item in files_to_pack:
        fdata = item['data']
        name = item['name']
        h = item['sdbm']

        name_encoded = name.encode('utf-16-le')
        name_len = len(name)

        entry_bytes = struct.pack('<I', h)
        entry_bytes += struct.pack('<I', name_len)
        entry_bytes += name_encoded
        entry_bytes += b'\x00\x00'
        entry_bytes += struct.pack('<q', current_offset)
        entry_bytes += struct.pack('<q', len(fdata))

        new_data += fdata
        new_table += entry_bytes
        current_offset += len(fdata)

    header = orig_data[:DATA_OFFSET]
    output = header + new_data + new_table

    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    with open(output_filepath, 'wb') as f:
        f.write(output)

    print(f"Packed {len(files_to_pack)} files into {output_filepath}")
    print(f"Data size: {len(new_data):,}, Table size: {len(new_table):,}, Total size: {len(output):,}")
    return len(files_to_pack)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage:")
        print("  n2pk_tool.py extract <input.N2PK> <output_dir>")
        print("  n2pk_tool.py pack <xml_dir> <output.N2PK> <orig.N2PK>")
        sys.exit(1)

    if sys.argv[1] == 'extract':
        extract_n2pk(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'pack':
        pack_n2pk(sys.argv[2], sys.argv[3], sys.argv[4])
