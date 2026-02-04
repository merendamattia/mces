# [1.1.0](https://github.com/merendamattia/mces/compare/v1.0.0...v1.1.0) (2026-02-04)


### Bug Fixes

* enhance algorithm selection in handleRunMces function to support connected and greedy path MCES algorithms ([6224139](https://github.com/merendamattia/mces/commit/6224139471757ae11c484972675cc8060c2f0a92))
* reduce max workers for concurrent runs from 6 to 3 for better resource management ([9aec8dc](https://github.com/merendamattia/mces/commit/9aec8dce094cfd50cfa0258321ede00d423977ba))
* update edge multipliers and increase max workers for improved benchmark performance ([125a6db](https://github.com/merendamattia/mces/commit/125a6dbf0e2394d0adf38daa361c92bc1dd79d67))


### Features

* add algorithm statistics tracking and display in frontend; enhance backend to return additional metrics ([77efb46](https://github.com/merendamattia/mces/commit/77efb462d4af9adae8635c77cfafb56ba22e96ab))
* add ilp_r2 algorithm to benchmark runner ([1514cb1](https://github.com/merendamattia/mces/commit/1514cb163fd962e356f22e23b66d1c760732e0c2))
* add plot generation script for benchmark results visualization ([4c1ec1b](https://github.com/merendamattia/mces/commit/4c1ec1b62e62f85ca6616610b8f3c660f74cee5b))
* add simulated annealing algorithm to benchmark runner ([3584406](https://github.com/merendamattia/mces/commit/35844060d61334900cb4c3d3c1938708ca94eb7f))
* add simulated annealing MCES algorithm and corresponding API endpoint ([391dbc7](https://github.com/merendamattia/mces/commit/391dbc7d28b5361c72fffcd570acb8248b7b7df1))
* add thread-safe printing for benchmark progress and results ([5be115b](https://github.com/merendamattia/mces/commit/5be115b78cae5efbc71c7976a35f3986cbdc4e81))
* enhance algorithm statistics display with improved styling and consistent table formatting ([2f810aa](https://github.com/merendamattia/mces/commit/2f810aafef03e44a06dc22467fd7e56079e8cd1e))
* enhance benchmark output with thread-safe printing and status updates ([49ba2c5](https://github.com/merendamattia/mces/commit/49ba2c5fd9d0bd0487191d7c0b02916da85da6e0))
* enhance solution optimality check in ilp_r2_mces function ([610e777](https://github.com/merendamattia/mces/commit/610e7773115c6aa20d2c238881c2546385eb2778))
* implement benchmark runner for MCES algorithms with CSV output and configurable parameters ([19b0350](https://github.com/merendamattia/mces/commit/19b035038947f8749afdeddba8bc24799ec6eb08))
* implement connected and greedy path MCES algorithms; update API and frontend for new functionalities ([34dbc85](https://github.com/merendamattia/mces/commit/34dbc85ab65303d3b656ccb03e7a8073be06eecc))
* implement ILP R2 algorithm for MCES and add API endpoint ([7e70624](https://github.com/merendamattia/mces/commit/7e706248a099764ef88072ccd1a1579d7b62aa23))
* refactor benchmark execution to use ThreadPoolExecutor for concurrent algorithm runs ([c310283](https://github.com/merendamattia/mces/commit/c3102830c5412fb5d0d081e1d4b92e5ddb3939e9))

# 1.0.0 (2025-12-21)


### Features

* add Docker support with multi-stage builds for backend and frontend, including health checks and nginx configuration ([6a2bf2f](https://github.com/merendamattia/mces/commit/6a2bf2fa3d61ee02a247bb51300e1f1230a9684d))
* add initial implementation of MCES visualizer with graph generation and rendering ([eb99289](https://github.com/merendamattia/mces/commit/eb99289319473223adecefcaaea35afe9f5af47f))
* enhance algorithm results display with improved layout and styling ([cabbd59](https://github.com/merendamattia/mces/commit/cabbd598e211538b166c073990b732a21b3684ed))
* enhance graph rendering and algorithm execution with improved documentation and layout handling ([70b88b5](https://github.com/merendamattia/mces/commit/70b88b5ee104dfb39f674145abe194403133d3a5))
* enhance result graphs styling with improved layout and visual effects ([998c85c](https://github.com/merendamattia/mces/commit/998c85c0428f6a596982db505e4395f35514ad1e))
* enhance UI styling and add footer with version info and links ([47d3823](https://github.com/merendamattia/mces/commit/47d38232a23ccfde1f3721d84e63b4d32673cd16))
* implement MCES algorithms with API integration and UI controls ([05c7827](https://github.com/merendamattia/mces/commit/05c78270d1a7f0cf365583e14be998f2f69e8836))
* improve random graph generation to ensure connectivity and edge constraints ([b13bfd9](https://github.com/merendamattia/mces/commit/b13bfd91ec4927b98352673779f902473cfde4c4))
* update edge color handling and improve highlight styling in graph rendering ([fdc734e](https://github.com/merendamattia/mces/commit/fdc734e8705f9ca6f5d99af7648e942d9a18892a))
* update graph controls and visualization layout for improved user interaction ([886757e](https://github.com/merendamattia/mces/commit/886757eb4707d982508d57100d161e0fb52da7dc))
