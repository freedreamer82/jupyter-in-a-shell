# notebook_toolkit.py

Robust and sequential execution of Jupyter notebooks from the command line, with optional file logging.

## Features

- Executes all cells of a `.ipynb` notebook in order.
- Supports per-cell timeout.
- Saves output to a file or prints to console.
- Interactive error and interruption handling.
- Debug mode with stacktrace.

## Commands

- **run**  
  Executes all code cells in the notebook sequentially.  
  Options:  
  - `--timeout`, `-t`: Timeout per each cell (in seconds, 0 = no timeout)  
  - `--output`, `-o`: Save output to a file instead of printing to console  
  - `--debug`: Show detailed information in case of errors

- **show [CELL_NUM]**  
  Displays the code of a specific cell (`CELL_NUM`, 1-based), or all code cells if no number is provided.

- **edit CELL_NUM**  
  Edit the code of cell number `CELL_NUM` (1-based) using the text editor defined by the `$EDITOR` environment variable (default: nano).

- **info**  
  Shows notebook information: total number of cells, code cells, last modified date.

See the **Examples** section below for usage samples.

## Usage

```sh
python notebook_toolkit.py run notebook.ipynb [--timeout SECONDS] [--output FILE] [--debug]
python notebook_toolkit.py show [CELL_NUM] notebook.ipynb
python notebook_toolkit.py edit CELL_NUM notebook.ipynb
python notebook_toolkit.py info notebook.ipynb
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
python notebook_toolkit.py run example.ipynb
python notebook_toolkit.py run example.ipynb --timeout 1800
python notebook_toolkit.py run example.ipynb --output log.txt --debug
python notebook_toolkit.py show 2 example.ipynb
python notebook_toolkit.py show example.ipynb
python notebook_toolkit.py edit 2 example.ipynb
python notebook_toolkit.py info example.ipynb
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