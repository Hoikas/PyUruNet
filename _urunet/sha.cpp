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

#include <bit>
#include <format>
#include <memory>
#include <type_traits>

#include "urunet.h"

// ==============================================================================

namespace
{
    inline uint16_t swap_big_endian(uint16_t value)
    {
        if constexpr (std::endian::native == std::endian::big)
            return value;

#ifdef _MSC_VER
        return _byteswap_ushort(value);
#else
        return __builtin_bswap16(value);
#endif
    }

    inline uint32_t swap_big_endian(uint32_t value)
    {
        if constexpr (std::endian::native == std::endian::big)
            return value;

#ifdef _MSC_VER
        return _byteswap_ulong(value);
#else
        return __builtin_bswap32(value);
#endif
    }

    inline uint64_t swap_big_endian(uint64_t value)
    {
        if constexpr (std::endian::native == std::endian::big)
            return value;

#ifdef _MSC_VER
        return _byteswap_uint64(value);
#else
        return __builtin_bswap64(value);
#endif
    }

    enum class Sha
    {
        e_Sha0,
        e_Sha1,
    };

    template<Sha _HashT>
    inline std::array<uint32_t, 5> hs_internal_sha(const void* data, size_t size)
    {
        // This algorithm was C++20-ized from Zrax's implementation found
        // in libHSPlasma.

        std::array<uint32_t, 5> hash{
            0x67452301,
            0xefcdab89,
            0x98badcfe,
            0x10325476,
            0xc3d2e1f0
        };

        uint8_t stack_buffer[256];
        std::unique_ptr<uint8_t[]> heap_buffer;
        uint8_t* bufp;

        // Preprocess the message to pad it to a multiple of 512 bits,
        // with the (Big Endian) size in bits tacked onto the end.
        uint64_t buf_size = size + 1 + sizeof(uint64_t);
        if ((buf_size % 64) != 0)
            buf_size += 64 - (buf_size % 64);
        if (buf_size > sizeof(stack_buffer)) {
            heap_buffer = std::make_unique<uint8_t[]>(buf_size);
            bufp = heap_buffer.get();
        } else {
            bufp = stack_buffer;
        }

        memcpy(bufp, data, size);
        memset(bufp + size, 0, buf_size - size);
        bufp[size] = 0x80;  // Append '1' bit to the end of the message
        uint64_t msg_size_bits = static_cast<uint64_t>(size) * 8;
        msg_size_bits = swap_big_endian(msg_size_bits);
        memcpy(bufp + buf_size - sizeof(msg_size_bits),
            &msg_size_bits, sizeof(msg_size_bits));

        uint8_t* end = bufp + buf_size;
        uint32_t work[80];
        while (bufp < end) {
            memcpy(work, bufp, 64);
            bufp += 64;

            for (size_t i = 0; i < 16; ++i)
                work[i] = swap_big_endian(work[i]);

            for (size_t i = 16; i < 80; ++i) {
                // SHA-1 difference: no rol32(work[i], 1)
                const uint32_t temp = work[i - 3] ^ work[i - 8] ^ work[i - 14] ^ work[i - 16];
                if constexpr (_HashT == Sha::e_Sha1)
                    work[i] = std::rotl(temp, 1);
                else
                    work[i] = temp;
            }

            std::array<uint32_t, 5> hv = hash;

            // Main SHA loop
            for (size_t i = 0; i < 20; ++i) {
                constexpr uint32_t K = 0x5a827999;
                const uint32_t f = (hv[1] & hv[2]) | (~hv[1] & hv[3]);
                const uint32_t temp = std::rotl(hv[0], 5) + f + hv[4] + K + work[i];
                hv[4] = hv[3];
                hv[3] = hv[2];
                hv[2] = std::rotl(hv[1], 30);
                hv[1] = hv[0];
                hv[0] = temp;
            }
            for (size_t i = 20; i < 40; ++i) {
                constexpr uint32_t K = 0x6ed9eba1;
                const uint32_t f = (hv[1] ^ hv[2] ^ hv[3]);
                const uint32_t temp = std::rotl(hv[0], 5) + f + hv[4] + K + work[i];
                hv[4] = hv[3];
                hv[3] = hv[2];
                hv[2] = std::rotl(hv[1], 30);
                hv[1] = hv[0];
                hv[0] = temp;
            }
            for (size_t i = 40; i < 60; ++i) {
                constexpr uint32_t K = 0x8f1bbcdc;
                const uint32_t f = (hv[1] & hv[2]) | (hv[1] & hv[3]) | (hv[2] & hv[3]);
                const uint32_t temp = std::rotl(hv[0], 5) + f + hv[4] + K + work[i];
                hv[4] = hv[3];
                hv[3] = hv[2];
                hv[2] = std::rotl(hv[1], 30);
                hv[1] = hv[0];
                hv[0] = temp;
            }
            for (size_t i = 60; i < 80; ++i) {
                constexpr uint32_t K = 0xca62c1d6;
                const uint32_t f = (hv[1] ^ hv[2] ^ hv[3]);
                const uint32_t temp = std::rotl(hv[0], 5) + f + hv[4] + K + work[i];
                hv[4] = hv[3];
                hv[3] = hv[2];
                hv[2] = std::rotl(hv[1], 30);
                hv[1] = hv[0];
                hv[0] = temp;
            }

            hash[0] += hv[0];
            hash[1] += hv[1];
            hash[2] += hv[2];
            hash[3] += hv[3];
            hash[4] += hv[4];
        }

        // Bring the output back to host endian
        for (size_t i = 0; i < std::size(hash); ++i)
            hash[i] = swap_big_endian(hash[i]);

        return hash;
    }

    template<Sha _HashT>
    inline std::string hs_internal_sha_string(const void* data, size_t size)
    {
        auto hashbuf = hs_internal_sha<_HashT>(data, size);
        return std::format(
            "{:08x}{:08x}{:08x}{:08x}{:08x}",
            swap_big_endian(hashbuf[0]),
            swap_big_endian(hashbuf[1]),
            swap_big_endian(hashbuf[2]),
            swap_big_endian(hashbuf[3]),
            swap_big_endian(hashbuf[4])
        );
    }
};

// ==============================================================================

std::array<uint32_t, 5> urunet::sha0_buffer(const void* data, size_t size)
{
    return hs_internal_sha<Sha::e_Sha0>(data, size);
}

std::array<uint32_t, 5> urunet::sha1_buffer(const void* data, size_t size)
{
    return hs_internal_sha<Sha::e_Sha1>(data, size);
}

std::string urunet::sha0_string(const void* data, size_t size)
{
    return hs_internal_sha_string<Sha::e_Sha0>(data, size);
}

std::string urunet::sha1_string(const void* data, size_t size)
{
    return hs_internal_sha_string<Sha::e_Sha1>(data, size);
}
