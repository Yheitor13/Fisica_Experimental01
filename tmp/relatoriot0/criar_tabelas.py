from pathlib import Path
import ast, math, statistics, re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
root=Path.cwd()
source=(root/'tmp/relatoriot0/criar_relatorio.py').read_text(encoding='utf-8')
# Reuse only the data and calculation statements, without executing report authoring.
tree=ast.parse(source)
start=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pieces' for t in n.targets))
end=next(i for i in range(start,len(tree.body)) if isinstance(tree.body[i],ast.For))
exec(compile(ast.Module(body=tree.body[start:end+1],type_ignores=[]),'data','exec'))
for name,file in [('TimesLocal','times.ttf'),('TimesLocalBold','timesbd.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('TimesLocal',normal='TimesLocal',bold='TimesLocalBold')
base=ParagraphStyle('base',fontName='TimesLocal',fontSize=10,leading=12)
cap=ParagraphStyle('caption',parent=base,fontSize=12,leading=15,spaceAfter=10)
note=ParagraphStyle('note',parent=base,fontSize=10,leading=13,spaceBefore=6)
W=A4[0]-142
story=[]
def para(t,align=0,bold=False):
 s=ParagraphStyle('c',parent=base,alignment=align,fontName='TimesLocalBold' if bold else 'TimesLocal')
 return Paragraph(str(t),s)
def f(v,n=6):return format(v,f'.{n}f').replace('.',',')
def key(k):return re.sub(r'(\d)',r'<sub>\1</sub>',k)
def table(title,heads,rows,widths,notes,groups=None):
 story.append(Paragraph(title,cap))
 cells=[[para(h,0 if i==0 else 1,True) for i,h in enumerate(heads)]]
 cells += [[para(c,0 if i==0 else (1 if i==1 and len(heads)>4 else 2)) for i,c in enumerate(row)] for row in rows]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
 commands=[('LINEABOVE',(0,0),(-1,0),.8,colors.black),('LINEBELOW',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,-1),(-1,-1),.8,colors.black),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
 if groups:
  for a,b in groups:
   commands.append(('SPAN',(0,a),(0,b)))
   if a>1:commands.append(('TOPPADDING',(0,a),(-1,a),13))
 t.setStyle(TableStyle(commands));story.append(t)
 for n in notes:story.append(Paragraph(n,note))
def dimensional(stat=False):
 rows=[];groups=[]
 for ix,(name,data,inst) in enumerate(pieces):
  a=len(rows)+1
  for j,(k,values) in enumerate(data.items()):
   vals=[f(s[k]) for s in stats[ix]] if stat else [f(x,2) for x in values]
   rows.append([name if j==0 else '',key(k)]+vals)
  groups.append((a,len(rows)))
 return rows,groups
rows,groups=dimensional()
table('Tabela 1 - Medidas dimensionais das quatro peças (cm)',['Peça','Grandeza','Leitura 1','Leitura 2','Leitura 3'],rows,[145,65,81,81,W-372],['Fonte: registros experimentais apresentados no Relatório T0 (2026).','Nota: D é o diâmetro da bateria; D<sub>1</sub>, o diâmetro do furo; D<sub>2</sub>, o diâmetro externo da arruela ou do ressalto; D<sub>3</sub>, o diâmetro da base; h, h<sub>1</sub> e h<sub>2</sub>, as alturas; L, a largura da corda do corte.'],groups)
story.append(PageBreak())
rows,groups=dimensional(True)
table('Tabela 2 - Tratamento estatístico das dimensões (cm)',['Peça','Grandeza','Média','DP','σ<sub>est</sub>','σ<sub>total</sub>'],rows,[111,54,72,72,72,W-381],['Fonte: elaboração a partir das medidas da Tabela 1 (2026).','Notas: DP = desvio padrão amostral; σ<sub>est</sub> = incerteza estatística da média; σ<sub>total</sub> = incerteza total. Cada grandeza possui três leituras.','Incerteza instrumental adotada: 0,001 cm para a bateria e 0,005 cm para as demais peças. Os valores intermediários são apresentados com seis casas decimais.'],groups)
story.append(PageBreak())
rows=[[pieces[i][0],f(v,8),f(u,8),f(100*u/v,2)] for i,(v,u) in enumerate(vols)]
table('Tabela 3 - Volumes e incertezas propagadas',['Peça','Volume<br/>(cm³)','Incerteza<br/>(cm³)','Incerteza relativa<br/>(%)'],rows,[148,100,100,W-348],['Fonte: elaboração a partir das dimensões médias e incertezas totais (2026).','Nota: valores apresentados antes do arredondamento final; a incerteza relativa corresponde a 100σ<sub>V</sub>/V.'])
story.append(Spacer(1,38))
final=['(1,00 ± 0,03) × 10<super>0</super>','(1,9 ± 0,9) × 10<super>-1</super>','(1,17 ± 0,06) × 10<super>1</super>','(3,0 ± 0,7) × 10<super>0</super>']
table('Tabela 4 - Resultados finais dos volumes',['Peça','Volume com incerteza (cm³)'],[[p[0],v] for p,v in zip(pieces,final)],[210,W-210],['Fonte: resultados da Tabela 3, com arredondamento final (2026).','Nota: incertezas com um algarismo significativo e volumes na mesma casa decimal das respectivas incertezas.'])
output=root/'Tabelas_RelatórioT0.pdf'
SimpleDocTemplate(str(output),pagesize=A4,leftMargin=71,rightMargin=71,topMargin=65,bottomMargin=57,title='Tabelas - Relatório T0',author='').build(story)
r=PdfReader(output)
assert len(r.pages)==3,len(r.pages)
assert all('Tabela' in p.extract_text() for p in r.pages)
print(str(output));print('Páginas:',len(r.pages))
