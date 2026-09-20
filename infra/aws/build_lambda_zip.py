"""
Creates a production-ready AWS Lambda deployment zip file with explicit UNIX permissions.
This prevents Windows NTFS file permission stripping on compiled C-extensions (.so files).
"""

import os
import stat
import zipfile

def build_lambda_zip(source_dir: str, output_zip: str):
    print(f"Packaging {source_dir} -> {output_zip} with UNIX permissions...")
    
    with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(source_dir):
            for d in dirs:
                dir_path = os.path.join(root, d)
                arc_name = os.path.relpath(dir_path, source_dir).replace('\\', '/') + '/'
                zinfo = zipfile.ZipInfo(arc_name)
                # UNIX directory mode: 0o755 (drwxr-xr-x)
                zinfo.external_attr = (stat.S_IFDIR | 0o755) << 16
                zf.writestr(zinfo, '')

            for f in files:
                file_path = os.path.join(root, f)
                arc_name = os.path.relpath(file_path, source_dir).replace('\\', '/')
                with open(file_path, 'rb') as fp:
                    data = fp.read()
                
                zinfo = zipfile.ZipInfo(arc_name)
                if f.endswith('.so') or f.endswith('.sh'):
                    # UNIX executable mode: 0o755 (-rwxr-xr-x)
                    zinfo.external_attr = (stat.S_IFREG | 0o755) << 16
                else:
                    # UNIX regular file mode: 0o644 (-rw-r--r--)
                    zinfo.external_attr = (stat.S_IFREG | 0o644) << 16
                
                zf.writestr(zinfo, data)

    zip_size = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"Successfully created {output_zip}: {zip_size:.2f} MB")

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dist_dir = os.path.join(repo_root, "dist_lambda")
    out_zip = os.path.join(repo_root, "workline_backend.zip")
    build_lambda_zip(dist_dir, out_zip)
