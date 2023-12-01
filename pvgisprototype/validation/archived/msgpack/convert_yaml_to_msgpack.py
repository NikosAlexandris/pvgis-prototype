import yaml
import msgpack

# Load YAML file
with open('parameters.yaml', 'r') as yaml_file:
    data = yaml.safe_load(yaml_file)
    print(f'Input data : {data}')

# Convert to MessagePack
with open('parameters.msgpack', 'wb') as msgpack_file:
    packed_data = msgpack.packb(data)
    msgpack_file.write(packed_data)

# Test deserialisation
try:
    with open('parameters.msgpack', 'rb') as file:
        parameters = msgpack.unpackb(file.read(), raw=False, use_list=False)
        print(f'Parameters deserialised : {parameters}')

except msgpack.exceptions.ExtraData as e:
    print("Extra data found during unpacking:", e)
    print(e.data)
