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
  - `--cells START-END` or `--cells N`: Execute only the cells in the specified range (1-based, inclusive).  
    - Example: `--cells 2-5` runs cells 2, 3, 4, 5.  
    - To run a single cell, use `--cells N`, e.g., `--cells 3` runs only cell 3.

- **show**  
  Displays the code of the specified code cells.  
  Options:  
  - `--cells START-END` or `--cells N`: Show only the specified code cells (1-based, inclusive).  
    - Example: `--cells 2-5` shows cells 2, 3, 4, 5.  
    - If not specified, shows all code cells.

- **edit**  
  Edit the code of a single code cell using the text editor defined by the `$EDITOR` environment variable (default: nano).  
  Options:  
  - `--cell N` (required): Edit only the specified code cell (1-based index).  
    - Example: `--cell 2` edits cell 2.  
    - You **must** specify `--cell N` (editing multiple or all cells at once is not supported).

- **info**  
  Shows notebook information: total number of cells, code cells, last modified date.

See the **Examples** section below for usage samples.

## Usage

```sh
python notebook_toolkit.py run notebook.ipynb [--timeout SECONDS] [--output FILE] [--debug] [--cells START-END|N]
python notebook_toolkit.py show notebook.ipynb [--cells START-END|N]
python notebook_toolkit.py edit notebook.ipynb --cell N
python notebook_toolkit.py info notebook.ipynb
```

### Options

- `--cells START-END` or `--cells N`  
    Select a range of code cells (1-based, inclusive).  
    Example: `--cells 2-5` selects cells 2, 3, 4, 5.  
    Example: `--cells 3` selects only cell 3.

- `--cell N`  
    Edit only the specified code cell (1-based index).  
    **Required** for `edit` command.

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
python notebook_toolkit.py run example.ipynb --cells 2-4
python notebook_toolkit.py show example.ipynb --cells 3
python notebook_toolkit.py show example.ipynb --cells 2-5
python notebook_toolkit.py show example.ipynb
python notebook_toolkit.py edit example.ipynb --cell 2
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