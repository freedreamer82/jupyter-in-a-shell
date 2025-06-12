# run_notebook.py

Robust and sequential execution of Jupyter notebooks from the command line, with optional file logging.

## Features

- Executes all cells of a `.ipynb` notebook in order.
- Supports per-cell timeout.
- Saves output to a file or prints to console.
- Interactive error and interruption handling.
- Debug mode with stacktrace.

## Usage

```sh
python run_notebook.py notebook.ipynb
```

### Options

- `--timeout`, `-t`  
    Timeout per cell in seconds (default: 0 = no timeout).  
    Example: `--timeout 3600` (1 hour per cell)

- `--output`, `-o`  
    File to save output (default: console only).  
    Example: `--output output.txt`

- `--debug`  
    Shows detailed stacktrace in case of errors.

### Examples

```sh
python run_notebook.py example.ipynb
python run_notebook.py example.ipynb --timeout 1800
python run_notebook.py example.ipynb --output log.txt --debug
```

## Notes

- Execution stops on error, prompting whether to continue.
- Output can be redirected to a file for later analysis.
- Requires Python 3 and the following packages: `nbformat`, `jupyter_client`.

## Dependencies

Install dependencies with:

```sh
pip install nbformat jupyter_client
```

## License

MIT