import json
import logging

from twisted.internet import defer
from klein import Klein

from service import utils, get_summary, config, insert_from_moex

app = Klein()
logging.basicConfig(format='%(asctime)-15s %(name)-15s - %(levelname)-7s : %(message)s', level=logging.DEBUG)

methods = {
    'insert_from_moex': insert_from_moex.run,
    'get_summary': get_summary.run
}


@app.route('/', methods=['POST'])
@app.route('/jsonrpc2', methods=['POST'])
@defer.inlineCallbacks
def jsonrpc2(request):
    request.setHeader('Content-Type', 'application/json')
    req = json.loads(request.content.read().decode('utf-8'))
    ver = req.get('jsonrpc')
    method = req.get('method')
    par = req.get('params')
    id_ = req.get('id')
    func = methods.get(method)
    logging.info(f'jsonrpc2 id={id_} method={method} params={par}')
    if ver != '2.0':
        response = make_response(id_, error={'code': 101, 'message': f'version JSON-RPC not supported'})
    elif id_ is None:
        response = make_response(id_, error={'code': 102, 'message': f'id must not be empty'})
    elif func is None:
        response = make_response(id_, error={'code': 104, 'message': f'method "{method}" not defined'})
    else:
        response = yield jsonrpc2_call(func, par, id_)
    defer.returnValue(json.dumps(response, default=utils.json_serial))


@defer.inlineCallbacks
def jsonrpc2_call(func, par, id_):
    try:
        result = yield func(par)
        if result is not None:
            return make_response(id_, result=result)
        else:
            str_err = 'Invalid parameters or Time out'
            logging.error(str_err)
            return make_response(id_, error={'code': 105, 'message': str_err})
    except Exception as err:
        str_err = str(err).replace('\n', ' ')
        logging.error(str_err)
        return make_response(id_, error={'code': 103, 'message': str_err})


def make_response(id_, result=None, error=None):
    if result is not None:
        return {'jsonrpc': '2.0', 'result': result, 'id': id_}
    elif error is not None:
        return {'jsonrpc': '2.0', 'error': error, 'id': id_}


@app.route('/<restname>/<method>', methods=['POST'])
@defer.inlineCallbacks
def call_method(request, restname, method):
    request.setHeader('Content-Type', 'application/json')
    rest_methods = config.get(restname, [])
    if method not in rest_methods:
        response = {'code': 405, 'message': f'method "{method}" not allowed'}
    else:
        func = methods.get(method)
        if func is not None:
            par = json.loads(request.content.read().decode('utf-8'))
            response = yield basic_call(func, par)
        else:
            response = {'code': 104, 'message': f'method "{method}" not defined'}
    defer.returnValue(json.dumps(response, default=utils.json_serial))


@defer.inlineCallbacks
def basic_call(func, par):
    try:
        result = yield func(par)
        if result is not None:
            return result
        else:
            str_err = 'Invalid parameters or Time out'
            logging.error(str_err)
            return {'code': 105, 'message': str_err}
    except Exception as err:
        str_err = str(err).replace('\n', ' ')
        logging.error(str_err)
        return {'code': 103, 'message': str_err}
