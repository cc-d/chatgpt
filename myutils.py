#!/usr/bin/env python3
import logging
import shutil
import time
from decimal import ROUND_HALF_UP, Decimal
from functools import wraps
from typing import List, Optional


def setup_logging(level: str = 'debug') -> None:
    log_level = getattr(logging, level.upper(), logging.DEBUG)
    logging.basicConfig(
        level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')


MFORMAT = f'[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] %(message)s'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(module)s.%(funcName)s() %(message)s',
    handlers=[logging.StreamHandler()],
)

mlogger = logging.getLogger(__name__)

def logf(level: str = 'debug'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            setup_logging(level)
            start_time = time.time()

            result = func(*args, **kwargs)

            end_time = time.time()
            elapsed_time = end_time - start_time
            log_message = f"[{elapsed_time:.2f}] {func.__name__}({args}, {kwargs}) >>>>>>>>>> {result}"
            mlogger.log(getattr(logging, level.upper()), log_message)

            return result
        return wrapper
    return decorator


def D(num) -> Decimal:
    return Decimal(str(num))


def CD(num) -> Decimal:
    return D(
        str(num)).quantize(D('0.01'), rounding=ROUND_HALF_UP)



def boxprint(strings: List[str], title: Optional[str] = None) -> None:
    # Get terminal
    title = str(title)
    terminal_width, _ = shutil.get_terminal_size()

    # Determine column width and number of rows
    max_length = max(*(len(s) for s in strings), len(title) - (len(title) // 3) )
    # 4 for column padding and separators
    num_columns = max(1, terminal_width // (max_length + 4))
    column_width = (terminal_width - num_columns - 1) // num_columns
    num_rows = -(-len(strings) // num_columns)  # ceil division

    # Prepare box border
    horizontal_border = '+' + '-' * \
        (column_width * num_columns + num_columns - 1) + '+'
    empty_row = '|' + ' ' * \
        (column_width * num_columns + num_columns - 1) + '|'

    # Prepare box title
    if title:
        title_line = '| ' + \
            title.center(column_width * num_columns + num_columns - 2) + '|'
        print(horizontal_border)
        print(title_line)
    print(horizontal_border)

    # Print rows of data
    for i in range(num_rows):
        row_strings = strings[i::num_rows]
        if len(row_strings) < num_columns:
            row_strings.extend([''] * (num_columns - len(row_strings)))
        columns = [s.ljust(column_width - 2) for s in row_strings]
        print('| ' + ' | '.join(c.ljust(column_width - 2)
              for c in columns) + ' |')

    # Print bottom border
    print(empty_row)
    print(horizontal_border)
