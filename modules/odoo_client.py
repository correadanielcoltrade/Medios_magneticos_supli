import os
import re
import xmlrpc.client
from pathlib import Path
from urllib.parse import urlparse


def load_env_file(path=None):
    env_path = Path(path or Path.cwd() / '.env')
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


class OdooContactProvider:
    """Consulta datos basicos de contacto en Odoo para completar reportes."""

    def __init__(self, url, db, user, password):
        self.url = self._normalizar_url(url)
        self.db = db
        self.user = user
        self.password = password
        self.uid = None
        self._models = None
        self._partner_fields = None
        self._city_fields = None
        self._state_cache = {}
        self._city_cache = {}
        self._cache = {}

    @classmethod
    def from_environment(cls):
        load_env_file()
        url = os.environ.get('ODOO_URL', '').strip()
        user = os.environ.get('ODOO_USER', '').strip()
        # Para xmlrpc, SIEMPRE usar la contraseña real, nunca la API Key
        password = os.environ.get('ODOO_PASSWORD', '').strip()
        db = os.environ.get('ODOO_DB', '').strip() or cls._inferir_db(url)

        if not all([url, db, user, password]):
            return None
        return cls(url, db, user, password)

    @staticmethod
    def _normalizar_url(url):
        url = url.strip().rstrip('/')
        if url.endswith('/odoo'):
            url = url[:-5]
        return url

    @staticmethod
    def _inferir_db(url):
        host = urlparse(url).hostname or ''
        if host.endswith('.odoo.com'):
            return host.split('.')[0]
        return ''

    @staticmethod
    def _limpiar_vat(valor):
        return re.sub(r'[^0-9A-Za-z]', '', str(valor or '')).upper()

    @classmethod
    def _variantes_vat(cls, nit):
        nit = str(nit or '').strip()
        limpio = cls._limpiar_vat(nit)
        variantes = [nit]
        if '-' in nit:
            variantes.append(nit.split('-', 1)[0])
        if limpio:
            variantes.append(limpio)
            if len(limpio) > 1:
                variantes.append(limpio[:-1])
        return list(dict.fromkeys(v for v in variantes if v))

    @staticmethod
    def _dominio_or(campo, operador, valores):
        condiciones = [(campo, operador, valor) for valor in valores]
        if not condiciones:
            return []
        if len(condiciones) == 1:
            return [condiciones[0]]
        return ['|'] * (len(condiciones) - 1) + condiciones

    def _conectar(self):
        if self.uid and self._models:
            return

        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common', allow_none=True)
        self.uid = common.authenticate(self.db, self.user, self.password, {})
        if not self.uid:
            raise RuntimeError('No fue posible autenticarse en Odoo.')

        self._models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object', allow_none=True)

    def _execute_kw(self, model, method, args=None, kwargs=None):
        self._conectar()
        return self._models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args or [],
            kwargs or {},
        )

    def _fields_get(self, model):
        return self._execute_kw(model, 'fields_get', [], {'attributes': ['string']})

    def _partner_campos(self):
        if self._partner_fields is None:
            self._partner_fields = self._fields_get('res.partner')
        return self._partner_fields

    def _city_campos(self):
        if self._city_fields is None:
            try:
                self._city_fields = self._fields_get('res.city')
            except Exception:
                self._city_fields = {}
        return self._city_fields

    def _leer_estado(self, state_id):
        if not state_id:
            return {}
        if state_id not in self._state_cache:
            registros = self._execute_kw(
                'res.country.state',
                'read',
                [[state_id], ['name', 'code']],
            )
            self._state_cache[state_id] = registros[0] if registros else {}
        return self._state_cache[state_id]

    def _leer_ciudad(self, city_id):
        if not city_id:
            return {}
        if city_id not in self._city_cache:
            campos_disponibles = self._city_campos()
            campos = ['name']
            for campo in ('code', 'l10n_co_edi_code'):
                if campo in campos_disponibles:
                    campos.append(campo)
            registros = self._execute_kw('res.city', 'read', [[city_id], campos])
            self._city_cache[city_id] = registros[0] if registros else {}
        return self._city_cache[city_id]

    @staticmethod
    def _codigo_municipio(codigo_ciudad, codigo_dpto):
        codigo_ciudad = str(codigo_ciudad or '').strip()
        codigo_dpto = str(codigo_dpto or '').strip()
        if codigo_ciudad.isdigit() and len(codigo_ciudad) >= 5 and codigo_ciudad.startswith(codigo_dpto):
            return codigo_ciudad[-3:]
        return codigo_ciudad

    @staticmethod
    def _codigo_pais(country_id):
        if not country_id:
            return ''
        nombre = country_id[1] if isinstance(country_id, list) and len(country_id) > 1 else ''
        return '169' if 'colombia' in str(nombre).lower() else str(nombre)

    def _mapear_contacto(self, contacto):
        direccion = ' '.join(
            parte for parte in [
                str(contacto.get('street') or '').strip(),
                str(contacto.get('street2') or '').strip(),
            ]
            if parte
        )

        estado = self._leer_estado(contacto.get('state_id')[0]) if contacto.get('state_id') else {}
        dpto = str(estado.get('code') or '').strip()

        ciudad = ''
        if contacto.get('city_id'):
            ciudad_odoo = self._leer_ciudad(contacto['city_id'][0])
            codigo_ciudad = ciudad_odoo.get('code') or ciudad_odoo.get('l10n_co_edi_code')
            ciudad = self._codigo_municipio(codigo_ciudad, dpto) or ciudad_odoo.get('name', '')
        ciudad = ciudad or str(contacto.get('city') or '').strip()

        return {
            'direccion': direccion,
            'dpto': dpto,
            'municipio': ciudad,
            'pais': self._codigo_pais(contacto.get('country_id')),
        }

    def obtener_contacto(self, nit):
        clave = self._limpiar_vat(nit)
        if not clave:
            return {}
        if clave in self._cache:
            return self._cache[clave]

        variantes = self._variantes_vat(nit)
        campos_disponibles = self._partner_campos()
        campos = ['vat', 'street', 'street2', 'city', 'state_id', 'country_id']
        if 'city_id' in campos_disponibles:
            campos.append('city_id')

        contactos = self._execute_kw(
            'res.partner',
            'search_read',
            [self._dominio_or('vat', '=', variantes)],
            {'fields': campos, 'limit': 5},
        )
        if not contactos and clave:
            contactos = self._execute_kw(
                'res.partner',
                'search_read',
                [[('vat', 'ilike', clave)]],
                {'fields': campos, 'limit': 10},
            )

        contacto = {}
        claves_validas = {self._limpiar_vat(v) for v in variantes}
        for candidato in contactos:
            if self._limpiar_vat(candidato.get('vat')) in claves_validas:
                contacto = candidato
                break
        if not contacto and contactos:
            contacto = contactos[0]

        datos = self._mapear_contacto(contacto) if contacto else {}
        self._cache[clave] = datos
        return datos

    def obtener_contactos(self, nits):
        return {str(nit): self.obtener_contacto(nit) for nit in nits}
