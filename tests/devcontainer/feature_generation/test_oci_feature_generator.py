import os
import pathlib

import pytest
from helpers import RESOURCE_DIR

from minilayer.devcontainer.feature_generation.oci_feature_generator import (
    OCIFeatureGenerator,
)

FEATURE_DEFINITION_DIR = os.path.join(RESOURCE_DIR, "test_feature_definitions")


TEST_IMAGE = "mcr.microsoft.com/devcontainers/base:debian"


@pytest.mark.parametrize(
    "feature_id,feature_definition_dir,release_version",
    [
        (v, os.path.join(FEATURE_DEFINITION_DIR, v), "v0.3.7rc7")
        for v in os.listdir(FEATURE_DEFINITION_DIR)
    ],
)
def test_feature_dir_generation(
    shell,
    tmp_path: pathlib.Path,
    feature_id: str,
    feature_definition_dir: str,
    release_version: str,
) -> None:
    feature_definition = os.path.join(feature_definition_dir, "feature-definition.json")

    tmp_path_str = tmp_path.as_posix()
    OCIFeatureGenerator.generate(
        feature_definition=feature_definition,
        output_dir=tmp_path.as_posix(),
        release_version=release_version,
    )

    assert os.path.isfile(
        os.path.join(tmp_path_str, "test", feature_id, "scenarios.json")
    )
    assert os.path.isfile(
        os.path.join(tmp_path_str, "src", feature_id, "library_scripts.sh")
    )
    assert os.path.isfile(
        os.path.join(tmp_path_str, "src", feature_id, "devcontainer-feature.json")
    )
    assert os.path.isfile(os.path.join(tmp_path_str, "src", feature_id, "install.sh"))


@pytest.mark.parametrize(
    "feature_id,feature_definition_dir,release_version",
    [
        (v, os.path.join(FEATURE_DEFINITION_DIR, v), "v0.3.7rc7")
        for v in os.listdir(FEATURE_DEFINITION_DIR)
    ],
)
def test_feature_dir_generation_and_run_devcontainer_tests(
    shell,
    tmp_path: pathlib.Path,
    feature_id: str,
    feature_definition_dir: str,
    release_version: str,
) -> None:
    feature_definition = os.path.join(feature_definition_dir, "feature-definition.json")

    tmp_path_str = tmp_path.as_posix()
    OCIFeatureGenerator.generate(
        feature_definition=feature_definition,
        output_dir=tmp_path_str,
        release_version=release_version,
    )
    response = shell.run(
        f"BUILDKIT_PROGRESS=plain devcontainer features test -p {tmp_path_str} -f {feature_id} --skip-autogenerated",
        shell=True,
    )
    print(response.stdout)
    print(response.stderr)

    assert response.exitcode == 0
