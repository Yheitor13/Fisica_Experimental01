from pathlib import Path
import ast,math,statistics,re
root=Path.cwd(); work=root/'tmp/relatoriot0'
# Load only reusable MathML helpers and calculation data.
helper=(work/'criar_formulas.py').read_text(encoding='utf-8-sig').split('sections=[]')[0]
exec(helper)
tree=ast.parse((work/'criar_relatorio.py').read_text(encoding='utf-8-sig'))
a=next(j for j,t in enumerate(tree.body) if isinstance(t,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='pieces' for v in t.targets))
b=next(j for j in range(a,len(tree.body)) if isinstance(tree.body[j],ast.For))
exec(compile(ast.Module(body=tree.body[a:b+1],type_ignores=[]),'calc','exec'))
exec(helper)
def fmt(v,d=8):return f'{v:.{d}f}'.replace('.',',')
def num(v,d=8):return n(fmt(v,d))
def unit(power=1):return '<mtext> cm'+('' if power==1 else ('²' if power==2 else '³'))+'</mtext>'
def join(xs):return row(*[t for j,x in enumerate(xs) for t in ([op('+')] if j else [])+[x]])
def bar(x):return '<mover>'+x+op('¯')+'</mover>'
def symbol(k):return sub(i(k[0]),n(k[1])) if len(k)==2 else i(k)
def heading(t):return '<h3>'+t+'</h3>'
def block(s):return '<div class="block">'+s+'</div>'
def radical(terms,per=2):
 rows=[]
 for z in range(0,len(terms),per):
  rr=join([sq(t) for t in terms[z:z+per]])
  rows.append('<mtr><mtd>'+row(op('+') if z else '',rr)+'</mtd></mtr>')
 return sqrt('<mtable columnalign="left" rowspacing="0.55em">'+''.join(rows)+'</mtable>')
def coeff(ix,z):
 if ix==0:return [frac(row(pi,z['D'],z['h']),n(2)),frac(row(pi,sup(z['D'],2)),n(4))]
 if ix==1:return [row(op('−'),frac(row(pi,z['h'],z['D1']),n(2))),frac(row(pi,z['h'],z['D2']),n(2)),frac(row(pi,par(diff(z['D2'],z['D1']))),n(4))]
 d1,d2,d3,h1,h2=[z[k] for k in ['D1','D2','D3','h1','h2']]
 c=[row(op('−'),frac(row(pi,d1,par(row(h1,op('+'),h2))),n(2))),frac(row(pi,h2,d2),n(2)),frac(row(pi,h1,d3),n(2)),frac(row(pi,par(diff(d3,d1))),n(4)),frac(row(pi,par(diff(d2,d1))),n(4))]
 if ix==3:
  L=z['L'];t=z['theta'];AA=z['A'];q=sqrt(diff(d3,L))
  c[2]=row(frac(row(h1,d3),n(4)),par(row(n(2),pi,op('−'),t,op('+'),frac(row(n(2),L),q))))
  if '<mn>' in t:
   inner='<mtable columnalign="left"><mtr><mtd>'+row(n(2),pi,op('−'),t)+'</mtd></mtr><mtr><mtd>'+row(op('+'),frac(row(n(2),L),q))+'</mtd></mtr></mtable>'
   c[2]=row(frac(row(h1,d3),n(4)),par(inner))
  c[3]=par(row(c[3],op('−'),AA));c.append(row(op('−'),frac(row(h1,sup(L,2)),row(n(2),q))))
 return c
names=['Moeda / bateria','Arruela','Cilindro com ressalto e furo','Cilindro com ressalto, furo e corte plano']
finals=[('1,00','0,03',0),('1,9','0,9',-1),('1,17','0,06',1),('3,0','0,7',0)]
def finalvol(ix):
 v,u,pow=finals[ix];return row(V,op('='),par(row(n(v),op('±'),n(u))),op('×'),sup(n(10),pow),unit(3))
def measurefinal(k,m,u):
 exponent=math.floor(math.log10(abs(m)));place=math.floor(math.log10(u));dec=max(0,exponent-place)
 return row(symbol(k),op('='),par(row(n(fmt(round(m,-place)/10**exponent,dec)),op('±'),n(fmt(round(u,-place)/10**exponent,dec)))),op('×'),sup(n(10),exponent),unit())
def table(data):
 s='<table><thead><tr><th>Grandeza</th><th>Medida 1 (cm)</th><th>Medida 2 (cm)</th><th>Medida 3 (cm)</th></tr></thead><tbody>'
 for k,vals in data.items():s+='<tr><td>'+re.sub(r'(\d)',r'<sub>\1</sub>',k)+'</td>'+''.join('<td>'+fmt(v,2)+'</td>' for v in vals)+'</tr>'
 return s+'</tbody></table>'
def volume_content(ix):
 m,sd,e,u=stats[ix];z={k:par(num(v)) for k,v in m.items()};v,uv=vols[ix]
 s=''
 if ix==0:
  s+=txt('O volume é a área circular da base multiplicada pela altura.')+eq(row(V,op('='),frac(row(pi,sup(D,2),h),n(4))))
  s+=eq(row(V,op('≈'),frac(row(pi,sup(z['D'],2),z['h']),n(4)),unit(3),op('≈'),num(v),unit(3)))
 elif ix==1:
  s+=txt('Subtraímos o cilindro do furo do cilindro externo.')+eq(row(V,op('='),ann(d2,h)))
  s+=eq(row(V,op('≈'),frac(row(pi,z['h']),n(4)),par(diff(z['D2'],z['D1'])),unit(3),op('≈'),num(v),unit(3)))
 else:
  s+=txt('Somamos duas arruelas com o mesmo furo D₁. A superior usa D₂ e h₂; a base usa D₃ e h₁.')
  values=[]
  for j,dk,hk in [(1,'D2','h2'),(2,'D3','h1')]:
   val=math.pi*m[hk]*(m[dk]**2-m['D1']**2)/4;values.append(val)
   s+=eq(row(sub(V,n(j)),op('='),ann(symbol(dk),symbol(hk))))
   s+=eq(row(sub(V,n(j)),op('≈'),frac(row(pi,z[hk]),n(4)),par(diff(z[dk],z['D1'])),unit(3),op('≈'),num(val),unit(3)))
  if ix==2:s+=eq(row(V,op('='),sub(V,n(1)),op('+'),sub(V,n(2)),op('≈'),num(values[0]),op('+'),num(values[1]),op('≈'),num(v),unit(3)))
  else:
   radius=m['D3']/2;t=2*math.asin(m['L']/m['D3']);AA=m['D3']**2/8*(t-math.sin(t))
   s+=heading('Volume retirado pelo corte')+txt('O corte é um segmento circular da base. A calculadora deve estar em radianos.')
   s+=eq(row(R,op('='),frac(d3,n(2)),op('≈'),frac(num(m['D3']),n(2)),op('='),num(radius),unit()))
   s+=eq(row(theta,op('='),n(2),i('arcsen'),par(frac(L,d3)),op('≈'),n(2),i('arcsen'),par(frac(num(m['L']),num(m['D3']))),op('≈'),num(t),'<mtext> rad</mtext>'))
   s+=eq(row(A,op('='),frac(sup(R,2),n(2)),par(row(theta,op('−'),i('sen'),theta))))
   s+=eq(row(A,op('≈'),frac(sq(num(radius)),n(2)),par(row(num(t),op('−'),i('sen'),par(num(t)))),unit(2),op('≈'),num(AA),unit(2)))
   s+=eq(row(sub(V,i('corte')),op('='),h1,A,op('≈'),num(m['h1']),op('×'),num(AA),op('≈'),num(m['h1']*AA),unit(3)))
   s+=eq(row(V,op('='),sub(V,n(1)),op('+'),sub(V,n(2)),op('−'),sub(V,i('corte'))))
   s+=eq(row(V,op('≈'),num(values[0]),op('+'),num(values[1]),op('−'),num(m['h1']*AA),op('≈'),num(v),unit(3)))
 return s
pages=[]
def addpage(name,s):pages.append(title(name)+s)
for ix,(name,data,inst) in enumerate(pieces):
 m,sd,e,u=stats[ix];keys=list(data);zs={k:symbol(k) for k in keys};zs.update(theta=theta,A=A);cs=coeff(ix,zs)
 z={k:par(num(v)) for k,v in m.items()}
 if ix==3:
  t=2*math.asin(m['L']/m['D3']);AA=m['D3']**2/8*(t-math.sin(t));z.update(theta=par(num(t)),A=par(num(AA)))
 cn=coeff(ix,z);v,uv=vols[ix]
 intro=txt('Resolução em centímetros. Cada dimensão possui três leituras; são preservados os valores confirmados. Os números exibidos são aproximações; os cálculos mantêm a precisão interna até o arredondamento final.') if ix==0 else ''
 intro+=table(data)
 if ix==3:intro+=txt('L é a largura da corda do corte; sua segunda leitura é 1,31 cm.')
 intro+=heading('1. Média')+txt('Somamos as três medidas e dividimos por 3.')
 for k,vals in data.items():intro+=eq(row(bar(symbol(k)),op('='),frac(join([num(x,2) for x in vals]),n(3)),op('='),frac(num(sum(vals),2),n(3)),op('≈'),num(m[k]),unit()))
 if ix==1:intro+=txt('A média de h é 0,08333333 cm. O valor 0,12 cm anotado no roteiro não corresponde às três medidas.')
 addpage(names[ix]+' · Dados e média',intro)
 s=heading('2. Desvio padrão amostral')+txt('Calculamos os desvios em relação à média, elevamos ao quadrado, somamos, dividimos por N − 1 = 2 e extraímos a raiz. A média aparece como fração para evitar arredondamento nos desvios.')
 for k,vals in data.items():
  ssq=sum((x-m[k])**2 for x in vals);mean=frac(num(sum(vals),2),n(3))
  s+=block(eq(row(sub(i('s'),symbol(k)),op('='),sqrt(frac(join([sq(row(num(x,2),op('−'),mean)) for x in vals]),n(2))),unit()))+eq(row(sub(i('s'),symbol(k)),op('≈'),sqrt(frac(num(ssq,10),n(2))),unit(),op('≈'),num(sd[k]),unit())))
 addpage(names[ix]+' · Dispersão das medidas',s)
 s=heading('3. Erro estatístico')+txt('Dividimos o desvio padrão por √3 para obter a incerteza da média.')
 for k in keys:s+=eq(row(sig(row(i('est'),op(','),symbol(k))),op('='),frac(sub(i('s'),symbol(k)),sqrt(n(3))),op('≈'),frac(num(sd[k]),sqrt(n(3))),unit(),op('≈'),num(e[k]),unit()))
 s+=heading('4. Erro total')+txt('Combinamos o erro estatístico e o instrumental pela raiz da soma dos quadrados.')
 s+=eq(row(sig(i('inst')),op('='),num(inst*10,2),'<mtext> mm</mtext>',op('='),frac(num(inst*10,2),n(10)),unit(),op('='),num(inst,3),unit()))
 if ix>1:s+=txt('Adota-se o mesmo erro instrumental da arruela, pois o item não informa outro valor.')
 for k in keys:s+=eq(row(sig(symbol(k)),op('≈'),sqrt(row(sq(num(e[k])),op('+'),sq(num(inst,3)))),unit(),op('≈'),num(u[k]),unit()))
 addpage(names[ix]+' · Erros estatístico e total',s)
 addpage(names[ix]+' · Volume',heading('5. Volume e erro propagado')+volume_content(ix))
 s=heading('Aplicação da equação (5) do roteiro')+txt('As derivadas são avaliadas nas médias. Cada σ é o erro total calculado no passo 4.')
 s+=eq(row(sup(sv,2),op('='),join([row(sq(der(symbol(k))),sup(sig(symbol(k)),2)) for k in keys])))
 if ix>1:s+=txt('O furo D₁ é compartilhado pelas duas arruelas; por isso, sua derivada usa a soma h₁ + h₂.')
 if ix==3:
  s+=txt('O ângulo e a área do corte dependem de D₃ e L. Essa dependência está incluída nas derivadas abaixo; não são grandezas medidas adicionais.')
 for k,c in zip(keys,cs):s+=eq(row(der(symbol(k)),op('='),c))
 s+=txt('A seguir, substituímos essas derivadas e os erros totais em uma única expressão para a incerteza da peça inteira.')
 addpage(names[ix]+' · Derivadas do volume',s)
 s=heading('Expressão completa do erro propagado')+eq(row(sv,op('='),radical([row(c,sig(symbol(k))) for k,c in zip(keys,cs)])))
 s+=heading('Substituição dos valores')+txt('Inserimos as médias e os erros totais já calculados. Todos os termos dentro da raiz pertencem à mesma soma.')
 s+='<div class="numeric">'+eq(row(sv,op('≈'),radical([row(c,par(num(u[k]))) for k,c in zip(keys,cn)],1),unit(3)))+'</div>'
 addpage(names[ix]+' · Substituição na propagação',s)
 s=heading('Calculando cada parcela')+txt('Calculamos primeiro os produtos que serão elevados ao quadrado. O sinal negativo desaparece após a elevação ao quadrado.')
 for k,c in zip(keys,cn):s+=eq(row(c,par(num(u[k])),unit(3),op('≈'),num(termsall[ix][k]),unit(3)))
 s+=heading('Somando os quadrados e extraindo a raiz')+eq(row(sv,op('≈'),radical([num(termsall[ix][k]) for k in keys]),unit(3)))
 s+=eq(row(sv,op('≈'),sqrt(num(sum(t*t for t in termsall[ix].values()),10)),unit(3),op('≈'),num(uv),unit(3)))
 s+=eq(row(V,op('≈'),par(row(num(v),op('±'),num(uv))),unit(3)))
 addpage(names[ix]+' · Cálculo das parcelas',s)
 s=heading('Resultado final e respostas ao enunciado')+txt('Arredondamos a incerteza para um algarismo significativo e o volume para a mesma casa decimal.')+eq(finalvol(ix))
 s+=eq(row(sub(i('ε'),i('rel')),op('='),frac(sv,V),op('×'),n(100),op('%'),op('≈'),frac(num(uv),num(v)),op('×'),n(100),op('%'),op('≈'),num(100*uv/v,2),op('%')))
 s+=txt('<b>Item 1.</b> As três leituras de cada dimensão estão na tabela inicial desta peça.')+txt('<b>Item 2.</b> As médias e os erros totais, com o arredondamento final, são:')
 for k in keys:s+=eq(measurefinal(k,m[k],u[k]))
 if ix<2:s+=txt('<b>Item 3a.</b> Volume calculado com as médias: '+fmt(v)+' cm³.<br/><b>Item 3b.</b> Erro propagado: '+fmt(uv)+' cm³.<br/><b>Item 3c.</b> Volume em notação científica:')+eq(finalvol(ix))
 else:s+=txt('<b>Item 2, continuação.</b> A dedução do volume e sua propagação foram desenvolvidas no passo 5, repetindo o procedimento solicitado. Este item do roteiro apresenta perguntas 1 e 2.')
 s+=txt('O volume obtido é positivo. '+('A dispersão das alturas explica a incerteza relativa elevada; as leituras confirmadas foram mantidas.' if ix in [1,3] else 'O resultado é coerente com as dimensões e o modelo geométrico adotado.'))
 addpage(names[ix]+' · Respostas finais',s)
css='''@page{size:A4;margin:17mm 17mm 18mm}body{font-family:"Times New Roman";font-size:11pt;color:#000;margin:0}section{break-after:page}section:last-child{break-after:auto}h2{font-size:15pt;margin:0 0 14pt}h3{font-size:12pt;margin:13pt 0 9pt;break-after:avoid}p{line-height:1.3;margin:8pt 0}.eq{margin:12pt 0;break-inside:avoid}math{font-size:16px}.numeric math{font-size:14px}.block{break-inside:avoid}.running{font-size:9pt;border-bottom:1px solid #888;padding-bottom:5pt;margin-bottom:14pt}table{border-collapse:collapse;width:100%;margin:15pt 0;font-size:10.5pt}thead{border-top:1px solid black;border-bottom:1px solid black}tbody{border-bottom:1px solid black}td,th{padding:5pt;text-align:center}.num{text-align:right;font-size:10pt;margin-top:-5pt}.eqno{break-inside:avoid}'''
def writehtml(name,pp):
 html='<!doctype html><html lang="pt-BR"><meta charset="utf-8"><style>'+css+'.block .eq{margin:9pt 0}</style>'
 for j,s in enumerate(pp,1):html+='<section><div class="running">Física Geral Experimental I · '+name+' · '+str(j)+'</div>'+s+'</section>'
 (work/(name+'.html')).write_text(html+'</html>',encoding='utf-8')
writehtml('Resolucao_Completa',pages)
# Exact numbered equations from the report and its unnumbered applications.
rp=[]
def numbered(content,num):return '<div class="eqno">'+content+'<div class="num">('+str(num)+')</div></div>'
x=i('x');N=i('N');xb=bar(x);xi=sub(x,i('i'));summ='<munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>N</mi></munderover>'
s=title('Equações do Relatório T0')+txt('Transcrição matemática das equações numeradas (1) a (8) e das aplicações sem número. A numeração original foi preservada.')+heading('Tratamento estatístico')
s+=numbered(eq(row(xb,op('='),frac(join([sub(x,n(j)) for j in [1,2,3]]),n(3))))+eq(row(i('s'),op('='),sqrt(frac(row(summ,sq(row(xi,op('−'),xb))),row(N,op('−'),n(1)))))),1)
s+=numbered(eq(row(sig(i('est')),op('='),frac(i('s'),sqrt(N))))+eq(row(sig(i('total')),op('='),sqrt(row(sup(sig(i('est')),2),op('+'),sup(sig(i('inst')),2))))),2)
s+=numbered(eq(row(sup(sv,2),op('='),'<munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>m</mi></munderover>',sq(row(der(xi),sig(xi))))),3)
s+=txt('N = 3 leituras. Na soma de propagação, m é o número de dimensões distintas do volume. As derivadas são avaliadas nas médias; as dimensões distintas são consideradas sem correlação.')
s+=heading('Conversões usadas no relatório')+eq(row(sig(i('inst')),op('='),n('0,01'),'<mtext> mm</mtext>',op('='),n('0,001'),unit()))+eq(row(sig(i('inst')),op('='),n('0,05'),'<mtext> mm</mtext>',op('='),n('0,005'),unit()))
rp.append(s)
s=title('Exemplo do relatório: diâmetro da bateria');m,sd,e,u=stats[0]
s+=eq(row(bar(D),op('='),frac(join([n('2,08'),n('2,03'),n('2,00')]),n(3)),op('≈'),num(m['D']),unit()))
s+=eq(row(sub(i('s'),D),op('='),sqrt(frac(join([sq(row(num(t,2),op('−'),bar(D))) for t in pieces[0][1]['D']]),n(2)))))
s+=eq(row(sub(i('s'),D),op('≈'),num(sd['D']),unit()))
s+=eq(row(sig(row(i('est'),op(','),D)),op('='),frac(sub(i('s'),D),sqrt(n(3))),op('≈'),num(e['D']),unit()))
s+=eq(row(sig(D),op('≈'),sqrt(row(sq(num(e['D'])),op('+'),sq(n('0,001')))),op('≈'),num(u['D']),unit()))
s+=heading('Volumes da bateria e da arruela')+numbered(eq(row(sub(V,i('bateria')),op('='),frac(row(pi,sup(D,2),h),n(4))))+eq(row(sub(V,i('arruela')),op('='),ann(d2,h))),4)
s+=volume_content(0)+volume_content(1)
rp.append(s)
s=title('Volumes das peças compostas')+numbered(eq(row(sub(V,n(1)),op('='),ann(d2,h2)))+eq(row(sub(V,n(2)),op('='),ann(d3,h1))),5)
s+=eq(row(sub(V,i('ressalto')),op('='),sub(V,n(1)),op('+'),sub(V,n(2)),op('≈'),n('0,79116560'),op('+'),n('10,92460315'),op('≈'),n('11,71576875'),unit(3)))
s+=numbered(eq(row(R,op('='),frac(d3,n(2))))+eq(row(theta,op('='),n(2),i('arcsen'),par(frac(L,d3))))+eq(row(A,op('='),frac(sup(R,2),n(2)),par(row(theta,op('−'),i('sen'),theta)))),6)
s+=numbered(eq(row(sub(V,i('com corte')),op('='),sub(V,n(1)),op('+'),sub(V,n(2)),op('−'),h1,A)),7)
s+=txt('D₁ é o furo comum; D₂ e h₂ descrevem o ressalto, D₃ e h₁ descrevem a base; L é a corda do corte. θ é calculado em radianos.')
rp.append(s)
s=title('Aplicação numérica do corte plano')
s+=eq(row(R,op('='),frac(n('2,17'),n(2)),op('='),n('1,085'),unit()))+eq(row(theta,op('≈'),n('1,28853876'),'<mtext> rad</mtext>'))+eq(row(A,op('≈'),n('0,19312945'),unit(2)))+eq(row(h1,A,op('≈'),n('0,15514732'),unit(3)))
s+=eq(row(sub(V,i('com corte')),op('≈'),n('0,41866609'),op('+'),n('2,76362115'),op('−'),n('0,15514732'),op('≈'),n('3,02713992'),unit(3)))
s+=heading('Verificação geométrica usada no texto')+eq(row(i('d'),op('='),sqrt(row(sup(R,2),op('−'),sq(frac(L,n(2))))),op('≈'),n('0,8675'),unit()))+eq(row(frac(d2,n(2)),op('≈'),n('0,5967'),unit(),op(';'),frac(d1,n(2)),op('≈'),n('0,2867'),unit()))
s+=txt('A distância do centro à corda supera os raios do ressalto e do furo, justificando a retirada de material apenas da base.')
rp.append(s)
s=title('Propagação das incertezas no relatório')+heading('Bateria')
z={'D':D,'h':h};cb=coeff(0,z)
s+=derivs([D,h],cb)+eq(row(sv,op('='),radical([row(c,sig(x)) for c,x in zip(cb,[D,h])])))+eq(row(sv,op('≈'),sqrt(join([sq(n('0,02291298')),sq(n('0,01133762'))])),op('≈'),n('0,02556455'),unit(3)))
s+=heading('Derivadas da arruela citadas no texto')+derivs([d1,d2,h],coeff(1,{'D1':d1,'D2':d2,'h':h}))
s+=heading('Furo compartilhado nas peças compostas')+eq(row(der(d1),op('='),row(op('−'),frac(row(pi,d1,par(row(h1,op('+'),h2))),n(2)))))
rp.append(s)
da3=frac(row(op('∂'),A),row(op('∂'),d3));daL=frac(row(op('∂'),A),row(op('∂'),L));q=sqrt(diff(d3,L))
s=title('Derivadas do corte e resultados finais')+numbered(eq(row(da3,op('='),frac(d3,n(4)),par(row(theta,op('−'),frac(row(n(2),L),q)))))+eq(row(daL,op('='),frac(sup(L,2),row(n(2),q)))),8)
s+=heading('Derivadas do volume citadas após a equação (8)')+eq(row(der(d3),op('='),h1,par(row(frac(row(pi,d3),n(2)),op('−'),da3))))+eq(row(der(h1),op('='),frac(row(pi,par(diff(d3,d1))),n(4)),op('−'),A))+eq(row(der(L),op('='),op('−'),h1,daL))
s+=heading('Incerteza relativa e apresentação dos resultados')+eq(row(sub(i('ε'),i('rel')),op('='),frac(sv,V),op('×'),n(100),op('%')))
for ix in range(4):s+=txt(names[ix])+eq(finalvol(ix))
rp.append(s)
writehtml('Equacoes_do_RelatorioT0',rp)
print('Páginas planejadas:',len(pages),len(rp))

