# token_world

[![codecov](https://codecov.io/gh/reubenjohn/token_world/branch/main/graph/badge.svg?token=token_world_token_here)](https://codecov.io/gh/reubenjohn/token_world/branch/main)
[![CI](https://github.com/reubenjohn/token_world/actions/workflows/main.yml/badge.svg)](https://github.com/reubenjohn/token_world/actions/workflows/main.yml)

## Usage

```py
from token_world import BaseClass
from token_world import base_function

BaseClass().base_method()
base_function()
```

```bash
$ python -m token_world
#or
$ token_world
```

## Setup

For instructions on setting up the project for development and contributions, see [CONTRIBUTING.md](CONTRIBUTING.md)

To set up the environment variables, create a `.env` file in the root directory of your project and add the following lines:

```shell
OPENAI_BASE_URL=http://192.168.1.199:11434/v1
OPENAI_API_KEY=your_openai_api_key_here
```

Alternatively, you can provide the `--openai_base_url` and `--openai_api_key` arguments when running the CLI:

```bash
$ python -m token_world --openai_base_url http://192.168.1.199:11434/v1 --openai_api_key your_openai_api_key_here
#or
$ token_world --openai_base_url http://192.168.1.199:11434/v1 --openai_api_key your_openai_api_key_here
```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
