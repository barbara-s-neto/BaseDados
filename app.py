import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db
APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    stats = db.execute('''
    SELECT * FROM
      (SELECT COUNT(*) n_jogadores FROM jogadores)
    JOIN
      (SELECT COUNT(*) n_equipas FROM equipas)
    JOIN
      (SELECT COUNT(*) n_regioes FROM regioes)
    JOIN 
      (SELECT COUNT(*) n_patrocinadores FROM patrocinadores)
    JOIN 
      (SELECT COUNT(*) n_parcerias FROM parcerias)
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html',stats=stats)

# Equipas
@APP.route('/equipas/')
def list_equipas():
    equipas = db.execute(
      '''
      SELECT *
      FROM equipas
      ORDER BY nome
      ''').fetchall()
    return render_template('equipas-list.html', equipas=equipas)

@APP.route('/equipas/<expr>/')
def get_equipa(expr):
  equipa = db.execute(
      '''SELECT sigla, nome, Njogos, NJogosGanhos, RacioDeVitorias, KD, AssassinatosPorJogo, MortesPorJogo, regiao
      FROM equipas 
      WHERE sigla = ?'''
      ,[expr]).fetchone()

  if equipa is None:
     abort(404, 'Não existe equipa com sigla {}.'.format(expr))

  return render_template('equipa.html', equipa=equipa)

@APP.route('/equipas/vertudo/<expr>/')
def get_equipacompleta(expr):
  equipa = db.execute(
      '''SELECT sigla, nome, Njogos, NJogosGanhos, RacioDeVitorias, KD, AssassinatosPorJogo, MortesPorJogo, regiao
      FROM equipas 
      WHERE sigla = ?'''
      ,[expr]).fetchone()

  if equipa is None:
     abort(404, 'Não existe equipa com sigla {}.'.format(expr))

  regiao = db.execute(
      '''
      SELECT r.nome , r.sigla
      FROM regioes r JOIN equipas e on e.regiao=r.sigla
      WHERE e.sigla = ?
      ''', [expr]).fetchone()

  jogadores = db.execute(
      '''
      SELECT j.nickname
      FROM jogadores j join equipas e on j.equipa=e.sigla
      WHERE e.sigla = ?
      ORDER BY j.nickname Desc
      ''', [expr]).fetchall()

  parcerias = db.execute(
      ''' 
      SELECT p.nome
      FROM parcerias p join equipas e on e.sigla=p.sigla
      WHERE p.sigla = ?
      ORDER BY p.nome Desc
      ''', [expr]).fetchall()
  return render_template('equipavermais.html', 
           equipa=equipa, regiao=regiao, jogadores=jogadores, parcerias=parcerias)

@APP.route('/equipas/search/<expr>/')
def search_equipa(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  equipas = db.execute(
      'SELECT sigla, nome'
      'FROM equipas'
      'WHERE nome LIKE \'%' + expr + '%\''
      ).fetchall()
  return render_template('equipa-search.html',
           search=search,equipas=equipas)



# Jogadores
@APP.route('/jogadores/')
def list_jogadores():
    jogadores = db.execute('''
      SELECT nickname, regiao, equipa
      FROM jogadores
      ORDER BY nickname
    ''').fetchall()
    return render_template('jogador-list.html', jogadores=jogadores)

#visto ate aqui

@APP.route('/jogadores/<expr>/')
def ver_jogador(expr):
  jogador = db.execute(
    
    'SELECT *'
    'FROM jogadores'
   ' WHERE nickname = \''+ expr + '\''
    ).fetchone()

  if jogador is None:
     abort(404, 'O jogador {} não existe. Por favor tenha em atenção os caracteres maiúsculos e minúsculos'.format(expr))

  return render_template('jogador.html', 
           jogador=jogador)
 
@APP.route('/jogadores/search/<expr>/')
def search_jogador(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  jogadores = db.execute(
      ' SELECT nickname'
      ' FROM jogadores '
      ' WHERE nickname LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('jogador-search.html', 
           search=search,jogadores=jogadores)

@APP.route('/jogadores/searchbyteam/<expr>/')
def searchbyteam_jogador(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  jogadores = db.execute(
      ' SELECT nickname'
      ' FROM jogadores '
      ' WHERE equipa = \'' + expr + '\''
    ).fetchall()

  return render_template('jogador-search.html', 
           search=search,jogadores=jogadores)


@APP.route('/jogadores/naojogamemcasa')
def jogador_foradecasa():

  jogadores = db.execute(
     'SELECT nickname'
     'FROM jogadores'
     'Where nickname not in (SELECT j.nickname FROM jogadores j natural join equipas e WHERE j.regiao=e.regiao)'
    ).fetchall()

  return render_template('jogadoresforadecasa.html', 
           jogadores=jogadores)

# Regiões
@APP.route('/regioes/')
def list_regioes():
    regioes = db.execute('''
      SELECT sigla
      FROM regioes
      ORDER BY nome
    ''').fetchall()
    return render_template('regioes-list.html', regioes=regioes)

@APP.route('/regioes/<expr>/')
def ver_nome_regiao(expr):
  regiao = db.execute(
    '''
    SELECT sigla, nome
    FROM regioes
    WHERE sigla = ?
    ''', [expr]).fetchone()

  if regiao is None:
     abort(404, 'Não existe região com sigla {}.'.format(expr))

  #movies = db.execute(
   # '''
    #SELECT MovieId, Title
   # FROM MOVIE NATURAL JOIN MOVIE_GENRE
   # WHERE GenreId = ?
    #ORDER BY Title
   # ''', [id]).fetchall()

  return render_template('regioes.html', 
           #genre=genre, 
           regiao=regiao)

#Patrocinadores
@APP.route('/patrocinadores/')
def list_patrocinadores():
    patrocinadores = db.execute('''
      SELECT nome
      FROM patrocinadores
      ORDER BY nome
    ''').fetchall()
    return render_template('patrocinadores-list.html', patrocinadores=patrocinadores)

@APP.route('/patrocinadores/search/<expr>/')
def search_patrocinador(expr):
  search = { 'expr': expr }
 
  patrocinadores = db.execute(
      ' SELECT nome'
      ' FROM patrocinadores'
      ' WHERE nome LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('patrocinadores-search.html', 
           search=search,patrocinadores=patrocinadores)

@APP.route('/patrocinadores/<expr>/')
def ver_patrocinador(expr):
  patrocinador = db.execute(
    '''
    SELECT nome
    FROM patrocinadores
    WHERE nome = ?
    ''', [expr]).fetchone()

  if patrocinador is None:
     abort(404, '{} nao é um patrocinador.'.format(expr))

  return render_template('patrocinador.html',  
           patrocinador=patrocinador)

#Parcerias
@APP.route('/parcerias/byteam/<expr>')
def list_patrocinadoresbyteam(expr):
    search = { 'expr': expr }
    patrocinadores = db.execute(
     ' SELECT nome'
      ' FROM parcerias '
      ' WHERE sigla = \'' + expr + '\''
    ).fetchall()

    if patrocinadores is None:
     abort(404, '{} nao é a sigla de nenhuma equipa.'.format(expr))

    return render_template('parcerias-byteam-list.html', patrocinadores=patrocinadores, search=search)

@APP.route('/parcerias/bysponsor/<expr>')
def list_patrocinadoresbysponsor(expr):
    search = { 'expr': expr }
    patrocinadores = db.execute(
     ' SELECT sigla'
      ' FROM parcerias '
      ' WHERE nome = \'' + expr + '\''
    ).fetchall()

    if patrocinadores is None:
     abort(404, '{} nao é um patrocinador.'.format(expr))

    return render_template('parcerias-bysponsor-list.html', patrocinadores=patrocinadores, search=search)

@APP.route('/parcerias/')
def list_parcerias():
    parcerias = db.execute('''
      SELECT sigla, nome
      FROM parcerias
      ORDER BY sigla
    ''').fetchall()
    return render_template('parcerias-list.html', parcerias=parcerias)
#visto ate aqui

