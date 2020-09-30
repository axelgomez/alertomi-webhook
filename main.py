#/usr/bin/python

'''
El flujo es:
1. Se recibe la alerta de AlertManager
2. FastAPI valida y parsea el JSON que recibe
3. Se imprime por pantalla lo recibido
4. Se obtienen las variables que importan
5. Se envían al distribuidor de alertas dichas variables en un POST
6. Se imprime la respuesta del POST

Un Json de ejemplo es:
{
   "receiver":"webhook",
   "status":"firing",
   "alerts":[
      {
         "status":"firing",
         "labels":{
            "region": "VERA",
            "environment": "NO PROD",
            "alertname":"KubeNodeUnreachable",
            "effect":"NoSchedule",
            "endpoint":"https-main",
            "instance":"10.130.0.19:8443",
            "job":"kube-state-metrics",
            "key":"node.kubernetes.io/unreachable",
            "namespace":"openshift-monitoring",
            "node":"swrk2024os.cltrnoprod.bancocredicoop.coop",
            "pod":"kube-state-metrics-7c858887c5-98swk",
            "prometheus":"openshift-monitoring/k8s",
            "service":"kube-state-metrics",
            "severity":"warning"
         },
         "annotations":{
            "message":"swrk2024os.cltrnoprod.bancocredicoop.coop is unreachable and some workloads may be rescheduled."
         },
         "startsAt":"2020-08-20T16:37:30.395075553Z",
         "endsAt":"0001-01-01T00:00:00Z",
         "generatorURL":"https://prometheus-k8s-openshift-monitoring.apps.cltrnoprod.bancocredicoop.coop/graph?g0.expr=kube_node_spec_taint%7Beffect%3D%22NoSchedule%22%2Cjob%3D%22kube-state-metrics%22%2Ckey%3D%22node.kubernetes.io%2Funreachable%22%7D+%3D%3D+1\u0026g0.tab=1",
         "fingerprint":"86b60c836f0561c4"
      }
   ],
   "groupLabels":{
   },
   "commonLabels":{
      "alertname":"KubeNodeUnreachable",
      "effect":"NoSchedule",
      "endpoint":"https-main",
      "instance":"10.130.0.19:8443",
      "job":"kube-state-metrics",
      "key":"node.kubernetes.io/unreachable",
      "namespace":"openshift-monitoring",
      "node":"swrk2024os.cltrnoprod.bancocredicoop.coop",
      "pod":"kube-state-metrics-7c858887c5-98swk",
      "prometheus":"openshift-monitoring/k8s",
      "service":"kube-state-metrics",
      "severity":"warning"
   },
   "commonAnnotations":{
      "message":"swrk2024os.cltrnoprod.bancocredicoop.coop is unreachable and some workloads may be rescheduled."
   },
   "externalURL":"https://alertmanager-main-openshift-monitoring.apps.cltrnoprod.bancocredicoop.coop",
   "version":"4",
   "groupKey":"{}/{severity=~\"^(?:critical|warning)$\"}:{}"
}

La URL del distribuidor de alertas es:
http://snsc-desa.bancocredicoop.coop/consola-gerproc/alertas.php?sistema=[NOMBRE DEL SISTEMA]&prioridad=[ALTA]&fecha=[YYYY-MM-DD]&componente=[Redes]&estado=[MAYOR,CRITICO,CESE]&mensaje=[TEXTO]&indicaciones=[DESCRIPCION DE ACCION A TOMAR]

'''

from typing import List, Optional
from fastapi import FastAPI,Request,status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import date, timedelta, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import smtplib

#Especificar comentario para modificacion de estructura
class Labels(BaseModel):
  alertname: str
  severity: str
  alertmanager: Optional[str]
  config_hash: Optional[str]
  deployment: Optional[str]
  effect: Optional[str]
  daemonset: Optional[str]
  condition: Optional[str]
  endpoint: Optional[str]
  environment: Optional[str]
  instance: Optional[str]
  job_name: Optional[str]
  job: Optional[str]
  key: Optional[str]
  hostname: Optional[str]
  name: Optional[str]
  plugin_id: Optional[str]
  namespace: Optional[str]
  node: Optional[str]
  pod: Optional[str]
  container: Optional[str]
  prometheus: Optional[str]
  region: Optional[str]
  reason: Optional[str]
  exported_namespace: Optional[str]
  phase: Optional[str]
  resource: Optional[str]
  service: Optional[str]
  version: Optional[str]
  verb: Optional[str]
  status: Optional[str]
  type: Optional[str]

  
#Establish SMTP Connection
#s = smtplib.SMTP('smtp.bancocredicoop.coop', 25) 
  
#Start TLS based SMTP Session
#s.starttls() 
 
#Login Using Your Email ID & Password
#s.login("your-email@id.com", "your-email-ID-PASSWORD")

class Annotations(BaseModel):
  message: Optional[str]
  description: Optional[str]
  summary: Optional[str]

class Alerts(BaseModel):
  status: str
  labels: Labels
  annotations: Annotations
  startsAt: Optional[str]
  endsAt: Optional[str]
  generatorURL: Optional[str]
  fingerprint: Optional[str]


#class GroupLabels(BaseModel):
#  instance: Optional[str]
# severity: Optional[str]
#  alertname: Optional[str]


class CommonLabels(BaseModel):
  alertname: str
  severity: str
  effect: Optional[str]
  endpoint: Optional[str]
  instance: Optional[str]
  job: Optional[str]
  key: Optional[str]
  namespace: Optional[str]
  node: Optional[str]
  pod: Optional[str]
  prometheus: Optional[str]
  service: Optional[str]


class CommonAnnotations(BaseModel):
  description: Optional[str]
  summary: Optional[str]
  message: Optional[str]


class Alertas(BaseModel):
  receiver: str
  status: str
  alerts: List[Alerts]
  #groupLabels: GroupLabels
  #commonLabels: CommonLabels
  #commonAnnotations: CommonAnnotations
  externalURL: Optional[str]
  version: Optional[str]
  groupKey: Optional[str]
  truncatedAlerts: Optional[str]


'''
{
   "receiver":"webhook",
   "status":"firing",
   "alerts":[
      {
         "status":"firing",
         "labels":{
            "alertname":"KubeNodeUnreachable",
            "effect":"NoSchedule",
            "endpoint":"https-main",
            "instance":"10.130.0.19:8443",
            "job":"kube-state-metrics",
            "key":"node.kubernetes.io/unreachable",
            "namespace":"openshift-monitoring",
            "node":"swrk2024os.cltrnoprod.bancocredicoop.coop",
            "pod":"kube-state-metrics-7c858887c5-98swk",
            "prometheus":"openshift-monitoring/k8s",
            "service":"kube-state-metrics",
            "severity":"warning"
         },
         "annotations":{
            "message":"swrk2024os.cltrnoprod.bancocredicoop.coop is unreachable and some workloads may be rescheduled."
         },
         "startsAt":"2020-08-20T16:37:30.395075553Z",
         "endsAt":"0001-01-01T00:00:00Z",
         "generatorURL":"https://prometheus-k8s-openshift-monitoring.apps.cltrnoprod.bancocredicoop.coop/graph?g0.expr=kube_node_spec_taint%7Beffect%3D%22NoSchedule%22%2Cjob%3D%22kube-state-metrics%22%2Ckey%3D%22node.kubernetes.io%2Funreachable%22%7D+%3D%3D+1\u0026g0.tab=1",
         "fingerprint":"86b60c836f0561c4"
      }
   ],
   "groupLabels":{

   },
   "commonLabels":{
      "alertname":"KubeNodeUnreachable",
      "effect":"NoSchedule",
      "endpoint":"https-main",
      "instance":"10.130.0.19:8443",
      "job":"kube-state-metrics",
      "key":"node.kubernetes.io/unreachable",
      "namespace":"openshift-monitoring",
      "node":"swrk2024os.cltrnoprod.bancocredicoop.coop",
      "pod":"kube-state-metrics-7c858887c5-98swk",
      "prometheus":"openshift-monitoring/k8s",
      "service":"kube-state-metrics",
      "severity":"warning"
   },
   "commonAnnotations":{
      "message":"swrk2024os.cltrnoprod.bancocredicoop.coop is unreachable and some workloads may be rescheduled."
   },
   "externalURL":"https://alertmanager-main-openshift-monitoring.apps.cltrnoprod.bancocredicoop.coop",
   "version":"4",
   "groupKey":"{}/{severity=~\"^(?:critical|warning)$\"}:{}"
}
'''
'''http://snsc-desa.bancocredicoop.coop/consola-gerproc/alertas.php?sistema=[NOMBRE DEL SISTEMA]&prioridad=[ALTA]&fecha=[YYYY-MM-DD]&componente=[Redes]&estado=[MAYOR,CRITICO,CESE]&mensaje=[TEXTO]&indicaciones=[DESCRIPCION DE ACCION A TOMAR]'''


class Item(BaseModel):
  name: str
  price: float
  is_offer: Optional[bool] = None


def ParsearAlerta(alerta):
  try:
    #se obtienen las variables a enviar al omi-notify-update.sh
    # ${APLICACION}|${TITULO}|${DESCRIPCION}|${SEVERIDAD_OMI}|${PRIORIDAD_OMI}|${ESTADO_OMI}|${CATEGORIA}
    f = open("/etc/alert-omi-webhook-dictionary/alerts-dictionary","r")
    file_content = f.read()
    variables_OMI = json.loads(file_content)
    f_config = open("/etc/alert-omi-webhook-dictionary/alert-webhook-config","r")
    file_config = f_config.read()
    config = json.loads(file_config)
    #Email Body Content
    
   

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
    titulo = ""
    if hasattr(alerta.labels,'instance'):
      if alerta.labels.instance != None:
        titulo += "{} - ".format(alerta.labels.instance)
    
    titulo += "{} - {}".format(
        alerta.labels.alertname,
        estado_servicio
    )

    clave_dict = "({},{})".format(alerta.labels.alertname,alerta.labels.severity)
    # Si la clave no existe en el diccionario -> retornar
    if clave_dict not in variables_OMI:
      mensaje_recibido = ""
      if hasattr(alerta,'startsAt'):
        if alerta.startsAt != None:
          mensaje_recibido += "{}".format(alerta.startsAt)
      mensaje_recibido += " - Recibido: {{{}}}".format(alerta)
      print("WARN - No existe en diccionario - {}".format(mensaje_recibido))
      return alerta

    mensaje = "{}".format(variables_OMI[clave_dict]['MENSAJE'])
    if hasattr(alerta.labels,'region'):
      if alerta.labels.region != None:
        mensaje += " - {}".format(alerta.labels.region)
    if hasattr(alerta.labels,'environment'):
      if alerta.labels.environment != None:
        mensaje += " - {}".format(alerta.labels.environment)
    indicaciones = variables_OMI[clave_dict]['INDICACIONES']  
    componente = variables_OMI[clave_dict]['COMPONENTE']
    if hasattr(alerta.labels,'node'):
      if alerta.labels.node != None:
        mensaje += " - node:{}".format(alerta.labels.node)
    if hasattr(alerta.labels,'namespace'):
      if alerta.labels.namespace != None:
        mensaje += " - namespace:{}".format(alerta.labels.namespace)

    if alerta.status == 'resolved':
      estado = "CESE"
    else:  
      estado= variables_OMI[clave_dict]['ESTADO']

    if("OMI" in variables_OMI[clave_dict]["ENVIO"]):
      payload = {'sistema': 'ESB Contenedores','prioridad':'ALTA','fecha':alerta.startsAt,'componente':componente,'estado':estado,'mensaje':mensaje,'indicaciones':indicaciones} 
      r = requests.post(config['ruta_snsc'], params=payload)

    #Enviar Email
#    if("EMAIL" in variables_OMI[clave_dict]["ENVIO"]):
#      tupla = ("OMI",alerta.labels.alertname,alerta.labels.environment,alerta.labels.namespace,alerta.labels.severity,alerta.labels.region)
#      subject= "| ".join(tupla) 
#      message="""From: {}
#      To: {}\n
#      Subject: {}\n
#      {}
#      """.format(config['sender_alertas'],config['dest_alertas'],subject,alerta)
#      s.sendmail(config['sender_alertas'], config['dest_alertas'], message)
    #Terminating the SMTP Session
#    s.quit()
    mensaje_recibido = ""
    mensaje_enviado = ""
    if hasattr(alerta,'startsAt'):
      if alerta.startsAt != None:
        mensaje_recibido += "{}".format(alerta.startsAt)
        mensaje_enviado += "{}".format(alerta.startsAt)
    mensaje_recibido += " - Recibido: {{{}}}".format(alerta)
    mensaje_enviado += " - Enviado: {}|{}|{}|{}|{}|{}".format(aplicacion,
                                                  titulo,
                                                  mensaje,
                                                  estado,
                                                  componente,
                                                  indicaciones)
    print("INFO - {}".format(mensaje_recibido))
    print("INFO - {}".format(mensaje_enviado))
    return alerta
  except RequestValidationError as e:
    raise RequestValidationError(r,e)


app = FastAPI()

@app.get("/")
def read_root():
  return {"Status": "Ok"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
  json_error = JSONResponse(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    content=jsonable_encoder({"detail": exc.errors(), "body": exc.body})
  )
  print("WARN - Estructura invalida - {}".format(json_error))
  return json_error


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
      alerta = ParsearAlerta(
          a)
      print("DEBUG - Alerta recibida - {}".format(alerta))
#      print("{}-Recibido:".format(a.startsAt) + "{" + "{}".format(a)+ "}")
#      print("{}-Enviado: {}|{}|{}|{}|{}|{}".format(a.startsAt,aplicacion, titulo,
#                                       mensaje, estado, componente, indicaciones))
    return {"status": "OK"}


@app.post("/echo")
def actualizar_alerta(
    *,
        alertas: Alertas):
    dict_alertas = alertas.dict()
    return dict_alertas


