from flask import Flask
from flask import jsonify
from flask import request

from src.adapters import orm
from src.domain import model
from src.service_layer import services
from src.service_layer import unit_of_work

app = Flask(__name__)
orm.start_mappers()


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"batchref": batchref}), 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        request.json["eta"],
        unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return "OK", 201


if __name__ == "__main__":
    app.run()
