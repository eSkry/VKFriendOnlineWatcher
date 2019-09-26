import vk_api
import os


def GetUserOnlineStatus(vk: vk_api.VkApiMethod, id):
    responce = vk.users.get(id = id,fields=['online'])
    print(responce)