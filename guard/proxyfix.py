from werkzeug.contrib.fixers import ProxyFix

def _reverse_proxified(app):
    """
    Configure apache as:
      RequestHeader set X-Script-Name /videos
    """

    def wsgi_call(environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return app(environ, start_response)

    return wsgi_call

"""
'ProxyFix' applied for reading X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Host

'_reverse_proxified' applied for 'X-Script-Name'.
That's required when external request path is different from application server path.
"""
def fix(app):
    return _reverse_proxified(ProxyFix(app))
