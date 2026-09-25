from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile,ZIP_DEFLATED
import ast,math,statistics,hashlib,json,re
from lxml import etree as E
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL,WD_BREAK,WD_TAB_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
root=Path.cwd();work=root/'tmp/template'
# Source measurements, calculations and MathML helpers.
src=(root/'tmp/relatoriot0/criar_relatorio.py').read_text(encoding='utf-8-sig');tree=ast.parse(src)
a=next(j for j,t in enumerate(tree.body) if isinstance(t,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='pieces' for v in t.targets));b=next(j for j in range(a,len(tree.body)) if isinstance(tree.body[j],ast.For))
exec(compile(ast.Module(body=tree.body[a:b+1],type_ignores=[]),'data','exec'))
exec((root/'tmp/relatoriot0/criar_formulas.py').read_text(encoding='utf-8-sig').split('sections=[]')[0])
xslt=E.XSLT(E.parse('C:/Program Files/Microsoft Office/root/Office16/MML2OMML.XSL'))
doc=Document(root/'refs/template_tcc.docx')
# Replace documented content slots while retaining the source style system.
body=doc._element.body
for node in list(body):
 if node.tag!=qn('w:sectPr'):body.remove(node)
sec=doc.sections[0]
for el in list(sec._sectPr):
 if E.QName(el).localname in ['headerReference','footerReference','pgNumType','titlePg']:sec._sectPr.remove(el)
sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(3);sec.left_margin=Cm(3);sec.right_margin=Cm(2);sec.bottom_margin=Cm(2);sec.header_distance=Cm(1.25);sec.footer_distance=Cm(1.25)
for nm in ['Normal','Heading 1','Heading 2','Instituição','Autor','Título do trabalho','Subtítulo do trabalho','Cidade_Ano','Tipo do trabalho_Orientador','Resumo','Seção não numerada']:
 st=doc.styles[nm];st.font.size=Pt(12);st.font.color.rgb=RGBColor(0,0,0)
 if nm not in ['Título do trabalho','Subtítulo do trabalho','Cidade_Ano','Tipo do trabalho_Orientador']:st.font.name='Times New Roman'
 st.paragraph_format.space_after=Pt(0);st.paragraph_format.space_before=Pt(0)
 st.paragraph_format.line_spacing=1.5
 st.paragraph_format.first_line_indent=Cm(0);st.paragraph_format.left_indent=Cm(0);st.paragraph_format.right_indent=Cm(0)
 for tag in ['numPr','pBdr']:
  for el in list(st.element.xpath('./w:pPr/w:'+tag)):el.getparent().remove(el)
normal=doc.styles['Normal'];normal.paragraph_format.alignment=AL.JUSTIFY;normal.paragraph_format.first_line_indent=Cm(1.25)
for nm in ['Heading 1','Heading 2','Seção não numerada']:
 st=doc.styles[nm];st.font.bold=True;st.paragraph_format.keep_with_next=True;st.paragraph_format.space_after=Pt(18);st.paragraph_format.space_before=Pt(18)
 st.paragraph_format.alignment=AL.CENTER if nm=='Seção não numerada' else AL.LEFT
 st.paragraph_format.page_break_before=nm in ['Heading 1','Seção não numerada']
outline=OxmlElement('w:outlineLvl');outline.set(qn('w:val'),'0');doc.styles['Seção não numerada'].element.get_or_add_pPr().append(outline)
for nm in ['toc 1','toc 2']:
 st=doc.styles[nm];st.font.name='Times New Roman';st.font.size=Pt(12);st.font.color.rgb=RGBColor(0,0,0);st.paragraph_format.line_spacing=1.5
# No automatic template numbering; titles carry their explicit section numbers.
for el in list(doc.settings.element):
 if E.QName(el).localname in ['evenAndOddHeaders','updateFields']:doc.settings.element.remove(el)
upd=OxmlElement('w:updateFields');upd.set(qn('w:val'),'true');doc.settings.element.append(upd)
def para(text='',style='Normal',center=False,indent=True):
 p=doc.add_paragraph(text,style);p.paragraph_format.widow_control=True
 if center:p.alignment=AL.CENTER
 if not indent:p.paragraph_format.first_line_indent=Cm(0)
 return p
def front_title(t):
 p=para(t,'Resumo',True,False);p.paragraph_format.space_after=Pt(18)
 for r in p.runs:r.bold=True
 return p
def gap(pt):
 p=para('',indent=False);p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(pt);p.paragraph_format.space_before=Pt(0);p.paragraph_format.keep_with_next=True
 p.add_run().font.size=Pt(1)
def newpage():doc.add_page_break()
def heading(text,level=1):
 p=para(text,'Heading '+str(level),indent=False)
 return p
def formula(mml,number=None):
 p=para('',indent=False);p.alignment=AL.CENTER;p.paragraph_format.line_spacing=1;p.paragraph_format.space_before=Pt(10);p.paragraph_format.space_after=Pt(10);p.paragraph_format.keep_together=True
 if number:
  p.alignment=AL.LEFT;p.paragraph_format.tab_stops.add_tab_stop(Cm(7.4),WD_TAB_ALIGNMENT.CENTER);p.paragraph_format.tab_stops.add_tab_stop(Cm(16),WD_TAB_ALIGNMENT.RIGHT);p.add_run('\t')
 xml=E.fromstring(('<math xmlns="http://www.w3.org/1998/Math/MathML">'+mml+'</math>').encode());mathnode=xslt(xml).getroot();p._p.append(mathnode)
 if number:p.add_run('\t('+str(number)+')')
 return p
def caption(text):
 p=para(text,indent=False);p.paragraph_format.line_spacing=1;p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(12);p.paragraph_format.space_after=Pt(6)
 for r in p.runs:r.font.size=Pt(10)
 return p
def source(text):
 p=para(text,indent=False);p.paragraph_format.line_spacing=1;p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(8)
 for r in p.runs:r.font.size=Pt(10)
 return p
def table(title,headers,rows,widths):
 caption(title);t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for cell,w,val in zip(t.rows[0].cells,widths,headers):cell.width=Cm(w);cell.text=val
 for values in rows:
  cells=t.add_row().cells
  for c,w,val in zip(cells,widths,values):c.width=Cm(w);c.text=str(val)
 for j,r in enumerate(t.rows):
  trpr=r._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
  if j==0:trpr.append(OxmlElement('w:tblHeader'))
  for k,c in enumerate(r.cells):
   c.vertical_alignment=1
   pr=c._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
   for side in ['top','bottom','left','right']:
    edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single' if (side=='top' and j==0) or (side=='bottom' and j in [0,len(t.rows)-1]) else 'nil');edge.set(qn('w:sz'),'6');edge.set(qn('w:color'),'000000');borders.append(edge)
   pr.append(borders)
   for p in c.paragraphs:
    p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(4);p.paragraph_format.space_before=Pt(4);p.alignment=AL.LEFT if k==0 else AL.CENTER
    if len(rows)<6:p.paragraph_format.keep_with_next=j<len(t.rows)-1
    for run in p.runs:run.font.name='Times New Roman';run.font.size=Pt(10);run.bold=j==0
 return t
def f(x,k=6):return format(x,f'.{k}f').replace('.',',')
def sym(k):return k.translate(str.maketrans('123','₁₂₃'))
def field(p,code):
 r=OxmlElement('w:r');fld=OxmlElement('w:fldChar');fld.set(qn('w:fldCharType'),'begin');r.append(fld);p._p.append(r)
 r=OxmlElement('w:r');txt=OxmlElement('w:instrText');txt.set(qn('xml:space'),'preserve');txt.text=' '+code+' ';r.append(txt);p._p.append(r)
 r=OxmlElement('w:r');fld=OxmlElement('w:fldChar');fld.set(qn('w:fldCharType'),'separate');r.append(fld);p._p.append(r)
 r=OxmlElement('w:r');t=OxmlElement('w:t');t.text='';r.append(t);p._p.append(r)
 r=OxmlElement('w:r');fld=OxmlElement('w:fldChar');fld.set(qn('w:fldCharType'),'end');r.append(fld);p._p.append(r)
# Cover adapted from template roles.
para('UNIVERSIDADE FEDERAL DE UBERLÂNDIA','Instituição',True,False)
para('INSTITUTO DE FÍSICA','Instituição',True,False)
gap(50);para('INTEGRANTES: [.......]','Autor',True,False)
gap(78);para('RELATÓRIO T0','Título do trabalho',True,False)
para('Medidas dimensionais e determinação de volumes','Subtítulo do trabalho',True,False)
para('com propagação de incertezas','Subtítulo do trabalho',True,False)
gap(230);para('Uberlândia','Cidade_Ano',True,False);para('2026','Cidade_Ano',True,False)
# Front matter starts the page count, with no visible header.
sec=doc.add_section(WD_SECTION_START.NEW_PAGE)
sec.header.is_linked_to_previous=False;sec.footer.is_linked_to_previous=False
pg=OxmlElement('w:pgNumType');pg.set(qn('w:start'),'1');sec._sectPr.append(pg)
para('INTEGRANTES: [.......]','Autor',True,False)
gap(65);para('RELATÓRIO T0','Título do trabalho',True,False)
para('Medidas dimensionais e determinação de volumes','Subtítulo do trabalho',True,False)
para('com propagação de incertezas','Subtítulo do trabalho',True,False)
gap(40)
p=para('Relatório apresentado à disciplina Física Geral Experimental I, do Instituto de Física da Universidade Federal de Uberlândia.','Tipo do trabalho_Orientador',indent=False);p.paragraph_format.left_indent=Cm(8);p.paragraph_format.line_spacing=1
for text in ['Curso: [.......]','Turma: [.......]','Matrículas: [.......]','Docente: [.......]','Data de realização: [.......]']:
 p=para(text,'Tipo do trabalho_Orientador',indent=False);p.paragraph_format.left_indent=Cm(8);p.paragraph_format.line_spacing=1;p.paragraph_format.space_before=Pt(8)
gap(130);para('Uberlândia','Cidade_Ano',True,False);para('2026','Cidade_Ano',True,False)
newpage();front_title('RESUMO')
resumo='Este trabalho determina os volumes de quatro peças a partir de medidas dimensionais realizadas com paquímetro e avalia a influência das incertezas dessas medidas nos resultados. O estudo considera uma bateria cilíndrica, uma arruela, um cilindro com ressalto e furo e uma peça semelhante com corte plano. O tratamento utiliza três leituras por dimensão, calcula a média, o desvio padrão amostral e a incerteza estatística da média, combina a contribuição instrumental e propaga a incerteza para o volume. A modelagem representa as peças compostas pela soma de duas arruelas e desconta, na última peça, o volume de um segmento circular. O procedimento mantém todas as leituras confirmadas e usa centímetros como unidade de comprimento. O cálculo fornece volumes aproximados de um, dezenove centésimos, onze inteiros e sete décimos e três centímetros cúbicos, respectivamente. A incerteza relativa varia de dois inteiros e cinquenta e seis centésimos por cento a quarenta e seis inteiros e cinquenta e cinco centésimos por cento. A análise identifica a dispersão das alturas como a principal limitação da arruela e da peça com corte. Os resultados das peças compostas permanecem condicionados à hipótese geométrica de furo com diâmetro uniforme ao longo de toda a altura considerada.'
assert 150<=len(resumo.split())<=500
para(resumo,indent=False);gap(12);para('Palavras-chave: Medidas dimensionais. Paquímetro. Volume. Propagação de incertezas.',indent=False)
newpage();front_title('ABSTRACT')
abstract='This study determines the volumes of four objects from dimensional measurements taken with a caliper and evaluates how measurement uncertainties affect the results. It considers a cylindrical battery, a washer, a stepped cylinder with a hole, and a similar object with a flat cut. The analysis uses three readings per dimension, calculates the mean, the sample standard deviation, and the statistical uncertainty of the mean, combines the instrumental contribution, and propagates the resulting uncertainty to the volume. The geometric model represents each stepped object as the sum of two washers and subtracts the volume of a circular segment from the object with the flat cut. All confirmed readings are retained, and lengths are expressed in centimeters. The calculated volumes are approximately one, nineteen hundredths, eleven point seven, and three cubic centimeters, respectively. Relative uncertainties range from two point five six to forty-six point five five percent. The analysis identifies the scatter in height measurements as the main limitation for the washer and the object with the flat cut. Results for the stepped objects remain conditional on the geometric assumption of a uniform hole extending through the full height included in the model.'
para(abstract,indent=False);gap(12);para('Keywords: Dimensional measurements. Caliper. Volume. Uncertainty propagation.',indent=False)
newpage();front_title('LISTA DE TABELAS')
for j,t in enumerate(['Medidas dimensionais das quatro peças','Tratamento estatístico das dimensões','Volumes e incertezas propagadas','Resultados finais dos volumes'],1):
 p=para(f'Tabela {j} – {t}\t',indent=False);p.paragraph_format.tab_stops.add_tab_stop(Cm(16),WD_TAB_ALIGNMENT.RIGHT);field(p,'PAGEREF tab'+str(j)+' \\h')
newpage();front_title('SUMÁRIO');field(para('',indent=False),'TOC \\o "1-2" \\h \\z \\t "Seção não numerada,1"')
# Textual matter continues count from front matter.
sec=doc.add_section(WD_SECTION_START.NEW_PAGE);sec.header.is_linked_to_previous=False;sec.footer.is_linked_to_previous=False
for el in list(sec._sectPr):
 if E.QName(el).localname=='pgNumType':sec._sectPr.remove(el)
p=sec.header.paragraphs[0];p.alignment=AL.RIGHT;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.line_spacing=1;field(p,'PAGE')
for run in p.runs:run.font.size=Pt(10)
intro_heading=heading('1 INTRODUÇÃO');intro_heading.paragraph_format.page_break_before=False
para('A apresentação de uma medida experimental requer uma estimativa acompanhada de sua incerteza. Em medidas dimensionais, a dispersão entre leituras e a contribuição do instrumento influenciam tanto os comprimentos medidos diretamente quanto os volumes calculados a partir deles. O tratamento estatístico permite avaliar essas contribuições e apresentar resultados com arredondamento compatível com a precisão obtida (Iwamoto et al., 2014).')
para('Este trabalho tem como objetivo determinar os volumes de uma bateria cilíndrica, uma arruela, um cilindro com ressalto e furo e uma peça semelhante com corte plano, utilizando os registros do roteiro de laboratório (Sousa, 2026). Para isso, calcula médias, desvios padrão, incertezas estatísticas e totais e propaga essas incertezas pelas expressões geométricas dos volumes.')
para('A análise também compara as incertezas relativas e identifica as dimensões que mais influenciam os resultados. A interpretação considera as limitações das três leituras por grandeza e as hipóteses necessárias para representar as peças por sólidos geométricos ideais.')
heading('2 FUNDAMENTAÇÃO TEÓRICA')
heading('2.1 Tratamento das medidas',2)
para('Para três leituras de uma dimensão x, a média fornece a estimativa usada no cálculo do volume. O desvio padrão amostral descreve a dispersão das leituras em torno dessa média e utiliza o divisor N − 1, com N igual ao número de medidas (Iwamoto et al., 2014).')
x=i('x');N=i('N');xb='<mover>'+x+op('¯')+'</mover>';xi=sub(x,i('i'));sumx='<munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>N</mi></munderover>'
formula(row(xb,op('='),frac(row(sub(x,n(1)),op('+'),sub(x,n(2)),op('+'),sub(x,n(3))),n(3))),1)
formula(row(i('s'),op('='),sqrt(frac(row(sumx,sq(row(xi,op('−'),xb))),row(N,op('−'),n(1))))),2)
para('A incerteza estatística da média é obtida dividindo o desvio padrão pela raiz do número de leituras. O erro total adotado no roteiro combina essa incerteza com a contribuição instrumental pela soma dos quadrados (Sousa, 2026).')
formula(row(sig(i('est')),op('='),frac(i('s'),sqrt(N))),3)
formula(row(sig(i('total')),op('='),sqrt(row(sup(sig(i('est')),2),op('+'),sup(sig(i('inst')),2)))),4)
heading('2.2 Propagação das incertezas',2)
para('O volume depende de várias dimensões. Para dimensões distintas consideradas sem correlação, a propagação de primeira ordem combina as contribuições de cada dimensão por meio das derivadas da expressão completa do volume, avaliadas nas médias.')
formula(row(sup(sig(V),2),op('='),'<munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>m</mi></munderover>',sq(row(der(xi),sig(xi)))),5)
para('Nessa expressão, m é o número de dimensões do modelo e a incerteza de cada dimensão corresponde ao seu erro total. Uma dimensão compartilhada por duas partes da peça deve aparecer uma única vez na soma, com a derivada da expressão completa. O resultado final é apresentado com um algarismo significativo na incerteza e o volume arredondado para a mesma casa decimal.')
heading('3 METODOLOGIA')
para('O conjunto analisado reúne três leituras de cada dimensão das quatro peças indicadas no roteiro de laboratório. O instrumento indicado é o paquímetro. Foram utilizados os diâmetros externos, os diâmetros dos furos e as alturas identificadas nas figuras. Na última peça, foi utilizada também a largura L da face plana do corte, vista de cima (Sousa, 2026).')
para('As medidas foram expressas em centímetros. Adotou-se a contribuição instrumental de 0,01 milímetro, equivalente a 0,001 centímetro, para a bateria, e de 0,05 milímetro, equivalente a 0,005 centímetro, para a arruela. Nas duas peças com ressalto, foi adotado o valor de 0,005 centímetro sob a hipótese de utilização do mesmo instrumento da arruela, pois esses itens não especificam outro valor.')
para('O tratamento seguiu cinco etapas: média, desvio padrão amostral, erro estatístico da média, erro total e erro propagado do volume. Todas as leituras confirmadas foram mantidas, incluindo a segunda medida de L igual a 1,31 centímetro. Os cálculos conservaram a precisão interna até o arredondamento final.')
para('As peças compostas foram modeladas como duas arruelas de mesmo diâmetro interno. Essa representação pressupõe que o furo tenha diâmetro uniforme ao longo da altura total considerada. Trata-se de uma hipótese do cálculo, ainda sujeita à confirmação na peça real; se o furo terminar no interior da peça, será necessário conhecer sua profundidade e revisar os volumes e suas incertezas.')
newpage()
rows=[]
for name,data,_ in pieces:
 for j,(k,vals) in enumerate(data.items()):rows.append([name if j==0 else '',sym(k)]+[f(v,2) for v in vals])
t=table('Tabela 1 – Medidas dimensionais das quatro peças (cm)',['Peça','Grandeza','Leitura 1','Leitura 2','Leitura 3'],rows,[5.0,2.0,3,3,3])
source('Fonte: Sousa (2026), com transcrição conferida e segunda leitura de L confirmada como 1,31 cm.')
source('Nota: D é o diâmetro da bateria; D₁ é o diâmetro do furo; D₂ é o diâmetro da arruela ou do ressalto; D₃ é o diâmetro da base; h, h₁ e h₂ são alturas; L é a largura do corte vista de cima.')
heading('4 RESULTADOS E DISCUSSÃO')
heading('4.1 Médias e incertezas das dimensões',2)
para('A Tabela 2 apresenta os resultados das quatro primeiras etapas. As casas decimais adicionais permitem acompanhar os cálculos intermediários. Na arruela, as alturas de 0,10, 0,14 e 0,01 centímetro resultam em média de 0,083333 centímetro, corrigindo o valor de 0,12 centímetro anotado no roteiro.')
rows=[]
for ix,(name,data,_) in enumerate(pieces):
 for j,k in enumerate(data):rows.append([['Bateria','Arruela','Ressalto e furo','Ressalto, furo e corte'][ix] if j==0 else '',sym(k)]+[f(z[k]) for z in stats[ix]])
table('Tabela 2 – Tratamento estatístico das dimensões (cm)',['Peça','Grandeza','Média','DP','σ est','σ total'],rows,[3.6,2.2,2.55,2.55,2.55,2.55])
source('Fonte: elaboração a partir dos dados da Tabela 1.')
source('Nota: DP é o desvio padrão amostral; σ est é a incerteza estatística da média; σ total é o erro total. Foram utilizadas três leituras por dimensão.')
newpage();heading('4.2 Modelos geométricos e volumes',2)
para('A bateria foi representada por um cilindro. Na arruela, o volume do furo é subtraído do volume do cilindro externo. Assim, com D e h para a bateria e D₁, D₂ e h para a arruela, obtêm-se as expressões:')
formula(row(sub(V,i('bateria')),op('='),frac(row(pi,sup(D,2),h),n(4))),6)
formula(row(sub(V,i('arruela')),op('='),ann(d2,h)),7)
para('Para a peça com ressalto, a arruela superior usa D₂ e h₂ e a base usa D₃ e h₁. As duas partes compartilham o diâmetro interno D₁. Sob a hipótese descrita na metodologia, o volume total corresponde à soma:')
formula(row(sub(V,n(1)),op('='),ann(d2,h2)),8)
formula(row(sub(V,n(2)),op('='),ann(d3,h1)),9)
formula(row(sub(V,i('ressalto')),op('='),sub(V,n(1)),op('+'),sub(V,n(2))),10)
para('Na peça com corte plano, subtrai-se o volume de um segmento circular da base. L representa a linha reta que une as extremidades do corte na circunferência, chamada corda. O ângulo θ é determinado pela função inversa do seno, indicada por arcsen, e deve ser calculado em radianos.')
formula(row(R,op('='),frac(d3,n(2)),op(';'),theta,op('='),n(2),i('arcsen'),par(frac(L,d3))),11)
formula(row(A,op('='),frac(sup(R,2),n(2)),par(row(theta,op('−'),i('sen'),theta))),12)
formula(row(sub(V,i('com corte')),op('='),sub(V,n(1)),op('+'),sub(V,n(2)),op('−'),h1,A),13)
para('Com as dimensões médias, o raio da base é 1,085 centímetro, o ângulo é aproximadamente 1,28853876 radiano e a área removida é 0,19312945 centímetro quadrado. O volume retirado é aproximadamente 0,15514732 centímetro cúbico. A distância do centro à linha do corte, aproximadamente 0,8675 centímetro, supera o raio do ressalto, de 0,5967 centímetro. Portanto, nessa geometria, o corte remove material somente da base.')
heading('4.3 Propagação e resultados finais',2)
para('A propagação foi aplicada à expressão completa de cada volume. Para a bateria, as contribuições do diâmetro e da altura são combinadas pela expressão:')
formula(row(sig(V),op('='),sqrt(row(sq(row(frac(row(pi,D,h),n(2)),sig(D))),op('+'),sq(row(frac(row(pi,sup(D,2)),n(4)),sig(h)))))),14)
para('Nas peças compostas, o furo comum exige combinar as duas alturas na derivada em relação a D₁:')
formula(row(der(d1),op('='),op('−'),frac(row(pi,d1,par(row(h1,op('+'),h2))),n(2))),15)
para('No corte plano, a área A depende de D₃ e L. Por isso, suas derivadas são incorporadas à expressão do volume, em vez de atribuir ao ângulo e à área incertezas independentes adicionais:')
da3=frac(row(op('∂'),A),row(op('∂'),d3));daL=frac(row(op('∂'),A),row(op('∂'),L));q=sqrt(diff(d3,L))
formula(row(da3,op('='),frac(d3,n(4)),par(row(theta,op('−'),frac(row(n(2),L),q)))),16)
formula(row(daL,op('='),frac(sup(L,2),row(n(2),q))),17)
para('As Tabelas 3 e 4 apresentam, respectivamente, os valores intermediários dos volumes e sua apresentação final. As incertezas relativas foram calculadas antes do arredondamento pela razão entre a incerteza propagada e o volume, multiplicada por cem.')
table('Tabela 3 – Volumes e incertezas propagadas',['Peça','V (cm³)','σ V (cm³)','σ V / V (%)'],[[name,f(v,8),f(uv,8),f(100*uv/v,2)] for (name,_,_),(v,uv) in zip(pieces,vols)],[5.5,3.5,3.5,3.5]);source('Fonte: elaboração a partir das dimensões médias e dos erros totais.')
table('Tabela 4 – Resultados finais dos volumes',['Peça','Volume com incerteza (cm³)'],[['Bateria','(1,00 ± 0,03)'],['Arruela','(0,19 ± 0,09)'],['Ressalto e furo','(11,7 ± 0,6)'],['Ressalto, furo e corte','(3,0 ± 0,7)']],[8,8]);source('Fonte: resultados da Tabela 3, com arredondamento final.')
heading('4.4 Interpretação e limitações',2)
para('A bateria apresentou a menor incerteza relativa, de 2,56%, seguida da peça com ressalto e furo, com 4,78%. A arruela e a peça com corte apresentaram 46,55% e 23,40%, respectivamente. Esses valores descrevem a precisão obtida pelo procedimento adotado, mas não representam o desvio em relação ao volume verdadeiro, pois não foi utilizado um valor de referência independente.')
para('Na arruela, a dispersão das alturas responde por aproximadamente 99,9% da variância propagada do volume. Na peça com corte, as contribuições das alturas h₁ e h₂ correspondem a aproximadamente 88,4% e 8,7% dessa variância. Portanto, a repetição e a conferência das medidas de altura teriam maior potencial de reduzir a incerteza dessas peças. Todas as medidas confirmadas foram utilizadas nos cálculos.')
para('Diferenças no posicionamento do instrumento, na identificação das superfícies de referência, na pressão de contato ou na leitura são possíveis causas de dispersão. Os dados disponíveis, entretanto, não permitem atribuir a variação a uma causa específica. A análise utiliza somente três leituras por dimensão e não estabelece um intervalo de confiança de noventa e cinco por cento.')
para('A propagação empregada é uma aproximação de primeira ordem. Os modelos consideram superfícies planas, seções circulares e dimensões uniformes, sem quantificar desvios de forma. Além dessas limitações, os resultados das peças compostas dependem da confirmação da extensão do furo e da contribuição instrumental adotada.')
heading('5 CONCLUSÃO')
para('O tratamento das medidas permitiu calcular os volumes da bateria, da arruela, da peça com ressalto e furo e da peça com corte plano como (1,00 ± 0,03), (0,19 ± 0,09), (11,7 ± 0,6) e (3,0 ± 0,7) centímetros cúbicos, respectivamente, sob as hipóteses geométricas e instrumentais declaradas. A composição por duas arruelas e a subtração do segmento circular permitiram expressar os volumes em função das dimensões medidas.')
para('A dispersão das alturas foi a principal limitação da arruela e da peça com corte. Recomenda-se ampliar as repetições e padronizar as superfícies e o posicionamento do paquímetro. Antes de interpretar como definitivos os resultados das peças compostas, é necessário confirmar se o furo atravessa a altura considerada no modelo. Sem volumes de referência, os resultados permitem discutir a precisão, mas não determinar sua exatidão.')
para('REFERÊNCIAS','Seção não numerada',indent=False)
refs=['IWAMOTO, Wellington Akira; GUARANY, Cristiano Alves; FOSCHINI, Mauricio; DI LORENZO, Antonino. Guias e roteiros para Laboratório de Física Experimental I. 1. ed. Uberlândia: Instituto de Física, Universidade Federal de Uberlândia, 2014.','SOUSA, Lucas Soares. L1-Laboratório-FG1: Engenharia – Diurno. Roteiro de atividades. 15 set. 2026. 5 p.']
for ref in refs:
 p=para(ref,indent=False);p.alignment=AL.LEFT;p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(12)
# Table page references point to stable caption bookmarks.
for ix,p in enumerate([p for p in doc.paragraphs if re.match(r'Tabela [1-4] –',p.text) and '\t' not in p.text],1):
 start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),str(100+ix));start.set(qn('w:name'),'tab'+str(ix));end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),str(100+ix));p._p.insert(0,start);p._p.append(end)
# Set all language markers to Portuguese and remove accidental inherited highlights.
for run in doc.element.xpath('//w:r'):
 for el in list(run.xpath('./w:rPr/w:highlight')):el.getparent().remove(el)
doc.core_properties.title='Relatório T0 – Medidas dimensionais e determinação de volumes';doc.core_properties.author='[.......]';doc.core_properties.subject='Relatório conforme template fornecido'
out=root/'RelatórioT0_Template.docx';doc.save(out)
# Retain opaque template package parts exactly as supplied where not edited by object model.
keep=['word/footnotes.xml','word/endnotes.xml','word/numbering.xml','word/theme/theme1.xml','word/fontTable.xml','word/webSettings.xml']
with ZipFile(root/'refs/template_tcc.docx') as original,ZipFile(out) as current:
 data={n:current.read(n) for n in current.namelist()}
 for name in original.namelist():
  if name in keep or name.startswith('customXml/') or name.startswith('word/media/'):data[name]=original.read(name)
with ZipFile(out,'w',ZIP_DEFLATED) as z:
 for name,value in data.items():z.writestr(name,value)
print(out);print('Resumo:',len(resumo.split()),'palavras; abstract:',len(abstract.split()));print('Equações:',len(doc.element.xpath('//m:oMath')))


