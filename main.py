
from config import oldVer, newVer, zipDir, insDir, settings 
import zipfile
import shutil
import os


def edit_line(filename, target_prefix, replacement_line):
    edited_lines = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith(target_prefix):
                edited_lines.append(replacement_line + "\n")
            else:
                edited_lines.append(line)

    with open(filename, 'w') as file:
        file.writelines(edited_lines)


for servername in settings.keys():
    
    # zip解凍
    pathFrom    = f"{zipDir}/bedrock-server-{newVer}.zip"
    pathTo      = f"{insDir}/bedrock-server-{newVer}_{servername}"
    with zipfile.ZipFile(pathFrom, 'r') as zipf:
        # 解凍先のフォルダーを指定する（存在しない場合は自動的に作成される）
        zipf.extractall(pathTo)
    

    # server.propertiesの編集
    for key in settings[servername].keys():
        edit_line(f"{pathTo}/server.properties", f"{key}=", f"{key}={settings[servername][key]}")


    # worldsのコピー
    pathFrom    = f"{insDir}/bedrock-server-{oldVer}_{servername}/worlds"
    pathTo      = f"{insDir}/bedrock-server-{newVer}_{servername}/worlds"
    try:
        shutil.copytree(pathFrom, pathTo)
    except Exception as e:
        print(f"エラー: {e}")
    
    
    # allowlist.jsonのコピー
    pathFrom    = f"{insDir}/bedrock-server-{oldVer}_{servername}/allowlist.json"
    pathTo      = f"{insDir}/bedrock-server-{newVer}_{servername}/allowlist.json"
    try:
        shutil.copy2(pathFrom, pathTo)
    except Exception as e:
        print(f"エラー: {e}")

    
    # permissions.jsonのコピー
    pathFrom    = f"{insDir}/bedrock-server-{oldVer}_{servername}/permissions.json"
    pathTo      = f"{insDir}/bedrock-server-{newVer}_{servername}/permissions.json"
    try:
        shutil.copy2(pathFrom, pathTo)
    except Exception as e:
        print(f"エラー: {e}")


    # bedrock_serverのパーミッション設定
    pathTo      = f"{insDir}/bedrock-server-{newVer}_{servername}/bedrock_server"
    os.chmod(pathTo, 0o700)
    

    # start_serverの編集
    edit_line(f"{insDir}/start_server_{servername}.sh", "cd /root/", f"cd /root/bedrock_server/bedrock-server-{newVer}_{servername}/")
    

    print("Done")





