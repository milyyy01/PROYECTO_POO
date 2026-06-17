import requests
from evaluacion import Evaluacion

class MoodleService:

    def __init__(self, token, domain):
        self.token = token
        self.domain = domain
        self.url = f"{domain}/webservice/rest/server.php"

    def obtener_evaluaciones(self, courseid):
        params = {
            "wstoken": self.token,
            "wsfunction": "core_course_get_contents",
            "moodlewsrestformat": "json",
            "courseid": courseid
        }

        response = requests.get(self.url, params=params)

        evaluaciones = []

        if response.status_code == 200:
            data = response.json()

            for seccion in data:
                for mod in seccion.get("modules", []):
                    if mod["modname"] in ["assign", "quiz"]:
                        
                        # convertir API → objeto Evaluacion
                        ev = Evaluacion(
                            id_eval=mod["id"],
                            nombre=mod["name"],
                            tipo=mod["modname"],
                            fecha=None,
                            puntaje_max=100
                        )

                        evaluaciones.append(ev)

        return evaluaciones
