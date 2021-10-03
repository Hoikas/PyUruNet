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
#include <random>
#include <string_view>

#include "urunet.h"

#define CATCH_CONFIG_MAIN
#include <catch2/catch.hpp>

TEST_CASE("Round-trip", "[rc4]")
{
    std::random_device random;
    auto key = random();

    urunet::rc4 encrypt(&key, sizeof(key));
    urunet::rc4 decrypt(&key, sizeof(key));
    auto round_trip = [&encrypt, &decrypt](std::string_view value){
        // It's perfectly acceptable to transform in place.
        auto buf = std::make_unique<char[]>(value.size());
        encrypt.transform(value.data(), buf.get(), value.size());
        decrypt.transform(buf.get(), buf.get(), value.size());
        return std::string(buf.get(), value.size());
    };

    REQUIRE(round_trip("") == "");
    REQUIRE(round_trip("a") == "a");
    REQUIRE(round_trip("abc") == "abc");
    REQUIRE(round_trip("Боже, Царя храни!") == "Боже, Царя храни!");
}

TEST_CASE("SHA-0", "[sha]")
{
    REQUIRE(urunet::sha0_string("", 0) == "f96cea198ad1dd5617ac084a3d92c6107708c0ef");
    REQUIRE(urunet::sha0_string("abc", 3) == "0164b8a914cd2a5e74c4f7ff082c4d97f1edf880");
}

TEST_CASE("SHA-1", "[sha]")
{
    REQUIRE(urunet::sha1_string("", 0) == "da39a3ee5e6b4b0d3255bfef95601890afd80709");
    REQUIRE(urunet::sha1_string("abc", 3) == "a9993e364706816aba3e25717850c26c9cd0d89d");
}
