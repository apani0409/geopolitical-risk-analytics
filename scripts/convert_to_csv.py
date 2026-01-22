#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import sys
import logging

def json_to_csv(src_path: Path, dst_path: Path):
    import pandas as pd

    with src_path.open('r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        df = pd.json_normalize(data)
    elif isinstance(data, dict):
        # try to find a list of records inside the dict
        list_found = None
        for v in data.values():
            if isinstance(v, list):
                list_found = v
                break
        if list_found is not None:
            df = pd.json_normalize(list_found)
        else:
            df = pd.json_normalize([data])
    else:
        raise ValueError(f"Unsupported JSON root type: {type(data)}")

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dst_path, index=False)


def xml_to_csv(src_path: Path, dst_path: Path):
    import pandas as pd

    try:
        df = pd.read_xml(src_path)
    except Exception:
        # fallback: try simple element-based parsing
        import xml.etree.ElementTree as ET
        tree = ET.parse(src_path)
        root = tree.getroot()
        records = []
        # if root has many children each representing a record
        # convert their subelements to dicts
        for child in list(root):
            rec = {}
            for elem in child.iter():
                if elem is child:
                    continue
                # use tag names; for nested tags use tag text only
                rec[elem.tag] = elem.text
            if rec:
                records.append(rec)
        if records:
            df = pd.json_normalize(records)
        else:
            # last resort: try to coerce root text
            df = pd.DataFrame([{root.tag: root.text}])

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dst_path, index=False)


def convert_file(path: Path, src_root: Path, dst_root: Path):
    rel = path.relative_to(src_root)
    out_path = dst_root.joinpath(rel).with_suffix('.csv')
    logging.info(f"Converting {path} -> {out_path}")
    try:
        if path.suffix.lower() == '.json':
            json_to_csv(path, out_path)
        elif path.suffix.lower() == '.xml':
            xml_to_csv(path, out_path)
        else:
            logging.warning(f"Skipping unsupported file: {path}")
            return False
        return True
    except Exception as e:
        logging.error(f"Failed to convert {path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Convert JSON and XML files to CSV (recursively)')
    parser.add_argument('--source', '-s', required=True, help='Source data folder')
    parser.add_argument('--dest', '-d', required=True, help='Destination folder for CSVs')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    src_root = Path(args.source).resolve()
    dst_root = Path(args.dest).resolve()

    if not src_root.exists():
        logging.error(f"Source folder not found: {src_root}")
        sys.exit(2)

    total = 0
    converted = 0
    for path in src_root.rglob('*'):
        if path.is_file() and path.suffix.lower() in ['.json', '.xml']:
            total += 1
            ok = convert_file(path, src_root, dst_root)
            if ok:
                converted += 1

    logging.info(f"Done. Found {total} files; converted {converted} files to CSV in {dst_root}")


if __name__ == '__main__':
    main()
