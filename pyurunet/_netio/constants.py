#    PyUruNet
#    Copyright (C) 2016  Adam 'Hoikas' Johnson <AdamJohnso AT gmail DOT com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import uuid

class DiffieHellmanG:
    auth = 41
    game = 73
    gatekeeper = 4


class NetProtocol:
    auth = 10
    gatekeeper = 22
    file = 16


class Product:
    branch_id = 1
    build_id = 918
    host = "127.0.0.1"
    port = 14617
    uuid = uuid.UUID("ea489821-6c35-4bd0-9dae-bb17c585e680")
