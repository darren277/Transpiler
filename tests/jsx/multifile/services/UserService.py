from axios import axios

NGINX_HOST = process.env.REACT_APP_NGINX_HOST
NGINX_PORT = process.env.REACT_APP_NGINX_PORT

FLASK_APP = f'http://{NGINX_HOST}:{NGINX_PORT}/flaskapp'

USER_API_BASE_URL = f'{FLASK_APP}/users'


class UserService:
    def getUsers(self): return axios.get(USER_API_BASE_URL)
    def createUser(self, user): return axios.post(USER_API_BASE_URL, user, {headers: { 'Content-Type': 'application/json' }})
    def getUserById(self, userId): return axios.get(USER_API_BASE_URL + '/' + userId)
    def updateUser(self, userId, user): return axios.put(USER_API_BASE_URL + '/' + userId, user, {headers: { 'Content-Type': 'application/json' }})
    def deleteUser(self, userId): return axios.delete(USER_API_BASE_URL + '/' + userId)

