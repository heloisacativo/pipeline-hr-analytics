import kagglehub
import zipfile
import os
import shutil

path = kagglehub.dataset_download("pavansubhasht/ibm-hr-analytics-attrition-dataset")

print("Path to dataset files:", path)
files = os.listdir(path)
print(f"Arquivos baixados: {files}")

os.makedirs('data/raw', exist_ok=True)

for file in files:
    source_file = os.path.join(path, file)
    
    if file.endswith('.zip'):
        with zipfile.ZipFile(source_file, 'r') as zip_ref:
            zip_ref.extractall('data/raw')
            print(f"Arquivo {file} descompactado em data/raw")
    else:
        dest_file = os.path.join('data/raw', file)
        shutil.copy2(source_file, dest_file)
        print(f"Arquivo {file} copiado para data/raw")

print("Dataset disponível em data/raw")