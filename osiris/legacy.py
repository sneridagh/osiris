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

            if is_legacy_request:
                try:
                    body = json.loads(response.body)
                except:
                    pass
                else:
                    body['oauth_token'] = body.pop('access_token')
                    body['fresh'] = False
                    body.pop('token_type')
                    body.pop('expires_in')
                    response.body = json.dumps(body)
            return response

    return legacy_oauth_tween
