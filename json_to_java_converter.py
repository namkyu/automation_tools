import json


def find(dictionary):
    for k, v in dictionary.items():
        if isinstance(v, dict):
            for result_key, result_value in find(v):
                yield result_key, result_value
        elif isinstance(v, list):
            for d in v:
                for result_key, result_value in find(d):
                    yield result_key, result_value
                break  # list는 한 번만 출력하기 위해서 break 처리
        else:
            yield k, v  # find 함수를 호출한 쪽으로 반환


def convert(word):
    return word.split('_')[0] + ''.join(x.capitalize() or '_' for x in word.split('_')[1:])


def print_prop(primitive_type, prop, json_key):
    print('@JsonProperty("' + json_key + '")')
    print('private %s %s;\n' % (primitive_type, prop))


file = open("file/test.json", encoding="UTF8")
json = json.load(file)
file.close()

for key, value in list(find(json)):
    prop_name = convert(key)
    if isinstance(value, bool):
        print_prop("Boolean", prop_name, key)
    elif isinstance(value, (float, int)):
        print_prop("Integer", prop_name, key)
    else:
        print_prop("String", prop_name, key)
