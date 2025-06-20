import sys
import time
import nbformat
from jupyter_client import KernelManager
from queue import Empty
import os
import atexit
from datetime import datetime

VERSION = "1.0.0"
AUTHOR = 'SW Engineer Garzola Marco'

def run_notebook_realtime_extended(notebook_path, cell_timeout=3600, output_file=None):
    """
    Executes a Jupyter notebook sequentially and robustly.
    
    Args:
        notebook_path: Path to the notebook
        cell_timeout: Timeout per cell (0 = no timeout)
        output_file: File to save output (None = console only)
    """
    
    # Setup output file if specified
    output_stream = None
    if output_file:
        output_stream = open(output_file, 'w', encoding='utf-8', buffering=1)
        log(f"📝 Output will be saved to: {output_file}", output_stream)
        
        devnull = open(os.devnull, 'w')
        sys.stdout = devnull
        sys.stderr = devnull
        # Cleanup: close devnull at the end of execution
        def cleanup_output():
            if output_stream and not output_stream.closed:
                output_stream.close()
            if devnull and not devnull.closed:
                devnull.close()
        atexit.register(cleanup_output)

    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    
    # Configure the kernel manager
    km = KernelManager()
    km.start_kernel()
    kc = km.client()
    kc.start_channels()
    
    # Wait for the kernel to be ready
    log("🔄 Waiting for kernel to be ready...", output_stream)
    kc.wait_for_ready(timeout=60)
    log("✅ Kernel ready!", output_stream)
    
    try:
        code_cells = [cell for cell in nb.cells if cell.cell_type == 'code' and cell.source.strip()]
        
        for i, cell in enumerate(nb.cells):
            if cell.cell_type != 'code':
                continue
                
            code = cell.source.strip()
            if not code:  # Skip empty cells
                continue
                
            cell_num = len([c for c in nb.cells[:i+1] if c.cell_type == 'code' and c.source.strip()])
            
            log(f"\n{'='*60}", output_stream)
            log(f"📋 Executing cell {cell_num}/{len(code_cells)}", output_stream)
            log(f"{'='*60}", output_stream)
            log(f"Code preview:\n{code[:300]}{'...' if len(code) > 300 else ''}", output_stream)
            log(f"{'='*60}\n", output_stream)
            
            # Execute the cell
            success = execute_cell_simple(kc, code, cell_num, cell_timeout, output_stream)
            
            if not success:
                log(f"\n❌ Cell {cell_num} failed or timed out", output_stream)
                user_input = input("\nContinue with next cell? (y/n/q): ").strip().lower()
                if user_input == 'q':
                    log("🛑 Execution stopped by user", output_stream)
                    break
                elif user_input != 'y':
                    log("🛑 Execution stopped by user", output_stream)
                    break
            else:
                log(f"\n✅ Cell {cell_num} completed successfully", output_stream)
            
    except KeyboardInterrupt:
        log("\n\n🛑 Execution interrupted by user", output_stream)
        try:
            kc.interrupt_kernel()
            time.sleep(2)
        except:
            pass
        
    finally:
        log("\n📋 Cleaning up...", output_stream)
        try:
            kc.stop_channels()
            km.shutdown_kernel()
        except:
            pass
            
        if output_stream:
            output_stream.close()
            
        log("✅ Cleanup complete", output_stream)

def execute_cell_simple(kc, code, cell_num, timeout, output_stream=None):
    """
    Simplified version that only uses execute_interactive
    """
    log(f"🚀 Starting execution at {time.strftime('%H:%M:%S')}", output_stream)
    start_time = time.time()
    
    # Create output hook that uses our logging system
    def cell_output_hook(msg):
        output_hook(msg, output_stream)
    
    try:
        # Use execute_interactive - if timeout is 0 or None, do not use timeout
        if timeout == 0 or timeout is None:
            reply = kc.execute_interactive(
                code, 
                timeout=None,  # No timeout
                output_hook=cell_output_hook,
                stdin_hook=None
            )
        else:
            reply = kc.execute_interactive(
                code, 
                timeout=timeout,
                output_hook=cell_output_hook,
                stdin_hook=None
            )
        
        elapsed = time.time() - start_time
        log(f"\n⏱️ Completed in {elapsed:.2f}s", output_stream)
        
        # Check if there were errors
        if reply['content']['status'] == 'error':
            log("❌ Cell execution failed", output_stream)
            return False
        else:
            return True
            
    except Exception as e:
        elapsed = time.time() - start_time
        if "timeout" in str(e).lower():
            log(f"\n⏰ TIMEOUT after {elapsed:.2f}s", output_stream)
        else:
            log(f"\n❌ Execution error: {e}", output_stream)
        return False

def output_hook(msg, output_stream=None):
    """
    Hook to capture real-time output
    """
    msg_type = msg['header']['msg_type']
    content = msg.get('content', {})
    
    if msg_type == 'stream':
        # Print, logging output
        text = content.get('text', '')
        log_raw(text, output_stream, end='')
        
    elif msg_type == 'execute_result':
        # Expression result
        data = content.get('data', {})
        if 'text/plain' in data:
            result = data['text/plain']
            log(f"\n📤 Output: {result}", output_stream)
            
    elif msg_type == 'display_data':
        # Plots, images
        data = content.get('data', {})
        if 'text/plain' in data:
            display = data['text/plain']
            log(f"\n🖼️ Display: {display}", output_stream)
            
    elif msg_type == 'error':
        # Errors
        ename = content.get('ename', 'Error')
        evalue = content.get('evalue', 'Unknown error')
        traceback = content.get('traceback', [])
        
        log(f"\n❌ {ename}: {evalue}", output_stream)
        for line in traceback:
            # Remove ANSI codes for cleaner output
            clean_line = ''.join(char for char in line if ord(char) < 127)
            log(clean_line, output_stream, level='ERROR')
            
    elif msg_type == 'status':
        # Status updates
        execution_state = content.get('execution_state', 'unknown')
        if execution_state == 'busy':
            log(f"🔄 Busy at {time.strftime('%H:%M:%S')}", output_stream)
        elif execution_state == 'idle':
            log(f"⚡ Idle at {time.strftime('%H:%M:%S')}", output_stream)

def log(message, output_stream=None, level='INFO', end='\n'):
    """Unified logging for console and file (no timestamp)"""
    formatted_msg = f"{message}"
    
    # Write to console only if there is no output_stream
    if output_stream is None:
        print(formatted_msg, end=end)
    
    # Write to file if specified
    if output_stream and not output_stream.closed:
        output_stream.write(formatted_msg + end)
        output_stream.flush()

def log_raw(message, output_stream=None, end='\n'):
    """Log without timestamp for raw code output"""
    # Write to console only if there is no output_stream
    if output_stream is None:
        sys.stdout.write(message + end)
        sys.stdout.flush()
    
    # Write to file if specified
    if output_stream and not output_stream.closed:
        output_stream.write(message + end)
        output_stream.flush()

def main():
    import argparse

    if "--version" in sys.argv or "-v" in sys.argv:
        print(f"{VERSION} - {AUTHOR}")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Robust sequential Jupyter notebook execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_notebook.py notebook.ipynb
  python run_notebook.py notebook.ipynb --timeout 7200  # 2 hours per cell
  python run_notebook.py notebook.ipynb --timeout 0     # No timeout
  python run_notebook.py show 2 notebook.ipynb
  python run_notebook.py show notebook.ipynb
  python run_notebook.py edit 2 notebook.ipynb
  python run_notebook.py info notebook.ipynb

This version uses execute_interactive() for more reliable execution.
        """,
        add_help=False
    )
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Default run command (no subcommand)
    parser_run = subparsers.add_parser("run", help="Run the notebook (default)")
    parser_run.add_argument("notebook", help="Path to .ipynb file")
    parser_run.add_argument("--timeout", "-t", type=int, default=0,
                            help="Timeout per cell in seconds (default: 0=no timeout, e.g. 3600 for 1 hour)")
    parser_run.add_argument("--output", "-o", type=str, default=None,
                            help="File to save output (default: console only)")
    parser_run.add_argument("--debug", action="store_true",
                                help="Debug mode with more output")

    # Show command (cell_num is now optional)
    parser_show = subparsers.add_parser("show", help="Show code of a cell or all code cells")
    parser_show.add_argument("cell_num", type=int, nargs="?", help="Cell number (1-based, optional)")
    parser_show.add_argument("notebook", help="Path to .ipynb file")

    # Edit command
    parser_edit = subparsers.add_parser("edit", help="Edit code of a cell")
    parser_edit.add_argument("cell_num", type=int, help="Cell number (1-based)")
    parser_edit.add_argument("notebook", help="Path to .ipynb file")
    # Info command
    parser_info = subparsers.add_parser("info", help="Show notebook info")
    parser_info.add_argument("notebook", help="Path to .ipynb file")

    # Parse args before help check to ensure subcommands are registered
    args = parser.parse_args()

    # Show help with subcommands if requested
    if "--help" in sys.argv or "-h" in sys.argv:
        if len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h"):
            parser.print_help()
            print("\nSub-commands:")
            subparsers.choices['run'].print_help()
            subparsers.choices['show'].print_help()
            subparsers.choices['edit'].print_help()
            subparsers.choices['info'].print_help()
            sys.exit(0)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "show":
        # Show a specific code cell or all code cells
        with open(args.notebook, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        code_cells = [cell for cell in nb.cells if cell.cell_type == 'code']
        if args.cell_num is not None:
            idx = args.cell_num - 1
            if 0 <= idx < len(code_cells):
                print(f"\n--- Cell {args.cell_num} ---\n")
                print(code_cells[idx].source)
            else:
                print(f"❌ Cell {args.cell_num} not found (total code cells: {len(code_cells)})")
        else:
            for i, cell in enumerate(code_cells, 1):
                print(f"\n--- Cell {i} ---\n")
                print(cell.source)
                print("-" * 40)
        sys.exit(0)

    elif args.command == "info":
        # Show notebook info
        try:
            stat = os.stat(args.notebook)
            mtime = datetime.fromtimestamp(stat.st_mtime)
            with open(args.notebook, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
            total_cells = len(nb.cells)
            code_cells = len([cell for cell in nb.cells if cell.cell_type == 'code'])
            print(f"📄 Notebook: {args.notebook}")
            print(f"🕒 Last modified: {mtime}")
            print(f"🔢 Total cells: {total_cells}")
            print(f"💻 Code cells: {code_cells}")
        except Exception as e:
            print(f"❌ Error reading notebook info: {e}")
        sys.exit(0)

    elif args.command == "edit":
        # Edit the code of the requested cell (opens $EDITOR)
        import tempfile
        import subprocess

        with open(args.notebook, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        code_cells = [cell for cell in nb.cells if cell.cell_type == 'code']
        idx = args.cell_num - 1
        if 0 <= idx < len(code_cells):
            old_code = code_cells[idx].source
            print(f"\n--- Editing Cell {args.cell_num} ---\n")
            with tempfile.NamedTemporaryFile("w+", suffix=".py") as tf:
                tf.write(old_code)
                tf.flush()
                editor = os.environ.get("EDITOR", "nano")
                subprocess.call([editor, tf.name])
                tf.seek(0)
                new_code = tf.read()
            if new_code != old_code:
                code_cells[idx].source = new_code
                with open(args.notebook, "w", encoding="utf-8") as f:
                    nbformat.write(nb, f)
                print("✅ Cell updated.")
            else:
                print("No changes made.")
        else:
            print(f"❌ Cell {args.cell_num} not found (total code cells: {len(code_cells)})")
        sys.exit(0)

    else:
        # Default: run notebook
        output_file = args.output
        timeout = None if args.timeout == 0 else args.timeout

        start_msg = f"🚀 Starting notebook execution: {args.notebook}"
        timeout_msg = f"⏱️  Cell timeout: {'No limit' if timeout is None else f'{timeout}s'}"
        output_msg = f"📝 Output: {'Console only' if not output_file else f'Console + {output_file}'}"
        mode_msg = f"🔧 Mode: Interactive"

        print(start_msg)
        print(timeout_msg)
        print(output_msg)
        print(mode_msg)
        print("🔄 Use Ctrl+C to interrupt execution")
        print("📝 Each cell waits for the previous one to complete\n")

        try:
            run_notebook_realtime_extended(args.notebook, timeout, output_file)
        except FileNotFoundError:
            msg = f"❌ Error: Notebook file '{args.notebook}' not found"
            if output_file:
                with open(output_file, 'a') as f:
                    f.write(f"{msg}\n")
            print(msg)
            sys.exit(1)
        except Exception as e:
            msg = f"❌ Unexpected error: {e}"
            if output_file:
                with open(output_file, 'a') as f:
                    f.write(f"{msg}\n")
            print(msg)
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)

        final_msg = "🎉 Notebook execution completed!"
        print(f"\n{final_msg}")
        if output_file:
            try:
                with open(output_file, 'a') as f:
                    f.write(f"{final_msg}\n")
            except:
                pass

if __name__ == "__main__":
    main()            