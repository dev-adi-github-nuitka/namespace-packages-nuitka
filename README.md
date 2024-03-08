# namespace-packages-nuitka

A minimal reproducible example project demonstrating namespace packages in Nuitka

Version info: Python compilation with Nuitka '2.1' on Python '3.9' commercial grade 'not installed'.

## Instructions for Reproducing

### Before: Setuptools Compilation

Begin at the root of the project

1. Create a new virtual environment and upgrade pip
1. Run `pip install ./src/pkg1` and `pip install ./src/pkg2`
1. Run `pip install .`
1. Run `python -m main`. You should get output like the below:

    ```shell
    Thing One
    Thing Two
    _NamespacePath(['./Code/namespace-packages-nuitka/.venv/lib/python3.9/site-packages/shared_ns'])
    ```

#### After: Nuitka Compilation

Begin at root of project

1. Create a new virtual environment, upgrade pip and pip install `build`
1. Change each of the `pyproject.toml`s so they have the following `[build-system]` section

    ```toml
    [build-system]
    requires = [
        "setuptools==64.0.0",
        "wheel==0.37.1",
        "nuitka",
        "toml",
        "build"
    ]
    build-backend = "nuitka.distutils.Build"
    ```

1. Build each project (`.`, `./src/pkg1`, `./src/pkg2`) using `python -m build`
1. Install each project from the wheels you created
1. Run `python -c "from main import run; run()"`
1. Notice you get the following output:

    ```shell
    Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "./namespace-packages-nuitka/.venv/lib/python3.9/site-packages/main.py", line 2, in <module main>
    ModuleNotFoundError: No module named 'shared_ns.thing1'
    ```

1. Now re-install `pkg1` with the `--force-reinstall` flag and run  `python -c "from main import run; run()"` again
1. Notice now `pkg2`'s shared namespace (`thing2`) is now unavailable instead of `pkg1` like before:

    ```shell
    Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "./namespace-packages-nuitka/.venv/lib/python3.9/site-packages/main.py", line 3, in <module main>
    ModuleNotFoundError: No module named 'shared_ns.thing2'
    ```

## Other Observations

### Theory

I think that `shared_ns.cpython-39-darwin.so` is getting overwritten by both `pkg1` and `pkg2`, whichever is installed most recently. Both have the lines:

```shell
creating './namespace-packages-nuitka/src/pkg1/dist/tmp09j_4blr/pkg1-1.0.0-cp39-cp39-macosx_13_0_arm64.whl' and adding 'build/bdist.macosx-13.4-arm64/wheel' to it
adding 'shared_ns.cpython-39-darwin.so'
adding 'shared_ns.pyi'
adding 'pkg1-1.0.0.dist-info/METADATA'
adding 'pkg1-1.0.0.dist-info/WHEEL'
adding 'pkg1-1.0.0.dist-info/top_level.txt'
adding 'pkg1-1.0.0.dist-info/RECORD'
```

The actual build command being used is:

```shell
Building: 'shared_ns' with command '['/private/var/folders/sm/krx6g3v56kqdqnws07wg5_000000gn/T/build-env-t_8uv7t3/bin/python', '-m', 'nuitka', '--module', --enable-plugin=pylint-warnings', '--output-dir=/private/var/folders/sm/krx6g3v56kqdqnws07wg5_000000gn/T/build-via-sdist-wo261zre/pkg1-1.0.0/build/lib', '--nofollow-import-to=*.tests', '--remove-output', '--include-package=shared_ns', '/private/var/folders/sm/krx6g3v56kqdqnws07wg5_000000gn/T/build-via-sdist-wo261zre/pkg1-1.0.0/build/lib/shared_ns']'
```

### A Workaround

I can workaround the problem by explicitly specifying the packages in the `pyproject.toml`s:

```toml
[tool.setuptools]
packages = ["src.shared_ns.thing1"]
```

Then the build command becomes:

```shell
Building: 'src.shared_ns.thing1' with command '['/private/var/folders/sm/krx6g3v56kqdqnws07wg5_000000gn/T/build-env-21m033cz/bin/python', '-m', 'nuitka', '--module','--enable-plugin=pylint-warnings','--output-dir=/private/var/folders/sm/krx6g3v56kqdqnws07wg5_000000gn/T/build-via-sdist-o17twzlu/pkg1-1.0.0/build/lib/src/shared_ns', '--nofollow-import-to=*.tests','--remove-output', '--include-package=thing1','/private/var/folders/sm/krx6g3v56kqdqnws07wg5_000000gn/T/build-via-sdist-o17twzlu/pkg1-1.0.0/build/lib/src/shared_ns/thing1']'
```

and the shared object is:

```shell
adding 'src/shared_ns/thing1.cpython-39-darwin.so'
adding 'src/shared_ns/thing1.pyi'
```

And the namespace functionality works again. But this is slightly difficult to maintain, especially if there are a lot of sub-packages that all need to be listed. Also, I tried using [Custom Discovery](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#custom-discovery) but that also doesn't work.
