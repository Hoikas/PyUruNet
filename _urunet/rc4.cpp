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

#include "urunet.h"

// ==============================================================================

urunet::rc4::rc4(const void* key, size_t size)
    : m_x(), m_y()
{
    for (size_t i = 0; i < std::size(m_state); ++i)
        m_state[i] = i;

    const uint8_t* keybuf = reinterpret_cast<const uint8_t*>(key);
    uint8_t x = 0;
    for (size_t i = 0; i < std::size(m_state); ++i) {
        x = keybuf[i % size] + m_state[i] + x;
        std::swap(m_state[i], m_state[x]);
    }
}

void urunet::rc4::transform(const void* in, void* out, size_t size)
{
    const uint8_t* inptr = reinterpret_cast<const uint8_t*>(in);
    uint8_t* outptr = reinterpret_cast<uint8_t*>(out);

    while (size > 0) {
        m_x += 1;
        m_y += m_state[m_x];
        std::swap(m_state[m_x], m_state[m_y]);
        *outptr++ = (*inptr++) ^ m_state[(m_state[m_x] + m_state[m_y]) % std::size(m_state)];
        --size;
    }
}
