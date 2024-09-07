from adapters import orm
from adapters import repository
from config import db_config as app_config
from domain import model
from flask import Flask
from flask import jsonify
from flask import request
from service_layer import services
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
orm.start_mappers()

get_session = sessionmaker(bind=create_engine(app_config.get_postgres_uri()))


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    batches = repository.SqlAlchemyRepository(session).list()
    line = model.OrderLine(
        request.json["orderid"], request.json["sku"], request.json["qty"]
    )
    try:
        batchref = services.allocate(line, batches, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    session.commit()
    return jsonify({"batchref": batchref}), 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        request.json["eta"],
        repo,
        session,
    )
    return "OK", 201


if __name__ == "__main__":
    app.run()
