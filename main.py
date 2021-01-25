from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


# Get Cafe from ID
def get_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    return cafe


def refresh_db():
    return db.session.query(Cafe).order_by('name').all()


def convert_dict(db_entry):
    obj_dict = db_entry.__dict__
    del obj_dict['_sa_instance_state']
    return obj_dict


# Delete entry
def delete_entry(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()

@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def random():
    this_cafe = convert_dict(choice(refresh_db()))
    return jsonify(this_cafe)


@app.route("/all")
def all():
    return jsonify(dict([(cafe.id, convert_dict(cafe)) for cafe in refresh_db()]))


@app.route("/search")
def search():
    location = request.args.get('location')
    return jsonify(dict([(cafe.id, convert_dict(cafe)) for cafe in refresh_db() if cafe.location == location]))


## HTTP POST - Create Record
@app.route("/add", methods=['GET', 'POST'])
def add():
    new_cafe = Cafe()
    try:
        for attr in request.args:
            if request.args.get(attr).lower() == "false":
                new_cafe.__setattr__(attr, False)
            elif request.args.get(attr).lower() == "true":

                new_cafe.__setattr__(attr, True)
            else:
                new_cafe.__setattr__(attr, request.args.get(attr))
        db.session.add(new_cafe)
        db.session.commit()
        return '{"response":{"success":"Successfully added Cafe: ' + new_cafe.name + '!"}}'
    except:
        return '{"response":{"error":"Failed to add requested cafe to database"}}'


## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<cafe_id>', methods=['GET', 'PATCH'])
def reprice(cafe_id):
    try:
        cafe = get_cafe(cafe_id)
        cafe.coffee_price = request.args.get('coffee_price')
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    except:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


## HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['GET', 'DELETE'])
def report_closed(cafe_id):
    try:
        if request.args.get('api-key') != "TopSecretAPIKey":
            return jsonify(response={"error": "Incorrect API Key!"}), 404
        else:
            delete_entry(cafe_id)
            return jsonify(response={"success": "Successfully deleted the cafe!"}), 200
    except:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
