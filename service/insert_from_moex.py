from service import utils, config, moex_rest
from db import app_db

import traceback
import logging
from twisted.internet import defer, threads

logging.basicConfig(format='%(asctime)-15s %(name)-15s - %(levelname)-7s : %(message)s', level=logging.DEBUG)


def convert_parameters(params: dict) -> dict:
    try:
        return {
            "securities": utils.to_str(params.get("securities")),
            "date_from": utils.to_str(params.get("date_from")),
            "date_to": utils.to_str(params.get("date_to")),
            "boards": utils.to_str(params.get("boards"))
        }
    except Exception as e:
        logging.error(f'convert_parameters: {e}')
        logging.error(traceback.print_exc())


@defer.inlineCallbacks
def run(params: dict):
    try:
        prm = convert_parameters(params)

        idxs_list = []

        date_from = utils.Ymd_to_date(prm['date_from'])
        date_to = utils.Ymd_to_date(prm['date_to'])

        if date_from and date_to:
            res_moex_rest = yield threads.deferToThread(moex_rest.get_moex_data,
                                                        config.moex_url, 'stock', 'index', prm['boards'],
                                                        prm['securities'], prm['date_from'], prm['date_to'])

            for idx in res_moex_rest:

                idx_dict = {'boards': prm['boards'],
                            'securities': prm['securities'],
                            'value': float(idx[5]),
                            'date_idx': utils.Ymd_to_date(idx[2]),
                            }

                idxs_list.append(idx_dict)

                # добавляем котировку в бд
                yield threads.deferToThread(app_db.add, idx_dict)

            for idx in idxs_list:
                idx['date_idx'] = utils.to_str(idx['date_idx'].date())

            logging.info(f'insert_from_moex res {idxs_list}')
            return idxs_list

    except Exception as e:
        logging.error(f'insert_from_moex.run: {e}')
        logging.error(traceback.print_exc())
