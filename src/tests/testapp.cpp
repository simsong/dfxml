#include "config.h"
#include <gtest/gtest.h>
#include "../hash_t.h"

using namespace std;

const uint8_t nulls[512] = {0};

TEST(hash_t, sha1_t) {

    /* First test the operation of the digest function */
    uint8_t buf20[20] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19};
    ASSERT_EQ(sizeof(buf20),20);
    ASSERT_EQ(buf20[5], 5);
    sha1_t v20(buf20);
    for(int i=0;i<20;i++){
        ASSERT_EQ(v20.digest[i], i);
    }
}

TEST(hash_t, hash_md5_empty) {
    md5_t val = md5_generator::hash_buf(nulls,0);
    ASSERT_EQ(val.hexdigest(), "d41d8cd98f00b204e9800998ecf8427e");
}

TEST(hash_t, hash_sha1_empty) {
    sha1_t val = sha1_generator::hash_buf(nulls,0);
    ASSERT_EQ(val.hexdigest(), "da39a3ee5e6b4b0d3255bfef95601890afd80709");
}

TEST(hash_t, hash_sha256_empty) {
    sha256_t val = sha256_generator::hash_buf(nulls,0);
    ASSERT_EQ(val.hexdigest(), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
}

TEST(hash_t, hash_sha512_empty) {
    sha512_t val = sha512_generator::hash_buf(nulls,0);
    ASSERT_EQ(val.hexdigest(), "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e");
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

