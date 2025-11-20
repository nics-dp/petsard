# CHANGELOG

<!-- version list -->

## v1.10.0-rc.4 (2025-11-20)

### Bug Fixes

- Correct repository check in image-publish workflow
  ([`5a97897`](https://github.com/nics-dp/petsard/commit/5a97897a045f5746d5a0c6fc49b3fc43261d9042))

- Correct repository URLs in pyproject.toml
  ([`d4a0a33`](https://github.com/nics-dp/petsard/commit/d4a0a33c414ef1557ed94421171e1c67db1fe7d7))

- **ci**: Always build and publish packages on branch push
  ([`a2dfe50`](https://github.com/nics-dp/petsard/commit/a2dfe5023c37395b7943190d3affda2532a005e5))


## v1.10.0-rc.3 (2025-11-20)

### Bug Fixes

- **ci**: Correct Python syntax in test report generation
  ([`de583e0`](https://github.com/nics-dp/petsard/commit/de583e064935d764b1c828b06afe501703d0821b))

- **logging**: Replace print statements with logger in error handling
  ([`a829bd1`](https://github.com/nics-dp/petsard/commit/a829bd1143b445aa1b869839af4cf8253865a70b))

### Chores

- **release**: Remove changelog generation
  ([`2c8ddb3`](https://github.com/nics-dp/petsard/commit/2c8ddb3ca9ff0d578d835b035ec69685c191d743))

### Code Style

- **lint**: Apply ruff safe auto-fixes
  ([`d4a36f7`](https://github.com/nics-dp/petsard/commit/d4a36f7cf041b567a0e231db5165afd1daafba03))

### Documentation

- **dev-guide**: Add navigation links to subpages
  ([`193fd5e`](https://github.com/nics-dp/petsard/commit/193fd5e051a12d0e880d6a82f5c0455fd7313a66))

- **error-handling**: Rewrite error handling guide with error-code-first approach
  ([`2cba269`](https://github.com/nics-dp/petsard/commit/2cba2695a812187f14e152fee65c3baf47e4669e))

- **i18n**: Translate Chinese comments to English
  ([`7f0fe26`](https://github.com/nics-dp/petsard/commit/7f0fe26eb64bf17f973220fa819f167faeeb98c5))

### Refactoring

- **exceptions**: Establish hierarchical exception architecture with error codes
  ([`645bd96`](https://github.com/nics-dp/petsard/commit/645bd968be4b3f1b990c404012035cce6f060c0b))

- **logging**: Optimize log levels, formatting, and timing records
  ([`6ef1830`](https://github.com/nics-dp/petsard/commit/6ef1830f3bcbae7b90db64275f581f84246b013a))

- **synthesizer**: Remove SDV dependency
  ([`adbb407`](https://github.com/nics-dp/petsard/commit/adbb40732cac8e67b0a5efa276137f7e45444440))


## v1.10.0-rc.2 (2025-11-19)

### Documentation

- **adapter-api**: Complete API reference documentation
  ([`8111da7`](https://github.com/nics-dp/petsard/commit/8111da738a5423ae35b26e11106728b554d05f1a))

- **api**: Refactor internal API docs and consolidate YAML guides
  ([`02f5089`](https://github.com/nics-dp/petsard/commit/02f50890d5585cb51c177abdc4774c8121004ac3))

- **developer-guide**: Remove deprecated guides and simplify structure
  ([`e18b8ff`](https://github.com/nics-dp/petsard/commit/e18b8ff760c8f83250db18b5d08c60082b3b24ad))

### Refactoring

- **adapter**: Consolidate common patterns and add type annotations
  ([`3fe1c04`](https://github.com/nics-dp/petsard/commit/3fe1c043eab10531f38a952acd31d80f625f394d))

- **core**: Remove eval() usage and improve code quality
  ([`8c33292`](https://github.com/nics-dp/petsard/commit/8c33292551e825db1d58257bbcaf8194ab3de19e))

- **deps**: Optimize dependency groups and update install docs
  ([`2a68acb`](https://github.com/nics-dp/petsard/commit/2a68acb142e49e9419987fe7c1814bd490755109))

### Testing

- Achieve 100% pass rate and streamline docs
  ([`056afe5`](https://github.com/nics-dp/petsard/commit/056afe52c560478c6cb425ee3bfd90c1079f8c6a))


## v1.10.0-rc.1 (2025-11-19)


## v1.9.0 (2025-10-19)


## v1.8.1 (2025-10-18)

- Initial Release
