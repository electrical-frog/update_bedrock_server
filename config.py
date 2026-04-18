
from pathlib import Path


projectDir = Path(__file__).resolve().parent

oldVer = 'auto'
newVer = 'latest'

zipDir = './downloads'
insDir = '/root/bedrock_server'

downloadLinksApiUrl = 'https://net-secondary.web.minecraft-services.net/api/v1.0/download/links'
downloadType = 'serverBedrockLinux'
downloadUserAgent = 'update_bedrock_server/1.0'
apiTimeoutSec = 30
downloadTimeoutSec = 300

serverBinaryName = 'bedrock_server'
serverPropertiesName = 'server.properties'
copyTargets = [
        'worlds',
        'allowlist.json',
        'permissions.json',
]
bedrockServerMode = 0o700
startScriptPrefix = 'start_server_'
startScriptCdPrefix = 'cd /root/'
currentLinkPrefix = 'current_'

restartAfterUpdate = True
systemctlPath = '/usr/bin/systemctl'
systemdUnitTemplate = 'bedrock@.service'
systemdUnitDir = '/etc/systemd/system'
systemdServicePrefix = 'bedrock@'
systemdServiceSuffix = '.service'
systemdDescriptionPrefix = 'Minecraft Bedrock Server'
systemdRestartSec = 10

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
        'survival2':{
            'gamemode'      :'survival',
            'difficulty'    :'easy',
            'server-port'   :'19136',
            'server-portv6' :'19137',
            'allow-list'    :'true',
        },
}
