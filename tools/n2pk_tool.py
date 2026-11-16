"""
Van Helsing N2PK Tool - Exact Specification
Neocore Package binary format:
  Offset 0..3: uint32 name_len (15)
  Offset 4..33: UTF-16 LE string "Neocore Package" (30 bytes)
  Offset 34..35: uint16 null terminator (0)
  Offset 36..43: int64 data_size (length of data section in bytes)
  Offset 44..(44 + data_size - 1): concatenated file data
  Offset (44 + data_size)..(44 + data_size + 3): uint32 file_count (number of files)
  Offset (44 + data_size + 4)..(EOF): file table entries, sorted by SDBM hash in ascending order:
      uint32 sdbm_hash
      uint32 filename_len
      UTF-16 LE filename (filename_len * 2 bytes)
      uint16 null terminator (0)
      int64 data_offset (relative to offset 44)
      int64 data_size (length of this file in bytes)
"""

import struct
import os
import sys

HEADER_MAGIC = "Neocore Package"
DATA_START_OFFSET = 44


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

    name_len = struct.unpack_from('<I', data, 0)[0]
    magic = data[4:4 + name_len * 2].decode('utf-16-le')
    assert magic == HEADER_MAGIC, f"Invalid N2PK header: {magic}"

    data_size = struct.unpack_from('<q', data, 36)[0]
    data_start = DATA_START_OFFSET
    data_end = data_start + data_size

    file_count = struct.unpack_from('<I', data, data_end)[0]
    table_pos = data_end + 4

    entries = []
    for _ in range(file_count):
        h = struct.unpack_from('<I', data, table_pos)[0]
        nl = struct.unpack_from('<I', data, table_pos + 4)[0]
        name = data[table_pos + 8: table_pos + 8 + nl * 2].decode('utf-16-le')
        next_pos = table_pos + 8 + nl * 2 + 2  # skip null term
        offset = struct.unpack_from('<q', data, next_pos)[0]
        size = struct.unpack_from('<q', data, next_pos + 8)[0]
        table_pos = next_pos + 16

        entries.append({
            'hash': h,
            'name': name,
            'offset': offset,
            'size': size
        })

        file_bytes = data[data_start + offset: data_start + offset + size]
        out_path = os.path.join(output_dir, name)
        with open(out_path, 'wb') as out_f:
            out_f.write(file_bytes)

    print(f"Extracted {len(entries)} files from {filepath} to {output_dir}")
    return entries


def pack_n2pk(xml_dir, output_filepath, template_n2pk_path):
    """
    Pack directory of XML files back into N2PK with:
      1. Correct int64 data_size at offset 36.
      2. Correct uint32 file_count at offset (44 + data_size).
      3. File table entries sorted by SDBM hash.
    """
    # Extract template to get complete list of required filenames
    with open(template_n2pk_path, 'rb') as f:
        orig_data = f.read()

    name_len = struct.unpack_from('<I', orig_data, 0)[0]
    orig_data_size = struct.unpack_from('<q', orig_data, 36)[0]
    orig_data_end = DATA_START_OFFSET + orig_data_size
    orig_file_count = struct.unpack_from('<I', orig_data, orig_data_end)[0]

    table_pos = orig_data_end + 4
    files_to_pack = []

    for _ in range(orig_file_count):
        nl = struct.unpack_from('<I', orig_data, table_pos + 4)[0]
        name = orig_data[table_pos + 8: table_pos + 8 + nl * 2].decode('utf-16-le')
        next_pos = table_pos + 8 + nl * 2 + 2
        orig_offset = struct.unpack_from('<q', orig_data, next_pos)[0]
        orig_size = struct.unpack_from('<q', orig_data, next_pos + 8)[0]
        table_pos = next_pos + 16

        p = os.path.join(xml_dir, name)
        if os.path.exists(p):
            with open(p, 'rb') as f:
                fdata = f.read()
        else:
            fdata = orig_data[DATA_START_OFFSET + orig_offset: DATA_START_OFFSET + orig_offset + orig_size]

        files_to_pack.append({
            'name': name,
            'data': fdata,
            'sdbm': sdbm(name)
        })

    # Sort files by SDBM hash in ascending order (Neocore engine requirement for binary search)
    files_to_pack.sort(key=lambda x: x['sdbm'])

    # Build data section
    data_section = b''
    for item in files_to_pack:
        item['offset'] = len(data_section)
        data_section += item['data']

    new_data_size = len(data_section)

    # Build header (44 bytes)
    magic_bytes = HEADER_MAGIC.encode('utf-16-le')
    header = struct.pack('<I', len(HEADER_MAGIC))
    header += magic_bytes
    header += struct.pack('<H', 0)  # null terminator
    header += struct.pack('<q', new_data_size)  # int64 data_size!

    assert len(header) == DATA_START_OFFSET, f"Header size is {len(header)}, expected {DATA_START_OFFSET}"

    # Build file table
    table_section = struct.pack('<I', len(files_to_pack))  # uint32 file_count!

    for item in files_to_pack:
        name = item['name']
        name_encoded = name.encode('utf-16-le')
        entry = struct.pack('<I', item['sdbm'])
        entry += struct.pack('<I', len(name))
        entry += name_encoded
        entry += struct.pack('<H', 0)  # null terminator
        entry += struct.pack('<q', item['offset'])
        entry += struct.pack('<q', len(item['data']))
        table_section += entry

    complete_file = header + data_section + table_section

    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    with open(output_filepath, 'wb') as f:
        f.write(complete_file)

    print(f"Packed {len(files_to_pack)} files into {output_filepath}")
    print(f"  Header size: {len(header)}")
    print(f"  Data size:   {new_data_size:,} bytes")
    print(f"  Table size:  {len(table_section):,} bytes")
    print(f"  Total size:  {len(complete_file):,} bytes")
    return len(files_to_pack)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage:")
        print("  n2pk_tool.py extract <input.N2PK> <output_dir>")
        print("  n2pk_tool.py pack <xml_dir> <output.N2PK> <template.N2PK>")
        sys.exit(1)

    if sys.argv[1] == 'extract':
        extract_n2pk(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'pack':
        pack_n2pk(sys.argv[2], sys.argv[3], sys.argv[4])
