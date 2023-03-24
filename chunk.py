#!/usr/bin/env python3

import sys
from typing import List


def chunk_text(file_path: str, chunk_size: int) -> List[str]:
    with open(file_path, 'r') as f:
        text = f.read()
        text_chunks = []
        start = 0
        end = chunk_size

        while end < len(text):
            while text[end] != ' ':
                end -= 1
            text_chunks.append(text[start:end])
            start = end + 1
            end = start + chunk_size

        text_chunks.append(text[start:])

    return text_chunks


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <file_path>")
        return

    file_path = sys.argv[1]
    chunk_size = int(0.99 * 2048)  # 99% of the input limit for the chatbox

    # Extract the stock name from the file name
    stock_name = file_path.split('.')[0]

    text_chunks = chunk_text(file_path, chunk_size)

    for i, chunk in enumerate(text_chunks):
        with open(f"{stock_name}-{i}.chunk", 'w') as f:
            f.write(chunk)


if __name__ == '__main__':
    main()
