# cpm: The Chromos Project Manager  ![CI](https://github.com/jorsanpe/cpm/workflows/CI/badge.svg)
A modern project management tool for C/C++ projects.

The [docs](https://github.com/jorsanpe/cpm/wiki) are currently maintained in the repository wiki.

## Installation
`pip3 install cpm-cli`

CPM depends on [CMake](https://cmake.org/) and [ninja](https://ninja-build.org/) for the build process.

## Getting started
```
cpm create DeathStartLaserBackend
cd DeathStartLaserBackend
cpm build
```

After creating the project, the binary will be available in the project root directory. 
```
./DeathStartLaserBackend
```

### Manage dependencies
CPM manages your project dependencies through CPM-Hub. In order to install a package, simply run:

```
cpm install R2D2-API
```

### Run your tests
```
cpm test
```

Test sources reside in the `tests` directory. They are found recursively from the root directory
 using the expression `test_*.cpp`.
