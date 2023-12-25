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
      '''
      SELECT sigla, nome, Njogos, NJogosGanhos, RacioDeVitorias, KD, AssassinatosPorJogo, MortesPorJogo
      FROM equipas 
      WHERE sigla = ?
      ''', [expr]).fetchone()

  if equipa is None:
     abort(404, 'Não existe equipa com sigla {}.'.format(expr))

  regiao = db.execute(
      '''
      SELECT r.nome 
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
  return render_template('equipa.html', 
           equipa=equipa, regiao=regiao, jogadores=jogadores, parcerias=parcerias)

@APP.route('/equipas/search/<expr>/')
def search_equipa(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  equipas = db.execute(
      ''' 
      SELECT sigla, nome
      FROM equipas
      WHERE nome LIKE ?
      ''', [expr]).fetchall()
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

  #movies = db.execute(
   # '''
    #SELECT MovieId, Title
    #FROM MOVIE NATURAL JOIN MOVIE_ACTOR
   # WHERE ActorId = ?
    #ORDER BY Title
    #''', [id]).fetchall()

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

#visto ate aqui

# Streams
@APP.route('/streams/<int:id>/')
def get_stream(id):
  stream = db.execute(
      '''
      SELECT StreamId, StreamDate, Charge, MovieId, Title, CustomerId, Name
      FROM STREAM NATURAL JOIN MOVIE NATURAL JOIN CUSTOMER 
      WHERE StreamId = ?
      ''', [id]).fetchone()

  if stream is None:
     abort(404, 'Stream id {} does not exist.'.format(id))

  return render_template('stream.html', stream=stream)


# Staff
@APP.route('/staff/')
def list_staff():
    staff = db.execute('''
      SELECT S1.StaffId AS StaffId, 
             S1.Name AS Name,
             S1.Job AS Job, 
             S1.Supervisor AS Supervisor,
             S2.Name AS SupervisorName
      FROM STAFF S1 LEFT JOIN STAFF S2 ON(S1.Supervisor = S2.StaffId)
      ORDER BY S1.Name
    ''').fetchall()
    return render_template('staff-list.html', staff=staff)

@APP.route('/staff/<int:id>/')
def show_staff(id):
  staff = db.execute(
    '''
    SELECT StaffId, Name, Supervisor, Job
    FROM STAFF
    WHERE staffId = ?
    ''', [id]).fetchone()

  if staff is None:
     abort(404, 'Staff id {} does not exist.'.format(id))
  superv={}
  if not (staff['Supervisor'] is None):
    superv = db.execute(
      '''
      SELECT Name
      FROM staff
      WHERE staffId = ?
      ''', [staff['Supervisor']]).fetchone()
  supervisees = []
  supervisees = db.execute(
    '''
      SELECT StaffId, Name from staff
      where Supervisor = ?
      ORDER BY Name
    ''',[id]).fetchall()

  return render_template('staff.html', 
           staff=staff, superv=superv, supervisees=supervisees)

