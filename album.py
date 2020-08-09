import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_path = ""
DB_PATH = "sqlite:////Users/dezdezu/Documents/SF/b/b6/b6.13/albums.sqlite3"
Base = declarative_base()


class Album(Base):
    """
    Описывает структуру таблицы album для хранения записей музыкальной библиотеки
    """

    __tablename__ = "album"

    id = sa.Column(sa.INTEGER, primary_key=True)
    year = sa.Column(sa.INTEGER)
    artist = sa.Column(sa.TEXT)
    genre = sa.Column(sa.TEXT)
    album = sa.Column(sa.TEXT)


def connect_db():
    """
    Устанавливает соединение к базе данных, создает таблицы, если их еще нет и возвращает объект сессии
    если переменная db_path пустая (не вводился путь к базе данных), то используется путь по умолчанию (DB_PATH)
    """
    if db_path == "":
        engine = sa.create_engine(DB_PATH)
    else:
        engine = sa.create_engine(db_path)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()


def find(artist):
    """
    Находит все альбомы в базе данных по заданному артисту (в формате БД)
    """
    session = connect_db()
    albums = session.query(Album).filter(Album.artist == artist).all()
    return albums

def get_artists_list():
    '''
    Возвращает список артистов в базе данных (в формате списка)
    '''
    session = connect_db()
    artists = session.query(Album).all()
    artists_names = [album.artist for album in artists]
    result = []
    for _ in artists_names:
        if _ not in result:
            result.append(_)
    return result

def is_valid(artist, album, genre, year):
    '''
    Проверяет, нет ли такой записи в базе (по полям artist и album), а также корректное значение года
    '''
    session = connect_db()
    all_records = session.query(Album).all()
    new_record = Album(
        id = 0,
        year = year,
        artist = artist,
        genre = genre,
        album = album
    )
    if new_record.artist == "" or new_record.album == "" or new_record.genre == "":
        return False
    for _ in all_records:
        if _.artist == new_record.artist and _.album == new_record.album:
            return False
    return True

def add_record(artist, album, genre, year):
    session = connect_db()
    new_record = Album(
        id = len(session.query(Album).all()) + 1,
        year = year,
        artist = artist,
        genre = genre,
        album = album
    )
    session.add(new_record)
    session.commit()
# список из объектов - элеметнов базы данных

# session = connect_db()
# artists = session.query(Album).all()

# список из артистов



# print(len(artists))
# print(artists[0].id)