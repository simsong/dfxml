
# This software was developed at the National Institute of Standards
# and Technology in whole or in part by employees of the Federal
# Government in the course of their official duties. Pursuant to
# title 17 Section 105 of the United States Code portions of this
# software authored by NIST employees are not subject to copyright
# protection and are in the public domain. For portions not authored
# by NIST employees, NIST has been granted unlimited rights. NIST
# assumes no responsibility whatsoever for its use by other parties,
# and makes no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

__version__ = "0.3.0"

import dfxml.objects as Objects
import logging
import os
import hashlib
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

_nagged_ids = False
_used_ids = set()
_last_id = 1

def _generate_id():
    """
    Creates an ID number unique to all DFXML documents ran through write_sector_hashes_to_db in this process.
    """
    global _used_ids
    global _last_id
    while _last_id in _used_ids:
        _last_id += 1
    _used_ids.add(_last_id)
    return _last_id

sql_schema_files = """CREATE TABLE files(
  obj_id INTEGER NOT NULL,
  partition INTEGER,
  inode INTEGER,
  filename TEXT,
  filesize INTEGER
);"""
sql_schema_block_hashes = """CREATE TABLE block_hashes(
  obj_id INTEGER NOT NULL,
  img_offset INTEGER,
  fs_offset INTEGER,
  file_offset INTEGER,
  len INTEGER NOT NULL,
  md5 TEXT,
  sha1 TEXT
);"""

def write_sector_hashes_to_db(raw_image, dfxml_doc, predicate, db_output_path, pad_sectors=False):
    """
    Produces sector hashes of all files that fit a predicate.
    Predicate function: Takes a FileObject as input; returns True if the FileObject should have its sectors hashed (if possible).
    """
    global _used_ids

    if os.path.exists(db_output_path):
        raise ValueError("Database output path exists.  Aborting - will not overwrite.  (Path: %r.)" % db_output_path)

    conn = sqlite3.connect(db_output_path)
    conn.isolation_level = "EXCLUSIVE"
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(sql_schema_files)
    cursor.execute(sql_schema_block_hashes)
    conn.commit()

    for (obj_no, obj) in enumerate(dfxml_doc):
        if not isinstance(obj, Objects.FileObject):
            continue
        if not predicate(obj):
            continue
        brs = obj.data_brs
        if brs is None:
            continue
        if obj.id is None:
            if not _nagged_ids:
                _logger.info("At least one FileObject had a null .id property.  Generating IDs.")
                _nagged_ids = True
            obj.id = _generate_id()
        else:
            if obj.id in _used_ids:
                _logger.warning("ID reuse: %r." % obj.id)
            _used_ids.add(obj.id)
        try:
            file_offset = 0
            cursor.execute("INSERT INTO files(obj_id, partition, inode, filename, filesize) VALUES (?,?,?,?,?);", (
              obj.id,
              obj.partition,
              obj.inode,
              obj.filename,
              obj.filesize
            ))
            found_incomplete_chunk = False
            for chunk in brs.iter_contents(raw_image, buffer_size=512):
                if found_incomplete_chunk:
                    _logger.debug("File with unexpected mid-stream incomplete byte run: %r." % obj)
                    raise ValueError("Found incomplete sector in middle of byte_runs list.")
                md5obj = hashlib.md5()
                sha1obj = hashlib.sha1()

                md5obj.update(chunk)
                sha1obj.update(chunk)

                if pad_sectors and len(chunk) < 512:
                    found_incomplete_chunk = True
                    remainder = 512 - len(chunk)
                    nulls = remainder * b"0"
                    md5obj.update(nulls)
                    sha1obj.update(nulls)

                #TODO No img_offset or fs_offset for now; could be done with a little byte_runs offset acrobatics, or a request to restore sector hash records in DFXML.
                cursor.execute("INSERT INTO block_hashes(obj_id, img_offset, fs_offset, file_offset, len, md5, sha1) VALUES (?,?,?,?,?,?,?);", (
                  obj.id,
                  None,
                  None,
                  file_offset,
                  len(chunk),
                  md5obj.hexdigest(),
                  sha1obj.hexdigest()
                ))

                file_offset += len(chunk)
            if not obj.filesize is None and file_offset != obj.filesize:
                _logger.warning("The hashed blocks' lengths do not sum to the filesize recorded: respectively, %d and %d.  File ID %r." % (file_offset, obj.filesize, obj.id))
        except AttributeError as e:
            #Some files' contents can't be accessed straightforwardly.  Note and skip.
            _logger.error(e.args[0] + ("  File ID %r." % obj.id))
            _logger.debug("The problem FileObject: %r." % obj)

        #Commit every thousand files
        if obj_no % 1000 == 999:
            _logger.debug("Committing hashes of object number %d." % obj_no)
            conn.commit()
    conn.commit()
    conn.close()

def is_allocated(fobj):
    if fobj.alloc_name and fobj.alloc_inode:
        return True
    elif fobj.alloc:
        return True
    return False

def is_new_file(fobj):
    if not fobj.annos is None:
        return  "new" in fobj.annos
    return None

def is_mod_file(fobj):
    if not fobj.annos is None:
        return  "modified" in fobj.annos
    return None

def is_new_or_mod_file(fobj):
    return is_new_file(fobj) or is_mod_file(fobj)

def main():
    predicates = {
      "all": (lambda x: True),
      "allocated": is_allocated,
      "new": is_new_file,
      "mod": is_mod_file,
      "newormod": is_new_or_mod_file
    }
    if args.predicate is None:
        args.predicate = "new"
    if args.predicate not in predicates:
        raise ValueError("--predicate must be from this list: %r.  Received: %r." % (predicates.keys(), args.predicate))

    if args.xml:
        d = Objects.parse(args.xml)
    else:
        d = Objects.parse(args.disk_image)
    write_sector_hashes_to_db(args.disk_image, d, is_allocated, args.db_output, args.pad)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Walks a file system and outputs sector hashes of all files matching a predicate.  Can be used as a library for the function write_sector_hashes_to_db.")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-x", "--xml", help="Pre-computed DFXML.")
    parser.add_argument("--predicate", help="Condition for selecting files to sector hash.  One of 'new', 'allocated', 'all', 'mod'(ified), 'newormod'.  Default 'allocated'.")
    parser.add_argument("--pad", help="Pad non-full sectors with null bytes.", action="store_true")
    parser.add_argument("disk_image")
    parser.add_argument("db_output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()
