import msgpack

# Test data
test_data = {'key1': 'value1', 'key2': [1, 2, 3]}

# Serialize the test data
packed_test_data = msgpack.packb(test_data)

# Deserialize the test data
unpacked_test_data = msgpack.unpackb(packed_test_data, raw=False, use_list=False)

print(unpacked_test_data)
