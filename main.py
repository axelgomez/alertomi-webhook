#/usr/bin/python

'''
El flujo es:
1. entra JSON_ejemplo. Se loguea
2. se parsea
3. se valida si ya existe en el diccionario de alertas
4. si existe se le asigna el id existente
5. si no existe se espera a respuesta del omi para el id
6. se envía al omi la actualización. Se loguea
6.1 si el envío falla se envía mail (pendiente smtp) y se retorna. Se loguea
7. se almacena el id en el diccionario
8. 


'''
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import logging
from datetime import date, timedelta, datetime


class Labels(BaseModel):
  alertname: str
  instance: str
  job: str
  severity: str


class Annotations(BaseModel):
  description: str
  summary: str


class Alerts(BaseModel):
  status: str
  labels: Labels
  annotations: Annotations
  startsAt: str
  endsAt: str
  generatorURL: str
  fingerprint: Optional[str]


class GroupLabels(BaseModel):
  instance: Optional[str]
  severity: Optional[str]
  alertname: Optional[str]


class CommonLabels(BaseModel):
  alertname: str
  instance: str
  job: str
  severity: str


class CommonAnnotations(BaseModel):
  description: Optional[str]
  summary: Optional[str]


class Alertas(BaseModel):
  receiver: str
  status: str
  alerts: List[Alerts]
  #groupLabels: GroupLabels
  #commonLabels: CommonLabels
  #commonAnnotations: CommonAnnotations
  externalURL: str
  version: str
  groupKey: str
  truncatedAlerts: Optional[str]


'''
{
  "receiver": "webhook",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "PrometheusTargetMissing",
        "instance": "localhost:9100",
        "job": "node_exporter",
        "severity": "critical"
      },
      "annotations": {
        "description": "A Prometheus targets has disappeared. An exporter might be crashed.\n VALUE = 0\n LABELS: map[__name__:up instance:localhost:9100 job:node_exporter]",
        "summary": "Prometheus target missing (instance localhost:9100)"
      },
      "startsAt": "2020-07-29T19:02:37.336992059Z",
      "endsAt": "2020-07-29T19:06:37.336992059Z",
      "generatorURL": "http://localhost:9090/graph?g0.expr=up+%3D%3D+0&g0.tab=1"
    }
  ],
  "groupLabels": {
    "instance": "localhost:9100",
    "severity": "critical"
  },
  "commonLabels": {
    "alertname": "PrometheusTargetMissing",
    "instance": "localhost:9100",
    "job": "node_exporter",
    "severity": "critical"
  },
  "commonAnnotations": {
    "description": "A Prometheus target has disappeared. An exporter might be crashed.\n VALUE = 0\n LABELS: map[__name__:up instance:localhost:9100)"
  },
  "externalURL": "http://localhost:9093",
  "version": "4",
  "groupKey": "{}:{instance=\"localhost:9100\", severity=\"critical\"}"
}
'''


class Item(BaseModel):
  name: str
  price: float
  is_offer: Optional[bool] = None


def ParsearAlerta(alerta):
  #se obtienen las variables a enviar al omi-notify-update.sh
  # ${APLICACION}|${TITULO}|${DESCRIPCION}|${SEVERIDAD_OMI}|${PRIORIDAD_OMI}|${ESTADO_OMI}|${CATEGORIA}
  if (alerta.status == "firing"):
    estado_servicio = alerta.labels.severity.upper()
    severidad_omi = "CRITICAL"
    prioridad_omi = "highest"
    estado_omi = "O"
  elif(alerta.status == "resolved"):
    estado_servicio = "OK"
    severidad_omi = "NORMAL"
    prioridad_omi = "lowest"
    estado_omi = "R"
  else:
    estado_servicio = "DESCONOCIDO"
    severidad_omi = "DESCONOCIDA"
    prioridad_omi = ""
    estado_omi = ""

  aplicacion = alerta.labels.job
  titulo = "{} - {} - {}".format(
      alerta.labels.instance,
      alerta.labels.alertname,
      estado_servicio
  )
  descripcion = "{} - {} - {}".format(
      titulo,
      alerta.annotations.description,
      "MENSAJE PREDETERMINADO"
  )

  #return aplicacion, ("{},{},{},{},{}".format(
  return aplicacion, titulo, descripcion, severidad_omi, prioridad_omi, estado_omi


def AlmacenarEnLog(logger, alerta):
  aplicacion, titulo, descripcion, severidad_omi, prioridad_omi, estado_omi = ParsearAlerta(
      alerta)

  #echo "$FECHA | $APLICACION | $NOTIFICATIONTYPE | $SERVICEDESC | $HOSTNAME | $HOSTADDRESS | $SERVICESTATE | $LONGDATETIME | $SERVICEOUTPUT | $MENSAJE | $ESTADO_OMI envia_OMI=$ENVIA_OMI | mail=$ENVIA_MAIL | " >> $LOG_FILE
  if (alerta.status == "firing"):
    estado_servicio = alerta.labels.severity.upper()
  elif(alerta.status == "resolved"):
    estado_servicio = "OK"
  else:
    estado_servicio = "UNKNOWN"

  desc_servicio = alerta.annotations.description
  hostaddress = alerta.labels.instance
  mensaje = "MENSAJE PREDETERMINADO"

  logger.info("{} | {} | {} | {}".format(
      aplicacion,
      desc_servicio,
      hostaddress,
      estado_servicio,
      mensaje,
      estado_omi,
      severidad_omi
  )
  )
  return


#MAIN
logger = logging.getLogger('alertmanager-omi-webhook')
hdlr = logging.FileHandler('log/' + 'alertmanager-omi-webhook.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

app = FastAPI()


@app.get("/")
def read_root():
  return {"Hola": "Leo"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
  return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
  return {"item_name": item.name, "item_id": item_id}


@app.post("/alerts")
def actualizar_alerta(
    *,
        alertas: Alertas):
    for a in alertas.alerts:
      aplicacion, titulo, descripcion, severidad_omi, prioridad_omi, estado_omi = ParsearAlerta(
          a)
      print("{}|{}|{}|{}|{}|{}".format(aplicacion, titulo,
                                       descripcion, severidad_omi, prioridad_omi, estado_omi))
      AlmacenarEnLog(logger, a)
    return {"status": "OK"}


@app.post("/echo")
def actualizar_alerta(
    *,
        alertas: Alertas):
    dict_alertas = alertas.dict()
    return dict_alertas
