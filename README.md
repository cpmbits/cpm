# cpm: A modern project management tool for C/C++ projects  ![CI](https://github.com/jorsanpe/cpm/workflows/CI/badge.svg)

You can find the [documentation](https://cpmbits.com/documentation/getting_started.html) in the [cpmbits website](https://cpmbits.com).

## Installation
`pip3 install cpm-cli`

CPM depends on [CMake](https://cmake.org/) and [ninja](https://ninja-build.org/) for the build process.

## Getting started
```
cpm create DeathStartLaserBackend
cd DeathStartLaserBackend
cpm build
```

After creating the project, the binary will be available in the project `build` directory. 
```
./build/DeathStartLaserBackend
```

### Manage dependencies
CPM manages your project dependencies through CPM-Hub. In order to install a package, simply run:

```
cpm install cest
```

### Run your tests
```
cpm test
```

Test sources reside in the `tests` directory. `cpm` will consider as test suites any files that match the expression
`test_*.cpp`. 
