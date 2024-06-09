from flask import Flask, request, jsonify
import repository, model

app = Flask(__name__)


@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    return jsonify(data)


@flask.route.gubbins
def allocate_endpoint():
    batches = repository.SqlAlchemyRepository(session=session).list()
    line = [model.OrderLine(
        data['orderid'],
        data['sku'],
        data['qty'],
    ) for data in request.get_json()['lines']]
    model.allocate(line, batches)
    session.commit()
    return 201


if __name__ == '__main__':
    app.run()
