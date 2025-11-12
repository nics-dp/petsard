本專案遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

所有重要的變更都會記錄在此檔案中。

<!-- version list -->

## [1.9.0](https://github.com/nics-dp/petsard/compare/v1.8.1...v1.9.0) (2025-10-20)

### Features

* **metadater**: detect duplicate attributes in schema YAML ([103a62d](https://github.com/nics-dp/petsard/commit/103a62dc))
* **adapter**: auto-update schema stats across data processing pipeline ([93f254c](https://github.com/nics-dp/petsard/commit/93f254cb))
* **reporter**: add properties filter for save_schema ([6f78a84](https://github.com/nics-dp/petsard/commit/6f78a845))
* **reporter**: add save_schema method to export module schemas ([a71b4f7](https://github.com/nics-dp/petsard/commit/a71b4f73))
* **metadater**: add automatic numeric precision tracking across pipeline ([9c44f81](https://github.com/nics-dp/petsard/commit/9c44f812))

### Bug Fixes

* **schema**: handle missing field names and int type conversion errors ([094f9c2](https://github.com/nics-dp/petsard/commit/094f9c22))
* **reporter**: remove duplicate brackets in granularity output names ([3cb9a80](https://github.com/nics-dp/petsard/commit/3cb9a800))
* **splitter**: use round() for accurate train split ratio ([a7023ea](https://github.com/nics-dp/petsard/commit/a7023eab))

### Documentation

* **preprocessor**: add English docs and update zh-TW ([b13ef66](https://github.com/nics-dp/petsard/commit/b13ef667))
* **preprocessor**: clarify nullable attribute handling in missing value processing ([2b569c6](https://github.com/nics-dp/petsard/commit/2b569c6a))
* **reporter**: add save_validation docs and fix filename format ([3a15aea](https://github.com/nics-dp/petsard/commit/3a15aea0))
* **petsard-yaml**: add depth-first execution explanation with diagram ([eb36ae9](https://github.com/nics-dp/petsard/commit/eb36ae95))
* **constrainer-yaml**: add constraints file example with detailed explanations ([4b05bdd](https://github.com/nics-dp/petsard/commit/4b05bdd2))
* **getting-started**: standardize tutorial titles and fix schema links ([7354fa7](https://github.com/nics-dp/petsard/commit/7354fa76))
* **evaluator**: split workflow into modular diagrams ([507aba5](https://github.com/nics-dp/petsard/commit/507aba5f))
* **installation**: remove duplicate content from docker-build guide ([5e707cb](https://github.com/nics-dp/petsard/commit/5e707cb3))

## [1.8.1](https://github.com/nics-dp/petsard/compare/v1.7.0...v1.8.1) (2025-10-18)

### Bug Fixes

* **ci**: extract version from git tag for package build ([f159bb2](https://github.com/nics-dp/petsard/commit/f159bb23))
* **release**: add all angular commit types to patch_tags for automatic versioning ([ba98f49](https://github.com/nics-dp/petsard/commit/ba98f497))

### Documentation

* add comment to version field in pyproject.toml ([13ac852](https://github.com/nics-dp/petsard/commit/13ac8520))
* **glossary**: add 41 terms and standardize formatting ([2696d24](https://github.com/nics-dp/petsard/commit/2696d24f))
* **getting-started**: add synthesis tutorial guides ([a6c3c27](https://github.com/nics-dp/petsard/commit/a6c3c279))
* **python-api**: remove internal links and See Also sections ([ef95531](https://github.com/nics-dp/petsard/commit/ef95531b))
* **installation**: add installation guides ([af63cde](https://github.com/nics-dp/petsard/commit/af63cdeb))

### Build System

* add git verify config and PEP 440 version docs ([c46ff3d](https://github.com/nics-dp/petsard/commit/c46ff3d0))

### Tests

* align tests with implementation changes ([1e57879](https://github.com/nics-dp/petsard/commit/1e578795))

### Continuous Integration

* **test-suite**: improve report readability ([86bd47c](https://github.com/nics-dp/petsard/commit/86bd47cd))

## [1.7.0](https://github.com/nics-dp/petsard/compare/v1.6.0...v1.7.0) (2025-09-17)

### Features

* **synthesizer**: add universal precision rounding for all synthesizers ([6a37b50](https://github.com/nics-dp/petsard/commit/6a37b50c))
* **metadater**: add comprehensive statistics support with dedicated stats module ([163618d](https://github.com/nics-dp/petsard/commit/163618d0))

### Bug Fixes

* **synthesizer**: add enforce_rounding to SDV synthesizers for precision handling ([327f4e3](https://github.com/nics-dp/petsard/commit/327f4e3a))
* Add automatic dtype alignment in EvaluatorAdapter to handle type mismatches ([2ec8d6b](https://github.com/nics-dp/petsard/commit/2ec8d6bd))
* **synthesizer**: refactor SDV integration with proper Schema conversion ([8c34248](https://github.com/nics-dp/petsard/commit/8c34248e))
* **synthesizer**: correct SchemaMetadater.to_sdv() method calls for new Schema architecture ([8c945610](https://github.com/nics-dp/petsard/commit/8c945610))
* **processor**: adapt Processor to new Schema architecture with attributes-based metadata ([71626d6](https://github.com/nics-dp/petsard/commit/71626d6f))
* **splitter**: adapt Splitter to new Schema architecture and fix metadata handling ([be13812](https://github.com/nics-dp/petsard/commit/be13812f))
* **loader**: resolve FrozenInstanceError and mixed data type handling in new Metadater architecture ([05db90c](https://github.com/nics-dp/petsard/commit/05db90c3))
* remove duplicate from_data method in Metadater class ([dc035a2](https://github.com/nics-dp/petsard/commit/dc035a2e))
* **linting**: resolve ruff errors ([82cdc1e](https://github.com/nics-dp/petsard/commit/82cdc1ef))

### Refactor

* move stats calculation logic to Metadater classes ([195a909](https://github.com/nics-dp/petsard/commit/195a909b))
* **status**: replace MetadataChange with Metadata diff tracking ([3d8f052](https://github.com/nics-dp/petsard/commit/3d8f052b))
* **metadater**: migrate to new three-layer unified architecture ([6ce90a2](https://github.com/nics-dp/petsard/commit/6ce90a21))

### Documentation

* add statistics documentation and reorganize glossary ([dc035a2](https://github.com/nics-dp/petsard/commit/dc035a2e))

### Continuous Integration

* semantic-release not to cache uv ([b4bbc62](https://github.com/nics-dp/petsard/commit/b4bbc628))
* Modify semantic-release workflow configuration ([f6ff7db](https://github.com/nics-dp/petsard/commit/f6ff7db8))
* add uv.lock ([67b47c3](https://github.com/nics-dp/petsard/commit/67b47c30))

## [1.6.0](https://github.com/nics-dp/petsard/compare/v1.5.1...v1.6.0) (2025-08-06)

### Features

* **deps**: reorganize dependency groups for PyPI compatibility ([d71190d](https://github.com/nics-dp/petsard/commit/d71190db))
* **reporter**: Add naming_strategy parameter for flexible filename formats ([2ceb7697](https://github.com/nics-dp/petsard/commit/2ceb7697))
* Refactor Reporter architecture to functional design with multi-granularity support ([b9d6cd5](https://github.com/nics-dp/petsard/commit/b9d6cd5c))

### Refactor

* **status**: Restructure Status module architecture and simplify core objects ([3aca604](https://github.com/nics-dp/petsard/commit/3aca6045))
* **status**: improve error handling and eliminate code duplication ([aae4733](https://github.com/nics-dp/petsard/commit/aae47331))
* **status**: diagnose and optimize core architecture with memory-safe containers ([1aa0502](https://github.com/nics-dp/petsard/commit/1aa05022))
* **reporter**: implement functional design with centralized status management ([ab85fcb](https://github.com/nics-dp/petsard/commit/ab85fcbd))
* **reporter**: eliminate hard-coded dependencies and unify enum mapping patterns ([3cd96ce](https://github.com/nics-dp/petsard/commit/3cd96cee))
* **reporter**: split monolithic file and improve SRP compliance ([73fc902](https://github.com/nics-dp/petsard/commit/73fc9023))

### Bug Fixes

* Fix AI Development Compliance Check workflow failure ([e192038](https://github.com/nics-dp/petsard/commit/e1920386))

### Tests

* Update Reporter tests for functional design and multi-granularity support ([8d4254c](https://github.com/nics-dp/petsard/commit/8d4254cc))
* enhance GitHub Actions test suite with detailed reporting and coverage analysis ([5137200](https://github.com/nics-dp/petsard/commit/51372009))

### Continuous Integration

* improve pytest reporting with detailed failure information and test statistics ([e192038](https://github.com/nics-dp/petsard/commit/e1920386))
* add comprehensive Ruff code quality checks to test suite ([b71a108](https://github.com/nics-dp/petsard/commit/b71a1088))

## [1.5.1](https://github.com/nics-dp/petsard/compare/v1.5.0...v1.5.1) (2025-07-24)

### Bug Fixes

* **container**: update `pyproject.toml` for container building ([368092d](https://github.com/nics-dp/petsard/commit/368092dc))
* resolve merge conflicts ([9140af0](https://github.com/nics-dp/petsard/commit/9140af0c))

### Documentation

* **demo**: update default synthesis reporter source to Postprocessor ([85b8aa7](https://github.com/nics-dp/petsard/commit/85b8aa72))
* consolidate functional design files into centralized .ai structure ([d0e284c](https://github.com/nics-dp/petsard/commit/d0e284c5))

## [1.5.0](https://github.com/nics-dp/petsard/compare/v1.4.0...v1.5.0) (2025-07-16)

### Features

* **docker**: add unified dev/prod environment management ([feb087d](https://github.com/nics-dp/petsard/commit/feb087d3))
* add Docker containerization support ([269d444](https://github.com/nics-dp/petsard/commit/269d4440))
* **constrainer**: add FieldProportionsConstrainer implementation ([0ef6c56](https://github.com/nics-dp/petsard/commit/0ef6c567))

### Bug Fixes

* **docker**: optimize build architecture and remove legacy files ([3271448](https://github.com/nics-dp/petsard/commit/3271448e))

### Documentation

* **docker**: update documentation for new build architecture and commands ([82d9e6c](https://github.com/nics-dp/petsard/commit/82d9e6c7))
* add Docker usage tutorials ([d0eb086](https://github.com/nics-dp/petsard/commit/d0eb0862))
* add Docker development guide ([f5da6e9](https://github.com/nics-dp/petsard/commit/f5da6e90))
* update constrainer documentation ([4853898](https://github.com/nics-dp/petsard/commit/4853898b))
* remove unused functional_design.md ([fc84069](https://github.com/nics-dp/petsard/commit/fc840e68))

### Tests

* add comprehensive field_proportions tests ([0ef6c56](https://github.com/nics-dp/petsard/commit/0ef6c567))

### Build System

* update python version constraint and maintainer info ([f028f86](https://github.com/nics-dp/petsard/commit/f028f86b))
* remove obsolete trusted publishing setup documentation ([d26e7f8](https://github.com/nics-dp/petsard/commit/d26e7f8c))

## [1.4.0](https://github.com/nics-dp/petsard/compare/v1.3.1...v1.4.0) (2025-07-02)

### Features

* **evaluator**: integrate mpUCCs evaluator into PETsARD system ([2f80678](https://github.com/nics-dp/petsard/commit/2f806788))
* **operator**: add timing functionality and documentation ([89b4396](https://github.com/nics-dp/petsard/commit/89b43966))
* redesign Status with Metadater integration ([ebafc67](https://github.com/nics-dp/petsard/commit/ebafc67b))

### Refactor

* **splitter**: implement functional programming with overlap control ([3410ae9](https://github.com/nics-dp/petsard/commit/3410ae93))

### Build System

* migrate to PyPI Trusted Publishing for secure automated releases ([c55788a](https://github.com/nics-dp/petsard/commit/c55788aa))

### Documentation

* add v1.4.0 release notes ([c984f5e](https://github.com/nics-dp/petsard/commit/c984f5ed))

## [1.3.1](https://github.com/nics-dp/petsard/compare/v1.3.0...v1.3.1) (2025-04-18)

### Build System

* update dependency for security and SBOM alerts ([2191003](https://github.com/nics-dp/petsard/commit/2191003e), [1bad385](https://github.com/nics-dp/petsard/commit/1bad3854))

### Continuous Integration

* config update ([c7c1377](https://github.com/nics-dp/petsard/commit/c7c1377d))
* update `pages` ci deps ([ad79153](https://github.com/nics-dp/petsard/commit/ad79153c))
* remove python deps test ci ([9e21ecf](https://github.com/nics-dp/petsard/commit/9e21ecf2))
* update semantic-release action ([142ec94](https://github.com/nics-dp/petsard/commit/142ec94d))
* set dependabot as version updater ([65cda6e](https://github.com/nics-dp/petsard/commit/65cda6e4))
* update trigger ([4e19d56](https://github.com/nics-dp/petsard/commit/4e19d56d))
