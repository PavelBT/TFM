# services/field_correctors/form_cleaners/banorte_credito.py

from typing import Dict
from services.field_correctors.alias_mapper import AliasMapper

class BanorteCreditoFormProcessor:
    def __init__(self):
        self.mapper = AliasMapper("services/field_correctors/aliases/banorte_credito.yaml")

    def transform(self, fields: Dict[str, str]) -> Dict:
        get = lambda k: self.mapper.get(fields, k)

        return {
            "tipo_formulario": "solicitud_credito_personal_banorte",

            "datos_control": {
                "folio": get("folio"),
                "fecha_solicitud": {
                    "dia": get("dia"),
                    "mes": get("mes"),
                    "año": get("año")
                },
                "no_cliente": get("no_cliente"),
                "sucursal": get("sucursal"),
                "nombre_ejecutivo": get("nombre_ejecutivo"),
                "no_nomina": get("no_nomina"),
                "zona_region": get("zona_region")
            },

            "credito": {
                "monto_solicitado": get("monto_solicitado").replace("$", "").replace(",", ""),
                "plazo_credito": self.mapper.get_checked(fields, ["12", "18", "24", "36"]),
                "cuenta_cliente": get("cuenta_cliente")
            },

            "datos_personales": {
                "nombre": get("nombre").title(),
                "apellido_paterno": get("apellido_paterno").title(),
                "apellido_materno": get("apellido_materno").title(),
                "genero": self.mapper.get_checked(fields, ["femenino", "masculino"]),
                "fecha_nacimiento": {
                    "dia": get("nacimiento_dia"),
                    "mes": get("nacimiento_mes"),
                    "año": get("nacimiento_año")
                },
                "edad": get("edad"),
                "estado_civil": self.mapper.get_checked(fields, ["soltero", "casado", "unión libre", "divorciado", "viudo"]),
                "regimen_matrimonial": self.mapper.get_checked(fields, ["sociedad conyugal", "separación de bienes"]),
                "rfc": get("rfc"),
                "curp": get("curp"),
                "nacionalidad": get("nacionalidad"),
                "pais_nacimiento": get("pais_nacimiento"),
                "entidad_nacimiento": get("entidad_nacimiento"),
                "grado_estudios": get("grado_estudios"),
                "tipo_identificacion": get("tipo_identificacion"),
                "numero_identificacion": get("numero_identificacion"),
                "domicilio": {
                    "calle": get("domicilio_calle"),
                    "colonia": get("domicilio_colonia"),
                    "municipio": get("domicilio_municipio"),
                    "estado": get("domicilio_estado"),
                    "cp": get("domicilio_cp")
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
                "tipo_ingreso": self.mapper.get_checked(fields, ["asalariado", "honorarios"])
            },

            "finanzas": {
                "ingreso_mensual": get("ingreso_mensual").replace("$", "").replace(",", ""),
                "otros_ingresos": self.mapper.get_checked(fields, ["sí", "no"]),
                "origen_otros_ingresos": get("origen_otros_ingresos"),
                "gastos_mensuales": get("gastos_mensuales"),
                "tipo_propiedad": self.mapper.get_checked(fields, ["propia", "rentada", "hipotecada", "de familiares"])
            },

            "referencias": {
                "referencia_1": {
                    "nombre": get("referencia1_nombre"),
                    "parentesco": get("referencia1_parentesco"),
                    "telefono": get("referencia1_telefono")
                },
                "referencia_2": {
                    "nombre": get("referencia2_nombre"),
                    "parentesco": get("referencia2_parentesco"),
                    "telefono": get("referencia2_telefono")
                }
            },

            "otros": {
                "autorizacion_consulta_buro": True,
                "aceptacion_terminos": True
            }
        }
