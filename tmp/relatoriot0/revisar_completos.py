from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from pypdf import PdfReader
p=Path('tmp/relatoriot0')
for prefix in ['completa','equacoes']:
 fs=sorted(p.glob(prefix+'-*.png'))
 for z in range(0,len(fs),8):
  canvas=Image.new('RGB',(1200,850),'#888888')
  for j,f in enumerate(fs[z:z+8]):
   im=Image.open(f);im.thumbnail((295,405));canvas.paste(im,((j%4)*300,(j//4)*425+20));ImageDraw.Draw(canvas).text(((j%4)*300+5,(j//4)*425+3),f.stem,fill='white')
  canvas.save(p/(prefix+'-montage'+str(z)+'.jpg'))
for f in ['Calculos_Corrigidos_Resolucao_Completa.pdf','Equações_do_RelatórioT0.pdf']:
 r=PdfReader(f);print(f,len(r.pages));print([len(p.extract_text()) for p in r.pages])
