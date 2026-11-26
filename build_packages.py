"""Build reproducible browser-app installer ZIPs. Uses only Python stdlib."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'releases'
VERSION = '3.0.0'
APP_FILES = ['index.html','app.js','esd-core.js','style.css','README.md','使用说明.txt','server.py','requirements.txt','download_models.py','legacy-v1.html']

def package(platform):
    name = f'SurgMark-ESD-{VERSION}-{platform}.zip'
    items = {f'SurgMark-ESD/{f}': ROOT/f for f in APP_FILES}
    if platform == 'Windows':
        for f in ['install-windows.cmd','install-windows.ps1']:
            items[f] = ROOT/f
        items['SurgMark-ESD/Start-SurgMark.cmd'] = ROOT/'Start-SurgMark.cmd'
    else:
        items['install-macos.command'] = ROOT/'install-macos.command'
        items['SurgMark-ESD/Start-SurgMark.command'] = ROOT/'Start-SurgMark.command'
    with zipfile.ZipFile(OUT/name,'w',zipfile.ZIP_DEFLATED) as z:
        for target,path in sorted(items.items()):
            info=zipfile.ZipInfo(target, (2026,11,26,0,0,0))
            info.create_system=3
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100755 if target.endswith('.command') else 0o100644)<<16
            z.writestr(info,path.read_bytes())
    with zipfile.ZipFile(OUT/name) as z:
        assert z.testzip() is None
        assert all(z.read(target)==path.read_bytes() for target,path in items.items())
    return name

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    names=[package('Windows'),package('macOS')]
    hashes={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}
    (OUT/'SHA256SUMS.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()))
    (OUT/'manifest.json').write_text(json.dumps({'version':VERSION,'type':'local-browser-app-installer','platforms':['Windows','macOS'],'requires_python_for_manual_annotation':False,'ai_models_included':False,'sha256':hashes},indent=2)+'\n')
    print(json.dumps({'packages':names,'sha256':hashes},indent=2))
