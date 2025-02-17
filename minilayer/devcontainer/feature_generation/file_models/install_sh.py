import logging
from typing import Dict, Optional, Union

from easyfs import File

from minilayer.devcontainer.models.devcontainer_feature_definition import (
    FeatureDependencies,
)
from minilayer.installers.devcontainer_feature.models.devcontainer_feature import (
    FeatureOption,
)

logger = logging.getLogger(__name__)


SINGLE_DEPENDENCY = """$minilayer_location \\
    install \\
    devcontainer-feature \\
    "{feature_oci}" \\
    {stringified_envs_args}
"""

HEADER = """#!/bin/bash -i

set -e

source ./library_scripts.sh

ensure_minilayer minilayer_location


{dependency_installation_lines}


{install_command}

"""


class InstallSH(File):
    REF_PREFIX = "$options."

    def __init__(
        self,
        install_command: str,
        dependencies: Optional[FeatureDependencies],
        options: Optional[Dict[str, FeatureOption]],
    ) -> None:
        self.install_command = install_command
        self.dependencies = dependencies or []
        self.options = options
        super().__init__(content=self.to_str().encode())

    def to_str(self) -> str:
        installation_lines = []
        for feature_dependency in self.dependencies:
            resolved_params = {}
            for param_name, param_value in feature_dependency.options.items():
                if isinstance(param_value, str):
                    if InstallSH.is_param_ref(param_value):
                        param_value = InstallSH.resolve_param_ref(
                            param_value, self.options
                        )

                resolved_params[param_name] = param_value
            installation_lines.append(
                self.create_install_command(feature_dependency.feature, resolved_params)
            )
        dependency_installation_lines = "\n\n".join(installation_lines)
        return HEADER.format(
            dependency_installation_lines=dependency_installation_lines,
            install_command=self.install_command,
        )

    @staticmethod
    def _escape_qoutes(value: str) -> str:
        return value.replace('"', '\\"')

    @classmethod
    def is_param_ref(cls, param_value: str) -> bool:
        return param_value.startswith(cls.REF_PREFIX)

    def create_install_command(
        self, feature_oci: str, params: Dict[str, Union[str, bool]]
    ) -> str:
        stringified_envs_args = " ".join(
            [
                f'--option {env}="{InstallSH._escape_qoutes(str(val))}"'
                for env, val in params.items()
            ]
        )

        return SINGLE_DEPENDENCY.format(
            stringified_envs_args=stringified_envs_args, feature_oci=feature_oci
        )

    @classmethod
    def resolve_param_ref(
        cls, param_ref: str, options: Optional[Dict[str, FeatureOption]]
    ) -> str:
        if options is None:
            raise ValueError(
                f"option reference was given: '{param_ref}' but no options exists"
            )

        option_name = param_ref.replace(cls.REF_PREFIX, "")

        option = options.get(option_name, None)
        if option is None:
            raise ValueError(
                f"could not resolve option reference: '{param_ref}' please ensure you spelled the option name right ({option})"
            )
        return f"${option_name}".upper()
