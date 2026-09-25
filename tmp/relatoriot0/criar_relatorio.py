from pathlib import Path
import math,statistics,re
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY,TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

root=Path(__file__).resolve().parents[2]
pdfmetrics.registerFont(TTFont('TNR','C:/Windows/Fonts/times.ttf'))
pdfmetrics.registerFont(TTFont('TNRB','C:/Windows/Fonts/timesbd.ttf'))
pdfmetrics.registerFont(TTFont('TNRI','C:/Windows/Fonts/timesi.ttf'))
pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNRB',italic='TNRI',boldItalic='TNRB')
ink=colors.HexColor('#172d40');gray=colors.HexColor('#52606B')
styles={
'body':ParagraphStyle('body',fontName='TNR',fontSize=11.5,leading=16,alignment=TA_JUSTIFY,spaceAfter=9),
'title':ParagraphStyle('title',fontName='TNRB',fontSize=22,leading=28,alignment=TA_CENTER,spaceAfter=18,textColor=ink),
'h1':ParagraphStyle('h1',fontName='TNRB',fontSize=15,leading=20,spaceAfter=13,textColor=ink),
'h2':ParagraphStyle('h2',fontName='TNRB',fontSize=12,leading=16,spaceBefore=8,spaceAfter=7,textColor=ink),
'eq':ParagraphStyle('eq',fontName='TNR',fontSize=11.5,leading=19,alignment=TA_CENTER,spaceAfter=10),
'small':ParagraphStyle('small',fontName='TNR',fontSize=9.5,leading=12,spaceAfter=6),
'cell':ParagraphStyle('cell',fontName='TNR',fontSize=9.4,leading=11.5),
'center':ParagraphStyle('center',fontName='TNR',fontSize=12,leading=18,alignment=TA_CENTER,spaceAfter=12),
'ref':ParagraphStyle('ref',fontName='TNR',fontSize=10.5,leading=14,spaceAfter=12,alignment=TA_JUSTIFY),
}
story=[]
def norm(s):
 for a,b in zip('₀₁₂₃₄₅₆₇₈₉','0123456789'):s=s.replace(a,'<sub>'+b+'</sub>')
 return s
def p(s,sty='body'):story.append(Paragraph(norm(s),styles[sty]))
def h(s):p(s,'h2')
def page(s):story.append(PageBreak());p(s,'h1')
def eq(s,n=None):p(s+(' &nbsp;&nbsp; ('+str(n)+')' if n else ''),'eq')
def f(x,n=6):return f'{x:.{n}f}'.replace('.',',')
def table(caption,headers,rows,widths):
 p(caption,'small')
 cells=[[Paragraph(norm(str(v)),styles['cell']) for v in row] for row in [headers]+rows]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='CENTER')
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEF2F5')),('LINEABOVE',(0,0),(-1,0),.7,ink),('LINEBELOW',(0,0),(-1,0),.6,ink),('LINEBELOW',(0,-1),(-1,-1),.7,ink),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 story.append(t);story.append(Spacer(1,7))

pieces=[('Bateria',{'D':[2.08,2.03,2.00],'h':[.31,.31,.30]},.001),('Arruela',{'D1':[.75,.71,.72],'D2':[1.85,1.89,1.87],'h':[.10,.14,.01]},.005),('Ressalto e furo',{'D1':[.76,.60,.72],'D2':[1.88,1.70,1.81],'D3':[2.51,2.4,2.53],'h1':[2.49,2.30,2.57],'h2':[.45,.30,.35]},.005),('Ressalto, furo e corte',{'D1':[.5,.61,.61],'D2':[1.1,1.26,1.22],'D3':[2.1,2.21,2.2],'h1':[.4,1.07,.94],'h2':[.9,.06,.5],'L':[1.2,1.31,1.4]},.005)]
stats=[];vols=[];termsall=[]
for idx,(name,data,inst) in enumerate(pieces):
 m={k:statistics.mean(a) for k,a in data.items()};s={k:statistics.stdev(a) for k,a in data.items()};e={k:s[k]/math.sqrt(3) for k in data};u={k:math.hypot(e[k],inst) for k in data};stats.append((m,s,e,u))
 if idx==0:
  D,H=m['D'],m['h'];v=math.pi*D*D*H/4;c={'D':math.pi*D*H/2,'h':math.pi*D*D/4}
 elif idx==1:
  d1,d2,H=m['D1'],m['D2'],m['h'];v=math.pi*H*(d2*d2-d1*d1)/4;c={'D1':-math.pi*H*d1/2,'D2':math.pi*H*d2/2,'h':math.pi*(d2*d2-d1*d1)/4}
 else:
  d1,d2,d3,h1,h2=[m[k] for k in ['D1','D2','D3','h1','h2']];v=math.pi/4*(h1*(d3*d3-d1*d1)+h2*(d2*d2-d1*d1));c={'D1':-math.pi*d1*(h1+h2)/2,'D2':math.pi*h2*d2/2,'D3':math.pi*h1*d3/2,'h1':math.pi*(d3*d3-d1*d1)/4,'h2':math.pi*(d2*d2-d1*d1)/4}
  if idx==3:
   L=m['L'];theta=2*math.asin(L/d3);A=d3*d3/8*(theta-math.sin(theta));v-=h1*A;c['D3']=h1*d3/4*(2*math.pi-theta+2*L/math.sqrt(d3*d3-L*L));c['h1']-=A;c['L']=-h1*L*L/(2*math.sqrt(d3*d3-L*L))
 terms={k:c[k]*u[k] for k in data};uv=math.sqrt(sum(t*t for t in terms.values()));vols.append((v,uv));termsall.append(terms)

p('UNIVERSIDADE FEDERAL DE UBERLÂNDIA','center')
p('INSTITUTO DE FÍSICA<br/>FÍSICA GERAL EXPERIMENTAL I','center')
story.append(Spacer(1,65))
p('RELATÓRIO T0','title')
p('Medidas dimensionais e determinação de volumes<br/>com propagação de incertezas','title')
story.append(Spacer(1,48))
p('Integrantes: [.......]<br/>Matrículas: [.......]<br/>Curso: [.......]<br/>Turma: [.......]<br/>Docente: [.......]<br/>Data de realização: [.......]','center')
story.append(Spacer(1,65))
p('Uberlândia<br/>2026','center')

page('Resumo')
resumo='Foram analisadas dimensões de quatro peças, registradas com paquímetro em três repetições por grandeza. Calcularam-se médias, desvios padrão, incertezas estatísticas e totais, seguidas da propagação para os volumes. Modelaram-se a bateria como cilindro e as demais peças por soma e subtração de volumes, incluindo um segmento circular no corte plano. Obtiveram-se (1,00 ± 0,03), (0,19 ± 0,09), (11,7 ± 0,6) e (3,0 ± 0,7) cm³, respectivamente. As incertezas relativas variaram de 2,56% a 46,55%. A dispersão das alturas limitou principalmente a determinação dos volumes da arruela e da peça com corte.'
p(resumo)
p('<b>Palavras-chave:</b> paquímetro; medidas dimensionais; volume; propagação de incertezas.','small')
h('1 Introdução e objetivos')
p('A determinação experimental de uma grandeza requer a apresentação de uma estimativa acompanhada de sua incerteza. Em medidas dimensionais, a dispersão entre leituras e a contribuição do instrumento afetam tanto o comprimento medido diretamente quanto grandezas calculadas a partir dele. O volume, por exemplo, depende simultaneamente dos diâmetros e das alturas empregados no modelo geométrico [1, 2].')
p('Este trabalho teve como objetivo determinar os volumes de uma bateria cilíndrica, uma arruela, um cilindro com ressalto e furo e uma peça semelhante com corte plano. Foram tratados três registros por dimensão, combinadas as contribuições estatística e instrumental e propagadas as incertezas para os volumes. A comparação entre os resultados permite identificar quais dimensões mais limitaram a precisão.')
h('1.1 Fundamentação do tratamento das medidas')
p('Para N = 3 leituras de uma grandeza x, a média x̄, o desvio padrão amostral s e a incerteza estatística da média σ<sub>est</sub> foram calculados conforme o roteiro e a apostila [1, 2]:')
eq('x̄ = (x₁ + x₂ + x₃)/3; &nbsp; s = √{Σ(xᵢ − x̄)²/(N − 1)}',1)
eq('σ<sub>est</sub> = s/√N; &nbsp; σ<sub>total</sub> = √(σ<sub>est</sub>² + σ<sub>inst</sub>²)',2)
p('Para um volume V dependente de dimensões xᵢ consideradas sem correlação, aplicou-se a propagação de primeira ordem:')
eq('σ<sub>V</sub>² = Σ[(∂V/∂xᵢ)² σ<sub>xᵢ</sub>²]',3)
p('As derivadas foram avaliadas nas médias, e σ<sub>xᵢ</sub> representa a incerteza total de cada dimensão. Uma variável compartilhada por duas partes do sólido foi tratada uma única vez na expressão completa do volume. Os valores finais foram arredondados para um algarismo significativo na incerteza, com a estimativa na mesma casa decimal.','small')

page('2 Procedimento experimental')
p('Foram considerados os registros das quatro peças apresentados nas tabelas do roteiro [1], com três leituras para cada dimensão. O instrumento indicado é o paquímetro. Não constam nos registros disponíveis sua marca, modelo, certificado de calibração, identificação dos operadores ou fotografias da montagem; esses dados não foram presumidos.')
p('O procedimento prescrito consistia em medir os diâmetros externos, os diâmetros dos furos e as alturas indicadas nas figuras. Na última peça, mediu-se também L, a largura da corda que delimita o corte plano. O roteiro solicita medidas por alunos diferentes, mas a associação entre cada leitura e seu operador não foi registrada. Após a transcrição, calcularam-se as médias e as incertezas, e aplicaram-se os modelos geométricos às dimensões médias.')
p('Adotou-se σ<sub>inst</sub> = 0,01 mm = 0,001 cm para a bateria e 0,05 mm = 0,005 cm para a arruela, conforme o enunciado. Para as duas peças com ressalto, utilizou-se 0,005 cm sob a hipótese de emprego do mesmo instrumento da arruela, pois esses itens não especificam outro valor. As dimensões foram mantidas em centímetros.')
rows=[]
for name,data,_ in pieces:
 for j,(k,a) in enumerate(data.items()):rows.append([name if j==0 else '',re.sub(r'(\d)',r'<sub>\1</sub>',k)]+[f(x,2) for x in a])
table('Tabela 1 - Registros dimensionais utilizados; todas as medidas em cm.',['Peça','Grandeza','Leitura 1','Leitura 2','Leitura 3'],rows,[159,60,78,78,78])
p('D₁ designa o furo; D₂, o diâmetro externo da arruela ou do ressalto; D₃, o diâmetro externo da base; h₁ e h₂, as alturas da base e do ressalto. Na bateria, D e h são diâmetro e altura. Fonte: roteiro [1], com leitura conferida e segunda medida de L confirmada como 1,31 cm.','small')

page('3 Resultados e discussão')
h('3.1 Tratamento estatístico das dimensões')
p('A Tabela 2 reúne as estimativas intermediárias. As casas adicionais permitem acompanhar o cálculo; a apresentação final dos volumes é feita com arredondamento apropriado. Foram preservadas todas as leituras confirmadas, sem exclusão de valores discrepantes.')
rows=[]
for idx,(name,data,_) in enumerate(pieces):
 m,s,e,u=stats[idx]
 for j,k in enumerate(data):rows.append([['Bateria','Arruela','Ressalto','Com corte'][idx] if j==0 else '',re.sub(r'(\d)',r'<sub>\1</sub>',k),f(m[k]),f(s[k]),f(e[k]),f(u[k])])
table('Tabela 2 - Média, desvio padrão e incertezas; todos os valores em cm.',['Peça','Grandeza','Média','DP','σ<sub>est</sub>','σ<sub>total</sub>'],rows,[72,57,81,81,81,81])
p('Fonte: cálculo a partir dos dados da Tabela 1. Na arruela, a média da altura é 0,083333… cm; o valor 0,12 cm anotado no roteiro não corresponde às três leituras e foi corrigido.','small')
h('Exemplo de aplicação: diâmetro da bateria')
eq('D̄ = (2,08 + 2,03 + 2,00)/3 = 2,036666… cm')
eq('s<sub>D</sub> = √{[(2,08 − D̄)² + (2,03 − D̄)² + (2,00 − D̄)²]/2}<br/>s<sub>D</sub> ≈ 0,04041452 cm; &nbsp; σ<sub>est,D</sub> = s<sub>D</sub>/√3 ≈ 0,02333333 cm')
eq('σ<sub>D</sub> = √[(0,02333333…)² + (0,001)²] ≈ 0,02335475 cm')
p('O mesmo procedimento foi aplicado às demais dimensões. Como σ<sub>total</sub> combina duas contribuições positivas em quadratura, ele não pode ser menor que a incerteza instrumental.','small')

page('3.2 Modelos geométricos e volumes')
p('Na bateria, utilizou-se o modelo cilíndrico. Na arruela, subtraiu-se o volume do furo do cilindro externo. A soma impressa na expressão da arruela no roteiro foi corrigida para a diferença, de modo coerente com a geometria [1].')
eq('V<sub>bateria</sub> = πD²h/4; &nbsp; V<sub>arruela</sub> = πh(D₂² − D₁²)/4',4)
eq('V<sub>bateria</sub> ≈ π(2,03666667)²(0,30666667)/4 ≈ 0,99907103 cm³')
eq('V<sub>arruela</sub> ≈ π(0,08333333)[(1,87)² − (0,72666667)²]/4<br/>V<sub>arruela</sub> ≈ 0,19431114 cm³')
p('A peça com ressalto e furo foi decomposta em duas arruelas com o mesmo diâmetro interno D₁. A superior tem diâmetro D₂ e altura h₂, e a inferior, diâmetro D₃ e altura h₁. O furo foi considerado passante, conforme o desenho.')
eq('V₁ = πh₂(D₂² − D₁²)/4; &nbsp; V₂ = πh₁(D₃² − D₁²)/4',5)
eq('V<sub>ressalto</sub> = V₁ + V₂ ≈ 0,79116560 + 10,92460315<br/>V<sub>ressalto</sub> ≈ 11,71576875 cm³')
p('Para a peça com corte, retirou-se da soma dessas duas arruelas o volume do segmento circular de área A e altura h₁. L é a corda do segmento menor mostrado no roteiro. Usando θ em radianos [1]:')
eq('R = D₃/2; &nbsp; θ = 2 arcsen(L/D₃); &nbsp; A = (R²/2)(θ − sen θ)',6)
eq('V<sub>com corte</sub> = V₁ + V₂ − h₁A',7)
eq('R = 2,17/2 = 1,085 cm; &nbsp; θ ≈ 1,28853876 rad<br/>A ≈ 0,19312945 cm²; &nbsp; h₁A ≈ 0,15514732 cm³')
eq('V<sub>com corte</sub> ≈ 0,41866609 + 2,76362115 − 0,15514732<br/>V<sub>com corte</sub> ≈ 3,02713992 cm³')
p('Nas dimensões médias, a distância do centro à corda é √[R² − (L/2)²] ≈ 0,8675 cm, maior que o raio do ressalto (0,5967 cm) e o do furo (0,2867 cm). Assim, o corte modelado atinge somente a base, sem remover material do ressalto ou interceptar o furo.','small')

page('3.3 Propagação das incertezas')
p('A equação (3) foi aplicada à expressão completa de cada volume, mantendo a dependência de todas as dimensões medidas. Para a bateria, por exemplo:')
eq('∂V/∂D = πDh/2; &nbsp; ∂V/∂h = πD²/4')
eq('σ<sub>V</sub> = √[(πDhσ<sub>D</sub>/2)² + (πD²σ<sub>h</sub>/4)²]<br/>σ<sub>V</sub> ≈ √[(0,02291298)² + (0,01133762)²] ≈ 0,02556455 cm³')
p('Na arruela, as derivadas em relação a D₁, D₂ e h são, respectivamente, −πhD₁/2, πhD₂/2 e π(D₂² − D₁²)/4. Nas peças compostas, o mesmo D₁ integra ambas as arruelas; portanto, ∂V/∂D₁ = −πD₁(h₁ + h₂)/2. Somar incertezas de volumes como se eles fossem independentes desconsideraria essa dependência compartilhada.')
p('No corte plano, θ depende de L e D₃. As derivadas da área do segmento, necessárias para considerar essa dependência, são:')
eq('∂A/∂D₃ = (D₃/4)[θ − 2L/√(D₃² − L²)]<br/>∂A/∂L = L²/[2√(D₃² − L²)]',8)
p('Assim, ∂V/∂D₃ = h₁[πD₃/2 − ∂A/∂D₃], ∂V/∂h₁ = π(D₃² − D₁²)/4 − A e ∂V/∂L = −h₁∂A/∂L. O ângulo e a área não foram acrescentados como grandezas independentes, pois resultam das seis dimensões já medidas.')
table('Tabela 3 - Volumes e incertezas propagadas antes do arredondamento final.',['Peça','V (cm³)','σ<sub>V</sub> (cm³)','σ<sub>V</sub>/V (%)'],[[name,f(v,8),f(uv,8),f(100*uv/v,2)] for (name,_,_),(v,uv) in zip(pieces,vols)],[155,110,110,78])
table('Tabela 4 - Resultados finais em notação científica.',['Peça','Volume com incerteza (cm³)'],[['Bateria','(1,00 ± 0,03) × 10<super>0</super>'],['Arruela','(1,9 ± 0,9) × 10<super>−1</super>'],['Ressalto e furo','(1,17 ± 0,06) × 10<super>1</super>'],['Ressalto, furo e corte','(3,0 ± 0,7) × 10<super>0</super>']],[185,268])
p('Fonte: cálculo a partir das Tabelas 1 e 2. Os resultados são consistentes com a memória de cálculo do projeto; diferenças nas últimas casas intermediárias decorrem do uso, aqui, da precisão integral antes do arredondamento.','small')

page('3.4 Discussão dos resultados e limitações')
p('A bateria apresentou a menor incerteza relativa, de 2,56%, seguida da peça com ressalto e furo, com 4,78%. A arruela e a peça com corte apresentaram 46,55% e 23,40%, respectivamente. Esses percentuais caracterizam a precisão obtida pelo tratamento adotado; não quantificam um desvio em relação ao volume verdadeiro, pois não foi fornecido um valor de referência independente.')
p('Na arruela, as alturas de 0,10, 0,14 e 0,01 cm resultaram em média de 0,083333… cm e incerteza total de aproximadamente 0,038766 cm. A contribuição dessa altura representa cerca de 99,9% da variância propagada do volume. Portanto, a elevada incerteza não se deve principalmente à resolução atribuída ao paquímetro, mas à dispersão das leituras. Os valores foram preservados, pois não existe justificativa documentada para descartar uma observação.')
p('Na peça com corte, as alturas da base (0,40; 1,07; 0,94 cm) e do ressalto (0,90; 0,06; 0,50 cm) também apresentaram dispersão expressiva. As contribuições de h₁ e h₂ correspondem a aproximadamente 88,4% e 8,7% da variância do volume. Já a largura L responde por cerca de 0,1%. Assim, repetir prioritariamente as medidas das alturas teria maior potencial de reduzir a incerteza do que apenas refinar a largura do corte.')
p('Diferenças no posicionamento do instrumento, na identificação das superfícies de referência, na pressão de contato, na leitura ou na transcrição constituem possíveis explicações para a dispersão. Entretanto, os registros não permitem determinar qual dessas causas ocorreu. A ausência de informações sobre calibração e correção de zero também impede avaliar quantitativamente eventuais efeitos sistemáticos.')
p('O conjunto contém apenas três leituras por grandeza. Com amostragem tão reduzida, não é possível caracterizar de forma robusta a distribuição dos erros ou atribuir ao intervalo apresentado uma probabilidade de cobertura de 95%. As incertezas foram estimadas pelo procedimento didático do roteiro, sem fator adicional de abrangência. A propagação empregada é uma aproximação de primeira ordem; sua interpretação exige cautela nos casos de grande dispersão [2].')
p('Os modelos consideram superfícies planas, seções circulares, furo passante e dimensões uniformes. Desvios de forma, rebarbas, conicidade e não paralelismo não foram quantificados. Por isso, a incerteza calculada expressa as contribuições dimensionais consideradas e não constitui uma avaliação completa de todas as fontes possíveis de erro. Não se ajustou regressão, pois os registros são repetições de dimensões, e não uma série funcional entre variáveis.')

page('4 Conclusões')
p('O tratamento das dimensões permitiu determinar os volumes da bateria, da arruela, da peça com ressalto e furo e da peça com corte plano como (1,00 ± 0,03), (0,19 ± 0,09), (11,7 ± 0,6) e (3,0 ± 0,7) cm³, respectivamente. A composição de volumes por duas arruelas e a subtração do segmento circular mostraram-se coerentes com a geometria indicada no roteiro. As dimensões compartilhadas foram consideradas na propagação da incerteza da expressão completa de cada sólido.')
p('A qualidade dos resultados foi limitada principalmente pela dispersão das alturas na arruela e na peça com corte. Recomenda-se ampliar o número de repetições, padronizar as superfícies de referência e o posicionamento do paquímetro, conferir o zero e registrar a identificação e as características do instrumento. Sem volumes de referência, não se pode concluir sobre a exatidão das estimativas; os dados permitem avaliar sua precisão no âmbito das hipóteses adotadas.')
h('Referências')
p('[1] SOUSA, Lucas Soares. <b>L1-Laboratório-FG1: Engenharia - Diurno</b>. Roteiro de atividades. 15 set. 2026. 5 p. Arquivo do projeto: <i>Trabalho_FG1.pdf</i>.','ref')
p('[2] IWAMOTO, Wellington Akira; GUARANY, Cristiano Alves; FOSCHINI, Mauricio; DI LORENZO, Antonino. <b>Guias e roteiros para Laboratório de Física Experimental I</b>. 1. ed. Uberlândia: Instituto de Física, 2014. Seções 2.2 e 3.3; capítulo 7. Arquivo do projeto: <i>Lab1.pdf</i>.','ref')
p('[3] ODASHIMA, Mariana M. <b>Física Geral Experimental: Lab Física 1 - Mecânica. Aula 4: Como fazer relatório</b>. Instituto de Física, Universidade Federal de Uberlândia, [s.d.]. 25 slides. Arquivo do projeto: <i>Relatorio.pdf</i>.','ref')
p('Nota de apresentação: a organização deste relatório segue a orientação de estrutura, concisão, discussão dos resultados e referências do material [3]. Os cálculos completos por peça encontram-se na memória de cálculo já existente na pasta do projeto.','small')

def footer(c,doc):
 if doc.page==1:return
 c.setStrokeColor(colors.HexColor('#CBD2D8'));c.line(57,43,A4[0]-57,43)
 c.setFont('TNR',9);c.setFillColor(gray);c.drawString(57,30,'Relatório T0 | Medidas e incertezas');c.drawRightString(A4[0]-57,30,str(doc.page-1))
out=root/'RelatórioT0.pdf'
doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=62,rightMargin=62,topMargin=52,bottomMargin=58,title='Relatório T0 - Medidas dimensionais e determinação de volumes',author='[.......]')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
print('Summary words',len(resumo.split()))
print('Volumes',vols)
for i in [1,3]:print('variance fractions',i,{k:round(t*t/vols[i][1]**2*100,4) for k,t in termsall[i].items()})
