import zipfile
import os

def create_zip(source_dir, output_filename):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '.git', '__pycache__', 'chroma_db', 'site-packages']]
            
            for file in files:
                if file.endswith('.zip') or file.endswith('.pyc') or file == 'create_backup.py':
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                print(f"Adding {arcname}")
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    create_zip('.', r'C:\Users\krunal\OneDrive\Desktop\project_backup_final.zip')
    print("Backup created successfully!")
