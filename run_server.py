import logging

import os
from webapp import app

if os.environ.get('FLASK_ENV') == 'PRODUCTION':
    logging_level = logging.WARN
else:
    logging_level = logging.DEBUG

logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO if logging_level == logging.DEBUG else logging.WARN)  # werkzeug is too blabbing
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO if logging_level == logging.DEBUG else logging.WARN)

if __name__ == '__main__':
    extra_dirs = ['webapp/static/css', 'webapp/static/img', 'webapp/static/js', 'webapp/templates', ]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    app.run(host='0.0.0.0',
            port=12080,
            debug=logging_level == logging.DEBUG,
            threaded=True,
            extra_files=extra_files)
