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

#visto ate aqui


# Actors
@APP.route('/actors/')
def list_actors():
    actors = db.execute('''
      SELECT ActorId, Name 
      FROM Actor
      ORDER BY Name
    ''').fetchall()
    return render_template('actor-list.html', actors=actors)


@APP.route('/actors/<int:id>/')
def view_movies_by_actor(id):
  actor = db.execute(
    '''
    SELECT ActorId, Name
    FROM ACTOR 
    WHERE ActorId = ?
    ''', [id]).fetchone()

  if actor is None:
     abort(404, 'Actor id {} does not exist.'.format(id))

  movies = db.execute(
    '''
    SELECT MovieId, Title
    FROM MOVIE NATURAL JOIN MOVIE_ACTOR
    WHERE ActorId = ?
    ORDER BY Title
    ''', [id]).fetchall()

  return render_template('actor.html', 
           actor=actor, movies=movies)
 
@APP.route('/actors/search/<expr>/')
def search_actor(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  actors = db.execute(
      ' SELECT ActorId, Name'
      ' FROM ACTOR '
      ' WHERE Name LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('actor-search.html', 
           search=search,actors=actors)

# Genres
@APP.route('/genres/')
def list_genres():
    genres = db.execute('''
      SELECT GenreId, Label 
      FROM GENRE
      ORDER BY Label
    ''').fetchall()
    return render_template('genre-list.html', genres=genres)

@APP.route('/genres/<int:id>/')
def view_movies_by_genre(id):
  genre = db.execute(
    '''
    SELECT GenreId, Label
    FROM GENRE 
    WHERE GenreId = ?
    ''', [id]).fetchone()

  if genre is None:
     abort(404, 'Genre id {} does not exist.'.format(id))

  movies = db.execute(
    '''
    SELECT MovieId, Title
    FROM MOVIE NATURAL JOIN MOVIE_GENRE
    WHERE GenreId = ?
    ORDER BY Title
    ''', [id]).fetchall()

  return render_template('genre.html', 
           genre=genre, movies=movies)

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

