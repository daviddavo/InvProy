# -*- coding: utf-8 -*-
#!/usr/bin/env python3

'''
    InvProy - Simulador de Redes / Proyecto de Investigación
    https://github.com/daviddavo/InvProy
    Copyright (C) 2016  David Davó Laviña  david@ddavo.me  http://ddavo.me
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    /////////////////////////////
    Este programa es código libre: Puedes redistribuirlo y/o modificarlo
    bajo los términos de la licencia GNU General Public License tal y como
    publicado por la Free Software Foundation, ya sea la versión 3 de layout
    licencia o la más reciente.
    Este programa es distribuido con la esperanza de que sea útil, pero
    SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de COMERCIABILIDAD
    o de la APTITUD DE LA MISMA PARA UN PROPÓSITO PARTICULAR. Ver la GNU General
    Public License para más detalles.
    Debes haber recibido una copia de la GNU General Public License con
    este programa, si no es así, ver <http://www.gnu.org/licenses/>.
'''

import os
from datetime import datetime
startTime = datetime.now()
from utils import logging
logger = logging.getLogger(__name__)

logger.debug("this is a debugging message")
logger.info("this is an informational message")
logger.warn("this is a warning message")
logger.error("this is an error message")
logger.critical("this is a critical message")

logger.info("Complete load time: %s", datetime.now() - startTime)