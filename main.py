
from config import oldVer, newVer, zipDir, insDir, settings 
import zipfile


for servername in settings.keys():
    # ZIPファイルを解凍する
    pathFrom    = f"{zipDir}/bedrock-server-{newVer}.zip"
    pathTo      = f"{insDir}/bedrock-server-{newVer}_{servername}"
    with zipfile.ZipFile(pathFrom, 'r') as zipf:
        # 解凍先のフォルダーを指定する（存在しない場合は自動的に作成される）
        zipf.extractall(pathTo)



    config.settings[servername]
    print()

    #zip解凍
    
    #名前変更





    #creativeコピー
