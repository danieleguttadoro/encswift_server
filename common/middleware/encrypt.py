from swift import gettext_ as _
import md5

from swift.common.swob import Request,Response, HTTPServerError, wsgify
from swift.common.utils import get_logger, generate_trans_id
from swift.common.wsgi import WSGIContext
from swift.proxy.controllers.container import ContainerController
from swift.proxy.controllers.base import get_container_info

from key_manager import *

class encrypt(WSGIContext):

   def __init__(self,app, conf):
        self.app = app
        self.conf = conf
   @wsgify
   def __call__(self, req):
        
        resp = req.get_response(self.app)
        env = req.environ
        username = env.get('HTTP_X_USER_NAME',None)
        
        if req.method == "GET" and username!= 'ceilometer' and username != None:               
            dek = req.environ.get('swift_crypto_fetch_key',None)       
            if dek != None:
                if dek == "NotAuthorized":
                    #User not authorized to access the container
                    return Response(request=req, status=401, content_type="text/plain")
                #Encrypt object
                resp.body = encrypt_msg(str(resp.body),dek) 
                resp.headers['Etag'] = md5.new(resp.body).hexdigest()
                resp.content_length = len(resp.body)  
        return resp
         

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def except_filter(app):
        return encrypt(app,conf)
    return except_filter
