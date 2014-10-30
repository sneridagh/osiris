import json


def legacy_oauth_factory(handler, registry):
    def legacy_oauth_tween(request):
            has_user_id = 'user_id' in request.params
            has_client_id = 'client_id' in request.params
            has_oauth_token = 'oauth_token' in request.params
            is_legacy_request = has_client_id or has_oauth_token or has_user_id

            if has_oauth_token:
                request.body = request.body.replace('oauth_token', 'access_token')

            if has_user_id:
                request.body = request.body.replace('user_id', 'username')

            response = handler(request)

            if '/token' in request.url and is_legacy_request:
                body = json.loads(response.body)
                body['oauth_token'] = body['access_token']
                body['fresh'] = False
                del body['access_token']
                del body['token_type']
                del body['expires_in']
                response.body = json.dumps(body)
            return response

    return legacy_oauth_tween
