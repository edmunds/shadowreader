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
from os import getenv
from os import path

import yaml
from collections import defaultdict
import importlib
import pkgutil

from classes.exceptions import InvalidLambdaEnvVarError


def load_yml_config(*, file: str, key: str) -> dict:
    """ Load shadowreader.yml file which specified configs for Shadowreader """
    files_to_try = [
        f'{file}',
        f'../{file}',
    ]
    for f in files_to_try:
        if path.isfile(f):
            file = open(f'{f}')
    data_map = yaml.safe_load(file)
    file.close()

    sr = data_map[key]

    return sr


def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


class Plugins:
    def __init__(self):
        self.sr_config = load_yml_config(file='shadowreader.yml', key='config')
        self.env_vars = self._init_env_vars(self.sr_config)

        plugins_location = self.sr_config['plugins_location']
        plugins = importlib.import_module(plugins_location)

        plugins_conf = load_yml_config(file='shadowreader.yml', key='plugins')

        stage = self.env_vars['stage']

        plugin_files = {
            name: name
            for finder, name, ispkg in iter_namespace(plugins)
        }

        self.plugins_conf = self._parse_plugins_conf(
            plugins_conf=plugins_conf,
            stage=stage,
            plugins_location=plugins_location)

        try:
            sr_plugs = defaultdict(str)
            for key, val in self.plugins_conf.items():
                sr_plugs[key] = plugin_files[val]
        except KeyError as e:
            raise ImportError(
                f'Failed to import plugin: \'{key}\', while looking for module: {e}'
            )
        self.sr_plugs = sr_plugs

    def _parse_plugins_conf(self, *, plugins_conf: dict, stage: str,
                            plugins_location: str):

        plugins_conf = self._identify_plugins_w_stage(
            plugins_conf=plugins_conf, stage=stage)

        plugins_conf = {
            key: f'{plugins_location}.{val}'
            for key, val in plugins_conf.items()
        }
        return plugins_conf

    def _identify_plugins_w_stage(self, *, plugins_conf: dict, stage: str):
        for plugin, val in plugins_conf.items():
            if 'stage' in val:
                plugins_conf[plugin] = val['stage'][stage]
        return plugins_conf

    def exists(self, plugin_name: str) -> bool:
        if plugin_name in self.sr_plugs:
            return True
        else:
            return False

    def load(self, plugin_name: str):
        plugin_location = self.sr_plugs[plugin_name]
        plugin = importlib.import_module(plugin_location)
        return plugin

    def _init_env_vars(self, sr_config):
        env_vars_to_get = sr_config['env_vars_to_get']
        env_vars = {}
        for env_var in env_vars_to_get:
            env_vars[env_var] = getenv(env_var, '')

        important_env_vars = ['region', 'stage']
        for env_var, val in env_vars.items():
            if env_var in important_env_vars and not val:
                msg = f'Invalid Lambda environment variable detected. env_var: {env_var}, env var val: {val}'
                raise InvalidLambdaEnvVarError(msg)

        return env_vars


sr_plugins = Plugins()
sr_config = sr_plugins.sr_config
env_vars = sr_plugins.env_vars
