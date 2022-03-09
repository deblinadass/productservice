import re
import jwt
import requests
from rest_framework.authentication import BaseAuthentication
from hstproductservice.exceptionhandler.hstexceptionhandler import hst_custom_validation
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from hstproductservice.hstproductserviceconfig import JWT_KEYWORD, JWT_TOKEN_PREFIX, URL_LOGIN_SERVICE

class HST_Backend_Token_Filter(BaseAuthentication):

    user_role_url_cache = dict()
        
    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', None)
        token = self.__get_token(header)
        if token:
            try:
                decodedtoken = jwt.decode(token, JWT_KEYWORD, algorithms=['HS256'])
            except jwt.ExpiredSignature:
                raise hst_custom_validation('Token Expired', status_code = HTTP_401_UNAUTHORIZED)
            except jwt.InvalidSignatureError:
                raise hst_custom_validation('Invalid Token', status_code = HTTP_403_FORBIDDEN)
            self._is_user_authorised(request, decodedtoken.get('role'))
            return None
        else:
            raise hst_custom_validation('Invalid Token', status_code = HTTP_403_FORBIDDEN)
    
    def __get_token(self, header):
        bearer, _, token = header.partition(' ')
        if bearer != JWT_TOKEN_PREFIX:
            raise ValueError('Invalid token')

        return token
        
    def _is_user_authorised(self, request, userrole):
        url_list = []
        request_URL = re.search('/(.+?)/(.+?)/', request.path).group(2)
        if  str(userrole) in HST_Backend_Token_Filter.user_role_url_cache:
            url_list = HST_Backend_Token_Filter.user_role_url_cache[str(userrole)]
        else:
            headers = {'Content-type':'application/json', 'Accept':'application/json', 'Authorization': request.META.get('HTTP_AUTHORIZATION', None)}
            result = requests.get(URL_LOGIN_SERVICE + 'getauthorisationsurls/' + str(userrole) + '/productservice/', headers=headers)
            for url in result.json():
                if url['taburls']:
                    url_list = url_list + url['taburls']
            HST_Backend_Token_Filter.user_role_url_cache[str(userrole)] = url_list
        if str(request_URL) not in url_list:
            raise hst_custom_validation('Unauthorised', status_code = HTTP_403_FORBIDDEN)