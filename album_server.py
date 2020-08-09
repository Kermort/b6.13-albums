from bottle import route
from bottle import run
from bottle import request
from bottle import HTTPError
from bottle import redirect
import os
import album

@route("")
@route("/")
def redirect_to_help():
    '''
    Перенаправление с корневой страницы на страницу помощи
    '''
    redirect("http://localhost:8080/help")

@route("/albums/<artist>")
def albums(artist):
    '''
    поиск альбомов исполнителя <artist> и вывод в виде списка
    '''
    albums_list = album.find(artist)
    if not albums_list:
        message = f"Альбомов исполнителя {artist} не найдено"
        result = HTTPError(404, message)
    else:
        album_names = [album.album for album in albums_list]
        result = f"Количество альбомов исполнителя {artist} - {len(album_names)}<br>"
        result += "Список альбомов:<br> "
        result += "\n".join(f"<li>{name}</li>" for name in album_names)
        result = "<ul>" + result + "</ul>" + "<br><a href='http://localhost:8080/artists'>Исполнители</a>"
        result = result + "<br><a href='http://localhost:8080/help'>Помощь</a>"
    return result

# тут получаем данные из форм для записи и передаем их в базу данных
@route("/albums", method="POST")
@route("/albums/", method="POST")
def add_record():
    '''
    Получение данных из форм (или напрямую из запроса), их проверка и запись в базу данных
    '''
    # проверка данных
    try:
        new_artist = request.forms.get("new_artist")
        new_album = request.forms.get("new_album")
        new_genre = request.forms.get("new_genre")
        new_year = int(request.forms.get("new_year"))
        if new_year < 1900 or new_year > 2020 or new_artist == "" or new_album == "" or new_genre == "" or new_year == "":
            raise ValueError
        if not album.is_valid(new_artist, new_album, new_genre, new_year):
            raise AttributeError
    except ValueError:
        result = HTTPError(406, "Проверьте введенные данные. Все поля должны быть заполнены, поле Year должно быть в диапазоне от 1900 до 2020 включительно.")
    except AttributeError:
        result = HTTPError(409, "Похоже, что данный альбом уже есть в базе")
    # если проверка прошла, то запись в базу данных
    else:
        album.add_record(new_artist, new_album, new_genre, new_year)
        result = f"New record: Artist - '{new_artist}', Album - '{new_album}', Genre - '{new_genre}', Year - '{new_year}'" + "<br><a href='http://localhost:8080/help'>Помощь</a>"
        result += "<br><a href='http://localhost:8080/new'>Назад</a>"
    return result

@route("/path", method="POST")
@route("/path/", method="POST")
def shoose_db():
    '''
    записывает путь к файлу базы данных для использования его вместо пути по умолчанию
    '''
    _path = request.forms.get("path")
    head, tail = os.path.split(_path)
    name, ext = os.path.splitext(tail)
    if os.path.isfile(_path) and ext == ".sqlite3":
        result = f"выбран файл {_path}"
        album.db_path = "sqlite:///" + _path
    else:
        result = "Что-то пошло не так. Проверьте введенный путь"
    result += "<br><a href='http://localhost:8080/help'>Назад</a>"
    return result

@route("/new")
@route("/new/")
def new_record():
    '''
    Страница с формой для добавления новой записи в базу данных
    '''
    return '''
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
</head>
<body>
    <p>Введите данные:</p>
    <form action="/albums" method="post" enctype="multipart/form-data">
  Artist: <input type="text" name="new_artist" />
  Album: <input type="text" name="new_album"/>
  Genre: <input type="text" name="new_genre"/>
  Year: <input type="text" name="new_year"/>
  <input type="submit" value="Add" />
  <br><a href='http://localhost:8080/artists'>Исполнители</a>
  <br><a href="http://localhost:8080/help">Помощь</a>
</form>
</body>
</html>
'''


@route("/help")
@route("/help/")
def help():
    '''
    Страница помощи
    '''
    return '''
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
</head>
<body>
    <p>/help - помощь (эта страница)</p>
    <p>/new - <a href="http://localhost:8080/new">добавление</a> новой записи в базу данных через форму</p>
    <p>/artists - <a href="http://localhost:8080/artists">список исполнителей</a>, чьи альбомы есть в базе</p>
    <p>/albums/&#60;artist&#62; - список альбомов исполнителя &#60;artist&#62;</p>
    <p>Для отправки запроса через терминал используйте следующий формат:
    http -f POST http://localhost:8080/albums new_artist="New Artist" new_genre="Rock" new_album="Super" new_year="1990"</p>
    <br>
    <p>Выбрать файл базы данных</p>
    <form action="/path" method="post" enctype="multipart/form-data">
    Укажите полный путь к файлу базы данных <br>
    <input type="text" name="path" style="width: 300px;"/>
    <input type="submit" value="Выбрать" />
</form>
</body>
</html>
    '''

@route("/artists")
@route("/artists/")
def artists():
    '''
    Выводит список исполнителей, альбомы которых есть в базе
    '''
    artists_list = album.get_artists_list()
    if not artists_list:
        message = "Исполнители не найдены. Похоже база пуста."
        result = HTTPError(404, message)
    else:
        result = "Список исполнителей, альбомы которых есть в базе:<br>"
        result += "\n".join(f"<li><a href='http://localhost:8080/albums/{name}'>{name}</a></li>" for name in artists_list)
        result = "<ul>" + result + "</ul>" + "<br><a href='http://localhost:8080/help'>Помощь</a>"
    return result

if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)