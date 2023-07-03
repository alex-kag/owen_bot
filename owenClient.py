import requests

from settings import LOGIN
from settings import PASSWORD


class OwenApi:
    def __init__(self, url):
        self.token = None
        self.url = url
        self.getToken()

    def getToken(self):
        login = {"login": LOGIN, "password": PASSWORD}
        respons = requests.post(f'{self.url}auth/open', json=login)

        if (respons.status_code == 200):
            self.token = respons.json()['token']
        return None

    def __sendPost(self,path,body=None):
        Headers = {'Authorization' : "Bearer " + self.token }
        response = requests.post(f'{self.url}{path}', headers=Headers, json=body)
        return response

    def getListDevices(self):
        """
        Возвращает список устройств
        :return:
        """
        response = self.__sendPost('device/index')
        if (response.status_code == 200):
            list = response.json()
        return list

    def getCategories(self):
        """
        Возвращает список категорий объектов
        :return:
        """
        response = self.__sendPost('category/index')
        if (response.status_code == 200):
            list = self.sort_list(response.json())

        return list

    def getDeviceInfo(self,id):
        """
        Возвращает список параметров устройства
        :return:
        """

        response = self.__sendPost(f'device/{id}')
        if (response.status_code == 200):
            list = response.json()
        return list

    def getDeviceParam(self,id):
        """
        Возвращает значения параметров устройства
        :return:
        """

        params_list = self.getDeviceInfo(id)

        params_dict = {i['id']:i  for i in params_list['parameters']}
        ids = [i for i in params_dict.keys()]
        body = {'ids':ids}

        response = self.__sendPost(f'parameters/last-data',body=body)
        if (response.status_code == 200):
            list = response.json()
        return list,params_dict,params_list['name']

    def sort_list(self, data):
        parent_id = set(i['parent_id'] for i in data)
        id = set(i['id'] for i in data)
        root = [parent_id - id]
        root = list(root[0])[0]
        data_dict = {item['id']: item for item in data}

        # Функция для рекурсивной сортировки
        def recursive_sort(item):
            result = [item]
            children = [child for child in data if child.get('parent_id') == item['id']]
            for child in children:
                result.extend(recursive_sort(child))
            return result

        # Сортируем каждый элемент списка, начиная с корневых уровней
        sorted_data = []
        for item in data:
            if item.get('parent_id') == root:
                sorted_data.extend(recursive_sort(item))

        return sorted_data

# my = OwenApi()
# my.getToken()
# rez = my.getListDevices()
#
# t = 0