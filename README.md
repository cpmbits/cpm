# cpm: The Chromos Project Manager
A modern project management tool for C/C++ projects.

## Installation
`pip3 install cpm`

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

## Manage dependencies
CPM manages your project dependencies through CPM-Hub. In order to install a package, simply run:

```
cpm install R2D2-API
```

## Run your tests
```
cpm test
```

Test sources reside in the `tests` directory. They are found recursively from the root directory
 using the expression `test_*.cpp`.
