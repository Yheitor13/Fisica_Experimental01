from pathlib import Path
from html import escape
p=Path('tmp/relatoriot0')
def row(*a):return '<mrow>'+''.join(a)+'</mrow>'
def i(s):return '<mi>'+s+'</mi>'
def n(s):return '<mn>'+str(s)+'</mn>'
def op(s):return '<mo>'+s+'</mo>'
def sub(x,y):return '<msub>'+x+'<mrow>'+y+'</mrow></msub>'
def sup(x,y):return '<msup>'+x+n(y)+'</msup>'
def frac(a,b):return '<mfrac>'+a+b+'</mfrac>'
def sqrt(a):return '<msqrt>'+a+'</msqrt>'
def par(a):return row(op('('),a,op(')'))
def sq(a):return sup(par(a),2)
def eq(a):return '<div class="eq"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block">'+a+'</math></div>'
def txt(t):return '<p>'+t+'</p>'
def title(t):return '<h2>'+t+'</h2>'
def sig(x):return sub(i('σ'),x)
def der(x):return frac(row(op('∂'),i('V')),row(op('∂'),x))
def rootterms(ts):
 rows=[]
 for j in range(0,len(ts),2):rows.append('<mtr><mtd>'+row(*( ([op('+')] if j else [])+[sq(t)+(op('+') if k==0 and j+1<len(ts) else '') for k,t in enumerate(ts[j:j+2])]))+'</mtd></mtr>')
 return sqrt('<mtable columnalign="left" rowspacing="0.6em">'+''.join(rows)+'</mtable>')
pi=i('π'); D=i('D');h=i('h');V=i('V');d1=sub(D,n(1));d2=sub(D,n(2));d3=sub(D,n(3));h1=sub(h,n(1));h2=sub(h,n(2));L=i('L');A=i('A');theta=i('θ');R=i('R');sv=sig(V)
def diff(a,b):return row(sup(a,2),op('−'),sup(b,2))
def ann(d,H):return row(frac(row(pi,H),n(4)),par(diff(d,d1)))
def derivs(xs,cs):return ''.join(eq(row(der(x),op('='),c)) for x,c in zip(xs,cs))
sections=[]
x=i('x');N=i('N');xb='<mover>'+x+op('¯')+'</mover>';xi=sub(x,i('i'));ss=i('s');se=sig(i('est'));st=sig(i('total'));si=sig(i('inst'))
sumx='<munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>N</mi></munderover>'
s=title('1. Fórmulas gerais - os cinco passos')+txt('Aplicáveis a cada dimensão medida. Neste trabalho, N = 3. Comprimentos em cm e volumes em cm³.')
s+=txt('<b>1 · Média aritmética</b>')+eq(row(xb,op('='),frac(row(sumx,xi),N),op('='),frac(row(sub(x,n(1)),op('+'),sub(x,n(2)),op('+'),sub(x,n(3))),n(3))))
s+=txt('<b>2 · Desvio padrão amostral (DP)</b>')+eq(row(ss,op('='),sqrt(frac(row(sumx,sq(row(xi,op('−'),xb))),row(N,op('−'),n(1))))))
s+=txt('<b>3 · Erro estatístico da média</b>')+eq(row(se,op('='),frac(ss,sqrt(N)),op('='),frac(ss,sqrt(n(3)))))
s+=txt('<b>4 · Erro total da dimensão</b>')+eq(row(st,op('='),sqrt(row(sup(se,2),op('+'),sup(si,2)))))
s+=txt('<b>5 · Erro propagado do volume</b>')+eq(row(sv,op('='),sqrt(row('<munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>m</mi></munderover>',sq(row(der(xi),sig(xi)))))))
s+=txt('σ indica a incerteza. Na etapa 5, σ de cada dimensão é seu erro total. A fórmula considera dimensões independentes e propagação de primeira ordem; m é o número de dimensões do modelo.')
s+=eq(row(i('V'),op('±'),sv))+eq(row(sub(i('ε'),i('rel')),op('='),frac(sv,V),op('×'),n(100),op('%')))
s+=txt('Erro instrumental adotado: 0,001 cm na bateria; 0,005 cm nas demais peças. Avaliam-se as fórmulas de volume e suas derivadas nas médias.')
sections.append(s)
cs=[frac(row(pi,D,h),n(2)),frac(row(pi,sup(D,2)),n(4))]
s=title('2. Bateria - cilindro')+txt('D: diâmetro externo; h: altura.')+eq(row(V,op('='),frac(row(pi,sup(D,2),h),n(4))))+txt('<b>Derivadas utilizadas na propagação</b>')+derivs([D,h],cs)+txt('<b>5 · Erro propagado</b>')+eq(row(sv,op('='),rootterms([row(c,sig(x)) for c,x in zip(cs,[D,h])])))+txt('<b>Resultado final</b>')+eq(row(V,op('='),par(row(n('1,00'),op('±'),n('0,03'))),'<mtext> cm³</mtext>'))
sections.append(s)
cs=[row(op('−'),frac(row(pi,h,d1),n(2))),frac(row(pi,h,d2),n(2)),frac(row(pi,par(diff(d2,d1))),n(4))]
s=title('3. Arruela')+txt('D₁: diâmetro do furo; D₂: diâmetro externo; h: altura.')+eq(row(V,op('='),ann(d2,h)))+txt('<b>Derivadas utilizadas na propagação</b>')+derivs([d1,d2,h],cs)+txt('<b>5 · Erro propagado</b>')+eq(row(sv,op('='),rootterms([row(c,sig(x)) for c,x in zip(cs,[d1,d2,h])])))+txt('O sinal negativo da primeira derivada desaparece quando o termo é elevado ao quadrado.')+txt('<b>Resultado final</b>')+eq(row(V,op('='),par(row(n('0,19'),op('±'),n('0,09'))),'<mtext> cm³</mtext>'))
sections.append(s)
xs=[d1,d2,d3,h1,h2]
cs=[row(op('−'),frac(row(pi,d1,par(row(h1,op('+'),h2))),n(2))),frac(row(pi,h2,d2),n(2)),frac(row(pi,h1,d3),n(2)),frac(row(pi,par(diff(d3,d1))),n(4)),frac(row(pi,par(diff(d2,d1))),n(4))]
v1=sub(V,n(1));v2=sub(V,n(2))
s=title('4. Cilindro com ressalto e furo')+txt('D₁: furo comum; D₂ e h₂: diâmetro e altura do ressalto; D₃ e h₁: diâmetro e altura da base.')+eq(row(v1,op('='),ann(d2,h2)))+eq(row(v2,op('='),ann(d3,h1)))+eq(row(V,op('='),v1,op('+'),v2))+txt('<b>5 · Erro propagado da peça inteira</b>')+eq(row(sv,op('='),rootterms([row(c,sig(x)) for c,x in zip(cs,xs)])))+txt('O mesmo D₁ aparece nas duas arruelas; sua contribuição é combinada antes de elevar ao quadrado. Os coeficientes que multiplicam cada σ são as derivadas do volume completo.')+txt('<b>Resultado final</b>')+eq(row(V,op('='),par(row(n('11,7'),op('±'),n('0,6'))),'<mtext> cm³</mtext>'))
sections.append(s)
csc=cs.copy();q=sqrt(diff(d3,L))
csc[2]=row(frac(row(h1,d3),n(4)),par(row(n(2),pi,op('−'),theta,op('+'),frac(row(n(2),L),q))))
csc[3]=par(row(cs[3],op('−'),A));csc.append(row(op('−'),frac(row(h1,sup(L,2)),row(n(2),q))))
s=title('5. Peça com ressalto, furo e corte plano')+txt('Mesmas dimensões da peça anterior, com L igual à corda do corte. O segmento removido atinge somente a base; θ é expresso em radianos.')+eq(row(R,op('='),frac(d3,n(2)),op(';'),theta,op('='),n(2),i('arcsen'),par(frac(L,d3))))+eq(row(A,op('='),frac(sup(d3,2),n(8)),par(row(theta,op('−'),i('sen'),theta))))+eq(row(sub(V,i('corte')),op('='),h1,A))+eq(row(V,op('='),ann(d2,h2),op('+'),ann(d3,h1),op('−'),h1,A))+txt('<b>5 · Erro propagado da peça inteira</b>')+eq(row(sv,op('='),rootterms([row(c,sig(x)) for c,x in zip(csc,xs+[L])])) )+txt('A e θ dependem de D₃ e L; essa dependência já está incluída na expressão. Os seis termos correspondem a D₁, D₂, D₃, h₁, h₂ e L, nessa ordem.')+txt('<b>Resultado final</b>')+eq(row(V,op('='),par(row(n('3,0'),op('±'),n('0,7'))),'<mtext> cm³</mtext>'))
sections.append(s)
html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Fórmulas - Relatório T0</title><style>@page{size:A4;margin:19mm 18mm}body{font-family:"Times New Roman";font-size:11pt;color:#000;margin:0}section{break-after:page}section:last-child{break-after:auto}h1{font-size:17pt;margin:0 0 16pt}h2{font-size:14pt;margin:0 0 14pt}p{line-height:1.35;margin:10pt 0}.eq{margin:14pt 0;break-inside:avoid}math{font-size:16px}section:last-child math{font-size:15px}.running{font-size:9pt;border-bottom:1px solid #888;padding-bottom:5pt;margin-bottom:17pt}</style>'''
for s in sections:html+='<section><div class="running">Física Geral Experimental I · Relatório T0 · Formulário</div>'+s+'</section>'
(p/'formulas.html').write_text(html+'</html>',encoding='utf-8')


