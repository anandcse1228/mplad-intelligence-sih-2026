import os
import zipfile

def create_project_zip():
    source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_zip = r"C:\Users\HP\.gemini\antigravity\brain\60878b3f-b33c-4a48-a2ed-c7b33c750f1c\mplads_intelligence_project.zip"
    
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', '.vscode', '.idea'}
    exclude_extensions = {'.pyc', '.pyo', '.DS_Store'}

    print(f"Creating project ZIP from: {source_dir}")
    print(f"Target destination: {target_zip}")

    with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in exclude_extensions:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

    zip_size = os.path.getsize(target_zip) / (1024 * 1024)
    print(f"[OK] Project ZIP created successfully: {zip_size:.2f} MB")

if __name__ == '__main__':
    create_project_zip()
