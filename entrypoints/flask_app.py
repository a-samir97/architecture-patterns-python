from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


import config
import domain.model as model
import adapters.orm as orm
import adapters.repository as repository
import service_layer.services as services

orm.start_mappers()

get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

app = Flask(__name__)


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    session = get_session()
    batches = repository.SqlAlchemyRepository(session).list()
    line = model.OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty']
    )
    try:
        batchref = services.allocate(line, batches, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    session.commit()
    return jsonify({'batchref': batchref}), 201
