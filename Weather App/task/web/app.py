from flask import Flask, render_template, request, redirect, flash, get_flashed_messages
import requests
import sys
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random




Base = declarative_base()


class City(Base):
    __tablename__ = "City"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=False, nullable=False)

engine = create_engine('sqlite:///weather.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

connection = engine.connect()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty'


dict_with_weather_info = {}


def get_id():
    return random.randrange(1000000)

def render_cities():
    city_query = request.form['city_name']
    api_key = 'api_key'
    req = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city_query}&units=metric&appid={api_key}')
    r = req.json()
    print(req.status_code)
    if req.status_code == 404:
        flash("The city doesn't exist!")
    else:
            if not session.query(City).filter(City.name == r["name"]).first():
                city_id = get_id()
                session.add(City(id=city_id, name=r["name"]))
                session.commit()
                dict_with_weather_info[city_id] = {
                    "city": r["name"], "degrees": int(r["main"]["temp"]), "state": r["weather"][0]['main'],
                    "id": city_id
                }
            elif session.query(City).filter_by(name=r["name"]).first():
                flash('The city has already been added to the list!')





@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        render_cities()
        return render_template('index.html', cities=dict_with_weather_info)
    if request.method == "GET":
        return render_template('index.html', cities=dict_with_weather_info)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_id(id):
    city_del = session.query(City).filter(City.id == id).first()
    if city_del:
        session.delete(city_del)
        session.commit()
        del dict_with_weather_info[id]
    return redirect('/')




# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(host='0.0.0.0', port=3333)