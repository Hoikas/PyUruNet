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

#pragma once

#include <array>
#include <cstdint>
#include <string>

namespace urunet
{
    class rc4
    {
        std::array<uint8_t, 256> m_state;
        uint8_t m_x, m_y;

    public:
        rc4() = delete;
        rc4(const void* key, size_t size);
        rc4(const rc4&) = delete;
        rc4(rc4&&) = delete;

        void transform(const void* inbuf, void* outbuf, size_t size);
    };

    std::array<uint32_t, 5> sha0_buffer(const void* data, size_t size);
    std::array<uint32_t, 5> sha1_buffer(const void* data, size_t size);
    std::string sha0_string(const void* data, size_t size);
    std::string sha1_string(const void* data, size_t size);
};
