import os
import zipfile
import subprocess
import argparse
import asyncio

async def extract_zip(zip_file, destination_folder, password):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(destination_folder, pwd=bytes(password, 'utf-8'))
        print(f"Extraído: {zip_file}")
    except zipfile.BadZipFile:
        print(f"Erro: {zip_file} não é um arquivo zip válido.")
    except RuntimeError as e:
        if "Bad password" in str(e):
            print(f"Erro: Senha incorreta para {zip_file}")
        else:
            print(f"Erro ao extrair {zip_file}: {e}")

async def execute_exe(exe_path):
    try:
        print(f"Executando: {exe_path}")
        process = await asyncio.create_subprocess_exec(
            exe_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            print(f"Executado: {exe_path}")
        else:
            print(f"Erro ao executar {exe_path}: {stderr.decode()}")
    except Exception as e:
        print(f"Erro ao executar {exe_path}: {e}")

async def process_zip(zip_file, destination_folder, password):
    await extract_zip(zip_file, destination_folder, password)
    for root, _, files in os.walk(destination_folder):
        for file in files:
            if file.endswith('.exe'):
                exe_path = os.path.join(root, file)
                await execute_exe(exe_path)

async def extract_and_execute(source_folder, destination_folder, password):
    try:
        if os.path.isfile(source_folder) and source_folder.endswith('.zip'):
            zip_files = [source_folder]
        else:
            zip_files = [os.path.join(root, file) for root, _, files in os.walk(source_folder) 
                         for file in files if file.endswith('.zip')]

        for zip_file in zip_files:
            await process_zip(zip_file, destination_folder, password)

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrair e executar arquivos de um arquivo zip.")
    parser.add_argument("source", help="Arquivo zip de origem ou pasta contendo arquivos zip")
    parser.add_argument("destination", help="Pasta de destino para os arquivos extraídos")
    parser.add_argument("password", help="Senha para o(s) arquivo(s) zip")

    args = parser.parse_args()

    asyncio.run(extract_and_execute(args.source, args.destination, args.password))