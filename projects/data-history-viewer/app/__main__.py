#!/usr/bin/env python3

import connexion
from app.encoder import JSONEncoder

# NOTE: turning on connexion.App debug causes Docker deploy to not work due to some app/ (circular?) dependency
if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/', debug=False, swagger_ui=True)
    app.app.json_encoder = JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Manage AWS Athena historical data queries.'})
    app.run(port=8080)
