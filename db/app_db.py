from service import utils, config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

import logging
logging.basicConfig(format='%(asctime)-15s %(name)-15s - %(levelname)-7s : %(message)s', level=logging.DEBUG)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////tmp/{config.db_name}.db'
db = SQLAlchemy(app)


class Idxs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    boards = db.Column(db.String(50))
    securities = db.Column(db.String(50))
    value = db.Column(db.Float)
    date_idx = db.Column(db.Date)

    def __init__(self, boards, securities, value, date_idx):
        self.boards = boards
        self.securities = securities
        self.value = value
        self.date_idx = date_idx


def add(idx_dict):
    # если в базе нет зсписи, то инсертим
    if not Idxs.query.filter_by(boards=idx_dict['boards'],
                                       securities=idx_dict['securities'],
                                       date_idx=idx_dict['date_idx'].date()).first():
        logging.info(f"insert_idx {idx_dict['boards']}/{idx_dict['securities']}/{idx_dict['date_idx'].date()}")
        new_idx = Idxs(idx_dict['boards'], idx_dict['securities'], idx_dict['value'], idx_dict['date_idx'])
        db.session.add(new_idx)
        db.session.commit()
    # если есть - update
    else:
        logging.info(f"exist_update_idx {idx_dict['boards']}/{idx_dict['securities']}/{idx_dict['date_idx'].date()}")
        Idxs.query.filter_by(boards=idx_dict['boards'],
                                    securities=idx_dict['securities'],
                                    date_idx=idx_dict['date_idx']).update({'value': idx_dict['value']})
        db.session.commit()


def get():
    db_idxs = []
    max_date = db.session.query(func.max(Idxs.date_idx)).first()
    min_date = db.session.query(func.min(Idxs.date_idx)).first()
    for i in Idxs.query.order_by(Idxs.boards,
                                 Idxs.securities,
                                 Idxs.date_idx).all():
        idx = {'boards': i.boards,
               'securities': i.securities,
               'value': i.value,
               'date_idx': utils.to_str(i.date_idx),
               'security_from': utils.to_str(min_date[0]),
               'security_to': utils.to_str(max_date[0])
               }
        db_idxs.append(idx)
    return db_idxs


db.create_all()