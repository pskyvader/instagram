from .base import base

# from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model

# from app.models.modulo import modulo as modulo_model
# from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model
from app.models.configuracion import configuracion as configuracion_model

from app.models.igusuario import igusuario as igusuario_model
from app.models.igaccounts import igaccounts as igaccounts_model
from app.models.ighashtag import ighashtag as ighashtag_model
from app.models.igtotal import igtotal as igtotal_model

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


class instagram_bot:
    bot = None
    error_mensaje = ""

    def __init__(self):
        self.get_bot()
        respuesta = self.login()
        if not respuesta["exito"]:
            bot = None
            self.error_mensaje = respuesta["mensaje"]

    def user(self, id):
        respuesta = {"exito": False, "mensaje": ""}
        if self.bot == None:
            respuesta["mensaje"] = self.error_mensaje
            return respuesta
        else:
            bot = self.bot
            respuesta["exito"] = True
        if respuesta["exito"]:
            if id.isdigit():
                user = bot.get_user_info(id)
            else:
                user_id = bot.get_user_id_from_username(id)
                user = bot.get_user_info(user_id)

            if "pk" not in user:
                respuesta["exito"] = False
                respuesta["mensaje"] = "No se encontro un usuario valido"
            else:
                respuesta["exito"] = True
                respuesta["mensaje"] = "Usuario: " + user["full_name"]

        return respuesta

    def update(self):
        respuesta = {"exito": False, "mensaje": ""}

        if self.bot == None:
            respuesta["mensaje"] = self.error_mensaje
            return respuesta
        else:
            bot = self.bot
            respuesta["exito"] = True
        if respuesta["exito"]:
            key = "get"
            turn_remain = int(
                configuracion_model.getByVariable("turn_remain_" + key, "0")
            )
            if turn_remain > 0:
                bot.console_print("Bloqueado por " + str(turn_remain) + " turnos")
                configuracion_model.setByVariable(
                    "turn_remain_" + key, str(turn_remain - 1), False
                )
                return respuesta

        if respuesta["exito"]:
            bot.console_print("Adquiriendo usuarios", progress=5)
            users_total = igaccounts_model.getAll()
            bot.console_print("Adquiriendo seguidores", progress=10)
            followers = bot.followers.copy()
            if len(followers) == 0:
                respuesta["exito"] = False
                respuesta["mensaje"] = "Error al obtener seguidores"
            else:
                bot.console_print(
                    "total seguidores:" + str(len(followers)), progress=10
                )
        if respuesta["exito"]:
            bot.console_print("Adquiriendo siguiendo", progress=15)
            following = bot.following.copy()
            if len(following) == 0:
                respuesta["exito"] = False
                respuesta["mensaje"] = "Error al obtener seguidos"
            else:
                bot.console_print("total siguiendo:" + str(len(following)), progress=10)

        if respuesta["exito"]:
            c_time = functions.current_time("%Y-%m-%d")
            start_follow = 0
            stop_follow = 0

            bot.console_print("Actualizando Usuarios actuales", progress=20)
            count_users = len(users_total)
            for k, u in enumerate(users_total):
                k += 1
                progress = 19 + ((k / count_users) * 40)
                msg = u["username"] + " - " + str(k) + "/" + str(count_users)

                if u["profile_pic_url"] == "":
                    bot.console_print("Actualizando datos de " + msg, progress=progress)
                    u = bot.get_user_info(u["pk"], False)

                if str(u["pk"]) in followers:
                    followers.remove(str(u["pk"]))
                    if not u["follower"]:
                        start_follow += 1
                        bot.console_print(
                            "Actualizando seguidor " + msg, progress=progress
                        )
                        igaccounts_model.update({"id": u[0], "follower": True}, False)
                else:
                    if u["follower"]:
                        stop_follow += 1
                        bot.console_print(
                            "Actualizando No seguidor " + msg, progress=progress
                        )
                        igaccounts_model.update({"id": u[0], "follower": False}, False)

                if str(u["pk"]) in following:
                    following.remove(str(u["pk"]))
                    if not u["following"]:
                        bot.console_print(
                            "Actualizando siguiendo " + msg, progress=progress
                        )
                        igaccounts_model.update({"id": u[0], "following": True}, False)
                else:
                    if u["following"]:
                        bot.console_print(
                            "Actualizando No siguiendo " + msg, progress=progress
                        )
                        igaccounts_model.update({"id": u[0], "following": False}, False)

                if not respuesta["exito"]:
                    break

        if respuesta["exito"]:
            bot.console_print("Ingresando nuevos seguidores", progress=60)
            count_followers = len(followers)
            for k, f in enumerate(followers):
                k = k + 1
                progress = 59 + ((k / count_followers) * 20)
                u = bot.get_user_info(f)
                if not u:
                    if bot.api.fatal_error:
                        respuesta["exito"] = False
                        break
                else:
                    start_follow += 1
                    bot.console_print(
                        "agregando "
                        + u["username"]
                        + " - "
                        + str(k)
                        + "/"
                        + str(count_followers),
                        progress=progress,
                    )
                    if not u["follower"]:
                        igaccounts_model.update({"id": u[0], "follower": True}, False)
                    if not u["following"] and f in following:
                        igaccounts_model.update({"id": u[0], "following": True}, False)

        if respuesta["exito"]:
            bot.console_print("Ingresando nuevos siguiendo", progress=80)
            count_following = len(following)
            for k, f in enumerate(following):
                k = k + 1
                progress = 79 + ((k / count_following) * 20)
                u = bot.get_user_info(f)
                if not u:
                    if bot.api.fatal_error:
                        respuesta["exito"] = False
                        break
                else:
                    bot.console_print(
                        "agregando "
                        + u["username"]
                        + " - "
                        + str(k)
                        + "/"
                        + str(count_following),
                        progress=progress,
                    )
                    if not u["following"]:
                        igaccounts_model.update({"id": u[0], "following": True}, False)
                    if not u["follower"] and f in followers:
                        igaccounts_model.update({"id": u[0], "follower": True}, False)

        if respuesta["exito"]:
            bot.console_print("Completado", progress=100)
        else:
            bot.console_print("Completado con errores", progress=100)

        igtotal_model.set_total("start_follow", c_time, start_follow)
        igtotal_model.set_total("stop_follow", c_time, stop_follow)
        return respuesta

    def follow(self, accion):
        from math import log10

        respuesta = {"exito": False, "mensaje": ""}

        if self.bot == None:
            respuesta["mensaje"] = self.error_mensaje
            return respuesta
        else:
            bot = self.bot
            respuesta["exito"] = True

        if respuesta["exito"]:
            key = "follow"
            turn_remain = int(
                configuracion_model.getByVariable("turn_remain_" + key, "0")
            )
            if turn_remain > 0:
                bot.console_print("Bloqueado por " + str(turn_remain) + " turnos")
                configuracion_model.setByVariable(
                    "turn_remain_" + key, str(turn_remain - 1), False
                )
                return respuesta

        if respuesta["exito"]:
            if accion == "hashtag":
                hashtags = ighashtag_model.getAll({"estado": True})
                for h in hashtags:
                    h["followers"] = igaccounts_model.getAll(
                        {"hashtag": h["hashtag"]}, select="total"
                    )

                hashtags = sorted(hashtags, key=lambda i: i["followers"])

                hashtags_total = len(hashtags)
                proporcion = 100 / hashtags_total
                while not bot.reached_limit("follows") and not bot.api.fatal_error:
                    for k, hashtag in enumerate(hashtags):
                        base = (k / hashtags_total) * 100
                        h = hashtag["hashtag"]
                        if not bot.reached_limit("follows"):
                            bot.console_print("Siguiendo usuarios con hashtag: " + h)
                            users = bot.get_hashtag_users(h)
                            # Calculo para emparejar la cantidad de usuarios por hashtag, minimo 5
                            # curva logaritmica inversa (k+1=1,x=50) (k+1=20,x=10.421) (k+1=50,x=5.936)
                            this_hashtag = (70 / (log10(k + 1) + 1)) - 20
                            this_hashtag = 5 if this_hashtag < 5 else int(this_hashtag)
                            users = users[:this_hashtag]
                            bot.follow_users(users, base, proporcion, h)
                            if bot.api.fatal_error:
                                respuesta["exito"] = False
                                respuesta["mensaje"] = "Error Fatal"
                                break
                        else:
                            respuesta["exito"] = False
                            respuesta["mensaje"] = "Limite alcanzado"
                            break
            bot.console_print("Completado", progress=100)
        return respuesta

    def unfollow(self, accion):
        respuesta = {"exito": False, "mensaje": ""}
        if self.bot == None:
            respuesta["mensaje"] = self.error_mensaje
            return respuesta
        else:
            bot = self.bot
            respuesta["exito"] = True

        if respuesta["exito"]:
            key = "unfollow"
            turn_remain = int(
                configuracion_model.getByVariable("turn_remain_" + key, "0")
            )
            if turn_remain > 0:
                bot.console_print("Bloqueado por " + str(turn_remain) + " turnos")
                configuracion_model.setByVariable(
                    "turn_remain_" + key, str(turn_remain - 1), False
                )
                return respuesta

        if respuesta["exito"] and bot.reached_limit("unfollows"):
            bot.console_print("Limite alcanzado por hoy.")
            respuesta["exito"] = False
            respuesta["mensaje"] = "Limite alcanzado"

        if respuesta["exito"]:
            if accion == "nonfollower":
                days_unfollow = int(
                    configuracion_model.getByVariable("days_unfollow", 5)
                )
                fecha_limite = (
                    datetime.datetime.now() - datetime.timedelta(days=days_unfollow)
                ).strftime("%Y-%m-%d")
                user_list = igaccounts_model.getAll(
                    {
                        "following": True,
                        "follower": False,
                        "favorito": False,
                        "DATE(fecha) <": fecha_limite,
                    },
                    select="pk",
                )
            elif accion == "old":
                days_unfollow = int(
                    configuracion_model.getByVariable("days_unfollow_old", 20)
                )
                fecha_limite = (
                    datetime.datetime.now() - datetime.timedelta(days=days_unfollow)
                ).strftime("%Y-%m-%d")
                user_list = igaccounts_model.getAll(
                    {
                        "following": True,
                        "favorito": False,
                        "DATE(fecha) <": fecha_limite,
                    },
                    select="pk",
                )

            user_list = list(f["pk"] for f in user_list)
            total_user_list = len(user_list)

            for k, user_id in enumerate(user_list):
                if bot.reached_limit("unfollows"):
                    bot.console_print("Limite alcanzado por hoy.")
                    respuesta["exito"] = False
                    respuesta["mensaje"] = "Limite alcanzado"
                    break
                progress = (k / total_user_list) * 100
                respuesta["exito"] = bot.unfollow(user_id, progress)
                if not respuesta["exito"]:
                    if bot.api.fatal_error:
                        respuesta["mensaje"] = "Error Fatal"
                        break

            bot.console_print("Completado", progress=100)
        return respuesta

    def delete(self):
        respuesta = {"exito": False, "mensaje": ""}
        if self.bot == None:
            respuesta["mensaje"] = self.error_mensaje
            return respuesta
        else:
            bot = self.bot
            respuesta["exito"] = True

        if respuesta["exito"]:
            hashtag = ighashtag_model.getAll({"estado": True})
            hashtag = [h["hashtag"] for h in hashtag]
            f = igaccounts_model.getAll(
                {"hashtag!": ""}, {"group": "hashtag"}, "count(pk) as total,hashtag"
            )

            delete_hashtag = []
            for u in f:
                if u["hashtag"] not in hashtag and u["total"] > 0:
                    delete_hashtag.append(u["hashtag"])

            for d in delete_hashtag:
                user = igaccounts_model.getAll({"hashtag": d})
                for u in user:
                    igaccounts_model.update({"id": u[0], "hashtag": ""}, False)

            users = igaccounts_model.getAll(
                {
                    "follower": False,
                    "following": False,
                    "favorito": False,
                    "hashtag": "",
                }
            )

            for k, u in enumerate(users):
                show_message = True if (k % 100) == 0 else False
                bot.unfollowed_file.append(u["pk"], show_message=show_message)
                igaccounts_model.delete(u[0], False)

            respuesta["exito"] = True
            respuesta["mensaje"] = "Limpieza completada"
        return respuesta

    def update_hashtag(self):
        from app.controllers.back.themes.paper.home import home
        import random

        respuesta = {"exito": False, "mensaje": ""}
        limit_hashtag = int(configuracion_model.getByVariable("limit_hashtag", "10"))
        minimum_hashtag = int(configuracion_model.getByVariable("minimum_hashtag", "1500"))

        h = home()
        hashtag_list = h.get_hashtag_users(True)
        # hashtag_list: lista de hashtags agrupados por atributo (siguiendo,seguidos,quitados,eficiencia,total)
        # y el menor numero para comparar
        # ordenados de mayor a menor cantidad de usuarios con dicho hashtag
        if len(hashtag_list["total"]) >= int(limit_hashtag * 1.5):
            # desactivar el peor hashtag. conservar para evitar agregarlo nuevamente
            # si hay 15 elementos, se comparan los primeros 10
            menor_list = list(hashtag_list["total"].values())[limit_hashtag - 1]
            if menor_list > minimum_hashtag:
                hashtag_eficiencia = {
                    k: hashtag_list["eficiencia2"][k]
                    for k in list(hashtag_list["eficiencia2"])[:limit_hashtag]
                }
                hashtag_menor = min(
                    hashtag_eficiencia, key=dict(hashtag_eficiencia).get
                )
                query = ighashtag_model.getByHashtag(hashtag_menor)
                update_query = {}
                update_query["id"] = query[0]
                update_query["estado"] = False
                update_query["following"] = hashtag_list["following"][hashtag_menor]
                update_query["follower"] = hashtag_list["followers"][hashtag_menor]
                update_query["removed"] = hashtag_list["removed"][hashtag_menor]
                update_query["eficiencia"] = hashtag_list["eficiencia"][hashtag_menor]
                update_query["eficiencia2"] = hashtag_list["eficiencia2"][hashtag_menor]
                update_query["total"] = hashtag_list["total"][hashtag_menor]
                ighashtag_model.update(update_query, False)
                respuesta["mensaje"] = "Hashtag " + hashtag_menor + " quitado"
            else:
                respuesta[
                    "mensaje"
                ] = "Aun no hay suficientes cuentas siguiendo para evaluar"

            respuesta["exito"] = True

        if respuesta["exito"]:
            hashtag_list = h.get_hashtag_users(True)

        if len(hashtag_list["total"]) < int(limit_hashtag * 1.5):
            # buscar nuevos hashtag e ingresarlos
            if self.bot == None:
                respuesta["mensaje"] += self.error_mensaje
                respuesta["exito"] = False
                return respuesta
            else:
                bot = self.bot
                respuesta["exito"] = True

            if respuesta["exito"]:
                tags = ighashtag_model.getAll()
                if len(tags) > 0 and "hashtag" in tags[0]:
                    tags = set(x["hashtag"] for x in tags)
                    tag_list = set()
                    intento = 0
                    while len(tag_list) <= 0 and intento < len(tags):
                        intento += 1
                        tag = random.choice(list(tags))
                        tag_list = set(bot.get_tags(tag))
                        tag_list = tag_list - tags

                    if len(tag_list) > 0:
                        final_tag = random.choice(list(tag_list))
                        insert_query = {"hashtag": final_tag, "estado": True}
                        ighashtag_model.insert(insert_query, False)
                        respuesta["mensaje"] += (
                            ". Nuevo Hashtag " + final_tag + " agregado"
                        )
                    else:
                        respuesta["exito"] = False
                        respuesta[
                            "mensaje"
                        ] = "No se encontraron nuevos hashtag. agrega manualmente"

                else:
                    respuesta["exito"] = False
                    respuesta["mensaje"] = "Debe haber al menos un hashtag creado"

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
