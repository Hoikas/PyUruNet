//    PyUruNet
//    Copyright (C) 2016  Adam 'Hoikas' Johnson <AdamJohnso AT gmail DOT com>
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Affero General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Affero General Public License for more details.
//
//    You should have received a copy of the GNU Affero General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include <memory>

#include "urunet.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// ==============================================================================

PYBIND11_MODULE(_urunet, m)
{
    m.doc() = "PyUruNet C++ helper module";

    // SHA Functions
    // NOTE: We could use buffer.str() to get a binary std::string, but binary
    //       std::strings are unusual IMO, and that would require an extra copy.
    //       So we use the low-level Python API to work with the bytes.
    m.def(
        "sha0_buffer",
        [](const pybind11::bytes& buffer) {
            return urunet::sha0_buffer(PyBytes_AsString(buffer.ptr()), PyBytes_Size(buffer.ptr()));
        },
        pybind11::pos_only(),
        pybind11::arg("value")
    );
    m.def(
        "sha1_buffer",
        [](const pybind11::bytes& buffer) {
            return urunet::sha1_buffer(PyBytes_AsString(buffer.ptr()), PyBytes_Size(buffer.ptr()));
        },
        pybind11::pos_only(),
        pybind11::arg("value")
    );
    m.def(
        "sha0_string",
        [](const pybind11::bytes& buffer) {
            return urunet::sha0_string(PyBytes_AsString(buffer.ptr()), PyBytes_Size(buffer.ptr()));
        },
        pybind11::pos_only(),
        pybind11::arg("value")
    );
    m.def(
        "sha1_string",
        [](const pybind11::bytes& buffer) {
            return urunet::sha1_string(PyBytes_AsString(buffer.ptr()), PyBytes_Size(buffer.ptr()));
        },
        pybind11::pos_only(),
        pybind11::arg("value")
    );

    // RC4
    pybind11::class_<urunet::rc4>(m, "rc4")
        .def(
            pybind11::init([](const pybind11::bytes& key) {
                return std::make_unique<urunet::rc4>(PyBytes_AsString(key.ptr()), PyBytes_Size(key.ptr()));
            })
        )
        .def(
            "transform",
            [](urunet::rc4& self, const pybind11::bytes& buffer) {
                const Py_ssize_t size = PyBytes_Size(buffer.ptr());
                if (size <= 256) {
                    char temp[256];
                    self.transform(PyBytes_AsString(buffer.ptr()), temp, size);
                    return pybind11::bytes(temp, size);
                } else {
                    auto temp = std::make_unique<char[]>(size);
                    self.transform(PyBytes_AsString(buffer.ptr()), temp.get(), size);
                    return pybind11::bytes(temp.get(), size);
                }
            }
        )
    ;
}
