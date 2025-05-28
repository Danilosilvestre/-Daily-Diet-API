from flask import Flask, request, jsonify
from datetime import datetime, timezone
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models.meal import Meal

import bcrypt
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

# view login
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
       #login
       user = User.query.filter_by(username=username).first()
       
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):

        # Autenticar o usuário
           login_user(user)
           print(current_user.is_authenticated)
           return jsonify({"message": "Autenticação realizada com sucesso!"})
    
    return jsonify({"message": " Credenciais incorretas"}), 400

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})

# Criar usuário
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if username and password and email:
        # Cria um novo usuário
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = User(username=username, email=email, password=hashed_password.decode("utf-8"), role="user")

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Usuário criado com sucesso!"})
    return jsonify({"message": "Dados inválidos"}), 400
    
@app.route("/users/<int:user_id>/meals", methods=["POST"])
@login_required
def create_meal(user_id):
    data = request.get_json()

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Usuário não encontrado!"}), 404
    
    if current_user.role != "admin" and current_user.id != user_id:
        return jsonify({"message": "Você não tem permissão para criar refeições para outros usuários."}), 403
    
    meal = Meal(
    name = data.get("name"),
    description = data.get("description"),
    date_time=datetime.fromisoformat(data.get("date_time")) if data.get("date_time") else datetime.now(timezone.utc),
    is_on_diet = data.get("is_on_diet", False),
    user_id = user.id

    )

    db.session.add(meal)
    db.session.commit()
    return jsonify({
        "message": "Refeição cadastrada com sucesso!",
        "meal": {
            "id": meal.id,
            "name": meal.name,
            "description": meal.description,
            "date_time": meal.date_time.isoformat(),
            "is_on_diet": meal.is_on_diet,
            "user_id": meal.user_id
        }
    })

@app.route("/meals/<string:meal_id>", methods=["GET"])
@login_required
def read_meals(meal_id):
    meal = Meal.query.get(meal_id)
    if meal:
        return jsonify({
            "message": "Refeição encontrada com sucesso!",
            "meal": {
                "id": meal.id,
                "name": meal.name,
                "description": meal.description,
                "date_time": meal.date_time.isoformat(),
                "is_on_diet": meal.is_on_diet
            }
        })
    return jsonify({"message": "Refeição não encontrada!"}), 404

@app.route("/meals/<string:meal_id>", methods=["PUT"])
@login_required
def update_meal(meal_id):
    data = request.get_json()
    meal = Meal.query.get(meal_id)
 
    if current_user.role != "admin" and current_user.id != meal.user_id:
        return jsonify({"message": "Você não tem permissão para atualizar refeições para outros usuários."}), 403


    if not meal:
        return jsonify({"message": "Refeição não encontrada!"}), 404
    if "name" in data:
        meal.name = data["name"]
    if "description" in data:
        meal.description = data["description"]
    if "date_time" in data:
        meal.date_time = datetime.fromisoformat(data["date_time"]) if data["date_time"] else datetime.now(timezone.utc)
    if "is_on_diet" in data:
        meal.is_on_diet = data["is_on_diet"]
    db.session.commit()

    return jsonify({"message": "Refeição atualizada com sucesso!",})    
        
@app.route("/users/<int:user_id>/meals", methods=["GET"])
@login_required
def list_meals_by_user(user_id):

    user = User.query.get(user_id)

    if current_user.role != "admin" and current_user.id != user_id:
        return jsonify({"message": "Você não tem permissão para listar as refeições de outros usuários."}), 403

    if not user:
        return jsonify({"message": "Usuário não encontrado!"}), 404
    
    meals = Meal.query.filter_by(user_id=user.id).all()
    meals_list = []
    for meal in meals:
        meals_list.append({
            "id": meal.id,
            "name": meal.name,
            "description": meal.description,
            "date_time": meal.date_time.isoformat(),
            "is_on_diet": meal.is_on_diet
        })
    return jsonify({"message": f"Refeições encontradas para o usuário {user.username}!", "meals": meals_list})
    
@app.route("/meals/<string:meal_id>", methods=["DELETE"])
@login_required
def delete_meal(meal_id):
   
    meal = Meal.query.get(meal_id)

    if current_user.role != "admin" and current_user.id != meal.user_id:

        return jsonify({"message": "Você não tem permissão para deletar esta refeição."}), 403 

    if not meal:
        return jsonify({"message": "Refeição não encontrada!"}), 404
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": "Refeição deletada com sucesso!"})

@app.route("/users/<string:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
   
    user = User.query.get(user_id)

    if current_user.role != "admin":
        return jsonify({f"message": "Você não tem permissão para deletar este usuário."}), 403 

    if not user:
        return jsonify({"message": "Usuário não encontrado!"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuário deletado com sucesso!"})

if __name__ == "__main__":
    app.run(debug=True)
