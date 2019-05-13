from .base import base

# from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model

# from app.models.modulo import modulo as modulo_model
# from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model
from app.models.configuracion import configuracion as configuracion_model

from app.models.igusuario import igusuario as igusuario_model
from app.models.igaccounts import igaccounts as igaccounts_model
from app.models.ighashtag import ighashtag as ighashtag_model

# from .detalle import detalle as detalle_class
# from .lista import lista as lista_class
from .head import head
from .header import header
from .aside import aside
from .footer import footer

from core.app import app

# from core.database import database
from core.functions import functions

# from core.image import image
from core.socket import socket

import json


from instabot import Bot
import datetime


class instagram_bot():
    bot = None
    error_mensaje=''
    def __init__(self):
        self.get_bot()
        respuesta = self.login()
        if not respuesta['exito']:
            bot=None
            self.error_mensaje=respuesta['mensaje']
        
    def update(self):
        respuesta = {"exito": False, "mensaje": ""}

        if self.bot==None:
            respuesta['mensaje']=self.error_mensaje
            return respuesta
        else:
            bot=self.bot
            respuesta['exito']=True
        
        if respuesta['exito']:
            bot.console_print("Adquiriendo usuarios", progress=5)
            users_total = igaccounts_model.getAll()
            bot.console_print("Adquiriendo seguidores", progress=10)
            followers = bot.followers.copy()
            if len(followers)==0:
                respuesta['exito']=False
                respuesta['mensaje']='Error al obtener seguidores'
            else:
                bot.console_print("total seguidores:"+str(len(followers)), progress=10)
        if respuesta['exito']:
            bot.console_print("Adquiriendo siguiendo", progress=15)
            following = bot.following.copy()
            if len(following)==0:
                respuesta['exito']=False
                respuesta['mensaje']='Error al obtener seguidos'
            else:
                bot.console_print("total siguiendo:"+str(len(following)), progress=10)

        if respuesta['exito']:
            bot.console_print("Actualizando Usuarios actuales", progress=20)
            count_users = len(users_total)
            for k, u in enumerate(users_total):
                igaccounts_model.update_user(u[0],u)
                k = k + 1
                progress = 19 + ((k / count_users) * 40)
                msg=u["username"] + " - " + str(k) + "/" + str(count_users)
                if str(u["pk"]) in followers:
                    followers.remove(str(u["pk"]))
                    if not u["follower"]:
                        bot.console_print( "Actualizando " +msg, progress=progress )
                        igaccounts_model.update({"id": u[0], "follower": True},False)
                else:
                    if u["follower"]:
                        bot.console_print( "Actualizando " +msg, progress=progress )
                        igaccounts_model.update({"id": u[0], "follower": False},False)

                if str(u["pk"]) in following:
                    following.remove(str(u["pk"]))
                    if not u["following"]:
                        bot.console_print( "Actualizando " +msg, progress=progress )
                        igaccounts_model.update({"id": u[0], "following": True},False)
                else:
                    if u["following"]:
                        bot.console_print( "Actualizando " +msg, progress=progress )
                        igaccounts_model.update({"id": u[0], "following": False},False)
                
                if not respuesta['exito']:
                    break


        if respuesta['exito']:
            bot.console_print("Ingresando nuevos seguidores", progress=60)
            count_followers = len(followers)
            for k, f in enumerate(followers):
                k = k + 1
                progress = 59 + ((k / count_followers) * 20)
                u = bot.get_user_info(f)
                if not u:
                    if bot.api.fatal_error:
                        respuesta['exito']=False
                        break
                else:
                    bot.console_print( "agregando " + u["username"] + " - " + str(k) + "/" + str(count_followers), progress=progress )
                    if not u["follower"]:
                        igaccounts_model.update({"id": u[0], "follower": True},False)
                    if not u["following"] and f in following:
                        igaccounts_model.update({"id": u[0], "following": True},False)

        if respuesta['exito']:
            bot.console_print("Ingresando nuevos siguiendo", progress=80)
            count_following = len(following)
            for k, f in enumerate(following):
                k = k + 1
                progress = 79 + ((k / count_following) * 20)
                u = bot.get_user_info(f)
                if not u:
                    if bot.api.fatal_error:
                        respuesta['exito']=False
                        break
                else:
                    bot.console_print( "agregando " + u["username"] + " - " + str(k) + "/" + str(count_following), progress=progress )
                    if not u["following"]:
                        igaccounts_model.update({"id": u[0], "following": True},False)
                    if not u["follower"] and f in followers:
                        igaccounts_model.update({"id": u[0], "follower": True},False)

        if respuesta['exito']:
            bot.console_print("Completado", progress=100)
        else:
            bot.console_print("Completado con errores", progress=100)
        return respuesta




    def follow(self,accion):
        respuesta = {"exito": False, "mensaje": ""}

        if self.bot==None:
            respuesta['mensaje']=self.error_mensaje
            return respuesta
        else:
            bot=self.bot
            respuesta['exito']=True
        
        if respuesta['exito']:
            if accion=='hashtag':
                hashtags = ighashtag_model.getAll({'estado':True})
                hashtags_total=len(hashtags)
                proporcion=100/hashtags_total
                while not bot.reached_limit('follows') and not bot.api.fatal_error:
                    for k,hashtag in enumerate(hashtags):
                        base=(k/hashtags_total)*100
                        h= hashtag['hashtag']
                        if not bot.reached_limit('follows'):
                            bot.console_print("Siguiendo usuarios con hashtag: " + h)
                            users = bot.get_hashtag_users(h)
                            bot.follow_users(users,base,proporcion,h)
                            if bot.api.fatal_error:
                                respuesta['exito']=False
                                respuesta['mensaje']='Error Fatal'
                                break
                        else:
                            respuesta['exito']=False
                            respuesta['mensaje']='Limite alcanzado'
                            break
            bot.console_print("Completado", progress=100)
        return respuesta




    def unfollow(self,accion):
        respuesta = {"exito": False, "mensaje": ""}

        if self.bot==None:
            respuesta['mensaje']=self.error_mensaje
            return respuesta
        else:
            bot=self.bot
            respuesta['exito']=True
        
        if respuesta['exito']:
            if accion=='nonfollower':
                days_unfollow=int(configuracion_model.getByVariable('days_unfollow',5))
                fecha_limite=(datetime.datetime.now() - datetime.timedelta(days=days_unfollow)).strftime("%Y-%m-%d")
                non_followers=igaccounts_model.getAll({'following':True,'follower':False,'favorito':False,'DATE(fecha) <':fecha_limite})
                non_followers=list(f['pk'] for f in non_followers)
                total_non_followers=len(non_followers)

                for k, user_id in enumerate(non_followers):
                    if bot.reached_limit('unfollows'):
                        bot.console_print("Limite alcanzado por hoy.")
                        respuesta['exito']=False
                        respuesta['mensaje']='Limite alcanzado'
                        break
                    progress=(k/total_non_followers)*100
                    respuesta['exito']=bot.unfollow(user_id,progress)
                    if not respuesta['exito']:
                        if bot.api.fatal_error:
                            respuesta['mensaje']='Error Fatal'

                            break
            bot.console_print("Completado", progress=100)
        return respuesta


    def get_bot(self):
        get_var = configuracion_model.getByVariable
        if self.bot == None:
            self.bot = Bot(
                max_likes_per_day=int(get_var("max_likes_per_day", 1000)),
                max_unlikes_per_day=int(get_var("max_unlikes_per_day", 1000)),
                max_follows_per_day=int(get_var("max_follows_per_day", 900)),
                max_unfollows_per_day=int(get_var("max_unfollows_per_day", 900)),
                max_comments_per_day=int(get_var("max_comments_per_day", 100)),
                max_likes_to_like=int(get_var("max_likes_to_like", 100)),
                max_followers_to_follow=int(get_var("max_followers_to_follow", 2000)),
                min_followers_to_follow=int(get_var("min_followers_to_follow", 10)),
                max_following_to_follow=int(get_var("max_following_to_follow", 7500)),
                min_following_to_follow=int(get_var("min_following_to_follow", 10)),
                max_followers_to_following_ratio=int(
                    get_var("max_followers_to_following_ratio", 10)
                ),
                max_following_to_followers_ratio=int(
                    get_var("max_following_to_followers_ratio", 2)
                ),
                min_media_count_to_follow=int(get_var("min_media_count_to_follow", 3)),
                like_delay=float(get_var("like_delay", 0)),
                unlike_delay=float(get_var("unlike_delay", 0)),
                follow_delay=float(get_var("follow_delay", 0)),
                unfollow_delay=float(get_var("unfollow_delay", 0)),
                comment_delay=float(get_var("comment_delay", 0)),
                get_delay=float(get_var("get_delay", 0)),
                like_sleep=float(get_var("like_sleep", 10)),
                unlike_sleep=float(get_var("unlike_sleep", 10)),
                follow_sleep=float(get_var("follow_sleep", 10)),
                unfollow_sleep=float(get_var("unfollow_sleep", 10)),
                comment_sleep=float(get_var("comment_sleep", 10)),
                get_sleep=float(get_var("get_sleep", 10)),
                stop_words=json.loads(
                    get_var(
                        "stop_words",
                        json.dumps(
                            [
                                "order",
                                "shop",
                                "store",
                                "free",
                                "doodleartindonesia",
                                "doodle art indonesia",
                                "fullofdoodleart",
                                "commission",
                                "vector",
                                "karikatur",
                                "jasa",
                                "open",
                            ]
                        ),
                    )
                ),
                blacklist_hashtags=json.loads(
                    get_var(
                        "blacklist_hashtags", json.dumps(["#shop", "#store", "#free"])
                    )
                ),
            )
        return self.bot

    def login(self):
        bot = self.get_bot()
        respuesta = {"exito": False, "mensaje": ""}
        user = igusuario_model.getAll({"estado": True}, {"limit": 1})
        if len(user) != 1:
            respuesta["mensaje"] = "No hay usuario para login"
        else:
            user = user[0]
            if bot.login(
                username=user["usuario"], password=user["password"], use_cookie=False
            ):
                respuesta["exito"] = True
            else:
                respuesta["mensaje"] = "Error en login"
        return respuesta
