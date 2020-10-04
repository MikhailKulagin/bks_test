from service import utils
from db import app_db

import traceback
import logging
from twisted.internet import defer, threads

logging.basicConfig(format='%(asctime)-15s %(name)-15s - %(levelname)-7s : %(message)s', level=logging.DEBUG)


class SummaryIdxs():
    def __init__(self):
        # Ответ rest-а. Все инструменты с котировками и изменениями в %
        self.idxs_percent_list = []
        # индексы по инструментам
        self.instrument_idxs_dict = {}

    def add_instrument_value(self, instrument, date_idx, value):
        if self.instrument_idxs_dict.get(instrument):
            if not self.instrument_idxs_dict[instrument].get(date_idx):
                self.instrument_idxs_dict[instrument][date_idx] = value
        else:
            self.instrument_idxs_dict[instrument] = {date_idx: value}

    def prev_idx_value(self, instrument, date_idx):
        instrument_dates = [utils.Ymd_to_date(i) for i in self.instrument_idxs_dict[instrument].keys()]
        instrument_dates.sort()
        last_date = instrument_dates.index(utils.Ymd_to_date(date_idx))
        if len(instrument_dates) > 1:
            prev_date = instrument_dates[last_date-1]
            prev_value = self.instrument_idxs_dict[instrument][utils.to_str(prev_date.date())]
            return prev_value


@defer.inlineCallbacks
def run(params: dict):
    try:

        summary_idxs = SummaryIdxs()

        res_db = yield threads.deferToThread(app_db.get)
        for idx in res_db:

            instrument = idx['boards']+idx['securities']

            summary_idxs.add_instrument_value(instrument, idx['date_idx'], idx['value'])

            prev_value = summary_idxs.prev_idx_value(instrument, idx['date_idx'])
            if prev_value:
                idx.update({'pip': utils.get_change(idx['value'], prev_value)})
            else:
                idx.update({'pip': None})

            summary_idxs.idxs_percent_list.append(idx)

        logging.info(f'idxs_percent_list res {summary_idxs.idxs_percent_list}')
        return summary_idxs.idxs_percent_list

    except Exception as e:
        logging.error(f'get_from_db.run: {e}')
        logging.error(traceback.print_exc())
