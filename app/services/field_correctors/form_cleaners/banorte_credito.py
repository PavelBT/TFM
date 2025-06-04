# services/field_correctors/form_cleaners/banorte_credito.py

from typing import Dict
from services.field_correctors.alias_mapper import AliasMapper

class BanorteCreditoFormProcessor:
    def __init__(self):
        self.mapper = AliasMapper("services/field_correctors/aliases/banorte_credito.yaml")

    def transform(self, fields: Dict[str, str]) -> Dict:
        get = lambda k: self.mapper.get(fields, k) or ""
        get_checked = lambda keys: self.mapper.get_checked(fields, keys)

        # Fecha de solicitud
        fecha_solicitud = {
            "dia": get("fecha_solicitud.dia"),
            "mes": get("fecha_solicitud.mes"),
            "año": get("fecha_solicitud.año")
        }
        if all(fecha_solicitud.values()):
            fecha_solicitud_str = f"{fecha_solicitud['año']}-{fecha_solicitud['mes'].zfill(2)}-{fecha_solicitud['dia'].zfill(2)}"
        else:
            fecha_solicitud_str = ""

        # Género
        genero = ""
        if get_checked(["genero.femenino"]) == "Sí":
            genero = "F"
        elif get_checked(["genero.masculino"]) == "Sí":
            genero = "M"

        # Estado civil
        estado_civil = get_checked([
            "estado_civil.soltero (a)", "estado_civil.casado (a)", "estado_civil.unión libre",
            "estado_civil.divorciado (a)", "estado_civil.viudo (a)"
        ]) or get_checked([
            "soltero", "casado", "unión libre", "divorciado", "viudo"
        ])

        # Régimen matrimonial
        regimen_matrimonial = get_checked([
            "regimen_matrimonial.sociedad conyugal", "regimen_matrimonial.separación de bienes"
        ]) or get_checked([
            "sociedad conyugal", "separación de bienes"
        ])

        # Plazo crédito
        plazo_credito = get_checked(["12", "18", "24", "36"])

        # Tipo ingreso
        tipo_ingreso = get_checked(["asalariado", "honorarios"])

        # Tipo propiedad
        tipo_propiedad = get_checked(["propia", "rentada", "hipotecada", "de familiares"])

        # Otros ingresos
        otros_ingresos = get_checked(["sí", "no"])

        # Montos
        def clean_monto(val):
            if not val:
                return ""
            return val.replace("$", "").replace(",", "").replace(".", "")

        return {
            "tipo_formulario": "solicitud_credito_personal_banorte",

            "datos_control": {
                "folio": get("folio"),
                "fecha_solicitud": fecha_solicitud_str,
                "no_cliente": get("no_cliente"),
                "sucursal": get("sucursal"),
                "nombre_ejecutivo": get("nombre_ejecutivo"),
                "no_nomina": get("no_nomina"),
                "zona_region": get("zona_region")
            },

            "credito": {
                "monto_solicitado": clean_monto(get("monto_solicitado")),
                "plazo_credito": plazo_credito,
                "cuenta_cliente": get("cuenta_cliente")
            },

            "datos_personales": {
                "nombre": get("nombre").title(),
                "apellido_paterno": get("apellido_paterno").title(),
                "apellido_materno": get("apellido_materno").title(),
                "genero": genero,
                "fecha_nacimiento": {
                    "dia": get("nacimiento_dia"),
                    "mes": get("nacimiento_mes"),
                    "año": get("nacimiento_año")
                },
                "edad": get("edad"),
                "estado_civil": estado_civil,
                "regimen_matrimonial": regimen_matrimonial,
                "rfc": get("rfc"),
                "curp": get("curp"),
                "nacionalidad": get("nacionalidad"),
                "pais_nacimiento": get("pais_nacimiento"),
                "entidad_nacimiento": get("entidad_nacimiento"),
                "grado_estudios": get("grado_estudios"),
                "tipo_identificacion": get("tipo_identificacion"),
                "numero_identificacion": get("numero_identificacion"),
                "domicilio": {
                    "calle": get("domicilio.calle"),
                    "colonia": get("domicilio.colonia"),
                    "municipio": get("domicilio.municipio"),
                    "estado": get("domicilio.estado"),
                    "cp": get("domicilio.cp")
                },
                "telefono_casa": get("telefono_casa"),
                "telefono_celular": get("telefono_celular"),
                "otro_telefono": get("otro_telefono"),
                "tiempo_residencia": get("tiempo_residencia")
            },

            "empleo_actual": {
                "empresa": get("empresa"),
                "domicilio_laboral": get("domicilio_laboral"),
                "telefono_empresa": get("telefono_empresa"),
                "giro_empresa": get("giro_empresa"),
                "puesto": get("puesto"),
                "nombre_jefe": get("nombre_jefe"),
                "antiguedad_meses": get("antiguedad_meses"),
                "tipo_ingreso": tipo_ingreso
            },

            "finanzas": {
                "ingreso_mensual": clean_monto(get("ingreso_mensual")),
                "otros_ingresos": otros_ingresos,
                "origen_otros_ingresos": get("origen_otros_ingresos"),
                "gastos_mensuales": get("gastos_mensuales"),
                "tipo_propiedad": tipo_propiedad
            },

            "referencias": {
                "referencia_1": {
                    "nombre": get("referencia_1.nombre"),
                    "parentesco": get("referencia_1.parentesco"),
                    "telefono": get("referencia_1.telefono")
                },
                "referencia_2": {
                    "nombre": get("referencia_2.nombre"),
                    "parentesco": get("referencia_2.parentesco"),
                    "telefono": get("referencia_2.telefono")
                }
            },

            "otros": {
                "autorizacion_consulta_buro": True,
                "aceptacion_terminos": True
            }
        }
