from twisted.internet import reactor
from twisted.web.server import Site
import logging
from service import config, rest

logging.basicConfig(format='%(asctime)-15s %(name)-15s - %(levelname)-7s : %(message)s', level=logging.DEBUG)


def process():
    try:
        port = int(config.port)
    except Exception:
        logging.warning(f'run on default port')
        port = config.default_port

    log = logging.getLogger("rest2bks")
    site = Site(rest.app.resource())
    reactor.listenTCP(port, site)
    log.info(f"listen local port {port}")
    reactor.run()
