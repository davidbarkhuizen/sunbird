import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.mark.skipif(shutil.which('g++') is None, reason='needs g++')
def test_firmware_logic(tmp_path):
    exe = tmp_path / 'test_sssp'
    subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', '-o', str(exe),
                    str(ROOT / 'tests' / 'firmware' / 'test_sssp.cpp')], check=True)
    result = subprocess.run([str(exe)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
