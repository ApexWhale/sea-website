import os
bind = '0.0.0.0:' + os.environ.get('PORT', '8080')
workers = 2
threads = 4
timeout = 45
accesslog = None  # OAuth callbacks contain codes: never log request URLs.
errorlog = '-'
capture_output = False
