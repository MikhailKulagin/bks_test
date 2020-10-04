from service import config
import traceback
import logging
import requests
import json

logging.basicConfig(format='%(asctime)-15s %(name)-15s - %(levelname)-7s : %(message)s', level=logging.DEBUG)


def get_moex_data(moex_url, engines, markets, boards, securities, date_from, date_to):
    try:
        count = int(config.moex_try_count)
    except Exception:
        logging.warning(f'run on default try count')
        count = config.default_try
    while count > 0:
        count -= 1
        try:
            res = requests.get(f'{moex_url}'
                               f'/iss/history/engines/{engines}/markets/{markets}/boards/{boards}/securities/{securities}.json?'
                               f'from={date_from}&till={date_to}')
            res_code = res.status_code
            res = res.content
            res_dict = json.loads(res.decode('UTF-8'))
            data = res_dict['history']['data']
            return data

        except Exception as e:
            logging.error(f'error: {e}')
            logging.error(traceback.print_exc())
        # на 5XX ошибках 10 раз повтоярем запрос
        if 599 >= res_code >= 500:
            continue
        else:
            break
