# update_bedrock_server


## 概要
Linuxで立てたBedrockサーバーのバージョンを更新します。

## 特徴
マップ情報を引き継げます。

## インストール
```
git clone https://github.com/electrical-frog/update_bedrock_server
```

## 使用方法

step 1.
  download bedrockserver from
  https://www.minecraft.net/ja-jp/download/server/bedrock
  to 任意のフォルダ

step 2. 
  edit config.py
  ```
oldVer = '1.20.80.05'
newVer = '1.21.0.03'

zipDir = '/mnt/share02/share'
insDir = '/root/bedrock_server'

settings = {
        'survival':{
            'gamemode'      :'survival',
            'difficulty'    :'easy',
            'server-port'   :'19132',
            'server-portv6' :'19133',
        },
        'creative':{
            'gamemode'      :'creative',
            'difficulty'    :'easy',
            'server-port'   :'19134',
            'server-portv6' :'19135',
        },
}
  
  ```

step 3.

  exec bellow code
  ```:console
  # python3 main.py
  ```

step 4.（設定していない場合のみ
crontabを設定します
```:crontab -e
@reboot /usr/bin/sleep 10; /usr/bin/bash /root/bedrock_server/start_server_survival.sh
@reboot /usr/bin/sleep 20; /usr/bin/bash /root/bedrock_server/start_server_creative.sh

```

step 5.

サーバーを再起動します。   
