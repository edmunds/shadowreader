"""
Copyright 2018 Edmunds.com, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
"""

from libs import zipper
import json


def test_zipping_str():
    data = 'asdf'

    zipped = zipper.compress(data=data)

    unzipped = zipper.decompress(data=zipped)

    assert unzipped == data


def test_zipping_dict():
    orig_data = {'test': 'asdasdasdasd', '1': 1, 'list': ['asdf'], 'bool': True}
    data = json.dumps(orig_data)
    zipped = zipper.compress(data=data)

    unzipped = zipper.decompress(data=zipped)
    unzipped = json.loads(unzipped)
    print(unzipped)
    print(orig_data)
    assert unzipped == orig_data
